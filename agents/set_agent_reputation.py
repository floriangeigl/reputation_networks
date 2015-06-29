from agents.set_agent import SetAgent

__author__ = 'iliremavriqi'

class SetAgentReputation(SetAgent):
    def __init__(self, reputation, *args, **kwargs):
        SetAgent.__init__(self, *args, **kwargs)
        if self.knowledge is None:
            self.knowledge = set()
        self.knowledge = self._convert_to_set(self.knowledge)
        assert isinstance(self.knowledge, set)
        self.reputation = reputation

    def __str__(self):
        return 'SetAgentReputation ID ' + str(self.id) + '; Reputation: ' + str(self.reputation) + '; words: ' + str(self.knowledge)
