#
# Licensed under the LICENSE.
# Copyright 2017, Sony Mobile Communications Inc.
#
'''
Generation of bi-directional graph on the warehouse nodes generated in the previous steps.
Bi-directional means that there are no travel conventions for aisles in the warehouse.
'''


import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import LineString, Polygon
import networkx as nx


def generateadjmat(obstacles_and_dummy_obstacles, allnodes, real_object_corner_indicies):

    '''
    # Polygons must follow clockwise coordinate convention
    :param obstacles_and_dummy_obstacles:
    :param allnodes:
    :param real_object_corner_indicies:
    :return:
    '''


    polylist = []  # to store shapely polygon objects

    for obstacle in obstacles_and_dummy_obstacles:  # convert obstacle polygons
        polylist.append(Polygon(obstacle))

    print('Generating adjmat')
    matty = np.ndarray((len(allnodes), len(allnodes)), dtype=bool)

    # Initialize adjacency matrix as fully connected
    for i in range(0, len(allnodes) - 1):
        for j in range(i, len(allnodes)):
            matty[i, j] = 1
            matty[j, i] = 1

    # Deny edges in adjacency matrix that are obstructed
    print('Pruning Obstructed Edges')
    for i in range(0, len(allnodes) - 1):
        print('Edges for Node ', i, 'of ', len(allnodes), ' nodes.')
        for j in range(i + 1, len(allnodes)):
            for poly in polylist:
                shapely_line = LineString([tuple(allnodes[i]), tuple(allnodes[j])])
                if poly.intersection(shapely_line).length != 0:
                    matty[i, j] = 0
                    matty[j, i] = 0
                    break  # break out of polygon loop

    adjmat = matty
    adjmat = connect_polygon_edges(adjmat, real_object_corner_indicies)
    return adjmat, polylist


def connect_polygon_edges(adjmat, real_object_corner_indicies):
    '''

    :param adjmat:
    :param real_object_corner_indicies:
    :return:
    '''
    for object_id_list in real_object_corner_indicies:
        for i in range(0, len(object_id_list) - 1):
            adjmat[object_id_list[i], object_id_list[i + 1]] = 1
            adjmat[object_id_list[i + 1], object_id_list[i]] = 1
        # Connect last to first
        adjmat[object_id_list[0], object_id_list[len(object_id_list) - 1]] = 1
        adjmat[object_id_list[len(object_id_list) - 1], object_id_list[0]] = 1

    return adjmat


def generate_weighted_adjmat(allnodes, adjmat):
    '''
    Get distances for reachable pairs of nodes. simply euclidean given there are no obstructions
    :param allnodes:
    :param adjmat:
    :return:
    '''

    dist_matrix = np.ndarray(shape=(len(allnodes), len(allnodes)), dtype=int)
    print('Generating wadjmat')
    for i in range(0, len(allnodes) - 1):
        for j in range(i + 1, len(allnodes)):
            if adjmat[i, j] == 1:
                # calculate distance
                dist_matrix[i, j] = int(np.sqrt(int(allnodes[i][0] - allnodes[j][0]) ** 2 + int(allnodes[i][1] - allnodes[j][1]) ** 2))  # euclidean dist
                dist_matrix[j, i] = dist_matrix[i, j]
            else:
                dist_matrix[i, j] = 0
                dist_matrix[j, i] = dist_matrix[i, j]

    for i in range(0, len(allnodes)):
        dist_matrix[i, i] = 0

    # run check to make sure no zero rounding has occured:
    for i in range(0, len(allnodes) - 1):
        for j in range(i + 1, len(allnodes)):
            if adjmat[i, j] == 1:
                assert (dist_matrix[i, j] > 0)
    # print'All int valued distances in wadjmat are greater than 0'

    wadjmat = dist_matrix
    print('done Generating wadjmat')

    return wadjmat


