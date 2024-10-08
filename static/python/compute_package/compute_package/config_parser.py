import configparser

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
        'initial_connection': params.get('initial_connection', 'full_nodirect'),
        'node_add_prob': params.get('node_add_prob', '0.2'),
        'node_delete_prob': params.get('node_delete_prob', '0.2'),
        'num_hidden': params.get('num_hidden', '3'),
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
    
    file_name = 'neat_config.ini'

    # Write the parsed config to file
    with open(file_name, 'w') as configfile:
        config.write(configfile)
    
    return file_name
