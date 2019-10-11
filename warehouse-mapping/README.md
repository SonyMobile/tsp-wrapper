# Warehouse graph generation
The python modules here are the steps used to digitize a warehouse.

### Special dependencies:
matplotlib, shapely, networkx, also for post-processing:
concorde_wrapper (with same installation as in the concorde_wrapper
service), PyQt5.  The steps below were all carried out by running
modules one by one in the warehouse-digitization repo.

## Prerequisites:

### Map cropping and measuring:

Before the walkthrough can start the warehouse layout map
(FloormapShelfzone_KCO.xlsx) needs to be cropped (unless the WMS has
provided an already well cropped image - which they never have done so
far) and the scale of the crop needs to be known.  Usually the image
provided by the WMS includes a bunch of irrelevant info, which should
be removed from the crop.  Save the crop as a .png. I used Windows
Paint to do this (i.e. the simplest drawing software).  In the future
there may be cases which require more work on the map (e.g. rescaling)
and then Paint won't suffice.  The output from this step is mapKC.png
in the warehouse-digitization repo.

### Obstacles generation
First visualize the warehouse map using matplotlib. Make sure extent
is set according to the crop scale produced in the map cropping
step. Make sure you can see the coordinates of the mouse cursor in the
matplotlib window.  Using the coordinates shown by the cursor and
programming, create a datastructure that contains the coordinates of
all the racks, starting at top left of racks and going clockwise.

### Stopping position generation
Look at the warehouse pick location description file shared from the
warehouse, the layout map and if necessary the raw pick log dump to
deduce where all their pick locations are on the map. Usually this
also involves a meeting with a warehouse floor manager who can
explain it properly. Decide how raw pick locations are going to be
translated into "stop locations".  There is no need to have more stop
locations than one every 1 - 3 meters in the warehouse.  In the
sample code each orange box gets one stop location. Create a
structure that will contain all "stop locations" in the warehouse.
In the sample code it is called "stop_locs". Insert all stop
locations into this structure so that all of them contain x, y
coordinates and names that correspond to part of their name in pick
locations in the log dump.  Also insert a stop locations that denote
the start and end locations for pick runs in the warehouse.  In the
sample code the start and end are the same location and they are
called "depot". Visualize and verify the contents of the generated
datastructures using matplotlib and debugger.

### Enumeration
Give a unique node index number, 0 - , to all the stop_loc and
obstacles coordinates generated in the previous steps.  In the sample
code, the depot is given index 0, then all stop locations are
enumerated followed by the obstacles.  The names (id) of all stop
locations following the enumerated index order;
REALOBJECTCORNERINDICIES: List of obstacles with corresponding node
index. OBSTACLESANDDUMMYOBSTACLES: List of obstacles with
corresponding x, y coordinate tuples.

## Graph generation
Call the generateADJMAT function using OBSTACLESANDDUMMYOBSTACLES,
allcoords and REALOBJECTCORNERINDICIES as inputs.  This generates
ADJMAT, which is a matrix that only says whether nodes are directly
connected i.e.  True for all the nodes that are directly connected
without passing through any obstacle, False otherwise.  It also
generates polylist, which is very similar to OBSTACLESANDDUMMOBSTACLES
above but transformed into Shapely objects.  Call
visualizeAdjMat(ADJMAT, polylist, allcoords) to visualize all node
connectivity.  If there are any lines going through obstacles then
something went wrong in a previous step.  Doing this visualization for
a full warehouse takes ~2 minutes. P.S. comment out calls to
generateADJMAT and visualizeAdjMat whenever they are not used. Call
generateWeightedADJMAT(allcoords, ADJMAT). This generates WADJMAT
which gives the distances between all nodes that are directly
connected. generateGraphNetwork(ADJMAT, WADJMAT, allcoords).  This
gives distmat, which gives all distances between all nodes, and
SPNODESPATH, which provides info on how to get from one node to
another following the shortest route in the warehouse.

## Postprocessing (not included in repo)
Steps that may be necessary to make use of the warehouse files:
Transorm SPNODESPATH into two files startendndarray and spnodeslist
which are numpy arrays that together fulfill the functionality of
SPNODESPATH. This step is necessary to reduce RAM usage since
SPNODESPATH takes up lots of RAM. Generate fake pick runs: Generate a
dict, pick_runs0, that contains a couple of lists with randomly
generated node indicies e.g. [0, 43, 2, 15, 18, 0] which starts at the
depot (0), then goes through some stop locations and then returns to
the depot. Solve and visualize the fake pick runs using PyQt GUI. This
module solves and visualizes the digitization and the fake pick runs
from above. Keydict is a file that has stop location coordinates as
keys and node index as value. This can also be generated
earlier. Extract real historical picks from picking log dump. Create
json requests out of the real pick runs above. In the concorde_wrapper
python repo, run main.py flask server. Send the above requests to the
flask server. If a json pick run response comes back it means
optimization succeeded.


##Notes/lessons learned:
- concorde_wrapper basically never fails when pick runs have between
  5-300 items and there aren't too many duplicate pick locations in the
  request. It is easy to think that when concorde_wrapper behaves
  strangely it is because there is something wrong with
  concorde_wrapper, but in fact it is much more likely that something
  went wrong in the warehouse digitization steps. One example is when
  the keydict is wrong in some way so that there are many pick location
  tags that point to the same node indicies.
- No rack/obstacle generation needed at map edges.
- It saves a ton of time in graph generation, and also limits the
  graph file sizes, to compress the pick locations into fewer stop
  locations. There is no need to have more than 1 stop location every
  1 - 3 meters.
- Johan has done this 3 times and finds it very hard to write generic
  functions for the modules "obstacles" and "stop_pos" due to the
  variations between warehouses. The data structures these modules
  generate are tied to the warehouse log dumps and these have so far
  been very different.
