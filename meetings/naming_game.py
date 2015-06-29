from meeting import Meeting
from agents.agent import Agent


class NamingGame(Meeting):
    def __init__(self, attendees_selector, *args, **kwargs):
        Meeting.__init__(self, attendees_selector, *args, **kwargs)

    def meet(self, *args, **kwargs):
        super(NamingGame, self).meet(*args, **kwargs)
        agents = self.attendees_selector.get_attendees()
        speaker, listeners = agents[0], agents[1:]
        assert isinstance(speaker, Agent)
        assert all(isinstance(i, Agent) for i in listeners)
        piece_of_knowledge = speaker.get_random_knowledge()
        if all(piece_of_knowledge in l for l in listeners):
            speaker.set_knowledge(piece_of_knowledge)
            self.add_to_log(speaker, self.ACTION_TYPE_SET)
            for l in listeners:
                l.set_knowledge(piece_of_knowledge)
                self.add_to_log(l, self.ACTION_TYPE_SET)
        else:
            speaker.refresh_knowledge(piece_of_knowledge)
            self.add_to_log(speaker, self.ACTION_TYPE_REFRESH)
            for l in listeners:
                if piece_of_knowledge not in l:
                    l.add_knowledge(piece_of_knowledge)
                    self.add_to_log(l, self.ACTION_TYPE_ADD)
