#
# Licensed under the LICENSE.
# Copyright 2017, Sony Mobile Communications Inc.
#
'''
# name: for debugging. pass in "" if not needed
# coords_path_bef_sol:
#     list of ndarrays with [x, y]'s.
#     [array([128600.,  79250.]), array([112600.,  25577.]), ...]
#     It is ndarrays instead of tuples bcs the file with all coordinates
#     is in this format and it was never converted to just list of tuples,
#     but sending in list of tuples would probably work.
# indicies_bef_sol: [0, 2344, 1233, 768, ... , ]
# sol_list: lg should be [0, 1, 2, 3, 4 ... ] and optimized: [0, 2, 3, 1, ...]
# ind_aft_sol  [0, 768, 1233, 2344... , ]
# show_fullpath: It is being used elsewhere but in this setting it should always be True
# startIdx_mat, endIdx_mat, allSPNodeIdxArray, coords_all:
# See how these are loaded/created in ControllerMW -> load_data()
'''

def sol_to_xy(name,
              coords_path_bef_sol,
              indicies_bef_sol,
              sol_list,
              ind_aft_sol,
              startendndarray,
              spnodeslist,
              coords_all):
    """
    sol_to_xy
    :param name:
    :param coords_path_bef_sol:
    :param indicies_bef_sol:
    :param sol_list:
    :param ind_aft_sol:
    :param startendndarray:
    :param spnodeslist:
    :param coords_all:
    :return:
    """

    def get_fullpath_coords():
        """
        get_fullpath_coords
        :return:
        """
        fullpath_coords = []  # for debugging
        fullpath_coords_flat = []

        for i in range(0, len(sol) - 1):  # gen fullpath of the sol nodes

            sol_from = sol[i]
            sol_to = sol[i + 1]

            ind_from = indicies_bef_sol[sol_from]
            ind_to = indicies_bef_sol[sol_to]

            nodes_path_start = (startendndarray[:, :, 0][ind_from][ind_to])
            nodes_path_end = (startendndarray[:, :, 1][ind_from][ind_to])

            indicies_path_coords = spnodeslist[nodes_path_start:nodes_path_end]

            nodes_path_coords = coords_all[indicies_path_coords, :]

            nodes_path_coords = nodes_path_coords.tolist()  # it is saved as npy

            if len(nodes_path_coords) < 2:
                # print("INSIDE POSSIBLY REDUNDANT IF (its for safety")
                node_to_coords = coords_path_bef_sol[sol_to]
                fullpath_coords.append([node_to_coords])  # as list because else adds a list
            else:  # adds whole path as list
                if fullpath_coords_flat:
                    # cannot do this until fullpath has got its first path
                    prev = fullpath_coords_flat[-1]
                    this = nodes_path_coords[0]

                    # check that nodes are linked
                    if (prev[0] != this[0]) or (prev[1] != this[1]):  # x and y
                        # raise ValueError("joErr nodes not linked!")
                        wrong_node0 = ias[i - 1]
                        wrong_node1 = ias[i]
                        # print("temp")
                        print("joWarn: nodes not linked in " + name + "! Wrong nodes: " +
                              str(wrong_node0) + "   " + str(wrong_node1) +
                              "        x0: " + str(prev[0]) +
                              " y0: " + str(prev[1]) +
                              "    x1: " + str(this[0]) +
                              " y1: " + str(this[1]))

                fullpath_coords.append(nodes_path_coords)  #
                fullpath_coords_flat.extend(nodes_path_coords[1:])

        # append info of first node
        fullpath_coords_flat = [fullpath_coords[0][0]] + fullpath_coords_flat

        return fullpath_coords_flat

    sol = sol_list
    ias = ind_aft_sol
    name = name

    path_coords = get_fullpath_coords()

    full_path_coords_pp = []  # post processed
    for row in path_coords:
        dicto = {'x': str(row[0]), 'y': str(row[1])}
        full_path_coords_pp.append(dicto)

    return full_path_coords_pp
