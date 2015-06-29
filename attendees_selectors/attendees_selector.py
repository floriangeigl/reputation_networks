from abc import abstractmethod

from agents_connections.agents_connection import AgentsConnection


class AttendeesSelector(object):
    def __init__(self, agents_connection):
        self.con = agents_connection
        assert isinstance(self.con, AgentsConnection)

    @abstractmethod
    def get_attendees(self):
        pass

    def get_all_agents(self):
        return self.con.get_all_agents()