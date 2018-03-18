#!/usr/bin/python

import re,string,sys
fulllist_glob = []
fullfunction_glob = []


def banner():
   print "-" * 70
   print """
 _    _ _     _      __  __       _____   _____ 
| |  | (_)   | |    |  \/  |     |  __ \ / ____|
| |__| |_  __| | ___| \  / |_   _| |__) | (___  
|  __  | |/ _` |/ _ \ |\/| | | | |  ___/ \___ \ 
| |  | | | (_| |  __/ |  | | |_| | |     ____) |
|_|  |_|_|\__,_|\___|_|  |_|\__, |_|    |_____/ 
              __/ |        
             |___/          

[-]PowerShell Encoding Tool
[-]Written by Peter Kim
"""
try:
   source = sys.argv[1]
   destination = sys.argv[2]
   f = open(source,'r')
   wr = open(destination,'w')

except IndexError:
   banner()
   print "[-]Usage: python hidemyps.py <source file> <output file>"
   print "[-]Example: python hidemyps.py mimikatz.ps1 hidemimkatz.ps1"
   sys.exit()

banner()
print "[*] Starting Encoding PowerShell Script"
print "[*] Modifying variables, function names, strings, removing comments"
full = []

#Taking every function name and variable and running ROT13 
#TODO: Create full list of variables to ignore

def rot(x):
   global fulllist_glob
   reg_line = re.findall('(\$\w+)',x)
   if len(reg_line) > 0:
      reg_line.sort(key=lambda item: (-len(item), item))
      for reg in reg_line:
         if (len(reg) > 3) and (reg.lower() != '$this') and (reg.lower() != '$args') and (reg.lower() != '$env') and (reg.lower() != '$global') and (reg.lower() != '$rawbytes') and (reg.lower() != '$pwd') and (reg.lower() != '$pid') and (reg.lower() != '$true') and (reg.lower() != '$false') and (reg.lower() != '$pscmdlet') and (reg.lower() != '$null'):
            reg_rot = reg.encode('rot13')
            fulllist_glob.append(reg)
            x = x.replace(reg,reg_rot)
   return x

#Cheat function to identify which variables or function names to sent to ROT13

def cleaner(x):
        global fullfunction_glob
        for ffg in fullfunction_glob:
                ffg = ffg.strip()
                fgg = " " + ffg + " "
                fgggg = "" + ffg + ""
                fggg = "(" + ffg + " "
                x_strip = x.strip()
                if (x_strip.startswith(ffg)) or (fggg in x) or (fgg in x) or (fgggg in x) or (x_strip.endswith(ffg)):
                    x = x.replace(ffg, ffg.encode('rot13'))
        return x

#For each line identify function names and send to ROT13

for x in f:
   xstrip = x.strip()  
 
   if (xstrip.lower().startswith("function ")) and ("unction local:" not in x.lower()):
      func = xstrip.split(' ',1)
      #print func[1]
      if "(" in func[1]:
        temp = func[1]
        temp = temp.split("(")
        func[1] = temp[0]
      fullfunction_glob.append(func[1])
      func_rot = func[1].encode('rot13')
      x = x.replace(func[1],func_rot)
   x = rot(x)
   full.append(x)
   
fulllist_glob = set(fulllist_glob)
fullfunction_glob = set(fullfunction_glob)
      
#TODO: Create full list of PowerShell default functions to put into whitelist

import base64
comment = 0
for q in full:
   if ("$erfhygf = Main;" == q.strip()):
      q = q.replace("Main","Znva") #This line is specific to the new version of Mimikatz
   if (comment == 1) or (q.strip() == "<#"):
      comment = 1
      if q.strip() == "#>":
         comment = 0
      continue 
   if "#" in q: #Removing comments from the PowerShell scripts
      qs = q.split("#",1)
      if '"' in qs[1]:
	    pass
      else:
		q = qs[0] + "\n"
   q = cleaner(q)
   for w in fulllist_glob:
      w = w[1:]
      w = w.strip()
      if (" -"+w+" " in q) and ("Add-Member" not in q):
         q = q.replace(" -"+w+" "," -"+w.encode('rot13')+" ") 
   if (".tostring" in q.lower()) or ("`" in q) or ("+" in q) or ("test-memoryrange" in q.lower()) or ("get-memoryprocaddress" in q.lower()):
      pass
   else:
      if ("write-verbose" in q.lower()) and ("$" in q) and ('"' in q):
         q_split = q.split("$",1)
         q_split[0] = q_split[0].replace('"','("')
         q_split[1] = q_split[1].replace('"','")')
         q = q_split[0] + '"+"$'+ q_split[1]
      elif (q[0] == '"') and ("$" in q) and ('"' in q):
         q_split = q.split("$",1)
         q_split[0] = q_split[0].replace('"','("')
         q_split[1] = q_split[1].replace('"','")')
         q = q_split[0] + '"+"$'+ q_split[1]
      else:
         quotes_fix = re.findall('"([^"]*)"', q)
         for qf in quotes_fix:
            if qf:
               firstpart, secondpart = qf[:len(qf)/2], qf[len(qf)/2:]
               q = q.replace('"'+qf+'"','("'+firstpart+'"+"'+secondpart+'")')
         tick_fix = re.findall("'([^']*)'", q)
         for qft in tick_fix:
            if (qft) and (len(qft) > 3):
               firstpart, secondpart = qft[:len(qft)/2], qft[len(qft)/2:]
               q = q.replace("'"+qft+"'","('"+firstpart+"'+'"+secondpart+"')")
   wr.write(q )
   
print "[*] Encoding Finished"
