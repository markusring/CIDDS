# Imports
import csv 
import sys
import pandas as pd 
from datetime import datetime

# Path to data
inputFile = sys.argv[1]

if inputFile == "--help" or inputFile == "-help" or inputFile == "--h" or inputFile == "-h" or inputFile == "":
    print("Usage: python anonymization.py inputFlowFile.csv outputFlowsFile.csv")
    exit()

outputFile = sys.argv[2]

# IPs to replace 
ipsToAnonym = dict()
ipsToAnonym["ATTACKER1"] = "333.333.333.333"
ipsToAnonym["ATTACKER2"] = "333.333.333.333"
ipsToAnonym["ATTACKER3"] = "333.333.333.333"
ipsToAnonym["DNS"] = "333.333.333.333"
ipsToAnonym["EXT_SERVER"] = "333.333.333.333"
ipsToAnonym["OPENSTACK_NET"] = "333.333.333.333"

# anonymized external ips 
counter = 10000
extIPs = dict() 

# Anonymizes the given IP Address
def anonymize(ip): 
    # STEP 1: Consider default ips: 
    if ip == "0.0.0.0" or ip == "255.255.255.255":
        return ip 
    
    # STEP 2: Do not anonymize internal IPs of OpenStack clients 
    ipParts = ip.split(".")
    if ipParts[0] == "192" and ipParts[1] == "168":
        return ip

    # STEP 3: Handle special IPs: 
    for key in ipsToAnonym: 
        concreteIP = ipsToAnonym[key]
        if ip == concreteIP: 
            return key
    
    # STEP 4: Anonymize external ips: 
    global counter
    index = ip.rfind(".")
    uniqueSubnetID = ip[0:index]
    if uniqueSubnetID not in extIPs: 
        extIPs[uniqueSubnetID] = counter
        counter = counter + 1
    key = str(extIPs[uniqueSubnetID]) + "_" + ipParts[3]
    return key


# Open the result file 
with open(outputFile, 'w') as result: 
    writer = csv.writer(result)
    
    # Open the file with the unlabelled flows 
    with open(inputFile, 'r') as inputData: 
        reader = csv.reader(inputData, delimiter=',')
        firstLine = True
        # Iterate through each line 
        for row in reader:
            try:
                # Handle first line specifically (header line) 
                if firstLine == True : 
                    firstLine = False
                    writer.writerow(row)
                    continue

                # Read the attribute value 
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
                label = row[12]
                attackType = row[13]
                attackID = row[14]
                attackDescription = row[15]

                # anonymize src and dst ip address
                srcIPAddr = srcIPAddr.strip()
                dstIPAddr = dstIPAddr.strip()
                
                srcIPAddr = anonymize(srcIPAddr)
                dstIPAddr = anonymize(dstIPAddr)
                
                # Write the  line 
                writer.writerow([datefirstseen,duration,proto,srcIPAddr,srcPt,dstIPAddr,dstPt,packets,bbytes,flows,flags,tos,label,attackType,attackID,attackDescription])
                
            except Exception as e:
                print("Error")
                with open("labelling_errors.log", "a") as ef:
                    ef.write(str(e) + "\nROW: " + str(row[0]) + "\n")
