from math import asin, sin, cos, atan2, pi, atan, degrees, radians, sqrt, exp
from shapely.geometry import Polygon, Point
import sys
import os
import ROOT
from ROOT import TH1D, TH2D, TH3D, TGraph
import tables
from array import array

print "input run data file:",sys.argv[1]
print "input lidar file:",sys.argv[2]
print "weather file:",sys.argv[3]
print "output file:",sys.argv[4]
print "kml file:",sys.argv[5]

lidar = open(str(sys.argv[2]),'r')
#lidar = open('/home/john_davis/Desktop/RadMAP_Run_Data/14St_Lidar.txt','r')
lidar_data = lidar.readlines()

f = ROOT.TFile(str(sys.argv[4]), "recreate")
OneD_fol = ROOT.TFolder("1D_Graphs","1D_Graphs")
kmlfile = str(sys.argv[5])

infile = open(str(sys.argv[1]), 'r')
event = infile.readlines()
n_events = len(event)

# functions for weather data
def unix2utc(ts):
    from datetime import datetime as dt
    d = dt.utcfromtimestamp(ts)
    return d.strftime('%m/%d/%Y %H:%M:%S')

def FindWeather(weatherfile):
  # find if exists - True / False
  if os.path.isfile(weatherfile):
    weather_avail = True
  else:
    weather_avail = False
  return weather_avail;

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

def FindLatLon(theta,r,ev_lat,ev_lon,R):
    dx = r*cos(theta)
    dy = r*sin(theta)
    lat2 = ev_lat + (180./pi)*(dy/R)
    lon2 = ev_lon + (180./pi)*(dx/R)/(cos(ev_lat*pi/180))
    return [lat2,lon2]

def Pt_SliceR(ev_lat,ev_lon):
  SliceR = Polygon(((coords_right[0],coords_right[1]),
    (coords_right[2],coords_right[3]),
    (coords_right[4],coords_right[5]),
    (coords_right[6],coords_right[7]),
    (coords_right[8],coords_right[9]),
    (coords_right[10],coords_right[11]),
    (coords_right[12],coords_right[13])))
  point = Point((ev_lat,ev_lon))
  slR = point.within(SliceR)
  return slR

def Pt_SliceL(ev_lat,ev_lon):
  SliceL = Polygon(((coords_left[0],coords_left[1]),
    (coords_left[2],coords_left[3]),
    (coords_left[4],coords_left[5]),
    (coords_left[6],coords_left[7]),
    (coords_left[8],coords_left[9]),
    (coords_left[10],coords_left[11]),
    (coords_left[12],coords_left[13])))
  point = Point((ev_lat,ev_lon))
  slL = point.within(SliceL)
  return slL

def Check_14St(ev_lat,ev_lon):
  St_poly = Polygon(((37.80375833333333,-122.26878055555555),
    (37.80314722222222,-122.26916388888888),
    (37.80622222222222,-122.277425),
    (37.80683888888888,-122.277025)))
  point = Point((ev_lat,ev_lon))
  St = point.within(St_poly)
  return St

def Check_DTOAK(ev_lat,ev_lon):
  oak_poly = Polygon(((37.80174722222222,-122.27128888888889),
    (37.80349444444444,-122.27603055555555),
    (37.80786944444444,-122.27381666666666),
    (37.806755555555554,-122.26869166666667),
    (37.812374999999996,-122.26591111111111),
    (37.81121388888889,-122.2636),
    (37.806869444444445,-122.26615555555556),
    (37.80575833333333,-122.26838055555555)))
  point = Point((ev_lat,ev_lon))
  OAK = point.within(oak_poly)
  return OAK

def Check_Poly(ev_lat,ev_lon):
  poly = Polygon(((37.878160,-122.257492), # University Ave
    (37.873646,-122.284185),
    (37.870511,-122.309028),
    (37.863800,-122.305111),
    (37.869214,-122.254670)))
  point = Point((ev_lat,ev_lon))
  Poly = point.within(poly)
  return Poly

