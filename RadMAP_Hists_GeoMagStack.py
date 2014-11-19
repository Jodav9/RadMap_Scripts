import numpy as np
import ROOT
from ROOT import TH1D, TH2D, TH3D, TGraph, THStack
import tables
import sys
import math
import os
from math import radians, cos, sin, asin, sqrt, exp, ceil
from array import array
from shapely.geometry import Polygon, Point

lidar_path = '/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/Lidar/'

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

# functions for weather data
def unix2utc(ts):
    from datetime import datetime as dt
    d = dt.utcfromtimestamp(ts)
    return d.strftime('%m/%d/%Y %H:%M:%S')

#find range for input variable.. ex: findLims(temp)
def findLims(lis):
    lis = [v for v in lis if v != '---']
    return [min(lis),max(lis)]

###   end functions ###################
#######################################

# Load the time-sorted event text file
infile = open(str(sys.argv[1]), 'r')
event = infile.readlines()

#insert error if number of args is not =4 if(len(sys.argv)!=4):

print 'input file:',sys.argv[1]
print 'output file:',sys.argv[3] 

def FindWeather(weatherfile):
  # find if exists - True / False
  if os.path.isfile(weatherfile):
    weather_avail = True
  else:
    weather_avail = False
  return weather_avail;

def FindLidar(input_file):
  filename = os.path.basename(input_file)
  lidar_file = lidar_path+filename[1:11]+'.txt'
  if os.path.isfile(lidar_file):
    lidar_avail = True
    #lidar_data = open(lidar_file,'r')
  else:
    lidar_avail = False
  return lidar_avail,lidar_file;

lidar_avail = FindLidar(str(sys.argv[1]))[0]
lidar_file = FindLidar(str(sys.argv[1]))[1]
if lidar_avail:
  lidar_data = open(lidar_file,'r')
  print 'lidar file:',lidar_file

weather_avail = FindWeather(str(sys.argv[2]))

if weather_avail:
  # weather data file
  tx = open(str(sys.argv[2]), 'r')
  print 'weather file:',sys.argv[2]

if not weather_avail:
  print '*****************\n','Weather not available for this run\n','*****************'

# find Kp index file
geowea_file = '/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/Geomag/20'+str(sys.argv[2])[-9:-7]
print 'geomagnetic data file:',geowea_file
# open Kp index file
geowea = open(geowea_file,'r')
dateinfo = geowea.readlines()

#Open Fresno station Geomag Data file
geo = open('/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/Geomag/FRN_Data.txt','r')
geoline = geo.readlines()
#Put the data into an array
geodata = []
for i in range (0,len(geoline)):
    geodata.append(geoline[i].split(','))

#create root file and tree
f = ROOT.TFile(str(sys.argv[3]), "recreate")
alt_fol = ROOT.TFolder("Alt_CR_Hists","Alt_CR_Hists")
press_fol = ROOT.TFolder("Press_CR_Hists","Press_CR_Hists")
temp_fol = ROOT.TFolder("Temp_CR_Hists","Temp_CR_Hists")
hum_fol = ROOT.TFolder("Hum_CR_Hists","Hum_CR_Hists")
dew_fol = ROOT.TFolder("DewPt_CR_Hists","DewPt_CR_Hists")
adens_fol = ROOT.TFolder("AirDens_CR_Hists","AirDens_CR_Hists")
Kp_fol = ROOT.TFolder("Kp_CR_Hists","Kp_CR_Hists")
GeoMag_fol = ROOT.TFolder("GeoMag_CR_Hists","GeoMag_CR_Hists")
Lidar_fol = ROOT.TFolder("Lidar_CR_Hists","Lidar_CR_Hists")
TwoD_fol = ROOT.TFolder("2D_Hists","2D_Hists")
OneD_fol = ROOT.TFolder("1D_Graphs","1D_Graphs")
time_fol = ROOT.TFolder("Time_CR_Hists","Time_CR_Hists")
ThreeD_fol = ROOT.TFolder("3D_Hists","3D_Hists")
CR_Freq_fol = ROOT.TFolder("CR_Freq_Plots","CR_Freq_Plots")

start_event = 0
n_events = len(event)
n_bins = 60 #for count rate hists
max_alt = 1500
#alt_buffer = 10 #filter to minimize unreasonable jumps in altitude (10 m)
#alt_min_time = 10
#alt_buffer_ct = 0
#prev_ev_in_buffer = False
min_press = 950.
max_press = 1050.
press_bins = 200
min_temp = 30.
max_temp = 105.
temp_bins = 75 
min_dew = 10.
max_dew = 70.
dew_bins = 120.
min_airdens = 1.130
max_airdens = 1.260
airdens_bins = 130.
min_hum = 0.
max_hum = 30.
hum_bins = 120
min_Kp = 0. 
max_Kp = 9.
Kp_bins = 90
idx=0  #floating index for getweather loop
min_geo = 0.
max_geo = 50.
geo_bins = 50
min_daytime = 0.
max_daytime = 24.
daytime_bins = 48
min_lidar = 0.
max_lidar = 1.0
lidar_bins = 100

min_CR = 0
max_CR = 10
CR_bins = 100 # bin every 0.1 CPS

beg_time = float(event[0].split(',')[2])
last_ev_time = float(event[0].split(',')[2])
prev_alt = float(event[0].split(',')[5])
prev_bin = int(('%.5f' % float((prev_alt/max_alt)*n_bins))[:-6])
beg_lat = float(event[0].split(',')[3])
beg_lon = float(event[0].split(',')[4])

prev_hist_alt = -1

end_time = float(event[n_events-1].split(',')[2])
#print "End Time:",end_time
timeint = 60. # 60 second time interval for time hist
runtime = end_time-beg_time
#print "Run Time:",runtime
time_bins = int(ceil(runtime/timeint)) #set number of time bins for CR hist
#print "Time Bins:",time_bins
end_time = float(beg_time+timeint*time_bins)
#print "New End Time:",end_time
# time_per_bin = (end_time-beg_time)/time_bins
# print 'time per time bin: ', time_per_bin

allhists = []

# alt
h1 = TH1D("alt_events","Neutron Event Altitude",n_bins,0,max_alt);
h1.GetXaxis().SetTitle("Altitude (m)")
h1.GetYaxis().SetTitle("Counts")
h1.Sumw2()
allhists.append(h1)
#
h1a = TH1D("press_corr_alt_events","Neutron Event Altitude",n_bins,0,max_alt);
h1a.GetXaxis().SetTitle("Altitude (m)")
h1a.GetYaxis().SetTitle("Counts")
h1a.Sumw2()
#
h2 = TH1D("alt_time","Neutron Time at Altitude",n_bins,0,max_alt);
h2.GetXaxis().SetTitle("Altitude (m)")
h2.GetYaxis().SetTitle("Time (s)")
allhists.append(h2)
# press
h4 = TH1D("press_events","Neutron Event Pressure",press_bins,min_press,max_press);
h4.GetXaxis().SetTitle("Pressure (mbar)")
h4.GetYaxis().SetTitle("Counts")
h4.Sumw2()
allhists.append(h4)
#
h4a = TH1D("press_corr_press_events","Neutron Event Pressure",press_bins,min_press,max_press);
h4a.GetXaxis().SetTitle("Pressure (mbar)")
h4a.GetYaxis().SetTitle("Counts")
h4a.Sumw2()
#
h5 = TH1D("press_time","Time at Pressure",press_bins,min_press,max_press);
h5.GetXaxis().SetTitle("Pressure (mbar)")
h5.GetYaxis().SetTitle("Time (s)")
allhists.append(h5)
# temp
h7 = TH1D("temp_events","Neutron Event Temperature",temp_bins,min_temp,max_temp);
h7.GetXaxis().SetTitle("Temperature (F)")
h7.GetYaxis().SetTitle("Counts")
h7.Sumw2()
allhists.append(h7)
#
h7a = TH1D("press_corr_temp_events","Neutron Event Temperature",temp_bins,min_temp,max_temp);
h7a.GetXaxis().SetTitle("Temperature (F)")
h7a.GetYaxis().SetTitle("Counts")
h7a.Sumw2()
#
h8 = TH1D("temp_time","Time at Temperature",temp_bins,min_temp,max_temp);
h8.GetXaxis().SetTitle("Temperature (F)")
h8.GetYaxis().SetTitle("Time (s)")
allhists.append(h8)
# humidity
h10 = TH1D("hum_events","Neutron Event Humidity",hum_bins,min_hum,max_hum);
h10.GetXaxis().SetTitle("Absolute Humidity (g/m^3)")
h10.GetYaxis().SetTitle("Counts")
h10.Sumw2()
allhists.append(h10)
#
h10a = TH1D("press_corr_hum_events","Neutron Event Humidity",hum_bins,min_hum,max_hum);
h10a.GetXaxis().SetTitle("Absolute Humidity (g/m^3)")
h10a.GetYaxis().SetTitle("Counts")
h10a.Sumw2()
#
h11 = TH1D("hum_time","Time at Humidity",hum_bins,min_hum,max_hum);
h11.GetXaxis().SetTitle("Absolute Humidity (g/m^3)")
h11.GetYaxis().SetTitle("Time (s)")
allhists.append(h11)
# dew point
h17 = TH1D("dew_events","Neutron Event Dew Point",int(dew_bins),min_dew,max_dew);
h17.GetXaxis().SetTitle("Dew Point (F)")
h17.GetYaxis().SetTitle("Counts")
h17.Sumw2()
allhists.append(h17)
#
h17a = TH1D("press_corr_dew_events","Neutron Event Dew Point",int(dew_bins),min_dew,max_dew);
h17a.GetXaxis().SetTitle("Dew Point (F)")
h17a.GetYaxis().SetTitle("Counts")
h17a.Sumw2()
#
h18 = TH1D("dew_time","Time at Dew Point",int(dew_bins),min_dew,max_dew);
h18.GetXaxis().SetTitle("Dew Point (F)")
h18.GetYaxis().SetTitle("Time (s)")
allhists.append(h18)
# air density
h20 = TH1D("airdens_events","Neutron Event Air Density",int(airdens_bins),min_airdens,max_airdens);
h20.GetXaxis().SetTitle("Inside Air Density (kg/m^3)")
h20.GetYaxis().SetTitle("Counts")
h20.Sumw2()
allhists.append(h20)
#
h20a = TH1D("press_corr_airdens_events","Neutron Event Air Density",int(airdens_bins),min_airdens,max_airdens);
h20a.GetXaxis().SetTitle("Inside Air Density (kg/m^3)")
h20a.GetYaxis().SetTitle("Counts")
h20a.Sumw2()
#
h21 = TH1D("airdens_time","Time at Air Density",int(airdens_bins),min_airdens,max_airdens);
h21.GetXaxis().SetTitle("Inside Air Density (kg/m^3)")
h21.GetYaxis().SetTitle("Time (s)")
allhists.append(h21)
# Kp value
h23 = TH1D("Kp_events","Neutron Event Kp Value",Kp_bins,min_Kp,max_Kp);
h23.GetXaxis().SetTitle("Kp Value")
h23.GetYaxis().SetTitle("Counts")
h23.Sumw2()
allhists.append(h23)
#
h23a = TH1D("press_corr_Kp_events","Neutron Event Kp Value",Kp_bins,min_Kp,max_Kp);
h23a.GetXaxis().SetTitle("Kp Value")
h23a.GetYaxis().SetTitle("Counts")
h23a.Sumw2()
#
h24 = TH1D("Kp_time","Time at Kp Value",Kp_bins,min_Kp,max_Kp);
h24.GetXaxis().SetTitle("Kp Value")
h24.GetYaxis().SetTitle("Time (s)")
allhists.append(h24)
# time
h13 = TH1D("time_events","Neutron Events",time_bins,beg_time,end_time);
h13.GetXaxis().SetTitle("Epoch Time (s)")
h13.GetYaxis().SetTitle("Counts")
h13.Sumw2()
allhists.append(h13)
#
h13a = TH1D("press_corr_time_events","Neutron Events",time_bins,beg_time,end_time);
h13a.GetXaxis().SetTitle("Epoch Time (s)")
h13a.GetYaxis().SetTitle("Counts")
h13a.Sumw2()
#
# count rate distribution
h15 = TH1D("CR","Neutron Count Rate Distribution",CR_bins,min_CR,max_CR);
h15.GetXaxis().SetTitle("Count Rate (CPS)")
h15.GetYaxis().SetTitle("Frequency")
#
h15a = TH1D("corr_CR","Neutron Count Rate Distribution",CR_bins,min_CR,max_CR);
h15a.GetXaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
h15a.GetYaxis().SetTitle("Frequency")
# count distribution (per timeint 60 sec)
ct_bins = int((max_CR - min_CR)*timeint)
min_ct = min_CR*timeint
max_ct = max_CR*timeint
h16 = TH1D("ct_freq","Neutron Counts per 60 sec",ct_bins,min_ct,max_ct);
h16.GetXaxis().SetTitle("Counts per 60 sec")
h16.GetYaxis().SetTitle("Frequency")

