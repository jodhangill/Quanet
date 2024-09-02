import neat
import backtrader as bt
import pandas as pd
import numpy as np
import js
import json
import sys
from .reporters import CustomReporter, log, send_generation_progress
from .config_parser import process_config

class NeatStrategy(bt.Strategy):
    params = (('neat_net', None),)  # Neural network created from genome

    def __init__(self):
        # Initialize lists to store equity, dates, orders, cash, and prices
        self.equity = []
        self.dates = []
        self.orderSequence = []
        self.cash = []
        self.prices = []

        # Define indicators
        self.sma = bt.indicators.MovingAverageSimple(self.datas[0], period=15)  # Simple Moving Average
        self.atr = bt.indicators.ATR(self.datas[0])  # Average True Range
        self.adx = bt.indicators.AverageDirectionalMovementIndex(self.datas[0])  # Average Directional Movement Index
        self.rsi = bt.indicators.RSI(self.datas[0])  # Relative Strength Index
        self.volume = self.datas[0].volume  # Volume indicator

        # Initialize means and standard deviations for scaling
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
        # Collect indicator values
        inputs = np.array([
            self.sma[0],
            self.atr[0],
            self.adx[0],
            self.rsi[0],
            self.volume[0]
        ])

        # Update statistics and scale inputs
        self.update_statistics(inputs)
        scaled_inputs = self.scale_data(inputs)

        # Get output from NEAT neural network
        output = self.params.neat_net.activate(scaled_inputs)[0]

        # Decision-making based on network output
        if output > 0.5:
            # Buy condition
            available_cash = self.broker.get_cash()
            size = int(available_cash * 0.10 / self.data.close[0])

            if size >= 1:
                self.buy(size=size)
                self.orderSequence.append('buy')
        else:
            # Sell or hold condition
            position = self.getposition()
            if position.size > 0:
                self.sell(size=position.size)
                self.orderSequence.append('sell')
            else:
                self.orderSequence.append('hold')

        # Track equity, cash, dates, and prices for analysis
        self.equity.append(self.broker.get_value())
        self.cash.append(self.broker.get_cash())
        self.dates.append(self.datas[0].datetime.date(0).strftime('%Y-%m-%d'))
        self.prices.append(self.data.close[0])

def eval_genomes(genomes, config, fitness_function, datas):
    genome_idx = 0
    for genome_id, genome in genomes:
        results = []
        genome.fitness = 0
        for i, data in enumerate(datas):
            cerebro = bt.Cerebro()
            net = neat.nn.FeedForwardNetwork.create(genome, config)  # Create a neural network from the genome
            cerebro.addstrategy(NeatStrategy, neat_net=net)

            # Save the data to a file for backtrader
            with open("data.txt", "w") as f:
                f.write(data)

            # Load data into backtrader
            data_feed = bt.feeds.YahooFinanceCSVData(dataname="data.txt")
            cerebro.adddata(data_feed)

            # Add analyzers for performance metrics
            cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
            cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
            cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
            cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
            
            cerebro.broker.set_cash(100000.0)
            strategies = cerebro.run()
            strategy = strategies[0]

            # Retrieve analyzer results
            sharpe_ratio = strategy.analyzers.sharpe.get_analysis().get('sharperatio')
            max_drawdown = strategy.analyzers.drawdown.get_analysis().get('max', {}).get('drawdown')
            total_compound_returns = strategy.analyzers.returns.get_analysis().get('rtot')
            sqn = strategy.analyzers.sqn.get_analysis().get('sqn')

            # Calculate fitness with error handling
            try:
                fitness = eval(fitness_function) or sys.float_info.min
            except Exception as e:
                print(f"Error evaluating fitness function: {e}")
                fitness = sys.float_info.min

            # Store the result of this data set
            result = {
                'data_id': i,
                'equity': strategy.equity,
                'cash': strategy.cash,
                'dates': strategy.dates,
                'orderSequence': strategy.orderSequence,
                'prices': strategy.prices,
                'sr': sharpe_ratio,
                'md': max_drawdown,
                'tcr': total_compound_returns,
                'sqn': sqn,
                'fitness': fitness
            }
            results.append(result)

            genome.fitness += fitness  # Update genome's fitness with calculated fitness
            
        genome.results = results  # Store the results in the genome
        genome_idx += 1
        send_generation_progress(-1, genome_idx, len(genomes))  # Send progress update

def run(config_params, datas, fitness_function):
    config_file = process_config(config_params)  # Process configuration parameters

    # Set up NEAT configuration
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    p = neat.Population(config)  # Create the NEAT population
    p.add_reporter(CustomReporter(True))  # Add custom reporter for logging
    stats = neat.StatisticsReporter()  # Add statistics reporter
    p.add_reporter(stats)

    max_generations = int(config_params.get('max_generations', 5))
    try:
        winner = p.run(lambda genomes, config: eval_genomes(genomes, config, fitness_function, datas), max_generations)
    except neat.population.CompleteExtinctionException:
        winner = stats.best_genome()  # Handle complete extinction case

    log('\nBest genome:\n{!s}'.format(winner))

    return format(winner)  # Return the best genome as a formatted string

def main():
    # Send loading finished update
    result_dict = {"loading": -1}
    result_string = json.dumps(result_dict)
    js.postMessage(result_string)

    config = getattr(js, 'config')
    fitness_function = getattr(js, 'fit_func')
    datas = getattr(js, 'data')

    run(json.loads(config), datas, fitness_function)