def press_corr(ev_press):
  press_I = exp((994.25-ev_press)/168.663)
  return press_I


weather_avail = FindWeather(str(sys.argv[3]))

if weather_avail:
  # weather data file
  tx = open(str(sys.argv[3]), 'r')
  #print 'weather file:',sys.argv[3]

if not weather_avail:
  print '*****************\n','Weather not available for this run\n','*****************'

# set variables for weather data
utctime, bar = ([] for i in range(2)) #utctime, temp, hum, bar, dew, dens, val = ([] for i in range(7))

if weather_avail:
  # read in temp data and fill arrays
  for line in tx:
    if line[0].isdigit():
      data = line.split(',')
      utctime.append(float(data[0])) 
      #temp.append(float(data[3])) 
      #hum.append(float(data[6]))
      bar.append(float(data[18]))
      #dew.append(float(data[7]))
      #dens.append(float(data[28]))

def getWeather(ev_time,idx):
  ev_press = -1  #ev_temp, ev_hum, ev_press, ev_dew, ev_dens = (-1 for i in range(5))#ev_temp, ev_hum, ev_press, ev_dew, ev_dens = (-1 for i in range(5))
  for i in range(idx,len(utctime)-1):
    timecut_low = utctime[i] - (utctime[i]-utctime[i-1])/2
    timecut_high = utctime[i] + (utctime[i+1]-utctime[i])/2
    if timecut_low <= ev_time < timecut_high:
      #ev_temp = temp[i]
      #ev_hum = AbsHum(temp[i],hum[i])
      ev_press = bar[i]
      #ev_dew = dew[i]
      #ev_dens = dens[i]
      #ev_rel_hum = hum[i]
      idx = i
  return ev_press,idx#[ev_temp, ev_hum, ev_press, ev_dew, ev_dens, ev_rel_hum],idx

angle_bins = 36
min_angle = 0
max_angle = 180

# Open Angle hist
oa1 = TH1D("openangle_events","Neutron Event Open Angles",angle_bins,min_angle,max_angle);
oa1.GetXaxis().SetTitle("Open Angle (degrees)")
oa1.GetYaxis().SetTitle("Counts")
oa1.Sumw2()
# press adj
oa1a = TH1D("press_corr_openangle_events","Neutron Event Open Angles",angle_bins,min_angle,max_angle);
oa1a.GetXaxis().SetTitle("Open Angle (degrees)")
oa1a.GetYaxis().SetTitle("Counts")
oa1a.Sumw2()
#
oa2 = TH1D("openangle_time","Neutron Time at Open Angle",angle_bins,min_angle,max_angle);
oa2.GetXaxis().SetTitle("Open Angle (degrees)")
oa2.GetYaxis().SetTitle("Time (s)")

####################################
## Current manual inputs
####################################
#prev_lat = 37.805691
#prev_lon = -122.274619
# truck location (center point)
#lat = 37.805958
#lon = -122.275314
#####################################

r = 25. #m circle radius to search for adjacent buildings
in_r = 15. #m inner radius
R = 6378137. #m earth radius
delta = r/R

# if arc_pts is changed, must change slice coords
arc_pts = 5. # sample pts to make up search "fan"
fan_angle = pi/9. # 20 degree fan opening angle
mid_pt = (arc_pts+1)/2

trav_dist = 0
St14th = False
DTOAK = False
POLY = False
prev_lat = float(event[0].split(',')[3])
prev_lon = float(event[0].split(',')[4])
prev_bearing_lat = prev_lat
prev_bearing_lon = prev_lon
prev_ev_time = float(event[0].split(',')[2])

truck_bearing = 0
prev_truck_bearing = 0

oa_times = []
open_angles = []
CoordAngle = []
SearchPts = []
angle_cts = 0
angle_time = 0

idx = 0

start_event = 0
############
for ent in range(start_event, n_events-1):
  if(ent % (n_events/100) == 0):
    print '%d / %d' % (ent, n_events)

