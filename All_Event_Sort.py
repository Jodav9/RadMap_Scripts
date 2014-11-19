import os
import sys
import os.path
import fileinput

from ROOT import gSystem, TTree, TFile, TH1F
gSystem.Load('/home/john_davis/Desktop/RadMAP_TopLevel/MISTI/src/libMISTI')
from ROOT import MISTIEvent
import operator

# Load the root file
inF = TFile(str(sys.argv[1]))
inT = inF.Get('MISTI_LS')

infile = str(sys.argv[1])

print 'input file:',sys.argv[1]
print 'output file:',sys.argv[2]

######

# New GPS files location (to be used for all runs available)
newgpsdir = '/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/NewGPS/'

def FindNewGPS(infile):
  # assign gps file names
  year = infile[-18:-14]
  mo = infile[-24:-22]
  day = infile[-21:-19]
  gps_check = newgpsdir+year+mo+day+'.txt'
  # find if exists - True / False
  if os.path.isfile(gps_check):
    new_gps_avail = True
  else:
    new_gps_avail = False
  return new_gps_avail,gps_check;

######

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

altcorr = 30.5 # add 30.5 m to GPS altitude to correct old GPS

inT.GetEntry(0)
beg_time = Event.epoch_time()

beg_lat = Event.gps_lat()
beg_lon = Event.gps_long()
ncount = 0
all_events = []

if n_events > inT.GetEntries():
  n_events = inT.GetEntries()

# begin main loops (after new gps availability is determined)
new_gps_avail = FindNewGPS(infile)

file = open(str(sys.argv[2]), "w+") # w+ opens for reading and writing
event = file.readlines()

if not new_gps_avail[0]:
  for ent in range(start_event, n_events):
    if(ent % (n_events/100) == 0):
      print '%d / %d' % (ent, n_events)
    inT.GetEntry(ent)
    if(Event.rawamplitude() < 4010 and Event.amplitude() > 6.5 and Event.channel() != chprob1 and Event.channel() != chprob2):
      ncount+=1;
      #if Event.channel()==7:
      #  neutron_events.append([6,'%.9f' % Event.epoch_time(),Event.gps_lat(),Event.gps_long(),Event.gps_alt(),ent])
      #else:
      ch = Event.channel()
      time = float('%.9f' % Event.epoch_time())
      lat = Event.gps_lat()
      long = Event.gps_long()
      alt = Event.gps_alt()
      ev_alt = alt+altcorr

      #sorted_events = sorted(all_events, key=lambda all_events: all_events[1]);
      for line in fileinput.input(str(sys.argv[2]),inplace=1)




 '''     file.seek(0)
      if(len(event) == 0):
        file.write('{ev},{ch},{tme},{lat},{lon},{alt},{ev_num},\n'.format(ev=0,
                      ch=ch,
                      tme=time,
                      lat=lat,
                      lon=long,
                      alt='%.3f' % ev_alt,
                      ev_num=ent,))
      if(len(event) > 0):
        for i in range(0,len(event)):
          line_time = float(event[i].split(',')[2])
          if time <= line_time:
            file.write(event[i])
          else:
            file.write('{ev},{ch},{tme},{lat},{lon},{alt},{ev_num},\n'.format(ev=i,
                        ch=ch,
                        tme=time,
                        lat=lat,
                        lon=long,
                        alt='%.3f' % ev_alt,
                        ev_num=ent,))
            #now write remaining lines in after it
            for j in range(i,len(event)):
              file.write('{ev},{ch},{tme},{lat},{lon},{alt},{ev_num},\n'.format(ev=j+1,
                          ch=event[j].split(',')[1],
                          tme=event[j].split(',')[2],
                          lat=event[j].split(',')[3],
                          lon=event[j].split(',')[4],
                          alt=event[j].split(',')[5],
                          ev_num=event[j].split(',')[6],))
            break;'''

