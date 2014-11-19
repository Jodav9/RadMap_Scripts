import os
import sys
import os.path

from ROOT import gSystem, TTree, TFile, TH1F, TGraph, TCanvas, gStyle
gSystem.Load('/home/john_davis/Desktop/RadMAP_TopLevel/MISTI/src/libMISTI')
from ROOT import MISTIEvent
import operator
'''import curses
stdscr = curses.initscr()

curses.noecho()
curses.cbreak()
stdscr.keypad(True)'''

# Load the root file
inF = TFile(str(sys.argv[1]))
inT = inF.Get('MISTI_LS')

infile = str(sys.argv[1])

print 'input root file:',sys.argv[1]
#print 'input text file:',sys.argv[2]
#print 'output file:',sys.argv[2]
######

Event = MISTIEvent()
inT.SetBranchAddress('Event', Event)

# n_start_event is neutron event number from sorted .txt files
def GetPulses(PSD_min,PSD_max,min_amp,max_amp,SatPulseReject=False,NeutronsOnly=False,sortedtxt=False,n_start_event=0,start_time=0,Ch='ALL'):
  print PSD_min,PSD_max,min_amp,max_amp,SatPulseReject,NeutronsOnly,sortedtxt,n_start_event,start_time,Ch

  if SatPulseReject:
    max_raw_amp = 4010
  if not SatPulseReject:
    max_raw_amp = 5000
  if NeutronsOnly:
    min_n_llr = 6.9
  if not NeutronsOnly:
    min_n_llr = -1000
  if (Ch == 'ALL'):
    channels = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
  if (type(Ch)==int):
    channels = [Ch]

  c1 = TCanvas( 'c1', 'Raw Pulse Data', 0, 0, 600, 650 )
  c1.Divide(1,2)

  n_events = inT.GetEntries()
  print "Number of events: ",n_events

  if sortedtxt:
    # create array of root file event numbers following the first designated neutron event
    event_order = []
    for i in range(n_start_event,len(n_event)):
      event_order.append(int(n_event[i].split(',')[6]))

  if type(start_time)==str:
    print 'start time is str'
    start_time = float(start_time)

  if start_time > 0:
    inT.GetEntry(0)
    runstart = Event.epoch_time()
    inT.GetEntry(n_events-1)
    runend = Event.epoch_time()
    # determine new start event based on location of desired start event (assumes constant event rate so we subtract 3000000 events to undershoot)
    start_event = int(((start_time-runstart)/(runend-runstart))*n_events)-3000000
    print 'Searching from event number ',start_event
    print 'Looking for first pulse...'
    for ent in range(start_event, n_events):
      inT.GetEntry(ent)
      if(ent % (n_events/100) == 0):
        print '%d / %d' % (ent, n_events)
      if Event.epoch_time() >= start_time:
        start_event = ent
        print 'Pulses starting at event number ',start_event
        break

  if start_time == 0:
    start_event = 0

  if sortedtxt:
    for i in range(0,len(event_order)):
      ent = event_order[i]
      print ent
      inT.GetEntry(ent)
      c1.cd(1)
      g = TGraph(Event.GetGraph())
      g.SetTitle("Raw Pulse - Event "+str(ent)+" - Time - "+str(Event.epoch_time())+" - Detector ch "+str(Event.channel())+" - Integral: "+str('%.2f' % Event.amplitude())+" - PSD Value: "+str('%.2f' % Event.PSD()))
      g.GetXaxis().SetTitle("Sample")
      g.GetYaxis().SetTitle("Value")
      g.GetYaxis().SetRangeUser(-100,5000)
      g.Draw("AL")
      c1.Update()
      # Get Graph Integral:
      c1.cd(2)
      h = TGraph(Event.GetGraphCum())
      h.SetTitle("Pulse Integral")
      h.GetXaxis().SetTitle("Sample")
      h.GetYaxis().SetTitle("Value")
  #    h.GetYaxis().SetRangeUser(-1000,35000)
      h.Draw("AL")
      c1.Update()
      opt = raw_input("Press Enter to continue or q to quit: ")
      if (opt == 'q'):
        sys.exit(0)

  if not sortedtxt:
    for ent in range(start_event, n_events):
      inT.GetEntry(ent)
      if(ent % (n_events/100) == 0):
        print '%d / %d' % (ent, n_events)
      if(Event.llr_n() >= min_n_llr and Event.rawamplitude() < max_raw_amp and max_amp > Event.amplitude() > min_amp and Event.channel() in channels and PSD_min <= Event.PSD() <= PSD_max ):
        # Get Graph:
        if(Event.llr_n() >= 6.9):
          print "NEUTRON"
        c1.cd(1)
        g = TGraph(Event.GetGraph())
        g.SetTitle("Raw Pulse - Event "+str(ent)+" - Time - "+str(Event.epoch_time())+" - Detector ch "+str(Event.channel())+" - Integral: "+str('%.2f' % Event.amplitude())+" - PSD Value: "+str('%.2f' % Event.PSD()))
        g.GetXaxis().SetTitle("Sample")
        g.GetYaxis().SetTitle("Value")
        g.GetYaxis().SetRangeUser(-100,5000)
        g.Draw("AL")
        c1.Update()
        # Get Graph Integral:
        c1.cd(2)
        h = TGraph(Event.GetGraphCum())
        h.SetTitle("Pulse Integral")
        h.GetXaxis().SetTitle("Sample")
        h.GetYaxis().SetTitle("Value")
    #    h.GetYaxis().SetRangeUser(-1000,35000)
        h.Draw("AL")
        c1.Update()
        opt = raw_input("Press Enter to continue or q to quit: ")
        if (opt == 'q'):
          sys.exit(0)
   #     raw_input("Continue?")
    #    if (key == 13): #enter
     #     continue

