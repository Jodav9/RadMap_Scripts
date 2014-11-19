import numpy as np
import ROOT
from ROOT import TH1D, TH2D, TH3D, TFolder, gDirectory, TGraph, TMultiGraph, TCanvas, gROOT
import tables
import sys
import math
import os
from os import walk
from array import array
import operator
ROOT.SetMemoryPolicy( ROOT.kMemoryStrict )
# To do: create root file and name it based on input file, write histograms to root file, print bin values?

# Load the root files
#Histsdir = '/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/Converted/PyRootHists/'
# for B88 files only
Histsdir = '/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/Data/B88_Files/PyRootHists/'
# combine both combined files ???
#Histsdir = '/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/Data/B88_Files/PyRootHists/All_Combined/'
#Histsdir = '/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/Data/'

Hists_in = []
for (dirpath, dirnames, filenames) in walk(Histsdir):
    Hists_in.extend(filenames)
    break 
#print Hists_in

#sort hists in for cronological order
Pre_Sort_Hists = []
for i in range(0,len(Hists_in)):
    yr = int(Hists_in[i][9:11])
    mo = int(Hists_in[i][1:3])
    day = int(Hists_in[i][4:6])
    Pre_Sort_Hists.append([Hists_in[i],yr,mo,day])
SortedHists = sorted(Pre_Sort_Hists, key=operator.itemgetter(1,2,3))

#create root file and tree
root_out = ROOT.TFile(str(sys.argv[1]), "recreate")
alt_fol = ROOT.TFolder("Alt_CR_Hists","Alt_CR_Hists")
press_fol = ROOT.TFolder("Press_CR_Hists","Press_CR_Hists")
temp_fol = ROOT.TFolder("Temp_CR_Hists","Temp_CR_Hists")
hum_fol = ROOT.TFolder("Hum_CR_Hists","Hum_CR_Hists")
dew_fol = ROOT.TFolder("DewPt_CR_Hists","DewPt_CR_Hists")
adens_fol = ROOT.TFolder("AirDens_CR_Hists","AirDens_CR_Hists")
Kp_fol = ROOT.TFolder("Kp_CR_Hists","Kp_CR_Hists")
GeoMag_fol = ROOT.TFolder("GeoMag_CR_Hists","GeoMag_CR_Hists")
TwoD_fol = ROOT.TFolder("2D_Hists","2D_Hists")
OneD_fol = ROOT.TFolder("1D_Graphs","1D_Graphs")
time_fol = ROOT.TFolder("Time_CR_Hists","Time_CR_Hists")
ThreeD_fol = ROOT.TFolder("3D_Hists","3D_Hists")
CR_Freq_fol = ROOT.TFolder("CR_Freq_Plots","CR_Freq_Plots")

n_bins = 60 #for count rate hists
max_alt = 1500
min_press = 950.
max_press = 1050.
press_bins = 200
min_temp = 30
max_temp = 105
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
min_geo = 0.
max_geo = 50.
geo_bins = 50
min_daytime = 0.
max_daytime = 24.
daytime_bins = 48

min_date = 0
max_date = 86
date_bins = 86

min_CR = 0
max_CR = 10
CR_bins = (max_CR - min_CR)*10 # bin every 0.1 CPS

# array of all histograms
allhists = []

