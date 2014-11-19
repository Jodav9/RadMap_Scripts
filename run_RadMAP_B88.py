from subprocess import Popen, PIPE
from os import walk
import sys

#this script is currently executed from the desktop
#files for processing are inserted into the folder: /home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/Data 
convdir = '/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/Data/'
gpsdir = '/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/GPS/'
newgpsdir = '/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/NewGPS/'
#outputdir = '/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/Converted/'
# for B88 files
outputdir = '/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/Data/B88_Files/'
#pyhistsdir = '/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/Converted/PyRootHists/'
# for B88 files
pyhistsdir = '/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/Data/B88_Files/PyRootHists/'
combhistsdir = '/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/Converted/PyRootHists/Combinbed'
mistihistsdir = '/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/Converted/MistiHists/'
weatherdir = '/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/Weather/'
kmldir = '/home/john_davis/Desktop/RadMAP_Run_Data/Files_To_Convert/Converted/GPS_Kml/'

#available psd cal files
Sep12psd = '/home/john_davis/Desktop/Calibration_Data/09_2012_calib/09_2012_psdcal.root'
Dec12psd = '/home/john_davis/Desktop/Calibration_Data/12_2012_calib/12_2012_psdcal.root'
May13psd = '/home/john_davis/Desktop/Calibration_Data/05_2013_calib/psdcal_05_2013.root'

# only one ecal file being used right now
ecal = '/home/john_davis/Desktop/Calibration_Data/aaroncalibs/ecal.root'

#prompt user for run options:
print '\n','Run Options:\n','1 - All\n','2 - ConvertMISTIData\n','3 - N_Event_Sort (Includes NewGPS)\n','4 - Add NewGPS Only (2013 and later)\n','5 - USGS GPS Elevation\n','6 - Fix High Consecutive Count Issues\n','7 - RadMAP_Hists\n','8 - RadMAP_CombineHists\n','9 - GPS kml Plot\n','10 - mistiHists\n'

runopt = []
opt = raw_input("Enter an option: ")
runopt.append(opt)
more_opt = 'y'
while (opt != '1' and (more_opt != 'n' or more_opt != 'N')):
  more_opt = raw_input("Add more options? (Y/N): ")
  if (more_opt == 'Y' or more_opt == 'y'):
    opt = raw_input("Enter an option: ")
    runopt.append(opt)
    if (opt == '1'):
      break
  elif (more_opt == 'N' or more_opt == 'n'):
    print 'No additional options desired.'
    break
  else:
    print more_opt,"is not a valid option -- try again"
 #   sys.exit("Error")

print 'options entered: ',runopt

#determine which psd and gps file to use for each input file
psdcal, gpspreparse, gpsopts, gpsfile, outfile, inpath, txtout, rootout, olddig, n_sort_in, pyhistin, weatherfile, mistihist_in, mistihist_out = ([] for i in range(14))

#txtout - event sorted txt file
#rootout - histogramed data
#olddig - digitizer old or new

########################################

# convertmistidata function
def convertdata(inpath,psdcal,gpsfile,ecal,outfile,olddig):
    if (olddig): #adds the -D option if True
        convert_exe = Popen(['./convertMISTIData '+inpath+' -D '+'-d '+'-p '+psdcal+' -g '+gpsfile+' -e '+ecal+' '+outfile], shell=True, cwd='RadMAP_TopLevel/MISTI/src')
    else:
        convert_exe = Popen(['./convertMISTIData '+inpath+' -d '+'-p '+psdcal+' -g '+gpsfile+' -e '+ecal+' '+outfile], shell=True, cwd='RadMAP_TopLevel/MISTI/src')
    return convert_exe

