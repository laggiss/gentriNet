"""

Script modified from amaury's downloader.py.  Specifically this randomly selects a point within a road segment for each road segment.
Then, from that list of random points, a subset is randomly selected for downlading.  For each point with more than one
available panorama, a single one is randomly selected for download at a given location.

A shapefile must be available with the random points and must contain the downstreet bearing as well as a field that identifies
each road segment.

I used polyline to segment tool in arcgis, followed by the add geometry bearing tool and finally the vertices to segments and a spatial join from segments to vertices
to create the shapefile used here.

"""

import numpy as np
from scipy import misc
#import gist
import streetview
from osgeo import ogr
import random
import pandas as pan

API_KEY = 'YOUR API KEY'


# ------------------------------------------------------------------------------




"""

Downloads Google StreetView images of random points in Ottawa



:param n_loc: number of locations to download. CAUTION: some points have no images, so it's not the exact number of subdirectories created

"""

# Output folder for panaorama images
DIRECTORY = r'C:\gist\roads'

# Shapefile with points on roads with bearing of roads and segment grouping variable
ds = ogr.Open(r'C:\gist\roads\roadpointswithbearing2.dbf')

# number of samples for each road segment
nptsSample = 1

# number of subsamples for all grouped road segments
nsubsample = 10

# Get layer
layer = ds.GetLayer()

# Create list of road segment identifiers
elist=[row.GetField("RD_SEGMENT") for row in layer]

# Create list of indices which is the same length as the number of rows in the
#   shapefile containing the x,y,bearing information (could also get an object id if base 0 in shapefile)
idx = range(0,len(elist))

# Merge the list of idices and segment identifiers into a pandas dataframe for sampling
df=pan.DataFrame.from_items([('idx',idx),('elist',elist)])

# Sample n points on each road segment.  Each road segment contains the same identifier
#   so group by identifier and then sample n points within each group outputting to the new dataframe.

tt=df.groupby('elist').apply(pan.DataFrame.sample, n=nptsSample).reset_index(drop=True)

# Get the IDs from the random sample dataframe, tt, in order to identify the rows in the original
#   shapefile at which to get the panorama
ransample=tt['idx'].tolist()

# Set progress counter
prog=1

# Get a set of n random subsamples from grouped road segments
n_loc=[random.randint(0,len(ransample)) for i in range(0,nsubsample)]

# Download for each random segment subsample
for i in n_loc:

    print('%.2f' % (i * 100 / prog) + " %")

    # get feature geometry and bearing from shapefile
    feature = layer[ransample[i]]

    lon = feature.GetGeometryRef().GetX()

    lat = feature.GetGeometryRef().GetY()

    heading = feature.GetField("BEARING")

    # Get the number of panaoramas at the location
    panIds = streetview.panoids(lat, lon)

    # Randomly select one of the n panaormas at this location
    if len(panIds) > 0:


        pid = random.randint(0,len(panIds)-1)

        img = streetview.api_download(panIds[pid]["panoid"], heading, DIRECTORY, API_KEY, fov=80, pitch=0,year=panIds[pid]["year"])

    prog+=1