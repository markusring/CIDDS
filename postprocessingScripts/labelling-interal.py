# Imports
import csv 
import sys
import pandas as pd 
from datetime import datetime

# Path to data
inputFileData = sys.argv[1]
inputFileAttacks = sys.argv[2]
outputFileData = sys.argv[3]

### Read the activites ###
attacks = pd.read_csv(inputFileAttacks,sep=",")
# convert to ms from 1.1.1970
attacks["startTime"] = attacks["start"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f").timestamp())
attacks["endTime"] = attacks["end"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f").timestamp())


# Add the labels 
def addLabels(srcIP, dstIP, time, srcPt, dstPt):
    # Default values if not attack hits 
    res = dict() 
    res['description'] = "---"
    res['attackID'] = "---"
    res['attack'] = "---"
    res['scan'] = "---"
    res['label'] = "normal"

    # skip spaces and tabs 
    ip1 = srcIP.strip()
    ip2 = dstIP.strip()
    pt1 = srcPt.strip()
    pt2 = dstPt.strip()
    
    found = False
    bothIntern = False
    
    # both intern? 
    if (len(ip1) >= 7 and ip1[0:7] == "192.168") and (len(ip2) >= 7 and ip2[0:7] == "192.168"):
        bothIntern = True

    # we only attacked intern ip addresses
    if bothIntern: 
        return res
    
    # Handle special case of network drive --> label traffic to the network drive as normal 
    if ((ip1 == "192.168.100.5" and pt1 == "445") or (ip2 == "192.168.100.5" and pt2 == "445")):
        return res


    # Iterate through all executed attacks 
    for row in attacks.iterrows(): 
        start = (row[1]).get('startTime')
        end   = (row[1]).get('endTime')
        attackerIP = (row[1]).get('IP')
        #add buffer of 20 seconds
        start = start - 20
        end = end + 20
 
        if time > start and time < end: 
            if ip1 == attackerIP or ip2 == attackerIP:                     
                res['description'] = (row[1]).get('description')
                res['attackID'] = (row[1]).get('activityID')
                res['attack'] = (row[1]).get('activity')
                                    
                if ip1 == attackerIP: 
                    res['label'] = "attacker"
                else: 
                    res['label'] = "victim" 
                return res
    # If not attack hits
    return res
    


# Open the result file 
with open(outputFileData, 'w') as res: 
    writer = csv.writer(res)
    
    # Open the file with the unlabelled flows 
    with open(inputFileData, 'r') as fl: 
        reader = csv.reader(fl, delimiter=',')
        firstLine = True
        for row in reader:
            try:
                # Iterate through each line 
                if firstLine == True : 
                    firstLine = False
                    writer.writerow(row+['label','attack','attackID','attackDescription'])
                    continue
                # Read the value 
                datefirstseen = row[0]
                duration = row[1]
                proto = row[2]
                srcIPAddr = row[3]
                srcPt = row[4]
                dstIPAddr = row[5]
                dstPt = row[6]
                packets = row[7]
                bbytes = row[8]
                flows = row[9]
                flags = row[10]
                tos = row[11]
                time = datetime.strptime(datefirstseen, "%Y-%m-%d %H:%M:%S.%f").timestamp()
                                
                # Assign labels 
                srcIPAddr = srcIPAddr.strip()
                res = addLabels(srcIPAddr,dstIPAddr,time,srcPt, dstPt)
                
                # Write the  line 
                writer.writerow([datefirstseen,duration,proto,srcIPAddr,srcPt,dstIPAddr,dstPt,packets,bbytes,flows,flags,tos,res['label'],res['attack'],res['attackID'],res['description']])
        
            except Exception as e:
                print("Error")
                with open("labelling_errors.log", "a") as ef:
                    ef.write(str(e) + "\nROW: " + str(row[0]) + "\n")
                