if new_gps_avail[0]:
  print 'Using New GPS\n','GPS file:',new_gps_avail[1]
  # read gps file and collect gps data
  gps_file = open(new_gps_avail[1],'r')
  gps_ev = gps_file.readlines()
  gpstime = []
  lat = []
  lon = []
  elev = []
  for i in range(0,len(gps_ev)):
    if (gps_ev[i][0].isdigit()):
        gpstime.append(float(gps_ev[i].split(' ')[0]))
        lat.append(float(gps_ev[i].split(' ')[2]))
        lon.append(float(gps_ev[i].split(' ')[3]))
        elev.append(float(gps_ev[i].split(' ')[4])+28.7)
  #####################
  #start loop
  idx = 0
  prev_ev_time = beg_time
  for ent in range(start_event, n_events):
    if(ent % (n_events/100) == 0):
      print '%d / %d' % (ent, n_events)
    inT.GetEntry(ent)
    if(Event.rawamplitude() < 4010 and Event.amplitude() > 6.5 and Event.channel() != chprob1 and Event.channel() != chprob2):
      ncount+=1;

      ev_time = Event.epoch_time()
      ev_ch = Event.channel()
      # if we are on the next buffer readout and isx is low, reset the start idx
      if (ent > 0 and ev_time < prev_ev_time and idx <= 1500):
        idx = 0;
      if (ent > 0 and ev_time < prev_ev_time and idx > 1500):
        idx = idx - 1500;
      # now check to see if we subtracted enough... if not, subtract more
      if (ent > 0 and ev_time < prev_ev_time and idx > 3000 and gpstime[idx] >= ev_time):
        idx = idx - 1500;
      # if all subtractions fail, restart at 0
      if (ent > 0 and ev_time < prev_ev_time and idx > 3000 and gpstime[idx] >= ev_time):
        idx = 0;
        print '********reset index to 0*************'
      for i in range(idx,len(gpstime)):
          # if truck is collecting data but GPS is not turned on yet, set the coordinate to the first GPS coordinate
          if (ev_time < gpstime[0]):
              all_events.append([Event.channel(),'%.9f' % Event.epoch_time(),lat[0],lon[0],'%.3f' % elev[0],ent]);
              break
          if (gpstime[i] >= ev_time):
              ev_alt = elev[i-1]+((ev_time-gpstime[i-1])/(gpstime[i]-gpstime[i-1]))*(elev[i]-elev[i-1])
              ev_lat = lat[i-1]+((ev_time-gpstime[i-1])/(gpstime[i]-gpstime[i-1]))*(lat[i]-lat[i-1])
              ev_lon = lon[i-1]+((ev_time-gpstime[i-1])/(gpstime[i]-gpstime[i-1]))*(lon[i]-lon[i-1])
              all_events.append([Event.channel(),'%.9f' % Event.epoch_time(),ev_lat,ev_lon,'%.3f' % ev_alt,ent]);
              break
          if(i == len(gpstime)-1):
              all_events.append([Event.channel(),'%.9f' % Event.epoch_time(),lat[i],lon[i],'%.3f' % elev[i],ent]);

      #print 'gpstime:',gpstime[i]
      #print 'evtime:',ev_time
      prev_ev_time = ev_time
      idx = i

  sorted_events = sorted(all_events, key=lambda all_events: all_events[1]);

  newGPStxt = str(sys.argv[2])[:-4]+'_NewGPS.txt'

  file = open(newGPStxt, "w")
  for i in range(0, len(sorted_events)):
    ev_alt = sorted_events[i][4]
    file.write('{ev},{ch},{tme},{lat},{lon},{alt},{ev_num},\n'.format(ev=i,
                  ch=sorted_events[i][0],
                  tme=sorted_events[i][1],
                  lat=sorted_events[i][2],
                  lon=sorted_events[i][3],
                  alt=sorted_events[i][4],
                  ev_num=sorted_events[i][5],))

inF.Close()
file.close()

# print 'nbayes: ',Event.bayes_prob_n(),' gbayes: ',Event.bayes_prob_g(),' sum: ',(Event.bayes_prob_n()+Event.bayes_prob_g());
