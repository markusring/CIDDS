# Imports
import csv 
import sys
import pandas as pd 
from datetime import datetime

# Path to data
inputFileData = sys.argv[1]

if inputFileData == "--help" or inputFileData == "-help" or inputFileData == "--h" or inputFileData == "-h" or inputFileData == "":
    print("Usage: python labelling-external.py inputFlowFile.csv attackLogFile.csv outputFlowsFile.csv")
    exit()

inputFileAttacks = sys.argv[2]
outputFileData = sys.argv[3]

# Special IPs  
openStackIP = "333.333.333.333"
externalIP = "333.333.333.333"

def addLabels(srcIP, dstIP, time, srcPt, dstPt):
    # Set the default values if the flow is no attack   
    res = dict() 
    res['description'] = "---"
    res['attackID'] = "---"
    res['attack'] = "---"
    res['scan'] = "---"
    res['label'] = "normal"

    # STEP 1: All traffic from the OpenStack network is normal 
    if srcIP == openStackIP or dstIP == openStackIP: 
        return res

    # STEP 2: Is this flow executed attack by ourselfs?  
    # Iterate through all executed attacks 
    for row in attacks.iterrows(): 
        start = (row[1]).get('startTime')
        end   = (row[1]).get('endTime')
        attackerIP = (row[1]).get('IP')
        
        # add buffer of 10 seconds
        start = start - 10
        end = end + 10
 
        # Does this flow hit the time window and ip? 
        if time > start and time < end: 
            if srcIP == attackerIP or dstIP == attackerIP:                     
                res['description'] = (row[1]).get('description')
                res['attackID'] = (row[1]).get('activityID')
                res['attack'] = (row[1]).get('activity')
                    
                if srcIP == externalIP: 
                    res['label'] = "victim"
                else: 
                    res['label'] = "attacker" 
                return res

    # STEP 3: Label remaining traffic (Traffic to HTTP and HTTPs is unkown, the other traffic is suspicious)  
    if (srcIP == externalIP and srcPt == "80") or (dstIP == externalIP and dstPt == "80") or (srcIP == externalIP and srcPt == "443") or (dstIP == externalIP and dstPt == "443"): 
        res['label'] = "unknown"
    else: 
        res['label'] = "suspicious"
    return res

    

### Read the attacks log-file ###
attacks = pd.read_csv(inputFileAttacks,sep=",")
# convert the timestamp 
attacks["startTime"] = attacks["start"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f").timestamp())
attacks["endTime"] = attacks["end"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f").timestamp())

# Open the result file 
with open(outputFileData, 'w') as res: 
    writer = csv.writer(res)
    
    # Open the file with the unlabelled flows 
    with open(inputFileData, 'r') as fl: 
        reader = csv.reader(fl, delimiter=',')
        firstLine = True
        # Iterate through each line 
        for row in reader:
            try:
                # Handle header
                if firstLine == True : 
                    firstLine = False
                    writer.writerow(row+['label','attackType','attackID','attackDescription'])
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
                dstIPAddr = dstIPAddr.strip()
                srcPt = srcPt.strip()
                dstPt = dstPt.strip()
                res = addLabels(srcIPAddr,dstIPAddr,time,srcPt,dstPt)
                
                # Write the  line 
                writer.writerow([datefirstseen,duration,proto,srcIPAddr,srcPt,dstIPAddr,dstPt,packets,bbytes,flows,flags,tos,res['label'],res['attack'],res['attackID'],res['description']])

            except Exception as e:
                print("Error")
                with open("labelling_errors.log", "a") as ef:
                    ef.write(str(e) + "\nROW: " + str(row[0]) + "\n")
                
