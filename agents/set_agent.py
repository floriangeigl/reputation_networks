from agents.agent import Agent
from lib.utils import *

class SetAgent(Agent):
    def __init__(self, *args, **kwargs):
        Agent.__init__(self, *args, **kwargs)
        if self.knowledge is None:
            self.knowledge = set()
        self.knowledge = self._convert_to_set(self.knowledge)
        assert isinstance(self.knowledge, set)

    @staticmethod
    def _convert_to_set(iterable):
        return convert_to_set(iterable)

    def add_knowledge(self, knowledge, iteration=None):
        if hasattr(knowledge, '__iter__'):
            knowledge = self._convert_to_set(knowledge)
            self.knowledge.update(knowledge)
        else:
            self.knowledge.add(knowledge)

    def remove_knowledge(self, knowledge):
        if hasattr(knowledge, '__iter__'):
            knowledge = self._convert_to_set(knowledge)
            self.knowledge -= knowledge
        else:
            self.knowledge.discard(knowledge)

    def set_knowledge(self, knowledge, iteration=None):
        self.knowledge = self._convert_to_set(knowledge)

    def __delitem__(self, key):
        try:
            self.knowledge.remove(key)
            return True
        except KeyError:
            return False

    def __add__(self, other):
        return self.knowledge | other.get_knowledge()

    def __str__(self):
        return 'SetAgent ' + str(self.id) + ': ' + ','.join(sorted(self.knowledge))