ch1 = TH1D("alt_events","Combined Neutron Event Altitude",n_bins,0,max_alt);
ch1.GetXaxis().SetTitle("Altitude (m)")
ch1.GetYaxis().SetTitle("Counts")
allhists.append(ch1)
# h1.Sumw2() error propagation
#
ch1a = TH1D("press_corr_alt_events","Combined Neutron Event Altitude",n_bins,0,max_alt);
ch1a.GetXaxis().SetTitle("Altitude (m)")
ch1a.GetYaxis().SetTitle("Counts")
#
ch2 = TH1D("alt_time","Combined Neutron Time at Altitude",n_bins,0,max_alt);
ch2.GetXaxis().SetTitle("Altitude (m)")
ch2.GetYaxis().SetTitle("Time (s)")
allhists.append(ch2)
# press
ch4 = TH1D("press_events","Combined Neutron Event Pressure",press_bins,min_press,max_press);
ch4.GetXaxis().SetTitle("Pressure (mbar)")
ch4.GetYaxis().SetTitle("Counts")
allhists.append(ch4)
#
ch4a = TH1D("press_corr_press_events","Combined Neutron Event Pressure",press_bins,min_press,max_press);
ch4a.GetXaxis().SetTitle("Pressure (mbar)")
ch4a.GetYaxis().SetTitle("Counts")
#
ch5 = TH1D("press_time","Combined Time at Pressure",press_bins,min_press,max_press);
ch5.GetXaxis().SetTitle("Pressure (mbar)")
ch5.GetYaxis().SetTitle("Time (s)")
allhists.append(ch5)
# temp
ch7 = TH1D("temp_events","Combined Neutron Event Temperature",temp_bins,min_temp,max_temp);
ch7.GetXaxis().SetTitle("Temperature (F)")
ch7.GetYaxis().SetTitle("Counts")
allhists.append(ch7)
#
ch7a = TH1D("press_corr_temp_events","Combined Neutron Event Temperature",temp_bins,min_temp,max_temp);
ch7a.GetXaxis().SetTitle("Temperature (F)")
ch7a.GetYaxis().SetTitle("Counts")
#
ch8 = TH1D("temp_time","Combined Time at Temperature",temp_bins,min_temp,max_temp);
ch8.GetXaxis().SetTitle("Temperature (F)")
ch8.GetYaxis().SetTitle("Time (s)")
allhists.append(ch8)
# humidity
ch10 = TH1D("hum_events","Combined Neutron Event Humidity",hum_bins,min_hum,max_hum);
ch10.GetXaxis().SetTitle("Absolute Humidity (g/m^3)")
ch10.GetYaxis().SetTitle("Counts")
allhists.append(ch10)
#
ch10a = TH1D("press_corr_hum_events","Combined Neutron Event Humidity",hum_bins,min_hum,max_hum);
ch10a.GetXaxis().SetTitle("Absolute Humidity (g/m^3)")
ch10a.GetYaxis().SetTitle("Counts")
#
ch11 = TH1D("hum_time","Combined Time at Humidity",hum_bins,min_hum,max_hum);
ch11.GetXaxis().SetTitle("Absolute Humidity (g/m^3)")
ch11.GetYaxis().SetTitle("Time (s)")
allhists.append(ch11)
# dew point
ch17 = TH1D("dew_events","Combined Neutron Event Dew Point",int(dew_bins),min_dew,max_dew);
ch17.GetXaxis().SetTitle("Dew Point (F)")
ch17.GetYaxis().SetTitle("Counts")
ch17.Sumw2()
#
ch17a = TH1D("press_corr_dew_events","Combined Neutron Event Dew Point",int(dew_bins),min_dew,max_dew);
ch17a.GetXaxis().SetTitle("Dew Point (F)")
ch17a.GetYaxis().SetTitle("Counts")
ch17a.Sumw2()
#
ch18 = TH1D("dew_time","Combined Time at Dew Point",int(dew_bins),min_dew,max_dew);
ch18.GetXaxis().SetTitle("Dew Point (F)")
ch18.GetYaxis().SetTitle("Time (s)")
# air density
ch20 = TH1D("airdens_events","Combined Neutron Event Air Density",int(airdens_bins),min_airdens,max_airdens);
ch20.GetXaxis().SetTitle("Inside Air Density (kg/m^3)")
ch20.GetYaxis().SetTitle("Counts")
ch20.Sumw2()
#
ch20a = TH1D("press_corr_airdens_events","Combined Neutron Event Air Density",int(airdens_bins),min_airdens,max_airdens);
ch20a.GetXaxis().SetTitle("Inside Air Density (kg/m^3)")
ch20a.GetYaxis().SetTitle("Counts")
ch20a.Sumw2()
#
ch21 = TH1D("airdens_time","Combined Time at Air Density",int(airdens_bins),min_airdens,max_airdens);
ch21.GetXaxis().SetTitle("Inside Air Density (kg/m^3)")
ch21.GetYaxis().SetTitle("Time (s)")
# Kp value
ch23 = TH1D("Kp_events","Combined Neutron Event Kp Value",Kp_bins,min_Kp,max_Kp);
ch23.GetXaxis().SetTitle("Kp Value")
ch23.GetYaxis().SetTitle("Counts")
ch23.Sumw2()
#
ch23a = TH1D("press_corr_Kp_events","Combined Neutron Event Kp Value",Kp_bins,min_Kp,max_Kp);
ch23a.GetXaxis().SetTitle("Kp Value")
ch23a.GetYaxis().SetTitle("Counts")
ch23a.Sumw2()
#
ch24 = TH1D("Kp_time","Combined Time at Kp Value",Kp_bins,min_Kp,max_Kp);
ch24.GetXaxis().SetTitle("Kp Value")
ch24.GetYaxis().SetTitle("Time (s)")
# count rate distribution
ch15 = TH1D("CR","Combined Neutron Count Rate Distribution",CR_bins,min_CR,max_CR);
ch15.GetXaxis().SetTitle("Count Rate (CPS)")
ch15.GetYaxis().SetTitle("Frequency")
#
ch15a = TH1D("corr_CR","Combined Neutron Count Rate Distribution",CR_bins,min_CR,max_CR);
ch15a.GetXaxis().SetTitle("Count Rate (CPS)")
ch15a.GetYaxis().SetTitle("Frequency")
# Fresno Geomagnetic Data
ch26 = TH1D("Geomag_events","Neutron Events Given Hourly Geomagnetic Field Strength Change",geo_bins,min_geo,max_geo);
ch26.GetXaxis().SetTitle("Hourly Change (nT)")
ch26.GetYaxis().SetTitle("Counts")
ch26.Sumw2()
#
ch26a = TH1D("press_corr_Geomag_events","Neutron Events Given Hourly Geomagnetic Field Strength Change",geo_bins,min_geo,max_geo);
ch26a.GetXaxis().SetTitle("Hourly Change (nT)")
ch26a.GetYaxis().SetTitle("Counts")
ch26a.Sumw2()
#
ch27 = TH1D("Geomag_time","Time at Geomagnetic Field Strength Change Value",geo_bins,min_geo,max_geo);
ch27.GetXaxis().SetTitle("Hourly Change (nT)")
ch27.GetYaxis().SetTitle("Time (s)")
# time of day
ch29 = TH1D("daytime_events","Neutron Events Time of Day",daytime_bins,min_daytime,max_daytime);
ch29.GetXaxis().SetTitle("Time of Day (hr)")
ch29.GetYaxis().SetTitle("Counts")
ch29.Sumw2()
#
ch30 = TH1D("daytime_time","Neutron Events Time of Day",daytime_bins,min_daytime,max_daytime);
ch30.GetXaxis().SetTitle("Time of Day (hr)")
ch30.GetYaxis().SetTitle("Time (s)")
# outside air density
ch32 = TH1D("outdens_events","Neutron Event Air Density",int(airdens_bins),min_airdens,max_airdens);
ch32.GetXaxis().SetTitle("Outside Air Density (kg/m^3)")
ch32.GetYaxis().SetTitle("Counts")
ch32.Sumw2()
#
ch32a = TH1D("press_corr_outdens_events","Neutron Event Air Density",int(airdens_bins),min_airdens,max_airdens);
ch32a.GetXaxis().SetTitle("Outside Air Density (kg/m^3)")
ch32a.GetYaxis().SetTitle("Counts")
ch32a.Sumw2()
#
ch33 = TH1D("outdens_time","Time at Air Density",int(airdens_bins),min_airdens,max_airdens);
ch33.GetXaxis().SetTitle("Outside Air Density (kg/m^3)")
ch33.GetYaxis().SetTitle("Time (s)")
# DT Oakland count rate distribution
ch90 = TH1D("DT_Oak_CR","Neutron Count Rate Distribution in Downtown Oakland",CR_bins,min_CR,max_CR);
ch90.GetXaxis().SetTitle("Count Rate (CPS)")
ch90.GetYaxis().SetTitle("Frequency")
#
ch90a = TH1D("DT_Oak_corr_CR","Neutron Count Rate Distribution in Downtown Oakland",CR_bins,min_CR,max_CR);
ch90a.GetXaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
ch90a.GetYaxis().SetTitle("Frequency")
# Berkeley count rate distribution
ch91 = TH1D("Berk_CR","Neutron Count Rate Distribution in Berkeley",CR_bins,min_CR,max_CR);
ch91.GetXaxis().SetTitle("Count Rate (CPS)")
ch91.GetYaxis().SetTitle("Frequency")
#
ch91a = TH1D("Berk_corr_CR","Neutron Count Rate Distribution in Berkeley",CR_bins,min_CR,max_CR);
ch91a.GetXaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
ch91a.GetYaxis().SetTitle("Frequency")
# Bridge count rate distribution
ch92 = TH1D("Bridge_CR","Neutron Count Rate Distribution over Bridges",CR_bins,min_CR,max_CR);
ch92.GetXaxis().SetTitle("Count Rate (CPS)")
ch92.GetYaxis().SetTitle("Frequency")
#
ch92a = TH1D("Bridge_corr_CR","Neutron Count Rate Distribution over Bridges",CR_bins,min_CR,max_CR);
ch92a.GetXaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
ch92a.GetYaxis().SetTitle("Frequency")
# Farm Land count rate distribution
ch93 = TH1D("Farm_CR","Neutron Count Rate Distribution in Farmland",CR_bins,min_CR,max_CR);
ch93.GetXaxis().SetTitle("Count Rate (CPS)")
ch93.GetYaxis().SetTitle("Frequency")
#
ch93a = TH1D("Farm_corr_CR","Neutron Count Rate Distribution in Farmland",CR_bins,min_CR,max_CR);
ch93a.GetXaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
ch93a.GetYaxis().SetTitle("Frequency")
# Highway count rate distribution
ch94 = TH1D("Hwy_CR","Neutron Count Rate Distribution on Highway",CR_bins,min_CR,max_CR);
ch94.GetXaxis().SetTitle("Count Rate (CPS)")
ch94.GetYaxis().SetTitle("Frequency")
#
ch94a = TH1D("Hwy_corr_CR","Neutron Count Rate Distribution on Highway",CR_bins,min_CR,max_CR);
ch94a.GetXaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
ch94a.GetYaxis().SetTitle("Frequency")
####
# One count rate distribution per date
ch100_2d = TH2D("Date_CR","Neutron Count Rate Distributions for All Runs",date_bins,min_date,max_date,CR_bins,min_CR,max_CR);
ch100_2d.GetXaxis().SetTitle("Date")
ch100_2d.GetYaxis().SetTitle("Count Rate (CPS)")
ch100_2d.GetZaxis().SetTitle("Frequency")
#
ch100a_2d = TH2D("Date_Adj_CR","Adjusted Neutron Count Rate Distributions for All Runs",date_bins,min_date,max_date,CR_bins,min_CR,max_CR);
ch100a_2d.GetXaxis().SetTitle("Date")
ch100a_2d.GetYaxis().SetTitle("Adjusted Count Rate (CPS)")
ch100a_2d.GetZaxis().SetTitle("Frequency")
# mean count rate per date
ch100 = TH1D("Date_Mean_CR","Neutron Mean Count Rate for All Runs",date_bins,min_date,max_date);
ch100.GetXaxis().SetTitle("Date")
ch100.GetYaxis().SetTitle("Mean Count Rate (CPS)")
#
ch100a = TH1D("Date_Adj_Mean_CR","Adjusted Neutron Mean Count Rate for All Runs",date_bins,min_date,max_date);
ch100a.GetXaxis().SetTitle("Date")
ch100a.GetYaxis().SetTitle("Adjusted Mean Count Rate (CPS)")

