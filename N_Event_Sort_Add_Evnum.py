import os
import sys
import os.path

from ROOT import gSystem, TTree, TFile, TH1F
gSystem.Load('/home/john_davis/Desktop/RadMAP_TopLevel/MISTI/src/libMISTI')
from ROOT import MISTIEvent
import operator

# Load the root file
inF = TFile(str(sys.argv[1]))
inT = inF.Get('MISTI_LS')

print 'input file:',sys.argv[1]
print 'output file:',str(sys.argv[1][:-5])+'_EV.txt'

Event = MISTIEvent()
inT.SetBranchAddress('Event', Event)

#Problem Channels ***** (chs 7 and 13 for old data to summer '13, ch 7 for new data (just eliminate both for analysis purposes) -- set to chprob to -1 if not needed)
chprob1 = 7
chprob2 = 13

# PARAMS
n_events = inT.GetEntries()
start_event = 0
min_n_prob = 0.999
min_n_llr = 6.9

inT.GetEntry(0)
beg_time = Event.epoch_time()

ncount = 0
neutron_events = []

if n_events > inT.GetEntries():
  n_events = inT.GetEntries()

for ent in range(start_event, n_events):
  if(ent % (n_events/100) == 0):
    print '%d / %d' % (ent, n_events)
  inT.GetEntry(ent)
#  if(Event.bayes_prob_n() > min_n_prob and Event.rawamplitude() < 4000 and Event.amplitude() > 6.5 and Event.channel() != chprob1 and Event.channel() != chprob2):
  if(Event.llr_n() >= min_n_llr and Event.rawamplitude() < 4010 and Event.amplitude() > 6.5 and Event.channel() != chprob1 and Event.channel() != chprob2):
    ncount+=1;
    neutron_events.append([Event.channel(),'%.9f' % Event.epoch_time(),ent])

sorted_events = sorted(neutron_events, key=lambda neutron_events: neutron_events[1]);

file = open(str(sys.argv[1][:-5])+'_EV.txt', "w")
for i in range(0, len(sorted_events)):
  file.write('{ev},{ch},{tme},{ev_num},\n'.format(ev=i,
							  ch=sorted_events[i][0],
							  tme=sorted_events[i][1],
                ev_num=sorted_events[i][2],))

print 'neutrons detected:';
print ncount;

sorted_events = []
inF.Close()
file.close()