import os
import sys

from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2.)**2. + cos(lat1) * cos(lat2) * sin(dlon/2.)**2.
    c = 2. * asin(sqrt(a)) 

    # 6378.1 km is the radius of the Earth = 6378100 m
    m = 6378100. * c
    return m

# Load the time-sorted event text file
infile = open(str(sys.argv[1]), 'r')
event = infile.readlines()

# out dir
#outdir = '/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/Converted/GPS_Kml/'

#output file
outfile = str(sys.argv[2])
#outfile = outdir+str(sys.argv[1])[-24:-4]+'.kml'

n_events = len(event)

lat_lidar = []
lon_lidar = []
elev = []

for ent in range(0, n_events):
#for ent in range(15000000, 20000000):
  if(ent % (n_events/100) == 0):
    print '%d / %d' % (ent, n_events)

  # get event information 
  ev_lat = float(event[ent].split(',')[1])
  ev_lon = float(event[ent].split(',')[0])
  ev_elev = float(event[ent].split(',')[2])
  lat_lidar.append(ev_lat)
  lon_lidar.append(ev_lon)
  elev.append(ev_elev)
 
# ****************** KML FILE WRITE **********************
# ********************************************************

#!/usr/bin/python
# a Python script that uses pyKML to create overlay of GPS count rates
from lxml import etree
from pykml.factory import KML_ElementMaker as KML

kmlobj = KML.kml(
    KML.Document(
    )
)
kmlobj.Document.append(
    KML.Style(
        KML.IconStyle(
            KML.scale(0.3),
            KML.color('641400D2'),
	        KML.Icon(
                KML.href('http://maps.google.com/mapfiles/kml/shapes/shaded_dot.png'),
            ),
	    ),
        KML.LabelStyle(
            KML.scale(0),
        ),
            id="red_dot"
    ),
)

ct=0
plot = False
for i in range(0,len(elev)):
  ct+=1
  if ct == 3:
    plot = True
    ct = 0
  else:
    plot = False

  if plot:
      kmlobj.Document.append(
	    KML.Placemark(
            KML.name(i),
            KML.description('Elevation: {elev}'.format(
                elev=elev[i]
                ),
            ),
            KML.styleUrl('#red_dot'),
            KML.Point(
                KML.altitudeMode('absolute'),
                KML.coordinates('{lon},{lat},{elev}'.format(
                            lon=lon_lidar[i],
                            lat=lat_lidar[i],
                            elev=elev[i],
                            ),
                ),
	        ),
	    ),
      )

file = open(outfile, "w")
file.write(etree.tostring(etree.ElementTree(kmlobj),pretty_print=True))
file.close()
#print etree.tostring(etree.ElementTree(kmlobj),pretty_print=True)