############
# 2D
############
# Alt v. Pressure v. CR
ch1_2d = TH2D("alt_press_events","Neutron Event Altitude and Pressure",n_bins,0,max_alt,press_bins,min_press,max_press);
ch1_2d.GetXaxis().SetTitle("Altitude (m)")
ch1_2d.GetYaxis().SetTitle("Pressure (mbar)")
ch1_2d.GetZaxis().SetTitle("Counts")
ch1_2d.Sumw2()
#
ch2_2d = TH2D("alt_press_time","Neutron Time at Altitude and Pressure",n_bins,0,max_alt,press_bins,min_press,max_press);
ch2_2d.GetXaxis().SetTitle("Altitude (m)")
ch2_2d.GetYaxis().SetTitle("Pressure (mbar)")
ch2_2d.GetZaxis().SetTitle("Time (s)")
# Alt v. Temp v. CR
ch4_2d = TH2D("alt_temp_events","Neutron Event Altitude and Temperature",n_bins,0,max_alt,temp_bins,min_temp,max_temp);
ch4_2d.GetXaxis().SetTitle("Altitude (m)")
ch4_2d.GetYaxis().SetTitle("Temperature (F)")
ch4_2d.GetZaxis().SetTitle("Counts")
ch4_2d.Sumw2()
#
ch5_2d = TH2D("alt_temp_time","Neutron Time at Altitude and Temperature",n_bins,0,max_alt,temp_bins,min_temp,max_temp);
ch5_2d.GetXaxis().SetTitle("Altitude (m)")
ch5_2d.GetYaxis().SetTitle("Temperature (F)")
ch5_2d.GetZaxis().SetTitle("Time (s)")
# Alt v. Hum v. CR
ch7_2d = TH2D("alt_hum_events","Neutron Event Altitude and Humidity",n_bins,0,max_alt,hum_bins,min_hum,max_hum);
ch7_2d.GetXaxis().SetTitle("Altitude (m)")
ch7_2d.GetYaxis().SetTitle("Absolute Humidity (g/m^3)")
ch7_2d.GetZaxis().SetTitle("Counts")
ch7_2d.Sumw2()
#
ch8_2d = TH2D("alt_hum_time","Neutron Time at Altitude and Humidity",n_bins,0,max_alt,hum_bins,min_hum,max_hum);
ch8_2d.GetXaxis().SetTitle("Altitude (m)")
ch8_2d.GetYaxis().SetTitle("Absolute Humidity (g/m^3)")
ch8_2d.GetZaxis().SetTitle("Time (s)")
# Alt v. Dew v. CR
ch10_2d = TH2D("alt_dew_events","Neutron Event Altitude and Dew Point",n_bins,0,max_alt,int(dew_bins),min_dew,max_dew);
ch10_2d.GetXaxis().SetTitle("Altitude (m)")
ch10_2d.GetYaxis().SetTitle("Dew Point (F)")
ch10_2d.GetZaxis().SetTitle("Counts")
ch10_2d.Sumw2()
#
ch11_2d = TH2D("alt_dew_time","Neutron Time at Altitude and Dew Point",n_bins,0,max_alt,int(dew_bins),min_dew,max_dew);
ch11_2d.GetXaxis().SetTitle("Altitude (m)")
ch11_2d.GetYaxis().SetTitle("Dew Point (F)")
ch11_2d.GetZaxis().SetTitle("Time (s)")
# Alt v. Airdens v. CR
ch13_2d = TH2D("alt_airdens_events","Neutron Event Altitude and Air Density",n_bins,0,max_alt,int(airdens_bins),min_airdens,max_airdens);
ch13_2d.GetXaxis().SetTitle("Altitude (m)")
ch13_2d.GetYaxis().SetTitle("Inside Air Density (kg/m^3)")
ch13_2d.GetZaxis().SetTitle("Counts")
ch13_2d.Sumw2()
#
ch14_2d = TH2D("alt_airdens_time","Neutron Time at Altitude and Air Density",n_bins,0,max_alt,int(airdens_bins),min_airdens,max_airdens);
ch14_2d.GetXaxis().SetTitle("Altitude (m)")
ch14_2d.GetYaxis().SetTitle("Inside Air Density (kg/m^3)")
ch14_2d.GetZaxis().SetTitle("Time (s)")
# Alt v. Geomag v. CR
ch16_2d = TH2D("alt_geomag_events","Neutron Event Altitude and Geomagnetic Field Strength Change",n_bins,0,max_alt,geo_bins,min_geo,max_geo);
ch16_2d.GetXaxis().SetTitle("Altitude (m)")
ch16_2d.GetYaxis().SetTitle("Hourly Change (nT)")
ch16_2d.GetZaxis().SetTitle("Counts")
ch16_2d.Sumw2()
#
ch17_2d = TH2D("alt_geomag_time","Neutron Time at Altitude and Geomagnetic Field Strength Change",n_bins,0,max_alt,geo_bins,min_geo,max_geo);
ch17_2d.GetXaxis().SetTitle("Altitude (m)")
ch17_2d.GetYaxis().SetTitle("Hourly Change (nT)")
ch17_2d.GetZaxis().SetTitle("Time (s)")
# Press v. out_Airdesn v. CR
ch19_2d = TH2D("press_outdens_events","Neutron Event Pressure and Air Density",press_bins,min_press,max_press,int(airdens_bins),min_airdens,max_airdens);
ch19_2d.GetXaxis().SetTitle("Pressure (mbar)")
ch19_2d.GetYaxis().SetTitle("Outside Air Density (kg/m^3)")
ch19_2d.GetZaxis().SetTitle("Counts")
ch19_2d.Sumw2()
#
ch20_2d = TH2D("press_outdens_time","Neutron Time at Pressure and Air Density",press_bins,min_press,max_press,int(airdens_bins),min_airdens,max_airdens);
ch20_2d.GetXaxis().SetTitle("Pressure (mbar)")
ch20_2d.GetYaxis().SetTitle("Outside Air Density (kg/m^3)")
ch20_2d.GetZaxis().SetTitle("Time (s)")
# Alt v. out_airdens v. CR
ch22_2d = TH2D("alt_outdens_events","Neutron Event Altitude and Air Density",n_bins,0,max_alt,int(airdens_bins),min_airdens,max_airdens);
ch22_2d.GetXaxis().SetTitle("Altitude (m)")
ch22_2d.GetYaxis().SetTitle("Outside Air Density (kg/m^3)")
ch22_2d.GetZaxis().SetTitle("Counts")
ch22_2d.Sumw2()
#
ch23_2d = TH2D("alt_outdens_time","Neutron Time at Altitude and Air Density",n_bins,0,max_alt,int(airdens_bins),min_airdens,max_airdens);
ch23_2d.GetXaxis().SetTitle("Altitude (m)")
ch23_2d.GetYaxis().SetTitle("Outside Air Density (kg/m^3)")
ch23_2d.GetZaxis().SetTitle("Time (s)")
# Out v. in_airdens v. CR
ch25_2d = TH2D("outdens_airdens_events","Neutron Event at Inside and Outside Air Density",int(airdens_bins),min_airdens,max_airdens,int(airdens_bins),min_airdens,max_airdens);
ch25_2d.GetXaxis().SetTitle("Outside Air Density (kg/m^3)")
ch25_2d.GetYaxis().SetTitle("Inside Air Density (kg/m^3)")
ch25_2d.GetZaxis().SetTitle("Counts")
ch25_2d.Sumw2()
#
ch26_2d = TH2D("outdens_airdens_time","Neutron Time at Inside and Outside Air Density",int(airdens_bins),min_airdens,max_airdens,int(airdens_bins),min_airdens,max_airdens);
ch26_2d.GetXaxis().SetTitle("Outside Air Density (kg/m^3)")
ch26_2d.GetYaxis().SetTitle("Inside Air Density (kg/m^3)")
ch26_2d.GetZaxis().SetTitle("Time (s)")
# Time of Day v. Geomag v. CR
ch28_2d = TH2D("time_geomag_events","Neutron Event Time of Day and Geomagnetic Field Strength Change",daytime_bins,min_daytime,max_daytime,geo_bins,min_geo,max_geo);
ch28_2d.GetXaxis().SetTitle("Time of Day (hr)")
ch28_2d.GetYaxis().SetTitle("Hourly Change (nT)")
ch28_2d.GetZaxis().SetTitle("Counts")
ch28_2d.Sumw2()
#
ch29_2d = TH2D("time_geomag_time","Neutron Time at Time of Day and Geomagnetic Field Strength Change",daytime_bins,min_daytime,max_daytime,geo_bins,min_geo,max_geo);
ch29_2d.GetXaxis().SetTitle("Time of Day (hr)")
ch29_2d.GetYaxis().SetTitle("Hourly Change (nT)")
ch29_2d.GetZaxis().SetTitle("Time (s)")
# Press v. Hum v. CR
ch31_2d = TH2D("press_hum_events","Neutron Event Pressure and Humidity",press_bins,min_press,max_press,hum_bins,min_hum,max_hum);
ch31_2d.GetXaxis().SetTitle("Pressure (mbar)")
ch31_2d.GetYaxis().SetTitle("Absolute Humidity (g/m^3)")
ch31_2d.GetZaxis().SetTitle("Counts")
ch31_2d.Sumw2()
#
ch32_2d = TH2D("press_hum_time","Neutron Time at Pressure and Humidity",press_bins,min_press,max_press,hum_bins,min_hum,max_hum);
ch32_2d.GetXaxis().SetTitle("Pressure (mbar)")
ch32_2d.GetYaxis().SetTitle("Absolute Humidity (g/m^3)")
ch32_2d.GetZaxis().SetTitle("Time (s)")
###
# CR environmental density plots
'''# Alt v. CR Freq
ch34_2d = TH2D("alt_CR_freq","Altitude Count Rate Frequency",n_bins,0,max_alt,CR_bins,min_CR,max_CR);
ch34_2d.GetXaxis().SetTitle("Altitude (m)")
ch34_2d.GetYaxis().SetTitle("Count Rate (CPS)")
ch34_2d.GetZaxis().SetTitle("Frequency")
# adjusted
ch34a_2d = TH2D("adj_alt_CR_freq","Adjusted Altitude Count Rate Frequency",n_bins,0,max_alt,CR_bins,min_CR,max_CR);
ch34a_2d.GetXaxis().SetTitle("Altitude (m)")
ch34a_2d.GetYaxis().SetTitle("Adjusted Count Rate (CPS)")
ch34a_2d.GetZaxis().SetTitle("Frequency") '''
# Press v. CR Freq
ch35_2d = TH2D("press_CR_freq","Pressure Count Rate Frequency",press_bins,min_press,max_press,CR_bins,min_CR,max_CR);
ch35_2d.GetXaxis().SetTitle("Pressure (mbar)")
ch35_2d.GetXaxis().SetTitleOffset(1.5)
ch35_2d.GetYaxis().SetTitle("Count Rate (CPS)")
ch35_2d.GetYaxis().SetTitleOffset(1.5)
ch35_2d.GetZaxis().SetTitle("Frequency")
ch35_2d.GetZaxis().SetTitleOffset(1.25)
# adjusted
ch35a_2d = TH2D("adj_press_CR_freq","Adjusted Pressure Count Rate Frequency",press_bins,min_press,max_press,CR_bins,min_CR,max_CR);
ch35a_2d.GetXaxis().SetTitle("Pressure (mbar)")
ch35a_2d.GetYaxis().SetTitle("Adjusted Count Rate (CPS)")
ch35a_2d.GetZaxis().SetTitle("Frequency")
# Temp v. CR Freq
ch36_2d = TH2D("temp_CR_freq","Temperature Count Rate Frequency",temp_bins,min_temp,max_temp,CR_bins,min_CR,max_CR);
ch36_2d.GetXaxis().SetTitle("Temperature (F)")
ch36_2d.GetYaxis().SetTitle("Count Rate (CPS)")
ch36_2d.GetZaxis().SetTitle("Frequency")
# adjusted
ch36a_2d = TH2D("adj_temp_CR_freq","Adjusted Temperature Count Rate Frequency",temp_bins,min_temp,max_temp,CR_bins,min_CR,max_CR);
ch36a_2d.GetXaxis().SetTitle("Temperature (F)")
ch36a_2d.GetYaxis().SetTitle("Adjusted Count Rate (CPS)")
ch36a_2d.GetZaxis().SetTitle("Frequency")
# Hum v. CR Freq
ch37_2d = TH2D("hum_CR_freq","Humidity Count Rate Frequency",hum_bins,min_hum,max_hum,CR_bins,min_CR,max_CR);
ch37_2d.GetXaxis().SetTitle("Absolute Humidity (g/m^3)")
ch37_2d.GetYaxis().SetTitle("Count Rate (CPS)")
ch37_2d.GetZaxis().SetTitle("Frequency")
# adjusted
ch37a_2d = TH2D("adj_hum_CR_freq","Adjusted Humidity Count Rate Frequency",hum_bins,min_hum,max_hum,CR_bins,min_CR,max_CR);
ch37a_2d.GetXaxis().SetTitle("Absolute Humidity (g/m^3)")
ch37a_2d.GetYaxis().SetTitle("Adjusted Count Rate (CPS)")
ch37a_2d.GetZaxis().SetTitle("Frequency")
# Kp value v. CR Freq
ch38_2d = TH2D("kp_CR_freq","Kp Value Count Rate Frequency",Kp_bins,min_Kp,max_Kp,CR_bins,min_CR,max_CR);
ch38_2d.GetXaxis().SetTitle("Kp Value")
ch38_2d.GetYaxis().SetTitle("Count Rate (CPS)")
ch38_2d.GetZaxis().SetTitle("Frequency")
# adjusted
ch38a_2d = TH2D("adj_kp_CR_freq","Adjusted Kp Value Count Rate Frequency",Kp_bins,min_Kp,max_Kp,CR_bins,min_CR,max_CR);
ch38a_2d.GetXaxis().SetTitle("Kp Value")
ch38a_2d.GetYaxis().SetTitle("Adjusted Count Rate (CPS)")
ch38a_2d.GetZaxis().SetTitle("Frequency")

