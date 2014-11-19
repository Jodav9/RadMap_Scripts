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
outdir = '/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/Converted/GPS_Kml/'

#output file
outfile = str(sys.argv[2])
#outfile = outdir+str(sys.argv[1])[-24:-4]+'.kml'

# PARAMS
start_event = 0
n_events = len(event)
#dx = 100. # meters
dx = 25. # meters

lat_neutron = []
lon_neutron = []
lat_gamma = []
lon_gamma = []
samepos_n = []
samepos_g = []
pos_error = []
timepos = []
countpos = []
epochtimeBegin = []
epochtimeEnd = []
distance = []
elevBegin = []
elevEnd = []

beg_time = float(event[0].split(',')[2])
beg_lat = float(event[0].split(',')[3])
beg_lon = float(event[0].split(',')[4])
beg_elev = float(event[0].split(',')[5])
trav_dist = 0.
ev_speed = 0.
samepos_ncount = 0
samepos_gcount = 0
ncount = 0
gcount = 0

for ent in range(start_event+1, n_events):
#for ent in range(15000000, 20000000):
  if(ent % (n_events/100) == 0):
    print '%d / %d' % (ent, n_events)

  # get event information 
  ev_time = float(event[ent].split(',')[2])
  ev_lat = float(event[ent].split(',')[3])
  ev_lon = float(event[ent].split(',')[4])
  ev_elev = float(event[ent].split(',')[5])

# travel dist calc
  trav_dist = haversine(beg_lon, beg_lat, ev_lon, ev_lat)
# neutron events speed calc
  delta_t =  ev_time - beg_time

  if(delta_t > 0):
    ev_speed = trav_dist/(delta_t)

#  if(trav_dist <= dx or samepos_ncount < 75 or ev_speed > 32.): # or delta_t < 15.625
  if(trav_dist <= dx or samepos_ncount < 50 or ev_speed > 32.):
    samepos_ncount += 1
  else:
    lat_neutron.append(beg_lat)
    lon_neutron.append(beg_lon)
    samepos_n.append(samepos_ncount/delta_t)#avg count rate in CPS
    countpos.append(samepos_ncount)#counts in position bin
    timepos.append(delta_t) #time in given position bin
    epochtimeBegin.append(beg_time)#epoch time entered bin
    epochtimeEnd.append(ev_time) #epoch time exited bin
    elevBegin.append(beg_elev) # elev entered bin
    elevEnd.append(ev_elev) # elev exited bin
    error = ((samepos_ncount**(0.5))/samepos_ncount)*(samepos_ncount/delta_t)
    pos_error.append(error)
    distance.append(trav_dist)
    # reset
    beg_time = ev_time
    beg_lat = ev_lat
    beg_lon = ev_lon
    beg_elev = ev_elev
    samepos_ncount = 0
    trav_dist = 0 
# for last event...
  if (ent == n_events-1):
    lat_neutron.append(beg_lat)
    lon_neutron.append(beg_lon)
    # append last event lat and lon...
    lat_neutron.append(ev_lat)
    lon_neutron.append(ev_lon)
    samepos_n.append(samepos_ncount/delta_t)#avg count rate in CPS
    countpos.append(samepos_ncount)#counts in position bin
    timepos.append(delta_t) #time in given position bin
    epochtimeBegin.append(beg_time)#epoch time entered bin
    epochtimeEnd.append(ev_time) #epoch time exited bin
    elevBegin.append(beg_elev) # elev entered bin
    elevEnd.append(ev_elev) # elev exited bin
    error = ((samepos_ncount**(0.5))/samepos_ncount)*(samepos_ncount/delta_t)
    pos_error.append(error)
    distance.append(trav_dist)


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
            KML.LineStyle(
                KML.width(50),
		KML.color(64780000),
            ),
	    KML.PolyStyle(
		KML.color(50780000),
	    ),
            id="transBluePoly"
        ),
)
kmlobj.Document.append(
	KML.Style(
            KML.LineStyle(
                KML.width(10),
		KML.color('641400D2'),
            ),
            KML.PolyStyle(
		KML.color('0FFFFFF'), 
	    ),
            id="clearRedPoly"
        ),
)
#kmlobj.Document.append(
#	KML.Style(
#            KML.BalloonStyle( 
#                KML.text(
#                    'Event Info:'
#                )        
#	    ),
#            id="dataBalloon"
#        ),
#)
# add placemarks to the Document element - neutrons
i=0;
for i in range(1,len(samepos_n)):
      kmlobj.Document.append(
	    KML.Placemark(
                KML.name(i,"_",'%.3f' % samepos_n[i],"_CPS"),
                KML.description('Counts: {cts}\n Time Range: {etb} - {ete}\n Time: {time} sec\n Count Rate: {cr} CPS\n Error: {err} CPS\n Distance: {dist} m\n Elevation Enter: {elevb} m\n Elevation Exit: {eleve} m'.format(
                    cts=countpos[i],
                    etb='%.2f' % epochtimeBegin[i],
                    ete='%.2f' % epochtimeEnd[i],
                    time='%.4f' % (timepos[i]),
                    cr='%.4f' % samepos_n[i],
                    err='%.4f' % pos_error[i],
		            dist='%.2f' % distance[i],
                    elevb=elevBegin[i],
                    eleve=elevEnd[i],
                    ),
                ),
                KML.styleUrl('#transBluePoly'),
                KML.Polygon(
                    KML.extrude(1),
                    KML.altitudeMode('relativeToGround'),
		    KML.outerBoundaryIs(
		        KML.LinearRing(
                            KML.coordinates('{lon1},{lat1},{alt},{lon2},{lat2},{alt},{lon1},{lat1},{alt}'.format(
                                lon1=lon_neutron[i],
                                lat1=lat_neutron[i],
                                alt=samepos_n[i]*500.,
			                    lon2=lon_neutron[i+1],
                                lat2=lat_neutron[i+1],
                                ),
                    	    ),
		        ),
		    ),
                ),
            ),
      )

'''i=0;
for i in range(1,len(samepos_n)-1):
      kmlobj.Document.append(
	    KML.Placemark(
                KML.name(i,"_err_",'%.4f' % pos_error[i+1],"_CPS"),
                KML.styleUrl('#clearRedPoly'),
                KML.Polygon(
                    KML.extrude(1),
                    KML.altitudeMode('relativeToGround'),
		    KML.outerBoundaryIs(
			KML.LinearRing(
                    	    KML.coordinates('{lon1},{lat1},{alt},{lon2},{lat2},{alt},{lon1},{lat1},{alt}'.format(
                            	lon1=lon_neutron[i],
                            	lat1=lat_neutron[i],
                            	alt=(pos_error[i+1]+samepos_n[i+1])*500.,
			    	lon2=lon_neutron[i+1],
                            	lat2=lat_neutron[i+1],
                           	),
                    	    ),
			),
		    ),
                ),
            ),
      )'''
file = open(outfile, "w")
file.write(etree.tostring(etree.ElementTree(kmlobj),pretty_print=True))
file.close()
#print etree.tostring(etree.ElementTree(kmlobj),pretty_print=True)