# get event information 
  ev_time = float(event[ent].split(',')[2])
  ev_alt = float(event[ent].split(',')[5])
  ev_detector = int(event[ent].split(',')[1])
  ev_lat = float(event[ent].split(',')[3])
  ev_lon = float(event[ent].split(',')[4])
  next_ev_time = float(event[ent+1].split(',')[2])

  #St14th = Check_14St(ev_lat,ev_lon)
  #DTOAK = Check_DTOAK(ev_lat,ev_lon)
  POLY = Check_Poly(ev_lat,ev_lon)

  last_ct_dist = haversine(prev_lon, prev_lat, ev_lon, ev_lat)
  #print "last_ct_dist:",last_ct_dist
  trav_dist += last_ct_dist
  if trav_dist >= 2.:
    truck_bearing = atan2(cos(prev_bearing_lat)*sin(ev_lat)-sin(prev_bearing_lat)*cos(ev_lat)*cos(ev_lon - prev_bearing_lon),sin(ev_lon - prev_bearing_lon)*cos(ev_lat))
  else:
    truck_bearing = prev_truck_bearing

  #if St14th:
  #if DTOAK:
  if POLY:
    angle_cts += 1
    #angle_time += (ev_time - prev_ev_time)
    angle_time += ((ev_time - prev_ev_time)/2. + (next_ev_time - ev_time)/2.)

  #if not St14th:
  #if not DTOAK:
  if not POLY:  
    angle_cts = 0
    angle_time = 0
    #trav_dist = 0

  #if St14th:
  #if DTOAK:
  if POLY:
    if weather_avail:
        for i in range(idx,len(utctime)-1):
          timecut_low = utctime[i] - (utctime[i]-utctime[i-1])/2
          timecut_high = utctime[i] + (utctime[i+1]-utctime[i])/2
          if timecut_low <= ev_time < timecut_high:
            #ev_temp = temp[i]
            #ev_hum = AbsHum(temp[i],hum[i])
            ev_press = bar[i]
            #ev_dew = dew[i]
            #ev_dens = dens[i]
            #ev_rel_hum = hum[i]
            idx = i

    ev_I_rel = float(press_corr(ev_press))
    ev_corr_ct = 1./ev_I_rel
    #print ev_corr_ct

    #print "travel distance",trav_dist
    #print "truck bearing:",truck_bearing
    bearing = (degrees(truck_bearing)+360)%360
    #print "truck bearing:",bearing
    rad_bear = radians(bearing)

    coords_left = []
    coords_right = []

    '''coords_left.append(ev_lat)
    coords_left.append(ev_lon)
    coords_right.append(ev_lat)
    coords_right.append(ev_lon)'''

    for i in range(1,int(arc_pts)+1):
        #theta = truck_bearing + pi*2*i/circlepts # bearing based on sample - start at bearing and go clockwise from there
        thetaL = truck_bearing + pi/2. + ((mid_pt-i)/(arc_pts-1))*fan_angle # bearing based on sample
        thetaR = thetaL - pi # 180 degree to get other side
        #lat2 = asin(sin(lat)*cos(delta)+cos(lat)*sin(delta)*cos(theta))
        #lon2 = lon + atan2(sin(theta)*sin(delta)*cos(lat), cos(delta)-sin(lat)*sin(lat2))

        if i == 1:
            R_lat_lon = FindLatLon(thetaR,in_r,ev_lat,ev_lon,R) # find inside radius point
            lat2R = R_lat_lon[0]
            lon2R = R_lat_lon[1]
            coords_right.append(lat2R)
            coords_right.append(lon2R)
            L_lat_lon = FindLatLon(thetaL,in_r,ev_lat,ev_lon,R)
            lat2L = L_lat_lon[0]
            lon2L = L_lat_lon[1]
            coords_left.append(lat2L)
            coords_left.append(lon2L)

        R_lat_lon = FindLatLon(thetaR,r,ev_lat,ev_lon,R)
        lat2R = R_lat_lon[0]
        lon2R = R_lat_lon[1]
        coords_right.append(lat2R)
        coords_right.append(lon2R)

        L_lat_lon = FindLatLon(thetaL,r,ev_lat,ev_lon,R)
        lat2L = L_lat_lon[0]
        lon2L = L_lat_lon[1]
        coords_left.append(lat2L)
        coords_left.append(lon2L)

        if i == int(arc_pts):
            R_lat_lon = FindLatLon(thetaR,in_r,ev_lat,ev_lon,R) # find inside radius point
            lat2R = R_lat_lon[0]
            lon2R = R_lat_lon[1]
            coords_right.append(lat2R)
            coords_right.append(lon2R)
            L_lat_lon = FindLatLon(thetaL,in_r,ev_lat,ev_lon,R)
            lat2L = L_lat_lon[0]
            lon2L = L_lat_lon[1]
            coords_left.append(lat2L)
            coords_left.append(lon2L)

    SearchPts.append([coords_left,coords_right])

    R_pts = []
    L_pts = []

    '''print "Lat/Lon:",ev_lat,ev_lon
    print "Coords L:",coords_left
    print "Coords R:",coords_right'''

    # define lidar search range based on truck lon, then lat
    lon_start = ev_lon + 3e-4  # about 26 meters from the truck
    lon_stop = ev_lon - 3e-4
    lat_start = ev_lat - 3e-4   # about 30 meters from truck
    lat_stop = ev_lat + 3e-4

    # declare indicies
    start_idx = 0
    start_found = False
    stop_idx = len(lidar_data)
    stop_found = False
    # find indicies based on truck location
    for i in range(0,len(lidar_data)):
        lidar_lat = float(lidar_data[i].split(',')[1])
        lidar_lon = float(lidar_data[i].split(',')[0])
        if not start_found and lon_start >= lidar_lon:
            start_idx = i
            start_found = True
        if not stop_found and lon_stop >= lidar_lon:
            stop_idx = i
            stop_found = True
        if start_found and stop_found:
            break

    for i in range(start_idx,stop_idx):
        lidar_lat = float(lidar_data[i].split(',')[1])
        lidar_lon = float(lidar_data[i].split(',')[0])
        lidar_alt = float(lidar_data[i].split(',')[2])
        if lat_start <= lidar_lat <= lat_stop:  # only if lat is within this region, commence search near truck 
            pt_in_R = Pt_SliceR(lidar_lat,lidar_lon)
            if not pt_in_R:
                pt_in_L = Pt_SliceL(lidar_lat,lidar_lon)
            if pt_in_R:
                R_pts.append([lidar_lat,lidar_lon,lidar_alt])
            if pt_in_L:
                L_pts.append([lidar_lat,lidar_lon,lidar_alt])

    # find max in each array
    '''R_hi = [0,0,0]
    for i in range(0,len(R_pts)):
        if R_pts[i][2] > R_hi[2]:
            R_hi = R_pts[i]
    L_hi = [0,0,0]
    for j in range(0,len(L_pts)):
        if L_pts[j][2] > L_hi[2]:
            L_hi = L_pts[j]

    #print "right side high point:",R_hi
    #print "left side high point:",L_hi
    CoordAngle = []
    R_angle = atan((haversine(ev_lon, ev_lat, R_hi[1], R_hi[0]))/R_hi[2])
    #print "Right side angle:",R_angle
    L_angle = atan((haversine(ev_lon, ev_lat, L_hi[1], L_hi[0]))/L_hi[2])
    #print "Left side angle:",L_angle
    Open_Angle = degrees(R_angle+L_angle)
    print "Lat:",ev_lat,"Lon:",ev_lon
    print "Open Angle:",Open_Angle
    CoordAngle.append([ev_lat,ev_lon,Open_Angle,bearing])'''

    min_R_angle = pi/2.
    min_R_ang_idx = -1
    min_L_angle = pi/2.
    min_L_ang_idx = -1

    #print R_pts
    #print L_pts

    for j in range(0,len(R_pts)):
      if R_pts[j][2] >= ev_alt + 2: # only look at points that are at least 2 meters above truck alt
        R_angle = atan((haversine(ev_lon, ev_lat, R_pts[j][1], R_pts[j][0]))/(R_pts[j][2]-ev_alt))
        if R_angle < min_R_angle:
            min_R_angle = R_angle
            min_R_ang_idx = j

    for j in range(0,len(L_pts)):
      if L_pts[j][2] >= ev_alt + 2:
        L_angle = atan((haversine(ev_lon, ev_lat, L_pts[j][1], L_pts[j][0]))/(L_pts[j][2]-ev_alt))
        if L_angle < min_L_angle:
            min_L_angle = L_angle
            min_L_ang_idx = j

    '''if min_R_ang_idx == -1:
        min_R_angle = pi/2.
    if min_L_ang_idx == -1:
        min_L_angle = pi/2.'''

    #print "right side angle / coords:",min_R_angle,R_pts[min_R_ang_idx]
    #print "left side angle / coords:",min_L_angle,L_pts[min_L_ang_idx]
    Open_Angle = degrees(min_R_angle+min_L_angle)
    #print "Coordinates:",ev_lat,ev_lon
    print ent
    print "Open Angle:",Open_Angle
    #print "Count Rate:",angle_cts/angle_time
    CoordAngle.append([ev_lat,ev_lon,Open_Angle,ev_alt,bearing])
    oa_times.append(ev_time)
    open_angles.append(Open_Angle)
    # fill hists for this angle bin
    oa1.Fill(Open_Angle,angle_cts)
    oa1a.Fill(Open_Angle,ev_corr_ct)
    oa2.Fill(Open_Angle,angle_time)
    # reset
    #trav_dist = 0
    angle_cts = 0
    angle_time = 0

  #reset variables
  prev_lat = ev_lat
  prev_lon = ev_lon
  prev_ev_time = ev_time
  prev_truck_bearing = truck_bearing
  if trav_dist >= 2.:
    trav_dist = 0
    prev_bearing_lat = ev_lat
    prev_bearing_lon = ev_lon

