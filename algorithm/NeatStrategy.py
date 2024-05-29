import backtrader as bt
import numpy as np

class NeatStrategy(bt.Strategy):
    params = (
        ('neat_net', None), # Neural network created from genome
    )

    def next(self):
        # Prepare input data for the neural network
        inputs = np.array([
            self.datas[0].volume[0],
            self.datas[0].close[0] 
        ])
        # Get the neural network output
        output = self.params.neat_net.activate(inputs)
        # Make a decision based on the neural network output
        if output[0] > 0.5:
            self.buy()
        elif output[0] < 0.5:
            self.sell()