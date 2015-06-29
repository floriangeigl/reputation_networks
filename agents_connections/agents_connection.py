from abc import abstractmethod

from agents.agent_generator import AgentGenerator
from graph_tool.all import *
from collections import defaultdict
from tools.printing import *


class AgentsConnection(object):
    def __init__(self, agent_generator, verbose=True):
        assert isinstance(agent_generator, AgentGenerator)
        self.verbose = verbose
        self.agent_generator = agent_generator

    def get_graph(self, directed=False):
        all_agents = self.get_all_agents()
        g = Graph(directed=directed)
        vertex_mapper = defaultdict(lambda: g.add_vertex())
        node_id = g.new_vertex_property('int')
        for i in all_agents:
            iv = vertex_mapper[int(i)]
            node_id[iv] = int(i)
            for j in all_agents:
                if i != j:
                    if self.are_connected([i, j]):
                        jv = vertex_mapper[int(j)]
                        g.add_edge(iv, jv)
        g.vp['NodeId'] = node_id
        remove_parallel_edges(g)
        return g


    @abstractmethod
    def add_agent(self, agent):
        '''
        adds agents.py to the network
        :param agent: agents.py to add
        '''
        pass

    @abstractmethod
    def __delitem__(self, agent):
        '''
        removes agents.py from network
        :param agent: agents.py to remove
        '''
        pass

    @abstractmethod
    def __iter__(self):
        '''
        iters through agents
        :return: iterator
        '''
        pass

    @abstractmethod
    def get_connected_agents(self, agent):
        '''
        returns
        :param agent: source agents.py
        :return: connected agents
        '''
        pass

    def are_connected(self, agents):
        '''
        checks if all agents are connected
        :param agents: iterable of agents
        :return: True if each agents is connected to all other agents
        '''
        pass

    def connect_agents(self, agents):
        '''
        creates a connection between given agents
        :param agents: iterable of agents
        '''
        pass

    def disconnect_agents(self, agents):
        '''
        deletes all connections between given agents
        :param agents: iterable of agents
        '''
        pass

    @abstractmethod
    def __len__(self):
        '''
        returns number of agents in network
        :return: number of agents in network
        '''
        pass

    @abstractmethod
    def get_all_agents(self):
        '''
        returns a set containing all agents
        :return: set of all contained agents
        '''
        pass

    @abstractmethod
    def get_random_agent(self):
        '''
        returns a random agent
        :return: random agent
        '''
        pass

    @abstractmethod
    def to_pickle(self, filename):
        '''
        serializes agents network including all agents to pickle
        :param filename: filename of resulting pickle-file
        '''
        pass

    @abstractmethod
    def read_pickle(self, filename):
        '''
        reads agents network from pickle
        :param filename: filename of pickle-file
        '''

    def print_f(self, *args, **kwargs):
        kwargs.update({'class_name': str(type(self).__name__)})
        print_f(*args, **kwargs)
