# Quanet

### Try Now: https://quanet.pythonanywhere.com

Quanet is a tool for applying the NeuroEvolution of Augmenting Topologies (NEAT) algorithm to quantitative trading, designed for users who want to leverage advanced trading strategies without needing to write code.

![alt text](/static/images/quanet.gif)

## Features

- **Codeless Interface**: Configure and run NEAT-based trading algorithms without programming.
- **Custom Fitness Functions**: Define your own metrics to evaluate trading strategies, such as Sharpe ratio, max drawdown, total compound returns, and SQN.
- **Flexible Data Selection**: Choose stock data from any stock or time range for testing your strategies.
- **Comprehensive Configuration**: Adjust parameters like max generations, number of hidden nodes, and population size to fine-tune the algorithm.

## How Quanet Works

1. **Initialization**: Quanet starts by setting up an initial population of trading strategies, each represented by a neural network. These strategies are random variations, or "genomes," that the algorithm will evaluate and refine over time.
![genome example](/static/images/genome.png)
*Genome Example*
2. **Simulation**: The algorithm tests each strategy using the chosen stock data over a specified time range. It simulates trading activities such as buying and selling based on various indicators and tracks how each strategy performs.
![Simulated Strategy](/static/images/graph.png)
*Simulated Strategy*
3. **Fitness Calculation**: After simulating trading, Quanet calculates the overall fitness of each strategy by aggregating performance scores from all the stock data. This score reflects how well the strategy performed across different scenarios.
4. **Evolution**: Based on the fitness scores, Quanet evolves the population of strategies. It selects the better-performing strategies to create new "offspring" strategies. These offspring are variations of the best strategies, incorporating mutations and recombinations to explore new possibilities.
5. **Rinse and Repeat**: This process repeats for a number of generations. With each generation, Quanet refines and improves the trading strategies by continuously evaluating and evolving them, aiming to find the most effective strategy.

## How to Use Quanet

1. **Create Your Fitness Function**: Think about what metrics are important for evaluating your trading strategies. Decide on metrics like Sharpe ratio, max drawdown, total returns, and SQN. Input these metrics into Quanet to create your fitness function. 
    For example, to find a strategy that balances profitability and risk, you could use the fitness function TOTAL COMPOUND RETURNS/(1 + MAX DRAWDOWN)
2. **Choose Your Stock Data**: Select the stocks and time periods you want to analyze. Quanet allows you to pick specific stocks and date ranges for testing your trading strategies.
![Ticker Examples](/static/images/tickers.png)
*Ticker Examples*
3. **Configure the NEAT Algorithm**: Quanet is built on NEAT-Python and provides extensive configuration options for almost all the parameters used in NEAT-Python. To tailor the algorithm to your needs, you can adjust settings such as the maximum number of generations, the fitness threshold, and the population size.
4. **Run the Algorithm**: Once everything is configured, start the algorithm. Quanet will automatically run the simulations, evaluate each trading strategy, and provide you with updates on its progress.
## Disclaimer

The output equation is for educational purposes only and should not be used for real-world trading or financial decisions.

## Acknowledgments

Special thanks to the developers of NEAT-Python and Backtrader for their contributions to this project. For detailed information on NEAT-Python parameters and configuration, see https://neat-python.readthedocs.io/en/latest/config_file.html.