###
# 3D
# Alt v. Press v. Hum v. CR
ch1_3d = TH3D("alt_press_hum_events","Neutron Event Altitude, Pressure and Humidity",n_bins,0,max_alt,press_bins,min_press,max_press,hum_bins,min_hum,max_hum);
ch1_3d.GetXaxis().SetTitle("Altitude (m)")
ch1_3d.GetYaxis().SetTitle("Pressure (mbar)")
ch1_3d.GetZaxis().SetTitle("Absolute Humidity (g/m^3)")
#h1_3d.Sumw2()
#
ch2_3d = TH3D("alt_press_hum_time","Neutron Time at Altitude, Pressure and Humidity",n_bins,0,max_alt,press_bins,min_press,max_press,hum_bins,min_hum,max_hum);
ch2_3d.GetXaxis().SetTitle("Altitude (m)")
ch2_3d.GetYaxis().SetTitle("Pressure (mbar)")
ch2_3d.GetZaxis().SetTitle("Absolute Humidity (g/m^3)")

# Set up TGraphs
altvpress = TMultiGraph()
airdensity = TMultiGraph()
altvoutdens = TMultiGraph()
timevpress = TMultiGraph()
timevhum = TMultiGraph()
dayvgeo = TMultiGraph()
'''
dethistalt, dethistpress, dethisttemp, dethisthum = ([] for i in range(4))
# create detector hists
for i in range(0,16):
  dethistalt.append('alt_ch_'+str(i))
  dethistalt[i] = TH1D(dethistalt[i],"Counts at Altitude",n_bins,0,max_alt);
  dethistpress.append('press_ch_'+str(i))
  dethistpress[i] = TH1D(dethistpress[i],"Count Rate at Pressure",press_bins,min_press,max_press);
  dethisttemp.append('temp_ch_'+str(i))
  dethisttemp[i] = TH1D(dethisttemp[i],"Count Rate at Temperature",temp_bins,min_temp,max_temp);
  dethisthum.append('hum_ch_'+str(i))
  dethisthum[i] = TH1D(dethisthum[i],"Count Rate at Humidity",hum_bins,min_hum,max_hum);
'''
ct_bin = [0.]*n_bins
time_bin = [0.]*n_bins
bin_alt = range(-max_alt/n_bins,max_alt,max_alt/n_bins)

weather = True

