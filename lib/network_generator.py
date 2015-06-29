from graph_tool.all import *

from lib.network import Network


def get_fully_connected(filename, size=100):
    return Network(filename, graph=complete_graph(size, self_loops=False, directed=False))