'''
key = ''
while key != ord('q'):
    key = stdscr.getch()'''


usetxt = raw_input("Use sorted text file? (Y/N): ")
if usetxt == 'Y' or usetxt == 'y':
  txtin = raw_input("'Paste Filenames' of sorted event text file: ")
  txtfile = open(txtin[1:-2], "r")
  print "opening ",txtin
  n_event = txtfile.readlines()
  ####
  sortedtxt=True
  n_start = int(raw_input("Enter first neutron event number: "))
  GetPulses(0,0,0,0,SatPulseReject=True,NeutronsOnly=True,sortedtxt=True,n_start_event=n_start,start_time=0,Ch='ALL')
  inF.Close()
  txtfile.close()
  sys.exit()
elif usetxt == 'N' or usetxt == 'n':
  sortedtxt=False
  ns_only1 = raw_input("Would you like to see only neutron events? (Y/N): ")
  if ns_only1 == 'Y' or ns_only1 == 'y':
    ns_only = True
  elif ns_only1 == 'N' or ns_only1 == 'n':
    ns_only = False
  else:
    print ns_only1,"is not a valid option -- try again"
    sys.exit()
####
  st_time1 = raw_input("Would you like to enter a start time? (Y/N): ")
  if st_time1 == 'Y' or st_time1 == 'y':
    st_time = '%.9f' % float(raw_input("Enter event start time (epoch time): "))
  else:
    st_time = 0
####
  satrej1 = raw_input("Would you like to reject saturated events? (Y/N): ")
  if satrej1 == 'Y' or satrej1 == 'y':
    satrej=True
  elif satrej1 == 'N' or satrej1 == 'n':
    satrej=False
  else:
    print satrej1,"is not a valid option -- try again"
    sys.exit()
####
  det_ch = raw_input("Would you like to specify a single channel? (Y/N): ")
  if det_ch == 'Y' or det_ch == 'y':
    Chan = int(raw_input("Specify channel number (0-15): "))
  elif det_ch == 'N' or det_ch == 'n':
    Chan ='ALL'
  else:
    print det_ch,"is not a valid option -- try again"
    sys.exit()
####
  PSD_min = float(raw_input("Specify min PSD value: "))
  PSD_max = float(raw_input("Specify max PSD value: "))
  min_amp = float(raw_input("Specify min pulse amplitude (cut at 6.5): "))
  max_amp = float(raw_input("Specify max pulse amplitude (2000 for all): "))
  GetPulses(PSD_min,PSD_max,min_amp,max_amp,SatPulseReject=satrej,NeutronsOnly=ns_only,sortedtxt=False,n_start_event=0,start_time=st_time,Ch=Chan)
  inF.Close()
  sys.exit()

