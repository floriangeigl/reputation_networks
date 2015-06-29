import pandas as pd
from meetings.meeting import Meeting
import warnings
from graph_tool.all import *
from lib.utils import *
from collections import defaultdict
import operator
import numpy as np
from copy import copy, deepcopy
from tools.printing import *

pd.set_option('display.max_colwidth', 100000)
pd.set_option('display.width', 100000)
pd.set_option('display.max_rows', 10000)


def get_log(log):
    if isinstance(log, Meeting):
        log = log.get_log()
    return log


def get_knowledge_size_series(meeting):
    log = get_log(meeting)
    no_change_agents = set(log[log['iteration'] == 0]['agent_id']) - set(log[log['iteration'] != 0]['agent_id'])
    df = pd.pivot_table(log, values='knowledge', index='iteration', columns='agent_id', aggfunc=lambda x: len(x.iloc[-1]))
    if len(no_change_agents) > 0:
        warn_message = str(len(no_change_agents)) + ' agents never changed their knowledge'
        warnings.warn(warn_message, RuntimeWarning)
    df.ffill(inplace=True)
    return df


def get_all_agent_ids(df, iteration=None):
    if iteration is None:
        data = df[df['iteration'] == df['iteration'].min()]
    else:
        data = df[df['iteration'] == iteration]
    return set.union(*list(data['knownby']))


def get_agents_knowledge_series(meeting, agents_network=None, verbose=0):
    if verbose >= 1:
        print_f('collect agents knowledge data', class_name='PandasUtils')
    assert isinstance(meeting, Meeting)
    df = meeting.get_log()
    if agents_network is None:
        overall_agents = meeting.get_attendees()
        agents_network = Graph()
        agents_network.vertex_properties['NodeId'] = agents_network.new_vertex_property('int')
        mapping = agents_network.vertex_properties['NodeId']
        for i in overall_agents:
            mapping[agents_network.add_vertex()] = i
    else:
        assert isinstance(agents_network, Graph)
        mapping = agents_network.vp['NodeId']
    reverse_mapping = dict()
    for v in agents_network.vertices():
        reverse_mapping[mapping[v]] = v
    df['agent'] = df['agent_id'].apply(func=lambda x, rev_map: rev_map[x], rev_map=reverse_mapping)
    # df.drop('agent_id',axis=1, inplace=True)
    if verbose >= 2:
        last_iter = -1
        for iteration, agent, knowledge in df:
            if last_iter != iteration:
                last_iter = iteration
                print_f(str(iteration).center(80, '='), class_name='PandasUtils')
            print_f(agent, 'knows', knowledge, class_name='PandasUtils')
    # df = pd.DataFrame(df, columns=['iteration', 'agent', 'knowledge'])
    df.sort('iteration', inplace=True)
    if verbose >= 2:
        print_f('resulting dataframe:', class_name='PandasUtils')
        print df
    return df, agents_network


def get_knownby_series_iter(meeting, knowledge_graph=None, check_each_iter=False):
    assert isinstance(meeting, Meeting)
    log = meeting.get_log()
    max_iteration = log['iteration'].max()
    if knowledge_graph is None:
        overall_knowledge = {i for j in log.knowledge for i in j}
        knowledge_graph = Graph()
        knowledge_graph.vertex_properties['NodeId'] = knowledge_graph.new_vertex_property('int')
        mapping = knowledge_graph.vertex_properties['NodeId']
        for i in overall_knowledge:
            v = knowledge_graph.add_vertex()
            mapping[v] = i
        yield 'graph', knowledge_graph
    else:
        assert isinstance(knowledge_graph, Graph)
        mapping = knowledge_graph.vp['NodeId']
    agents = meeting.get_attendees()
    agents = {int(agent): None for agent in agents}
    reverse_mapping = {mapping[v]: v for v in knowledge_graph.vertices()}
    known_by_dict = defaultdict(set)

    grouped_iter = log.groupby('iteration')
    last_iter_dict = None
    for iteration, data in grouped_iter:
        for _, row in data.iterrows():
            agent_id, action_type, knowledge = row[['agent_id', 'action_type', 'knowledge']]
            if (action_type == Meeting.ACTION_TYPE_ADD or action_type == Meeting.ACTION_TYPE_REFRESH) and not check_each_iter:
                agents[agent_id] = knowledge
                for i in knowledge:
                    if not isinstance(i, Vertex):
                        i = reverse_mapping[i]
                    known_by_dict[i].add(agent_id)

            elif action_type == Meeting.ACTION_TYPE_DELETE or action_type == Meeting.ACTION_TYPE_SET or check_each_iter:
                if agents[agent_id] is not None:  # zero iteration is None
                    for i in agents[agent_id]:
                        if not isinstance(i, Vertex):
                            i = reverse_mapping[i]
                        known_by_dict[i].remove(agent_id)
                agents[agent_id] = knowledge
                for i in knowledge:
                    if not isinstance(i, Vertex):
                        i = reverse_mapping[i]
                    known_by_dict[i].add(agent_id)
            else:
                print_f('Action Type unknown:', action_type, class_name='PandasUtils')

        if iteration != max_iteration:
            if last_iter_dict is not None:
                changed_dict = {key: val for key, val in known_by_dict.iteritems() if key not in last_iter_dict or last_iter_dict[key] != val}
            else:
                changed_dict = {key: val for key, val in known_by_dict.iteritems()}
        last_iter_dict = {key: copy(val) for key, val in known_by_dict.iteritems()}
        if iteration == max_iteration:
            yield iteration, last_iter_dict
        else:
            yield iteration, {key: copy(val) for key, val in changed_dict.iteritems()}


def get_knownby_series(meeting, knowledge_graph=None, check_each_iter=False, verbose=0):
    if verbose >= 1:
        print_f('collect known by data', class_name='PandasUtils')
    known_by_all_iterations = {iteration: data for iteration, data in
                               get_knownby_series_iter(meeting, knowledge_graph, check_each_iter=check_each_iter)}
    if verbose >= 1:
        print_f('convert to dataframe...', class_name='PandasUtils')
    if knowledge_graph is None:
        knowledge_graph = known_by_all_iterations.pop('graph')
    df = [(i, m, n) for i, j in sorted(known_by_all_iterations.iteritems(), key=operator.itemgetter(0)) for m, n in
          sorted(j.iteritems(), key=lambda x: int(x[0]))]
    if verbose >= 2:
        last_iter = -1
        for iteration, vertex, agents in df:
            if last_iter != iteration:
                last_iter = iteration
                print_f(str(iteration).center(80, '='), class_name='PandasUtils')
            print vertex, 'known by', agents
    df = pd.DataFrame(df, columns=['iteration', 'vertex', 'knownby'])
    df.sort(['iteration'], inplace=True)
    df.sort(inplace=True)
    if verbose >= 2:
        print_f('resulting dataframe:', class_name='PandasUtils')
        print df
    return df, knowledge_graph

def store_meeting_statistics(meeting, pickle_filename, **kwargs):
    df = pd.DataFrame(columns=['iteration', 'speakerID', 'speakerRep', 'listenerID', 'listenerRep', 'successful'],
                      data=meeting.get_statistics())
    df.to_pickle(pickle_filename)
