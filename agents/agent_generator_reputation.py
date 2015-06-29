from knowledge_generators.knowledgegenerator import KnowledgeGenerator
from agents.agent_generator import AgentGenerator
from agents.set_agent_reputation import SetAgentReputation

__author__ = 'iliremavriqi'


class AgentGeneratorReputation(AgentGenerator):
    def __init__(self, agent_type, knowledge_generator, default_reputation=1, *args, **kwargs):
        super(AgentGeneratorReputation, self).__init__(self, agent_type, knowledge_generator, *args, **kwargs)
        assert self.agent_type == SetAgentReputation
        self.reputation = default_reputation

    def generate_agent(self, agent_id=None, reputation=None, *args, **kwargs):
        if agent_id is not None:
            self.agent_id = agent_id
        else:
            self.agent_id += 1
        if reputation is None:
            reputation = self.reputation
        return self.agent_type(reputation=reputation, agent_id=self.agent_id,
                               knowledge=self.knowledge_generator.generate_knowledge(),
                               *self.args, **self.kwargs)
