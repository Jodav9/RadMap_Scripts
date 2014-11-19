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
Histsdir = '/home/john_davis/Desktop/Lidar_Analysis/New_Root/'

Hists_in = []
for (dirpath, dirnames, filenames) in walk(Histsdir):
    Hists_in.extend(filenames)
    break 
#print Hists_in

#create root file and tree
root_out = ROOT.TFile(str(sys.argv[1]), "recreate")

angle_bins = 36
min_angle = 0
max_angle = 180

# Open Angle hist
ch_oa1 = TH1D("openangle_events","Neutron Event Open Angles",angle_bins,min_angle,max_angle);
ch_oa1.GetXaxis().SetTitle("Open Angle (degrees)")
ch_oa1.GetYaxis().SetTitle("Counts")
ch_oa1.Sumw2()
# press adj
ch_oa1a = TH1D("press_corr_openangle_events","Neutron Event Open Angles",angle_bins,min_angle,max_angle);
ch_oa1a.GetXaxis().SetTitle("Open Angle (degrees)")
ch_oa1a.GetYaxis().SetTitle("Counts")
ch_oa1a.Sumw2()
#
ch_oa2 = TH1D("openangle_time","Neutron Time at Open Angle",angle_bins,min_angle,max_angle);
ch_oa2.GetXaxis().SetTitle("Open Angle (degrees)")
ch_oa2.GetYaxis().SetTitle("Time (s)")

print "Adding Hists..."
# main loop
for i in range(0,len(Hists_in)):
  weather = True
  Histnum = i
  print str(i+1)+".",Hists_in[i]
  fin = ROOT.TFile(Histsdir+Hists_in[i])
  keylist = fin.GetListOfKeys()
  for i,m in enumerate(keylist):
  	if m.GetName() == 'openangle_events':
  		oa1 = fin.Get(m.GetName())
  		#oa1 = hist.FindObject('openangle_events')
  		ch_oa1.Add(oa1)
  	if m.GetName() == 'press_corr_openangle_events':
  		oa1a = fin.Get(m.GetName())
  		#oa1a = hist.FindObject('press_corr_openangle_events')
  		ch_oa1a.Add(oa1a)
  	if m.GetName() == 'openangle_time':
  		oa2 = fin.Get(m.GetName())
  		#oa2 = hist.FindObject('openangle_time')
		ch_oa2.Add(oa2)

# change root directory back to new .root file location
root_out.cd()

# set all time bin errors to zero!
for x in range(0,angle_bins+1):
  oa2.SetBinError(x,0.)

# CR hist
ch_oa3 = ch_oa1.Clone()
ch_oa3.SetTitle("Combined Count Rate Given Open Angle")
ch_oa3.SetName("openangle_count_rate")
ch_oa3.Divide(ch_oa2)
ch_oa3.GetXaxis().SetTitle("Open Angle (degrees)")
ch_oa3.GetYaxis().SetTitle("Count Rate (CPS)")
# Corr CR hist
ch_oa3a = ch_oa1a.Clone()
ch_oa3a.SetTitle("Combined Pressure Adjusted Count Rate Given Open Angle")
ch_oa3a.SetName("press_corr_openangle_count_rate")
ch_oa3a.Divide(ch_oa2)
ch_oa3a.GetXaxis().SetTitle("Open Angle (degrees)")
ch_oa3a.GetYaxis().SetTitle("Count Rate (CPS)")

root_out.Write()
root_out.Close()
print "done writing file..."
sys.exit()