# Fresno Geomagnetic Data
h26 = TH1D("Geomag_events","Neutron Events Given Hourly Geomagnetic Field Strength Change",geo_bins,min_geo,max_geo);
h26.GetXaxis().SetTitle("Hourly Change (nT)")
h26.GetYaxis().SetTitle("Counts")
h26.Sumw2()
#
h26a = TH1D("press_corr_Geomag_events","Neutron Events Given Hourly Geomagnetic Field Strength Change",geo_bins,min_geo,max_geo);
h26a.GetXaxis().SetTitle("Hourly Change (nT)")
h26a.GetYaxis().SetTitle("Counts")
h26a.Sumw2()
#
h27 = TH1D("Geomag_time","Time at Geomagnetic Field Strength Change Value",geo_bins,min_geo,max_geo);
h27.GetXaxis().SetTitle("Hourly Change (nT)")
h27.GetYaxis().SetTitle("Time (s)")
# time of day
h29 = TH1D("daytime_events","Neutron Events Time of Day",daytime_bins,min_daytime,max_daytime);
h29.GetXaxis().SetTitle("Time of Day (hr)")
h29.GetYaxis().SetTitle("Counts")
h29.Sumw2()
#
h30 = TH1D("daytime_time","Neutron Events Time of Day",daytime_bins,min_daytime,max_daytime);
h30.GetXaxis().SetTitle("Time of Day (hr)")
h30.GetYaxis().SetTitle("Time (s)")
# outside air density
h32 = TH1D("outdens_events","Neutron Event Air Density",int(airdens_bins),min_airdens,max_airdens);
h32.GetXaxis().SetTitle("Outside Air Density (kg/m^3)")
h32.GetYaxis().SetTitle("Counts")
h32.Sumw2()
#
h32a = TH1D("press_corr_outdens_events","Neutron Event Air Density",int(airdens_bins),min_airdens,max_airdens);
h32a.GetXaxis().SetTitle("Outside Air Density (kg/m^3)")
h32a.GetYaxis().SetTitle("Counts")
h32a.Sumw2()
#
h33 = TH1D("outdens_time","Time at Air Density",int(airdens_bins),min_airdens,max_airdens);
h33.GetXaxis().SetTitle("Outside Air Density (kg/m^3)")
h33.GetYaxis().SetTitle("Time (s)")
# Lidar data
h35 = TH1D("lidar_events","Neutron Events Given Lidar Return Fraction of Solid Angle",lidar_bins,min_lidar,max_lidar);
h35.GetXaxis().SetTitle("Fraction of Returns")
h35.GetYaxis().SetTitle("Counts")
h35.Sumw2()
#
h35a = TH1D("press_corr_lidar_events","Neutron Events Given Lidar Return Fraction of Solid Angle",lidar_bins,min_lidar,max_lidar);
h35a.GetXaxis().SetTitle("Fraction of Returns")
h35a.GetYaxis().SetTitle("Counts")
h35a.Sumw2()
#
h36 = TH1D("lidar_time","Time at Lidar Return Fraction of Solid Angle",lidar_bins,min_lidar,max_lidar);
h36.GetXaxis().SetTitle("Fraction of Returns")
h36.GetYaxis().SetTitle("Time (s)")
####
# DT Oakland count rate distribution
h90 = TH1D("DT_Oak_CR","Neutron Count Rate Distribution in Downtown Oakland",CR_bins,min_CR,max_CR);
h90.GetXaxis().SetTitle("Count Rate (CPS)")
h90.GetYaxis().SetTitle("Frequency")
#
h90a = TH1D("DT_Oak_corr_CR","Neutron Count Rate Distribution in Downtown Oakland",CR_bins,min_CR,max_CR);
h90a.GetXaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
h90a.GetYaxis().SetTitle("Frequency")
# Berkeley count rate distribution
h91 = TH1D("Berk_CR","Neutron Count Rate Distribution in Berkeley",CR_bins,min_CR,max_CR);
h91.GetXaxis().SetTitle("Count Rate (CPS)")
h91.GetYaxis().SetTitle("Frequency")
#
h91a = TH1D("Berk_corr_CR","Neutron Count Rate Distribution in Berkeley",CR_bins,min_CR,max_CR);
h91a.GetXaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
h91a.GetYaxis().SetTitle("Frequency")
# Bridge count rate distribution
h92 = TH1D("Bridge_CR","Neutron Count Rate Distribution over Bridges",CR_bins,min_CR,max_CR);
h92.GetXaxis().SetTitle("Count Rate (CPS)")
h92.GetYaxis().SetTitle("Frequency")
#
h92a = TH1D("Bridge_corr_CR","Neutron Count Rate Distribution over Bridges",CR_bins,min_CR,max_CR);
h92a.GetXaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
h92a.GetYaxis().SetTitle("Frequency")
# Farm Land count rate distribution
h93 = TH1D("Farm_CR","Neutron Count Rate Distribution in Farmland",CR_bins,min_CR,max_CR);
h93.GetXaxis().SetTitle("Count Rate (CPS)")
h93.GetYaxis().SetTitle("Frequency")
#
h93a = TH1D("Farm_corr_CR","Neutron Count Rate Distribution in Farmland",CR_bins,min_CR,max_CR);
h93a.GetXaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
h93a.GetYaxis().SetTitle("Frequency")
# Highway count rate distribution
h94 = TH1D("Hwy_CR","Neutron Count Rate Distribution on Highway",CR_bins,min_CR,max_CR);
h94.GetXaxis().SetTitle("Count Rate (CPS)")
h94.GetYaxis().SetTitle("Frequency")
#
h94a = TH1D("Hwy_corr_CR","Neutron Count Rate Distribution on Highway",CR_bins,min_CR,max_CR);
h94a.GetXaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
h94a.GetYaxis().SetTitle("Frequency")

############
# 2D
############
# Alt v. Pressure v. CR
h1_2d = TH2D("alt_press_events","Neutron Event Altitude and Pressure",n_bins,0,max_alt,press_bins,min_press,max_press);
h1_2d.GetXaxis().SetTitle("Altitude (m)")
h1_2d.GetYaxis().SetTitle("Pressure (mbar)")
h1_2d.GetZaxis().SetTitle("Counts")
h1_2d.Sumw2()
#
h2_2d = TH2D("alt_press_time","Neutron Time at Altitude and Pressure",n_bins,0,max_alt,press_bins,min_press,max_press);
h2_2d.GetXaxis().SetTitle("Altitude (m)")
h2_2d.GetYaxis().SetTitle("Pressure (mbar)")
h2_2d.GetZaxis().SetTitle("Time (s)")
# Alt v. Temp v. CR
h4_2d = TH2D("alt_temp_events","Neutron Event Altitude and Temperature",n_bins,0,max_alt,temp_bins,min_temp,max_temp);
h4_2d.GetXaxis().SetTitle("Altitude (m)")
h4_2d.GetYaxis().SetTitle("Temperature (F)")
h4_2d.GetZaxis().SetTitle("Counts")
h4_2d.Sumw2()
#
h5_2d = TH2D("alt_temp_time","Neutron Time at Altitude and Temperature",n_bins,0,max_alt,temp_bins,min_temp,max_temp);
h5_2d.GetXaxis().SetTitle("Altitude (m)")
h5_2d.GetYaxis().SetTitle("Temperature (F)")
h5_2d.GetZaxis().SetTitle("Time (s)")
# Alt v. Hum v. CR
h7_2d = TH2D("alt_hum_events","Neutron Event Altitude and Humidity",n_bins,0,max_alt,hum_bins,min_hum,max_hum);
h7_2d.GetXaxis().SetTitle("Altitude (m)")
h7_2d.GetYaxis().SetTitle("Absolute Humidity (g/m^3)")
h7_2d.GetZaxis().SetTitle("Counts")
h7_2d.Sumw2()
#
h8_2d = TH2D("alt_hum_time","Neutron Time at Altitude and Humidity",n_bins,0,max_alt,hum_bins,min_hum,max_hum);
h8_2d.GetXaxis().SetTitle("Altitude (m)")
h8_2d.GetYaxis().SetTitle("Absolute Humidity (g/m^3)")
h8_2d.GetZaxis().SetTitle("Time (s)")
# Alt v. Dew v. CR
h10_2d = TH2D("alt_dew_events","Neutron Event Altitude and Dew Point",n_bins,0,max_alt,int(dew_bins),min_dew,max_dew);
h10_2d.GetXaxis().SetTitle("Altitude (m)")
h10_2d.GetYaxis().SetTitle("Dew Point (F)")
h10_2d.GetZaxis().SetTitle("Counts")
h10_2d.Sumw2()
#
h11_2d = TH2D("alt_dew_time","Neutron Time at Altitude and Dew Point",n_bins,0,max_alt,int(dew_bins),min_dew,max_dew);
h11_2d.GetXaxis().SetTitle("Altitude (m)")
h11_2d.GetYaxis().SetTitle("Dew Point (F)")
h11_2d.GetZaxis().SetTitle("Time (s)")
# Alt v. Airdens v. CR
h13_2d = TH2D("alt_airdens_events","Neutron Event Altitude and Air Density",n_bins,0,max_alt,int(airdens_bins),min_airdens,max_airdens);
h13_2d.GetXaxis().SetTitle("Altitude (m)")
h13_2d.GetYaxis().SetTitle("Inside Air Density (kg/m^3)")
h13_2d.GetZaxis().SetTitle("Counts")
h13_2d.Sumw2()
#
h14_2d = TH2D("alt_airdens_time","Neutron Time at Altitude and Air Density",n_bins,0,max_alt,int(airdens_bins),min_airdens,max_airdens);
h14_2d.GetXaxis().SetTitle("Altitude (m)")
h14_2d.GetYaxis().SetTitle("Inside Air Density (kg/m^3)")
h14_2d.GetZaxis().SetTitle("Time (s)")
# Alt v. Geomag v. CR
h16_2d = TH2D("alt_geomag_events","Neutron Event Altitude and Geomagnetic Field Strength Change",n_bins,0,max_alt,geo_bins,min_geo,max_geo);
h16_2d.GetXaxis().SetTitle("Altitude (m)")
h16_2d.GetYaxis().SetTitle("Hourly Change (nT)")
h16_2d.GetZaxis().SetTitle("Counts")
h16_2d.Sumw2()
#
h17_2d = TH2D("alt_geomag_time","Neutron Time at Altitude and Geomagnetic Field Strength Change",n_bins,0,max_alt,geo_bins,min_geo,max_geo);
h17_2d.GetXaxis().SetTitle("Altitude (m)")
h17_2d.GetYaxis().SetTitle("Hourly Change (nT)")
h17_2d.GetZaxis().SetTitle("Time (s)")
# Press v. out_Airdesn v. CR
h19_2d = TH2D("press_outdens_events","Neutron Event Pressure and Air Density",press_bins,min_press,max_press,int(airdens_bins),min_airdens,max_airdens);
h19_2d.GetXaxis().SetTitle("Pressure (mbar)")
h19_2d.GetYaxis().SetTitle("Outside Air Density (kg/m^3)")
h19_2d.GetZaxis().SetTitle("Counts")
h19_2d.Sumw2()
#
h20_2d = TH2D("press_outdens_time","Neutron Time at Pressure and Air Density",press_bins,min_press,max_press,int(airdens_bins),min_airdens,max_airdens);
h20_2d.GetXaxis().SetTitle("Pressure (mbar)")
h20_2d.GetYaxis().SetTitle("Outside Air Density (kg/m^3)")
h20_2d.GetZaxis().SetTitle("Time (s)")
# Alt v. out_airdens v. CR
h22_2d = TH2D("alt_outdens_events","Neutron Event Altitude and Air Density",n_bins,0,max_alt,int(airdens_bins),min_airdens,max_airdens);
h22_2d.GetXaxis().SetTitle("Altitude (m)")
h22_2d.GetYaxis().SetTitle("Outside Air Density (kg/m^3)")
h22_2d.GetZaxis().SetTitle("Counts")
h22_2d.Sumw2()
#
h23_2d = TH2D("alt_outdens_time","Neutron Time at Altitude and Air Density",n_bins,0,max_alt,int(airdens_bins),min_airdens,max_airdens);
h23_2d.GetXaxis().SetTitle("Altitude (m)")
h23_2d.GetYaxis().SetTitle("Outside Air Density (kg/m^3)")
h23_2d.GetZaxis().SetTitle("Time (s)")
# Out v. in_airdens v. CR
h25_2d = TH2D("outdens_airdens_events","Neutron Event at Inside and Outside Air Density",int(airdens_bins),min_airdens,max_airdens,int(airdens_bins),min_airdens,max_airdens);
h25_2d.GetXaxis().SetTitle("Outside Air Density (kg/m^3)")
h25_2d.GetYaxis().SetTitle("Inside Air Density (kg/m^3)")
h25_2d.GetZaxis().SetTitle("Counts")
h25_2d.Sumw2()
#
h26_2d = TH2D("outdens_airdens_time","Neutron Time at Inside and Outside Air Density",int(airdens_bins),min_airdens,max_airdens,int(airdens_bins),min_airdens,max_airdens);
h26_2d.GetXaxis().SetTitle("Outside Air Density (kg/m^3)")
h26_2d.GetYaxis().SetTitle("Inside Air Density (kg/m^3)")
h26_2d.GetZaxis().SetTitle("Time (s)")
# Time of Day v. Geomag v. CR
h28_2d = TH2D("time_geomag_events","Neutron Event Time of Day and Geomagnetic Field Strength Change",daytime_bins,min_daytime,max_daytime,geo_bins,min_geo,max_geo);
h28_2d.GetXaxis().SetTitle("Time of Day (hr)")
h28_2d.GetYaxis().SetTitle("Hourly Change (nT)")
h28_2d.GetZaxis().SetTitle("Counts")
h28_2d.Sumw2()
#
h29_2d = TH2D("time_geomag_time","Neutron Time at Time of Day and Geomagnetic Field Strength Change",daytime_bins,min_daytime,max_daytime,geo_bins,min_geo,max_geo);
h29_2d.GetXaxis().SetTitle("Time of Day (hr)")
h29_2d.GetYaxis().SetTitle("Hourly Change (nT)")
h29_2d.GetZaxis().SetTitle("Time (s)")
# Press v. Hum v. CR
h31_2d = TH2D("press_hum_events","Neutron Event Pressure and Humidity",press_bins,min_press,max_press,hum_bins,min_hum,max_hum);
h31_2d.GetXaxis().SetTitle("Pressure (mbar)")
h31_2d.GetYaxis().SetTitle("Absolute Humidity (g/m^3)")
h31_2d.GetZaxis().SetTitle("Counts")
h31_2d.Sumw2()
#
h32_2d = TH2D("press_hum_time","Neutron Time at Pressure and Humidity",press_bins,min_press,max_press,hum_bins,min_hum,max_hum);
h32_2d.GetXaxis().SetTitle("Pressure (mbar)")
h32_2d.GetYaxis().SetTitle("Absolute Humidity (g/m^3)")
h32_2d.GetZaxis().SetTitle("Time (s)")
###
# CR environmental density plots
'''# Alt v. CR Freq
h34_2d = TH2D("alt_CR_freq","Altitude Count Rate Frequency",n_bins,0,max_alt,CR_bins,min_CR,max_CR);
h34_2d.GetXaxis().SetTitle("Altitude (m)")
h34_2d.GetYaxis().SetTitle("Count Rate (CPS)")
h34_2d.GetZaxis().SetTitle("Frequency")
# adjusted
h34a_2d = TH2D("adj_alt_CR_freq","Adjusted Altitude Count Rate Frequency",n_bins,0,max_alt,CR_bins,min_CR,max_CR);
h34a_2d.GetXaxis().SetTitle("Altitude (m)")
h34a_2d.GetYaxis().SetTitle("Adjusted Count Rate (CPS)")
h34a_2d.GetZaxis().SetTitle("Frequency") '''
# Press v. CR Freq
h35_2d = TH2D("press_CR_freq","Pressure Count Rate Frequency",press_bins,min_press,max_press,CR_bins,min_CR,max_CR);
h35_2d.GetXaxis().SetTitle("Pressure (mbar)")
h35_2d.GetXaxis().SetTitleOffset(1.5)
h35_2d.GetYaxis().SetTitle("Count Rate (CPS)")
h35_2d.GetYaxis().SetTitleOffset(1.5)
h35_2d.GetZaxis().SetTitle("Frequency")
h35_2d.GetZaxis().SetTitleOffset(1.25)
# adjusted
h35a_2d = TH2D("adj_press_CR_freq","Adjusted Pressure Count Rate Frequency",press_bins,min_press,max_press,CR_bins,min_CR,max_CR);
h35a_2d.GetXaxis().SetTitle("Pressure (mbar)")
h35a_2d.GetYaxis().SetTitle("Adjusted Count Rate (CPS)")
h35a_2d.GetZaxis().SetTitle("Frequency")
# Temp v. CR Freq
h36_2d = TH2D("temp_CR_freq","Temperature Count Rate Frequency",temp_bins,min_temp,max_temp,CR_bins,min_CR,max_CR);
h36_2d.GetXaxis().SetTitle("Temperature (F)")
h36_2d.GetYaxis().SetTitle("Count Rate (CPS)")
h36_2d.GetZaxis().SetTitle("Frequency")
# adjusted
h36a_2d = TH2D("adj_temp_CR_freq","Adjusted Temperature Count Rate Frequency",temp_bins,min_temp,max_temp,CR_bins,min_CR,max_CR);
h36a_2d.GetXaxis().SetTitle("Temperature (F)")
h36a_2d.GetYaxis().SetTitle("Adjusted Count Rate (CPS)")
h36a_2d.GetZaxis().SetTitle("Frequency")
# Hum v. CR Freq
h37_2d = TH2D("hum_CR_freq","Humidity Count Rate Frequency",hum_bins,min_hum,max_hum,CR_bins,min_CR,max_CR);
h37_2d.GetXaxis().SetTitle("Absolute Humidity (g/m^3)")
h37_2d.GetYaxis().SetTitle("Count Rate (CPS)")
h37_2d.GetZaxis().SetTitle("Frequency")
# adjusted
h37a_2d = TH2D("adj_hum_CR_freq","Adjusted Humidity Count Rate Frequency",hum_bins,min_hum,max_hum,CR_bins,min_CR,max_CR);
h37a_2d.GetXaxis().SetTitle("Absolute Humidity (g/m^3)")
h37a_2d.GetYaxis().SetTitle("Adjusted Count Rate (CPS)")
h37a_2d.GetZaxis().SetTitle("Frequency")
# Kp value v. CR Freq
h38_2d = TH2D("kp_CR_freq","Kp Value Count Rate Frequency",Kp_bins,min_Kp,max_Kp,CR_bins,min_CR,max_CR);
h38_2d.GetXaxis().SetTitle("Kp Value")
h38_2d.GetYaxis().SetTitle("Count Rate (CPS)")
h38_2d.GetZaxis().SetTitle("Frequency")
# adjusted
h38a_2d = TH2D("adj_kp_CR_freq","Adjusted Kp Value Count Rate Frequency",Kp_bins,min_Kp,max_Kp,CR_bins,min_CR,max_CR);
h38a_2d.GetXaxis().SetTitle("Kp Value")
h38a_2d.GetYaxis().SetTitle("Adjusted Count Rate (CPS)")
h38a_2d.GetZaxis().SetTitle("Frequency")

