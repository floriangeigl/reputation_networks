from agents_connections.network import AgentsNetwork
from agents.set_agent_reputation import SetAgentReputation

__author__ = 'iliremavriqi'

class AgentsNetworkReputation(AgentsNetwork):
    def __init__(self, agent_generator, network_filename=None, largest_component=False, directed=False, vprop_node_id='nodeID', reputation='reputation',**kwargs):
        AgentsNetwork.__init__(self, agent_generator, network_filename, largest_component, directed, vprop_node_id, **kwargs)
        reputations = self.net.vp[reputation]
        agents = self.net.vp['agents']
        for v in self.net.vertices():
            a = agents[v]
            assert isinstance(a, SetAgentReputation)
            a.reputation = reputations[v]
