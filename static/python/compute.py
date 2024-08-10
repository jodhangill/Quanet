import neat
import backtrader as bt
import pandas as pd
import numpy as np
import configparser
import json
import js
import time
from neat.math_util import mean, stdev
import warnings
import graphviz
import matplotlib.pyplot as plt
import numpy as np


# From neat-python/examples/xor/visualize.py
def plot_stats(statistics, ylog=False, view=False, filename='avg_fitness.svg'):
    """ Plots the population's average and best fitness. """
    if plt is None:
        warnings.warn("This display is not available due to a missing optional dependency (matplotlib)")
        return

    generation = range(len(statistics.most_fit_genomes))
    best_fitness = [c.fitness for c in statistics.most_fit_genomes]
    avg_fitness = np.array(statistics.get_fitness_mean())
    stdev_fitness = np.array(statistics.get_fitness_stdev())

    plt.plot(generation, avg_fitness, 'b-', label="average")
    plt.plot(generation, avg_fitness - stdev_fitness, 'g-.', label="-1 sd")
    plt.plot(generation, avg_fitness + stdev_fitness, 'g-.', label="+1 sd")
    plt.plot(generation, best_fitness, 'r-', label="best")

    plt.title("Population's average and best fitness")
    plt.xlabel("Generations")
    plt.ylabel("Fitness")
    plt.grid()
    plt.legend(loc="best")
    if ylog:
        plt.gca().set_yscale('symlog')

    plt.savefig(filename)
    if view:
        plt.show()

    plt.close()

# From neat-python/examples/xor/visualize.py
def plot_spikes(spikes, view=False, filename=None, title=None):
    """ Plots the trains for a single spiking neuron. """
    t_values = [t for t, I, v, u, f in spikes]
    v_values = [v for t, I, v, u, f in spikes]
    u_values = [u for t, I, v, u, f in spikes]
    I_values = [I for t, I, v, u, f in spikes]
    f_values = [f for t, I, v, u, f in spikes]

    fig = plt.figure()
    plt.subplot(4, 1, 1)
    plt.ylabel("Potential (mv)")
    plt.xlabel("Time (in ms)")
    plt.grid()
    plt.plot(t_values, v_values, "g-")

    if title is None:
        plt.title("Izhikevich's spiking neuron model")
    else:
        plt.title("Izhikevich's spiking neuron model ({0!s})".format(title))

    plt.subplot(4, 1, 2)
    plt.ylabel("Fired")
    plt.xlabel("Time (in ms)")
    plt.grid()
    plt.plot(t_values, f_values, "r-")

    plt.subplot(4, 1, 3)
    plt.ylabel("Recovery (u)")
    plt.xlabel("Time (in ms)")
    plt.grid()
    plt.plot(t_values, u_values, "r-")

    plt.subplot(4, 1, 4)
    plt.ylabel("Current (I)")
    plt.xlabel("Time (in ms)")
    plt.grid()
    plt.plot(t_values, I_values, "r-o")

    if filename is not None:
        plt.savefig(filename)

    if view:
        plt.show()
        plt.close()
        fig = None

    return fig

# From neat-python/examples/xor/visualize.py
def plot_species(statistics, view=False, filename='speciation.svg'):
    """ Visualizes speciation throughout evolution. """
    if plt is None:
        warnings.warn("This display is not available due to a missing optional dependency (matplotlib)")
        return

    species_sizes = statistics.get_species_sizes()
    num_generations = len(species_sizes)
    curves = np.array(species_sizes).T

    fig, ax = plt.subplots()
    ax.stackplot(range(num_generations), *curves)

    plt.title("Speciation")
    plt.ylabel("Size per Species")
    plt.xlabel("Generations")

    plt.savefig(filename)

    if view:
        plt.show()

    plt.close()