# 3D
# Alt v. Press v. Hum v. CR
h1_3d = TH3D("alt_press_hum_events","Neutron Event Altitude, Pressure and Humidity",n_bins,0,max_alt,press_bins,min_press,max_press,hum_bins,min_hum,max_hum);
h1_3d.GetXaxis().SetTitle("Altitude (m)")
h1_3d.GetYaxis().SetTitle("Pressure (mbar)")
h1_3d.GetZaxis().SetTitle("Absolute Humidity (g/m^3)")
#h1_3d.Sumw2()
#
h2_3d = TH3D("alt_press_hum_time","Neutron Time at Altitude, Pressure and Humidity",n_bins,0,max_alt,press_bins,min_press,max_press,hum_bins,min_hum,max_hum);
h2_3d.GetXaxis().SetTitle("Altitude (m)")
h2_3d.GetYaxis().SetTitle("Pressure (mbar)")
h2_3d.GetZaxis().SetTitle("Absolute Humidity (g/m^3)")

# stacked hist
kpstack = THStack("kp_stack","Stacked Kp and Count Rate")
# Geomag time hist
h13G = TH1D("kp_timeline","Kp Events",time_bins,beg_time,end_time);
h13G.GetXaxis().SetTitle("Epoch Time (s)")
h13G.GetYaxis().SetTitle("Kp Index")
#h23 = TH1D("Kp_events","Neutron Event Kp Value",Kp_bins,min_Kp,max_Kp);
#h23.GetXaxis().SetTitle("Kp Value")
#h23.GetYaxis().SetTitle("Counts")

dethistalt, dethistpress, dethisttemp, dethisthum, dethisttime = ([] for i in range(5))
# create detector hists
for i in range(0,16):
  dethistalt.append('alt_ch_'+str(i))
  dethistalt[i] = TH1D(dethistalt[i],"Counts at Altitude",n_bins,0,max_alt);
  dethistalt[i].Sumw2()
  dethistpress.append('press_ch_'+str(i))
  dethistpress[i] = TH1D(dethistpress[i],"Count Rate at Pressure",press_bins,min_press,max_press);
  dethistpress[i].Sumw2()
  dethisttemp.append('temp_ch_'+str(i))
  dethisttemp[i] = TH1D(dethisttemp[i],"Count Rate at Temperature",temp_bins,min_temp,max_temp);
  dethisttemp[i].Sumw2()
  dethisthum.append('hum_ch_'+str(i))
  dethisthum[i] = TH1D(dethisthum[i],"Count Rate at Humidity",hum_bins,min_hum,max_hum);
  dethisthum[i].Sumw2()
  dethisttime.append('time_ch_'+str(i))
  dethisttime[i] = TH1D(dethisttime[i],"Neutron Count Rate",time_bins,beg_time,end_time);
  dethisttime[i].Sumw2()

# define pfotzer correction function given alt
def pfotzer_corr(ev_alt):
  # convert alt to feet
  alt_ft = ev_alt*3.28084
  # value for 'A' factor based on alt (converts terrestrial altitude to atmos pressure)
  A_val = 1033. - 0.03648*alt_ft + 0.000000426*(alt_ft**2)
  # find relative (to sea level) intensity  148 is typical n absorbtion length (g/cm^2)
  I_rel = exp((1033.-A_val)/148.)
  # then divide by I_rel to get the 'corrected' counts per one count at higher altitude
  return I_rel

def press_corr(ev_press):
  press_I = exp((994-ev_press)/182.181)
  return press_I

# http://en.wikipedia.org/wiki/Density_of_air
# calculate outside air density
def GetDens(ev_press,ev_temp,ev_hum):
    Temp_K = (5./9.)*(ev_temp-32.)+273.15
    Temp_C = (5./9.)*(ev_temp-32.)
    # saturation vapor pressure in mbar
    p_sat = 6.1078*(10**((7.5*Temp_C)/(237.3+Temp_C)))
    # saturation vapor pressure in mm Hg
    #p_sat = 0.750061683*(6.1078*(10**((7.5*Temp_C)/(237.3+Temp_C))))
    # vapor pressure of water
    p_v = (ev_hum/100.)*p_sat
    # partial pressure of dry air
    p_d = ev_press - p_v
    # outside air density
    out_dens = (p_d*100.*0.028964+p_v*100*0.018016)/(8.314*Temp_K)
    #out_dens = 1.2929*(273.15/Temp_K)*((0.750061683*ev_press-(p_sat*(ev_hum/100.)))/760.)
    return float('%.3f' % out_dens)

# Absolute humidity calc from The Effect of Atmospheric Water Vapor on Neutron Count 
# in the Cosmic-Ray Soil Moisture Observing System paper
def AbsHum(ev_temp,ev_hum):
    Temp_K = (5./9.)*(ev_temp-32.)+273.15
    Temp_C = (5./9.)*(ev_temp-32.)
    #vp at saturation in Pa
    p_sat = 100*(6.112*exp((17.67*Temp_C)/(243.5+Temp_C)))
    #actual water vapor pressure
    p_v = (ev_hum/100.)*p_sat
    #abs hum
    R_v = 461.5 #J(K^-1)(kg^-1) gas constant for water vapor
    hum_abs = 1000*p_v/(R_v*Temp_K) # in g/m^3
    return hum_abs

# find global Kp index for given time 
def findKp(epochtime,idx):
  stmp = unix2utc(epochtime)
  stmp_day = stmp[3:5]
  stmp_mo = stmp[0:2]
  stmp_yr = stmp[8:10]
  stmp_hr = int(stmp[11:13])
  for i in range(idx, len(dateinfo)):
    day = dateinfo[i][4:6]
    mo = dateinfo[i][2:4]
    year = dateinfo[i][0:2]
    if(stmp_yr == year and stmp_mo == mo and stmp_day == day):
      idx=i
      if stmp_hr in (0,1,2):
        Kpval = int(dateinfo[i][12:14])
      if stmp_hr in (3,4,5):
        Kpval = int(dateinfo[i][14:16])
      if stmp_hr in (6,7,8):
        Kpval = int(dateinfo[i][16:18])
      if stmp_hr in (9,10,11):
        Kpval = int(dateinfo[i][18:20])
      if stmp_hr in (12,13,14):
        Kpval = int(dateinfo[i][20:22])
      if stmp_hr in (15,16,17):
        Kpval = int(dateinfo[i][22:24])
      if stmp_hr in (18,19,20):
        Kpval = int(dateinfo[i][24:26])
      if stmp_hr in (21,22,23):
        Kpval = int(dateinfo[i][26:28])
      break
  geomag_data = True
  try: 
    Kpval
  except NameError:
    print '*************************\n','Geomag data not available\n','*************************'
    print 'First event without data:\n','epoch time: ',ev_time
    print 'UTC time: ',unix2utc(ev_time)
    print '*****************************'
    Kpval = -1
    geomag_data = False
  if geomag_data:
    if Kpval < 10:
      if Kpval == 0:
        Kpval = 0.0
      if Kpval == 3:
        Kpval = float(1./3.)
      if Kpval == 7:
        Kpval = float(2./3.)
    if Kpval >= 10:
      if str(Kpval)[1] == '0':
        Kpval = float(str(Kpval)[0])+0.0
      if str(Kpval)[1] == '3':
        Kpval = float(str(Kpval)[0])+float(1./3.)
      if str(Kpval)[1] == '7':
        Kpval = float(str(Kpval)[0])+float(2./3.)
  return Kpval,idx,geomag_data

# Find Fresno Geomag Field stregth value
def findMagRange(epochtime):
  stmp = unix2utc(epochtime)
  stmp_day = stmp[3:5]
  stmp_mo = stmp[0:2]
  stmp_yr = stmp[8:10]
  stmp_hr = int(stmp[11:13])
  for i in range(0, len(geodata)):
    day = geodata[i][0][3:5]
    mo = geodata[i][0][0:2]
    year = geodata[i][0][6:8]
    if(stmp_yr == year and stmp_mo == mo and stmp_day == day):
      MagRange = int(geodata[i][stmp_hr+1])
      break
  FRN_data = True
  try: 
    MagRange
  except NameError:
    print '*************************\n','FRN mag data not available\n','*************************'
    print 'First event without data:\n','epoch time: ',ev_time
    print 'UTC time: ',unix2utc(ev_time)
    print '*****************************'
    MagRange = -1
    FRN_data = False
  return MagRange,FRN_data