else:
  print sortedtxt,"is not a valid option -- try again"
  sys.exit()



# GetPulses(PSD_min,PSD_max,min_amp,max_amp,SatPulseReject=False,NeutronsOnly=False,start_time=0,Ch='ALL'):
#GetPulses(0,1,6.5,2000,SatPulseReject=True,NeutronsOnly=True,start_time=1374613690.61,Ch='ALL')

#GetPulses(PSD_min,PSD_max,min_amp,max_amp,SatPulseReject=False,NeutronsOnly=False,sortedtxt=False,n_start_event=0,Ch='ALL'):
#GetPulses(0,1,6.5,2000,SatPulseReject=True,NeutronsOnly=True,sortedtxt=True,n_start_event=7747,Ch='ALL')



'''curses.nocbreak()
stdscr.keypad(False)
curses.echo()
curses.endwin()'''

'''
#reject saturated pulses??
sat_rej = raw_input("Reject Saturated Pulses? (Y/N): ")
if (sat_rej == 'Y' or sat_rej == 'y'):
  print "Reject Saturated Pulses"
  max_raw_amp = 4010
elif (sat_rej == 'N' or sat_rej == 'n'):
  print "No Pulse Rejection"

#neutrons only??? --- FIX TO BE TRUE / FALSE
n_only = raw_input("Neutrons Only? (Y/N): ")
if (n_only == 'Y' or n_only == 'y'):
  print "Neutron Pulses Only"
  min_n_llr = 6.9
  min_amp = 6.5
elif (n_only == 'N' or n_only == 'n'):
  print "Neutron and Gamma Pulses"

# PSD value range?
PSD_vals = raw_input("Would You Like to Specify PSD Value Range? (Y/N): ")
if (PSD_vals == 'Y' or PSD_vals == 'y'):
  PSD_min = float(raw_input("Specify Min PSD Value: "))
  PSD_max = float(raw_input("Specify Max PSD Value: "))
  print "min: ",PSD_min," max: ",PSD_max
elif (PSD_vals == 'N' or PSD_vals == 'n'):
  print "No PSD Range Specified"

# look at one detector only???

# look at other requirements?

chprob1 = 7
chprob2 = 13
'''

'''
c1 = TCanvas( 'c1', 'Raw Pulse Data', 0, 0, 600, 650 )
c1.Divide(1,2)

if n_events > inT.GetEntries():
  n_events = inT.GetEntries()

for ent in range(start_event, n_events):
#for ent in range(start_event, 10000):
#  if(ent % (n_events/100) == 0):
#    print '%d / %d' % (ent, n_events)
  inT.GetEntry(ent)
#  if(Event.bayes_prob_n() > min_n_prob and Event.rawamplitude() < 4000 and Event.amplitude() > 6.5 and Event.channel() != chprob1 and Event.channel() != chprob2):
  if(Event.llr_n() >= min_n_llr and Event.rawamplitude() < max_raw_amp and Event.amplitude() > min_amp and Event.channel() != chprob1 and Event.channel() != chprob2 and Event.PSD() >= PSD_min and Event.PSD() <= PSD_max):
    # Get Graph:
    if(Event.llr_n() >= 6.9):
      print "NEUTRON"
    c1.cd(1)
    g = TGraph(Event.GetGraph())
    g.SetTitle("Raw Pulse - Event "+str(ent)+" - Detector ch "+str(Event.channel())+" - Integral: "+str('%.2f' % Event.amplitude())+" - PSD Value: "+str('%.2f' % Event.PSD()))
    g.GetXaxis().SetTitle("Sample")
    g.GetYaxis().SetTitle("Value")
#    g.GetYaxis().SetRangeUser(-100,5000)
    g.Draw("AL")
    c1.Update()
    # Get Graph Integral:
    c1.cd(2)
    h = TGraph(Event.GetGraphCum())
    h.SetTitle("Pulse Integral")
    h.GetXaxis().SetTitle("Sample")
    h.GetYaxis().SetTitle("Value")
#    h.GetYaxis().SetRangeUser(-1000,35000)
    h.Draw("AL")
    c1.Update()
    opt = raw_input("Press Enter to continue or q to quit: ")
    if (opt == 'q'):
      sys.exit(0)
'''