def draw_net(config, genome, view=False, filename=None, node_names=None, show_disabled=True, prune_unused=False,
             node_colors=None, fmt='svg'):
    """ Receives a genome and draws a neural network with arbitrary topology. """
    # Attributes for network nodes.
    if graphviz is None:
        warnings.warn("This display is not available due to a missing optional dependency (graphviz)")
        return

    # If requested, use a copy of the genome which omits all components that won't affect the output.
    if prune_unused:
        genome = genome.get_pruned_copy(config.genome_config)

    if node_names is None:
        node_names = {}

    assert type(node_names) is dict

    if node_colors is None:
        node_colors = {}

    assert type(node_colors) is dict

    node_attrs = {
        'shape': 'circle',
        'fontsize': '9',
        'height': '0.2',
        'width': '0.2'}

    dot = graphviz.Digraph(format=fmt, node_attr=node_attrs, graph_attr={'bgcolor': 'transparent'})

    inputs = set()
    for k in config.genome_config.input_keys:
        inputs.add(k)
        name = node_names.get(k, str(k))
        input_attrs = {'style': 'striped', 'fontcolor': 'white', 'color': 'white'}
        dot.node(name, _attributes=input_attrs)

    outputs = set()
    for k in config.genome_config.output_keys:
        outputs.add(k)
        name = node_names.get(k, str(k))
        node_attrs = {'style': 'striped', 'fontcolor': 'white', 'color': 'white'}

        dot.node(name, _attributes=node_attrs)

    used_nodes = set(genome.nodes.keys())
    for n in used_nodes:
        if n in inputs or n in outputs:
            continue

        attrs = {'style': 'striped', 'fontcolor': 'white', 'color': 'white'}
        dot.node(str(n), _attributes=attrs)

    for cg in genome.connections.values():
        if cg.enabled or show_disabled:
            # if cg.input not in used_nodes or cg.output not in used_nodes:
            #    continue
            input, output = cg.key
            a = node_names.get(input, str(input))
            b = node_names.get(output, str(output))
            style = 'solid' if cg.enabled else 'dotted'
            color = 'green' if cg.weight > 0 else 'red'
            width = str(0.1 + abs(cg.weight / 2.0))
            dot.edge(a, b, _attributes={'style': style, 'color': color, 'penwidth': width})

    return dot

def log(msg):
    result_dict = {"update": msg}
    result_string = json.dumps(result_dict)
    js.postMessage(result_string)

def send_genome(genome, config):
    formatted_connections = []
    for key, gene in genome.connections.items():
        formatted_gene = {
            "from": key[0],
            "to": key[1],
            "weight": gene.weight,
            "enabled": gene.enabled,
        }
        formatted_connections.append(formatted_gene)

    formatted_nodes = []
    for key, gene in genome.nodes.items():
        formatted_gene = {
            "id": key,
            "bias": gene.bias,
            "response": gene.response,
            "activation": gene.activation,
            "aggregation": gene.aggregation,
        }
        formatted_nodes.append(formatted_gene)

    # Draw neural network in dot format
    dot = draw_net(config, genome, node_names={0: "Buy/Sell", -1: "SMA", -2: "ATR", -3: "ADX", -4: "RSI", -5: "Volume"})

    print(genome.results)
    result_dict = {"genome": {
        "key": genome.key,
        "connections": formatted_connections,
        "nodes": formatted_nodes,
        "fitness": genome.fitness,
        "dot": dot.source,
        "graphs": genome.results,
    }}

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
        self.equity = []
        self.dates = []

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

        self.equity.append(self.broker.getvalue())
        self.dates.append(self.datas[0].datetime.date(0).strftime('%Y-%m-%d'))

def eval_genomes(genomes, config, fitness_function, datas):
    for genome_id, genome in genomes:
        results = []
        genome.fitness = 0
        for i, data in enumerate(datas):
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

            result = {
                'data_id': i,
                'equity': strategy.equity,
                'dates': strategy.dates,
                'sr': sharpe_ratio,
                'md': max_drawdown,
                'tcr': total_compound_returns,
                'sqn': sqn,
                'fitness': fitness
            }
            results.append(result)

            genome.fitness += fitness
        genome.results = results

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
        # Send best genome details to JS side
        send_genome(best_genome, config)
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

    first_genome_id, first_genome = next(iter(p.population.items()))

    max_generations = 5
    try:
        winner = p.run(lambda genomes, config: eval_genomes(genomes, config, fitness_function, datas), max_generations)
    except neat.population.CompleteExtinctionException:
        winner = stats.best_genome()

    log('\nBest genome:\n{!s}'.format(winner))

    return format(winner)

def main():
    result_dict = {"loading": -1}
    result_string = json.dumps(result_dict)
    js.postMessage(result_string)

    config = getattr(js, 'config')
    process_config(json.loads(config))

    fitness_function = getattr(js, 'fit_func')
    datas = getattr(js, 'data')

    run('neat_config.ini', datas, fitness_function)

main()

"Done!"