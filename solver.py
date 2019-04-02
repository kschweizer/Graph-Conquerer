import os
import sys
import networkx as nx
sys.path.append('..')
sys.path.append('../..')
import argparse
import utils
import heapq
from additional_utils import *
import random
import math

"""
======================================================================
  Complete the following function.
======================================================================
"""


def solve(list_of_kingdom_names, starting_kingdom, adjacency_matrix, params=[]):
    """
    Input:
        list_of_kingdom_names: An list of kingdom names such that node i of the graph corresponds to name index i in the list
        starting_kingdom: The name of the starting kingdom for the walk
        adjacency_matrix: The adjacency matrix from the input file

    Output:
        Return 2 things. The first is a list of kingdoms representing the walk, and the second is the set of kingdoms that are conquered
    """
    index = 0
    starting_index = -1
    for kingdom in list_of_kingdom_names:
        if starting_kingdom == kingdom:
            starting_index = index
            break
        index += 1
    graph = adjacency_matrix_to_graph(adjacency_matrix)
    christofides_graph, direct_path = christofides(graph, starting_index)
    tour = christofides_tour(christofides_graph, direct_path)
    conquered_set = random_conquer(graph)
    conquered_set, tour = annealing(graph, tour, conquered_set)
    closed_walk = []
    conquered_kingdoms = []
    for i in tour:
        closed_walk.append(list_of_kingdom_names[i])
    for i in conquered_set:
        conquered_kingdoms.append(list_of_kingdom_names[i])
    return closed_walk, conquered_kingdoms


def random_conquer(G):
    kingdoms = [i for i in range(nx.number_of_nodes(G))]
    conquered_set = []
    while not nx.is_dominating_set(G, conquered_set):
        conquering = random.choice(kingdoms)
        kingdoms.remove(conquering)
        conquered_set.append(conquering)
    return conquered_set


def complete_graph(G, weight="weight"):
    M = nx.Graph()

    seen = set()
    Gnodes = set(G)
    for u, (distance, path) in nx.all_pairs_dijkstra(G, weight=weight):
        seen.add(u)
        for v in Gnodes - seen:
            M.add_edge(u, v, weight=distance[v], path=path[v])

    return M


def christofides(G, starting_index):
    MST = nx.minimum_spanning_tree(G)
    G_copy = complete_graph(G)
    final_graph = nx.Graph()
    odd_vertices = []
    for node in MST.nodes():
        if MST.degree(node) % 2 != 0:
            odd_vertices.append(node)

    # CREATE PERFECT MATCHINGS IN MST
    perfect_matchings(G_copy, MST, odd_vertices)

    # CONSTRUCT EULERIAN TOUR
    MST_start = starting_index
    visited = [False] * len(MST.nodes())
    current_node = MST_start
    visited[current_node] = True
    for node in MST.neighbors(current_node):
        if not visited[node] or node == MST_start:
            next_node = node
            break

    direct_path = []
    while next_node != MST_start or not all(visited):
        visited[next_node] = True
        if "path" in G_copy[current_node][next_node]:
            final_graph.add_edge(current_node, next_node, weight=G_copy[current_node][next_node]["weight"], path=G_copy[current_node][next_node]["path"])
            direct_path.append(current_node)
        else:
            final_graph.add_edge(current_node, next_node, weight=G_copy[current_node][next_node]["weight"])
            direct_path.append(current_node)
        current_node = next_node
        for node in MST.neighbors(current_node):
            if not visited[node]:
                next_node = node
                break
        if next_node == current_node:
            for node in G_copy.neighbors(current_node):
                if not visited[node]:
                    next_node = node
                    break
        if next_node == current_node:
            next_node = MST_start
    if not G_copy.has_edge(current_node, next_node):
        path = nx.shortest_path(G_copy, current_node, next_node)
        path_length = nx.shortest_path_length(G_copy, current_node, node, "weight")
        G_copy.add_edge(current_node, next_node, weight=path_length, path=path)
    if "path" in G_copy[current_node][next_node]:
        final_graph.add_edge(current_node, next_node, weight=G_copy[current_node][next_node]["weight"],
                             path=G_copy[current_node][next_node]["path"])
        direct_path.append(current_node)
    else:
        final_graph.add_edge(current_node, next_node, weight=G_copy[current_node][next_node]["weight"])
        direct_path.append(current_node)
    return final_graph, direct_path