print "Adding Hists..."
# main loop
for i in range(0,len(SortedHists)):
  weather = True
  Histnum = i
  print str(i+1)+".",SortedHists[i][0]
  day = SortedHists[i][3]
  mo = SortedHists[i][2]
  yr = SortedHists[i][1]
  fin = ROOT.TFile(Histsdir+SortedHists[i][0])
  keylist = fin.GetListOfKeys()
  for i,m in enumerate(keylist):
    if m.GetTitle() == '1D_Graphs':
      folder = fin.Get(m.GetTitle())
      ap = folder.FindObject('alt_v_press')
      try:
        altvpress.Add(ap)
      except TypeError:
        print 'No Weather for this File'
        weather = False
  #if weather:
  for i,k in enumerate(keylist):
	  if k.IsFolder() == True:
	    if k.GetTitle() == 'Alt_CR_Hists':
	      folder = fin.Get(k.GetTitle())
	      h1 = folder.FindObject('alt_events')
	      ch1.Add(h1)
	      h1a = folder.FindObject('press_corr_alt_events')
	      ch1a.Add(h1a)
	      h2 = folder.FindObject('alt_time')
	      ch2.Add(h2)
	#      for z in range(0,16):
	#        dethist = folder.FindObject('alt_ch_'+str(z))
	#        dethistalt[z].Add(dethist) #gives count hist per detector
	    if k.GetTitle() == 'Press_CR_Hists':
	      folder = fin.Get(k.GetTitle())
	      h4 = folder.FindObject('press_events')
	      ch4.Add(h4)
	      h4a = folder.FindObject('press_corr_press_events')
	      ch4a.Add(h4a)
	      h5 = folder.FindObject('press_time')
	      ch5.Add(h5)
	#      for z in range(0,16):
	#        dethist = folder.FindObject('press_ch_'+str(z))
	#        dethist.Multiply(h5)
	#        dethistpress[z].Add(dethist) #gives count hist per detector
	    if k.GetTitle() == 'Temp_CR_Hists':
	      folder = fin.Get(k.GetTitle())
	      h7 = folder.FindObject('temp_events')
	      ch7.Add(h7)
	      h7a = folder.FindObject('press_corr_temp_events')
	      ch7a.Add(h7a)
	      h8 = folder.FindObject('temp_time')
	      ch8.Add(h8)
	#      for z in range(0,16):
	#        dethist = folder.FindObject('temp_ch_'+str(z))
	#        dethist.Multiply(h8)
	#        dethisttemp[z].Add(dethist) #gives count hist per detector
	    if k.GetTitle() == 'Hum_CR_Hists':
	      folder = fin.Get(k.GetTitle())
	      h10 = folder.FindObject('hum_events')
	      ch10.Add(h10)
	      h10a = folder.FindObject('press_corr_hum_events')
	      ch10a.Add(h10a)
	      h11 = folder.FindObject('hum_time')
	      ch11.Add(h11)
	#      for z in range(0,16):
	#        dethist = folder.FindObject('hum_ch_'+str(z))
	#        dethist.Multiply(h11)
	#        dethisthum[z].Add(dethist) #gives count hist per detector
	    if k.GetTitle() == 'DewPt_CR_Hists':
	      folder = fin.Get(k.GetTitle())
	      h17 = folder.FindObject('dew_events')
	      ch17.Add(h17)
	      h17a = folder.FindObject('press_corr_dew_events')
	      ch17a.Add(h17a)
	      h18 = folder.FindObject('dew_time')
	      ch18.Add(h18)
	    if k.GetTitle() == 'AirDens_CR_Hists':
	      folder = fin.Get(k.GetTitle())
	      h20 = folder.FindObject('airdens_events')
	      ch20.Add(h20)
	      h20a = folder.FindObject('press_corr_airdens_events')
	      ch20a.Add(h20a)
	      h21 = folder.FindObject('airdens_time')
	      ch21.Add(h21)
	      h32 = folder.FindObject("outdens_events")
	      ch32.Add(h32)
	      h32a = folder.FindObject("press_corr_outdens_events")
	      ch32a.Add(h32a)
	      h33 = folder.FindObject("outdens_time")
	      ch33.Add(h33)
	    if k.GetTitle() == 'Kp_CR_Hists':
	      folder = fin.Get(k.GetTitle())
	      h23 = folder.FindObject('Kp_events')
	      ch23.Add(h23)
	      h23a = folder.FindObject('press_corr_Kp_events')
	      ch23a.Add(h23a)
	      h24 = folder.FindObject('Kp_time')
	      ch24.Add(h24)
	    if k.GetTitle() == 'GeoMag_CR_Hists':
	      folder = fin.Get(k.GetTitle())
	      h26 = folder.FindObject('Geomag_events')
	      ch26.Add(h26)
	      h26a = folder.FindObject('press_corr_Geomag_events')
	      ch26a.Add(h26a)
	      h27 = folder.FindObject('Geomag_time')
	      ch27.Add(h27)
	    if k.GetTitle() == 'Time_CR_Hists':
	      folder = fin.Get(k.GetTitle())
	      h15 = folder.FindObject('CR')
	      ch15.Add(h15)
	      h15a = folder.FindObject('corr_CR')
	      # add dist to Date CR distribution
	      CRxfreq = 0
	      mean_CR = 0
	      freq_sum = 0
	      adj_CRxfreq = 0
	      adj_mean_CR = 0
	      adj_freq_sum = 0
	      for x in range(0,CR_bins):
	      	cps = h15.GetXaxis().GetBinCenter(x)# get x value associated with bin # 
	      	freq = h15.GetBinContent(x)
	      	if cps > 0.1:
	      		ch100_2d.Fill(Histnum,cps,freq)
	      		freq_sum += freq
	      		CRxfreq += cps*freq
	      	cps_corr = h15a.GetXaxis().GetBinCenter(x)
	      	freq_corr = h15a.GetBinContent(x)
	      	if cps_corr > 0.1:
	      		ch100a_2d.Fill(Histnum,cps_corr,freq_corr)
	      		adj_freq_sum += freq_corr
	      		adj_CRxfreq += cps_corr*freq_corr
	      mean_CR = CRxfreq/freq_sum
	      ch100.Fill(Histnum,mean_CR)
	      #adj_mean_CR = adj_CRxfreq/adj_freq_sum
	      #ch100a.Fill(Histnum,adj_mean_CR)
	      bin_name = str(mo)+'/'+str(day)+'/'+str(yr)
	      ch100_2d.GetXaxis().SetBinLabel(Histnum+1,bin_name)
	      #ch100a_2d.GetXaxis().SetBinLabel(Histnum+1,bin_name)
	      ch100.GetXaxis().SetBinLabel(Histnum+1,bin_name)
	      #ch100a.GetXaxis().SetBinLabel(Histnum+1,bin_name)
	      h15a = folder.FindObject('corr_CR')
	      ch15a.Add(h15a)
	      h29 = folder.FindObject('daytime_events')
	      ch29.Add(h29)
	      h30 = folder.FindObject('daytime_time')
	      ch30.Add(h30)
	      h90 = folder.FindObject('DT_Oak_CR')
	      ch90.Add(h90)
	      h90a = folder.FindObject('DT_Oak_corr_CR')
	      ch90a.Add(h90a)
	      h91 = folder.FindObject('Berk_CR')
	      ch91.Add(h91)
	      h91a = folder.FindObject('Berk_corr_CR')
	      ch91a.Add(h91a)
	      h92 = folder.FindObject('Bridge_CR')
	      ch92.Add(h92)
	      h92a = folder.FindObject('Bridge_corr_CR')
	      ch92a.Add(h92a)
	      h93 = folder.FindObject('Farm_CR')
	      ch93.Add(h93)
	      h93a = folder.FindObject('Farm_corr_CR')
	      ch93a.Add(h93a)
	      h94 = folder.FindObject('Hwy_CR')
	      ch94.Add(h94)
	      h94a = folder.FindObject('Hwy_corr_CR')
	      ch94a.Add(h94a)
	    if k.GetTitle() == '2D_Hists':
	      folder = fin.Get(k.GetTitle())
	      h1_2d = folder.FindObject('alt_press_events')
	      ch1_2d.Add(h1_2d)
	      h2_2d = folder.FindObject('alt_press_time')
	      ch2_2d.Add(h2_2d)
	      h4_2d = folder.FindObject('alt_temp_events')
	      ch4_2d.Add(h4_2d)
	      h5_2d = folder.FindObject('alt_temp_time')
	      ch5_2d.Add(h5_2d)
	      h7_2d = folder.FindObject('alt_hum_events')
	      ch7_2d.Add(h7_2d)
	      h8_2d = folder.FindObject('alt_hum_time')
	      ch8_2d.Add(h8_2d)
	      h10_2d = folder.FindObject('alt_dew_events')
	      ch10_2d.Add(h10_2d)
	      h11_2d = folder.FindObject('alt_dew_time')
	      ch11_2d.Add(h11_2d)
	      h13_2d = folder.FindObject('alt_airdens_events')
	      ch13_2d.Add(h13_2d)
	      h14_2d = folder.FindObject('alt_airdens_time')
	      ch14_2d.Add(h14_2d)
	      h16_2d = folder.FindObject('alt_geomag_events')
	      ch16_2d.Add(h16_2d)
	      h17_2d = folder.FindObject('alt_geomag_time')
	      ch17_2d.Add(h17_2d)
	      h19_2d = folder.FindObject('press_outdens_events')
	      ch19_2d.Add(h19_2d)
	      h20_2d = folder.FindObject('press_outdens_time')
	      ch20_2d.Add(h20_2d)
	      h22_2d = folder.FindObject('alt_outdens_events')
	      ch22_2d.Add(h22_2d)
	      h23_2d = folder.FindObject('alt_outdens_time')
	      ch23_2d.Add(h23_2d)
	      h25_2d = folder.FindObject('outdens_airdens_events')
	      ch25_2d.Add(h25_2d)
	      h26_2d = folder.FindObject('outdens_airdens_time')
	      ch26_2d.Add(h26_2d)
	      h28_2d = folder.FindObject('time_geomag_events')
	      ch28_2d.Add(h28_2d)
	      h29_2d = folder.FindObject('time_geomag_time')
	      ch29_2d.Add(h29_2d)
	      h31_2d = folder.FindObject('press_hum_events')
	      ch31_2d.Add(h31_2d)
	      h32_2d = folder.FindObject('press_hum_time')
	      ch32_2d.Add(h32_2d)
	    if k.GetTitle() == 'CR_Freq_Plots':
	      folder = fin.Get(k.GetTitle())
	      h35_2d = folder.FindObject('press_CR_freq')
	      ch35_2d.Add(h35_2d)
	      h35a_2d = folder.FindObject('adj_press_CR_freq')
	      ch35a_2d.Add(h35a_2d)
	      h36_2d = folder.FindObject('temp_CR_freq')
	      ch36_2d.Add(h36_2d)
	      h36a_2d = folder.FindObject('adj_temp_CR_freq')
	      ch36a_2d.Add(h36a_2d)
	      h37_2d = folder.FindObject('hum_CR_freq')
	      ch37_2d.Add(h37_2d)
	      h37a_2d = folder.FindObject('adj_hum_CR_freq')
	      ch37a_2d.Add(h37a_2d)
	      h38_2d = folder.FindObject('kp_CR_freq')
	      ch38_2d.Add(h38_2d)
	      h38a_2d = folder.FindObject('adj_kp_CR_freq')
	      ch38a_2d.Add(h38a_2d)
	    '''if k.GetTitle() == '3D_Hists':
	      folder = fin.Get(k.GetTitle())
	      h1_3d = folder.FindObject('alt_press_hum_events')
	      ch1_3d.Add(h1_3d)
	      h2_3d = folder.FindObject('alt_press_hum_time') #change to alt_press_hum_time
	      ch2_3d.Add(h2_3d)'''
	    '''
	    if k.GetTitle() == '1D_Graphs':
	      folder = fin.Get(k.GetTitle())
	      ap = folder.FindObject('alt_v_press')
	      try:
	        altvpress.Add(ap)
	      except TypeError:
	        print 'No Weather for this File'
	        weather = False
	      if weather:
	        altvpress.Add(ap,"p")
	        ad = folder.FindObject('air_densities')  
	        airdensity.Add(ad,"p")
	        ao = folder.FindObject('alt_v_outdens')
	        altvoutdens.Add(ao,"p")
	        tp = folder.FindObject('time_v_press')
	        timevpress.Add(tp,"l")
	        th = folder.FindObject('time_v_hum')
	        timevhum.Add(th,"l")
	      tg = folder.FindObject('time_v_geomag')
	      dayvgeo.Add(tg,"p")'''
  weather = True
  fin.Close()


