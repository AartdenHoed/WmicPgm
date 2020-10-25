import subprocess
import sys
import json
ch = subprocess.Popen(["powershell.exe", "-noprofile","-command",'& "D:/AartenHetty/OneDrive/ADHC Development/Powershell/InitVar.ps1"', "YES" ],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE, universal_newlines = True)

out,err = ch.communicate()

jsonstring = out
print(jsonstring)

initvar = json.loads(jsonstring)
print(initvar['ADHC_Computer'])
print(initvar['ADHC_User'])
