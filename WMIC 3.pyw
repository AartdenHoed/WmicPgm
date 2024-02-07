import sys
import getopt
import os
import subprocess
import logging
import time
import json
from operator import itemgetter
from datetime import datetime
from shutil import copyfile
from pathlib import Path

# ===================================================================================================================
class config_data:
    def __init__(self):
        # sys.argv = ['The python file', '--mode=analyze' ,'--outputdir=O:/ADHC Output/WmicFiles/']        
        # sys.argv = ['The python file', '--mode=create' ,'--outputdir=O:/ADHC Output/WmicFiles/']
        
        # sys.argv = ['The python file', '--mode=analyze']
        # sys.argv = ['The python file', '--mode=create', '--loglevel=info']
                
        # sys.argv = ['The python file', '--mode=create']
        # sys.argv = ['The python file', '--mode=dbload']
        # sys.argv = ['The python file', '--mode=analyze']
        
        # Determine other environment variables
        self.Version = "Version 02 Release 06.04"
        self.PythonVersion = sys.version
       
        self.PythonFile = os.path.realpath(__file__)
        self.PythonDirectory, self.PythonModule = os.path.split(self.PythonFile)
        self.PythonBase = os.path.basename(os.path.normpath(self.PythonDirectory))
        self.Created = os.path.getmtime(self.PythonFile)
        self.CreatedStr = time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(self.Created))
        logmsg = "Python Version: " + self.PythonVersion
        current_log.log_msg(logmsg,"info",50)
        logmsg = "Python file: " + self.PythonFile + " - Created: " + self.CreatedStr + " - Source " + self.Version
        current_log.log_msg(logmsg,"info",00)
      
        now = datetime.today()
        self.datestamp = now.strftime("%A %d %b %Y")
        self.timestamp = now.strftime("%H:%M")

        # invoke INITVAR
        parts = self.PythonBase.split(".")
        replacement = "Powershell"
        for p in parts :
            if (p.upper() == "GIT"):
                replacement = "Powershell.git"
                                
        initvar = '& "' + self.PythonFile.replace(self.PythonModule,"").replace(self.PythonBase, replacement) + 'INITVAR.PS1"'
        logmsg = "INITVAR will be invoked: " + initvar
        # print (logmsg)
        current_log.log_msg(logmsg,"info",51)
                        
        ch = subprocess.Popen(["powershell.exe", "-noprofile","-command",initvar, "YES" ],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE, universal_newlines = True)
        out,err = ch.communicate()

        jsonstring = out
        # print("JSON string = " + jsonstring)

        self.ADHCvariables = json.loads(jsonstring)

        self.Target_dir =  self.ADHCvariables['ADHC_WmicDirectory']
        
        self.computer = self.ADHCvariables['ADHC_Computer']
        self.compname = self.computer.replace("-", "_")
        self.generations = int(self.ADHCvariables['ADHC_WmicGenerations'])

        self.analysisfile = "Analysis_Copy_"+ self.compname + ".txt"

        self.wmicdbload = self.ADHCvariables["ADHC_WmicDbload"]

        self.outputdirectory = self.ADHCvariables['ADHC_OutputDirectory']
        self.wmictempdir = self.ADHCvariables['ADHC_WmicTempdir']
        self.jobstatus = self.ADHCvariables['ADHC_Jobstatus']
       
        self.MyMode = "create"
        self.loglevel = "info"

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
                    elif arg.lower() == "dbload":
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
                        self.Target_dir = arg.replace("\\\\", "/").replace("\\","/")
                        # print(self.Target_dir)                              
                else:
                    logmsg = "Wrong parameter ignored: " + opt + arg
                    current_log.log_msg(logmsg,"warning",6)
        
        if ( not os.path.isdir(self.wmictempdir)):
            os.makedirs(self.wmictempdir)
        self.logfile = self.Target_dir + "WMIC_" + self.compname + ".log"
        self.logtemp = self.wmictempdir + "WMIC_" + self.compname + ".log"
        
        self.rptfile = self.Target_dir + "Current_WMIC_Report.txt"
        self.rpttemp = self.wmictempdir + "Current_WMIC_Report.txt"
        self.wmictempname = "TempWMICoutput.txt"
        self.wmictempfull = self.wmictempdir + self.wmictempname
        # print (self.wmictempfull)

        self.JobProcess = "Wmic" + self.MyMode.capitalize()
        self.MyJob = Jobstatus()
        
        yyyymmdd = now.strftime("%Y%m%d")
        self.wmicfile = "WMIC_" + self.compname + "_" + yyyymmdd + ".txt"
                
        logmsg = "Mode = " + self.MyMode 
        current_log.log_msg(logmsg,"info",7)
        if self.MyMode == "create":
            logmsg = "Outputdir = " + self.Target_dir + " (number of generations = " + str(self.generations) + ")"
            current_log.log_msg(logmsg,"info",8)
        self.OK = True

