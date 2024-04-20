import re
mach =  'Microsoft \.NET 8\.0-Templates \d+\.\d+\.\d+ \(x64\)'
p = re.compile(mach)
print (p)
mystr = 'Microsoft .NET 8.0-Templates 6.0.127 (x64)'
# mystr = 'xxx'
m = p.match(mystr)
print (m)
if (m is None):
    print ("Noppes")
else :
    print (m .group())
    start = m.span()[0]
    end = m.span()[1]
    length = end - start
    print (length)
    strl = len(mystr)
    print (strl)
    if (m.group() == mystr):
        print ("joepie") 