# change root directory back to new .root file location
root_out.cd()

# set all time bin errors to zero!
for x in range(0,n_bins+1):
  ch2.SetBinError(x,0.)
  for y in range(0,press_bins+1):
    ch2_2d.SetBinError(x,y,0.)
  for y in range(0,temp_bins+1):
    ch5_2d.SetBinError(x,y,0.)
  for y in range(0,hum_bins+1):
    ch8_2d.SetBinError(x,y,0.)
  for y in range(0,int(dew_bins)+1):
    ch11_2d.SetBinError(x,y,0.)
  for y in range(0,int(airdens_bins)+1):
    ch14_2d.SetBinError(x,y,0.)
    ch23_2d.SetBinError(x,y,0.)
  for y in range(0,geo_bins+1):
    ch17_2d.SetBinError(x,y,0.)
for x in range(0,press_bins+1):
  ch5.SetBinError(x,0.)
  for y in range(0,int(airdens_bins)+1):
    ch20_2d.SetBinError(x,y,0.)
  for y in range(0,hum_bins+1):
    ch32_2d.SetBinError(x,y,0)
for x in range(0,temp_bins+1):
  ch8.SetBinError(x,0.)
for x in range(0,hum_bins+1):
  ch11.SetBinError(x,0.)
for x in range(0,int(dew_bins)+1):
  ch18.SetBinError(x,0.)
for x in range(0,int(airdens_bins)+1):
  ch21.SetBinError(x,0.)
  ch33.SetBinError(x,0.)
  for y in range(0,int(airdens_bins)+1):
    ch26_2d.SetBinError(x,y,0.)
for x in range(0,Kp_bins+1):
  ch24.SetBinError(x,0.)
for x in range(0,geo_bins+1):
  ch27.SetBinError(x,0.)
for x in range(0,daytime_bins+1):
  ch30.SetBinError(x,0.)
  for y in range(0,geo_bins+1):
    ch29_2d.SetBinError(x,y,0)

# alt
ch3 = ch1.Clone()
ch3.SetTitle("Combined Count Rate at Altitude")
ch3.SetName("alt_count_rate")
ch3.Divide(ch2)
ch3.GetXaxis().SetTitle("Altitude (m)")
ch3.GetYaxis().SetTitle("Count Rate (CPS)")
allhists.append(ch3)
#
ch3a = ch1a.Clone()
ch3a.SetTitle("Combined Count Rate at Altitude")
ch3a.SetName("corr_alt_count_rate")
ch3a.Divide(ch2)
ch3a.GetXaxis().SetTitle("Altitude (m)")
ch3a.GetYaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
#
# pressure
ch6 = ch4.Clone()
ch6.SetTitle("Count Rate at Pressure")
ch6.SetName("press_count_rate")
ch6.Divide(ch5)
ch6.GetXaxis().SetTitle("Pressure (mbar)")
ch6.GetYaxis().SetTitle("Count Rate (CPS)")
allhists.append(ch6)
#
ch6a = ch4a.Clone()
ch6a.SetTitle("Count Rate at Pressure")
ch6a.SetName("corr_press_count_rate")
ch6a.Divide(ch5)
ch6a.GetXaxis().SetTitle("Pressure (mbar)")
ch6a.GetYaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
#
# temp
ch9 = ch7.Clone()
ch9.SetTitle("Count Rate at Temperature")
ch9.SetName("temp_count_rate")
ch9.Divide(ch8)
ch9.GetXaxis().SetTitle("Temperature (F)")
ch9.GetYaxis().SetTitle("Count Rate (CPS)")
allhists.append(ch9)
#
ch9a = ch7a.Clone()
ch9a.SetTitle("Count Rate at Temperature")
ch9a.SetName("corr_temp_count_rate")
ch9a.Divide(ch8)
ch9a.GetXaxis().SetTitle("Temperature (F)")
ch9a.GetYaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
#
# hum
ch12 = ch10.Clone()
ch12.SetTitle("Count Rate at Humidity")
ch12.SetName("hum_count_rate")
ch12.Divide(ch11)
ch12.GetXaxis().SetTitle("Absolute Humidity (g/m^3)")
ch12.GetYaxis().SetTitle("Count Rate (CPS)")
allhists.append(ch12)
#
ch12a = ch10a.Clone()
ch12a.SetTitle("Count Rate at Humidity")
ch12a.SetName("corr_hum_count_rate")
ch12a.Divide(ch11)
ch12a.GetXaxis().SetTitle("Absolute Humidity (g/m^3)")
ch12a.GetYaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
#
# dew
ch19 = ch17.Clone()
ch19.SetTitle("Count Rate at Dew Point")
ch19.SetName("dew_count_rate")
ch19.Divide(ch18)
ch19.GetXaxis().SetTitle("Dew Point (F)")
ch19.GetYaxis().SetTitle("Count Rate (CPS)")
#
ch19a = ch17a.Clone()
ch19a.SetTitle("Count Rate at Dew Point")
ch19a.SetName("corr_dew_count_rate")
ch19a.Divide(ch18)
ch19a.GetXaxis().SetTitle("Dew Point (F)")
ch19a.GetYaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
# air density
ch22 = ch20.Clone()
ch22.SetTitle("Count Rate at Air Density")
ch22.SetName("airdens_count_rate")
ch22.Divide(ch21)
ch22.GetXaxis().SetTitle("Inside Air Density (kg/m^3)")
ch22.GetYaxis().SetTitle("Count Rate (CPS)")
#
ch22a = ch20a.Clone()
ch22a.SetTitle("Count Rate at Air Density")
ch22a.SetName("corr_airdens_count_rate")
ch22a.Divide(ch21)
ch22a.GetXaxis().SetTitle("Inside Air Density (kg/m^3)")
ch22a.GetYaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
# Kp value
ch25 = ch23.Clone()
ch25.SetTitle("Count Rate at Kp Value")
ch25.SetName("Kp_count_rate")
ch25.Divide(ch24)
ch25.GetXaxis().SetTitle("Kp Value")
ch25.GetYaxis().SetTitle("Count Rate (CPS)")
#
ch25a = ch23a.Clone()
ch25a.SetTitle("Count Rate at Kp Value")
ch25a.SetName("corr_Kp_count_rate")
ch25a.Divide(ch24)
ch25a.GetXaxis().SetTitle("Kp Value")
ch25a.GetYaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
# FRN geomag field value
ch28 = ch26.Clone()
ch28.SetTitle("Count Rate Given Hourly Geomagnetic Field Strength Change")
ch28.SetName("Geomag_count_rate")
ch28.Divide(ch27)
ch28.GetXaxis().SetTitle("Hourly Change (nT)")
ch28.GetYaxis().SetTitle("Count Rate (CPS)")
#
ch28a = ch26a.Clone()
ch28a.SetTitle("Count Rate Given Hourly Geomagnetic Field Strength Change")
ch28a.SetName("corr_Geomag_count_rate")
ch28a.Divide(ch27)
ch28a.GetXaxis().SetTitle("Hourly Change (nT)")
ch28a.GetYaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")
# time of day
ch31 = ch29.Clone()
ch31.SetTitle("Count Rate Given Time of Day")
ch31.SetName("daytime_count_rate")
ch31.Divide(ch30)
ch31.GetXaxis().SetTitle("Time of Day (hr)")
ch31.GetYaxis().SetTitle("Count Rate (CPS)")
# air density
ch34 = ch32.Clone()
ch34.SetTitle("Count Rate Given Air Density")
ch34.SetName("outdens_count_rate")
ch34.Divide(ch33)
ch34.GetXaxis().SetTitle("Outside Air Density (kg/m^3)")
ch34.GetYaxis().SetTitle("Count Rate (CPS)")
#
ch34a = ch32a.Clone()
ch34a.SetTitle("Count Rate Given Air Density")
ch34a.SetName("corr_outdens_count_rate")
ch34a.Divide(ch33)
ch34a.GetXaxis().SetTitle("Outside Air Density (kg/m^3)")
ch34a.GetYaxis().SetTitle("Pressure Adjusted Count Rate (CPS)")

