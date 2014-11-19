import os
import sys
import os.path

orig_file = open(str(sys.argv[1]), "r")
orig_event = orig_file.readlines()

evnum_file = open(str(sys.argv[2]), "r")
new_event = evnum_file.readlines()

outfile = open(str(sys.argv[1])[:-4]+'_Merged.txt', "w")

print 'original file:',sys.argv[1]
print 'evnum file:',sys.argv[2]

if len(orig_event) != len(new_event):
  print 'Files are not the same length!!!'
  sys.exit()

for i in range(0, len(orig_event)):
  if(i % (len(orig_event)/100) == 0):
    print '%d / %d' % (i, len(orig_event))
  n_num = int(orig_event[i].split(',')[0])
  ev_ch = int(orig_event[i].split(',')[1])
  ev_time = float(orig_event[i].split(',')[2])
  ev_lat = float(orig_event[i].split(',')[3])
  ev_lon = float(orig_event[i].split(',')[4])
  ev_alt = float(orig_event[i].split(',')[5])

  new_n_num = int(new_event[i].split(',')[0])
  new_ev_ch = int(new_event[i].split(',')[1])
  new_time = float(new_event[i].split(',')[2])
  new_ev_num = int(new_event[i].split(',')[3])

  if(n_num == new_n_num and ev_ch == new_ev_ch):
    outfile.write('{ev},{ch},{tme},{lat},{lon},{alt},{ev_num},\n'.format(ev=n_num,
              		ch=ev_ch,
                  tme='%.9f' % new_time,
                  lat=ev_lat,
                  lon=ev_lon,
                  alt='%.3f' % ev_alt,
                  ev_num=new_ev_num))
  else:
    print 'event mismatch at event: ',i
    sys.exit()

orig_file.close()
evnum_file.close()
outfile.close()