def christofides_tour(graph, direct_path):
    tour = []
    # NUM_NODES SET TO NODES - 1 FOR EASIER WHILE LOOP
    num_nodes = nx.number_of_nodes(graph) - 1
    index = 0
    while index < num_nodes:
        true_index = direct_path[index]
        true_index2 = direct_path[index + 1]
        shortest_path = graph[true_index][true_index2]["path"]
        if shortest_path[0] == direct_path[index]:
            tour += shortest_path[:-1]
        else:
            shortest_path = shortest_path[::-1]
            tour += shortest_path[:-1]
        index += 1
    true_index_penult = direct_path[num_nodes]
    start_node = direct_path[0]

    shortest_path = graph[true_index_penult][start_node]["path"]
    if shortest_path[0] == true_index_penult:
        tour += shortest_path[:-1]
    else:
        shortest_path = shortest_path[::-1]
    tour += shortest_path[:-1]
    tour.append(start_node)
    return tour


def perfect_matchings(G, MST, odd_vertices):
    while odd_vertices:
        u = odd_vertices.pop()
        dist = float("inf")
        closest = -1
        for v in odd_vertices:
            if not G.has_edge(u, v):
                path = nx.shortest_path(G, u, v)
                path_length = nx.shortest_path_length(G, u, v, "weight")
                G.add_edge(u, v, weight=path_length, path=path)
            if G[u][v]["weight"] < dist:
                dist = G[u][v]["weight"]
                closest = v
        MST.add_edge(u, closest, weight=dist)
        odd_vertices.remove(closest)


# USE OF SIMULATED ANNEALING TO PRODUCE CONQUERING SET
def annealing(graph, tour, conquered_set):
    kingdoms = [i for i in range(nx.number_of_nodes(graph))]
    T = 100.0
    T_min = 1
    alpha = .95
    old_cost = cost_of_solution(graph, tour, conquered_set)[0]
    min_cost_seen = float("inf")
    min_conquering_set = []
    while T > T_min:
        i = 0
        while i < 100:
            new_set = neighbor(graph, kingdoms, conquered_set)
            temp_tour_new = improve_tour(tour, new_set, graph)
            new_cost = cost_of_solution(graph, temp_tour_new, new_set)[0]
            if new_cost == "infinite":
                continue
            if new_cost < min_cost_seen:
                min_cost_seen = new_cost
                min_conquering_set = new_set
            ap = acceptance_probability(old_cost, new_cost, T)
            if ap > random.random():
                conquered_set = new_set
                old_cost = new_cost

            i += 1

        T *= alpha
    tour1 = improve_tour(tour, conquered_set, graph)
    tour2 = improve_tour(tour, min_conquering_set, graph)

    if cost_of_solution(graph, tour1, conquered_set) < cost_of_solution(graph, tour2, min_conquering_set):
        return conquered_set, tour1
    else:
        return min_conquering_set, tour2


def acceptance_probability(old_cost, new_cost, T):
    if old_cost == "infinite":
        return 1
    if new_cost < old_cost:
        return 1
    return math.exp(-(new_cost - old_cost) / T)


def neighbor(G, kingdoms, conquered_set):
    neighbor_function = random.choice([swap_neighbor, remove_neighbor, add_neighbor])
    new_set = neighbor_function(G, kingdoms, conquered_set)
    if new_set is None:
        return neighbor(G, kingdoms, conquered_set)
    else:
        return new_set


