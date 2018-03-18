
import sys
import getopt
import os
import subprocess
import logging
import time
from operator import itemgetter
from datetime import datetime
from shutil import copyfile
from pathlib import Path


# ===================================================================================================================
class config_data:
    def __init__(self):
        # sys.argv = ['The python file', '--mode=analyze' ,'--outputdir=D:/AartenHetty/OneDrive/WmicFiles/']
        sys.argv = ['The python file', '--mode=analyze' ,'--outputdir=D:/AHMRDH/OneDrive/WmicFiles/']
        # sys.argv = ['The python file', '--mode=create' ,'--outputdir=C:/Users/AartenHetty/OneDrive/WmicFiles/']
        # sys.argv = ['The python file', '--mode=create' ,'--outputdir=C:/Users/AHMRDH/OneDrive/Documents/WmicFiles/', '--loglevel=debug']
        # sys.argv = ['The python file', '--mode=analyze' ,'--outputdir=C:/Users/AHMRDH/OneDrive/Documents/WmicFiles/', '--loglevel=debug']
        # sys.argv = ['The python file', '--mode=create']
        # sys.argv = ['The python file', '--mode=analyze']
        
        # Determine other environment variables
        self.Version = "Version 01 Release 01.03"
       
        self.PythonFile = os.path.realpath(__file__)
        self.Created = os.path.getmtime(self.PythonFile)
        self.CreatedStr = time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(self.Created))
        logmsg = "Python file: " + self.PythonFile + " - Created: " + self.CreatedStr + " - Source " + self.Version
        current_log.log_msg(logmsg,"info",00)
      
        now = datetime.today()
        self.datestamp = now.strftime("%A %d %b %Y")
        self.timestamp = now.strftime("%H:%M")
        self.Target_dir = os.path.expanduser("~") + '/WmicFiles/'
        
        self.computer = os.environ['COMPUTERNAME']
        self.compname = self.computer.replace("-", "_")
        self.generations = 10
             
       
        self.MyMode = "create"
        self.loglevel = "info"

        self.RetryCount = 5
        self.BusyWaitTime = 5

        if len(sys.argv) > 1:
            try: options, remainder = getopt.getopt(sys.argv[1:],'', ['mode=','outputdir=','loglevel='])
            except getopt.GetoptError as err:
                logmsg = "Parameter error encountered: " + str(err)
                current_log.log_msg(logmsg,"error",1)
                self.OK = False
                return
            if remainder: 
                logmsg = 'REMAINING parameter ignored: ' + remainder
                current_log.log_msg(logmsg,"warning",2)
            if options:
                logmsg = 'OPTIONS   :' + str(options)
                current_log.log_msg(logmsg,"debug",3)
            for opt, arg in options:
                logmsg = "==> " + opt + " " + arg + " " + arg.lower()
                current_log.log_msg(logmsg,"debug",4)
                if opt == '--mode':
                    if arg.lower() == "analyze": 
                        self.MyMode = arg.lower()
                    elif arg.lower() == "create":
                        self.MyMode = arg.lower()
                    else:
                        logmsg = "Wrong parameter value ingnored: " + opt + arg
                        current_log.log_msg(logmsg,"warning",5)
                        
                elif opt == "--loglevel":
                    if arg.lower() == "debug":
                        self.loglevel = "debug"
                    elif arg.lower() == "info":
                        self.loglevel = "info"
                    else:
                        logmsg = "Wrong parameter value ingnored: " + opt + arg
                        current_log.log_msg(logmsg,"warning",24)
                        
                elif opt == "--outputdir":
                        self.Target_dir = arg
                else:
                    logmsg = "Wrong parameter ignored: " + opt + arg
                    current_log.log_msg(logmsg,"warning",6)
        
        if ( not os.path.isdir(self.Target_dir)):
            os.makedirs(self.Target_dir)
        self.logfile = self.Target_dir + "WMIC_" + self.compname + ".log"
        self.busyfile = self.Target_dir + "WMIC_" + self.compname + ".busy"
        self.rptfile = self.Target_dir + "Current_WMIC_Report.txt"
        
        yyyymmdd = now.strftime("%Y%m%d")
        self.wmicfile = "WMIC_" + self.compname + "_" + yyyymmdd + ".txt"
        self.wmictempfile = "WMIC_" + self.compname + "_" + yyyymmdd + ".tmp"  
        

        logmsg = "Mode = " + self.MyMode 
        current_log.log_msg(logmsg,"info",7)
        logmsg = "Outputdir = " + self.Target_dir 
        current_log.log_msg(logmsg,"info",8)
        self.OK = True

