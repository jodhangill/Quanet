import neat
import backtrader as bt
import numpy as np
import configparser
import json
import js
import time
from neat.math_util import mean, stdev

def log(msg):
    result_dict = {"update": msg}
    result_string = json.dumps(result_dict)
    js.postMessage(result_string)

def process_config(params):
    config = configparser.ConfigParser()

    # NEAT Configuration
    config['NEAT'] = {
        'fitness_criterion': params.get('fitness_criterion', 'max'),
        'fitness_threshold': params.get('fitness_threshold', '3.9'),
        'pop_size': params.get('pop_size', '150'),
        'reset_on_extinction': str(params.get('reset_on_extinction', False))
    }

    # Default Genome Configuration
    config['DefaultGenome'] = {
        'activation_default': params.get('activation_default', 'sigmoid'),
        'activation_mutate_rate': params.get('activation_mutate_rate', '0.0'),
        'activation_options': params.get('activation_options', 'sigmoid'),
        'aggregation_default': params.get('aggregation_default', 'sum'),
        'aggregation_mutate_rate': params.get('aggregation_mutate_rate', '0.0'),
        'aggregation_options': params.get('aggregation_options', 'sum'),
        'bias_init_mean': params.get('bias_init_mean', '0.0'),
        'bias_init_stdev': params.get('bias_init_stdev', '1.0'),
        'bias_max_value': params.get('bias_max_value', '30.0'),
        'bias_min_value': params.get('bias_min_value', '-30.0'),
        'bias_mutate_power': params.get('bias_mutate_power', '0.5'),
        'bias_mutate_rate': params.get('bias_mutate_rate', '0.7'),
        'bias_replace_rate': params.get('bias_replace_rate', '0.1'),
        'compatibility_disjoint_coefficient': params.get('compatibility_disjoint_coefficient', '1.0'),
        'compatibility_weight_coefficient': params.get('compatibility_weight_coefficient', '0.5'),
        'conn_add_prob': params.get('conn_add_prob', '0.5'),
        'conn_delete_prob': params.get('conn_delete_prob', '0.5'),
        'enabled_default': str(params.get('enabled_default', True)),
        'enabled_mutate_rate': params.get('enabled_mutate_rate', '0.01'),
        'feed_forward': str(params.get('feed_forward', True)),
        'initial_connection': params.get('initial_connection', 'full'),
        'node_add_prob': params.get('node_add_prob', '0.2'),
        'node_delete_prob': params.get('node_delete_prob', '0.2'),
        'num_hidden': params.get('num_hidden', '0'),
        'num_inputs': params.get('num_inputs', '5'),
        'num_outputs': params.get('num_outputs', '1'),
        'response_init_mean': params.get('response_init_mean', '1.0'),
        'response_init_stdev': params.get('response_init_stdev', '0.0'),
        'response_max_value': params.get('response_max_value', '30.0'),
        'response_min_value': params.get('response_min_value', '-30.0'),
        'response_mutate_power': params.get('response_mutate_power', '0.0'),
        'response_mutate_rate': params.get('response_mutate_rate', '0.0'),
        'response_replace_rate': params.get('response_replace_rate', '0.0'),
        'weight_init_mean': params.get('weight_init_mean', '0.0'),
        'weight_init_stdev': params.get('weight_init_stdev', '1.0'),
        'weight_max_value': params.get('weight_max_value', '30'),
        'weight_min_value': params.get('weight_min_value', '-30'),
        'weight_mutate_power': params.get('weight_mutate_power', '0.5'),
        'weight_mutate_rate': params.get('weight_mutate_rate', '0.8'),
        'weight_replace_rate': params.get('weight_replace_rate', '0.1')
    }

    # Default Species Set Configuration
    config['DefaultSpeciesSet'] = {
        'compatibility_threshold': params.get('compatibility_threshold', '3.0')
    }

    # Default Stagnation Configuration
    config['DefaultStagnation'] = {
        'species_fitness_func': params.get('species_fitness_func', 'max'),
        'max_stagnation': params.get('max_stagnation', '20'),
        'species_elitism': params.get('species_elitism', '2')
    }

    # Default Reproduction Configuration
    config['DefaultReproduction'] = {
        'elitism': params.get('elitism', '2'),
        'survival_threshold': params.get('survival_threshold', '0.2')
    }
    
    # Write the parsed config to file
    with open('neat_config.ini', 'w') as configfile:
        config.write(configfile)

class NeatStrategy(bt.Strategy):
    params = (('neat_net', None),)  # Neural network created from genome

    def __init__(self):
        self.buys = 0
        self.sells = 0

        # Define indicators
        self.sma = bt.indicators.MovingAverageSimple(self.datas[0], period=15)
        self.atr = bt.indicators.ATR(self.datas[0])
        self.adx = bt.indicators.AverageDirectionalMovementIndex(self.datas[0])
        self.rsi = bt.indicators.RSI(self.datas[0])
        self.volume = self.datas[0].volume

        # Initialize means and standard deviations
        self.means = np.zeros(5)
        self.stds = np.ones(5) 

    def scale_data(self, data):
        """Scale input data using stored means and stds"""
        inputs = np.array(data)
        return (inputs - self.means) / self.stds

    def update_statistics(self, data):
        """Update ongoing mean and std values"""
        self.means = np.array([np.mean([x, self.means[i]]) for i, x in enumerate(data)])
        self.stds = np.array([np.std([x, self.stds[i]]) for i, x in enumerate(data)])

    def next(self):
        inputs = np.array([
            self.sma[0],
            self.atr[0],
            self.adx[0],
            self.rsi[0],
            self.volume[0]
        ])

        self.update_statistics(inputs)
        scaled_inputs = self.scale_data(inputs)

        output = self.params.neat_net.activate(scaled_inputs)[0]

        if output > 0.5:
            available_cash = self.broker.get_cash()
            size = int(available_cash * 0.10 / self.data.close[0])

            if size >= 1:
                self.buys += 1
                self.buy(size=size)
        else:
            position = self.getposition()
            if position.size > 0:
                self.sells += 1
                self.sell(size=position.size)