#2D
ch3_2d = ch1_2d.Clone()
ch3_2d.SetTitle("Count Rate Given Altitude and Pressure")
ch3_2d.SetName("alt_press_count_rate")
ch3_2d.Divide(ch2_2d)
ch3_2d.GetXaxis().SetTitle("Altitude (m)")
ch3_2d.GetXaxis().SetTitleOffset(2)
ch3_2d.GetYaxis().SetTitle("Pressure (mbar)")
ch3_2d.GetYaxis().SetTitleOffset(2)
ch3_2d.GetZaxis().SetTitle("Count Rate (CPS)")
ch3_2d.GetZaxis().SetTitleOffset(1.25)
#
ch6_2d = ch4_2d.Clone()
ch6_2d.SetTitle("Count Rate Given Altitude and Temperature")
ch6_2d.SetName("alt_temp_count_rate")
ch6_2d.Divide(ch5_2d)
ch6_2d.GetXaxis().SetTitle("Altitude (m)")
ch6_2d.GetXaxis().SetTitleOffset(2)
ch6_2d.GetYaxis().SetTitle("Temperature (F)")
ch6_2d.GetYaxis().SetTitleOffset(2)
ch6_2d.GetZaxis().SetTitle("Count Rate (CPS)")
ch6_2d.GetZaxis().SetTitleOffset(1.25)
#
ch9_2d = ch7_2d.Clone()
ch9_2d.SetTitle("Count Rate Given Altitude and Humidity")
ch9_2d.SetName("alt_hum_count_rate")
ch9_2d.Divide(ch8_2d)
ch9_2d.GetXaxis().SetTitle("Altitude (m)")
ch9_2d.GetXaxis().SetTitleOffset(2)
ch9_2d.GetYaxis().SetTitle("Absolute Humidity (g/m^3)")
ch9_2d.GetYaxis().SetTitleOffset(2)
ch9_2d.GetZaxis().SetTitle("Count Rate (CPS)")
ch9_2d.GetZaxis().SetTitleOffset(1.25)
#
ch12_2d = ch10_2d.Clone()
ch12_2d.SetTitle("Count Rate Given Altitude and Dew Point")
ch12_2d.SetName("alt_dew_count_rate")
ch12_2d.Divide(ch11_2d)
ch12_2d.GetXaxis().SetTitle("Altitude (m)")
ch12_2d.GetXaxis().SetTitleOffset(2)
ch12_2d.GetYaxis().SetTitle("Dew Point (F)")
ch12_2d.GetYaxis().SetTitleOffset(2)
ch12_2d.GetZaxis().SetTitle("Count Rate (CPS)")
ch12_2d.GetZaxis().SetTitleOffset(1.25)
#
ch15_2d = ch13_2d.Clone()
ch15_2d.SetTitle("Count Rate Given Altitude and Air Density")
ch15_2d.SetName("alt_airdens_count_rate")
ch15_2d.Divide(ch14_2d)
ch15_2d.GetXaxis().SetTitle("Altitude (m)")
ch15_2d.GetXaxis().SetTitleOffset(2)
ch15_2d.GetYaxis().SetTitle("Inside Air Density (kg/m^3)")
ch15_2d.GetYaxis().SetTitleOffset(2)
ch15_2d.GetZaxis().SetTitle("Count Rate (CPS)")
ch15_2d.GetZaxis().SetTitleOffset(1.25)
#
ch18_2d = ch16_2d.Clone()
ch18_2d.SetTitle("Count Rate Given Altitude and Geomagnetic Field Strength Change")
ch18_2d.SetName("alt_geomag_count_rate")
ch18_2d.Divide(ch17_2d)
ch18_2d.GetXaxis().SetTitle("Altitude (m)")
ch18_2d.GetXaxis().SetTitleOffset(2)
ch18_2d.GetYaxis().SetTitle("Hourly Change (nT)")
ch18_2d.GetYaxis().SetTitleOffset(2)
ch18_2d.GetZaxis().SetTitle("Count Rate (CPS)")
ch18_2d.GetZaxis().SetTitleOffset(1.25)
#
ch21_2d = ch19_2d.Clone()
ch21_2d.SetTitle("Count Rate Given Pressure and Outside Air Density")
ch21_2d.SetName("press_outdens_count_rate")
ch21_2d.Divide(ch20_2d)
ch21_2d.GetXaxis().SetTitle("Pressure (mbar)")
ch21_2d.GetXaxis().SetTitleOffset(2)
ch21_2d.GetYaxis().SetTitle("Outside Air Density (kg/m^3)")
ch21_2d.GetYaxis().SetTitleOffset(2)
ch21_2d.GetZaxis().SetTitle("Count Rate (CPS)")
ch21_2d.GetZaxis().SetTitleOffset(1.25)
#
ch24_2d = ch22_2d.Clone()
ch24_2d.SetTitle("Count Rate Given Altitude and Air Density")
ch24_2d.SetName("alt_outdens_count_rate")
ch24_2d.Divide(ch23_2d)
ch24_2d.GetXaxis().SetTitle("Altitude (m)")
ch24_2d.GetXaxis().SetTitleOffset(1.5)
ch24_2d.GetYaxis().SetTitle("Outside Air Density (kg/m^3)")
ch24_2d.GetYaxis().SetTitleOffset(1.5)
ch24_2d.GetZaxis().SetTitle("Count Rate (CPS)")
ch24_2d.GetZaxis().SetTitleOffset(1.25)
#
ch27_2d = ch25_2d.Clone()
ch27_2d.SetTitle("Count Rate Given Inside and Outside Air Density")
ch27_2d.SetName("outdens_airdens_count_rate")
ch27_2d.Divide(ch26_2d)
ch27_2d.GetXaxis().SetTitle("Outside Air Density (kg/m^3)")
ch27_2d.GetXaxis().SetTitleOffset(1.5)
ch27_2d.GetYaxis().SetTitle("Inside Air Density (kg/m^3)")
ch27_2d.GetYaxis().SetTitleOffset(1.5)
ch27_2d.GetZaxis().SetTitle("Count Rate (CPS)")
ch27_2d.GetZaxis().SetTitleOffset(1.25)
#
ch30_2d = ch28_2d.Clone()
ch30_2d.SetTitle("Count Rate Given Time of Day and Geomagnetic Field Strength Change")
ch30_2d.SetName("time_geomag_count_rate")
ch30_2d.Divide(ch29_2d)
ch30_2d.GetXaxis().SetTitle("Time of Day (hr)")
ch30_2d.GetXaxis().SetTitleOffset(1.5)
ch30_2d.GetYaxis().SetTitle("Hourly Change (nT)")
ch30_2d.GetYaxis().SetTitleOffset(1.5)
ch30_2d.GetZaxis().SetTitle("Count Rate (CPS)")
ch30_2d.GetZaxis().SetTitleOffset(1.25)
#
ch33_2d = ch31_2d.Clone()
ch33_2d.SetTitle("Count Rate Given Pressure and Absolute Humidity")
ch33_2d.SetName("press_hum_count_rate")
ch33_2d.Divide(ch32_2d)
ch33_2d.GetXaxis().SetTitle("Pressure (mbar)")
ch33_2d.GetXaxis().SetTitleOffset(1.5)
ch33_2d.GetYaxis().SetTitle("Absolute Humidity (g/m^3)")
ch33_2d.GetYaxis().SetTitleOffset(1.5)
ch33_2d.GetZaxis().SetTitle("Count Rate (CPS)")
ch33_2d.GetZaxis().SetTitleOffset(1.25)
# 3D
ch3_3d = ch1_3d.Clone()
ch3_3d.SetTitle("Neutron Count Rate Given Altitude, Pressure and Humidity")
ch3_3d.SetName("alt_press_hum_time_count_rate")
ch3_3d.Divide(ch2_3d)
ch3_3d.GetXaxis().SetTitle("Altitude (m)")
ch3_3d.GetXaxis().SetTitleOffset(1.5)
ch3_3d.GetYaxis().SetTitle("Pressure (mbar)")
ch3_3d.GetYaxis().SetTitleOffset(1.5)
ch3_3d.GetZaxis().SetTitle("Absolute Humidity (g/m^3)")
ch3_3d.GetZaxis().SetTitleOffset(1.5)
###FIX labels
ch100_2d.GetXaxis().LabelsOption("v")
ch100_2d.GetYaxis().CenterTitle()
ch100a_2d.GetXaxis().LabelsOption("v")
ch100a_2d.GetYaxis().CenterTitle()
ch100.GetXaxis().LabelsOption("v")
ch100.GetYaxis().CenterTitle()
ch100a.GetXaxis().LabelsOption("v")
ch100a.GetYaxis().CenterTitle()

# append rest of hists to array
allhists.append(ch15)
allhists.append(ch1a)
allhists.append(ch3a)
allhists.append(ch4a)
allhists.append(ch6a)
allhists.append(ch7a)
allhists.append(ch9a)
allhists.append(ch10a)
allhists.append(ch12a)
allhists.append(ch15a) #21
allhists.append(ch17)
allhists.append(ch17a)
allhists.append(ch18)
allhists.append(ch19)
allhists.append(ch19a)
allhists.append(ch20)
allhists.append(ch20a)
allhists.append(ch21)
allhists.append(ch22)
allhists.append(ch22a)
allhists.append(ch23)
allhists.append(ch23a)
allhists.append(ch24)
allhists.append(ch25)
allhists.append(ch25a)
allhists.append(ch26)
allhists.append(ch26a)
allhists.append(ch27)
allhists.append(ch28)
allhists.append(ch28a)
allhists.append(ch29)
allhists.append(ch30)
allhists.append(ch31)
allhists.append(ch32)
allhists.append(ch33)
allhists.append(ch34)
allhists.append(ch32a)
allhists.append(ch34a)

