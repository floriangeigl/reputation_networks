from knowledge_generators.knowledgegenerator import KnowledgeGenerator


class AgentGenerator(object):
    def __init__(self, agent_type, knowledge_generator, *args, **kwargs):
        self.agent_type = agent_type
        self.agent_id = -1
        assert isinstance(knowledge_generator, KnowledgeGenerator)
        self.knowledge_generator = knowledge_generator
        self.args = args
        self.kwargs = kwargs

    def generate_agent(self, agent_id=None, *args, **kwargs):
        if agent_id is not None:
            self.agent_id = agent_id
        else:
            self.agent_id += 1
        #print self.knowledge_generator.generate_knowledge()
        return self.agent_type(agent_id=self.agent_id, knowledge=self.knowledge_generator.generate_knowledge(),
                               *self.args, **self.kwargs)