# ====================================================================================================================

class Jobstatus:
    
    def writestatus (self, outputdir, subdir, computername, process, errlevel, version, emsg):
        jobstatusfile = outputdir + subdir + computername + "_" + process + ".jst"
        if os.path.exists(jobstatusfile):
            logmsg = "Jobstatus file = " + jobstatusfile
            current_log.log_msg(logmsg,"info",52)            
        else:
            logmsg = "Jobstatus file " + jobstatusfile + " created."
            current_log.log_msg(logmsg,"info",53)
        joboutput = open(jobstatusfile, "w", encoding="utf-8")

        if (errlevel == "E"):
            errnum = 9
        elif (errlevel == "L"):
            errnum = 7
        elif (errlevel == "W"):
            errnum = 6
        elif (errlevel == "I"):
            errnum = 0
        else:
            logmsg = "Errolevel not recognized: "   + errlevel
            current_log.log_msg(logmsg,"error",54)
            errnum = 9

        now = datetime.today()
        dt = now.strftime("%d-%m-%Y %H:%M:%S")
                
        jobrecord = computername + "|" + process + "|" + str(errnum) + "|" + version + "|" + dt

        joboutput.write(jobrecord)
        joboutput.write("\n")
        joboutput.write(emsg)

        joboutput.close()      

# ====================================================================================================================

class My_Logger:
    def __init__(self):
        self.Logger = logging.getLogger("Sympa")
        self.msglist = []
        self.logfile = "none"
        self.loglvl = "info"
        self.logset = False
        
    def set_log(self,defdataset,tempdataset,lvl):
        self.logfile = defdataset
        self.logfileOLD = defdataset + "old"
        self.logtemp = tempdataset
        if os.path.exists(tempdataset):
            os.remove(tempdataset)
            logmsg = "Previous temporary logdataset " + tempdataset + " deleted."
            self.log_msg(logmsg, "info",60)
        if os.path.exists(self.logfile):
            logsize = os.path.getsize(self.logfile)
        else:
            logsize = 0
            logmsg = "Logdataset " + self.logfile + " will be created."
            self.log_msg(logmsg, "info",41)
        if logsize > 1024*1024:
            if os.path.exists(self.logfileOLD):
                os.remove(self.logfileOLD)
                logmsg = "OLD logdataset " + self.logfileOLD + " deleted."
                self.log_msg(logmsg, "info",38) 
            os.rename(self.logfile, self.logfileOLD)
            logmsg = "Logdataset " + self.logfile + " renamed to " + self.logfileOLD
            self.log_msg(logmsg, "info",39)
        else:
            logmsg = "Current logdataset (" + self.logfile + ") size is " + str(logsize) + " bytes."
            self.log_msg(logmsg, "info",40)
        self.loglvl = lvl
        self.logset = True
        logging.basicConfig(filename=self.logtemp)
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

    def log_append(self):
        # append temp logfile to definitive logfile
        logmsg = "Temporary logfile " + self.logtemp + " will be appended to " + self.logfile + " now."
        self.log_msg(logmsg, "info",60) 
        
              
        self.CopyMoveScript = envir.ADHCvariables['ADHC_CopyMoveScript']
        myscript = '& "' + self.CopyMoveScript + '"'
        t = '"' + self.logtemp + '"'
        o = '"' + self.logfile + '"'
        # print (t)
        # print (o)
        ch = subprocess.Popen(["powershell.exe" , "-noprofile" , "-command" , myscript, t, o , "COPY", "APPEND" ,"JSON" ],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE, universal_newlines = True)
        out,err = ch.communicate()
               
        msgstring = out
        # print("Msgstring = " + msgstring)

        msglist = json.loads(msgstring)
        errflag = False
        for msgentry in msglist:
            lvl = msgentry['Level']
            msg = msgentry['Message']
            if lvl == "I":
                mlvl = "info"
            elif lvl == "A":
                mlvl = "info"
            elif lvl == "N":
                mlvl = "info"
            else:
                mlvl = "critical"
                errmsg = msg
                errflag = True
            # print (msg)
            current_log.log_msg(msg,mlvl,99)
        
        if errflag:
            endmsg = "LOG copy-append action failed: " + errmsg
            envir.MyJob.writestatus(envir.outputdirectory, envir.jobstatus, envir.computer, envir.JobProcess, "E", envir.Version,endmsg) 
            print ("** ENDED ** " + endmsg)
            sys.exit(endmsg)          
        

