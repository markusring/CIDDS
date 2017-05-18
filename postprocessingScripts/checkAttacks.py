import csv

# Path to data
file = sys.argv[1]
counts = dict() 

if inputFileData == "--help" or inputFileData == "-help" or inputFileData == "--h" or inputFileData == "-h":
    print("Usage: python checkAttacks.py inputFlowFile.csv")
    exit()

with open(file, 'r') as flows: 
    reader = csv.reader(flows, delimiter=',')
    firstLine = True
    for row in reader:
        # Iterate through each line 
        if firstLine == True : 
            firstLine = False
            continue
        # Read the value 
        id = "-1"
        if(len(row)!=16): 
            print(row)
        else:
            id = row[14]

        if id in counts: 
            val = counts.get(id)
            val = val + 1 
            counts[id] = val
        else:
            counts[id] = 1

for key in counts: 
    print(key + "," + str(counts[key]))