# ===========================================================================================tm========================

class My_Logger:
    def __init__(self):
        self.Logger = logging.getLogger("Sympa")
        self.msglist = []
        self.logfile = "none"
        self.loglvl = "info"
        self.logset = False

    def set_log(self,dataset,lvl):
        self.logfile = dataset
        self.logfileOLD = dataset + "old"
        logsize = os.path.getsize(self.logfile)
        if logsize > 1024*1024:
            os.remove(self.logfileOLD)
            logmsg = "OLD logdataset " + self.logfileOLD + " deleted."
            self.log_msg(logmsg, "info",38) 
            os.rename(self.logfile, self.logfileOLD)
            logmsg = "Logdataset " + self.logfile + " renamed to " + self.lofileOLD
            self.log_msg(logmsg, "info",39)
        else:
            logmsg = "Current logdataset size is " + str(logsize) + " bytes."
            self.log_msg(logmsg, "info",40)
        self.loglvl = lvl
        self.logset = True
        logging.basicConfig(filename=self.logfile)
        if self.loglvl == "debug":
            self.Logger.setLevel(10)
        elif self.loglvl == "info" :
            self.Logger.setLevel(20)
        elif self.loglvl == "warning" :
            self.Logger.setLevel(30)
        elif self.loglvl == "error" :
            self.Logger.setLevel(40)
        elif self.loglvl == "critical" :
            self.Logger.setLevel(50)
        else:
            self.Logger.setLevel(0)
            logmsg = "Wrong logging level passed (self.loglvl): " + self.loglvl
            self.log_msg(logmsg, "error",9) 
            

    def log_msg(self, msgtext, msglvl, msgnr):
        entrytime = datetime.today()
        if self.logset:
            while len(self.msglist) > 0:
                outdata,outlvl,outnr,outtim = self.msglist.pop(0)
                outrec = self.log_layout(outdata, outlvl, outnr, outtim)
                if outlvl == "debug":
                    intlvl = 10
                elif outlvl == "info" :
                    intlvl = 20
                elif outlvl == "warning" :
                    intlvl = 30
                elif outlvl == "error" :
                    intlvl = 40
                elif outlvl == "critical" :
                    intlvl = 50
                else:
                    intlvl = 0
                    logmsg = "Wrong logging level passed (outlvl): " + outlvl
                    self.log_msg(logmsg, "error",10) 
                self.Logger.log(intlvl,outrec)
            outrec = self.log_layout(msgtext, msglvl, msgnr, entrytime)
            if msglvl == "debug":
                intlvl = 10
            elif msglvl == "info" :
                intlvl = 20
            elif msglvl == "warning" :
                intlvl = 30
            elif msglvl == "error" :
                intlvl = 40
            elif msglvl == "critical" :
                intlvl = 50
            else:
                intlvl = 0
                logmsg = "Wrong logging level passed (msglvl): " + msglvl
                self.log_msg(logmsg, "error",11) 
            self.Logger.log(intlvl, outrec)
        else:
            self.msglist.append([msgtext, msglvl, msgnr, entrytime])

    def log_layout(self,text,lvl,msgnr,timest):
        layed_out = ''
        l_timest = timest.strftime(" %d%b%Y - %H:%M:%S " )
        l_nr = str(msgnr).zfill(4)
        if lvl == "debug":
            l_indic = "D "
        elif lvl == "info":
            l_indic = "I "
        elif lvl == "warning":
            l_indic = "W "
        elif lvl == "critical":
            l_indic = "C "
        else:
            l_indic = "E "
        retrec = l_nr + l_indic + l_timest + text
        return retrec

# ===================================================================================================================