# ===================================================================================================================

class Enqueue:    
        
    def __init__(self):
        self.BusyWaitTime = "10"        
        self.LockScript = envir.ADHCvariables['ADHC_LockScript']
       
        # print (self.LockScript)
                
    def StartEnq(self):
        # print ("start")
        self.Error = False
        script = self.LockScript 
        # print (script)
        # print (envir.JobProcess)

        myscript = '& "' + self.LockScript + '"'
        ch = subprocess.Popen(["powershell.exe" , "-noprofile" , "-command" , myscript, "LOCK" , "WMIC", envir.JobProcess, self.BusyWaitTime , "JSON"],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE, universal_newlines = True)
        out,err = ch.communicate()
        
        msgstring = out
        # print(msgstring)

        msglist = json.loads(msgstring)

        errflag = False
        for msgentry in msglist:
            lvl = msgentry['Level']
            # print(lvl)
            msg = msgentry['Message']
            # print(msg)
            if lvl == "I":
                mlvl = "info"
            elif lvl == "A":
                mlvl = "info"
            elif lvl == "N":
                mlvl = "info"
            else:
                mlvl = "critical"
                errmsg = msg
                errflag = True
            
            current_log.log_msg(msg,mlvl,99)

        # Force abnormal end if ENQ fails. Logging impossible
        if errflag:
            endmsg = "Locking resource WMIC failed: " + errmsg
            envir.MyJob.writestatus(envir.outputdirectory, envir.jobstatus, envir.computer, envir.JobProcess, "L", envir.Version,endmsg) 
            print ("** ENDED ** " + endmsg)
            sys.exit(endmsg)           
       
    
    def FreeEnq(self):
        myscript = '& "' + self.LockScript + '"'
        ch = subprocess.Popen(["powershell.exe" , "-noprofile" , "-command" , myscript, "FREE" , "WMIC", envir.JobProcess, self.BusyWaitTime , "JSON"],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE, universal_newlines = True)
        out,err = ch.communicate()
        
        # Get messages
        msgstring = out
        # print(msgstring)

        msglist = json.loads(msgstring)

        errflag = False
        for msgentry in msglist:
            lvl = msgentry['Level']
            msg = msgentry['Message']
            if lvl == "I":
                mlvl = "info"
            elif lvl == "A":
                mlvl = "info"
            elif lvl == "N":
                mlvl = "info"
            else:
                mlvl = "critical"
                errflag = True
            
            current_log.log_msg(msg,mlvl,99)

        # Set ERROR flag or not depending on error message
        if errflag:
            logmsg = "FREEing WMIC resource failed"
            current_log.log_msg(logmsg,"warning",34)
            self.Error = True

# =================================================================================================================== 