#find lidar percent of returns if available
lidar_time, lidar = ([] for i in range(2))

if lidar_avail:
  # read in data and fill arrays
  for line in lidar_data:
    if line[0].isdigit():
      data = line.split(',')
      lidar_time.append(float(data[1])) 
      lidar.append(float(data[0]))

def getLidar(ev_time,idx):
  for i in range(idx,len(lidar_time)-1):
    if lidar_time[i] <= ev_time < lidar_time[i+1]:
      ev_lidar = lidar[i]
      idx = i
  if ev_time > lidar_time[len(lidar_time)-1]:
    ev_lidar = 2
  return ev_lidar,idx

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

def Check_BERK(ev_lat,ev_lon):
  berk_poly = Polygon(((37.87840277777778,-122.2578861111111),
    (37.876536111111115,-122.27195555555555),
    (37.87269444444445,-122.27146388888889),
    (37.86830277777778,-122.30132499999999),
    (37.86521944444445,-122.30034444444445),
    (37.870044444444446,-122.270775),
    (37.86365,-122.27028888888889),
    (37.866455555555554,-122.2480361111111)))
  point = Point((ev_lat,ev_lon))
  Berk = point.within(berk_poly)
  return Berk

def Check_Bridge(ev_lat,ev_lon):
  bridge_poly_1 = Polygon(((37.823275,-122.3309),
    (37.813944444444445,-122.32989722222221),
    (37.80500833333333,-122.35002499999999),
    (37.81880277777778,-122.36171388888889)))
  bridge_poly_2 = Polygon(((37.80880277777778,-122.37189722222222),
    (37.80192222222222,-122.35617777777777),
    (37.78536944444444,-122.38553611111112),
    (37.79223611111111,-122.38877222222223)))
  bridge_poly_3 = Polygon(((37.511402777777775,-122.11199722222221),
    (37.50955833333333,-122.11009722222222),
    (37.497816666666665,-122.12608333333333),
    (37.50066944444445,-122.12975555555555)))
  point = Point((ev_lat,ev_lon))
  B1 = point.within(bridge_poly_1)
  B2 = point.within(bridge_poly_2)
  B3 = point.within(bridge_poly_3)
  if B1 or B2 or B3:
    Bridge = True
  else:
    Bridge = False
  return Bridge

def Check_Farm(ev_lat,ev_lon):
  farm_poly = Polygon(((37.89499444444444,-121.69225555555556),
    (38.05250833333333,-121.53752777777778),
    (37.92816944444444,-121.32739166666666),
    (37.788511111111106,-121.31533888888889),
    (37.768175,-121.51590833333333)))
  point = Point((ev_lat,ev_lon))
  Farm = point.within(farm_poly)
  return Farm

def Check_Hwy(ev_lat,ev_lon):
  hwy_poly = Polygon(((37.82886666666667,-122.29152777777777),
    (37.890475,-122.3072),
    (37.91704722222222,-122.3262),
    (7.91491388888889,-122.32958888888888),
    (37.889625,-122.31080555555555),
    (37.82809166666667,-122.29750277777778),
    (37.823433333333334,-122.29336944444444),
    (37.80909166666667,-122.30776666666667),
    (37.80135555555555,-122.30159444444445),
    (37.80119166666666,-122.28403333333333),
    (37.80245277777777,-122.28343888888888),
    (37.80349722222222,-122.29020555555556),
    (37.803124999999994,-122.29926944444445),
    (37.80860833333333,-122.3036361111111),
    (37.819047222222224,-122.29358611111111),
    (37.82550555555556,-122.28971666666666)))
  point = Point((ev_lat,ev_lon))
  Hwy = point.within(hwy_poly)
  return Hwy

#################################
#################################

# set variables for weather data
utctime, temp, hum, bar, dew, dens, val = ([] for i in range(7))

if weather_avail:
  # read in temp data and fill arrays
  for line in tx:
    if line[0].isdigit():
      data = line.split(',')
      utctime.append(float(data[0])) 
      temp.append(float(data[3])) 
      hum.append(float(data[6]))
      bar.append(float(data[18]))
      dew.append(float(data[7]))
      dens.append(float(data[28]))

# find weather data for given event time
def getWeather(ev_time,idx):
  ev_temp, ev_hum, ev_press, ev_dew, ev_dens = (-1 for i in range(5))
  for i in range(idx,len(utctime)-1):
    timecut_low = utctime[i] - (utctime[i]-utctime[i-1])/2
    timecut_high = utctime[i] + (utctime[i+1]-utctime[i])/2
    if timecut_low <= ev_time < timecut_high:
      ev_temp = temp[i]
      ev_hum = AbsHum(temp[i],hum[i])
      ev_press = bar[i]
      ev_dew = dew[i]
      ev_dens = dens[i]
      ev_rel_hum = hum[i]
      idx = i
  return [ev_temp, ev_hum, ev_press, ev_dew, ev_dens, ev_rel_hum],idx
# find weather for first event if available
ev_time = float(event[0].split(',')[2])

if (weather_avail and utctime[len(utctime)-1] <= ev_time):
  weather_avail = False
  print '*****************\n','Weather not available for this run\n','*****************'

# check to see if weather was available for given data set time range
if weather_avail:
  try:
    ev_weather = getWeather(ev_time,0)
  except NameError:
    print '*****************\n','Weather not available for this run\n','*****************'
    weather_avail = False

if weather_avail:
#  for i in range(0,len(utctime)-1):
#      if utctime[i] <= ev_time < utctime[i+1]:
#        prev_temp = temp[i]
#        prev_hum = AbsHum(temp[i],hum[i])
#        prev_press = bar[i]
#        prev_dew = dew[i]
#        prev_dens = dens[i]
#        idx = i'''
  # first event weather
  ev_weather = getWeather(ev_time,0)
  prev_temp = ev_weather[0][0]
  prev_hum = ev_weather[0][1]
  prev_press = ev_weather[0][2]
  prev_dew = ev_weather[0][3]
  prev_dens = ev_weather[0][4]
  prev_rel_hum = ev_weather[0][5]
  idx = ev_weather[1]

if weather_avail: # if there is still weather data... continue
  prev_outdens = GetDens(prev_press,prev_temp,prev_rel_hum)
  prev_press_bin = int(('%.5f' % float(((prev_press-min_press)/(max_press-min_press))*press_bins))[:-6])
  prev_temp_bin = int(('%.5f' % float(((prev_temp-min_temp)/(max_temp-min_temp))*temp_bins))[:-6])
  prev_hum_bin = int(('%.5f' % float(((prev_hum-min_hum)/(max_hum-min_hum))*hum_bins))[:-6])
  prev_dew_bin = int(('%.5f' % float(((prev_dew-min_dew)/(max_dew-min_dew))*dew_bins))[:-6])
  prev_dens_bin = int(('%.5f' % float(((prev_dens-min_airdens)/(max_airdens-min_airdens))*airdens_bins))[:-6])
  prev_outdens_bin = int(('%.5f' % float(((prev_outdens-min_airdens)/(max_airdens-min_airdens))*airdens_bins))[:-6])

# Find Kp for first event
Kp = findKp(ev_time,0)
geomag_data = Kp[2]
if geomag_data:
  prev_Kpval = Kp[0]
  Kpidx = Kp[1] #stop index of Kp value search
  prev_Kp_bin = int(('%.5f' % float(((prev_Kpval-min_Kp)/(max_Kp-min_Kp))*Kp_bins))[:-6])

# Find Mag field change for current time
FRN_geomag = findMagRange(ev_time)
FRN_data = FRN_geomag[1]
if FRN_data:
  prev_geo = FRN_geomag[0]
  prev_geo_bin = int(('%.5f' % float(((prev_geo-min_geo)/(max_geo-min_geo))*geo_bins))[:-6])

# find lidar fraction for first event
if lidar_avail:
  lidar_frac = getLidar(ev_time,0)
  prev_lidar = lidar_frac[0]
  lidar_idx = lidar_frac[1]
  prev_lidar_bin = int(('%.5f' % float(((prev_lidar-min_lidar)/(max_lidar-min_lidar))*lidar_bins))[:-6])

time_lid=0
if lidar_avail:  # only bin lidar time if the ls are collecting neutron data
  for i in range(0,len(lidar_time)-1):
    if float(event[0].split(',')[2]) <= lidar_time[i] <= float(event[len(event)-1].split(',')[2]):
      #time_lid = lidar_time[i+1]-lidar_time[i]
      #h36.Fill(lidar[i],time_lid)
      h36.Fill(lidar[i],1)

prev_daytime = int(unix2utc(ev_time)[11:13])+float(int(unix2utc(ev_time)[14:16])/60.)-8
if prev_daytime < 0:
  prev_daytime = prev_daytime+24
prev_daytime_bin = int(('%.5f' % float((prev_daytime/24)*daytime_bins))[:-6])

curr_bin_time = 0
press_bin_time = 0
temp_bin_time = 0
hum_bin_time = 0
dew_bin_time = 0
dens_bin_time = 0
Kp_bin_time = 0
geo_bin_time = 0
daytime_bin_time = 0
altpress_bin_time = 0
alttemp_bin_time = 0
althum_bin_time = 0
altdew_bin_time = 0
altdens_bin_time = 0
altgeo_bin_time = 0
pressdens_bin_time = 0
outdens_bin_time = 0
altoutdens_bin_time = 0
outindens_bin_time = 0
daytimegeo_bin_time = 0
presshum_bin_time = 0
altpresshum_bin_time = 0
lidar_bin_time = 0

# create arrays for event 1D graphs
g_alt, g_press, g_temp, g_hum, g_dew, g_dens, g_Kp, g_geo, g_daytime, g_outdens = ([] for i in range(10))

# boolean for freq plots - need to know if the current event is in the same minute as previous
same_min = True
same_min_ct = 0 # use to ignore the first partial minute of run data for CR frew hists
min_counts = 0 # running tally for number of counts within the minute
corr_min_counts = 0
hist_CRs = False # tells us whether or not to histogram the count rate

# get minute int for first event
prev_min = int(unix2utc(ev_time)[-5:-3])

prev_DTOAK = False
DTOAK_ct = 0
DTOAK_corr_ct = 0
prev_BERK = False
BERK_ct = 0
BERK_corr_ct = 0
prev_Bridge = False
Bridge_ct = 0
Bridge_corr_ct = 0
prev_Farm = False
Farm_ct = 0
Farm_corr_ct = 0
prev_Hwy = False
Hwy_ct = 0
Hwy_corr_ct = 0

### test - create weather time hists
if weather_avail:
  first_event = True
  wea_cut_short = False
  first_event_time = float(event[0].split(',')[2])
  last_event_time = float(event[len(event)-1].split(',')[2])
  last_weather_time = utctime[len(utctime)-2] + 30. #need to go a whole bin early since the next bin is used in subsequent calcs

  if last_weather_time < last_event_time:  # only make hists for data where there is weather collection
    end_idx = len(utctime)-2
    last_bin_time = 60.  # We discard the last temp measurement and get the entire previous bin
    wea_cut_short = True

  for i in range(0,len(utctime)-1):
    timecut_low = utctime[i] - (utctime[i]-utctime[i-1])/2.
    timecut_high = utctime[i] + (utctime[i+1]-utctime[i])/2.
    if first_event and timecut_low <= first_event_time < timecut_high:
      first_bin_time = timecut_high - first_event_time
      print "First Weather Bin Length:",first_bin_time
      start_idx = i
      if wea_cut_short:
        print "Last Weather Bin Length:",last_bin_time
        break # we already have the last bin time
    if timecut_low <= last_event_time < timecut_high:
      last_bin_time = last_event_time- timecut_low
      print "Last Weather Bin Length:",last_bin_time
      end_idx = i
      break
  if first_bin_time > 300. or last_bin_time > 300.:
    print '*****************\n','Weather not available for this run\n','*****************'
    weather_avail = False