class Busy_list:
    def __init__(self):
        self.loopcount = 1
        self.dsnlist = []
        # print("self")

    def test (self, dsn):
        indic = dsn[0:5]
        extension = dsn[len(dsn)-5:len(dsn)]
        if (indic == "WMIC_") and (extension == ".busy"):
            return( True )
        else:
            return ( False )
        
    def check(self):
        self.isbusy = False
        self.dsnlist = []
        for dirname, dirnames, filenames in os.walk('.'):
            for filename in filenames:                      
                if self.test(filename) == False:     # is het een geldige busy file                          
                    pass                             # zo niet, skip
                else:                                   # zo ja, voeg toe aan busy lijst
                    Busy_item = Busy_Enqueue()
                    Busy_item.modtime = os.path.getmtime(filename)
                    Busy_item.dsname = envir.Target_dir + filename 
                    self.dsnlist.append(Busy_item)    
                    self.isbusy = True

    def clean(self):
        self.loopcount = self.loopcount + 1
        present = time.time()
        for busyfile in self.dsnlist:
            if (busyfile.modtime < (present - 60*envir.BusyWaitTime)):
                busyfile.CleanEnq("previous")
        
    def wait(self):
        logmsg = "Clean-up did not succeed, waiting for " + str(envir.BusyWaitTime) + " minutes..."
        current_log.log_msg(logmsg,"warning",35)
        time.sleep(60*envir.BusyWaitTime)

# ===================================================================================================================

class Busy_Enqueue:
    def __init__(self):
        self.dsname = envir.busyfile
        self.modtime = 0
        # print("self")
        
    def StartEnq(self, wmicf):
        # print ("start")
        b = open(self.dsname, 'wt', encoding="utf-8")
        busyrec = wmicf
        b.write(busyrec)
        b.close()
        logmsg = "WMIC lock set in file: " + self.dsname
        current_log.log_msg(logmsg,"info",30)
        
    def CleanEnq(self,whenwhere):
        # print ("cleanup")
        cleanneeded = True        
        try:
            b = open(self.dsname, 'rt', encoding="utf-8")
            # print ("open")
            busyrec = b.readline()
            # print (busyrec)
            self.errordsn = busyrec.strip()
            # print (self.errordsn)
            b.close()
            # print ("close")
            
        except Exception as inst:
            # print (inst)
            cleanneeded = False
            if (whenwhere == "previous"):
                logmsg = "Previous CREATE WMIC run ended clean"
                current_log.log_msg(logmsg,"info",27)
            else:
                logmsg = "No WMC lock file found, no clean-up needed"
                current_log.log_msg(logmsg,"info",32)
                
        if (cleanneeded):
            logmsg = whenwhere.capitalize() + " CREATE WMIC run failed with output file: " + self.errordsn          
            current_log.log_msg(logmsg,"warning",26)
            try:
                os.remove(self.errordsn)
                logmsg = "Failed WMIC output now deleted: " + self.errordsn          
                current_log.log_msg(logmsg,"warning",28)
            except:
                logmsg = "Could not delete failed WMIC output: " + self.errordsn          
                current_log.log_msg(logmsg,"error",36)
            try:
                os.remove(self.dsname)
                logmsg = "WMIC lock file of " + whenwhere +  " run deleted: " + self.dsname          
                current_log.log_msg(logmsg,"warning",29)
            except:
                logmsg = "Could not delete WMIC lock file of " + whenwhere +  " run: " + self.dsname          
                current_log.log_msg(logmsg,"warning",29)
          
    def EndEnq(self):
        os.remove(self.dsname)
        logmsg = "WMIC lock file released: " + self.dsname          
        current_log.log_msg(logmsg,"info",31)
        
# ===================================================================================================================        

