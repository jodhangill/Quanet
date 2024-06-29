import neat
import backtrader as bt
import yfinance as yf
from . import config_parser, NeatStrategy

# Download data example (TODO: Choose data from client-side)
data = yf.download('SPY', period="7d")
print(data)

def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        cerebro = bt.Cerebro()

        # Create neural network
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        # Pass the network as an argument to the strategy
        cerebro.addstrategy(NeatStrategy.NeatStrategy, neat_net=net)

        data_feed = bt.feeds.PandasData(dataname=data)
        cerebro.adddata(data_feed)

        # Add analyzer for testing base metric (TODO: Choose analyzers/"fitness function" from client-side)
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")

        cerebro.broker.setcash(100000.0)
        strategies = cerebro.run()
        strategy = strategies[0]

        sharpe_ratio = strategy.analyzers.sharpe.get_analysis()['sharperatio']
        genome.fitness = sharpe_ratio if sharpe_ratio else float('-INF')

def run(data):
    config_file = config_parser.process_parameters(data)

    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run for up to 10 generations.
    max_generations = 10
    try:
        # Run for up to 10 generations.
        winner = p.run(eval_genomes, max_generations)
    except neat.population.CompleteExtinctionException:
        winner = stats.best_genome()
    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))

    return format(winner)

