from __future__ import print_function
import numpy
import datetime
import os

# outage starting at 11/18/13 11:08a in all wind measurements
outages = [
    {
        'start': datetime.datetime(2013, 11, 18, 11, 8, 0),
        'stop': datetime.datetime(2999, 1, 1, 0, 0, 0),
        'affected': [
            'Wind Speed (knots)',
            'Wind Direction',
            'Wind Direction (degrees)',
            'Wind Run',
            'Wind High Speed (knots)',
            'Wind High Direction',
            'Wind High Direction (degrees)',
            'Wind Chill (F)',
            'THW Index (F)',
        ]
    }
]


def datetime_to_unix(dt):
    return float(dt.strftime('%s'))


class WeatherLinkParser(object):
    
    def __init__(self, file_name):
        self.file_name = file_name
        print('RadMAP weather archive file: opening ', self.file_name)
        try:
            self.file = open(self.file_name, 'r')
        except:
            print('Error opening file')
            exit(0)
        self.data = {}
        self.read_keys = [
            'Date',
            'Time',
            'Temp Out (F)',
            'Hi Temp (F)',
            'Low Temp (F)',
            'Outside Humidity (%)',
            'Dew Point (F)',
            'Wind Speed (knots)',
            'Wind Direction',
            'Wind Run',
            'Wind High Speed (knots)',
            'Wind High Direction',
            'Wind Chill (F)',
            'Heat Index (F)',
            'THW Index (F)',
            'Pressure (mbar)',
            'Rain (mm)',
            'Rain Rate (mm/hr)',
            'Heat D-D',
            'Cool D-D',
            'Inside Temp (F)',
            'Inside Humidity (%)',
            'Inside Dew Point (F)',
            'Inside Heat (F)',
            'Inside EMC',
            'Inside Air Density (kg/m^3)',
            'Wind Sample',
            'Wind Tx',
            'ISS Recept',
            'Archive Interval (minutes)'
        ]
        for key in self.read_keys:
            self.data[key] = []
    
    def select(self, indices):
        """
        Select all datasets down according to the provided indices.
        """
        for key in self.data.keys():
            self.data[key] = self.data[key][indices]
    
    def parse(self):
        """
        Read text file and parse into arrays.
        """
        self.num_lines = 0
        self.len_data = 0
        for line in self.file:
            data = line.split('\t')
            assert(len(data)==30)
            if self.num_lines < 2:
                pass
                # # read file header
                # print(data)
                # s = ''
                # for s1 in line.split('\t'):
                #     s += '{:8s}'.format(s1)
                # print(s)
            else:
                for j, key in enumerate(self.read_keys):
                    self.data[key].append(data[j].strip())
                self.len_data += 1
            self.num_lines += 1
        
        # convert strings into numbers
        for key in set(self.read_keys) - set(['Date', 'Time', 'Wind Direction',
                'Wind High Direction']):
            for i in range(self.len_data):
                try:
                    self.data[key][i] = float(self.data[key][i])
                except:
                    self.data[key][i] = numpy.nan
        
        # convert directions into degrees
        degrees = {
            '---':numpy.nan,
            'N':  0., 'NNE': 22.5, 'NE': 45., 'ENE': 67.5,
            'E': 90., 'ESE':112.5, 'SE':135., 'SSE':157.5,
            'S':180., 'SSW':202.5, 'SW':225., 'WSW':247.5,
            'W':270., 'WNW':292.5, 'NW':315., 'NNW':337.5
        }
        for key in ['Wind Direction', 'Wind High Direction']:
            new_key = key + ' (degrees)'
            self.data[new_key] = []
            for i in range(self.len_data):
                self.data[new_key].append(degrees[self.data[key][i]])
                # print(self.data[key][i], self.data[new_key][i])
        
        # calculate python datetime from Date and Time
        self.data['Datetime'] = []
        self.data['UTC_seconds'] = []
        for i in range(self.len_data):
            mmddyy = self.data['Date'][i]
            time_info = self.data['Time'][i].split(' ')
            HHMM = time_info[0]
            ampm = time_info[1]
            HH = int(HHMM.split(':')[0])
            MM = int(HHMM.split(':')[1])
            # take care of the silly non-24 hour time format used in the txt file
            if HH == 12:
                if ampm == 'a':
                    HH = 0
                else:
                    HH = 12
            elif ampm == 'p':
                HH += 12
            HHMM = '{:02d}:{:02d}'.format(HH, MM)
            # use the corrected 24-hour time to overwrite the time
            self.data['Time'][i] = HHMM
            mmddyy_HHMM = mmddyy + ' ' + HHMM
            dt = datetime.datetime.strptime(mmddyy_HHMM, '%m/%d/%y %H:%M')
            self.data['Datetime'].append(dt)
            self.data['UTC_seconds'].append(datetime_to_unix(dt))
        
        # remove spaces from Time field
        for i in range(self.len_data):
            self.data['Time'][i] = self.data['Time'][i].replace(' ', '')
        
        # convert lists to numpy arrays
        for key in self.data.keys():
            self.data[key] = numpy.array(self.data[key])
            # print(key, self.data[key])
        
        # remove bad data points
        # temperatures
        check_keys = [
            'Temp Out (F)',
            'Hi Temp (F)',
            'Low Temp (F)',
            'Dew Point (F)', 
            'Inside Temp (F)',
            'Inside Dew Point (F)',
        ]
        for key in check_keys:
            # use reasonable temperature range for Berkeley
            self.keep_in_range(key, 0., 120.)
        
        # humidity percents
        check_keys = [
            'Outside Humidity (%)',
            'Inside Humidity (%)',
        ]
        for key in check_keys:
            self.keep_in_range(key, 0., 100.)
        
        # check that times are monotonically increasing
        dt = self.data['UTC_seconds'][1:] - self.data['UTC_seconds'][:-1]
        if (dt <= 0.).any():
            ind = numpy.nonzero(dt <= 0.)[0]
            for i in ind:
                print(i, self.data['UTC_seconds'][i], self.data['UTC_seconds'][i+1])
        assert((dt > 0.).all())
        
        # find when large pressure changes occur (checks that time is correct)
        dP = self.data['Pressure (mbar)'][1:] - self.data['Pressure (mbar)'][:-1]
        dP_dt = dP / dt
        ind = numpy.nonzero(abs(dP_dt) > 8./60.)[0]
        print('Large pressure gradients at:')
        for i in ind:
            print('  ', self.data['Datetime'][i], self.data['Pressure (mbar)'][i],
                '  -  ', self.data['Datetime'][i+1], self.data['Pressure (mbar)'][i+1])
        
        # block out some data during outages
        print('Applying outages')
        for outage in outages:
            print('Outage from ', outage['start'], ' to ', outage['stop'])
            ind = (self.data['Datetime'] >= outage['start']) \
                * (self.data['Datetime'] <= outage['stop'])
            for key in outage['affected']:
                print('  Blocking out ' + key)
                self.data[key][ind] = numpy.nan
                print('    ', len(self.data[key][ind]))
        
        print('Done reading MISTI weather archive file')
    
    def __getitem__(self, key):
        return self.data[key]
    
    def keep_in_range(self, key, low_limit, high_limit):
        """
        Keep only data between the limits.
        """
        indices = (low_limit <= self.data[key]) * (self.data[key] <= high_limit)
        if (indices == False).any():
            print('Bad data in {}'.format(key))
            print(self.data[key][indices == False])
            print('Removing ',
                len(self.data[key][indices == False]),
                ' data from arrays (current length is ',
                len(self.data[key][indices]), ')')
            self.select(indices)
    
    def write(self, filename):
        """
        Write weather data to CSV file.
        """
        self.write_keys = [
            'UTC_seconds',
            'Date',
            'Time',
            'Temp Out (F)',
            'Hi Temp (F)',
            'Low Temp (F)',
            'Outside Humidity (%)',
            'Dew Point (F)', 
            'Wind Speed (knots)',
            'Wind Direction',
            'Wind Direction (degrees)',
            'Wind Run',
            'Wind High Speed (knots)',
            'Wind High Direction',
            'Wind High Direction (degrees)',
            'Wind Chill (F)',
            'Heat Index (F)',
            'THW Index (F)',
            'Pressure (mbar)',
            'Rain (mm)',
            'Rain Rate (mm/hr)',
            'Heat D-D',
            'Cool D-D',
            'Inside Temp (F)',
            'Inside Humidity (%)',
            'Inside Dew Point (F)',
            'Inside Heat (F)',
            'Inside EMC',
            'Inside Air Density (kg/m^3)',
            'Wind Sample',
            'Wind Tx',
            'ISS Recept',
            'Archive Interval (minutes)'
        ]
        with open(filename, 'w') as outfile:
            print(','.join(self.write_keys), file=outfile)
            for j in range(len(self.data['UTC_seconds'])):
                data_strings = []
                for key in self.write_keys:
                    data_strings.append('{}'.format(self.data[key][j]))
                print(','.join(data_strings), file=outfile)
    

if __name__ == '__main__':
    
    import pylab
    import sys
    
    print(sys.argv)
    assert(len(sys.argv) == 2)
    filename = sys.argv[1]
    
    print("")
    print("")
    print("-"*40)
    print("")
    f = WeatherLinkParser(filename)
    f.parse()
    f.write(filename.split('.txt')[0] + '.csv')