class WMIC_dslist:
    def __init__(self):
        self.complist = []

    # Test if this is a valid WMIC file
    def test (self, dsn):
        indic = dsn[0:5]
        extension = dsn[len(dsn)-4:len(dsn)]
        if (indic == "WMIC_") and (extension == ".txt"):
            return( True )
        else:
            return ( False )

    # copy temp file to current WMIC
    def copy_temp(self, dsn, tmp):
        tst_file = Path(dsn)
        if tst_file.is_file():
            verb16 = "updated"
        else:
            verb16 = "created"
        copyfile(tmp, dsn)
        os.remove (tmp)
        logmsg = "WMIC file " + verb16 + ": " + dsn
        current_log.log_msg(logmsg,"info",16)

    # Add new dsname tuple to object
    def push_obj(self, dsn):

        # Create attributes for dsntuple
        dsname = dsn
        i = dsn.rfind("_",0)
        timestamp = dsn[i+1:i+9]
        timenr = int(timestamp)
        j = dsn.find("_",0)
        computer = dsn[j+1:i]
        dsntuple = []
        dsntuple = [dsname, timestamp, timenr]

        # Create entry for this computer if not yet there                
        addit = True
        for item in self.complist:
            if item[0] == computer:
                addit = False
        if addit:
            dslist = []
            self.complist.append((computer,dslist))

        # Replace current list of dsntuples with a list with the new tuple added
        for item in self.complist:
            if item[0] == computer:
                dellit = item[1]
                newlist = []
                newlist = item[1]
                newlist.append(dsntuple)
                self.complist.remove((computer,dellit))
                self.complist.append((computer,newlist))
                break

    # Fill the list with valid WMIC files
    def fill_list(self):
        for dirname, dirnames, filenames in os.walk('.'):
            for filename in filenames:                      
                if self.test(filename) == False:     # is het een geldige WMIC file                          
                    pass                             # zo niet, skip
                else:
                    self.push_obj(filename)          # zo ja, voeg toe aan object WMIC_dir

    # Fill a list with the most recent WMIC file for each computer
    def get_last_WMICS(self):
        recents = []
        for item in self.complist:
            item[1].sort(key=itemgetter(2),reverse=True)
            rtup = []
            rtup = [item[0],item[1][0][0],item[1][0][1],item[1][0][2]]
            recents.append(rtup)
            
        return recents       
        

    # Delete obsolete files on this computer(we keep max 10 files per computer)      
    def del_obsolete(self,cp,gens):
        for item in self.complist:
            Lengte = len(item[1])
            item[1].sort(key=itemgetter(2),reverse=True)
            logmsg = "{} bevat {} datasets:".format(item[0], Lengte)
            current_log.log_msg(logmsg,"debug",19)
          
            teller = 0
            for item2 in item[1]:
                teller = teller + 1
                if teller <= gens:
                    logmsg = "   -  {} - KEPT".format(item2[0:1])
                    current_log.log_msg(logmsg,"debug",20)
                elif item[0] == cp:
                    os.remove (str(*item2[0:1]))
                    logmsg = "   -  {} - DELETED".format(item2[0:1])
                    current_log.log_msg(logmsg,"debug",21)
                    logmsg = "Old WMIC file deleted: " + str(*item2[0:1])
                    current_log.log_msg(logmsg,"info",12)
                else:
                    logmsg = "   -  {} - NO ACTION".format(item2[0:1])
                    current_log.log_msg(logmsg,"debug",22)

# ===================================================================================================================