def swap_neighbor(G, kingdoms, conquered_set):
    kingdoms = set(kingdoms)
    attempts = 0
    while attempts < 10:
        conquered_set_copy = list(conquered_set)
        conquered_set_set = set(conquered_set)
        random_node = random.choice(conquered_set)
        conquered_set_copy.remove(random_node)
        difference_set = [x for x in kingdoms if x not in conquered_set_set]
        if not difference_set:
            return
        replacement_node = random.choice(difference_set)
        conquered_set_copy.append(replacement_node)
        if nx.is_dominating_set(G, conquered_set_copy):
            return conquered_set_copy
        attempts += 1
    return conquered_set


def remove_neighbor(G, kingdoms, conquered_set):
    kingdoms = set(kingdoms)
    attempts = 0
    while attempts < 10:
        conquered_set_copy = list(conquered_set)
        to_remove = random.choice(conquered_set_copy)
        conquered_set_copy.remove(to_remove)
        if nx.is_dominating_set(G, conquered_set_copy):
            return conquered_set_copy
        attempts += 1
    return conquered_set


def add_neighbor(G, kingdoms, conquered_set):
    kingdoms_set = set(kingdoms)
    conquered_set_copy = list(conquered_set)
    conquered_set_set = set(conquered_set_copy)
    difference_set = [x for x in kingdoms_set if x not in conquered_set_set]
    if not difference_set:
        return
    added_node = random.choice(difference_set)
    conquered_set_copy.append(added_node)
    return conquered_set_copy


def improve_tour(tour, conquered_list, G):
    new_tour = tour.copy()
    currently_conquered = []
    i = 0
    while i < len(tour):
        step = 0
        sub_list = []
        delete = True
        good = False
        for k in range(i + 1, len(tour)):
            sub_list.append(tour[k])
            if tour[k] == tour[i]:
                good = True
                break
        if not good:
            sub_list = []
        if tour[i] in conquered_list and tour[i] not in currently_conquered:
            currently_conquered.append(tour[i])
        for kingdom in sub_list:
            if kingdom not in currently_conquered:
                delete = False
            for neighbor in G.neighbors(kingdom):
                if neighbor in currently_conquered:
                    delete = True
                    break
            if not delete:
                break
        if delete:
            for j in range(len(sub_list)):
                new_tour[i + j + 1] = -1
                step += 1
        i = 1 + step + i
    new_tour = [i for i in new_tour if i != -1]
    return new_tour






"""
======================================================================
   No need to change any code below this line
======================================================================
"""



def solve_from_file(input_file, output_directory, params=[]):
    print('Processing', input_file)
    
    input_data = utils.read_file(input_file)
    number_of_kingdoms, list_of_kingdom_names, starting_kingdom, adjacency_matrix = data_parser(input_data)
    closed_walk, conquered_kingdoms = solve(list_of_kingdom_names, starting_kingdom, adjacency_matrix, params=params)

    basename, filename = os.path.split(input_file)
    output_filename = utils.input_to_output(filename)
    output_file = f'{output_directory}/{output_filename}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    utils.write_data_to_file(output_file, closed_walk, ' ')
    utils.write_to_file(output_file, '\n', append=True)
    utils.write_data_to_file(output_file, conquered_kingdoms, ' ', append=True)


def solve_all(input_directory, output_directory, params=[]):
    input_files = utils.get_files_with_extension(input_directory, 'in')
    #for i in range(260, 270):
        #input_file = "inputs//" + str(i) + ".in"
        #solve_from_file(input_file, output_directory, params=params)
    for input_file in input_files:
        solve_from_file(input_file, output_directory, params=params)


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Parsing arguments')
    parser.add_argument('--all', action='store_true', help='If specified, the solver is run on all files in the input directory. Else, it is run on just the given input file')
    parser.add_argument('input', type=str, help='The path to the input file or directory')
    parser.add_argument('output_directory', type=str, nargs='?', default='.', help='The path to the directory where the output should be written')
    parser.add_argument('params', nargs=argparse.REMAINDER, help='Extra arguments passed in')
    args = parser.parse_args()
    output_directory = args.output_directory
    if args.all:
        input_directory = args.input
        solve_all(input_directory, output_directory, params=args.params)
    else:
        input_file = args.input
        solve_from_file(input_file, output_directory, params=args.params)
