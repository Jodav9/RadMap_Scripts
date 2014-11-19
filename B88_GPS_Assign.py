import os
import sys

# files
print 'input file:',sys.argv[1]
print 'output file:',sys.argv[1][:-4]+'_B88_GPS.txt'


#37.8766195284,-122.254485195,180.833,

infile = open(str(sys.argv[1]), 'r')
event = infile.readlines()

# file to write to:
gps_fix = open(str(sys.argv[1])[:-4]+'_B88_GPS.txt', "w")

for j in range(0,len(event)):
    if(j % (len(event)/100) == 0):
        print '%d / %d' % (j, len(event))
    ev_time = float(event[j].split(',')[2])
    ev_ch = int(event[j].split(',')[1])
    #ev_lat = float(event[j].split(',')[3])
    #ev_lon = float(event[j].split(',')[4])
    #ev_elev = float(event[j].split(',')[5])
    ev_num = int(event[j].split(',')[6])

    gps_fix.write('{ev},{ch},{tme},{lat},{lon},{alt},{evnum},\n'.format(ev=j,
		ch=ev_ch,
		tme='%.9f' % ev_time,
		lat=37.8766195284,
		lon=-122.254485195,
		alt=180.833,
        evnum=ev_num))

gps_fix.close()
infile.close()