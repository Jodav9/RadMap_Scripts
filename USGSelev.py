import os
import sys
import urllib, urllib2
# simple XML parsing
from xml.dom import minidom
from math import radians, cos, sin, asin, sqrt

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

# files
print 'input file:',sys.argv[1]
print 'output file:',sys.argv[2]

# make this into an alternate N_Event_Sort..
infile = open(str(sys.argv[1]), 'r')
event = infile.readlines()

# find out if a USGS.txt file was already started for the given run
# find if exists - True / False
if os.path.isfile(str(sys.argv[2])):
  usgs_avail = True
else:
  usgs_avail = False

######

# file to write to:
if not usgs_avail:
    usgs_alt = open(str(sys.argv[2]), "w")
    start_event = 0
if usgs_avail:
    # first read and find out where we left off and make that the start point
    usgs_alt_read = open(str(sys.argv[2]), "r")
    conv_events = usgs_alt_read.readlines()
    start_event = len(conv_events)
    usgs_alt_read.close()
    # now re-open in append mode
    usgs_alt = open(str(sys.argv[2]), "a")

# base_url = 'http://gisdata.usgs.gov/XMLWebServices/TNM_Elevation_Service.asmx/getElevation?X_Value=%f&Y_Value=%f&Elevation_Units=meters&Source_Layer=-1&Elevation_Only=1'

# the base URL of the web service
url = 'http://gisdata.usgs.gov/XMLWebServices/TNM_Elevation_Service.asmx/getElevation'

# make some fake headers, with a user-agent that will not be rejected by servers
user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {'User-Agent' : user_agent}

# get elevation function
def getUSGSelevation(ev_lat,ev_lon):
    # url GET args
    vals = {'X_Value' : ev_lon,
        'Y_Value' : ev_lat,
        'Elevation_Units' : 'meters',
        'Source_Layer' : '-1',
        'Elevation_Only' : '1', }
    # encode values
    encodedvals = urllib.urlencode(vals)  
    # make URL into GET statement:
    get_url = url + '?' + encodedvals
    # send request
    request = urllib2.Request(url=get_url, headers=headers)
    response = urllib2.urlopen(request)
    output = response.read()
    # convert the HTML back into plain XML
    for entity, char in (('lt', '<'), ('gt', '>'), ('amp', '&')):
        output = output.replace('&%s;' % entity, char)
    # parse the XML
    dom = minidom.parseString(output)
    children = dom.getElementsByTagName('Elevation_Query')[0]
    # get the elevation if it exists, if not, set it to 'NAN' so we can later replace with existing elevation
    try:
        ev_elev = float(children.getElementsByTagName('Elevation')[0].firstChild.data)
    except IndexError:
        ev_elev = 'NAN'
    return ev_elev

#############
# my stuff
############

dx = 5 #meters - min travel distance before making another elevation request

# first we must get the first event data and write to file
beg_time = float(event[start_event].split(',')[2])
beg_ch = int(event[start_event].split(',')[1])
beg_lat = float(event[start_event].split(',')[3])
beg_lon = float(event[start_event].split(',')[4])
prev_elev = getUSGSelevation(beg_lat,beg_lon)
beg_evnum = int(event[start_event].split(',')[6])
print '%d / %d' % (start_event, len(event))
usgs_alt.write('{ev},{ch},{tme},{lat},{lon},{alt},{ev_num},\n'.format(ev=start_event,
		ch=beg_ch,
		tme='%.9f' % beg_time,
		lat=beg_lat,
		lon=beg_lon,
		alt='%.3f' % prev_elev,
        ev_num=beg_evnum))

# main loop
for j in range(start_event+1,len(event)):
    if(j % (len(event)/100) == 0):
        print '%d / %d' % (j, len(event))
    ev_time = float(event[j].split(',')[2])
    ev_ch = int(event[j].split(',')[1])
    ev_lat = float(event[j].split(',')[3])
    ev_lon = float(event[j].split(',')[4])
    evnum = int(event[j].split(',')[6])
    
    # travel dist calc
    trav_dist = haversine(beg_lon, beg_lat, ev_lon, ev_lat)

    if(trav_dist <= dx):
        #use previous altitude
        ev_elev = prev_elev
    else:
        #use new alt request and reset 
        ev_elev = getUSGSelevation(ev_lat,ev_lon)
        # if usgs could not locate point, use existing gps elevation
        if (ev_elev == 'NAN'):
            ev_elev = float(event[j].split(',')[5])
            print 'No USGS Elevation for Coordinate:',ev_lat,ev_lon
        prev_elev = ev_elev
        #reset
        beg_lat = ev_lat
        beg_lon = ev_lon

    usgs_alt.write('{ev},{ch},{tme},{lat},{lon},{alt},{ev_num},\n'.format(ev=j,
		ch=ev_ch,
		tme='%.9f' % ev_time,
		lat=ev_lat,
		lon=ev_lon,
		alt='%.3f' % ev_elev,
        ev_num=evnum))

usgs_alt.close()
infile.close()
