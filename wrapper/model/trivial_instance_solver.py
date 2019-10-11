#
# Licensed under the LICENSE.
# Copyright 2017, Sony Mobile Communications Inc.
#
'''
TrivialInstanceSolver
'''

import itertools
import time
import numpy as np


class TrivialInstanceSolver:
    """
    TrivialInstanceSolver
    """

    SCALE_FACTORS = {
        'mm': 1000.0,
        'cm': 100.0,
        'dm': 10.0
    }

    def __init__(self, solve_dict):
        time0 = time.time()
        metric = solve_dict['metric']
        dist_adj_mat = solve_dict['distmat']
        node_seq_bef_sol = solve_dict['node_seq_bef_sol']
        self.lg_sol_fitness = TrivialInstanceSolver.getdist(dist_adj_mat, node_seq_bef_sol, metric)
        self.solver_sol, self.node_seq_aft_sol = \
            TrivialInstanceSolver.solve_trivial_instance(node_seq_bef_sol,
                                                         dist_adj_mat)
        self.solver_sol_fitness = TrivialInstanceSolver.getdist(dist_adj_mat, self.node_seq_aft_sol, metric)
        self.solve_dict = solve_dict
        self.solve_dict['lg_sol_fitness'] = self.lg_sol_fitness
        self.solve_dict['solver_sol'] = self.solver_sol
        self.solve_dict['solver_sol_fitness'] = self.solver_sol_fitness
        self.solve_dict['node_seq_aft_sol'] = self.node_seq_aft_sol
        self.solve_dict['time_to_optimize'] = time.time()-time0

    @staticmethod
    def solve_trivial_instance(locs, distmat):

        """
        #needed for when Concorde would otherwise fail - 4 items to pick
        #input locs INCLUDES START AND END depots
        :param locs:
        :param distmat:
        :return:
        """

        locs = locs.copy()
        origlocs = np.asarray(locs.copy()).flatten()
        end_depot_node_idx = locs[-1]
        del locs[-1]
        listofpermutations = list(itertools.permutations(locs[1:len(locs)]))
        distlist = []
        for perm in listofpermutations:
            permwithstartandend = [0]+list(perm)+[end_depot_node_idx]
            thisdist = 0
            for i in range(0, len(permwithstartandend)-1):
                thisdist += distmat[permwithstartandend[i]][permwithstartandend[i+1]]
            distlist.append(thisdist)
        distlist = np.asarray(distlist).flatten()
        mindist = np.min(distlist)
        index = np.argwhere(distlist == mindist).flatten()[0]
        nodelabelsol = np.asarray([0] + list(listofpermutations[index]) + [end_depot_node_idx]).flatten()
        unqs = np.unique(nodelabelsol)
        unqsdicts = {}
        for i in unqs.flatten():
            unqsdicts[i] = {}
            unqsdicts[i]['old'] = np.argwhere(origlocs == i).flatten()
            unqsdicts[i]['new'] = np.argwhere(nodelabelsol == i).flatten()

        nodeordersol = list(nodelabelsol).copy()
        for i in list(unqsdicts.keys()):
            for j in range(len(unqsdicts[i]['old'])):
                nodeordersol[unqsdicts[i]['old'][j]] = unqsdicts[i]['new'][j]
        return nodeordersol, nodelabelsol

    @staticmethod
    def getdist(dist_adj_mat, indicies, metric):

        """
        #if metric == 'mm':
        #    divisor_For_Meters = 1000.0
        #elif metric == 'cm':
        #    divisor_For_Meters = 100.0
        #elif metric == 'dm':
        #    divisor_For_Meters = 10.0
        :param dist_adj_mat:
        :param indicies:
        :param metric:
        :return:
        """


        scale = TrivialInstanceSolver.SCALE_FACTORS[metric]

        a_sol_distance = 0
        for i in range(0, len(indicies)-1):
            a_sol_distance = a_sol_distance + dist_adj_mat[indicies[i]][indicies[i+1]]
        #print('Optimal Solution Distance in Meters', a_sol_distance/divisor_For_Meters)

        # TODO Remove this once passed tested
        #return a_sol_distance / divisor_For_Meters
        return a_sol_distance / scale
