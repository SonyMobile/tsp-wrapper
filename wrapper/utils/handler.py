#
# Licensed under the LICENSE.
# Copyright 2017, Sony Mobile Communications Inc.
#
'''
The idea with the Handler class is to take care of everything that is
not directly related to optimization.
'''

import datetime
import importlib
import uuid
import numpy as np
from utils.sol_to_xy import sol_to_xy


class Handler:

    """
    Handler
    """

    def __init__(self, request, wh_dict, request_source):
        self.req_resp_dict = request
        self.solve_dict = self.init_solve_dict(wh_dict, request_source)

        if request_source == 'KC':
            module = importlib.import_module('utils.funcs_KC')

        self.get_node_from_keydict = getattr(module, 'get_node_from_keydict')

        if self.req_resp_dict['requestType'] == "PICK_ROUTE_OPTIMIZATION":
            self.solve_dict['isSingleBatchReq'] = False
            self.solve_dict['isPickRoundOptimRequest'] = True
            self.assignment_id = np.asarray(
                self.req_resp_dict['requestData']['pickLocations']['assignment_identifier']
            ).flatten()

            self.original_sorting_number = np.asarray(
                self.req_resp_dict['requestData']['pickLocations']['original_sorting_number']
            ).flatten()

            self.section = np.asarray(
                self.req_resp_dict['requestData']['pickLocations']['materialHandlingSection']
            ).flatten()

            self.rack = np.asarray(
                self.req_resp_dict['requestData']['pickLocations']['rackIdentifier']
            ).flatten()

            self.tier = np.asarray(
                self.req_resp_dict['requestData']['pickLocations']['rackLocationIdentifier_1']
            ).flatten()

            nodelist = []
            for i in range(len(self.rack)):
                nodelist.append(
                    self.get_node_from_keydict(self.section[i],
                                               self.rack[i],
                                               self.tier[i],
                                               self.solve_dict['keydict'])
                )
            self.nodelist = [self.solve_dict['start_depot_idx']] + \
                nodelist + \
                [self.solve_dict['end_depot_idx']]
            self.solve_dict['node_seq_bef_sol'] = self.nodelist.copy()
            self.solve_dict['is_reroute_req'] = \
                int(self.req_resp_dict['requestData']['isReroute'])
            self.solve_dict['is_clockwise_req'] = \
                int(self.req_resp_dict['requestData']['isClockwise'])

            coords_path_bef_sol = [self.solve_dict['allcoords'][i] \
                                   for i in self.solve_dict['node_seq_bef_sol']]
            self.solve_dict['coords_path_bef_sol'] = coords_path_bef_sol

        elif self.req_resp_dict['requestType'] == "BATCH_OPTIMIZATION":
            #'batchRound' in list(self.req_resp_dict['requestData'].keys()) \
            #    and 'pickRound' not in list(self.req_resp_dict['requestData'].keys()):
            #int(self.req_resp_dict['isBatchOptimizationRequest']) and \
            #    not int(self.req_resp_dict['isPickRoundOptimizationRequest']):
            self.solve_dict['isSingleBatchReq'] = True
            self.solve_dict['isPickRoundOptimRequest'] = False
            self.solve_dict['BatchSize'] = \
                int(self.req_resp_dict['requestData']['maxNumBoxesToBatch'])
            #returns the box queue dict, with all  forced boxes represented as a single box
            self.solve_dict['boxqueuedict'], self.solve_dict['ForceBatchBoxes'] = \
                self.gen_box_dict_for_batching()

        self.box_id_seq = None
        self.assignment_id_seq = None
        self.material_handling_section_seq = None
        self.rack_id_seq = None
        self.rack_location_id1_seq = None

    @staticmethod
    def init_solve_dict(wh_dict, request_source):

        """
        This function initializes solve_dict which is a dict that
        contains everything the optimizer classes need. Has same dict
        structure for both pickroute and batch optimization. It's
        loading the files in wh_dict into solve_dict, as well as
        initing other variables.

        :param wh_dict:
        :param request_source:
        :return:
        """

        solve_dict = {
            ####Warehouse Specific Attributes ###
            'warehouse_funcs': None,
            'request_source': None,
            'metric': None,
            'start_depot_idx': None,
            'end_depot_idx': None,
            'distmat': None,
            'keydict': None,
            'allcoords': None,
            ########
            #### Request Specific Info #####
            'uuid': None,
            'is_reroute_req': None,
            'is_clockwise_req': None,
            'node_seq_bef_sol': None,
            ###############################
            ##### originally Solve Output ###
            'lg_sol_fitness': None,
            'solver_sol': None,
            'solver_sol_fitness': None,
            'node_seq_aft_sol': None,
            'time_to_optimize': None,
            'time_of_req': None,
            ######################################
            ###To Distinguish Batch From PickRun Optimization Posts
            'isSingleBatchReq': None,
            'isPickRoundOptimRequest': None,
            'boxqueuedict': None,
            'forced_boxesToRestore': None,
            'batchSize': None
        }

        #### possible values for measurement_metrics are: 'mm','cm','dm'
        #### i.e. what measurement unit was used during map measurements
        measurement_metrics = {'DADC': 'cm', 'CAG': 'mm', 'KC': 'cm'}
        depot_specs = {'CAG': {'start_depot_idx': 0, 'end_depot_idx': 0},
                       'DADC': {'start_depot_idx': 0, 'end_depot_idx': 1},
                       'KC': {'start_depot_idx': 0, 'end_depot_idx': 0}}
        solve_dict['jobId'] = str(uuid.uuid4())
        solve_dict['uuid'] = str(uuid.uuid4())
        start_idx = depot_specs[request_source]['start_depot_idx']
        end_idx = depot_specs[request_source]['end_depot_idx']
        solve_dict['start_depot_idx'] = start_idx
        solve_dict['end_depot_idx'] = end_idx
        solve_dict['time_of_req'] = str(datetime.datetime.utcnow())
        # IF DEMO TIMESTAMP IS TO BE USED:
        # requestRecieved = \
        #     datetime.datetime(2019, 5, random.randint(27, 31), random.randint(5, 19),\
        #         random.randint(1, 60),random.randint(1, 60), random.randint(1, 999999))
        #     solve_dict['time_of_req'] = str(datetime.datetime(2018, 2, random.randint(1, 19),
        #                                     random.randint(5, 19), random.randint(1, 59),
        #                                     random.randint(1, 59), random.randint(1, 999999)))
        solve_dict['request_source'] = request_source  # TEMP, should not be needed

        for wh_data_key in list(wh_dict.keys()):  # populates solve_dict with files from wh_dict
            wh_data_key_short = wh_data_key.rsplit('/', 1)[-1]
            # ^-- TEMP, having full path in solve_dict causes problems later on in legacy functions.
            solve_dict[wh_data_key_short] = wh_dict[wh_data_key]
        solve_dict['metric'] = measurement_metrics[request_source]

        return solve_dict

    def gen_box_dict_for_batching(self):

        """
        gen_box_dict_for_batching
        :return:
        """

        enf_w_con = self.req_resp_dict['requestData']['enf_w_con']
        enf_v_con = self.req_resp_dict['requestData']['enf_v_con']

        boxqueuedict = {}  # datastructure used for batching
        if enf_w_con:
            boxqueuedict['enf_w_con'] = True
            boxqueuedict['maxBatchWeight'] = \
                float(self.req_resp_dict['requestData']['maxBatchWeight'])
            box_w_array = []
        else:
            boxqueuedict['enf_w_con'] = False

        if enf_v_con:
            boxqueuedict['enf_v_con'] = True
            boxqueuedict['maxBatchVolume'] = \
                float(self.req_resp_dict['requestData']['maxBatchVolume'])
            box_v_array = []
        else:
            boxqueuedict['enf_v_con'] = False


        arr_of_b = []  # to be converted to np array (of np arrays containg graph node indices)
        #b_d_d_t_a = []
        box_id_s_array = []

        forced_boxes = self.req_resp_dict['requestData']['forceBatchBoxes']
        for b_dict in self.req_resp_dict['requestData']['availableBoxes']:
            if enf_w_con:
                box_w_array.append(float(b_dict['boxWeight']))
            if enf_v_con:
                box_v_array.append(float(b_dict['boxVolume']))
            this_box_i_n_a = []

            box_id_s_array.append(b_dict['boxIdentifier'])
            for item_idx in range(len(b_dict['boxItemInfo']['materialHandlingSection'])):
                this_box_i_n_a.append(
                    self.get_node_from_keydict(
                        b_dict['boxItemInfo']['materialHandlingSection'][item_idx],
                        b_dict['boxItemInfo']['rackIdentifier'][item_idx],
                        b_dict['boxItemInfo']['rackLocationIdentifier_1'][item_idx],
                        self.solve_dict['keydict']))
            arr_of_b.append(np.asarray(this_box_i_n_a))
        arr_of_b = np.asarray(arr_of_b)

        boxqueuedict['boxnodelists'] = arr_of_b

        ###OBS dueDateTime is excluded from V2 json schema as it is not used
        ## uncomment (2 of 16) ONLY IF dueDateTime is reintroduced, currently not needed)
        #boxqueuedict['times'] = np.asarray(b_d_d_t_a).flatten()

        boxqueuedict['boxIDs'] = np.asarray(box_id_s_array).flatten()

        if enf_w_con:
            boxqueuedict['boxWeights'] = np.asarray(box_w_array).flatten()

        if enf_v_con:
            boxqueuedict['boxVolumes'] = np.asarray(box_v_array).flatten()

        if forced_boxes:
            boxqueuedict, forced_boxestoreturn = self.condence_forced_boxes(forced_boxes,
                                                                            boxqueuedict)
            return boxqueuedict, forced_boxestoreturn

        return boxqueuedict, {} #do not remove this second return val, which is an empty dict.

    @staticmethod
    def condence_forced_boxes(forcebatchboxes, boxqueuedict):

        """
        condence_forced_boxes
        :param forcebatchboxes:
        :param boxqueuedict:
        :return:
        """
        # treats all forced boxes to batch as one box
        # print(boxqueuedict)
        forced_box_i = 'forced_boxes'
        forced_box_n = []
        forced_boxes_to_restore = {}
        ###OBS dueDateTime is excluded from V2 json schema as it is not used
        ##uncomment (16 of 16) ONLY IF dueDateTime is reintroduced, currently not needed)
        #forcedboxTime = datetime.datetime.now()
        if boxqueuedict['enf_w_con']:
            forced_boxes_to_restore['weights'] = []
        if boxqueuedict['enf_v_con']:
            forced_boxes_to_restore['volumes'] = []
        ###OBS dueDateTime is excluded from V2 json schema as it is not used
        ##uncomment (15 of 16) ONLY IF dueDateTime is reintroduced, currently not needed)
        #forced_boxes_to_restore['times'] = []
        forced_boxes_to_restore['boxnodelists'] = []
        forced_boxes_to_restore['boxIDs'] = np.asarray(forcebatchboxes).flatten()
        a_t_del = []
        for box in forcebatchboxes:
            arg = np.argwhere(boxqueuedict['boxIDs'] == box)[0][0]
            a_t_del.append(arg)

            ###OBS dueDateTime is excluded from V2 json schema as it is not used
            ##uncomment (3 of 16) ONLY IF dueDateTime is reintroduced, currently not needed)
            #forced_boxes_to_restore['times'] += [boxqueuedict['times'][arg]]

            forced_boxes_to_restore['boxnodelists'] += [boxqueuedict['boxnodelists'][arg]]
            forced_box_n += [node for node in list(boxqueuedict['boxnodelists'][arg])]
            if boxqueuedict['enf_w_con']:
                forced_boxes_to_restore['weights'] += [boxqueuedict['boxWeights'][arg]]
            if boxqueuedict['enf_v_con']:
                forced_boxes_to_restore['volumes'] += [boxqueuedict['boxVolumes'][arg]]

        #remove forced_boxes as individual boxes from box dict queue
        a_t_del = np.asarray(a_t_del).flatten()
        boxqueuedict['boxIDs'] = np.delete(boxqueuedict['boxIDs'], a_t_del)

        ###OBS dueDateTime is excluded from V2 json schema as it is not used
        ##uncomment (4 of 16) ONLY IF dueDateTime is reintroduced, currently not needed)
        #boxqueuedict['times'] = np.delete(boxqueuedict['times'], a_t_del)

        boxqueuedict['boxnodelists'] = np.delete(boxqueuedict['boxnodelists'], a_t_del)
        # add condensed box to boxqueuedict
        if boxqueuedict['enf_w_con']:
            #remove first
            boxqueuedict['boxWeights'] = np.delete(boxqueuedict['boxWeights'], a_t_del)
            #add as condensed box weight info
            totalforced_boxes_weight = np.sum(np.asarray(
                forced_boxes_to_restore['weights']
            ).flatten())
            boxqueuedict['boxWeights'] = np.asarray([totalforced_boxes_weight] +
                                                    list(boxqueuedict['boxWeights'])).flatten()
        if boxqueuedict['enf_v_con']:
            boxqueuedict['boxVolumes'] = np.delete(boxqueuedict['boxVolumes'], a_t_del)
            totalforced_boxes_volume = np.sum(np.asarray(
                forced_boxes_to_restore['volumes']
            ).flatten())
            boxqueuedict['boxVolumes'] = np.asarray([totalforced_boxes_volume] +
                                                    list(boxqueuedict['boxVolumes'])).flatten()
        bnl = np.asarray([np.asarray(forced_box_n)]+list(boxqueuedict['boxnodelists'])).flatten()
        boxqueuedict['boxnodelists'] = bnl
        bids = np.asarray([forced_box_i]+list(boxqueuedict['boxIDs'])).flatten()
        boxqueuedict['boxIDs'] = bids

        ###OBS dueDateTime is excluded from V2 json schema as it is not used
        ##uncomment (5,6,7 of 16) ONLY IF dueDateTime is reintroduced, currently not needed)
        #tmes = np.asarray([forcedboxTime]+list(boxqueuedict['times'])).flatten()
        #boxqueuedict['times'] = tmes
        #forced_boxes_to_restore['times'] = np.asarray(forced_boxes_to_restore['times']).flatten()

        forced_boxes_to_restore['boxnodelists'] = \
            np.asarray(forced_boxes_to_restore['boxnodelists'])  #.flatten() DO NOT FLATTEN!!!

        if boxqueuedict['enf_w_con']:
            forced_boxes_to_restore['weights'] = \
                np.asarray(forced_boxes_to_restore['weights']).flatten()
        if boxqueuedict['enf_v_con']:
            forced_boxes_to_restore['volumes'] = \
                np.asarray(forced_boxes_to_restore['volumes']).flatten()

        return boxqueuedict, forced_boxes_to_restore

    @staticmethod
    def get_index_flattened_arr(row, column, length):

        """
        get_index_flattened_arr
        :param row:
        :param column:
        :param length:
        :return:
        """

        idxcount = 0
        for index in range(0, length):
            idxcount += (length - index)
            if row == index:
                idx = idxcount - (length - column)
                break
        return idx

    @staticmethod
    def get_spnodepath(from_node, to_node, spnodelist, startendarray, length):

        """
        get_spnodepath
        :param from_node:
        :param to_node:
        :param spnodelist:
        :param startendarray:
        :param length:
        :return:
        """
        ifrom = from_node
        jto = to_node
        if ifrom > jto:
            idx = Handler.get_index_flattened_arr(jto, ifrom, length)
            path = spnodelist[startendarray[idx, 0]:startendarray[idx, 1]].astype(np.int64).flatten()
            # reverse output
            return list(np.flip(path).flatten())

        idx = Handler.get_index_flattened_arr(ifrom, jto, length)
        path = spnodelist[startendarray[idx, 0]:startendarray[idx, 1]].astype(np.int64).flatten()
        return list(path)

    @staticmethod
    def get_full_path(node_seq_aft_sol, spnodelist, startendarray, end_depot_node_idx, length):

        """
        get_full_path
        :param node_seq_aft_sol:
        :param spnodelist:
        :param startendarray:
        :param end_depot_node_idx:
        :param length:
        :return:
        """

        pathappend = []
        for i in range(0, len(node_seq_aft_sol) - 1):
            from_node = node_seq_aft_sol[i]
            to_node = node_seq_aft_sol[i + 1]
            path_seg_to_append = Handler.get_spnodepath(from_node,
                                                        to_node,
                                                        spnodelist,
                                                        startendarray,
                                                        length)
            if len(path_seg_to_append) > 1:
                pathappend = pathappend + path_seg_to_append[0:len(path_seg_to_append) - 1]
            else:
                pathappend = pathappend + path_seg_to_append[:]
        pathappend = pathappend + [end_depot_node_idx]  ## End depot Specific to warehouse
        return pathappend

    def gen_response(self, solve_dict):

        """
        # For Pick-Runs:
        # Expected solver_output_index_ordering is the index ordering
        # required to convert request pick sequence to optimal
        # sequence.  This function assumes start and end depot are
        # represented in the output index sequence solution.
        :param solve_dict:
        :param auth:
        :return:
        """


        if self.solve_dict['isPickRoundOptimRequest']:

            solver_output_index_ordering = solve_dict['solver_sol'].copy()
            args_to_sort = solver_output_index_ordering[1:-1]  # strip sol of depot and
            args_to_sort = np.asarray([x - 1 for x in args_to_sort]).flatten()  # decrement by 1
            self.section = list(self.section[args_to_sort].flatten())
            self.rack = list(self.rack[args_to_sort].flatten())
            self.tier = list(self.tier[args_to_sort].flatten())
            self.req_resp_dict['responseData'] = {}

            self.req_resp_dict['responseData'] = {'returnPickerHints': None,
                                                  'userIdentifier': None,
                                                  'pickRoundIdentifier': None,
                                                  'isClockwise': None,
                                                  'isReroute': None,
                                                  'mobileUnitIdentifier': None,
                                                  'optimalRouteDistance': None,
                                                  'originalRouteDistance': None,
                                                  'distanceSavedMeters': None,
                                                  'pickLocations': {'assignment_identifier': None,
                                                                    'original_sorting_number': None,
                                                                    'optimizedSortingNumber': None,
                                                                    'materialHandlingSection': None,
                                                                    'rackIdentifier': None,
                                                                    'rackLocationIdentifier_1': None,
                                                                    'rackLocationIdentifier_2': []}}

            self.req_resp_dict['responseData']['returnPickerHints'] = self.req_resp_dict['requestData']['returnPickerHints']
            self.req_resp_dict['responseData']['userIdentifier'] = self.req_resp_dict['requestData']['userIdentifier']
            self.req_resp_dict['responseData']['pickRoundIdentifier'] = self.req_resp_dict['requestData']['pickRoundIdentifier']
            self.req_resp_dict['responseData']['isClockwise'] = self.req_resp_dict['requestData']['isClockwise']
            self.req_resp_dict['responseData']['isReroute'] = self.req_resp_dict['requestData']['isReroute']
            self.req_resp_dict['responseData']['mobileUnitIdentifier'] = self.req_resp_dict['requestData']['mobileUnitIdentifier']
            self.req_resp_dict['responseData']['optimalRouteDistance'] = str(solve_dict['solver_sol_fitness'])
            self.req_resp_dict['responseData']['originalRouteDistance'] = str(solve_dict['lg_sol_fitness'])
            self.req_resp_dict['responseData']['distanceSavedMeters'] = str(solve_dict['lg_sol_fitness']-solve_dict['solver_sol_fitness'])
            self.req_resp_dict['responseData']['pickLocations']['assignment_identifier'] = list(self.assignment_id[args_to_sort].flatten())
            self.req_resp_dict['responseData']['pickLocations']['original_sorting_number'] = list(self.original_sorting_number[args_to_sort].flatten())
            self.req_resp_dict['responseData']['pickLocations']['optimizedSortingNumber'] = list(self.original_sorting_number.flatten())
            self.req_resp_dict['responseData']['pickLocations']['materialHandlingSection'] = list(self.section)
            self.req_resp_dict['responseData']['pickLocations']['rackIdentifier'] = list(self.rack)
            self.req_resp_dict['responseData']['pickLocations']['rackLocationIdentifier_1'] = list(self.tier)
            self.req_resp_dict['jobId'] = solve_dict['jobId']
            ##see below for time tracking entries to json
            # self.req_resp_dict['responseData']['requestReceivedAtDateTime'] = \
            #     self.solve_dict['time_of_req'].replace(tzinfo=datetime.timezone.utc).isoformat()
            self.req_resp_dict['responseData']['requestReceivedAtDateTime'] = self.solve_dict['time_of_req']  #joChange

            #NOTE Response time entered at end after webAppData....
            #WEBAPPINFO

            #66 HERE
            bef_full_path_coords = sol_to_xy("",
                                             solve_dict['coords_path_bef_sol'],
                                             solve_dict['node_seq_bef_sol'],
                                             list(range(0, len(solve_dict['solver_sol']))),
                                             solve_dict['node_seq_aft_sol'],
                                             solve_dict['startendndarray'],
                                             solve_dict['spnodeslist'],
                                             np.asarray(solve_dict['allcoords'], dtype=np.uint32))

            aft_full_path_coords = sol_to_xy("",
                                             solve_dict['coords_path_bef_sol'],
                                             solve_dict['node_seq_bef_sol'],
                                             solve_dict['solver_sol'],
                                             solve_dict['node_seq_aft_sol'],
                                             solve_dict['startendndarray'],
                                             solve_dict['spnodeslist'],
                                             np.asarray(solve_dict['allcoords'], dtype=np.uint32))

            node_seq_coords_bef = []
            node_seq_coords_aft = []
            seqbef = solve_dict['node_seq_bef_sol']
            seqaft = solve_dict['node_seq_aft_sol']

            for _, val in enumerate(seqbef):
                node_seq_coords_bef.append(
                    [str(solve_dict['allcoords'][val][0]),
                     str(solve_dict['allcoords'][val][1])])

            for _, val in enumerate(seqaft):
                node_seq_coords_aft.append(
                    [str(solve_dict['allcoords'][val][0]),
                     str(solve_dict['allcoords'][val][1])])


            #TODO: PickRoute webAppData for dashboard
            for_web_app = {}
            for_web_app['bef_optimization'] = {}
            for_web_app['aft_optimization'] = {}

            for_web_app['aft_optimization']['distanceSavedMeters'] = self.req_resp_dict['responseData']['distanceSavedMeters']
            for_web_app['aft_optimization']['materialHandlingSection'] = self.req_resp_dict['responseData']['pickLocations']['materialHandlingSection']
            for_web_app['aft_optimization']['rackIdentifier'] = self.req_resp_dict['responseData']['pickLocations']['rackIdentifier']
            for_web_app['aft_optimization']['rackLocationIdentifier_1'] = self.req_resp_dict['responseData']['pickLocations']['rackLocationIdentifier_1']
            for_web_app['aft_optimization']['rackLocationIdentifier_2'] = self.req_resp_dict['responseData']['pickLocations']['rackLocationIdentifier_2']
            for_web_app['bef_optimization']['materialHandlingSection'] = self.req_resp_dict['requestData']['pickLocations']['materialHandlingSection']
            for_web_app['bef_optimization']['rackIdentifier'] = self.req_resp_dict['requestData']['pickLocations']['rackIdentifier']
            for_web_app['bef_optimization']['rackLocationIdentifier_1'] = self.req_resp_dict['requestData']['pickLocations']['rackLocationIdentifier_1']
            for_web_app['bef_optimization']['rackLocationIdentifier_2'] = self.req_resp_dict['requestData']['pickLocations']['rackLocationIdentifier_2']
            for_web_app['numberOfLocations'] = str(len(seqbef)-2)
            # for_web_app['requestReceivedAtDateTime'] = self.solve_dict['time_of_req'].replace(tzinfo=datetime.timezone.utc).isoformat()
            for_web_app['requestReceivedAtDateTime'] = self.solve_dict['time_of_req']  #joChange

            #for_web_app['responseGeneratedAtDateTime'] enter at end
            #for_web_app['responseTimeTakenSeconds'] = None

            for_web_app['coordinateUnitOfMeasurement'] = solve_dict['metric']
            for_web_app['pickRunID'] = self.req_resp_dict['responseData']['pickRoundIdentifier']
            for_web_app['bef_optimization']['timeStamps'] = []

            pncoords = []

            for r in range(0, len(node_seq_coords_bef)):
                dicto = {'x': str(node_seq_coords_bef[r][0]), 'y': str(node_seq_coords_bef[r][1])}
                pncoords.append(dicto)

            for_web_app['bef_optimization']['pickNodeCoords'] = pncoords

            for_web_app['bef_optimization']['fullPathCoords'] = bef_full_path_coords
            for_web_app['bef_optimization']['user'] = self.req_resp_dict['responseData']['userIdentifier']
            for_web_app['bef_optimization']['totalDistanceMeters'] = self.req_resp_dict['responseData'][
                'originalRouteDistance']
            for_web_app['bef_optimization']['avgVelocityMetersPerSecond'] = None
            for_web_app['bef_optimization']['metersPerPick'] = str(solve_dict['lg_sol_fitness'] / (float(len(solve_dict['node_seq_bef_sol']) - 2.0)))
            for_web_app['aft_optimization']['timeStamps'] = []

            pncoords = []
            for r in range(0, len(node_seq_coords_aft)):
                dicto = {'x': str(node_seq_coords_aft[r][0]), 'y': str(node_seq_coords_aft[r][1])}
                pncoords.append(dicto)

            for_web_app['aft_optimization']['pickNodeCoords'] = pncoords
            for_web_app['aft_optimization']['fullPathCoords'] = aft_full_path_coords
            for_web_app['aft_optimization']['user'] = self.req_resp_dict['responseData']['userIdentifier']
            for_web_app['aft_optimization']['totalDistanceMeters'] = self.req_resp_dict['responseData']['optimalRouteDistance']
            for_web_app['aft_optimization']['avgVelocityMetersPerSecond'] = None
            for_web_app['aft_optimization']['metersPerPick'] = str(solve_dict['solver_sol_fitness'] / (float(len(solve_dict['node_seq_aft_sol']) - 2.0)))

            # Populate time taken and resp gen time entries
            respGenTime = datetime.datetime.utcnow()
            respGenTimeTaken = np.datetime64(str(respGenTime)) - np.datetime64(str(self.solve_dict['time_of_req']))
            respGenTimeTaken = respGenTimeTaken.item().total_seconds()
            for_web_app['responseGeneratedAtDateTime'] = str(respGenTime)
            # self.req_resp_dict['responseData']['requestReceivedAtDateTime'] = self.solve_dict['time_of_req'].replace(tzinfo=datetime.timezone.utc).isoformat()
            self.req_resp_dict['responseData']['requestReceivedAtDateTime'] = str(respGenTime)
            self.req_resp_dict['responseData']['responseGeneratedAtDateTime'] = str(respGenTime)
            self.req_resp_dict['responseData']['responseTimeTakenSeconds'] = str(respGenTimeTaken)
            for_web_app['responseGeneratedAtDateTime'] = str(respGenTime)
            for_web_app['responseTimeTaken'] = str(respGenTimeTaken)
            self.req_resp_dict['webAppData'] = for_web_app

            # Reroute check
            if int(self.req_resp_dict['requestData']['isReroute']):
                self.req_resp_dict['responseData']['rerouteStartLocation']['materialHandlingSection'] = list(self.req_resp_dict['requestData']['rerouteStartLocation']['materialHandlingSection'])
                self.req_resp_dict['responseData']['rerouteStartLocation']['rackIdentifier'] = list(self.req_resp_dict['requestData']['rerouteStartLocation']['rackIdentifier'])
                self.req_resp_dict['responseData']['rerouteStartLocation']['rackLocationIdentifier_1'] = list(self.req_resp_dict['requestData']['rerouteStartLocation']['rackLocationIdentifier_1'])

            #Hints Requirement Check
            if int(self.req_resp_dict['requestData']['returnPickerHints']):
                hints = solve_dict['warehouse_funcs']['GetPickerHints_'+ solve_dict['request_source']](solve_dict)
                # need to assure the above line works. TEST!!! why it wouldnt work: passing in function from main where in this class that function has not been imported....
                self.req_resp_dict['responseData']['pickLocations']['PickerHints'] = hints.instructions
                #print(self.solve_dict['node_seq_aft_sol'], len(hints.instructions), len(self.solve_dict['node_seq_aft_sol']))

        elif self.solve_dict['isSingleBatchReq']:
            self.req_resp_dict['webAppData'] = {}
            self.map_box_items_to_sol_indicies()


            #need to add start and end depot to solution before sending to pickerhints.
            self.solve_dict['node_seq_aft_sol'] = [int(self.solve_dict['start_depot_idx'])]+list(np.asarray(self.solve_dict['SingleBatchOutput']['node_seq_aft_sol']).astype(int).flatten())
            self.solve_dict['node_seq_aft_sol'] = self.solve_dict['node_seq_aft_sol'] + [int(self.solve_dict['end_depot_idx'])]

            self.req_resp_dict["responseData"] = {}
            self.req_resp_dict['responseData']['batchAsPickRoute'] = {}

            # if int(self.req_resp_dict['requestData']['returnPickerHints']):  # DOESN'T WORK IN NEW VERSION (YET)
            # 	hints = solve_dict['warehouse_funcs']['GetPickerHints_' + solve_dict['request_source']](self.solve_dict)
            # 	self.req_resp_dict['responseData']['batchAsPickRoute']['pickerHints'] = list(hints.instructions)

            self.req_resp_dict["jobId"] = self.solve_dict['jobId']
            self.req_resp_dict['responseData']['boxesInBatch'] = self.solve_dict['SingleBatchOutput']['BoxesInBatch']
            self.req_resp_dict['responseData']['batchAsPickRoute']['boxIdentifier'] = list(self.box_id_seq)
            self.req_resp_dict['responseData']['batchAsPickRoute']['assignment_identifier'] = list(self.assignment_id_seq)
            self.req_resp_dict['responseData']['batchAsPickRoute']['materialHandlingSection'] = list(self.material_handling_section_seq)
            self.req_resp_dict['responseData']['batchAsPickRoute']['rackIdentifier'] = list(self.rack_id_seq)
            self.req_resp_dict['responseData']['batchAsPickRoute']['rackLocationIdentifier_1'] = list(self.rack_location_id1_seq)
            self.req_resp_dict['responseData']['batchAsPickRoute']['rackLocationIdentifier_2'] = [] #doesnt exist for DADC



            self.req_resp_dict['responseData']['excludedFromBatch'] = {'allExcludedBoxes': self.solve_dict['SingleBatchOutput']['allExcludedBoxes']}
            self.req_resp_dict['responseData']['excludedFromBatch']['evaluatedBoxesExcludedFromBatch'] = self.solve_dict['SingleBatchOutput']['evaluatedButExcludedFromBatch']
            self.req_resp_dict['responseData']['excludedFromBatch']['boxesNotEvaluated'] = self.solve_dict['SingleBatchOutput']['boxesPostedButNotEvaluated']

            #DateTimeData
            respGenTime = datetime.datetime.utcnow()
            recievedReqAtTime = str(self.solve_dict['time_of_req'])
            respGenTimeTaken = np.datetime64(str(respGenTime)) - np.datetime64(recievedReqAtTime)
            respGenTimeTaken = respGenTimeTaken.item().total_seconds()
            self.req_resp_dict['responseData']['requestReceivedAtDateTime'] = self.solve_dict['time_of_req']  # .replace(tzinfo=datetime.timezone.utc).isoformat()
            self.req_resp_dict['responseData']['responseGeneratedAtDateTime'] = str(respGenTime)  # .replace(tzinfo=datetime.timezone.utc).isoformat()
            self.req_resp_dict['responseData']['responseTimeTakenSeconds'] = str(respGenTimeTaken)

            for_web_app = {}
            for_web_app['bef_optimization'] = {}
            for_web_app['aft_optimization'] = {}

            # @Enys, for distanceSavedMeters we could do an estimate here where estDistSaved = historicBatchMpp*numPicks - thisbatchPickRouteDist
            #Problem with such a hardcoded estimate is that sometimes we would see a negative distance saved - overall it should be positive...
            # So I have left is as None
            for_web_app['aft_optimization']['distanceSavedMeters'] = None

            for_web_app['aft_optimization']['materialHandlingSection'] = self.req_resp_dict['responseData']['batchAsPickRoute']['materialHandlingSection']
            for_web_app['aft_optimization']['rackIdentifier'] = self.req_resp_dict['responseData']['batchAsPickRoute']['rackIdentifier']
            for_web_app['aft_optimization']['rackLocationIdentifier_1'] = self.req_resp_dict['responseData']['batchAsPickRoute']['rackLocationIdentifier_1']
            for_web_app['aft_optimization']['rackLocationIdentifier_2'] = self.req_resp_dict['responseData']['batchAsPickRoute']['rackLocationIdentifier_2']

            #there was no predefined route, hence all below is empty...
            for_web_app['bef_optimization']['materialHandlingSection'] = []
            for_web_app['bef_optimization']['rackIdentifier'] = []
            for_web_app['bef_optimization']['rackLocationIdentifier_1'] = []
            for_web_app['bef_optimization']['rackLocationIdentifier_2'] = []
            for_web_app['numberOfLocations'] = str(len(self.req_resp_dict['responseData']['batchAsPickRoute']['rackIdentifier']))
            for_web_app['requestReceivedAtDateTime'] = self.solve_dict['time_of_req']  # joChange  .replace(tzinfo=datetime.timezone.utc).isoformat()
            # for_web_app['responseGeneratedAtDateTime'] enter at end
            # for_web_app['responseTimeTakenSeconds'] = None
            for_web_app['coordinateUnitOfMeasurement'] = solve_dict['metric']

            #Again, empty fields in the batch optim case
            for_web_app['pickRunID'] = None
            for_web_app['bef_optimization']['timeStamps'] = []
            for_web_app['bef_optimization']['pickNodeCoords'] = []
            for_web_app['bef_optimization']['fullPathCoords'] = []

            #Note: UID does not exist for batch optimization... which is to be automated. #self.req_resp_dict['responseData']['userIdentifier']
            for_web_app['bef_optimization']['user'] = None
            for_web_app['bef_optimization']['totalDistanceMeters'] = None # This could be an estimate of what we would have expected from the wms batching: i.e. AvgHistBatching*numpicks
            for_web_app['bef_optimization']['avgVelocityMetersPerSecond'] = None
            for_web_app['bef_optimization']['metersPerPick'] = None

            for_web_app['aft_optimization']['timeStamps'] = []

            node_seq_coords_aft = []
            seqaft = self.solve_dict['node_seq_aft_sol']

            for _, val in seqaft:
                node_seq_coords_aft.append([str(solve_dict['allcoords'][val][0]),
                                            str(solve_dict['allcoords'][val][1])])

            pncoords = []
            for r in range(0, len(node_seq_coords_aft)):
                dicto = {'x': str(node_seq_coords_aft[r][0]), 'y': str(node_seq_coords_aft[r][1])}
                pncoords.append(dicto)

            for_web_app['aft_optimization']['pickNodeCoords'] = pncoords

            solve_dict['solver_sol'] = list(range(0, len(solve_dict['node_seq_aft_sol'])))
            coords_path_aft_sol = \
                [self.solve_dict['allcoords'][i] for i in self.solve_dict['node_seq_aft_sol']]
            # coords_path_bef_sol are the x, y pick location coordinates in the order they are
            # before optimization.
            # node_seq_bef_sol are the corresponding digital twin 'nodes' (with indexes from 0
            # to around 2500).
            solve_dict['coords_path_aft_sol'] = coords_path_aft_sol
            solve_dict['node_seq_bef_sol'] = solve_dict['node_seq_aft_sol']
            aft_full_path_coords = sol_to_xy("",
                                             solve_dict['coords_path_aft_sol'],
                                             solve_dict['node_seq_bef_sol'],
                                             solve_dict['solver_sol'],
                                             solve_dict['node_seq_aft_sol'],
                                             solve_dict['startendndarray'],
                                             solve_dict['spnodeslist'],
                                             np.asarray(solve_dict['allcoords'], dtype=np.int16))

            for_web_app['aft_optimization']['fullPathCoords'] = aft_full_path_coords
            for_web_app['aft_optimization']['user'] = None #self.req_resp_dict['responseData']['userIdentifier']
            for_web_app['aft_optimization']['totalDistanceMeters'] = self.solve_dict['SingleBatchOutput']['TotalDistanceofOptimalRouteForOptimizedBatch'] #str(solve_dict['solver_sol_fitness'])#self.req_resp_dict['responseData']['optimalRouteDistance']
            for_web_app['aft_optimization']['avgVelocityMetersPerSecond'] = None
            for_web_app['aft_optimization']['metersPerPick'] = self.solve_dict['SingleBatchOutput']['metersPerPick']

            self.req_resp_dict['jobId'] = solve_dict['jobId']

            # Populate time taken and resp gen time entries
            respGenTime = datetime.datetime.utcnow()
            respGenTimeTaken = np.datetime64(str(respGenTime)) - np.datetime64(str(self.solve_dict['time_of_req']))
            respGenTimeTaken = respGenTimeTaken.item().total_seconds()
            for_web_app['responseGeneratedAtDateTime'] = str(respGenTime)
            for_web_app['responseGeneratedAtDateTime'] = str(respGenTime)
            for_web_app['responseTimeTaken'] = str(respGenTimeTaken)
            #notOptimMetersPerPick = None #i.e. no baseline
            optimMetersPerPick = float(for_web_app['aft_optimization']['metersPerPick'])
            # str(self.calculate_efficiency_gain_DADC(notOptimMetersPerPick, optimMetersPerPick))
            for_web_app['estPercentageEfficiencyGain'] = None
            # print('est % eff gain',for_web_app['estPercentageEfficiencyGain'])
            self.req_resp_dict['webAppData'] = for_web_app

        # # JOHAN'S QUICK FIX PART
        # # print("/gen_response BEF V57")
        # if self.solve_dict['isPickRoundOptimRequest']:
        #     forWMS, forBQ_hist, forBQ_optim = j_mod.v57_PRO(self.req_resp_dict, auth, demo=False)
        # elif self.solve_dict['isSingleBatchReq']:
        #     forWMS, forBQ_hist, forBQ_optim = j_mod.v57_BO(self.req_resp_dict, auth, demo=False)
        # # print("/gen_response AFT V57")
        return [], [], []

    def map_box_items_to_sol_indicies(self):

        """
        #inputs = 'boxqueuedict', 'ForceBatchBoxes', solution, original request

        :return:
        """
        solution = \
            np.asarray(self.solve_dict['SingleBatchOutput']['node_seq_aft_sol']).astype(int).flatten()

        if self.solve_dict['ForceBatchBoxes'] != {}:
            #extract forced boxes from boxqueue
            boxqueue, self.solve_dict['SingleBatchOutput']['BoxesInBatch'] = \
                self.forced_box_extractor()
        else:
            boxqueue = self.solve_dict['boxqueuedict']

        boxes_in_batch = self.solve_dict['SingleBatchOutput']['BoxesInBatch']

        orig_node_list_order_boxes_in_batch = []
        for box in boxes_in_batch:
            #info gathered by request item-ordered boxes in computed batch
            index = np.argwhere(boxqueue['boxIDs'] == box)[0]
            for nodes in boxqueue['boxnodelists'][index]:
                for node in nodes:
                    orig_node_list_order_boxes_in_batch.append(node)
        orig_node_list_order_boxes_in_batch = \
            np.asarray(orig_node_list_order_boxes_in_batch).flatten()

        orig_box_item_info_ordered_by_box = [[], [], [], [], []]
        # [boxID, assignment_ids, section, rack, tier]
        # applies to dadc, may need extra rack identifier for new WH.

        for box in boxes_in_batch:
            for i in range(len(self.req_resp_dict['requestData']['availableBoxes'][:])):
                if self.req_resp_dict['requestData']['availableBoxes'][i]['boxIdentifier'] == box:
                    BoxInfo = self.req_resp_dict['requestData']['availableBoxes'][i]['boxItemInfo']
                    for j in range(len(BoxInfo['rackIdentifier'])):
                        orig_box_item_info_ordered_by_box[0] += [box]
                        orig_box_item_info_ordered_by_box[1] += [BoxInfo['assignment_identifier'][j]]
                        orig_box_item_info_ordered_by_box[2] += [BoxInfo['materialHandlingSection'][j]]
                        orig_box_item_info_ordered_by_box[3] += [BoxInfo['rackIdentifier'][j]]
                        orig_box_item_info_ordered_by_box[4] += [BoxInfo['rackLocationIdentifier_1'][j]]
        orig_box_item_info_ordered_by_box[0] = np.asarray(orig_box_item_info_ordered_by_box[0]).flatten()
        orig_box_item_info_ordered_by_box[1] = np.asarray(orig_box_item_info_ordered_by_box[1]).flatten()
        orig_box_item_info_ordered_by_box[2] = np.asarray(orig_box_item_info_ordered_by_box[2]).flatten()
        orig_box_item_info_ordered_by_box[3] = np.asarray(orig_box_item_info_ordered_by_box[3]).flatten()
        orig_box_item_info_ordered_by_box[4] = np.asarray(orig_box_item_info_ordered_by_box[4]).flatten()

        uniques, _ = np.unique(np.asarray(orig_node_list_order_boxes_in_batch).flatten())
        origIDXtosolIDXmapping = {}
        for _, val in enumerate(uniques):
            indicieswhereorig = np.argwhere(
                orig_node_list_order_boxes_in_batch == val
            ).flatten()
            indicieswheresol = np.argwhere(solution == val).flatten()
            for j, colval in enumerate(indicieswhereorig):
                #this dict maps orig node indices to the solution node index.
                origIDXtosolIDXmapping[indicieswheresol[j]] = colval
        sortedkeys = np.sort(np.asarray((list(origIDXtosolIDXmapping.keys()))).flatten()).flatten()
        argstomap = []
        for i in range(len(sortedkeys)):
            argstomap.append(origIDXtosolIDXmapping[i])
        argstomap = np.asarray(argstomap).flatten()
        self.box_id_seq = orig_box_item_info_ordered_by_box[0][argstomap]
        self.assignment_id_seq = orig_box_item_info_ordered_by_box[1][argstomap]
        self.material_handling_section_seq = orig_box_item_info_ordered_by_box[2][argstomap]
        self.rack_id_seq = orig_box_item_info_ordered_by_box[3][argstomap]
        self.rack_location_id1_seq = orig_box_item_info_ordered_by_box[4][argstomap]

    def forced_box_extractor(self):

        """
        #Note return dictionary here is likely not to have same index placement of boxIDs, boxnodelists, and times as
        # the original boxqueuedict generated from post input. This DOES NOT matter.
        :return:
        """

        boxIDs = self.solve_dict['boxqueuedict']['boxIDs']

        ###OBS dueDateTime is excluded from V2 json schema as it is not used
        ##uncomment (8 of 16) ONLY IF dueDateTime is reintroduced, currently not needed)
        #times = self.solve_dict['boxqueuedict']['times']
        boxnodelists = self.solve_dict['boxqueuedict']['boxnodelists']

        #Remove 'forced_boxes' from boxqueue dict data
        ForcedBoxArg = np.argwhere(boxIDs == 'forced_boxes').flatten()[0]
        boxIDs = np.delete(boxIDs, ForcedBoxArg).flatten()

        ###OBS dueDateTime is excluded from V2 json schema as it is not used
        ##uncomment (9 of 16) ONLY IF dueDateTime is reintroduced, currently not needed)
        #times = np.delete(times, ForcedBoxArg).flatten()
        boxnodelists = np.delete(boxnodelists, ForcedBoxArg).flatten()

        #get forced boxes data
        fbbsboxIDs = list(self.solve_dict['ForceBatchBoxes']['boxIDs'])
        ###OBS dueDateTime is excluded from V2 json schema as it is not used
        ##uncomment (10,11 of 16) ONLY IF dueDateTime is reintroduced, currently not needed)
        #fbbstimes = list(self.solve_dict['ForceBatchBoxes']['times'])
        # print(self.solve_dict['ForceBatchBoxes']['boxnodelists'], type(self.solve_dict['ForceBatchBoxes']['boxnodelists']), len(fbbsboxIDs))
        fbbsboxnodelists = list(self.solve_dict['ForceBatchBoxes']['boxnodelists'])

        boxIDs = list(boxIDs)
        ###OBS dueDateTime is excluded from V2 json schema as it is not used
        ##uncomment (12 of 16) ONLY IF dueDateTime is reintroduced, currently not needed)
        #times = list(times)
        boxnodelists = list(boxnodelists)
        consolidated_boxIDs = np.asarray(fbbsboxIDs+boxIDs).flatten()
        consolidated_boxnodelists = np.asarray(fbbsboxnodelists + boxnodelists).flatten()

        consolidatedboxqueuedict = {'boxIDs': consolidated_boxIDs, 'boxnodelists': consolidated_boxnodelists}
        ###OBS dueDateTime is excluded from V2 json schema as it is not used
        ##uncomment (13 of 16) ONLY IF dueDateTime is reintroduced, currently not needed)
        #consolidated_times = np.asarray(fbbstimes + times).flatten()

        ###OBS dueDateTime is excluded from V2 json schema as it is not used
        ##uncomment (14 of 16) ONLY IF dueDateTime is reintroduced, currently not needed)
        #consolidatedboxqueuedict = {'boxIDs': consolidated_boxIDs, 'times' :consolidated_times, 'boxnodelists': consolidated_boxnodelists}

        #restoring box ids for all forced boxes
        boxes_in_batch = self.solve_dict['SingleBatchOutput']['BoxesInBatch']
        # extract forced_boxes
        argo = np.argwhere(np.asarray(boxes_in_batch).flatten() == 'forced_boxes').flatten()[0]
        boxes_in_batch = list(boxes_in_batch)
        # print(boxes_in_batch, argo)

        # getting rid of the box called 'forced_boxes',
        # replacing this with the actual forced boxes:
        del boxes_in_batch[argo]
        for forcedbox in self.solve_dict['ForceBatchBoxes']['boxIDs']:
            boxes_in_batch.append(forcedbox)

        return consolidatedboxqueuedict, boxes_in_batch

    @staticmethod
    def set_default(obj):

        """
        set_default
        :param obj:
        :return:
        """
        if isinstance(obj, set):
            return list(obj)
        return []