if weather_avail:
  print "Histogramming weather time data..."
  # hist the first bin weather and time
  h5.Fill(bar[start_idx],first_bin_time)
  h8.Fill(temp[start_idx],first_bin_time)
  h11.Fill(AbsHum(temp[start_idx],hum[start_idx]),first_bin_time)
  h18.Fill(dew[start_idx],first_bin_time)
  h21.Fill(dens[start_idx],first_bin_time)
  h33.Fill(GetDens(bar[start_idx],temp[start_idx],hum[start_idx]),first_bin_time)
  #h2_2d.Fill(prev_alt,prev_press,first_bin_time)
  #h5_2d.Fill(prev_alt,prev_temp,first_bin_time)
  #h8_2d.Fill(prev_alt,prev_hum,first_bin_time)
  #h11_2d.Fill(prev_alt,prev_dew,first_bin_time)
  #h14_2d.Fill(prev_alt,prev_dens,first_bin_time)
  h20_2d.Fill(bar[start_idx],GetDens(bar[start_idx],temp[start_idx],hum[start_idx]),first_bin_time)
  #h23_2d.Fill(prev_alt,prev_outdens,first_bin_time)
  h26_2d.Fill(GetDens(bar[start_idx],temp[start_idx],hum[start_idx]),dens[start_idx],first_bin_time)
  h32_2d.Fill(bar[start_idx],AbsHum(temp[start_idx],hum[start_idx]),first_bin_time)
  #h2_3d.Fill(prev_alt,prev_press,prev_hum,first_bin_time)

  for i in range(start_idx+1,end_idx): # this will exclude the last bin which is to be added manually
    bin_time = ((utctime[i+1]-utctime[i])/2.)+((utctime[i]-utctime[i-1])/2.)# should usually be 60 sec between measurements, but not always!
    h5.Fill(bar[i],bin_time)
    h8.Fill(temp[i],bin_time)
    h11.Fill(AbsHum(temp[i],hum[i]),bin_time)
    h18.Fill(dew[i],bin_time)
    h21.Fill(dens[i],bin_time)
    h33.Fill(GetDens(bar[i],temp[i],hum[i]),bin_time)
    #h2_2d.Fill(prev_alt,prev_press,bin_time)
    #h5_2d.Fill(prev_alt,prev_temp,bin_time)
    #h8_2d.Fill(prev_alt,prev_hum,bin_time)
    #h11_2d.Fill(prev_alt,prev_dew,bin_time)
    #h14_2d.Fill(prev_alt,prev_dens,bin_time)
    h20_2d.Fill(bar[i],GetDens(bar[i],temp[i],hum[i]),bin_time)
    #h23_2d.Fill(prev_alt,prev_outdens,bin_time)
    h26_2d.Fill(GetDens(bar[i],temp[i],hum[i]),dens[i],bin_time)
    h32_2d.Fill(bar[i],AbsHum(temp[i],hum[i]),bin_time)
    #h2_3d.Fill(prev_alt,prev_press,prev_hum,bin_time)

  # hist the last bin weather and time
  h5.Fill(bar[end_idx],last_bin_time)
  h8.Fill(temp[end_idx],last_bin_time)
  h11.Fill(AbsHum(temp[end_idx],hum[end_idx]),last_bin_time)
  h18.Fill(dew[end_idx],last_bin_time)
  h21.Fill(dens[end_idx],last_bin_time)
  h33.Fill(GetDens(bar[end_idx],temp[end_idx],hum[end_idx]),last_bin_time)
  #h2_2d.Fill(prev_alt,prev_press,last_bin_time)
  #h5_2d.Fill(prev_alt,prev_temp,last_bin_time)
  #h8_2d.Fill(prev_alt,prev_hum,last_bin_time)
  #h11_2d.Fill(prev_alt,prev_dew,last_bin_time)
  #h14_2d.Fill(prev_alt,prev_dens,last_bin_time)
  h20_2d.Fill(bar[end_idx],GetDens(bar[end_idx],temp[end_idx],hum[end_idx]),last_bin_time)
  #h23_2d.Fill(prev_alt,prev_outdens,last_bin_time)
  h26_2d.Fill(GetDens(bar[end_idx],temp[end_idx],hum[end_idx]),dens[end_idx],last_bin_time)
  h32_2d.Fill(bar[end_idx],AbsHum(temp[end_idx],hum[end_idx]),last_bin_time)
  #h2_3d.Fill(prev_alt,prev_press,prev_hum,last_bin_time)

if weather_avail and wea_cut_short:  # compute new n_events range
  for i in range(0,n_events):
    ev_time = float(event[i].split(',')[2])
    if ev_time > last_weather_time:
      print "No weather data after event",i-1
      n_events = (i-1)
      break

###################################################################
# main loop
###################################################################

for ent in range(start_event+1, n_events):
#for ent in range(start_event+1, 5000):
  if(ent % (n_events/100) == 0):
    print '%d / %d' % (ent, n_events)

# get event information 
  ev_time = float(event[ent].split(',')[2])
  ev_alt = float(event[ent].split(',')[5])
  ev_detector = int(event[ent].split(',')[1])
  ev_lat = float(event[ent].split(',')[3])
  ev_lon = float(event[ent].split(',')[4])
  #ev_I_rel = float(pfotzer_corr(ev_alt))
  #ev_corr_ct = 1./ev_I_rel

  #for cr distribution- current minute int:
  curr_min = int(unix2utc(ev_time)[-5:-3])
  if(curr_min == prev_min):
    same_min = True
  else:
    same_min = False
    same_min_ct += 1 # wait to hist until count = 2

  if same_min and same_min_ct >= 1:
    min_counts += 1
    hist_CRs = False
  if not same_min and same_min_ct >= 2:
    hist_CRs = True # tells us to histogram the count rate for prev minute
    prev_CR = min_counts/60.
    min_counts = 1 # reset to include just the current event

  if(ev_alt < 0):
    ev_alt = 0
# add one count to time bin
  h13.Fill(ev_time,1)
  dethisttime[ev_detector].Fill(ev_time,1)
#  h13a.Fill(ev_time,ev_corr_ct)
  h1.Fill(ev_alt,1)
  dethistalt[ev_detector].Fill(ev_alt,1)
#  h1a.Fill(ev_alt,ev_corr_ct)

  # current event altitude bin
  altbin = int(('%.5f' % float((ev_alt/max_alt)*n_bins))[:-6])
  if(altbin == prev_bin): #and curr_bin_time > 10):
    curr_bin_time += (ev_time - last_ev_time)
    '''if same_min and not first_min:       #######NEED to work on this one#####
      n_alt_ct += 1;
    if not same_min and not first_min:
      h34_2d.Fill(ev_alt,'counts at altitude / time',1)'''
  if(altbin != prev_bin): #and curr_bin_time > 10):
    #histogram previous bin since we left that altitude bin
    curr_bin_time += (ev_time - last_ev_time)
    h2.Fill(prev_alt,curr_bin_time)
    #reset bin time
    curr_bin_time = 0

  ev_daytime = int(unix2utc(ev_time)[11:13])+float(int(unix2utc(ev_time)[14:16])/60.)-8 #subtract 8 hrs for pacific time (w/o DST)
  if ev_daytime < 0:
    ev_daytime = ev_daytime+24
  h29.Fill(ev_daytime,1)
  daytime_bin = int(('%.5f' % float((ev_daytime/24)*daytime_bins))[:-6])
  if(daytime_bin == prev_daytime_bin):
    daytime_bin_time += (ev_time - last_ev_time)
  else:
    daytime_bin_time += (ev_time - last_ev_time)
    h30.Fill(prev_daytime,daytime_bin_time)
    daytime_bin_time = 0

  # Lidar fraction
  if lidar_avail:
    lidar_frac = getLidar(ev_time,lidar_idx)
    ev_lidar = lidar_frac[0]
    #print 'frac:',ev_lidar,' time:',ev_time
    lidar_idx = lidar_frac[1]
    lidar_bin = int(('%.5f' % float(((ev_lidar-min_lidar)/(max_lidar-min_lidar))*lidar_bins))[:-6])
    h35.Fill(ev_lidar,1)
    #if(lidar_bin == prev_lidar_bin):
    #  lidar_bin_time += (ev_time - last_ev_time)
    #else:
    #  lidar_bin_time += (ev_time - last_ev_time)
    #  h36.Fill(prev_lidar,lidar_bin_time)
    #  lidar_bin_time = 0
    ### alt way to do bin time ###


  # Fill Kp val
  if geomag_data:
    Kp = findKp(ev_time,Kpidx)
    ev_Kpval = Kp[0]
    Kpidx = Kp[1]
    h13G.Fill(ev_time,ev_Kpval/10.)
    h23.Fill(ev_Kpval,1)
#    h23a.Fill(ev_Kpval,ev_corr_ct)
    if hist_CRs:
      h38_2d.Fill(prev_Kpval,prev_CR,1)
    Kp_bin = int(('%.5f' % float(((ev_Kpval-min_Kp)/(max_Kp-min_Kp))*Kp_bins))[:-6])
    if(Kp_bin == prev_Kp_bin):
      Kp_bin_time += (ev_time - last_ev_time)
    else:
      Kp_bin_time += (ev_time - last_ev_time)
      h24.Fill(prev_Kpval,Kp_bin_time)
      #reset bin time
      Kp_bin_time = 0

  if FRN_data:
    FRN_geomag = findMagRange(ev_time)
    ev_geo = FRN_geomag[0]
    h26.Fill(ev_geo,1)
#    h26a.Fill(ev_geo,ev_corr_ct)
    h16_2d.Fill(ev_alt,ev_geo,1)
    h28_2d.Fill(ev_daytime,ev_geo,1)
    geo_bin = int(('%.5f' % float(((ev_geo-min_geo)/(max_geo-min_geo))*geo_bins))[:-6])
    if(geo_bin == prev_geo_bin):
      geo_bin_time += (ev_time - last_ev_time)
    else:
      geo_bin_time += (ev_time - last_ev_time)
      h27.Fill(prev_geo,geo_bin_time)
      #reset bin time
      geo_bin_time = 0
    if(geo_bin == prev_geo_bin and altbin == prev_bin):
      altgeo_bin_time += (ev_time - last_ev_time)
    else:
      altgeo_bin_time += (ev_time - last_ev_time)
      h17_2d.Fill(prev_alt,prev_geo,altgeo_bin_time)
      #reset bin time
      altgeo_bin_time = 0

    if(geo_bin == prev_geo_bin and daytime_bin == prev_daytime_bin):
      daytimegeo_bin_time += (ev_time - last_ev_time)
    else:
      daytimegeo_bin_time += (ev_time - last_ev_time)
      h29_2d.Fill(prev_daytime,prev_geo,daytimegeo_bin_time)
      #reset bin time
      daytimegeo_bin_time = 0

  if weather_avail:
#    for i in range(idx,len(utctime)-1):
#      if utctime[i] <= ev_time < utctime[i+1]:
#        ev_temp = temp[i]
#        ev_hum = AbsHum(temp[i],hum[i])
#        ev_press = bar[i]
#        ev_dew = dew[i]
#        ev_dens = dens[i]
#        idx = i

