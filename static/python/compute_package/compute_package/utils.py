import warnings
import graphviz
import matplotlib.pyplot as plt

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

def neural_net_to_equation(nodes, connections, id):
    """ Translates a neural network formatted as nodes and connections into a mathematical equation (string)"""
    node_names={-1: "SMA", -2: "ATR", -3: "ADX", -4: "RSI", -5: "Volume"}
    if id < 0:
        return node_names[id]

    contributions = []
    for connection in connections:
        if connection['enabled'] and connection['to'] == id:
                from_node = connection['from']
                weight = connection['weight']
                contributions.append(f"({weight} * {neural_net_to_equation(nodes, connections, from_node)})")

    agg_contributions = " + ".join(contributions)
    output = f"1 / (1 + exp(-({agg_contributions})))"
    return output
