import os
import sys
import os.path
import operator
from shapely.geometry import Polygon, Point

print "input file:",sys.argv[1]
print "output file:",sys.argv[2]

lidar = open(str(sys.argv[1]),'r') # input file
LidarOut = open(str(sys.argv[2]),'w') # output file

sift = False # sift means select only points within polygon
sort = True # sort by lat then lon

lidar_data = lidar.readlines()

def Check_Poly(ev_lat,ev_lon):
  #St_poly = Polygon(((37.80375833333333,-122.26878055555555),
  #  (37.80314722222222,-122.26916388888888),
  #  (37.80622222222222,-122.277425),
  #  (37.80683888888888,-122.277025)))
  '''St_poly = Polygon(((37.80174722222222,-122.27128888888889),
    (37.80349444444444,-122.27603055555555),
    (37.80786944444444,-122.27381666666666),
    (37.806755555555554,-122.26869166666667),
    (37.812374999999996,-122.26591111111111),
    (37.81121388888889,-122.2636),
    (37.806869444444445,-122.26615555555556),
    (37.80575833333333,-122.26838055555555)))'''
  '''poly = Polygon(((37.878160,-122.257492),   # university Ave
    (37.873646,-122.284185),
    (37.870511,-122.309028),
    (37.863800,-122.305111),
    (37.869214,-122.254670)))'''
# dt oakland (larger region)
  poly = Polygon(((37.812594,-122.270164),
    (37.822968,-122.267433),
    (37.821722,-122.259872),
    (37.797118,-122.249193),
    (37.787229,-122.263842),
    (37.794675,-122.289563),
    (37.805828,-122.288179),
    (37.802708,-122.278026)))
  point = Point((ev_lat,ev_lon))
  in_poly = point.within(poly)
  return in_poly

if sift:
    if sort:
        lidar_sort = []
    in_poly = False
    for i in range(1,len(lidar_data)):
        if(i % (len(lidar_data)/100) == 0):
            print '%d / %d' % (i, len(lidar_data))
        ev_lat = float(lidar_data[i].split(',')[1])
        ev_lon = float(lidar_data[i].split(',')[0])
        ev_alt = float(lidar_data[i].split(',')[2])
        in_poly = Check_Poly(ev_lat,ev_lon)
        if in_poly and not sort:
            LidarOut.write('{lon},{lat},{alt},\n'.format(lon=ev_lon,
            lat=ev_lat,
            alt='%.3f' % ev_alt))
        if in_poly and sort:
            lidar_sort.append(lidar_data[i])
        in_poly = False

if sort:
    print "sorting data..."

    if not sift:   # just take lidar input and sort it, write to specified output
        lidar_sort = []
        for i in range(0,len(lidar_data)):
            lidar_sort.append(lidar_data[i])

    sorted_events = sorted(lidar_sort)#, key=lambda lidar_sort: lidar_sort);
    for i in range(0, len(sorted_events)):
        LidarOut.write(sorted_events[i])

lidar.close()