def eval_genomes(genomes, config, fitness_function, datas):
    for genome_id, genome in genomes:
        genome.fitness = 0
        for data in datas:
            cerebro = bt.Cerebro()
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            cerebro.addstrategy(NeatStrategy, neat_net=net)

            with open("data.txt", "w") as f:
                f.write(data)

            data_feed = bt.feeds.YahooFinanceCSVData(dataname="data.txt")
            cerebro.adddata(data_feed)

            # Add analyzers
            cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
            cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
            cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
            cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
            
            cerebro.broker.set_cash(100000.0)
            strategies = cerebro.run()
            strategy = strategies[0]

            # Retrieve analyzer results
            sharpe_ratio = strategy.analyzers.sharpe.get_analysis().get('sharperatio', float('-inf'))
            max_drawdown = strategy.analyzers.drawdown.get_analysis().get('max', {}).get('drawdown', float('-inf'))
            total_compound_returns = strategy.analyzers.returns.get_analysis().get('rtot', float('-inf'))
            sqn = strategy.analyzers.sqn.get_analysis().get('sqn', float('-inf'))

            # Calculate fitness with error handling
            try:
                fitness = eval(fitness_function) or float('-inf')
            except Exception as e:
                print(f"Error evaluating fitness function: {e}")
                fitness = float('-inf')

            genome.fitness += fitness

class CustomReporter(neat.reporting.BaseReporter):
    def __init__(self, show_species_detail):
        self.show_species_detail = show_species_detail
        self.generation = None
        self.generation_start_time = None
        self.generation_times = []
        self.num_extinctions = 0

    def start_generation(self, generation):
        self.generation = generation
        log('\n ****** Running generation {0} ****** \n'.format(generation))
        self.generation_start_time = time.time()

    def end_generation(self, config, population, species_set):
        ng = len(population)
        ns = len(species_set.species)
        if self.show_species_detail:
            log('Population of {0:d} members in {1:d} species:'.format(ng, ns))
            log("   ID   age  size   fitness   adj fit  stag")
            log("  ====  ===  ====  =========  =======  ====")
            for sid in sorted(species_set.species):
                s = species_set.species[sid]
                a = self.generation - s.created
                n = len(s.members)
                f = "--" if s.fitness is None else f"{s.fitness:.3f}"
                af = "--" if s.adjusted_fitness is None else f"{s.adjusted_fitness:.3f}"
                st = self.generation - s.last_improved
                log(f"  {sid:>4}  {a:>3}  {n:>4}  {f:>9}  {af:>7}  {st:>4}")
        else:
            log('Population of {0:d} members in {1:d} species'.format(ng, ns))

        elapsed = time.time() - self.generation_start_time
        self.generation_times.append(elapsed)
        self.generation_times = self.generation_times[-10:]
        average = sum(self.generation_times) / len(self.generation_times)
        log('Total extinctions: {0:d}'.format(self.num_extinctions))
        if len(self.generation_times) > 1:
            log("Generation time: {0:.3f} sec ({1:.3f} average)".format(elapsed, average))
        else:
            log("Generation time: {0:.3f} sec".format(elapsed))

    def post_evaluate(self, config, population, species, best_genome):
        # pylint: disable=no-self-use
        fitnesses = [c.fitness for c in population.values()]
        fit_mean = mean(fitnesses)
        fit_std = stdev(fitnesses)
        best_species_id = species.get_species_id(best_genome.key)
        log('Population\'s average fitness: {0:3.5f} stdev: {1:3.5f}'.format(fit_mean, fit_std))
        log(
            'Best fitness: {0:3.5f} - size: {1!r} - species {2} - id {3}'.format(best_genome.fitness,
                                                                                 best_genome.size(),
                                                                                 best_species_id,
                                                                                 best_genome.key))

    def complete_extinction(self):
        self.num_extinctions += 1
        log('All species extinct.')

    def found_solution(self, config, generation, best):
        log('\nBest individual in generation {0} meets fitness threshold - complexity: {1!r}'.format(
            self.generation, best.size()))

    def species_stagnant(self, sid, species):
        if self.show_species_detail:
            log("\nSpecies {0} with {1} members is stagnated: removing it".format(sid, len(species.members)))

    def info(self, msg):
        log(msg)

def run(config_file, datas, fitness_function):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    p = neat.Population(config)
    p.add_reporter(CustomReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    max_generations = 10
    try:
        winner = p.run(lambda genomes, config: eval_genomes(genomes, config, fitness_function, datas), max_generations)
    except neat.population.CompleteExtinctionException:
        winner = stats.best_genome()

    log('\nBest genome:\n{!s}'.format(winner))

    return format(winner)

def main():
    config = getattr(js, 'config')
    process_config(json.loads(config))
    fitness_function = getattr(js, 'fit_func')
    datas = getattr(js, 'data')
    run('neat_config.ini', datas, fitness_function)

main()
"Done!"