class report_matrix:
    def __init__(self):
        self.rptlist = [["## Reporting node: " + envir.computer, " " , " "],
                        ["## Vendor ##","## Component ##","## Highest Release ##"],
                        ["###      ###","###         ###","###               ###"]]

    def getcolwidth(self):
    # determine colwidth for report
        widths = []
        cols = len(self.rptlist[0]);
        for j in range (0, cols):
            widths.append(0)
        for i in range (0, len(self.rptlist)):
            for j in range (0, cols):
                fieldlen = len(self.rptlist[i][j])
                if fieldlen > widths[j]:
                    widths.pop(j)
                    widths.insert(j,fieldlen)
        logmsg = "Report column widths: /"
        for i in range (0, len(widths)):
            logmsg = logmsg + str(widths[i]) + "/"
        current_log.log_msg(logmsg,"debug",23)
        return widths
                        

    def printit(self,nrofrecs):
        maxwidths = self.getcolwidth()
        max = len(self.rptlist)
        if nrofrecs > max or nrofrecs == 0:
            nrofrecs = max
        for i in range (0,nrofrecs):
            nrofcols = len(self.rptlist[i])
            formit = "{0:" + str(maxwidths[0]+2) + "}  {1:" + str(maxwidths[2]+2) + "}"
            print (formit.format(self.rptlist[i][0],self.rptlist[i][2]),end="" )
            maxrel = self.rptlist[i][2]
            for j in range (3,nrofcols):
                currel = self.rptlist[i][j]
                if currel != maxrel and i > 2 and currel != "N/A":
                    currel = currel + "  <=== "
                formit = "{:" + str(maxwidths[j]+8) + "}"
                print(formit.format(currel) ,end="")
            formit = "{:" + str(maxwidths[1]+2) + "}"
            print (formit.format(self.rptlist[i][1]))
        
    def reportit(self,nrofrecs,outfile):
        maxwidths = self.getcolwidth()
        f = open(outfile, 'wt', encoding="utf-16")
        max = len(self.rptlist)
        if nrofrecs > max or nrofrecs == 0:
            nrofrecs = max
        for i in range (0,nrofrecs):
            nrofcols = len(self.rptlist[i])
            v = self.rptlist[i][0].ljust(maxwidths[0]+2)
            c = self.rptlist[i][1].ljust(maxwidths[1]+2)
            r = self.rptlist[i][2].ljust(maxwidths[2]+2)
            outrec = v+r
            maxrel = self.rptlist[i][2]
            for j in range (3,nrofcols):
                currel = self.rptlist[i][j]
                if currel != maxrel and i > 2 and currel != "N/A":
                    currel = currel + "  <==="
                rc = currel.ljust(maxwidths[j]+8)
                outrec = outrec + rc
            outrec = outrec + c
            f.write(outrec+"\n")
        f.close()

    def stow_rec (self, computer, timestamp, vendor, component, release):

        # clean component name from release info
        component = component.replace(release, " ")

        # be sure vendor is nog blank
        if vendor.strip()== "":
            vendor = "-- Ve n d o r   U n k n o w n --"

        # add column for computer the first time
        
        headlen = len(self.rptlist[1])      # this is the second headerline, with the computer namee
        addcomp = True
        for i in range (0,headlen):
            if computer == self.rptlist[1][i]:
                col_offset = i
                addcomp = False
                break
        if addcomp:
            self.rptlist[0].append(" ")         # first header line
            self.rptlist[1].append(computer)    # second header line
            self.rptlist[2].append(timestamp)   # third header line
            col_offset = headlen

        # add or update table row
        # column 0 = Vendor
        # column 1 = Component
        # column 2 = highest release
        # column 3-n = release of computer in comparison

        tablen = len(self.rptlist)
        addrow = True
        for i in range (0, tablen):
            if vendor == self.rptlist[i][0] and component == self.rptlist[i][1]:
                if len(self.rptlist[i]) != col_offset + 1:
                    for j in range (len(self.rptlist[i]),col_offset):
                        self.rptlist[i].append("N/A")
                    self.rptlist[i].append(release)
                    if release > self.rptlist[i][2]:
                        self.rptlist[i].pop(2)
                        self.rptlist[i].insert(2,release)
                        
                    addrow = False
                break
        if addrow:
            self.rptlist.append([vendor,component,release])
            for j in range (3,col_offset):
                self.rptlist[tablen].append("N/A")
            self.rptlist[tablen].append(release)

    def fillwithNAplusSORT(self):
        # fill the blanks with N/A and sort on vendor, component
        tablen = len(self.rptlist)
        nrofcols = len(self.rptlist[0])
        self.rptlist.sort(key=lambda tup: (tup[0],tup[1]) )
        for i in range (0, tablen):
            if len(self.rptlist[i]) < nrofcols:
                for j in range (len(self.rptlist[i]),nrofcols):
                        self.rptlist[i].append("N/A")
        

       
         
# ===================================================================================================================================
 
# Initiate logging function and write first log messages
current_log = My_Logger()
logmsg = "-------------------"
current_log.log_msg(logmsg,"info",13)
logmsg = "Program start"
current_log.log_msg(logmsg,"info",14)

# get & set parameters & environment data
envir = config_data()

if not envir.OK:
    rccode = 2
    logmsg = "Program end with code = " + str(rccode)
    current_log.log_msg(logmsg,"info",25)
    sys.exit(rccode)

current_log.set_log(envir.logfile,envir.loglevel)
os.chdir(envir.Target_dir)