class WMIC_dbload: 
    def __init__(self):
        dbload = envir.ADHCvariables['ADHC_WmicDbload']

        self.Error = False
        if (dbload == "Y") :
            import pyodbc
            self.Active = True
            self.cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=adhc-2\SQLEXPRESS;DATABASE=Sympa;TRUSTED_CONNECTION=YES')
            self.cursor = self.cnxn.cursor()
            self.cursor2 = self.cnxn.cursor()
        else:
            self.Active = False
        
    def uniq(self,mystring, mylist):
        if (mystring in mylist):
            unique = False
        else:
            unique = True
            mylist.append(mystring)
        return unique

    def re_init(self):
        self.computer_exists = 0
        self.computer_added = 0
        self.vendor_exists = 0
        self.vendor_added = 0
        self.component_exists = 0
        self.component_added = 0
        self.processed_dsn = 0

        self.dsname = "init"
        self.skipped_dsn  = 0
        self.wronghost_dsn = 0
        
        self.install_count = 0
        self.install_date = 0
        self.install_added = 0
        self.install_ended = 0

        self.uniq_computer = []
        self.uniq_vendor = []
        self.uniq_component = []

    def header(self, header):
         
                
        self.comppos = header.find("Computer")
        self.compval = header[self.comppos:self.comppos+8]
        
        self.timepos = header.find("Timestamp")
        self.timeval = header[self.timepos:self.timepos+9]
        self.comp_end = self.timepos - 1

        self.idatepos = header.find("InstallDate")
        self.idateval = header[self.idatepos:self.idatepos+11]
        self.time_end = self.idatepos - 1

        self.ilocpos = header.find("InstallLocation")
        self.ilocval = header[self.ilocpos:self.ilocpos+15]
        self.idate_end = self.ilocpos - 1

        self.namepos = header.find("Name")
        self.nameval = header[self.namepos:self.namepos+4]
        self.iloc_end = self.namepos-1
        
        self.venpos = header.find("Vendor")
        self.venval = header[self.venpos:self.venpos+6]
        self.name_end = self.venpos - 1
             
        self.verspos = header.find("Version")
        self.versval = header[self.verspos:self.verspos+7]
        self.ven_end = self.verspos - 1

        self.vers_end = len(header)

        # print (self.compval, self.timeval, self.idateval, self.ilocval, self.nameval, self.venval, self.versval)
        
        

    def load (self,line,dsn,host):
        self.ok = "Ok"
        
        self.vers_end = len(line)
        ComputerName = line[self.comppos:self.comp_end]
        VendorName = line[self.venpos:self.ven_end]
        ComponentName = line[self.namepos:self.name_end]
        Release = line[self.verspos:self.vers_end]
        
        qdatestring = line[self.timepos:self.time_end]
        self.qd = qdatestring
        qdatetime = datetime.strptime(qdatestring.strip(), '%Y-%m-%d %H:%M:%S')
        
        InstallDate = line[self.idatepos:self.idate_end]
        InstallLocation = line[self.ilocpos:self.iloc_end]

        # check whether this dataset is for this host
        if (host.strip().replace("_","-") != ComputerName.strip().replace("_","-")):
            self.wronghost_dsn = self.wronghost_dsn + 1
            self.ok = "Wrong host"
            return (self.ok)

        # check whether this dataset already has been processed

        if (self.dsname != dsn):
            self.dsname = dsn

            query = """SELECT a.ComputerName, b.MeasuredDateTime
                        from dbo.Computer a, dbo.Installation b
                        where a.ComputerID = b.ComputerID and a.ComputerName = ? and b.MeasuredDateTime >= ? """
            self.cursor.execute(query, ComputerName, qdatestring)
            row = self.cursor.fetchone()
            if row:                             # dataset already processed, return directly
                self.ok = "Contains older timestamps"                
                self.skipped_dsn  = self.skipped_dsn + 1
                return (self.ok)
            else:
                self.processed_dsn = self.processed_dsn + 1              

        # Check whether computer exists, if not, add it

        query = "SELECT ComputerID,ComputerName,ComputerPurchaseDate FROM dbo.Computer WHERE ComputerName = ?" 
        self.cursor.execute(query, ComputerName)

        row = self.cursor.fetchone()
        if row:
            # print (ComputerName + " exists already")
            ComputerID = row[0]
            if (self.uniq(ComputerName,self.uniq_computer)):
                self.computer_exists = self.computer_exists + 1
        else:
            print (ComputerName + " not found - will be inserted")
            query = "INSERT INTO dbo.Computer (ComputerName) VALUES (?)"
            self.cursor.execute(query, ComputerName)
            self.cursor.commit()
            self.cursor.execute("SELECT @@IDENTITY AS ID")
            ComputerID = self.cursor.fetchone()[0]
            if (self.uniq(ComputerName,self.uniq_computer)):
                self.computer_added = self.computer_added + 1
            
            print ('ComputerID = {0}'.format(ComputerID))
        self.cid = ComputerID

        # Check whether vendor exists, if not, add it

        query = "SELECT VendorID,VendorName FROM dbo.Vendor WHERE VendorName = ?" 
        self.cursor.execute(query, VendorName)

        row = self.cursor.fetchone()
        if row:
            # print (VendorName + " exists already")
            VendorID = row[0]
            if (self.uniq(VendorName,self.uniq_vendor)):
                self.vendor_exists = self.vendor_exists + 1        
        else:
            print (VendorName + " not found - will be inserted")
            query = "INSERT INTO dbo.Vendor (VendorName) VALUES (?)"
            self.cursor.execute(query, VendorName)
            self.cursor.commit()
            self.cursor.execute("SELECT @@IDENTITY AS ID")
            VendorID = self.cursor.fetchone()[0]
            if (self.uniq(VendorName,self.uniq_vendor)):
                self.vendor_added = self.vendor_added + 1

            print ('VendorID = {0}'.format(VendorID))

        # Check whether component exists, if not, add it

        query = "SELECT ComponentID,VendorID,ComponentName FROM dbo.Component WHERE ComponentName = ?" 
        self.cursor.execute(query, ComponentName)

        row = self.cursor.fetchone()
        if row:
            # print (ComponentName + " exists already")
            ComponentID = row[0]
            VID = row[1]
            if (VID != VendorID) :
                logmsg = "Vendor ID mismatch: VENDOR table contains {0}, COMPONENT table contains {1}".format(VendorID, VID)
                print (logmsg)
                current_log.log_msg(logmsg,"error",85)
                self.Error = True
            else:
                a=1
                # print ("Vendor ID matches: {0}".format(VendorID))
            if (self.uniq(ComponentName,self.uniq_component)):
                self.component_exists = self.component_exists + 1        
        else:
            print (ComponentName + " not found - will be inserted")
            query = "INSERT INTO dbo.Component (ComponentName,VendorID) VALUES (?,?)"
            self.cursor.execute(query, ComponentName,VendorID)
            self.cursor.commit()
            self.cursor.execute("SELECT @@IDENTITY AS ID")
            ComponentID = self.cursor.fetchone()[0]
            if (self.uniq(ComponentName,self.uniq_component)):
                self.component_added = self.component_added + 1

            print ('ComponentID = {0}'.format(ComponentID))

        # Check whether Installation exists, handle   
 
        query = """SELECT ComputerID,ComponentID,Release,Location,InstallDate,MeasuredDateTime,StartDateTime,EndDateTime,Count
                    FROM dbo.Installation
                    WHERE Release = ? and ComponentID = ? and ComputerID = ? and EndDateTime IS NULL"""
        self.cursor.execute(query, Release, ComponentID, ComputerID)

        rows = self.cursor.fetchall()
        if rows:
            for row in rows:
                # print (row.MeasuredDateTime)
                # print ("Component " + ComponentName + " found on computer " + ComputerName)
                # Als de huidige measure date in het record staat, verhoog counter met 1 en update record
                if (row.MeasuredDateTime == qdatetime) :
                    # print ("Record already in database with same MeasuredDateTime, update counter")
                    newcount = row.Count + 1
                    query = "UPDATE dbo.Installation SET count = ? WHERE ComputerID = ? and ComponentID = ? and Release = ? and StartDateTime = ?"
                    self.cursor2.execute(query, newcount, ComputerID, ComponentID, Release, row.StartDateTime)
                    self.cursor2.commit()
                    self.install_count = self.install_count + 1       
                else:
                    # current measureddatetime MUST be less (older) qdatetime, because otherwise the dataset would have been skipped
                    # print ("Record has older MeasuredDateTime, update MeasuredDateTime and set count on 1")
                    query = """UPDATE dbo.Installation
                                SET MeasuredDateTime = ? , Count = 1 
                                WHERE ComputerID = ? and ComponentID = ? and Release = ? and StartDateTime = ?"""
                    self.cursor2.execute(query, qdatestring, ComputerID, ComponentID, Release, row.StartDateTime)
                    self.cursor2.commit()
                    self.install_date = self.install_date + 1        
        else:
            print ("Component " + ComponentName + " not found on computer " + ComputerName +", add it") 
            query = "INSERT INTO dbo.Installation (ComputerID,ComponentID,Release,InstallDate,Location,MeasuredDateTime,StartDateTime,EndDateTime,Count) Values(?,?,?,?,?,?,?,NULL,?)"
            self.cursor2.execute(query, ComputerID, ComponentID, Release,InstallDate,InstallLocation,qdatestring,qdatestring,1)
            self.cursor2.commit()
            self.install_added = self.install_added + 1

        return (self.ok)


    def end_dates(self):
        # Set Enddate for all records that have not been updated so apparantly do not exist anymore
        print ("Set enddates")
        query = "UPDATE dbo.Installation SET EndDateTime = ? WHERE ComputerID = ? and MeasuredDateTime < ? and EndDateTime IS NULL"
        self.install_ended = self.cursor2.execute(query, self.qd, self.cid, self.qd).rowcount
        
     
        
