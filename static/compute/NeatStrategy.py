import backtrader as bt
import numpy as np

class NeatStrategy(bt.Strategy):
    params = (
        ('neat_net', None), # Neural network created from genome
    )

    def __init__(self):
        self.buys = 0
        self.sells = 0

        # Define inputs for the neural network
        self.sma = bt.indicators.MovingAverageSimple(self.datas[0], period=15)
        self.atr = bt.indicators.ATR(self.datas[0])
        self.adx = bt.indicators.AverageDirectionalMovementIndex(self.datas[0])
        self.rsi = bt.indicators.RSI(self.datas[0])
        self.volume = self.datas[0].volume

        # Initialize variables to store means and standard deviations
        self.means = np.zeros(5)
        self.stds = np.ones(5) 

    def scale_data(self, data):
        """Scale each of the input data"""
        # Concatenate input features into a single array
        inputs = np.array(data)

        # Scale input features using stored means and standard deviations
        scaled_inputs = (inputs - self.means) / self.stds

        return scaled_inputs

    def update_statistics(self, data):
        """Maintain ongoing mean and standard deviation values"""
        # Update means
        self.means = np.array([np.mean([x, self.means[i]]) for i, x in enumerate(data)])

        # Update standard deviations
        self.stds = np.array([np.std([x, self.stds[i]]) for i, x in enumerate(data)])

    def next(self):
        # Prepare input data for the neural network
        inputs = np.array([
            self.sma[0],
            self.atr[0],
            self.adx[0],
            self.rsi[0],
            self.volume[0]
        ])

        # Apply feature scaling on input values
        self.update_statistics(inputs)
        scaled_inputs = self.scale_data(inputs)

        # Get the neural network output
        output = self.params.neat_net.activate(scaled_inputs)[0]

        # Make a decision based on the neural network output
        if output > 0.5:
            # The neural network decided to buy

            available_cash = self.broker.get_cash()

            # Set position size to buy with 10% of available cash
            size = int(available_cash * 0.10 / self.data.close[0])

            # Check if size is at least one stock
            if size >= 1:
                self.buys += 1
                self.buy(size=size)

        else:
            # The neural network decided to sell
            position = self.getposition()
            if position.size > 0:
                self.sells += 1
                self.order = self.sell(size=position.size)