##################
#print "All open angles:",CoordAngle

for x in range(0,angle_bins+1):
  oa2.SetBinError(x,0.)

# CR hist
oa3 = oa1.Clone()
oa3.SetTitle("Count Rate Given Open Angle")
oa3.SetName("openangle_count_rate")
oa3.Divide(oa2)
oa3.GetXaxis().SetTitle("Open Angle (degrees)")
oa3.GetYaxis().SetTitle("Count Rate (CPS)")
# Corr CR hist
oa3a = oa1a.Clone()
oa3a.SetTitle("Pressure Adjusted Count Rate Given Open Angle")
oa3a.SetName("press_corr_openangle_count_rate")
oa3a.Divide(oa2)
oa3a.GetXaxis().SetTitle("Open Angle (degrees)")
oa3a.GetYaxis().SetTitle("Count Rate (CPS)")

n_points = len(oa_times)
oa_time = TGraph(n_points,array('d',oa_times),array('d',open_angles))
oa_time.SetName("oa_v_time")
oa_time.SetTitle("Open Angles")
oa_time.GetXaxis().SetTitle("Time (sec)")
oa_time.GetYaxis().SetTitle("Open Angle (degrees)")
OneD_fol.Add(oa_time)

OneD_fol.Write()
f.Write()
f.Close()
lidar.close()
infile.close()

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
                KML.width(5),
                KML.color('64147800'),
            ),
        KML.PolyStyle(
            KML.color('5f14B400'),
        ),
            id="GreenPoly"
        ),
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
kmlobj.Document.append(
    KML.Style(
        KML.IconStyle(
            KML.scale(1.0),
            KML.color('64147800'),
            KML.Icon(
                KML.href('http://maps.google.com/mapfiles/kml/shapes/shaded_dot.png'),
            ),
        ),
        KML.LabelStyle(
            KML.scale(0.75),
        ),
            id="green_dot"
    ),
)