#    ev_weather = getWeather(ev_time,idx)
#    ev_temp = ev_weather[0][0]
#    ev_hum = ev_weather[0][1]
#    ev_press = ev_weather[0][2]
#    ev_dew = ev_weather[0][3]
#    ev_dens = ev_weather[0][4]
#    ev_rel_hum = ev_weather[0][5]
#    idx = ev_weather[1]

    # for some reason its slower when I use the function form above
    for i in range(idx,len(utctime)-1):
      timecut_low = utctime[i] - (utctime[i]-utctime[i-1])/2
      timecut_high = utctime[i] + (utctime[i+1]-utctime[i])/2
      if timecut_low <= ev_time < timecut_high:
        ev_temp = temp[i]
        ev_hum = AbsHum(temp[i],hum[i])
        ev_press = bar[i]
        ev_dew = dew[i]
        ev_dens = dens[i]
        ev_rel_hum = hum[i]
        idx = i

    # apply count correction for given event
    ev_I_rel = float(press_corr(ev_press))
    ev_corr_ct = 1./ev_I_rel

    if not hist_CRs and same_min_ct >= 1:
      corr_min_counts += ev_corr_ct
    if hist_CRs:
      prev_corr_CR = corr_min_counts/60.
      corr_min_counts = ev_corr_ct # reset to include just the current event

    h1a.Fill(ev_alt,ev_corr_ct)
    h13a.Fill(ev_time,ev_corr_ct)
    if lidar_avail:
      h35a.Fill(ev_lidar,ev_corr_ct)
    if geomag_data:
      h23a.Fill(ev_Kpval,ev_corr_ct)
      if hist_CRs:
        h38a_2d.Fill(prev_Kpval,prev_corr_CR,1)
    if FRN_data:      
      h26a.Fill(ev_geo,ev_corr_ct)
    # add a count to weather count hists
    h7.Fill(ev_temp,1)
    h7a.Fill(ev_temp,ev_corr_ct)
    dethisttemp[ev_detector].Fill(ev_temp,1)
    h4.Fill(ev_press,1)
    h4a.Fill(ev_press,ev_corr_ct)
    dethistpress[ev_detector].Fill(ev_press,1)
    h10.Fill(ev_hum,1)
    h10a.Fill(ev_hum,ev_corr_ct)
    dethisthum[ev_detector].Fill(ev_hum,1)
    h17.Fill(ev_dew,1)
    h17a.Fill(ev_dew,ev_corr_ct)
    h20.Fill(ev_dens,1)
    h20a.Fill(ev_dens,ev_corr_ct)
    ev_outdens = GetDens(ev_press,ev_temp,ev_rel_hum)
    h32.Fill(ev_outdens,1)
    h32a.Fill(ev_outdens,ev_corr_ct)
    #2D hists
    h1_2d.Fill(ev_alt,ev_press,1)
    h4_2d.Fill(ev_alt,ev_temp,1)
    h7_2d.Fill(ev_alt,ev_hum,1)
    h10_2d.Fill(ev_alt,ev_dew,1)
    h13_2d.Fill(ev_alt,ev_dens,1)
    h19_2d.Fill(ev_press,ev_outdens,1)
    h22_2d.Fill(ev_alt,ev_outdens,1)
    h25_2d.Fill(ev_outdens,ev_dens,1)
    h31_2d.Fill(ev_press,ev_hum,1)
    # CR dist hists
    if hist_CRs:
      h35_2d.Fill(prev_press,prev_CR,1)
      h35a_2d.Fill(prev_press,prev_corr_CR,1)
      h36_2d.Fill(prev_temp,prev_CR,1)
      h36a_2d.Fill(prev_temp,prev_corr_CR,1)
      h37_2d.Fill(prev_hum,prev_CR,1)
      h37a_2d.Fill(prev_hum,prev_corr_CR,1)

    # 3D hists
    h1_3d.Fill(ev_alt,ev_press,ev_hum,1)

  #  if (bldg88):
  #    h7_88.Fill(ev_weather[0],1)
  #    h4_88.Fill(ev_weather[2],1)
  #    h10_88.Fill(ev_weather[1],1)
    # find current weather bins
  #  pressbin = int((ev_weather[2]-min_press)/((max_press-min_press)/press_bins)+1)
    pressbin = int(('%.5f' % float(((ev_press-min_press)/(max_press-min_press))*press_bins))[:-6])
  #  if(pressbin == prev_press_bin):
  #    press_bin_time += (ev_time - last_ev_time)
  #  else:
  #    press_bin_time += (ev_time - last_ev_time)
  #    h5.Fill(prev_press,press_bin_time)
      #reset pressure bin time
  #    press_bin_time = 0
    # if both bins are the same, we are in the same 2D bin as well
    if(pressbin == prev_press_bin and altbin == prev_bin):
      altpress_bin_time += (ev_time - last_ev_time)
    else:
      altpress_bin_time += (ev_time - last_ev_time)
      h2_2d.Fill(prev_alt,prev_press,altpress_bin_time)
      #reset bin time
      altpress_bin_time = 0

    #bldg 88 pressure
  #  if(bldg88 and pressbin == prev_press_bin_88):
  #    press_bin_time_88 += (ev_time - last_ev_time)
  #  elif(bldg88 and pressbin != prev_press_bin_88):
  #    h5_88.Fill(prev_press,press_bin_time_88)
      #reset pressure bin time
  #    press_bin_time = 0

    temp_bin = int(('%.5f' % float(((ev_temp-min_temp)/(max_temp-min_temp))*temp_bins))[:-6])
    #if(temp_bin == prev_temp_bin):
    #  temp_bin_time += (ev_time - last_ev_time)
    #else:
    #  temp_bin_time += (ev_time - last_ev_time)
    #  h8.Fill(prev_temp,temp_bin_time)
    #  reset temp bin time
    #  temp_bin_time = 0
    if(temp_bin == prev_temp_bin and altbin == prev_bin):
      alttemp_bin_time += (ev_time - last_ev_time)
    else:
      alttemp_bin_time += (ev_time - last_ev_time)
      h5_2d.Fill(prev_alt,prev_temp,alttemp_bin_time)
      #reset bin time
      alttemp_bin_time = 0

    hum_bin = int(('%.5f' % float(((ev_hum-min_hum)/(max_hum-min_hum))*hum_bins))[:-6])
    #if(hum_bin == prev_hum_bin):
    #  hum_bin_time += (ev_time - last_ev_time)
    #else:
    #  hum_bin_time += (ev_time - last_ev_time)
    #  h11.Fill(prev_hum,hum_bin_time)
      #reset hum bin time
    #  hum_bin_time = 0
    if(hum_bin == prev_hum_bin and altbin == prev_bin):
      althum_bin_time += (ev_time - last_ev_time)
    else:
      althum_bin_time += (ev_time - last_ev_time)
      h8_2d.Fill(prev_alt,prev_hum,althum_bin_time)
      #reset bin time
      althum_bin_time = 0
  #  if(hum_bin == prev_hum_bin and pressbin == prev_press_bin):
  #    presshum_bin_time += (ev_time - last_ev_time)
  #  else:
  #    presshum_bin_time += (ev_time - last_ev_time)
  #    h32_2d.Fill(prev_press,prev_hum,presshum_bin_time)
      #reset bin time
  #    presshum_bin_time = 0
    if(altbin == prev_bin and hum_bin == prev_hum_bin and pressbin == prev_press_bin):
      altpresshum_bin_time += (ev_time - last_ev_time)
    else:
      altpresshum_bin_time += (ev_time - last_ev_time)
      h2_3d.Fill(prev_alt,prev_press,prev_hum,altpresshum_bin_time)
      #reset bin time
      altpresshum_bin_time = 0
    dew_bin = int(('%.5f' % float(((ev_dew-min_dew)/(max_dew-min_dew))*dew_bins))[:-6])
    #if(dew_bin == prev_dew_bin):
    #  dew_bin_time += (ev_time - last_ev_time)
    #else:
    #  dew_bin_time += (ev_time - last_ev_time)
    #  h18.Fill(prev_dew,dew_bin_time)
    #  dew_bin_time = 0
    if(dew_bin == prev_dew_bin and altbin == prev_bin):
      altdew_bin_time += (ev_time - last_ev_time)
    else:
      altdew_bin_time += (ev_time - last_ev_time)
      h11_2d.Fill(prev_alt,prev_dew,altdew_bin_time)
      #reset bin time
      altdew_bin_time = 0

    dens_bin = int(('%.5f' % float(((ev_dens-min_airdens)/(max_airdens-min_airdens))*airdens_bins))[:-6])
    #if(dens_bin == prev_dens_bin):
    #  dens_bin_time += (ev_time - last_ev_time)
    #else:
    #  dens_bin_time += (ev_time - last_ev_time)
    #  h21.Fill(prev_dens,dens_bin_time)
    #  dens_bin_time = 0
    if(dens_bin == prev_dens_bin and altbin == prev_bin):
      altdens_bin_time += (ev_time - last_ev_time)
    else:
      altdens_bin_time += (ev_time - last_ev_time)
      h14_2d.Fill(prev_alt,prev_dens,altdens_bin_time)
      #reset bin time
      altdens_bin_time = 0

    outdens_bin = int(('%.5f' % float(((ev_outdens-min_airdens)/(max_airdens-min_airdens))*airdens_bins))[:-6])
    #if(outdens_bin == prev_outdens_bin):
    #  outdens_bin_time += (ev_time - last_ev_time)
    #else:
    #  outdens_bin_time += (ev_time - last_ev_time)
    #  h33.Fill(prev_outdens,outdens_bin_time)
    #  outdens_bin_time = 0
    if(outdens_bin == prev_outdens_bin and altbin == prev_bin):
      altoutdens_bin_time += (ev_time - last_ev_time)
    else:
      altoutdens_bin_time += (ev_time - last_ev_time)
      h23_2d.Fill(prev_alt,prev_outdens,altoutdens_bin_time)
      #reset bin time
      altoutdens_bin_time = 0
  #  if(outdens_bin == prev_outdens_bin and dens_bin == prev_dens_bin):
  #    outindens_bin_time += (ev_time - last_ev_time)
  #  else:
  #    outindens_bin_time += (ev_time - last_ev_time)
  #    h26_2d.Fill(prev_outdens,prev_dens,outindens_bin_time)
      #reset bin time
  #    outindens_bin_time = 0

    #press v out_airdens
  #  if(pressbin == prev_press_bin and outdens_bin == prev_outdens_bin):
  #    pressdens_bin_time += (ev_time - last_ev_time)
  #  else:
  #    pressdens_bin_time += (ev_time - last_ev_time)
  #    h20_2d.Fill(prev_press,prev_outdens,pressdens_bin_time)
      #reset bin time
  #    pressdens_bin_time = 0

  #DT Oakland CR
  DTOAK = Check_DTOAK(ev_lat,ev_lon)
  if DTOAK:
    if not prev_DTOAK:
      DTOAK_bin_start = ev_time
    if prev_DTOAK:
      if ev_time - DTOAK_bin_start <= 60.:          
        DTOAK_ct += 1
        if weather_avail:
          DTOAK_corr_ct += ev_corr_ct
      else:
        # bin it!!
        DTOAK_CR = DTOAK_ct/60.
        h90.Fill(DTOAK_CR,1)
        DTOAK_ct = 1
        if weather_avail:
          DTOAK_corr_CR = DTOAK_corr_ct/60.
          h90a.Fill(DTOAK_corr_CR,1)
          DTOAK_corr_ct = ev_corr_ct
        DTOAK_bin_start = ev_time
    prev_DTOAK = True
  if not DTOAK:
    prev_DTOAK = False
    DTOAK_ct = 0
    if weather_avail:
      DTOAK_corr_ct = 0

  #Berkeley CR
  BERK = Check_BERK(ev_lat,ev_lon)
  if BERK:
    if not prev_BERK:
      BERK_bin_start = ev_time
    if prev_BERK:
      if ev_time - BERK_bin_start <= 60.:          
        BERK_ct += 1
        if weather_avail:
          BERK_corr_ct += ev_corr_ct
      else:
        BERK_CR = BERK_ct/60.
        h91.Fill(BERK_CR,1)
        BERK_ct = 1
        if weather_avail:
          BERK_corr_CR = BERK_corr_ct/60.
          h91a.Fill(BERK_corr_CR,1)
          BERK_corr_ct = ev_corr_ct
        BERK_bin_start = ev_time
    prev_BERK = True
  if not BERK:
    prev_BERK = False
    BERK_ct = 0
    if weather_avail:
      BERK_corr_ct = 0

  #Bridge CR
  Bridge = Check_Bridge(ev_lat,ev_lon)
  if Bridge:
    if not prev_Bridge:
      Bridge_bin_start = ev_time
    if prev_Bridge:
      if ev_time - Bridge_bin_start <= 60.:          
        Bridge_ct += 1
        if weather_avail:
          Bridge_corr_ct += ev_corr_ct
      else:
        # bin it!!
        Bridge_CR = Bridge_ct/60.
        h92.Fill(Bridge_CR,1)
        Bridge_ct = 1
        if weather_avail:
          Bridge_corr_CR = Bridge_corr_ct/60.
          h92a.Fill(Bridge_corr_CR,1)
          Bridge_corr_ct = ev_corr_ct
        Bridge_bin_start = ev_time
    prev_Bridge = True
  if not Bridge:
    prev_Bridge = False
    Bridge_ct = 0
    if weather_avail:
      Bridge_corr_ct = 0

  #Farmland CR
  Farm = Check_Farm(ev_lat,ev_lon)
  if Farm:
    if not prev_Farm:
      Farm_bin_start = ev_time
    if prev_Farm:
      if ev_time - Farm_bin_start <= 60.:          
        Farm_ct += 1
        if weather_avail:
          Farm_corr_ct += ev_corr_ct
      else:
        # bin it!!
        Farm_CR = Farm_ct/60.
        h93.Fill(Farm_CR,1)
        Farm_ct = 1
        if weather_avail:
          Farm_corr_CR = Farm_corr_ct/60.
          h93a.Fill(Farm_corr_CR,1)
          Farm_corr_ct = ev_corr_ct
        Farm_bin_start = ev_time
    prev_Farm = True
  if not Farm:
    prev_Farm = False
    Farm_ct = 0
    if weather_avail:
      Farm_corr_ct = 0

  #Highway CR
  Hwy = Check_Hwy(ev_lat,ev_lon)
  if Hwy:
    if not prev_Hwy:
      Hwy_bin_start = ev_time
    if prev_Hwy:
      if ev_time - Hwy_bin_start <= 60.:          
        Hwy_ct += 1
        if weather_avail:
          Hwy_corr_ct += ev_corr_ct
      else:
        # bin it!!
        Hwy_CR = Hwy_ct/60.
        h94.Fill(Hwy_CR,1)
        Hwy_ct = 1
        if weather_avail:
          Hwy_corr_CR = Hwy_corr_ct/60.
          h94a.Fill(Hwy_corr_CR,1)
          Hwy_corr_ct = ev_corr_ct
        Hwy_bin_start = ev_time
    prev_Hwy = True
  if not Hwy:
    prev_Hwy = False
    Hwy_ct = 0
    if weather_avail:
      Hwy_corr_ct = 0

  #compute the remaining time for the last bin when acquisiton stops
  if(ent == n_events-1):
    h2.Fill(prev_alt,curr_bin_time)
    h30.Fill(prev_daytime,daytime_bin_time)
    #if lidar_avail:
      #fill time hist .Fill(prev_lidar,lidar_bin_time)
    if geomag_data:
      h24.Fill(prev_Kpval,Kp_bin_time)
    if FRN_data:
      h27.Fill(prev_geo,geo_bin_time)
      h17_2d.Fill(prev_alt,prev_geo,altgeo_bin_time)
      h29_2d.Fill(prev_daytime,prev_geo,daytimegeo_bin_time)
    if weather_avail:
      #h5.Fill(prev_press,press_bin_time)
      #h8.Fill(prev_temp,temp_bin_time)
      #h11.Fill(prev_hum,hum_bin_time)
      #h18.Fill(prev_dew,dew_bin_time)
      #h21.Fill(prev_dens,dens_bin_time)
      #h33.Fill(prev_outdens,outdens_bin_time)
      h2_2d.Fill(prev_alt,prev_press,altpress_bin_time)
      h5_2d.Fill(prev_alt,prev_temp,alttemp_bin_time)
      h8_2d.Fill(prev_alt,prev_hum,althum_bin_time)
      h11_2d.Fill(prev_alt,prev_dew,altdew_bin_time)
      h14_2d.Fill(prev_alt,prev_dens,altdens_bin_time)
      #h20_2d.Fill(prev_press,prev_outdens,pressdens_bin_time)
      h23_2d.Fill(prev_alt,prev_outdens,altoutdens_bin_time)
      #h26_2d.Fill(prev_outdens,prev_dens,outindens_bin_time)
      #h32_2d.Fill(prev_press,prev_hum,presshum_bin_time)
      h2_3d.Fill(prev_alt,prev_press,prev_hum,altpresshum_bin_time)

  #append to 1D graph arrays
  g_alt.append(ev_alt)
  g_daytime.append(ev_daytime)
  if weather_avail:
    g_press.append(ev_press)
    g_temp.append(ev_temp)
    g_hum.append(ev_hum)
    g_dew.append(ev_dew)
    g_dens.append(ev_dens)
    g_outdens.append(ev_outdens)
  if geomag_data:
    g_Kp.append(ev_Kpval)
  if FRN_data:
    g_geo.append(ev_geo)

  #reset
  prev_bin = altbin
  last_ev_time = ev_time
  prev_alt = ev_alt
  prev_daytime = ev_daytime
  prev_daytime_bin = daytime_bin
  beg_lat = ev_lat
  beg_lon = ev_lon
  prev_min = curr_min

  if lidar_avail:
    prev_lidar = ev_lidar
    prev_lidar_bin = lidar_bin

  if geomag_data:
    prev_Kpval = ev_Kpval
    prev_Kp_bin = Kp_bin

  if FRN_data:
    prev_geo = ev_geo
    prev_geo_bin = geo_bin
  
  if weather_avail:
    prev_press_bin = pressbin
    prev_press = ev_press
    prev_temp_bin = temp_bin
    prev_temp = ev_temp
    prev_hum_bin = hum_bin
    prev_hum = ev_hum
    prev_dew = ev_dew
    prev_dew_bin = dew_bin
    prev_dens = ev_dens
    prev_dens_bin = dens_bin
    prev_outdens = ev_outdens
    prev_outdens_bin = outdens_bin

