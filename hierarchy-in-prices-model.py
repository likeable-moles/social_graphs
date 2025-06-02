from collections import Counter
from datetime import datetime
import logging
import networkx as nx
import matplotlib.pyplot as plt
import random as r
import ranking
from timeit import default_timer as timer
from datetime import timedelta

logger = logging.getLogger(__name__)

NODE_LABLES = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def prices_model(n, m=2):
    """
    Generate a Price's Model network with n nodes.

    Parameters:
        n (int): Number of nodes
        m (int): mean number of outgoing edges per new node

    Returns:
        networkx.DiGraph: A directed graph following Price's model
    """
    if m < 1 or m >= n:
        raise ValueError("m must be >= 1 and < n")
    if n > len(NODE_LABLES):
        raise ValueError("n must be less that the number of node labels {}".format(len(NODE_LABLES)))

    G = nx.DiGraph()
    G.add_nodes_from([(i, {"label": NODE_LABLES[i]}) for i in range(m)])
    for new_node in range(m, n):
        # calculate probability of attachment to existing nodes.
        # The probability that a new edge connects to any node with a degree k is
        #
        # (k + 1) p_k
        # -----------
        #   m + 1
        #
        # where `p_k` is the fraction of nodes with degree k, and `m` is a fixed mean out-degree.

        # get a map of node degree k to number of nodes of degree k.
        degrees = [deg for _, deg in G.in_degree()] # Extract just the in-degrees
        degree_count_map = dict(Counter(degrees))
        max_degree = max(degrees)

        # calculate p_k, the fraction of nodes with in-degree k.
        pk = {degree: (degree_count_map[degree] if degree in degree_count_map else 0) / G.number_of_nodes() for degree in range(max_degree+1)}
        logger.debug("p_k, the fraction of nodes with in-degree k: {}".format(pk))
        p = {degree: ((degree + 1) * p_k) / (m + 1) for degree, p_k in pk.items()}
        logger.debug("p, the probability of attachment to node of in-degree k: {}".format(p))

        nodes = set(G.nodes().keys())
        attached = False
        while not attached:
            for node in nodes:
                if r.random() < p[G.in_degree(node)]:
                    G.add_node(new_node, label=NODE_LABLES[new_node])
                    G.add_edge(node, new_node)
                    attached = True

    return G


def visualize_graph(G, node_ranks=None, show=False, layout='spring'):
    """
    Visualizes a NetworkX graph.

    Parameters:
    - G: networkx.Graph or networkx.DiGraph
    - node_ranks: optional dict mapping nodes to ranks (used for color or label)
    - layout: layout algorithm to use: 'spring', 'kamada_kawai', 'circular', 'shell'
    """
    # Choose layout
    if layout == 'spring':
        pos = nx.spring_layout(G, seed=42)
    elif layout == 'kamada_kawai':
        pos = nx.kamada_kawai_layout(G)
    elif layout == 'circular':
        pos = nx.circular_layout(G)
    elif layout == 'shell':
        pos = nx.shell_layout(G)
    else:
        raise ValueError("Unsupported layout type")

    plt.figure(figsize=(8, 6))

    edgelist = G.edges()
    # Node color by rank (if provided)
    if node_ranks:
        # Normalize rank values to color scale
        print("node_ranks: {}".format(node_ranks))
        ranks = [node_ranks.get(node, 0) for node in G.nodes()]
        node_colors = ranks
        labels = {node: f"{G.nodes[node]['label']}\nRank:{node_ranks[node]}" for node in G.nodes()}
        edge_style = ['solid' if node_ranks[edge[0]] < node_ranks[edge[1]] else 'dashed' for edge in edgelist]
        edge_color = ['black' if node_ranks[edge[0]] < node_ranks[edge[1]] else 'orange' for edge in edgelist]
    else:
        node_colors = "lightblue"
        labels = {node: str(node) for node in G.nodes()}
        edge_style = 'solid'
        edge_color = 'black'

    # Draw graph
    # node_shape: s: square, o: circle, ^>v<, d: diamond, p, h: hexagon, 8: octagon
    nx.draw_networkx_nodes(G, pos, node_size=1000, node_color=node_colors, cmap=plt.cm.viridis, alpha=.5, node_shape='s')

    nx.draw_networkx_edges(G, pos, edgelist=edgelist, style=edge_style, edge_color=edge_color)
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_color='black', verticalalignment="center")

    plt.axis('off')
    plt.tight_layout()

    now = datetime.now()
    image_file_name = "report/images/{}-network.png".format(now.strftime("%Y-%m-%d-%H:%M:%S.%f"))
    logger.debug(f"write file {image_file_name}")
    plt.savefig(image_file_name)
    if show:
        plt.show()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-n', '--nodes',
        type=int,
        help='The number of nodes')
    parser.add_argument(
        '-t', '--trials',
        type=int,
        default=1,
        help='The number of trials')
    parser.add_argument(
        '-s', '--show',
        action="store_true",
        help='Show the graph')
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    args = parser.parse_args()
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    n_nodes = args.nodes if args.nodes else 12
    for t in range(args.trials):
        G = prices_model(n=n_nodes, m=2)
        start = timer()
        node_ranks, agony = ranking.min_agony_ranking(G)
        end = timer()
        print("elapsed time {}".format(timedelta(seconds=end-start)))
        print("Graph agony: {}".format(agony))
        visualize_graph(G, node_ranks=node_ranks, show=args.show, layout='circular')


if __name__ == "__main__":
    main()