ct=0
plot = False
for i in range(0,len(CoordAngle)):
  ct+=1
  if ct == 5:
    plot = True
    ct = 0
  else:
    plot = False
  if plot:
      kmlobj.Document.append(
        KML.Placemark(
            KML.name(i,"_",'%.1f' % CoordAngle[i][2]),
            KML.description('Open Angle: {angle}'.format(
                angle=CoordAngle[i][2]
                ),
            ),
            KML.styleUrl('#green_dot'),
            KML.Point(
                KML.altitudeMode('absolute'),
                KML.coordinates('{lon},{lat},{elev}'.format(
                            lon=CoordAngle[i][1],
                            lat=CoordAngle[i][0],
                            elev=CoordAngle[i][3]+3.,
                            ),
                ),
            ),
        ),
      )
      kmlobj.Document.append(
        KML.Placemark(
            KML.name(i,"_Side1"),
            KML.styleUrl('#GreenPoly'),
            KML.Polygon(
                KML.extrude(1),
                KML.altitudeMode('absolute'),
                KML.outerBoundaryIs(
                    KML.LinearRing(
                        KML.coordinates('{lon1},{lat1},{elev},{lon2},{lat2},{elev},{lon3},{lat3},{elev},{lon4},{lat4},{elev},{lon5},{lat5},{elev},{lon6},{lat6},{elev},{lon7},{lat7},{elev},{lon1},{lat1},{elev}'.format(
                            lon1=SearchPts[i][0][1],
                            lat1=SearchPts[i][0][0],
                            lon2=SearchPts[i][0][3],
                            lat2=SearchPts[i][0][2],
                            lon3=SearchPts[i][0][5],
                            lat3=SearchPts[i][0][4],
                            lon4=SearchPts[i][0][7],
                            lat4=SearchPts[i][0][6],
                            lon5=SearchPts[i][0][9],
                            lat5=SearchPts[i][0][8],
                            lon6=SearchPts[i][0][11],
                            lat6=SearchPts[i][0][10],
                            lon7=SearchPts[i][0][13],
                            lat7=SearchPts[i][0][12],
                            elev=CoordAngle[i][3]+5.,
                            ),
                        ),
                    ),
                ),
            ),
        ),
      )
      kmlobj.Document.append(
        KML.Placemark(
            KML.name(i,"_Side2"),
            KML.styleUrl('#GreenPoly'),
            KML.Polygon(
                KML.extrude(1),
                KML.altitudeMode('absolute'),
                KML.outerBoundaryIs(
                    KML.LinearRing(
                        KML.coordinates('{lon1},{lat1},{elev},{lon2},{lat2},{elev},{lon3},{lat3},{elev},{lon4},{lat4},{elev},{lon5},{lat5},{elev},{lon6},{lat6},{elev},{lon7},{lat7},{elev},{lon1},{lat1},{elev}'.format(
                            lon1=SearchPts[i][1][1],
                            lat1=SearchPts[i][1][0],
                            lon2=SearchPts[i][1][3],
                            lat2=SearchPts[i][1][2],
                            lon3=SearchPts[i][1][5],
                            lat3=SearchPts[i][1][4],
                            lon4=SearchPts[i][1][7],
                            lat4=SearchPts[i][1][6],
                            lon5=SearchPts[i][1][9],
                            lat5=SearchPts[i][1][8],
                            lon6=SearchPts[i][1][11],
                            lat6=SearchPts[i][1][10],
                            lon7=SearchPts[i][1][13],
                            lat7=SearchPts[i][1][12],
                            elev=CoordAngle[i][3]+5.,
                            ),
                        ),
                    ),
                ),
            ),
        ),
      )

file = open(kmlfile, "w")
file.write(etree.tostring(etree.ElementTree(kmlobj),pretty_print=True))
file.close()
#print etree.tostring(etree.ElementTree(kmlobj),pretty_print=True)