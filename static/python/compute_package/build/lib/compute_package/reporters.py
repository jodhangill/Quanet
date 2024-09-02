import js
import json
import neat
from neat.math_util import mean, stdev
import time
from .utils import draw_net, neural_net_to_equation

def log(msg):
    """Send message to JS environment"""
    result_dict = {"log": msg}
    result_string = json.dumps(result_dict)
    js.postMessage(result_string)

def send_generation_progress(gen, genome, total):
    """Send progress update to JS environment"""
    result_dict = {"update": {
        "gen": gen,
        "genome": genome,
        "total": total,
    }}
    result_string = json.dumps(result_dict)
    js.postMessage(result_string)

def send_genome(genome, config):
    """Send best genome of generation to JS environment"""
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

    result_dict = {"genome": {
        "key": genome.key,
        "connections": formatted_connections,
        "nodes": formatted_nodes,
        "fitness": genome.fitness,
        "dot": dot.source,
        "graphs": genome.results,
        "equation": neural_net_to_equation(formatted_nodes, formatted_connections, 0),
    }}

    result_string = json.dumps(result_dict)
    js.postMessage(result_string)

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
        send_generation_progress(generation, 0, 0)
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