def generate_graph_network(adjmat, wadjmat, allnodes):

    '''
    # generate Graph in networkx
    :param adjmat:
    :param wadjmat:
    :param allnodes:
    :return:
    '''

    print('generate_graph_network')
    rows, cols = np.where(adjmat == 1)
    dists = wadjmat[rows, cols]
    edges = zip(rows.tolist(), cols.tolist(), dists.tolist())
    nx_graph = nx.Graph()
    nx_graph.add_weighted_edges_from(edges)

    # generate shortest path routes

    shortest_path = nx.shortest_path(nx_graph, weight='weight')
    # with open('SPNODEPATHS', 'wb') as handle:
    # 	pickle.dump(shortest_path, handle, protocol=pickle.HIGHEST_PROTOCOL)

    sp_dist_matrix = np.ndarray(shape=(len(allnodes), len(allnodes)), dtype=int)

    for i in range(0, len(allnodes)):  # - 1):
        for j in range(i, len(allnodes)):  #i + 1, len(allnodes)):
            if i == j:
                sp_dist_matrix[i, j] = 0
                sp_dist_matrix[j, i] = 0
            else:
                distance_for_this_pair = 0
                sequence_of_transitions = shortest_path[i][j]
                for k in range(0, len(sequence_of_transitions) - 1):
                    distance_for_this_pair = distance_for_this_pair + int(np.sqrt(int(allnodes[sequence_of_transitions[k]][0] - allnodes[sequence_of_transitions[k + 1]][0]) ** 2 + int(allnodes[sequence_of_transitions[k]][1] - allnodes[sequence_of_transitions[k + 1]][1]) ** 2))
                sp_dist_matrix[i, j] = distance_for_this_pair
                sp_dist_matrix[j, i] = distance_for_this_pair

    # with open('SPDISTMAT', 'wb') as handle:
    # 	pickle.dump(sp_dist_matrix, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print('done generate_graph_network')

    return sp_dist_matrix, shortest_path


def visualizeadjmat(adjmat, polylist, allnodes):
    '''
    Visualizes graph result
    :param adjmat:
    :param polylist:
    :param allnodes:
    :return:
    '''

    print('Visualizing...')
    # if visualize:  # set to 1 to plot edges and obstacles
    matplotlib.rcParams['agg.path.chunksize'] = 10000

    # % matplotlib
    # inline
    plt.rcParams['figure.figsize'] = (3.0, 4.0)

    _, ax = plt.subplots()
    plt.title('Connected Edges Around Obstacles, Inspect for Mapping Errors')
    # polygon_shape = patches.Polygon(points, linewidth=1, edgecolor='r', facecolor='none')
    # ax.add_patch(polygon_shape)
    for _, val in enumerate(polylist):
        x, y = val.exterior.coords.xy
        points = np.array([x, y], np.int32).T

        # fig, ax = plt.subplots(1)
        polygon_shape = patches.Polygon(points, linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(polygon_shape)
    plt.axis("auto")

    print('Visualizing...')
    for i in range(0, len(allnodes) - 1):
        for j in range(i + 1, len(allnodes)):
            if adjmat[i, j]:
                ax.plot([allnodes[i][0], allnodes[j][0]],
                        [allnodes[i][1], allnodes[j][1]],
                        color='b',
                        lw=.25)
        if i % 100 == 0:
            print(str(i) + " out of " + str(len(allnodes)) + " nodes done")
    plt.show()


    print('adjmat Generated.')


# EXAMPLE USAGE ===========================
# folder_name = 'warehouse-specific/KC-ca/files-KC-ca/'
#
# with open(folder_name + 'allcoords', 'rb') as handle:
#     allcoords = pickle.load(handle)
#
# with open(folder_name + 'obstacles_and_dummy_obstacles', 'rb') as handle:
#     obstacles_and_dummy_obstacles = pickle.load(handle)
#
# with open(folder_name + 'real_object_corner_indicies', 'rb') as handle:
#     real_object_corner_indicies = pickle.load(handle)
#
# adjmat, polylist = generateadjmat(obstacles_and_dummy_obstacles,
#                                   allcoords,
#                                   real_object_corner_indicies)
#
# with open(folder_name + 'adjmat', 'wb') as handle:  # save them
# 	pickle.dump(adjmat, handle)
#
# with open(folder_name + 'polylist', 'wb') as handle:
# 	pickle.dump(polylist, handle)
#
# with open(folder_name + 'adjmat', 'rb') as handle:
#     adjmat = pickle.load(handle)
#
# with open(folder_name + 'polylist', 'rb') as handle:
#     polylist = pickle.load(handle)

# visualizeadjmat(adjmat, polylist, allcoords)  # 1 min for 500 nodes, 1 hour for ~3500 nodes
#
# wadjmat = generate_weighted_adjmat(allcoords, adjmat)
#
# distmat, SPNODEPATHS = generate_graph_network(adjmat, wadjmat, allcoords)
#
# with open(folder_name + 'distmat', 'wb') as handle:
#     pickle.dump(distmat, handle)
#
# with open(folder_name + 'SPNODEPATHS', 'wb') as handle:
#     pickle.dump(SPNODEPATHS, handle)