# ===================================================================================================================        

class WMIC_dslist:
    def __init__(self):
        self.complist = []
        self.CopyMoveScript = envir.ADHCvariables['ADHC_CopyMoveScript']

    # Test if this is a valid WMIC file
    def test (self, dsn):
        indic = dsn[0:5]
        extension = dsn[len(dsn)-4:len(dsn)]
        if (indic == "WMIC_") and (extension == ".txt"):
            return( True )
        else:
            return ( False )

    # copy temp file to current WMIC
    def copy_temp(self, dsn):
        tmpfile = envir.wmictempfull
        deffile = envir.Target_dir + dsn
        tst_file = Path(deffile)
        if tst_file.is_file():
            verb16 = "updated"
        else:
            verb16 = "created"
        logmsg = "WMIC file wil be " + verb16 + ": " + dsn
        current_log.log_msg(logmsg,"info",16)


        # copy temp file while addding prefix 
        
        infil = open(tmpfile, 'rt',encoding="utf-16")
        outfil = open(deffile, 'wt', encoding="utf-16")
        outfil2 = open(envir.analysisfile, 'wt', encoding="utf-16")
        nrofrecs = 0
        eof = False
        now = datetime.today()
        timestring = now.strftime("%Y-%m-%d %H:%M:%S")
        head1 = "Computer"
        head2 = "Timestamp"
        lenhead1 = max(len(head1.strip()),len(envir.computer.strip()))
        lenhead2 = max(len(head2.strip()),len(timestring.strip()))
        prefix1 = head1.ljust(lenhead1+2) + head2.ljust(lenhead2+2)
        prefix2 = envir.computer.ljust(lenhead1+2) + timestring.ljust(lenhead2+2)              
        while not eof:
            nextrec = infil.readline()
            nrofrecs = nrofrecs + 1
            if nextrec != "":
                if nextrec.strip() != '':                           # skip records with only spaces
                   if (nrofrecs == 1):
                       prefrec = prefix1 + nextrec
                   else:                      
                       prefrec = prefix2+ nextrec
                   # print(prefrec)
                   outfil.write(prefrec)
                   outfil2.write(prefrec)
            else:
                eof = True
            
        infil.close()
        outfil.close()
        outfil2.close()
        logmsg = str(nrofrecs) + " Records have been copied from " + tmpfile + " to " + deffile
        current_log.log_msg(logmsg,"info",82)

        os.remove (tmpfile)
        logmsg = tmpfile + " Has been deleted"
        current_log.log_msg(logmsg,"info",83)

        
       

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
        self.complist.sort(key=itemgetter(0))
        for item in self.complist:
            item[1].sort(key=itemgetter(2)) # most recent file LAST
        # print (self.complist)

    # Fill a list with the most recent WMIC file for each computer
    def get_AnalysisFiles(self):
        recents = []
        for dirname, dirnames, filenames in os.walk('.'):
            for filename in filenames:                      
                if (filename[0:13] == "Analysis_Copy"):    # is het een geldige Analyse file                          
                    recents.append(filename)               # zo ja, voeg toe aan object WMIC_dir
                    
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
        self.CopyMoveScript = envir.ADHCvariables['ADHC_CopyMoveScript']
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
            # print (str(nrofcols))
            formit = "{0:" + str(maxwidths[0]+2) + "}  {1:" + str(maxwidths[2]+2) + "}"
            print (formit.format(self.rptlist[i][0],self.rptlist[i][2]),end="" )
            maxrel = self.rptlist[i][2]
            # print (maxrel)
            for j in range (3,nrofcols):
                currel = self.rptlist[i][j]
                if currel != maxrel and i > 2 and currel != "N/A":
                    currel = currel + "  <=== "
                formit = "{:" + str(maxwidths[j]+8) + "}"
                print(formit.format(currel) ,end="")
            formit = "{:" + str(maxwidths[1]+2) + "}"
            print (formit.format(self.rptlist[i][1]))
        
    def reportit(self,nrofrecs,tempfile,outfile):
        maxwidths = self.getcolwidth()
        f = open(tempfile, 'wt', encoding="utf-16")
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
        # copy temp report to definitive location
        myscript = '& "' + self.CopyMoveScript + '"'

        t = '"' + tempfile + '"'
        o = '"' + outfile + '"'
        ch = subprocess.Popen(["powershell.exe" , "-noprofile" , "-command" , myscript, t, o, "MOVE", "REPLACE" ,"JSON"],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE, universal_newlines = True)
        out,err = ch.communicate()

        msgstring = out
        # print(msgstring)

        msglist = json.loads(msgstring)

        errflag = False
        for msgentry in msglist:
            lvl = msgentry['Level']
            msg = msgentry['Message']
            if lvl == "I":
                mlvl = "info"
            elif lvl == "A":
                mlvl = "info"
            elif lvl == "N":
                mlvl = "info"
            else:
                mlvl = "critical"
                errmsg = msg
                errflag = True
            
            current_log.log_msg(msg,mlvl,99)

        if errflag:
            endmsg = "Report move action failed: " + errmsg
            envir.MyJob.writestatus(envir.outputdirectory, envir.jobstatus, envir.computer, envir.JobProcess, "E", envir.Version,endmsg) 
            print ("** ENDED ** " + endmsg)
            sys.exit(endmsg)           

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

    envir.MyJob.writestatus(envir.outputdirectory, envir.jobstatus, envir.computer, envir.JobProcess, "E", envir.Version,logmsg) 
    print ("** ENDED ** rccode = " + str(rccode))    
    sys.exit(rccode)

