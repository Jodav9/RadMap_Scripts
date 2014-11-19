from math import asin, sin, cos, atan2, pi, atan, degrees, radians, sqrt, exp
from shapely.geometry import Polygon, Point
import ntpath
import sys
import os
import ROOT
from ROOT import TH1D, TH2D, TH3D, TGraph
import tables
from array import array

weatherdir = '/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/Weather/'
gpsdir = '/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/NewGPS/'

# assign gps filename
in_file_name = ntpath.basename(str(sys.argv[1]))
yr = in_file_name[7:11]
mo = in_file_name[1:3]
day = in_file_name[4:6]
gps_file = open(gpsdir+yr+mo+day+'.txt','r')
gps_ev = gps_file.readlines()
n_gps = len(gps_ev) 

# weather file
weatherfile = weatherdir+yr+'-'+mo+'.csv'

print "input run data file:",sys.argv[1]
print "input lidar file:",sys.argv[2]
print "weather file:",weatherfile
print "GPS file:",gpsdir+yr+mo+day+'.txt'
print "output file:",sys.argv[3]
print "kml file:",sys.argv[4]

lidar = open(str(sys.argv[2]),'r')
#lidar = open('/home/john_davis/Desktop/RadMAP_Run_Data/14St_Lidar.txt','r')
lidar_data = lidar.readlines()

f = ROOT.TFile(str(sys.argv[3]), "recreate")
OneD_fol = ROOT.TFolder("1D_Graphs","1D_Graphs")
kmlfile = str(sys.argv[4])

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
    (coords_right[8],coords_right[9])))
    #(coords_right[10],coords_right[11]),
    #(coords_right[12],coords_right[13])))
  point = Point((ev_lat,ev_lon))
  slR = point.within(SliceR)
  return slR

def Pt_SliceL(ev_lat,ev_lon):
  SliceL = Polygon(((coords_left[0],coords_left[1]),
    (coords_left[2],coords_left[3]),
    (coords_left[4],coords_left[5]),
    (coords_left[6],coords_left[7]),
    (coords_left[8],coords_left[9])))
    #(coords_left[10],coords_left[11]),
    #(coords_left[12],coords_left[13])))
  point = Point((ev_lat,ev_lon))
  slL = point.within(SliceL)
  return slL

'''def Check_14St(ev_lat,ev_lon):
  St_poly = Polygon(((37.80375833333333,-122.26878055555555),
    (37.80314722222222,-122.26916388888888),
    (37.80622222222222,-122.277425),
    (37.80683888888888,-122.277025)))
  point = Point((ev_lat,ev_lon))
  St = point.within(St_poly)
  return St'''

### Downtown Oakland
'''def Check_Poly(ev_lat,ev_lon):
  poly = Polygon(((37.80174722222222,-122.27128888888889),
    (37.80349444444444,-122.27603055555555),
    (37.80786944444444,-122.27381666666666),
    (37.806755555555554,-122.26869166666667),
    (37.812374999999996,-122.26591111111111),
    (37.81121388888889,-122.2636),
    (37.806869444444445,-122.26615555555556),
    (37.80575833333333,-122.26838055555555)))
  point = Point((ev_lat,ev_lon))
  Poly = point.within(poly)
  return Poly'''

### University Ave
def Check_Poly(ev_lat,ev_lon):
  poly = Polygon(((37.878160,-122.257492), # University Ave
    (37.873646,-122.284185),
    (37.870511,-122.309028),
    (37.863800,-122.305111),
    (37.869214,-122.254670)))
  point = Point((ev_lat,ev_lon))
  Poly = point.within(poly)
  return Poly
  
# Bigger Oakland Area
'''def Check_Poly(ev_lat,ev_lon):
  poly = Polygon(((37.812594,-122.270164),
    (37.822968,-122.267433),
    (37.821722,-122.259872),
    (37.797118,-122.249193),
    (37.787229,-122.263842),
    (37.794675,-122.289563),
    (37.805828,-122.288179),
    (37.802708,-122.278026)))
  point = Point((ev_lat,ev_lon))
  Poly = point.within(poly)
  return Poly'''

def press_corr(ev_press):
  press_I = exp((994.25-ev_press)/168.663)
  return press_I


weather_avail = FindWeather(weatherfile)

if weather_avail:
  # weather data file
  tx = open(weatherfile, 'r')
  #print 'weather file:',weatherfile

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


# define start of GPS data
gps_start_idx = 0
for i in range(0,len(gps_ev)):
  if (gps_ev[i][0].isdigit()):
    #print "start idx:",i
    gps_start_idx = i
    break

angle_bins = 19 #36
min_angle = 0
max_angle = 190 #180

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

r = 35. #m circle radius to search for adjacent buildings
in_r = 7. #m inner radius
R = 6378137. #m earth radius
delta = r/R

# if arc_pts is changed, must change slice coords both above and for kml
arc_pts = 3. # sample pts to make up search "fan"
fan_angle = pi/24. # 7.5 degree fan opening angle
mid_pt = (arc_pts+1)/2