#get list of files to convert and parse gps if running convertmistidata
for i in range(len(runopt)):
  if (runopt[i] == '2' or runopt[i] == '1'):
    infile = []
    for (dirpath, dirnames, filenames) in walk(convdir):
        infile.extend(filenames)
        break
    #make sure there is data to process
    if (len(infile) == 0):
        print infile[i],"No data in data folder!"
        sys.exit()
    #available gps files (pre-parsing)
    for (dirpath, dirnames, filenames) in walk(gpsdir):
        gpspreparse.extend(filenames)
        break
    #parse gps func
    def parsegps(gpsin):
        parse_exe = Popen(['python WritePosAndTime.py '+gpsin], shell=True, cwd='RadMAP_TopLevel/MISTI/scripts/PythonTools')
        return parse_exe
    #parse any unparsed gps files in folder
    for x in range(0,len(gpspreparse)):
        filetype = gpspreparse[x][-3:]
        if(filetype == 'sql' or filetype == '.gz'):
            parse_exe = parsegps(gpsdir+gpspreparse[x])
            print parse_exe.communicate()
            print 'parsed',gpspreparse[x];
    del gpspreparse
    #new gps listing
    for (dirpath, dirnames, filenames) in walk(gpsdir):
        gpsopts.extend(filenames)
        break
    for i in range(0,len(infile)):
        # input file path add to file name
        inpath.append(convdir+infile[i])
        # output file name assignment
        outfile.append(outputdir+infile[i][:-4]+'.root')
        yr = int(infile[i][9:11])
        mo = int(infile[i][1:3])
        day = int(infile[i][4:6])
        # assign old or new digitizer (double check date of installation)
        if ((yr==13 and mo<5) or yr<13):
            olddig.append(True)
        else:
            olddig.append(False)
        if (len(olddig) != (i+1)):
            print infile[i],"Can't Figure out Digitizer Format - Check Code"
            sys.exit("Error--Halted")
        # sort to find matching psd cal file
        if (yr==12 and mo<12):
            psdcal.append(Sep12psd);
        elif ((yr==12 and mo==12) or (yr==13 and mo<05) or (yr==13 and mo==5 and day<14)):
            psdcal.append(Dec12psd);
        elif ((yr==13 and mo>5) or (yr==13 and mo==5 and day>=14) or yr==14):
            psdcal.append(May13psd);
        else:
            print infile[i],"is Missing Match for PSD Calibration"
            sys.exit("Error--Halted")
        # sort to find matching gps file
        for k in range(0,len(gpsopts)):
            yr_gps = int(gpsopts[k][6:8])
            mo_gps = int(gpsopts[k][8:10])
            day_gps = int(gpsopts[k][10:12])
            gpstype = gpsopts[k][-3:]
            if (yr_gps==yr and mo_gps==mo and day_gps==day and gpstype == 'dat'):
                gpsfile.append(gpsdir+gpsopts[k]);
        if (len(gpsfile) != (i+1)):
            print infile[i],"is Missing GPS File"
            sys.exit("Error--Halted")
    for j in range(0,len(inpath)):
        convert_exe = convertdata(inpath[j],psdcal[j],gpsfile[j],ecal,outfile[j],olddig[j])
        print convert_exe.communicate()
    # force exit of loop in case user input both options 1 and 2
    break

########################################

#N_Event Sort stuff
# N_Event_Sort
def sortdata(outfile,txtout):
    sort_exe = Popen(['python N_Event_Sort.py '+outfile+' '+txtout], shell=True)
    return sort_exe

for i in range(len(runopt)):
  if (runopt[i] == '3' or runopt[i] == '1'):
    outfile = []
    for (dirpath, dirnames, filenames) in walk(outputdir):
        outfile.extend(filenames)
        break
    for j in range(len(outfile)):
        if (outfile[j][-4:] == 'root'):
            n_sort_in.append(outputdir+outfile[j])
            # sorted txt file name assignment
            txtout.append(outputdir+outfile[j][:-4]+'txt')
    for k in range(0,len(n_sort_in)):
        sort_exe = sortdata(n_sort_in[k],txtout[k])
        print sort_exe.communicate()
    break

########################################

#New GPS stuff
def NewGPS(sortedin,gps_file,outfile):
    newgps_exe = Popen(['python NewGPS.py '+sortedin+' '+gps_file+' '+outfile], shell=True)
    return newgps_exe

sortedin = []
outfile = []
gps_file = []
for i in range(len(runopt)):
  if (runopt[i] == '4' or runopt[i] == '1'):
    dirfiles = []
    for (dirpath, dirnames, filenames) in walk(outputdir):
        dirfiles.extend(filenames)
        break
    for j in range(len(dirfiles)):
        if (dirfiles[j][-4:] == '.txt' and len(dirfiles[j]) > 4 and int(dirfiles[j][9:11]) >= 13 and dirfiles[j][-10:] != 'NewGPS.txt'):
            sortedin.append(outputdir+dirfiles[j])
            # sorted txt file name assignment
            outfile.append(outputdir+dirfiles[j][:-4]+'_NewGPS.txt')
            # assign gps file names
            year = dirfiles[j][7:11]
            mo = dirfiles[j][1:3]
            day = dirfiles[j][4:6]
            gps_file.append(newgpsdir+year+mo+day+'.txt')
    for k in range(0,len(sortedin)):
        newgps_exe = NewGPS(sortedin[k],gps_file[k],outfile[k])
        print newgps_exe.communicate()
    break

########################################

#USGS GPS stuff
def USGSgps(sortedin,outfile):
    usgs_exe = Popen(['python USGSelev.py '+sortedin+' '+outfile], shell=True)
    return usgs_exe

sortedin = []
outfile = []
for i in range(len(runopt)):
  if (runopt[i] == '5' or runopt[i] == '1'):
    dirfiles = []
    for (dirpath, dirnames, filenames) in walk(outputdir):
        dirfiles.extend(filenames)
        break
    for j in range(len(dirfiles)):
        if (dirfiles[j][-4:] == '.txt' and len(dirfiles[j]) > 4 and dirfiles[j][-8:] != 'USGS.txt' and dirfiles[j][-11:] != 'B88_GPS.txt'):
            sortedin.append(outputdir+dirfiles[j])
            # sorted txt file name assignment
            outfile.append(outputdir+dirfiles[j][:-4]+'_USGS.txt')
    for k in range(0,len(sortedin)):
        usgs_exe = USGSgps(sortedin[k],outfile[k])
        print usgs_exe.communicate()
    break