# Lock resource WMIC
MyLock = Enqueue()
MyLock.StartEnq()

current_log.set_log(envir.logfile,envir.logtemp,envir.loglevel)                    # start physically writing messages after ENQ succeeded



os.chdir(envir.Target_dir)

if envir.MyMode == 'create':
    logmsg = "Create function entered"
    current_log.log_msg(logmsg,"info",17)
    # print (envir.wmictempname)
    os.chdir(envir.wmictempdir)
    ch=subprocess.Popen("WMIC /output: " + envir.wmictempname + " product get Name,Vendor,Version,InstallLocation,InstallDate",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output,err=ch.communicate()
    os.chdir(envir.Target_dir)

    if err:
        errstr = err.decode("utf-8")
        logmsg = "WMIC file creation failed on " + envir.computer + " date " + envir.datestamp + " time " + envir.timestamp + " error text: " + errstr
        current_log.log_msg(logmsg,"critical",15)

        rccode = 3
    else:
        WMIC_dir = WMIC_dslist()                                         # initialize list structure

        WMIC_dir.copy_temp(envir.wmicfile)                               # copy temp file to correct WMIC file + prefix

        WMIC_dir.fill_list()                                             # fill list structure with WMIC datasets
              
        WMIC_dir.del_obsolete(envir.compname,envir.generations)          # behoud voor deze computer max xx files

        logmsg = "Create function completed"
        current_log.log_msg(logmsg,"info",37)
        
        rccode = 0

elif envir.MyMode == "dbload":
    logmsg = "DB load function entered"
    current_log.log_msg(logmsg,"info",17)

    rccode = 0
    # print (str(rccode))

    dbloadobj = WMIC_dbload()
    
    if (dbloadobj.Active) :
        logmsg = "Current node able to execute db function"
        current_log.log_msg(logmsg,"info",80)
    else:
        logmsg = "Db function can not be executed on this node"
        current_log.log_msg(logmsg,"error",81)
        rccode = 6

    if (rccode == 0) :
        WMIC_dir = WMIC_dslist()                                         # initialize list structure with WMIC datasets
        WMIC_dir.fill_list()                                             # fill list structure with WMIC datasets

    # walk through computers, per computer through datasets (last is most recent and must be kept) and load in db

    for c in WMIC_dir.complist :

        logmsg = "Processing host " + c[0]
        print (logmsg)            
        current_log.log_msg(logmsg,"info",89)

        dbloadobj.re_init()
        
        for tuple in c[1]:
            
            
            curds = tuple[0]
                     
            firstrec = True
            inds = open(curds, 'rt',encoding="utf-16")
            eof = False
            while not eof:
                
                nextrec = inds.readline()
                if nextrec != "":
                    if firstrec :
                        dbloadobj.header(nextrec)                       # give column positions for future use
                        firstrec = False
                    else:
                        
                        goodfile = dbloadobj.load(nextrec,curds,c[0])       # give line of values to load in db
                        if (goodfile != "Ok"):
                            logmsg = "Input file " + curds +  " has been skipped (" + goodfile + ")"
                            print (logmsg)            
                            current_log.log_msg(logmsg,"info",87)
                            eof = True
                else:
                    eof = True
            
            inds.close()
            os.remove(curds)
            logmsg = "Input file " + curds +  " now deleted"
            print (logmsg)
            
            current_log.log_msg(logmsg,"info",86)

        if (goodfile == "Ok") :                                                     # only if file has not been skipped
            dbloadobj.end_dates()                                           # set end dates for non found components on this computer

        dsntotal = dbloadobj.processed_dsn + dbloadobj.skipped_dsn + dbloadobj.wronghost_dsn
        logmsg = "Total datasets = "+ str(dsntotal) + " *** processed = " + str(dbloadobj.processed_dsn) + " *** skipped (too old) = " + str(dbloadobj.skipped_dsn) + " *** skipped (wrong host) " + str(dbloadobj.wronghost_dsn)
        print (logmsg)
        current_log.log_msg(logmsg,"info",88)

        computertotal = dbloadobj.computer_exists + dbloadobj.computer_added 
        logmsg = "Total computers = "+ str(computertotal) + " *** existing = " + str(dbloadobj.computer_exists) + " *** added = " + str(dbloadobj.computer_added)
        print (logmsg)
        current_log.log_msg(logmsg,"info",88)
        
        vendortotal = dbloadobj.vendor_exists +   dbloadobj.vendor_added 
        logmsg = "Total vendors = "+ str(vendortotal) + " *** existing = " + str(dbloadobj.vendor_exists) + " *** added = " + str(dbloadobj.vendor_added)
        print (logmsg)
        current_log.log_msg(logmsg,"info",88)
        
        componenttotal = dbloadobj.component_exists + dbloadobj.component_added 
        logmsg = "Total components = "+ str(componenttotal) + " *** existing = " + str(dbloadobj.component_exists) + " *** added = " + str(dbloadobj.component_added)
        print (logmsg)
        current_log.log_msg(logmsg,"info",88)
        
        
        installtotal = dbloadobj.install_count + dbloadobj.install_date + dbloadobj.install_added + dbloadobj.install_ended 
        logmsg = "Total installations = "+ str(installtotal) +  " *** added = " + str(dbloadobj.install_added) + " *** actualized date = " + str(dbloadobj.install_date) + " *** counter updated = " + str(dbloadobj.install_count) + " *** ended = " + str(dbloadobj.install_ended)                   
        print (logmsg)
        current_log.log_msg(logmsg,"info",88)
        
 
elif envir.MyMode == "analyze":
    
    logmsg = "Analyze function entered"
    current_log.log_msg(logmsg,"info",17)
    WMIC_dir = WMIC_dslist()                                         # initialize list structure

    tobe_analyzed = []
    tobe_analyzed = WMIC_dir.get_AnalysisFiles()
    # print (tobe_analyzed)

    myrpt = report_matrix()
    # print (myrpt.rptlist[0])
        
    for dsname in tobe_analyzed:
        
        f = open(dsname, 'rt',encoding="utf-16")
        eof = False
        firstrec = f.readline()
        namepos = firstrec.find("Name")
        nameval = firstrec[namepos:namepos+4]
        venpos = firstrec.find("Vendor")
        venval = firstrec[venpos:venpos+6]
        verspos = firstrec.find("Version")
        versval = firstrec[verspos:verspos+7]
        comppos = firstrec.find("Computer")
        compval = firstrec[comppos:comppos+7]
        timepos = firstrec.find("Timestamp")
        timeval = firstrec[timepos:timepos+9]
        name_end = venpos - 1
        ven_end = verspos - 1
        comp_end = timepos - 1
        time_end = timepos + 19
        
        # print (namepos,nameval,venpos,venval,verspos,versval)
        # print (len(firstrec), ">>> "+firstrec + " <<<")
        while not eof:
            nextrec = f.readline()
            if nextrec != "":
                if nextrec.strip() != '':                           # skip records with only spaces
                    
                    nameval = nextrec[namepos:name_end].strip()
                    compname  = nextrec[comppos:comp_end].strip()
                    timestamp = nextrec[timepos:time_end].strip()
                    
                    venval = nextrec[venpos:ven_end].strip()

                    vers_end = len(nextrec)
                    versval = nextrec[verspos:vers_end].strip()
                    
                    # print ("Vendor = ", venval, " Component = ", nameval, " Version = ", versval, "Computer = ",compname," Timestamp = ", timestamp )
                    myrpt.stow_rec(compname, timestamp, venval, nameval, versval)
                    
            else:
                eof = True
            
        f.close()

    myrpt.fillwithNAplusSORT()

    myrpt.printit(50)
    # print (envir.rpttemp)
    # print(envir.rptfile)
    myrpt.reportit(0,envir.rpttemp,envir.rptfile)
    
    logmsg = "Analyze function completed"
    current_log.log_msg(logmsg,"info",37)

    rccode = 0

else:
    logmsg = "Something very wrong - corrupt parameters: " + envir.MyMode
    current_log.log_msg(logmsg,"critical",18)
    
    rccode = 4

logmsg = "Program end with code = " + str(rccode)
current_log.log_msg(logmsg,"info",25)

if (rccode > 0) :
    envir.MyJob.writestatus(envir.outputdirectory, envir.jobstatus, envir.computer, envir.JobProcess, "E", envir.Version,logmsg)
else:
    envir.MyJob.writestatus(envir.outputdirectory, envir.jobstatus, envir.computer, envir.JobProcess, "I", envir.Version,logmsg)

MyLock.FreeEnq()
current_log.log_append()

if MyLock.Error:
    rccode = 5
print ("** ENDED ** rccode = " + str(rccode))  
sys.exit(rccode)





 
