import os
import sys

#from ROOT import gSystem, TTree, TFile, TH1F
#gSystem.Load('/home/john_davis/Desktop/RadMAP_TopLevel/MISTI/src/libMISTI')
#from ROOT import MISTIEvent
import operator

print 'input file:',sys.argv[1]

# input txt file
infile = open(str(sys.argv[1]), 'r')
event = infile.readlines()
# error file to write to (txt):
errfile = open(str(sys.argv[1])[:-4]+'_EditInfo.txt', "w")

prev_ch = -1
ongoing_consec_ev = False
consec_start = []
consec_events= []
consec_end = []
channel = []
ev_start = []
ev_end = []
prev_ev_time = 0
consec_ch_ct = 0

# main loop
for j in range(0,len(event)):
    if(j % (len(event)/100) == 0):
        print '%d / %d' % (j, len(event))
    ev_time = float(event[j].split(',')[2])
    ev_ch = int(event[j].split(',')[1])
    if ev_ch == prev_ch:
        consec_ch_ct += 1
        if not ongoing_consec_ev: # this is a new consectutive event series
            consec_start.append(ev_time)
            channel.append(ev_ch)
            ev_start.append(j)
            ongoing_consec_ev = True
    elif ev_ch != prev_ch:
        ongoing_consec_ev = False
        if consec_ch_ct > 0:
            consec_events.append(consec_ch_ct)
            consec_end.append(prev_ev_time)
            ev_end.append(j-1)
            consec_ch_ct = 0

    prev_ev_time = ev_time
    prev_ch = ev_ch

#print len(consec_start)
#print len(consec_end)
#print len(consec_events)
#print len(channel)

remove_array = []
for i in range(0,len(consec_events)):
    if consec_events[i] > 5:
        errfile.write('Events {b} - {e} / Time: {st} - {end}: Channel {ch}, Removed {ev} events,\n'.format(st='%.9f' % consec_start[i],
        end='%.9f' % consec_end[i],
        b=ev_start[i],
        e=ev_end[i],
        ch=channel[i],
        ev=consec_events[i]))
        remove_array.append([ev_start[i],ev_end[i],consec_events[i]])

if len(remove_array) == 0:
    errfile.write('No Events Removed')
    infile.close()
    errfile.close()
    sys.exit('No Events Removed')

# now open the file to write to
outfile = open(str(sys.argv[1])[:-4]+'_Edited.txt', "w")

ev_number = 0
removing_events = False
remove_count = 0

for j in range(0,len(event)):
    for k in range(0,len(remove_array)):
        if (remove_array[k][0] <= j <= remove_array[k][1]+1): # and ev_ch == remove_array[k][2]): #float('1359488127.786070108'):
            #print 'duplicate event found at time','%.9f' % ev_time
            removing_events = True
            remove_count += 1
            cts_to_remove = remove_array[k][2]+1
            if remove_count == cts_to_remove:
                print "counts removed:",remove_count-1
                remove_count = 0
                cts_to_remove = 0
                removing_events = False
    if not removing_events:
        outfile.write('{ev},{ch},{tme},{lat},{lon},{alt},{ev_num},\n'.format(ev=ev_number,
        ch=int(event[j].split(',')[1]),
        tme='%.9f' % float(event[j].split(',')[2]),
        lat=float(event[j].split(',')[3]),
        lon=float(event[j].split(',')[4]),
        alt='%.3f' % float(event[j].split(',')[5]),
        ev_num=int(event[j].split(',')[6]),))

        ev_number += 1

infile.close()
outfile.close()
errfile.close()
