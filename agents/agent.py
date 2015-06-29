from abc import abstractmethod
import random


class Agent(object):
    def __init__(self, agent_id, knowledge=None):
        self.knowledge = knowledge
        self.id = agent_id

    def __hash__(self):
        return hash(self.id)

    def __contains__(self, item):
        '''
        Returns True if knowledge in agents knowledge
        :param knowledge: piece of knowledge
        :return: True if knowledge in agents knowledge
        '''
        return item in self.get_knowledge()

    def __len__(self):
        '''
        :return: size of agents knowledge
        '''
        return len(self.get_knowledge())

    def set_knowledge(self, knowledge, iteration=None):
        '''
        sets the knowledge of the agents
        :param knowledge: new knowledge
        '''
        self.knowledge = knowledge

    def get_knowledge(self, iteration=None):
        '''
        returns agents knowledge
        :return: agents knowledge
        '''
        return self.knowledge

    def get_random_knowledge(self, iteration=None, size=1):
        '''
        returns a random piece of agents knowledge
        :return: random piece of agents knowledge
        '''
        current_know = self.get_knowledge(iteration=iteration)
        try:
            result = random.sample(current_know, size)
        except ValueError:
            result = current_know
        if len(result) == 1:
            result = result[0]
        return result

    def __eq__(self, other):
        '''

        :param other: other agents
        :return: returns True if both agents have the same knowledge
        '''
        return self.id == other.get_id()

    def __iter__(self):
        '''
        iters through knowledge
        :return: knowledge iterator
        '''
        for i in self.get_knowledge():
            yield i

    def get_id(self):
        return self.id

    def __int__(self):
        return self.id

    def __str__(self):
        '''
        Creates Printable version of Agent
        :return: Information of agents in String
        '''
        return 'Agent ' + str(self.id) + ': ' + str(self.get_knowledge())

    @abstractmethod
    def add_knowledge(self, knowledge, iteration=None):
        '''
        :param knowledge: new knowledge
        :return: adds new knowledge to agents knowledge
        '''
        pass

    def per_iteration(self, iteration=None):
        '''
        performs a task which should be performed before each meeting
        :return:
        '''
        pass

    def refresh_knowledge(self, knowledge, iteration=None):
        '''

        :param knowledge: knowledge to be refreshed
        :return:
        '''
        pass

    @abstractmethod
    def remove_knowledge(self, knowledge):
        '''

        :param knowledge: knowledge
        :return: removes knowledge from agents knowledge
        '''
        pass

    @abstractmethod
    def __delitem__(self, key):
        '''

        :param key: piece of knowledge to remove
        :return: True if key was in agents knowledge
        '''
        pass

    def __add__(self, other):
        '''
        returns the combined knowledge of two agents
        :param other:
        :return: combined knowledge
        '''
        return self.knowledge + other.get_knowledge()

    def __iadd__(self, other):
        self.knowledge += other.get_knowledge()

    def __sub__(self, other):
        '''
        returns own knowledge without knowledge of other agents.
        :param other: other agents
        :return: returns knowledge of agents minus knowledge of other agents
        '''
        return self.knowledge - other.get_knowledge()

    def __isub__(self, other):
        self.knowledge -= other.get_knowledge()