allhists.append(ch90)
allhists.append(ch90a)
allhists.append(ch91)
allhists.append(ch91a)
allhists.append(ch92)
allhists.append(ch92a)
allhists.append(ch93)
allhists.append(ch93a)
allhists.append(ch94)
allhists.append(ch94a)

allhists.append(ch3_3d) #60
allhists.append(ch1_3d)
allhists.append(ch2_3d)
allhists.append(ch3_2d) #63
allhists.append(ch6_2d)
allhists.append(ch9_2d)
allhists.append(ch12_2d)
allhists.append(ch15_2d)
allhists.append(ch18_2d)
allhists.append(ch21_2d)
allhists.append(ch24_2d)
allhists.append(ch27_2d)
allhists.append(ch30_2d)
allhists.append(ch33_2d)
allhists.append(ch1_2d)
allhists.append(ch2_2d)
allhists.append(ch4_2d)
allhists.append(ch5_2d)
allhists.append(ch7_2d)
allhists.append(ch8_2d)
allhists.append(ch10_2d)
allhists.append(ch11_2d)
allhists.append(ch13_2d)
allhists.append(ch14_2d)
allhists.append(ch16_2d)
allhists.append(ch17_2d)
allhists.append(ch19_2d)
allhists.append(ch20_2d)
allhists.append(ch22_2d)
allhists.append(ch23_2d)
allhists.append(ch25_2d)
allhists.append(ch26_2d)
allhists.append(ch28_2d)
allhists.append(ch29_2d)
allhists.append(ch31_2d)
allhists.append(ch32_2d) #95

#allhists.append(ch34_2d)
#allhists.append(ch34a_2d)
allhists.append(ch35_2d)  #96
allhists.append(ch35a_2d)
allhists.append(ch36_2d)
allhists.append(ch36a_2d)
allhists.append(ch37_2d)
allhists.append(ch37a_2d)
allhists.append(ch38_2d)
allhists.append(ch38a_2d)

# iterate over all hists to put in folders and center axis titles
# hist number order in allhists array:: 1,2,4,5,7,8,10,11,3,6,9,12,15, 1a, 3a, 4a,6a,7a,9a,10a,12a,15a)
for i in range(0,len(allhists)):
  allhists[i].SetDirectory(0)
  allhists[i].GetXaxis().CenterTitle()
  allhists[i].GetYaxis().CenterTitle()
  if i in (0,1,8,13,14):
    alt_fol.Add(allhists[i])
  if i in (2,3,9,15,16):
    press_fol.Add(allhists[i])
  if i in (4,5,10,17,18):
    temp_fol.Add(allhists[i])
  if i in (6,7,11,19,20):
    hum_fol.Add(allhists[i])
  if i in (12,21,42,43,44,50,51,52,53,54,55,56,57,58,59):
    time_fol.Add(allhists[i])
  if i in (22,23,24,25,26):
    dew_fol.Add(allhists[i])
  if i in (27,28,29,30,31,45,46,47,48,49):
    adens_fol.Add(allhists[i])
  if i in (32,33,34,35,36):
    Kp_fol.Add(allhists[i])
  if i in (37,38,39,40,41):
    GeoMag_fol.Add(allhists[i])
  if i >= 63 and i <= 95:
    TwoD_fol.Add(allhists[i])
  if i in (60,61,62):
    ThreeD_fol.Add(allhists[i])
  if i >= 96:
    CR_Freq_fol.Add(allhists[i])

'''
# make det hist into count rate
for i in range(0,16):
  dethistalt[i].SetDirectory(0)
  alt_fol.Add(dethistalt[i])
  dethistpress[i].Divide(ch5)
  dethistpress[i].SetDirectory(0)
  press_fol.Add(dethistpress[i])
  dethisttemp[i].Divide(ch8)
  dethisttemp[i].SetDirectory(0)
  temp_fol.Add(dethisttemp[i])
  dethisthum[i].Divide(ch11)
  dethisthum[i].SetDirectory(0)
  hum_fol.Add(dethisthum[i])
'''

'''
# open canvas and make TMultiGraphs look nice
c1 = TCanvas( 'c1', 'alt_v_press', 0, 0, 400, 400 )
altvpress.SetName("alt_v_press")
altvpress.SetTitle("Event Altitude and Pressure; Altitude (m); Pressure (mbar)")
altvpress.Draw("AP")
c1.Update()
#
c2 = TCanvas( 'c2', 'air_densities', 0, 0, 400, 400 )
airdensity.SetName("air_densities")
airdensity.SetTitle("Event Inside and Outside Air Density; Outside Air Density (kg/m^3); Inside Air Density (kg/m^3)")
airdensity.Draw("AP")
c2.Update()
#
c3 = TCanvas( 'c3', 'alt_v_outdens', 0, 0, 400, 400 )
altvoutdens.SetName("alt_v_outdens")
altvoutdens.SetTitle("Event Altitude and Outside Air Density; Altitude (m); Outside Air Density (kg/m^3)")
altvoutdens.Draw("AP")
c3.Update()
#
c4 = TCanvas( 'c4', 'time_v_press', 0, 0, 400, 400 )
timevpress.SetName("time_v_press")
timevpress.SetTitle("Pressure at Time of Day; Time of Day (hr); Pressure (mbar)")
timevpress.Draw("AP")
c4.Update()
#
c5 = TCanvas( 'c5', 'time_v_hum', 0, 0, 400, 400 )
timevhum.SetName("time_v_hum")
timevhum.SetTitle("Humidity at Time of Day; Time of Day (hr); Absolute Humidity (g/m^3)")
timevhum.Draw("AP")
c5.Update()
#
c6 = TCanvas( 'c6', 'time_v_geomag', 0, 0, 400, 400 )
dayvgeo.SetName("time_v_geomag")
dayvgeo.SetTitle("Hourly Geomagnetic Field Strength Change at Time of Day; Time of Day (hr); Hourly Change (nT)")
dayvgeo.Draw("AP")
c6.Update()
# add TGraphs to folders
OneD_fol.Add(altvpress)
OneD_fol.Add(airdensity)
OneD_fol.Add(altvoutdens)
OneD_fol.Add(timevpress)
OneD_fol.Add(timevhum)
OneD_fol.Add(dayvgeo)'''

#Get bin content of resulting hists
combined_cts = []
combined_time = []
combined_cr = []
cr_error = []

# print 'num bins:', ch1.GetNbinsX

for y in range(0,n_bins+1):
    combined_cts.append(ch1.GetBinContent(y))
    combined_time.append(ch2.GetBinContent(y))
    combined_cr.append(ch3.GetBinContent(y))
    cr_error.append(ch3.GetBinError(y))

comb_press = []
comb_press_time = []
comb_press_cr = []
comb_press_bins = []
press_error = []

#press_interval = (max_press-min_press)/float(press_bins)
#comb_press_bins = np.arange(min_press - press_interval, max_press + press_interval, press_interval)

for i in range(0,press_bins+1):
  comb_press_bins.append(ch6.GetXaxis().GetBinCenter(i))
  comb_press.append(ch4.GetBinContent(i))
  comb_press_time.append(ch5.GetBinContent(i))
  comb_press_cr.append(ch6.GetBinContent(i))
  press_error.append(ch6.GetBinError(i))

# print bin contents of combined hists and save to file
#print 'Altitude Bins: ',bin_alt
#print 'Combined Neutron Events: ',combined_cts
#print 'Combined Time: ',combined_time
#print 'Combined Count Rate: ',combined_cr

# file = open("/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/Converted/PyRootHists/Combined/Combined_Hists_Out7May14.txt", "w")
file = open("/home/john_davis/Desktop/Combined_Hists_Out.txt", "w")
file.write('Altitude Bins:\n {alt}\n\n'.format(alt = bin_alt))
file.write('Combined Neutron Events:\n {ev}\n\n'.format(ev = combined_cts))
file.write('Combined Time:\n {time}\n\n'.format(time = combined_time))
file.write('Combined Count Rate:\n {cr}\n\n'.format(cr = combined_cr))
file.write('Count Rate Errors:\n {err}\n\n'.format(err = cr_error))

file.write('Pressure Bins:\n {pressbin}\n\n'.format(pressbin = comb_press_bins))
file.write('Pressure Events:\n {pressev}\n\n'.format(pressev = comb_press))
file.write('Pressure Time:\n {presstime}\n\n'.format(presstime = comb_press_time))
file.write('Pressure Count Rate:\n {pressCR}\n\n'.format(pressCR = comb_press_cr))
file.write('Pressure Errors:\n {presserr}\n\n'.format(presserr = press_error))

# save file and close
'''c1.Write()
c2.Write()
c3.Write()
c4.Write()
c5.Write()
c6.Write()'''
alt_fol.Write()
press_fol.Write()
temp_fol.Write()
hum_fol.Write()
dew_fol.Write()
adens_fol.Write()
Kp_fol.Write()
GeoMag_fol.Write()
time_fol.Write()
TwoD_fol.Write()
ThreeD_fol.Write()
OneD_fol.Write()
CR_Freq_fol.Write()
root_out.Write()
root_out.Close()
print "done writing file..."
sys.exit()