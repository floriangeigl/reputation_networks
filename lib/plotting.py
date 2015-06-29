from __future__ import division
from statsmodels.datasets import spector
from sys import platform as _platform
import matplotlib
if _platform == "linux" or _platform == "linux2":
    matplotlib.use('Agg')
import matplotlib.pylab as plt
import pandas as pd
import numpy as np
from meetings.meeting import Meeting
from collections import defaultdict
import operator
import matplotlib.cm as colormap
import warnings
import math
from graph_tool.all import *
import os
import lib.pandas_utils as pandas_utils
from DynamicNetworkViz.dyn_net_viz import graph_viz
from tools.printing import *
import tools.pd_tools as pd_tools
from operator import itemgetter
from matplotlib.colors import ColorConverter


class Plotting():
    @staticmethod
    def plot_knowledge_size(log, beta, language,  knowsize_filename, filename, step_size=1, **kwargs):
        Plotting.print_f('plot knowledge size')
        df = pandas_utils.get_knowledge_size_series(log) if isinstance(log, Meeting) else log
        assert isinstance(df, pd.DataFrame)
        if step_size > 1:
            keep_mask = df.index[(np.array(df.index) % step_size).astype('bool')]
            df.drop(keep_mask, axis=0, inplace=True)

        df.to_pickle(knowsize_filename +str(beta)+'.pickle')
        Plotting.plot_df_reputation(knowsize_filename, filename, language, max=False, min=False, median=False, mean=True, x_label='interactions', y_label='agents inventory size', **kwargs)
        plt.close('all')
        return df

    @staticmethod
    def plot_knownby_size(log, filename, check_each_iter=False, step_size=1, **kwargs):
        Plotting.print_f('plot known by size')
        df, _ = pandas_utils.get_knownby_series(log, check_each_iter=check_each_iter) if isinstance(log, Meeting) else log
        assert isinstance(df, pd.DataFrame)
        #size_df = df.copy(deep=True)
        if step_size > 1:
            df.drop(df.index[df['iteration'] % step_size != 0], axis=0, inplace=True)
        df['knownby'] = df['knownby'].apply(len)
        df = pd.pivot_table(df, columns=['vertex'], index=['iteration'], aggfunc='max')
        df.ffill(inplace=True)
        Plotting.plot_df(df, filename, x_label='iteration', y_label='#agents who have the node in their knowledge', **kwargs)
        plt.close('all')
        return df

    @staticmethod
    def plot_df(*args, **kwargs):
        return pd_tools.plot_df(*args, **kwargs)

    @staticmethod
    def plot_df_reputation(*args, **kwargs):
        return pd_tools.plot_df_reputation(*args, **kwargs)

    @staticmethod
    def print_f(*args, **kwargs):
        kwargs.update({'class_name': 'Plotting'})
        print_f(*args, **kwargs)

    @staticmethod
    def animate_knowledge_size(meeting, filename, agents_network=None, verbose=1, **kwargs):
        start = datetime.datetime.now()
        Plotting.print_f('Animate knowledge size evolution')
        if isinstance(meeting, pd.DataFrame):
            df = meeting
        else:
            if verbose >= 1:
                Plotting.print_f('get known by series')
            df, agents_network = pandas_utils.get_agents_knowledge_series(meeting, agents_network, verbose=verbose)
        animator = graph_viz(df, agents_network, df_opinion_key='knowledge', df_vertex_key='agent', filename=filename, verbose=verbose, max_node_alpha=1.0, **kwargs)
        result = animator.plot_network_evolution(delete_pictures=False)
        if verbose:
            Plotting.print_f('animating took', datetime.datetime.now() - start)
        return result

    @staticmethod
    def animate_knownby(meeting, filename, knowledge_graph=None, verbose=1, **kwargs):
        start = datetime.datetime.now()
        Plotting.print_f('Animate known by size evolution')
        if isinstance(meeting, pd.DataFrame):
            df = meeting
        else:
            if verbose >= 1:
                Plotting.print_f('get known by series')
            df, knowledge_graph = pandas_utils.get_knownby_series(meeting, knowledge_graph, verbose=verbose)
        # print df[df.iteration != df.iteration.max()]
        animator = graph_viz(df, knowledge_graph, df_opinion_key='knownby', filename=filename, verbose=verbose, **kwargs)
        result = animator.plot_network_evolution()
        if verbose:
            Plotting.print_f('animating took', datetime.datetime.now() - start)
        return result

    @staticmethod
    def plot_reputation_networks_fs(network, filename='output/final_state.png', dpi=80, width=15, height=15, alpha=1.,
                                    colors_dict=None, sfdp_C=2, sfdp_p=6, node_shrink_fac=0.25, font_size=28,
                                    binary_decision=None):
        # calc values
        color_converter = ColorConverter()
        agents_pmap = network.vp['agents']
        if colors_dict is None:
            colors_dict = defaultdict(lambda: color_converter.to_rgba('blue'))   # covers cases with #words > 3
            colors_dict[1] = color_converter.to_rgba('green')   # one word
            colors_dict[2] = color_converter.to_rgba('blue')  # two words
            colors_dict[3] = color_converter.to_rgba('red')    # three and more words
        for key, val in colors_dict.iteritems():
            if isinstance(val, str):
                val = color_converter.to_rgba(val)
            colors_dict[key] = val[:3] + tuple([alpha])

        colors_pmap = network.new_vertex_property('vector<double>')
        shape_pmap = network.new_vertex_property('int')
        used_keys = set()
        for v in network.vertices():
            agent_size = len(agents_pmap[v])
            if binary_decision is not None:
                agent_size = 1 if agent_size > 1 else 0
            used_keys.add(agent_size)
            colors_pmap[v] = colors_dict[agent_size]
            shape_pmap[v] = agent_size

        colors_dict = {key: val for key, val in colors_dict.iteritems() if key in used_keys}

        # calc node-size
        res = (dpi * height, dpi * width)
        tmp_output_size = min(res) * 0.7
        num_nodes = network.num_vertices()
        if num_nodes < 10:
            num_nodes = 10
        max_vertex_size = np.sqrt((np.pi * tmp_output_size ** 2) / num_nodes)
        if max_vertex_size < 1:
            max_vertex_size = 1
        min_vertex_size = max(max_vertex_size * node_shrink_fac, 1)
        deg_pmap = network.degree_property_map('total')
        verterx_size = prop_to_size(deg_pmap, mi=min_vertex_size, ma=max_vertex_size, power=1)

        # plot
        plt.close('all')
        plt.switch_backend('cairo')
        f, ax = plt.subplots(figsize=(width, height))
        tmp = ["o", "^", "s", "p", "h", "H", "8", "double_circle", "double_triangle", "double_square",
               "double_pentagon", "double_hexagon", "double_heptagon", "double_octagon"]

        if binary_decision:
            gt_shape_to_plt_shape = {idx: val for idx, val in enumerate(tmp)}
        else:
            gt_shape_to_plt_shape = {idx+1: val for idx, val in enumerate(tmp)}

        for key, val in sorted(colors_dict.iteritems(), key=lambda x: x[0]):
            label = str(key) + ' ' + ('word' if key == 1 else 'words')
            if binary_decision is not None:
                label = binary_decision[key]
            ax.plot(None, label=label, color=val, ms=font_size, marker=gt_shape_to_plt_shape[key], lw=10, alpha=alpha, ls='')

        pos = sfdp_layout(network, C=sfdp_C, p=sfdp_p)
        graph_draw(network, pos=pos, vertex_shape=shape_pmap, edge_color=[0.179, 0.203, 0.210, alpha / 6], vertex_size=verterx_size, output_size=res, mplfig=ax, vertex_fill_color=colors_pmap)  # , bg_color=color_converter.to_rgba('white'))
        plt.legend(loc='upper right', prop={'size': font_size})
        plt.axis('off')
        plt.savefig(filename, bbox_inches='tight', dpi=dpi)
        plt.close('all')
        plt.switch_backend('Agg')

    @staticmethod
    def plot_words_correlation(network, filename, agents_pmap='agents', correlation_metric='deg', dpi=150, lw=0, alpha=0.25, **kwargs):
        correlation_metric_name = correlation_metric
        if correlation_metric == 'deg':
            correlation_metric = network.degree_property_map('total')
        elif correlation_metric == 'indeg':
            correlation_metric = network.degree_property_map('in')
        elif correlation_metric == 'outdeg':
            correlation_metric = network.degree_property_map('out')
        elif correlation_metric == 'pagerank':
            correlation_metric = pagerank(network)
        elif correlation_metric == 'eigenvector':
            _, correlation_metric = eigenvector(network)
        elif correlation_metric == 'clustering_coefficient':
            correlation_metric = local_clustering(network)
        elif correlation_metric == 'betweenness':
            correlation_metric, _ = betweenness(network)
        elif correlation_metric == 'closeness':
            correlation_metric = closeness(network)
        elif correlation_metric == 'trust_transitivity':
            correlation_metric = trust_transitivity(network)
        elif correlation_metric == 'eigentrust':
            correlation_metric = eigentrust(network)
        elif correlation_metric == 'authority':
            _, correlation_metric, _ = hits(network)
        elif correlation_metric == 'hub':
            _, _, correlation_metric = hits(network)
        elif correlation_metric == 'reputation':
            correlation_metric = network.vp['reputation']
        # pagerank(network) network.degree_property_map('out')
        if isinstance(agents_pmap, str):
            agents_pmap = network.vp[agents_pmap]
        if correlation_metric == 'reputation_outdeg':
            data = [(network.vp['reputation'][v], network.degree_property_map('out')[v]) for v in network.vertices()]
            x = 'reputation scores'
            y = 'node degree'
        else:
            data = [(len(agents_pmap[v].get_knowledge()), correlation_metric[v]) for v in network.vertices()]
            x = '#words'
            y = correlation_metric_name
            plt.xlim(0,5)
        df = pd.DataFrame(columns=[x, y], data=data)
        df.plot(kind='scatter', x=x, y=y, lw=lw, alpha=alpha,**kwargs)

        if not (filename.endswith('.png') or filename.endswith('.pdf')):
            filename += '.png'
        plt.xlabel(x)
        plt.ylabel(y)
        plt.savefig(filename, dpi=dpi, bbox_inches='tight')

    @staticmethod
    def plot_knowledge_count(agent_network, filename):

        word_dict = dict()
        agent_list = agent_network.get_all_agents()
        for agent_item in agent_list:
            for word in agent_item.knowledge:
                if word not in word_dict:
                    word_dict[word] = 0
                word_dict[word] = word_dict[word] + 1

        word_count_tuple_list = word_dict.items()
        word_count_tuple_list = sorted(word_count_tuple_list, key=itemgetter(1))
        print word_count_tuple_list

        x = list()
        y = list()

        for item in word_count_tuple_list:
            word = item[0]
            count = item[1]
            x.append(word)
            y.append(count)

        plt.scatter(x, y, s=30, vmin = 0, vmax= 100, alpha=0.5)
        plt.savefig(filename)





