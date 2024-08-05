import neat
import backtrader as bt
import numpy as np
import configparser
import json
import js

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
                fitness = eval(fitness_function)
            except Exception as e:
                print(f"Error evaluating fitness function: {e}")
                fitness = float('-inf')

            genome.fitness += fitness

def run(config_file, datas, fitness_function):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    max_generations = 10
    try:
        winner = p.run(lambda genomes, config: eval_genomes(genomes, config, fitness_function, datas), max_generations)
    except neat.population.CompleteExtinctionException:
        winner = stats.best_genome()

    print('\nBest genome:\n{!s}'.format(winner))

    return format(winner)

if __name__ == '__main__':
    config = getattr(js, 'config')
    process_config(json.loads(config))
    fitness_function = getattr(js, 'fit_func')
    datas = getattr(js, 'data')
    run('neat_config.ini', datas, fitness_function)