# set time errors to zero
for x in range(0,n_bins+1):
  h2.SetBinError(x,0.)
  for y in range(0,press_bins+1):
    h2_2d.SetBinError(x,y,0.)
  for y in range(0,temp_bins+1):
    h5_2d.SetBinError(x,y,0.)
  for y in range(0,hum_bins+1):
    h8_2d.SetBinError(x,y,0.)
  for y in range(0,int(dew_bins)+1):
    h11_2d.SetBinError(x,y,0.)
  for y in range(0,int(airdens_bins)+1):
    h14_2d.SetBinError(x,y,0.)
    h23_2d.SetBinError(x,y,0.)
  for y in range(0,geo_bins+1):
    h17_2d.SetBinError(x,y,0.)
for x in range(0,press_bins+1):
  h5.SetBinError(x,0.)
  for y in range(0,int(airdens_bins)+1):
    h20_2d.SetBinError(x,y,0.)
  for y in range(0,hum_bins+1):
    h32_2d.SetBinError(x,y,0)
for x in range(0,temp_bins+1):
  h8.SetBinError(x,0.)
for x in range(0,hum_bins+1):
  h11.SetBinError(x,0.)
for x in range(0,int(dew_bins)+1):
  h18.SetBinError(x,0.)
for x in range(0,int(airdens_bins)+1):
  h21.SetBinError(x,0.)
  h33.SetBinError(x,0.)
  for y in range(0,int(airdens_bins)+1):
    h26_2d.SetBinError(x,y,0.)
for x in range(0,Kp_bins+1):
  h24.SetBinError(x,0.)
for x in range(0,geo_bins+1):
  h27.SetBinError(x,0.)
for x in range(0,daytime_bins+1):
  h30.SetBinError(x,0.)
  for y in range(0,geo_bins+1):
    h29_2d.SetBinError(x,y,0)
for x in range(0,lidar_bins+1):
  h36.SetBinError(x,0.)

# create count rate hists
# for altitude
h3 = h1.Clone()
h3.SetTitle("Count Rate Given Altitude")
h3.SetName("alt_count_rate")
h3.Divide(h2)
h3.GetXaxis().SetTitle("Altitude (m)")
h3.GetYaxis().SetTitle("Count Rate (CPS)")
allhists.append(h3)
#
h3a = h1a.Clone()
h3a.SetTitle("Count Rate Given Altitude")
h3a.SetName("corr_alt_count_rate")
h3a.Divide(h2)
h3a.GetXaxis().SetTitle("Altitude (m)")
h3a.GetYaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
# pressure
h6 = h4.Clone()
h6.SetTitle("Count Rate Given Pressure")
h6.SetName("press_count_rate")
h6.Divide(h5)
h6.GetXaxis().SetTitle("Pressure (mbar)")
h6.GetYaxis().SetTitle("Count Rate (CPS)")
allhists.append(h6)
#
h6a = h4a.Clone()
h6a.SetTitle("Count Rate Given Pressure")
h6a.SetName("corr_press_count_rate")
h6a.Divide(h5)
h6a.GetXaxis().SetTitle("Pressure (mbar)")
h6a.GetYaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
# temp
h9 = h7.Clone()
h9.SetTitle("Count Rate Given Temperature")
h9.SetName("temp_count_rate")
h9.Divide(h8)
h9.GetXaxis().SetTitle("Temperature (F)")
h9.GetYaxis().SetTitle("Count Rate (CPS)")
allhists.append(h9)
#
h9a = h7a.Clone()
h9a.SetTitle("Count Rate Given Temperature")
h9a.SetName("corr_temp_count_rate")
h9a.Divide(h8)
h9a.GetXaxis().SetTitle("Temperature (F)")
h9a.GetYaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
# hum
h12 = h10.Clone()
h12.SetTitle("Count Rate Given Humidity")
h12.SetName("hum_count_rate")
h12.Divide(h11)
h12.GetXaxis().SetTitle("Absolute Humidity (g/m^3)")
h12.GetYaxis().SetTitle("Count Rate (CPS)")
allhists.append(h12)
#
h12a = h10a.Clone()
h12a.SetTitle("Count Rate Given Humidity")
h12a.SetName("corr_hum_count_rate")
h12a.Divide(h11)
h12a.GetXaxis().SetTitle("Absolute Humidity (g/m^3)")
h12a.GetYaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
# dew
h19 = h17.Clone()
h19.SetTitle("Count Rate Given Dew Point")
h19.SetName("dew_count_rate")
h19.Divide(h18)
h19.GetXaxis().SetTitle("Dew Point (F)")
h19.GetYaxis().SetTitle("Count Rate (CPS)")
allhists.append(h19)
#
h19a = h17a.Clone()
h19a.SetTitle("Count Rate Given Dew Point")
h19a.SetName("corr_dew_count_rate")
h19a.Divide(h18)
h19a.GetXaxis().SetTitle("Dew Point (F)")
h19a.GetYaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
# air density
h22 = h20.Clone()
h22.SetTitle("Count Rate Given Air Density")
h22.SetName("airdens_count_rate")
h22.Divide(h21)
h22.GetXaxis().SetTitle("Inside Air Density (kg/m^3)")
h22.GetYaxis().SetTitle("Count Rate (CPS)")
allhists.append(h22)
#
h22a = h20a.Clone()
h22a.SetTitle("Count Rate Given Air Density")
h22a.SetName("corr_airdens_count_rate")
h22a.Divide(h21)
h22a.GetXaxis().SetTitle("Inside Air Density (kg/m^3)")
h22a.GetYaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
# Kp value
h25 = h23.Clone()
h25.SetTitle("Count Rate Given Kp Value")
h25.SetName("Kp_count_rate")
h25.Divide(h24)
h25.GetXaxis().SetTitle("Kp Value")
h25.GetYaxis().SetTitle("Count Rate (CPS)")
allhists.append(h25)
#
h25a = h23a.Clone()
h25a.SetTitle("Count Rate Given Kp Value")
h25a.SetName("corr_Kp_count_rate")
h25a.Divide(h24)
h25a.GetXaxis().SetTitle("Kp Value")
h25a.GetYaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
# FRN geomag field value
h28 = h26.Clone()
h28.SetTitle("Count Rate Given Hourly Geomagnetic Field Strength Change")
h28.SetName("Geomag_count_rate")
h28.Divide(h27)
h28.GetXaxis().SetTitle("Hourly Change (nT)")
h28.GetYaxis().SetTitle("Count Rate (CPS)")
#
h28a = h26a.Clone()
h28a.SetTitle("Count Rate Given Hourly Geomagnetic Field Strength Change")
h28a.SetName("corr_Geomag_count_rate")
h28a.Divide(h27)
h28a.GetXaxis().SetTitle("Hourly Change (nT)")
h28a.GetYaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
# time of day
h31 = h29.Clone()
h31.SetTitle("Count Rate Given Time of Day")
h31.SetName("daytime_count_rate")
h31.Divide(h30)
h31.GetXaxis().SetTitle("Time of Day (hr)")
h31.GetYaxis().SetTitle("Count Rate (CPS)")
# time
h14 = h13.Clone()
h14.SetTitle("Neutron Count Rate")
h14.SetName("time_count_rate")
h14.Scale(1/timeint)
h14.GetXaxis().SetTitle("Epoch Time (s)")
h14.GetYaxis().SetTitle("Count Rate (CPS)")
allhists.append(h14)
h14a = h13a.Clone()
h14a.SetTitle("Neutron Count Rate")
h14a.SetName("corr_time_count_rate")
h14a.Scale(1/timeint)
h14a.GetXaxis().SetTitle("Epoch Time (s)")
h14a.GetYaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
# air density
h34 = h32.Clone()
h34.SetTitle("Count Rate Given Air Density")
h34.SetName("outdens_count_rate")
h34.Divide(h33)
h34.GetXaxis().SetTitle("Outside Air Density (kg/m^3)")
h34.GetYaxis().SetTitle("Count Rate (CPS)")
#
h34a = h32a.Clone()
h34a.SetTitle("Count Rate Given Air Density")
h34a.SetName("corr_outdens_count_rate")
h34a.Divide(h33)
h34a.GetXaxis().SetTitle("Outside Air Density (kg/m^3)")
h34a.GetYaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
# Lidar data
h37 = h35.Clone()
h37.SetTitle("Count Rate Given Lidar Return Fraction of Solid Angle")
h37.SetName("lidar_count_rate")
h37.Divide(h36)
h37.GetXaxis().SetTitle("Fraction of Returns")
h37.GetYaxis().SetTitle("Count Rate (CPS)")
#
h37a = h35a.Clone()
h37a.SetTitle("Count Rate Given Lidar Return Fraction of Solid Angle")
h37a.SetName("corr_lidar_count_rate")
h37a.Divide(h36)
h37a.GetXaxis().SetTitle("Fraction of Returns")
h37a.GetYaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")

#2d
h3_2d = h1_2d.Clone()
h3_2d.SetTitle("Count Rate Given Altitude and Pressure")
h3_2d.SetName("alt_press_count_rate")
h3_2d.Divide(h2_2d)
h3_2d.GetXaxis().SetTitle("Altitude (m)")
h3_2d.GetXaxis().SetTitleOffset(1.5)
h3_2d.GetYaxis().SetTitle("Pressure (mbar)")
h3_2d.GetYaxis().SetTitleOffset(1.5)
h3_2d.GetZaxis().SetTitle("Count Rate (CPS)")
h3_2d.GetZaxis().SetTitleOffset(1.25)
#
h6_2d = h4_2d.Clone()
h6_2d.SetTitle("Count Rate Given Altitude and Temperature")
h6_2d.SetName("alt_temp_count_rate")
h6_2d.Divide(h5_2d)
h6_2d.GetXaxis().SetTitle("Altitude (m)")
h6_2d.GetXaxis().SetTitleOffset(1.5)
h6_2d.GetYaxis().SetTitle("Temperature (F)")
h6_2d.GetYaxis().SetTitleOffset(1.5)
h6_2d.GetZaxis().SetTitle("Count Rate (CPS)")
h6_2d.GetZaxis().SetTitleOffset(1.25)
#
h9_2d = h7_2d.Clone()
h9_2d.SetTitle("Count Rate Given Altitude and Humidity")
h9_2d.SetName("alt_hum_count_rate")
h9_2d.Divide(h8_2d)
h9_2d.GetXaxis().SetTitle("Altitude (m)")
h9_2d.GetXaxis().SetTitleOffset(1.5)
h9_2d.GetYaxis().SetTitle("Absolute Humidity (g/m^3)")
h9_2d.GetYaxis().SetTitleOffset(1.5)
h9_2d.GetZaxis().SetTitle("Count Rate (CPS)")
h9_2d.GetZaxis().SetTitleOffset(1.25)
#
h12_2d = h10_2d.Clone()
h12_2d.SetTitle("Count Rate Given Altitude and Dew Point")
h12_2d.SetName("alt_dew_count_rate")
h12_2d.Divide(h11_2d)
h12_2d.GetXaxis().SetTitle("Altitude (m)")
h12_2d.GetXaxis().SetTitleOffset(1.5)
h12_2d.GetYaxis().SetTitle("Dew Point (F)")
h12_2d.GetYaxis().SetTitleOffset(1.5)
h12_2d.GetZaxis().SetTitle("Count Rate (CPS)")
h12_2d.GetZaxis().SetTitleOffset(1.25)
#
h15_2d = h13_2d.Clone()
h15_2d.SetTitle("Count Rate Given Altitude and Air Density")
h15_2d.SetName("alt_airdens_count_rate")
h15_2d.Divide(h14_2d)
h15_2d.GetXaxis().SetTitle("Altitude (m)")
h15_2d.GetXaxis().SetTitleOffset(1.5)
h15_2d.GetYaxis().SetTitle("Inside Air Density (kg/m^3)")
h15_2d.GetYaxis().SetTitleOffset(1.5)
h15_2d.GetZaxis().SetTitle("Count Rate (CPS)")
h15_2d.GetZaxis().SetTitleOffset(1.25)
#
h18_2d = h16_2d.Clone()
h18_2d.SetTitle("Count Rate Given Altitude and Geomagnetic Field Strength Change")
h18_2d.SetName("alt_geomag_count_rate")
h18_2d.Divide(h17_2d)
h18_2d.GetXaxis().SetTitle("Altitude (m)")
h18_2d.GetXaxis().SetTitleOffset(1.5)
h18_2d.GetYaxis().SetTitle("Hourly Change (nT)")
h18_2d.GetYaxis().SetTitleOffset(1.5)
h18_2d.GetZaxis().SetTitle("Count Rate (CPS)")
h18_2d.GetZaxis().SetTitleOffset(1.25)
#
h21_2d = h19_2d.Clone()
h21_2d.SetTitle("Count Rate Given Pressure and Outside Air Density")
h21_2d.SetName("press_outdens_count_rate")
h21_2d.Divide(h20_2d)
h21_2d.GetXaxis().SetTitle("Pressure (mbar)")
h21_2d.GetXaxis().SetTitleOffset(1.5)
h21_2d.GetYaxis().SetTitle("Outside Air Density (kg/m^3)")
h21_2d.GetYaxis().SetTitleOffset(1.5)
h21_2d.GetZaxis().SetTitle("Count Rate (CPS)")
h21_2d.GetZaxis().SetTitleOffset(1.25)
#
h24_2d = h22_2d.Clone()
h24_2d.SetTitle("Count Rate Given Altitude and Air Density")
h24_2d.SetName("alt_outdens_count_rate")
h24_2d.Divide(h23_2d)
h24_2d.GetXaxis().SetTitle("Altitude (m)")
h24_2d.GetXaxis().SetTitleOffset(1.5)
h24_2d.GetYaxis().SetTitle("Outside Air Density (kg/m^3)")
h24_2d.GetYaxis().SetTitleOffset(1.5)
h24_2d.GetZaxis().SetTitle("Count Rate (CPS)")
h24_2d.GetZaxis().SetTitleOffset(1.25)
#
h27_2d = h25_2d.Clone()
h27_2d.SetTitle("Count Rate Given Inside and Outside Air Density")
h27_2d.SetName("outdens_airdens_count_rate")
h27_2d.Divide(h26_2d)
h27_2d.GetXaxis().SetTitle("Outside Air Density (kg/m^3)")
h27_2d.GetXaxis().SetTitleOffset(1.5)
h27_2d.GetYaxis().SetTitle("Inside Air Density (kg/m^3)")
h27_2d.GetYaxis().SetTitleOffset(1.5)
h27_2d.GetZaxis().SetTitle("Count Rate (CPS)")
h27_2d.GetZaxis().SetTitleOffset(1.25)
#
h30_2d = h28_2d.Clone()
h30_2d.SetTitle("Count Rate Given Time of Day and Geomagnetic Field Strength Change")
h30_2d.SetName("time_geomag_count_rate")
h30_2d.Divide(h29_2d)
h30_2d.GetXaxis().SetTitle("Time of Day (hr)")
h30_2d.GetXaxis().SetTitleOffset(1.5)
h30_2d.GetYaxis().SetTitle("Hourly Change (nT)")
h30_2d.GetYaxis().SetTitleOffset(1.5)
h30_2d.GetZaxis().SetTitle("Count Rate (CPS)")
h30_2d.GetZaxis().SetTitleOffset(1.25)
#
h33_2d = h31_2d.Clone()
h33_2d.SetTitle("Count Rate Given Pressure and Humidity")
h33_2d.SetName("press_hum_count_rate")
h33_2d.Divide(h32_2d)
h33_2d.GetXaxis().SetTitle("Pressure (mbar)")
h33_2d.GetXaxis().SetTitleOffset(1.5)
h33_2d.GetYaxis().SetTitle("Absolute Humidity (g/m^3)")
h33_2d.GetYaxis().SetTitleOffset(1.5)
h33_2d.GetZaxis().SetTitle("Count Rate (CPS)")
h33_2d.GetZaxis().SetTitleOffset(1.25)
# 3D
h3_3d = h1_3d.Clone()
h3_3d.SetTitle("Neutron Count Rate Given Altitude, Pressure and Humidity")
h3_3d.SetName("alt_press_hum_time_count_rate")
h3_3d.Divide(h2_3d)
h3_3d.GetXaxis().SetTitle("Altitude (m)")
h3_3d.GetXaxis().SetTitleOffset(1.5)
h3_3d.GetYaxis().SetTitle("Pressure (mbar)")
h3_3d.GetYaxis().SetTitleOffset(1.5)
h3_3d.GetZaxis().SetTitle("Absolute Humidity (g/m^3)")
h3_3d.GetZaxis().SetTitleOffset(1.5)