if envir.MyMode == 'create':
    
    # determine normal/abnormal end of previous run
    AmIbusy = Busy_Enqueue()
    
    AmIbusy.CleanEnq("previous")
    
    AmIbusy.StartEnq(envir.Target_dir + envir.wmictempfile)

    ch=subprocess.Popen("WMIC /output: " + envir.wmictempfile + " product get name,vendor,version",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output,err=ch.communicate()

    if err:
        errstr = err.decode("utf-8")
        logmsg = "WMIC file creation failed on " + envir.computer + " date " + envir.datestamp + " time " + envir.timestamp + " error text: " + errstr
        current_log.log_msg(logmsg,"critical",15)

        AmIbusy.CleanEnq("current")

        rccode = 3
    else:
        WMIC_dir = WMIC_dslist()                                         # initialize list structure

        WMIC_dir.copy_temp(envir.wmicfile,envir.wmictempfile)            # copy temp file to correct WMIC file

        WMIC_dir.fill_list()                                             # fill list structure with WMIC datasets
              
        WMIC_dir.del_obsolete(envir.compname,envir.generations)          # behoud voor deze computer max xx files
        
        AmIbusy.EndEnq()
    
        rccode = 0

elif envir.MyMode == "analyze":
    logmsg = "Analyze function entered"
    current_log.log_msg(logmsg,"info",17)

    Busy_status = Busy_list()

    Busy_status.check()
    
    while ((Busy_status.isbusy) and (Busy_status.loopcount <= envir.RetryCount)):
        logmsg = "One or more CREATE jobs are still busy. Clean-up will be attempted. Attempt number " + str(Busy_status.loopcount) + " of " + str(envir.RetryCount)
        current_log.log_msg(logmsg,"warning",33)
        Busy_status.clean()
        Busy_status.check()
        if Busy_status.isbusy :
            Busy_status.wait()
            
    if Busy_status.isbusy :
        logmsg = "Analyze cancelled due to persisting WMIC lock files"
        current_log.log_msg(logmsg,"warning",34)
        rccode = 5
        logmsg = "Program end with code = " + str(rccode)
        current_log.log_msg(logmsg,"info",25)
        sys.exit(rccode)

    WMIC_dir = WMIC_dslist()                                         # initialize list structure

    WMIC_dir.fill_list()                                             # fill list structure with WMIC datasets

    tobe_analyzed = []
    tobe_analyzed = WMIC_dir.get_last_WMICS()
    # print (tobe_analyzed)

    myrpt = report_matrix()
    # print (myrpt.rptlist[0])
   
    for item in tobe_analyzed:
        compname = item[0]
        dsname = item[1]
        f = open(dsname, 'rt',encoding="utf-16")
        eof = False
        firstrec = f.readline()
        namepos = firstrec.find("Name")
        nameval = firstrec[namepos:namepos+4]
        venpos = firstrec.find("Vendor")
        venval = firstrec[venpos:venpos+6]
        verspos = firstrec.find("Version")
        versval = firstrec[verspos:verspos+7]
        timestamp = dsname[-12:-4]
        # print (namepos,nameval,venpos,venval,verspos,versval)
        # print (len(firstrec), ">>> "+firstrec + " <<<")
        while not eof:
            nextrec = f.readline()
            if nextrec != "":
                if nextrec.strip() != '':                           # skip records with only spaces
                    
                    name_start = namepos
                    name_end = nextrec.find("   ",namepos,venpos)
                    if name_end == -1:
                        name_end = venpos - 1
                    nameval = nextrec[name_start:name_end].strip()
                    
                    ven_start = name_end + 1
                    ven_end = nextrec.find("   ",venpos,verspos)
                    if ven_end == -1:
                        ven_end = verspos - 1
                    venval = nextrec[ven_start:ven_end].strip()
                        
                    vers_start = ven_end + 1
                    vers_end = len(nextrec)
                    versval = nextrec[vers_start:vers_end].strip()
                    
                    # print ("Vendor = ", venval, " Component = ", nameval, " Version = ", versval)
                    myrpt.stow_rec(compname, timestamp, venval, nameval, versval)

                                       
                    
            else:
                eof = True

                              
                            
        f.close()

    myrpt.fillwithNAplusSORT()

    myrpt.printit(50)
    myrpt.reportit(0,envir.rptfile)
    
    logmsg = "Analyze function completed"
    current_log.log_msg(logmsg,"info",37)

    rccode = 0

else:
    logmsg = "Something very wrong - corrupt parameters: " + envir.MyMode
    current_log.log_msg(logmsg,"critical",18)
    rccode = 4

logmsg = "Program end with code = " + str(rccode)
current_log.log_msg(logmsg,"info",25)

sys.exit(rccode)





 