trav_dist = 0
St14th = False
DTOAK = False
POLY = False
'''prev_lat = float(event[0].split(',')[3])
prev_lon = float(event[0].split(',')[4])
prev_bearing_lat = prev_lat
prev_bearing_lon = prev_lon
prev_ev_time = float(event[0].split(',')[2])'''

truck_bearing = 0
prev_truck_bearing = 0

oa_times = []
open_angles = []
CoordAngle = []
SearchPts = []
angle_cts = 0
angle_time = 0

min_distance = 3 #meters for bin spacing based on GPS
dist = 0
first_in_poly = True
edge_found = False
gps_bin_time = 0

n_idx = 0 #start event for neutron data

idx = 0 #for weather finding

for g in range(gps_start_idx,len(gps_ev)):  #(456860,457000): for 04-25 test
  n_ct = 0
  n_corr_ct = 0
  gps_bin_time = 0
  edge_found = False
  # determine if lat, lon is in the search polygon
  gps_ev_time = float(gps_ev[g].split(' ')[0])
  gps_ev_lat = float(gps_ev[g].split(' ')[2])
  gps_ev_lon = float(gps_ev[g].split(' ')[3])
  gps_ev_elev = float(gps_ev[g].split(' ')[4])+28.7

  POLY = Check_Poly(gps_ev_lat,gps_ev_lon)

  if POLY and first_in_poly:
    prev_gps_ev_time = gps_ev_time
    prev_gps_ev_lat = gps_ev_lat
    prev_gps_ev_lon = gps_ev_lon
    prev_gps_ev_elev = gps_ev_elev
    first_in_poly = False

  if POLY and not first_in_poly:
    dist = haversine(prev_gps_ev_lon, prev_gps_ev_lat, gps_ev_lon, gps_ev_lat)
    if dist >= min_distance:
      #print "dist",dist
      edge_found = True

  if edge_found:
    #print "gps idx:",g
    gps_bin_time = gps_ev_time - prev_gps_ev_time
    # neutron counts in bin based on event times:
    for ent in range(n_idx, n_events-1):
      if(ent % (n_events/100) == 0):
        print '%d / %d' % (ent, n_events)
      ev_time = float(event[ent].split(',')[2])
      if prev_gps_ev_time <= ev_time < gps_ev_time:
        n_ct += 1
        if weather_avail:
          for i in range(idx,len(utctime)-1):
            timecut_low = utctime[i] - (utctime[i]-utctime[i-1])/2
            timecut_high = utctime[i] + (utctime[i+1]-utctime[i])/2
            if timecut_low <= ev_time < timecut_high:
              ev_press = bar[i]
              idx = i
        ev_I_rel = float(press_corr(ev_press))
        ev_corr_ct = 1./ev_I_rel
        n_corr_ct += ev_corr_ct
      if ev_time >= gps_ev_time:
        n_idx = ent
        break
    # now we have the bin time and number of counts.. need to find open angle
    # use interpolated bin center as lidar search point
    ev_lat = min(prev_gps_ev_lat,gps_ev_lat)+(max(prev_gps_ev_lat,gps_ev_lat)-min(prev_gps_ev_lat,gps_ev_lat))/2
    ev_lon = max(prev_gps_ev_lon,gps_ev_lon)+(min(prev_gps_ev_lon,gps_ev_lon)-max(prev_gps_ev_lon,gps_ev_lon))/2
    ev_time = gps_ev_time - gps_bin_time/2.
    ev_alt = (prev_gps_ev_elev+gps_ev_elev)/2.
    # truck bearing within bin
    orig_truck_bearing = atan2(cos(prev_gps_ev_lat)*sin(gps_ev_lat)-sin(prev_gps_ev_lat)*cos(gps_ev_lat)*cos(gps_ev_lon - prev_gps_ev_lon),sin(gps_ev_lon - prev_gps_ev_lon)*cos(gps_ev_lat))
    bearing = (degrees(truck_bearing)+360)%360
    #print "truck bearing:",bearing
    #rad_bear = radians(bearing)

    OA_is_180 = True
    OA_iteration = 0
    smallest_OA = 180.

    while OA_is_180:
      OA_iteration += 1
      if OA_iteration == 1:
        truck_bearing = orig_truck_bearing
      if OA_iteration == 2:
        truck_bearing = orig_truck_bearing - pi/4.  # 45 degrees
      if OA_iteration == 3:
        truck_bearing = orig_truck_bearing + pi/4.

      coords_left = []
      coords_right = []

      for i in range(1,int(arc_pts)+1):
          thetaL = truck_bearing + pi/2. + ((mid_pt-i)/(arc_pts-1))*fan_angle # bearing based on sample
          thetaR = thetaL - pi # 180 degree to get other side

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

      #print "Lat/Lon:",ev_lat,ev_lon
      #print "Coords L:",coords_left
      #print "Coords R:",coords_right

      # define lidar search range based on truck lon, then lat
      lon_start = ev_lon + 3.5e-4  # about __ meters from the truck
      lon_stop = ev_lon - 3.5e-4
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

      min_R_angle = pi/2.
      min_R_ang_idx = -1
      min_L_angle = pi/2.
      min_L_ang_idx = -1

      # scan through all points in search area and only keep those that are within 0.03 m alt of another pt
      # hoping to filter out trees
      R_scan_pts = []
      L_scan_pts = []
      scan_ct = 0
      for j in range(0,len(R_pts)):
        srch_pt = R_pts[j][2]
        scan_ct = 0
        for p in range(0,len(R_pts)):
          if p != j and srch_pt-0.015 <= R_pts[p][2] <= srch_pt+0.015:
            #print "search point alt:",srch_pt,j
            #print "other point alt:",R_pts[p][2],p
            scan_ct += 1
            #R_scan_pts.append(R_pts[j])
            #break
          if scan_ct >= 2:
            R_scan_pts.append(R_pts[j])
            break
      
      #print "r pts:",len(R_pts)
      #print "scanned pts:",len(R_scan_pts)
      #print "g:",g

      for j in range(0,len(L_pts)):
        srch_pt = L_pts[j][2]
        scan_ct = 0
        for p in range(0,len(L_pts)):
          if p != j and srch_pt-0.015 <= L_pts[p][2] <= srch_pt+0.015:
            scan_ct += 1
          if scan_ct >= 2:
            L_scan_pts.append(L_pts[j])
            break

      #print "right side scanned pts:",R_scan_pts
      #print "left side scanned pts:",L_scan_pts

      # now find minimum angle point within search area
      for j in range(0,len(R_scan_pts)):
        if R_scan_pts[j][2] >= ev_alt + 1: # only look at points that are at least 1 meter above truck alt
          R_angle = atan((haversine(ev_lon, ev_lat, R_scan_pts[j][1], R_scan_pts[j][0]))/(R_scan_pts[j][2]-ev_alt))
          if R_angle < min_R_angle:
              min_R_angle = R_angle
              min_R_ang_idx = j

      for j in range(0,len(L_scan_pts)):
        if L_scan_pts[j][2] >= ev_alt + 1:
          L_angle = atan((haversine(ev_lon, ev_lat, L_scan_pts[j][1], L_scan_pts[j][0]))/(L_scan_pts[j][2]-ev_alt))
          if L_angle < min_L_angle:
              min_L_angle = L_angle
              min_L_ang_idx = j

      Open_Angle = degrees(min_R_angle+min_L_angle)
      #print "Open Angle:",Open_Angle

      if OA_iteration == 1 and int(Open_Angle) < 180:
        OA_is_180 = False
        smallest_OA = Open_Angle

      if OA_iteration >= 2 and Open_Angle < smallest_OA:
        smallest_OA = Open_Angle

      if OA_iteration == 3:
        OA_is_180 = False

      CoordAngle.append([ev_lat,ev_lon,Open_Angle,ev_alt,bearing])

    ############################################
    # Add in : if open angle = 180 degrees, search fans at bearing +/- 45 degrees

    ############################################
    #print n_ct
    #print gps_bin_time
    #print "n_idx",n_idx
    #CoordAngle.append([ev_lat,ev_lon,smallest_OA,ev_alt,bearing])#CoordAngle.append([ev_lat,ev_lon,Open_Angle,ev_alt,bearing])
    oa_times.append(ev_time)
    open_angles.append(smallest_OA) #open_angles.append(Open_Angle)
    print "Open Angle:",smallest_OA
    # fill hists for this angle bin
    oa1.Fill(smallest_OA,n_ct)#oa1.Fill(Open_Angle,n_ct)
    oa1a.Fill(smallest_OA,n_corr_ct)#oa1a.Fill(Open_Angle,n_corr_ct)
    oa2.Fill(smallest_OA,gps_bin_time)#oa2.Fill(Open_Angle,gps_bin_time)
    # reset
    prev_gps_ev_time = gps_ev_time
    prev_gps_ev_lat = gps_ev_lat
    prev_gps_ev_lon = gps_ev_lon
    prev_gps_ev_elev = gps_ev_elev

  if not POLY:
    first_in_poly = True


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
  '''ct+=1
  if ct == 5:
    plot = True
    ct = 0
  else:
    plot = False'''
  plot = True
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
                            elev=CoordAngle[i][3]+1.5,
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
                        KML.coordinates('{lon1},{lat1},{elev},{lon2},{lat2},{elev},{lon3},{lat3},{elev},{lon4},{lat4},{elev},{lon5},{lat5},{elev},{lon1},{lat1},{elev}'.format(
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
                            #lon6=SearchPts[i][0][11],
                            #lat6=SearchPts[i][0][10],
                            #lon7=SearchPts[i][0][13],
                            #lat7=SearchPts[i][0][12],
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
                        KML.coordinates('{lon1},{lat1},{elev},{lon2},{lat2},{elev},{lon3},{lat3},{elev},{lon4},{lat4},{elev},{lon5},{lat5},{elev},{lon1},{lat1},{elev}'.format(
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
                            #lon6=SearchPts[i][1][11],
                            #lat6=SearchPts[i][1][10],
                            #lon7=SearchPts[i][1][13],
                            #lat7=SearchPts[i][1][12],
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