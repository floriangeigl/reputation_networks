from __future__ import division
from tools.printing import *
from tools.pd_tools import plot_df
import pandas as pd
import copy
from attendees_selectors.attendees_selector import AttendeesSelector
from collections import defaultdict


class Meeting(object):
    ACTION_TYPE_SET = 1
    ACTION_TYPE_ADD = 2
    ACTION_TYPE_DELETE = 3
    ACTION_TYPE_UNION = 4
    ACTION_TYPE_INTERSECT = 5
    ACTION_TYPE_REFRESH = 6

    def __init__(self, attendees_selector, data=None, log_step=1):
        self.print_f('init meetings')
        self.attendees_selector = attendees_selector
        assert isinstance(self.attendees_selector, AttendeesSelector)
        self.log_step = 1
        if data is None:
            self.print_f('add initial state of agents to log')
            self.log = pd.DataFrame(columns=['iteration', 'agent_id', 'action_type', 'knowledge'])
            self.log['iteration'] = self.log['iteration'].astype(int)
            self.log['agent_id'] = self.log['agent_id'].astype(int)
            self.log['action_type'] = self.log['action_type'].astype(int)
            self.iteration = 0
            for a in self.attendees_selector.get_all_agents():
                self.add_to_log(a, self.ACTION_TYPE_SET)
        else:
            self.log = data
            self.iteration = data['iteration'].max()
        self.log_step = log_step
        self.next_log_point = 0
        self.changed_agents = dict()
        self.last_knowledge_state = defaultdict(lambda: (None, None))
        self.next_log_point = log_step
        self.last_percent = -1
        self.tmp_iter_counter = 0
        self.print_f('setup done')
        self.memory_usage = []

    def get_attendees(self):
        return self.attendees_selector.get_all_agents()

    @staticmethod
    def read_from_pickle(filename):
        return Meeting(pd.read_pickle(filename))

    def add_to_log(self, agent, action_type):
        # knowledge = convert_to_iterable(knowledge)
        if self.log_step > 1:
            if self.iteration > self.next_log_point:
                for a, (action, knowledge) in self.changed_agents.iteritems():
                    if self.last_knowledge_state[a][1] != knowledge:
                        self.log.loc[len(self.log)] = [self.next_log_point, a.get_id(), action_type, knowledge]
                self.next_log_point += self.log_step
                self.last_knowledge_state.update(self.changed_agents)
                self.changed_agents = dict()
            self.changed_agents[agent] = (action_type, copy.copy(agent.get_knowledge(self.next_log_point)))
        else:
            agent_id = agent.get_id()
            self.log.loc[len(self.log)] = [self.iteration, agent_id, action_type, copy.copy(agent.get_knowledge(self.iteration))]

    def meet(self, max_meetings=None, num_meetings=1, status_each=1):
        '''
        performs a meeting of agents
        '''
        assert num_meetings > 0
        if self.tmp_iter_counter >= num_meetings:
            self.tmp_iter_counter = 0
        self.tmp_iter_counter += 1
        if self.tmp_iter_counter == 1:
            self.iteration += 1

        if max_meetings is not None:
            if self.iteration == self.tmp_iter_counter == 1:
                self.last_percent = 0
            c_percent = int(self.iteration / max_meetings * 100)
            if c_percent > self.last_percent + (status_each - 1) or status_each == 0:
                self.last_percent = c_percent
                mem_consumption = get_memory_consumption_in_mb()
                self.memory_usage.append((self.iteration, mem_consumption))
                self.print_f('iteration:', str(self.iteration).rjust(len(str(max_meetings))),
                             '\t(' + str(c_percent).rjust(3, '0') + '% || mem: ', str(mem_consumption).split('.')[0],
                             'MB )')
        else:
            self.print_f('iteration:', self.iteration)
        for i in self.attendees_selector.get_all_agents():
            i.per_iteration(self.iteration)

    def get_log(self):
        return self.log

    def get_mem_usage(self):
        idx, mem = zip(*self.memory_usage)
        return pd.Series(data=mem, index=idx)

    def plot_mem_usage(self, filename='mem_consumption', lw=2, alpha=0.8, **kwargs):
        plot_df(self.get_mem_usage(), filename, max=False, min=False, median=False, mean=False, x_label='iteration',
            y_label='memory usage in MB', alpha=alpha, lw=lw, **kwargs)

    def print_f(self, *args, **kwargs):
        kwargs.update({'class_name': str(type(self).__name__)})
        print_f(*args, **kwargs)

    def save(self, filename):
        '''
        Saves serialised version of meeting to file
        :param filename: output filename
        '''
        filename = filename if filename.endswith('.df') else filename + '.df'
        self.log.to_pickle(filename)