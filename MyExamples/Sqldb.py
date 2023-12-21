import pyodbc
import os
from datetime import datetime



cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=adhc-2\SQLEXPRESS;DATABASE=Sympa;TRUSTED_CONNECTION=YES')
cursor = cnxn.cursor()
cursor2 = cnxn.cursor()


# Check whether computer exists, if not, add it

query = "SELECT ComputerID,ComputerName,ComputerPurchaseDate FROM dbo.Computer WHERE ComputerName = ?" 
ComputerName = "Testcomputer"

cursor.execute(query, ComputerName)

row = cursor.fetchone()
if row:
    print (ComputerName + " exists already")
    ComputerID = row[0] 
else:
    print (ComputerName + " not found - will be inserted")
    query = "INSERT INTO dbo.Computer (ComputerName) VALUES (?)"
    cursor.execute(query, ComputerName)
    cursor.commit()
    cursor.execute("SELECT @@IDENTITY AS ID")
    ComputerID = cursor.fetchone()[0]    

print ('ComputerID = {0}'.format(ComputerID))

# Check whether vendor exists, if not, add it

query = "SELECT VendorID,VendorName FROM dbo.Vendor WHERE VendorName = ?" 
VendorName = "Testvendor"

cursor.execute(query, VendorName)

row = cursor.fetchone()
if row:
    print (VendorName + " exists already")
    VendorID = row[0]
else:
    print (VendorName + " not found - will be inserted")
    query = "INSERT INTO dbo.Vendor (VendorName) VALUES (?)"
    cursor.execute(query, VendorName)
    cursor.commit()
    cursor.execute("SELECT @@IDENTITY AS ID")
    VendorID = cursor.fetchone()[0]
    

print ('VendorID = {0}'.format(VendorID))

# Check whether component exists, if not, add it

query = "SELECT ComponentID,VendorID,ComponentName FROM dbo.Component WHERE ComponentName = ?" 
ComponentName = "Testcomponent"

cursor.execute(query, ComponentName)

row = cursor.fetchone()
if row:
    print (ComponentName + " exists already")
    ComponentID = row[0]
    VID = row[1]
    if (VID != VendorID) :
        print ("Vendor ID mismatch: VENDOR table contains {0}, COMPONENT table contains {1}".format(VendorID, VID))
    else:
        print ("Vendor ID matches: {0}".format(VendorID))
        
else:
    print (ComponentName + " not found - will be inserted")
    query = "INSERT INTO dbo.Component (ComponentName,VendorID) VALUES (?,?)"
    cursor.execute(query, ComponentName,VendorID)
    cursor.commit()
    cursor.execute("SELECT @@IDENTITY AS ID")
    ComponentID = cursor.fetchone()[0]
    

print ('ComponentID = {0}'.format(ComponentID))

# Check whether Installation exists, handle

Release = "Testrelease"

now = datetime.today()
qdatestring = now.strftime("%Y-%m-%d %H:%M:%S")
qdatestring = "2023-12-14 12:51:09"
print (qdatestring)

query = "SELECT ComputerID,ComponentID,Release,MeasuredDateTime,StartDateTime,EndDateTime,Count FROM dbo.Installation WHERE ComponentID = ? and ComputerID = ? and EndDateTime IS NULL"
cursor.execute(query, ComponentID, ComputerID)

rows = cursor.fetchall()
if rows:
    for row in rows:
        print (row.MeasuredDateTime)
        print ("Component " + ComponentName + " found on computer " + ComputerName)
        # Als de huidige measure date in het record staat, verhoog counter met 1 en update record
        if (row.MeasuredDateTime.strftime("%Y-%m-%d %H:%M:%S") == qdatestring) :
            print ("Record already in database with same MeasuredDateTime, update counter")
            newcount = row.Count + 1
            query = "UPDATE dbo.Installation SET count = ? WHERE ComputerID = ? and ComponentID = ? and Release = ? and StartDateTime = ?"
            cursor2.execute(query, newcount, ComputerID, ComponentID, Release, row.StartDateTime)
            cursor2.commit()
        else:
            print ("Record has older MeasuredDateTime, update MeasuredDateTime")
            query = "UPDATE dbo.Installation SET MeasuredDateTime = ? WHERE ComputerID = ? and ComponentID = ? and Release = ? and StartDateTime = ?"
            cursor2.execute(query, qdatestring, ComputerID, ComponentID, Release, row.StartDateTime)
            cursor2.commit()
else:
    print ("Component " + ComponentName + " not found on computer " + ComputerName +", add it") 
    query = "INSERT INTO dbo.Installation (ComputerID,ComponentID,Release,MeasuredDateTime,StartDateTime,EndDateTime,Count) Values(?,?,?,?,?,NULL,?)"
    cursor2.execute(query, ComputerID, ComponentID, Release,qdatestring,qdatestring,1)
    cursor2.commit()

# Set Enddate for all records that have not been updated so apparantly do not exist anymore
print ("Set enddates")
query = "UPDATE dbo.Installation SET EndDateTime = ? WHERE ComputerID = ? and MeasuredDateTime <> ?"
ended = cursor2.execute(query, qdatestring, ComputerID, qdatestring).rowcount
cursor2.commit()
print (str(ended) + " records have gotten an end date") 

print ("*** ENDED ***")
