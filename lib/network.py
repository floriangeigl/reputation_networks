from __future__ import division
from graph_tool.all import *
from collections import defaultdict


def read_group_list(filename, network, node_id_map=None):
    if node_id_map is None:
        try:
            node_id_map = network.vp['NodeId']
        except KeyError:
            node_id_map = None
    group_map = defaultdict(set)
    with open(filename, 'r') as f:
        for line in f:
            if not line.startswith('#'):
                line = map(int, line.strip().split())
                # group_map[int(line[0])].add(int(line[1]))
                group_map[int(line[0])] = set([int(line[1])])
    cat_pmap = network.new_vertex_property('object')
    for v in network.vertices():
        cat_pmap[v] = set()
    for v in network.vertices():
        cat_pmap[v].update(group_map[int(v) if node_id_map is None else node_id_map[v]])
    return cat_pmap


def read_edge_list(filename, comment='#', sep=None, parallel_edges=False, directed=False, return_node_id_mapping=False):
    graph = Graph(directed=directed)
    graph.vertex_properties["NodeId"] = graph.new_vertex_property('int')
    node_id_mappping = defaultdict(lambda: graph.add_vertex())
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                line = map(int, line.split(sep))
                s, t = node_id_mappping[line[0]], node_id_mappping[line[1]]
                graph.add_edge(s, t)
    remove_parallel_edges(graph)
    for orig_id, vertex in node_id_mappping.iteritems():
        graph.vertex_properties["NodeId"][vertex] = orig_id
    return graph if not return_node_id_mapping else (graph, node_id_mappping)


def bfs_level_iter(start_vertex, neighbours_f=lambda x: x.all_neighbours()):
    visited_nodes = set()
    neighbours = {[start_vertex]}
    distance = 0
    while neighbours:
        distance += 1
        neighbours = {j for i in neighbours for j in neighbours_f(i) if not j in visited_nodes}
        visited_nodes.update(neighbours)
        yield distance, neighbours.copy()






