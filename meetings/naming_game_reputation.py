import random
from meetings.naming_game import NamingGame
from agents.agent import Agent
from agents.set_agent_reputation import SetAgentReputation
import math

__author__ = 'spujari, iliremavriqi'



class  NamingGameReputation(NamingGame):
    def __init__(self, attendees_selector, beta, *args, **kwargs):
        NamingGame.__init__(self, attendees_selector, *args, **kwargs)
        self.__statistics = list()
        self.beta = beta

    def meet(self, *args, **kwargs):
        agents = self.attendees_selector.get_attendees()
        # get the speaker and listener
        speaker, listeners = agents[0], agents[1:]

        assert isinstance(speaker, SetAgentReputation)
        assert all(isinstance(i, Agent) for i in listeners)
        beta = self.beta
        meet_probability = 0
        for l in listeners:
            delta = speaker.reputation - l.reputation
            try:
                meet_probability = min(1, math.exp(delta * beta))
            except OverflowError:
                meet_probability = int(delta > 0)

        perform_meeting = meet_probability > random.random()
        for l in listeners:
            self.__statistics.append(
                (self.iteration, speaker.get_id(), speaker.reputation, l.get_id(), l.reputation, perform_meeting))
        if perform_meeting:
            super(NamingGameReputation, self).meet(*args, **kwargs)
        else:
            super(NamingGame, self).meet(*args, **kwargs)

    def get_statistics(self):
        return self.__statistics
