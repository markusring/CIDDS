# Imports
import csv 
import sys
import pandas as pd 
from datetime import datetime

# Path to data
inputFileData = sys.argv[1]

if inputFileData == "--help" or inputFileData == "-help" or inputFileData == "--h" or inputFileData == "-h" or inputFileData == "":
    print("Usage: python countTrafficPerHour flowFile.csv resultFile.csv")
    exit()

outputFileData = sys.argv[2]

# Traffic per hour 
tph = dict() 
order = []

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
                continue
            # Read the value 
            datefirstseen = row[0]
            index = datefirstseen.rfind(" ")
            uniqueSubnetID = datefirstseen[0:index+3]

            if uniqueSubnetID in tph: 
                c = tph[uniqueSubnetID]
                c = c+1
                tph[uniqueSubnetID] = c
            else:
                tph[uniqueSubnetID] = 1
                order.append(uniqueSubnetID)

        except Exception as e:
            print("Error")
            with open("labelling_errors.log", "a") as ef:
                ef.write(str(e) + "\nROW: " + str(row[0]) + "\n")
                

# Open the result file 
with open(outputFileData, 'w') as result: 
    writer = csv.writer(result)
    for val in order: 
        elem = []
        elem.append(val)
        elem.append(tph[val])
        writer.writerow(elem)