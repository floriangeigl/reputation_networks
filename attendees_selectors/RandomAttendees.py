import random

from attendees_selector import AttendeesSelector
from lib.network import bfs_level_iter


class RandomAttendees(AttendeesSelector):
    def __init__(self, agents_connection, size=2, connected=True, pairwise_connected=False, *args, **kwargs):
        AttendeesSelector.__init__(self, agents_connection)
        assert 2 <= size
        self.size = size
        self.connected = connected
        self.pairwise_connected = pairwise_connected

    def get_attendees(self):
        attendees = []
        while len(attendees) < 2:
            attendees = []
            if self.connected:
                main_agent = self.con.get_random_agent()
                attendees.append(main_agent)
                connected_agents = self.con.get_connected_agents(main_agent)
                if connected_agents:
                    random.shuffle(connected_agents)
                    attendees.extend(connected_agents)
                    if self.pairwise_connected:
                        pairwise_connected_attendees = attendees[:2]
                        for i in attendees[2:]:
                            if self.con.are_connected(pairwise_connected_attendees + [i]):
                                pairwise_connected_attendees.append(i)
                    else:
                        attendees = attendees[:self.size]
            else:
                attendees = [self.con.get_random_agent() for i in xrange(self.size)]
        random.shuffle(attendees)
        return attendees