########################################

#Fix High Det Count Rate
def CR_Fix(infile):
    crfix_exe = Popen(['python HighDetCRFix.py '+infile], shell=True)
    return crfix_exe

infile = []
for i in range(len(runopt)):
  if (runopt[i] == '6' or runopt[i] == '1'):
    dirfiles = []
    for (dirpath, dirnames, filenames) in walk(outputdir):
        dirfiles.extend(filenames)
        break
    for j in range(len(dirfiles)):
        if (dirfiles[j][-4:] == '.txt' and len(dirfiles[j]) > 4 and dirfiles[j][-8:] != 'Info.txt' and dirfiles[j][-10:] != 'Edited.txt'):
            infile.append(outputdir+dirfiles[j])
    for k in range(0,len(infile)):
        crfix_exe = CR_Fix(infile[k])
        print crfix_exe.communicate()
    break

########################################

# RadMAP_Hists
def rmhists(txtout,weatherfile,rootout):
    hists_exe = Popen(['python RadMAP_Hists.py '+txtout+' '+weatherfile+' '+rootout], shell=True)
    return hists_exe

# pyroothists
for i in range(len(runopt)):
  if (runopt[i] == '7' or runopt[i] == '1'):
    outfile = []
    for (dirpath, dirnames, filenames) in walk(outputdir):
        outfile.extend(filenames)
        break
    for j in range(len(outfile)):
        if (outfile[j][-3:] == 'txt' and len(outfile[j]) > 4 and outfile[j][-8:] != 'Info.txt'):
            pyhistin.append(outputdir+outfile[j])
            # root histograms output
            rootout.append(pyhistsdir+outfile[j][:-4]+'_Hists.root')
            # find weather files
            year = str(outfile[j][7:11])
            mo = str(outfile[j][1:3])
            weatherfile.append(weatherdir+year+'-'+mo+'.csv') #check if file exists in RadMAP_Hists.py
            '''if (year >= 2013 or (year == 2012 and mo == 12)):
                if (mo < 10):
                    mo = '0'+str(mo)
                else:
                    mo = str(mo)
                year = str(year)
                weatherfile.append(weatherdir+year+'-'+mo+'.csv')
            else:
                weatherfile.append(weatherdir+'2012-12.csv')'''
    for k in range(len(pyhistin)):
        hists_exe = rmhists(pyhistin[k],weatherfile[k],rootout[k])
        print hists_exe.communicate()
    break

########################################

# GPS neutron kml
def GPSneutron(gps_n_in,outfile):
    GPSn_exe = Popen(['python GPS_neutron.py '+gps_n_in+' '+outfile], shell=True)
    return GPSn_exe

#GPS neutron
gps_n_in = []
for i in range(len(runopt)):
  if (runopt[i] == '9' or runopt[i] == '1'):
    gpstxt = []
    outfile = []
    for (dirpath, dirnames, filenames) in walk(outputdir):
        gpstxt.extend(filenames)
        break
    for j in range(len(gpstxt)):
        if (gpstxt[j][-3:] == 'txt' and gpstxt[j][-8:] != 'Info.txt'):
            gps_n_in.append(outputdir+gpstxt[j])
            outfile.append(kmldir+gpstxt[j][:-4]+'.kml')
    for k in range(0,len(gps_n_in)):
        print 'Creating kml for: ',gps_n_in[k]
        GPSn_exe = GPSneutron(gps_n_in[k],outfile[k])
        print GPSn_exe.communicate()
    break

########################################

# mistihists
def mistihists(outfile,mistiout):
    misti_exe = Popen(['./mistiHists '+outfile+' '+mistiout], shell=True, cwd='RadMAP_TopLevel/MISTI/src')
    return misti_exe
#mistihists
for i in range(len(runopt)):
  if (runopt[i] == '10' or runopt[i] == '1'):
    outfile = []
    for (dirpath, dirnames, filenames) in walk(outputdir):
        outfile.extend(filenames)
        break
    for j in range(len(outfile)):
        if (outfile[j][-4:] == 'root'):
            mistihist_in.append(outputdir+outfile[j])
            # output file name assignment
            mistihist_out.append(mistihistsdir+outfile[j][:-5]+'_MistiHists.root')
    for k in range(0,len(mistihist_in)):
        print mistihist_in[k]
        print mistihist_out[k]
        misti_exe = mistihists(mistihist_in[k],mistihist_out[k])
        print misti_exe.communicate()
    break

#sys.exit("run_RadMAP Complete!")
#def gps_neutron(intxt,outkml):

#    gps_exe = Popen(['python GPS_neutron_detfix.py'], shell=True, cwd='Analysis_Code_RadMAP')
#    return gps_exe



