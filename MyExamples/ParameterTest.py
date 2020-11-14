import subprocess
import json

myscript = '& "' + "D:/AartenHetty/OneDrive/ADHC Development/Powershell/MyExamples/ParameterTest.ps1"+ '"'


ch = subprocess.Popen(["powershell.exe", "-noprofile","-command",myscript, "YES", "NO", '"weet ik veel"' ],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE, universal_newlines = True)
out,err = ch.communicate()

print ("Out = " )
print (out)
print ("Err = ")
print (err)

result = json.loads(out)

a = result['Message']

b = result['OK']
if b:
    print ("OK")
else:
    print ("NOK")

print (a)