#add hists to stack
h999 = h14.Clone()
h999.SetName("time_cr")
h999.SetMarkerStyle(20)
h999.SetMarkerColor(2)
h13G.SetMarkerStyle(20)
h13G.SetMarkerColor(3)
#h13G.Scale(1/10.)
kpstack.Add(h13G)
kpstack.Add(h999)
OneD_fol.Add(kpstack)

# fill count rate distribution (ignore last bin so only go to time_bins rather than time_bins+1)
Bin_CR = 0
for x in range(0,time_bins):
  Bin_CR = h14.GetBinContent(x)
  h15.Fill(Bin_CR,1)
  Bin_CR2 = h14a.GetBinContent(x)
  h15a.Fill(Bin_CR2,1)
  '''if (Bin_CR >= 0):
    h15.Fill(Bin_CR,1)
  if (Bin_CR2 >= 0):
    h15a.Fill(Bin_CR2,1)'''
allhists.append(h15)

# fill count in timeint distribution
Bin_Ct = 0
for x in range(0,time_bins):
  Bin_Ct = h13.GetBinContent(x)
  if (Bin_Ct >= 0):
    h16.Fill(Bin_Ct,1)
allhists.append(h16)

# append other newly added hists
# alt: h1a h3a / press: h4a h6a / temp: h7a h9a / hum: h10a h12a / time: h13a h14a h15a / dew: h17a h19a / dens: h20a h22a
allhists.append(h1a) #25
allhists.append(h3a) #26
allhists.append(h4a) #27
allhists.append(h6a) #28
allhists.append(h7a) #29
allhists.append(h9a) #30
allhists.append(h10a) #31
allhists.append(h12a) #32
allhists.append(h13a) #33
allhists.append(h14a) #34
allhists.append(h15a) #35
allhists.append(h17a) #36
allhists.append(h19a) #37
allhists.append(h20a) #38
allhists.append(h22a) #39
allhists.append(h23a) #40
allhists.append(h25a) #41
allhists.append(h26)
allhists.append(h27)
allhists.append(h28)
allhists.append(h26a)
allhists.append(h28a)
allhists.append(h29) #47
allhists.append(h30)
allhists.append(h31)
allhists.append(h32)
allhists.append(h33)
allhists.append(h34)
allhists.append(h32a)
allhists.append(h34a)
# Lidar
allhists.append(h35) #55
allhists.append(h35a)
allhists.append(h36)
allhists.append(h37)
allhists.append(h37a)
# CR dists
allhists.append(h90)
allhists.append(h90a)
allhists.append(h91)
allhists.append(h91a)
allhists.append(h92)
allhists.append(h92a)
allhists.append(h93)
allhists.append(h93a)
allhists.append(h94)
allhists.append(h94a)
#
allhists.append(h3_3d) #70
allhists.append(h1_3d)
allhists.append(h2_3d)
allhists.append(h3_2d) #73
allhists.append(h6_2d)
allhists.append(h9_2d)
allhists.append(h12_2d)
allhists.append(h15_2d)
allhists.append(h18_2d)
allhists.append(h21_2d)
allhists.append(h24_2d)
allhists.append(h27_2d)
allhists.append(h30_2d)
allhists.append(h33_2d)
allhists.append(h1_2d)
allhists.append(h2_2d)
allhists.append(h4_2d)
allhists.append(h5_2d)
allhists.append(h7_2d)
allhists.append(h8_2d)
allhists.append(h10_2d)
allhists.append(h11_2d)
allhists.append(h13_2d)
allhists.append(h14_2d)
allhists.append(h16_2d)
allhists.append(h17_2d)
allhists.append(h19_2d)
allhists.append(h20_2d)
allhists.append(h22_2d)
allhists.append(h23_2d)
allhists.append(h25_2d)
allhists.append(h26_2d)
allhists.append(h28_2d)
allhists.append(h29_2d)
allhists.append(h31_2d)
allhists.append(h32_2d) #105
#allhists.append(h34_2d)
#allhists.append(h34a_2d)
allhists.append(h35_2d)  #106
allhists.append(h35a_2d)
allhists.append(h36_2d)
allhists.append(h36a_2d)
allhists.append(h37_2d)
allhists.append(h37a_2d)
allhists.append(h38_2d)
allhists.append(h38a_2d)

# folder and center bin titles
for i in range(0,len(allhists)):
  allhists[i].SetDirectory(0)
  allhists[i].GetXaxis().CenterTitle()
  allhists[i].GetYaxis().CenterTitle()
  if i in (0,1,15,25,26):
    alt_fol.Add(allhists[i])
  if i in (2,3,16,27,28): 
    press_fol.Add(allhists[i])
  if i in (4,5,17,29,30): 
    temp_fol.Add(allhists[i])
  if i in (6,7,18,31,32): 
    hum_fol.Add(allhists[i])
  if i in (8,9,19,36,37):
    dew_fol.Add(allhists[i])
  if i in (10,11,20,38,39,50,51,52,53,54):
    adens_fol.Add(allhists[i])
  if i in (12,13,21,40,41):
    Kp_fol.Add(allhists[i])
  if i in (42,43,44,45,46):
    GeoMag_fol.Add(allhists[i])
  if i in (55,56,57,58,59):
    Lidar_fol.Add(allhists[i])
  if i in (14,22,23,24,33,34,35,47,48,49,60,61,62,63,64,65,66,67,68,69):
    time_fol.Add(allhists[i])
  if i >= 73 and i <= 105:
    TwoD_fol.Add(allhists[i])
  if i in (70,71,72):
    ThreeD_fol.Add(allhists[i])
  if i >= 106:
    CR_Freq_fol.Add(allhists[i])

# make det hist into count rate
for i in range(0,16):
  dethistalt[i].SetDirectory(0)
  alt_fol.Add(dethistalt[i])
  dethistpress[i].Divide(h5)
  dethistpress[i].SetDirectory(0)
  press_fol.Add(dethistpress[i])
  dethisttemp[i].Divide(h8)
  dethisttemp[i].SetDirectory(0)
  temp_fol.Add(dethisttemp[i])
  dethisthum[i].Divide(h11)
  dethisthum[i].SetDirectory(0)
  hum_fol.Add(dethisthum[i])
  dethisttime[i].Scale(1/timeint)
  dethisttime[i].SetDirectory(0)
  time_fol.Add(dethisttime[i])

# 1D graphs
n_points = len(g_alt)
if weather_avail:
  # must convert to c arrays to pass into TGraph
  altvpress = TGraph(n_points,array('d',g_alt),array('d',g_press))
  altvpress.SetName("alt_v_press")
  altvpress.SetTitle("Event Altitude and Pressure")
  altvpress.GetXaxis().SetTitle("Altitude (m)")
  altvpress.GetYaxis().SetTitle("Pressure (mbar)")
  OneD_fol.Add(altvpress)
  #
  airdensity = TGraph(n_points,array('d',g_outdens),array('d',g_dens))
  airdensity.SetName("air_densities")
  airdensity.SetTitle("Event Inside and Outside Air Density")
  airdensity.GetXaxis().SetTitle("Outside Air Density (kg/m^3)")
  airdensity.GetYaxis().SetTitle("Inside Air Density (kg/m^3)")
  OneD_fol.Add(airdensity)
  #
  altvoutdens = TGraph(n_points,array('d',g_alt),array('d',g_outdens))
  altvoutdens.SetName("alt_v_outdens")
  altvoutdens.SetTitle("Event Altitude and Outside Air Density")
  altvoutdens.GetXaxis().SetTitle("Altitude (m)")
  altvoutdens.GetYaxis().SetTitle("Outside Air Density (kg/m^3)")
  OneD_fol.Add(altvoutdens)
  #
  timevpress = TGraph(n_points,array('d',g_daytime),array('d',g_press))
  timevpress.SetName("time_v_press")
  timevpress.SetTitle("Pressure at Time of Day")
  timevpress.GetXaxis().SetTitle("Time of Day (hr)")
  timevpress.GetYaxis().SetTitle("Pressure (mbar)")
  OneD_fol.Add(timevpress)
  #
  timevhum = TGraph(n_points,array('d',g_daytime),array('d',g_hum))
  timevhum.SetName("time_v_hum")
  timevhum.SetTitle("Humidity at Time of Day")
  timevhum.GetXaxis().SetTitle("Time of Day (hr)")
  timevhum.GetYaxis().SetTitle("Absolute Humidity (g/m^3)")
  OneD_fol.Add(timevhum)
  #
  timevtemp = TGraph(n_points,array('d',g_daytime),array('d',g_temp))
  timevtemp.SetName("time_v_temp")
  timevtemp.SetTitle("Temperature at Time of Day")
  timevtemp.GetXaxis().SetTitle("Time of Day (hr)")
  timevtemp.GetYaxis().SetTitle("Temperature (F)")
  OneD_fol.Add(timevtemp)

if FRN_data:
  dayvgeo = TGraph(n_points,array('d',g_daytime),array('d',g_geo))
  dayvgeo.SetName("time_v_geomag")
  dayvgeo.SetTitle("Hourly Geomagnetic Field Strength Change at Time of Day")
  dayvgeo.GetXaxis().SetTitle("Time of Day (hr)")
  dayvgeo.GetYaxis().SetTitle("Hourly Change (nT)")
  OneD_fol.Add(dayvgeo)

#CPS_bin = []
#for i in range(0,n_bins+1):
#   CPS_bin.append(h3.GetBinContent(i))

#print CPS_bin

# save file and close
alt_fol.Write()
press_fol.Write()
temp_fol.Write()
hum_fol.Write()
dew_fol.Write()
adens_fol.Write()
Kp_fol.Write()
GeoMag_fol.Write()
Lidar_fol.Write()
time_fol.Write()
TwoD_fol.Write()
ThreeD_fol.Write()
OneD_fol.Write()
CR_Freq_fol.Write()
geowea.close()
infile.close()
f.Write()
f.Close()

#########################
