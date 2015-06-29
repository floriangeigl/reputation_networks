from agents.agent_generator_reputation import AgentGeneratorReputation
from agents_connections.network_reputation import AgentsNetworkReputation
from knowledge_generators.random_sample import RandomSampleKnowledgeGenerator
from lib.plotting import *
from attendees_selectors.RandomAttendees import RandomAttendees
from meetings.naming_game_reputation import NamingGameReputation
from agents.set_agent_reputation import SetAgentReputation
from lib.pandas_utils import store_meeting_statistics

__author__ = 'iliremavriqi'

def main():
    language = "german"
    network_filename = 'datasets/stackexchange/'+language+'/'+language+'_reputation_net.gt'

    know_size = 3  # each agent has 3 words
    number_of_unique_words = 100
    num_meetings = 2000001
    max_orig_lines = 100
    log_step = 20000

    # different betas tried over time
    # beta = [0, 0.0001, 0.001, 0.01, 0.1, 1, 2, 3]
    # beta = [0.00001, 0.00005, 0.0001, 0.0002,0.0003, ..., 0.0008, 0.0009, 0.001]
    # beta = [0, 0.00001, 0.0001, 0.00013, 0.00016, 0.0002, 0.001, 1]
    beta = 0

    know_gen = RandomSampleKnowledgeGenerator(population=number_of_unique_words, sample_size = know_size)
    agent_gen = AgentGeneratorReputation(SetAgentReputation, know_gen)
    con = AgentsNetworkReputation(agent_gen, network_filename=network_filename, largest_component=False,
                                  vprop_node_id='nodeID', reputation='reputation')

    path = 'datasets/stackexchange/'+language+'/output_reputation/'+language
    statistics_filename = path+'_statistics.txt'
    if not os.path.exists(os.path.dirname(statistics_filename)):
        os.makedirs(os.path.dirname(statistics_filename))

    attendee_select = RandomAttendees(con)
    meeting = NamingGameReputation(attendee_select, beta=beta, log_step=log_step)
    for i in range(num_meetings):
        meeting.meet(max_meetings=num_meetings)

    # get nodes that converged and those that did not converge
    all_agents = con.get_all_agents()
    num_agents = len(all_agents)
    low_deg_agents = set(map(int, filter(lambda agent: agent.get_knowledge() > 1, all_agents)))
    num_low_deg_agents = len(low_deg_agents)

    print_f('nodes with more than 1 words: ', low_deg_agents)
    print_f('number nodes with more than 1 words: ', num_low_deg_agents)

    num_high_deg_agents = num_agents - num_low_deg_agents
    low_agents_percentage = 100 * num_low_deg_agents / num_agents
    high_agents_percentage = 100 * num_high_deg_agents / num_agents

    # write statistics in a file
    with open(statistics_filename, "a") as f:
        f.write('\n')
        f.write(
            '-------------------------------------------------------------------------------------------------------------------')
        f.write('\n')
        f.write('network: ' + language + '; beta= ' + str(beta) + '; interactions: ' + str(num_meetings))
        f.write('\n')
        f.write('total number of agents: ' + str(num_agents))
        f.write('\n')
        f.write('agents with more than 1 words: ' + str(low_deg_agents))
        f.write('\n')
        f.write('number of agents with more than 1 words: ' + str(num_low_deg_agents))
        f.write('\n')
        f.write('percentage of low degree agents (> 1 word): ' + str(round(low_agents_percentage)) + '%')
        f.write('\n')
        f.write('number of agents that converged (=1 word): ' + str(num_high_deg_agents) + ' percentage: ' + str(
            round(high_agents_percentage)) + '%')

    knowsize_filename = path + '_knowsize_beta='
    pickle_filename = path + '_statistics_beta=' + str(beta) + '.pickle'

    #Plotting.plot_knowledge_count(con,'datasets/stackexchange/'+language+'/output_reputation/afterMeetingRep_wordCount_beta='+str(beta)+'.png')
    #Plotting.plot_knownby_size(meeting, 'datasets/stackexchange/'+language+'/output_reputation/naming_game_knownby_beta='+str(beta)+'.png', max_orig_lines=max_orig_lines)
    #Plotting.animate_knowledge_size(meeting, 'datasets/stackexchange/'+language+'/output_reputation/naming_game_know_size_animation', agents_network=agents_network, ips=1, plot_each=5, smoothing=15)
    #Plotting.animate_knownby(meeting, 'output/naming_game_knownby_animation', fps=1, plot_each=100, smoothing=30)

    #Plotting.plot_words_correlation(agents_network, 'datasets/stackexchange/'+language+'/output_reputation/naming_game_cor_words_reputation_beta='+str(beta), correlation_metric='reputation')
    #Plotting.plot_words_correlation(agents_network, 'datasets/stackexchange/'+language+'/output_reputation/naming_game_cor_words_deg', correlation_metric='deg')
    #Plotting.plot_words_correlation(agents_network, 'datasets/stackexchange/'+language+'/output_reputation/naming_game_cor_words_local_clustering_coefficient', correlation_metric='clustering_coefficient')
    #Plotting.plot_words_correlation(agents_network, 'datasets/stackexchange/'+language+'/output_reputation/naming_game_cor_words_outdeg', correlation_metric='outdeg')
    #Plotting.plot_words_correlation(agents_network, 'datasets/stackexchange/'+language+'/output_reputation/naming_game_cor_reputation_outdeg_beta='+str(beta), correlation_metric='reputation_outdeg')
    #Plotting.plot_words_correlation(agents_network, 'datasets/stackexchange/'+language+'/output/naming_game_cor_words_trust_transitivity', correlation_metric='trust_transitivity')
    #Plotting.plot_words_correlation(agents_network, 'datasets/stackexchange/'+language+'/output_reputation/naming_game_cor_words_eigenvector', correlation_metric='eigenvector')
    #Plotting.plot_words_correlation(agents_network, 'datasets/stackexchange/'+language+'/output_reputation/naming_game_cor_words_pagerank', correlation_metric='pagerank')
    #Plotting.plot_reputation_networks_fs(agents_network, filename='datasets/stackexchange/'+language+'/output_reputation/naming_game_final_state_beta='+str(beta)+'.png')

    print_f('start plot_knowledge_size')
    Plotting.plot_knowledge_size(meeting, beta, language, knowsize_filename,
                                 path + '_know_size_beta=' + str(beta) + '.pdf', max_orig_lines=max_orig_lines)
    store_meeting_statistics(meeting, pickle_filename)

if __name__ == '__main__':
    main()
