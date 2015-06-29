import graph_tool as gt
import random

from lib.network import read_edge_list
from agents_connection import AgentsConnection


class AgentsNetwork(AgentsConnection):
    def __init__(self, agent_generator, network_filename=None, largest_component=False, directed=False, vprop_node_id='nodeID', **kwargs):
        AgentsConnection.__init__(self, agent_generator, **kwargs)
        if network_filename is None:
            self.net = gt.Graph(directed=directed)
        else:
            try:
                self.print_f('load gt file', network_filename)
                self.net = gt.load_graph(network_filename)
                if self.net.is_directed() != directed:
                    self.net.set_directed(directed)
            except:
                self.print_f('failed. fall back to read edge list')
                self.net = read_edge_list(network_filename, directed=directed)

        if largest_component:
            self.print_f('reduce network to largest component')
            lc = gt.topology.label_largest_component(self.net)
            self.net.set_vertex_filter(lc)
            self.net.purge_vertices()

        self.print_f('create agents')
        self.agent_to_vertex = dict()
        agents_pmap = self.net.new_vertex_property('object')
        node_id_pmap = self.net.new_vertex_property('int')
        try:
            node_ids = self.net.vp[vprop_node_id]
        except KeyError:
            self.print_f('No vertex property named:', vprop_node_id)
            self.print_f('Available vertex properties:', self.net.vp.keys())
            self.print_f('Please use "vprop_node_id" param to specify the right one')
            exit()

        for agent_id, v in enumerate(self.net.vertices()):
            agent = self.agent_generator.generate_agent(node_ids[v])
            self.agent_to_vertex[agent] = v
            agents_pmap[v] = agent
            node_id_pmap[v] = int(agent)
        self.net.vp["agents"] = agents_pmap
        self.net.vp["NodeId"] = node_id_pmap
        self.print_f('setup done')

    def get_graph(self, directed=False):
        return self.net

    def add_agent(self, agent):
        self.agent_to_vertex[agent] = self.net.add_vertex()

    def __delitem__(self, agent):
        index_of_deleted_agent = int(self.agent_to_vertex[agent])
        last_agent = self.net.vertex_properties["agents"][self.net.num_vertices() - 1]
        self.net.remove_vertex(self.agent_to_vertex[agent], fast=True)
        self.agent_to_vertex[last_agent] = self.net.vertex(index_of_deleted_agent)

    def __iter__(self):
        for i in self.agent_to_vertex.keys():
            yield i

    def get_connected_agents(self, agent):
        av = self.agent_to_vertex[agent]
        return [self.net.vertex_properties["agents"][nv] for nv in av.out_neighbours()]

    def connect_agents(self, agents):
        agents_v = [self.agent_to_vertex[a] for a in agents]
        for i in agents_v:
            for j in agents_v:
                if i != j:
                    if self.net.edge(i, j) is None:
                        self.net.add_edge(i, j)

    def disconnect_agents(self, agents):
        agents_v = [self.agent_to_vertex[a] for a in agents]
        for i in agents_v:
            for j in agents_v:
                if i != j:
                    edge = self.net.edge(i, j)
                    if edge:
                        self.net.remove_edge(edge)

    def are_connected(self, agents):
        agents_v = [self.agent_to_vertex[a] for a in agents]
        return all((not self.net.edge(s, t) is None for s in agents_v for t in agents_v if s != t))

    def __len__(self):
        return self.net.num_vertices()

    def get_all_agents(self):
        return self.agent_to_vertex.keys()

    def get_random_agent(self):
        return random.sample(self.agent_to_vertex.keys(), 1)[0]

    def to_pickle(self, filename):
        pass

    def read_pickle(self, filename):
        pass
