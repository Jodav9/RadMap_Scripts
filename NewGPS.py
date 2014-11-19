import os
import sys

#from ROOT import gSystem, TTree, TFile, TH1F
#gSystem.Load('/home/john_davis/Desktop/RadMAP_TopLevel/MISTI/src/libMISTI')
#from ROOT import MISTIEvent
import operator

print 'input file:',sys.argv[1]
print 'gps file:',sys.argv[2]
print 'output file:',sys.argv[3]

# this file will covert any existing sorted N files to the new GPS..

gps_file = open(str(sys.argv[2]),'r')
# input txt file
infile = open(str(sys.argv[1]), 'r')
event = infile.readlines()
# file to write to (txt):
outfile = open(str(sys.argv[3]), "w")

gps_ev = gps_file.readlines()

gpstime = []
lat = []
lon = []
elev = []
idx = 0

# read gps file and collect gps data
for i in range(0,len(gps_ev)):
    if (gps_ev[i][0].isdigit()):
        gpstime.append(float(gps_ev[i].split(' ')[0]))
        lat.append(float(gps_ev[i].split(' ')[2]))
        lon.append(float(gps_ev[i].split(' ')[3]))
        elev.append(float(gps_ev[i].split(' ')[4])+28.7)

# main loop
for j in range(0,len(event)):
    if(j % (len(event)/100) == 0):
        print '%d / %d' % (j, len(event))
    ev_time = float(event[j].split(',')[2])
    ev_ch = int(event[j].split(',')[1])
    for i in range(idx,len(gpstime)):
        # if truck is collecting data but GPS is not turned on yet, set the coordinate to the first GPS coordinate
        if (ev_time < gpstime[0]):
            outfile.write('{ev},{ch},{tme},{lat},{lon},{alt},\n'.format(ev=j,
            ch=ev_ch,
            tme='%.9f' % ev_time,
            lat=lat[0],
            lon=lon[0],
            alt='%.3f' % elev[0]))
            break
        #if(ev_time-0.005 <= utctime <= ev_time+0.005):
        if (gpstime[i] >= ev_time):
            #lat = float(gps_ev[i].split(' ')[2])
            #lon = float(gps_ev[i].split(' ')[3])
            #elev = float(gps_ev[i].split(' ')[4])+32.0
            #interpolate the gps data if between two points
            ev_alt = elev[i-1]+((ev_time-gpstime[i-1])/(gpstime[i]-gpstime[i-1]))*(elev[i]-elev[i-1])
            outfile.write('{ev},{ch},{tme},{lat},{lon},{alt},\n'.format(ev=j,
			ch=ev_ch,
			tme='%.9f' % ev_time,
			lat=lat[i-1]+((ev_time-gpstime[i-1])/(gpstime[i]-gpstime[i-1]))*(lat[i]-lat[i-1]),
			lon=lon[i-1]+((ev_time-gpstime[i-1])/(gpstime[i]-gpstime[i-1]))*(lon[i]-lon[i-1]),
			alt='%.3f' % ev_alt))
            idx = i # assign next index so we dont need to sort through all previous data on the next event
            break
        if(i == len(gpstime)-1):
            outfile.write('{ev},{ch},{tme},{lat},{lon},{alt},\n'.format(ev=j,
						  ch=ev_ch,
						  tme='%.9f' % ev_time,
						  lat=lat[i],
						  lon=lon[i],
						  alt='%.3f' % elev[i]))
infile.close()
gps_file.close()
outfile.close()

