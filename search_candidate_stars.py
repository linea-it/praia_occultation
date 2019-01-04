#!/usr/bin/python2.7
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("config", help="Configuration file with input and output parameters. as described in the template PRAIA_occ_star_search_12.template.dat")
parser.add_argument("--log", default="praia_star_search.log", help="Name of the log file with the output of PRAIA_occ_star_search, the log will be in the data directory.")
args = parser.parse_args()

import subprocess
import os
import spiceypy as spice
import math
from datetime import datetime
import numpy as np

data_dir = os.environ.get("DIR_DATA")
config_file = args.config
log_filename = args.log
csv_file = os.path.join(data_dir, "occultation_table.csv")


log = os.path.join(data_dir, log_filename)

def searchCandidates(config_file, log):

    with open(log, 'w') as fp:
        p = subprocess.Popen('./PRAIA_occ_star_search_12 < '+config_file, stdin=subprocess.PIPE, shell=True, stdout=fp )
        p.communicate()


def fixtable(filename):
    inoutFile = open(filename, 'r+b')
    contents = inoutFile.readlines()

    contents[4] = " G: G magnitude from Gaia\n"
    contents[5] = contents[5][:41] + 'cluded)\n'
    contents[6] = " G" + contents[6][2:]
    contents[17] = contents[17][:27] + "\n"
    contents[26] = contents[26][:6] + "only Gaia DR1 stars are used\n"
    contents[27] = contents[27][:-1] + " (not applicable here)\n"
    contents[35] = contents[35][:34] + "10)\n"
    contents[36] = contents[36][:41] + "\n"
    contents[37] = contents[37][:36] + "/yr); (0 when not provided by Gaia DR1)\n"
    contents[39] = contents[39][:115] + "G" + contents[39][116:]

    for i in range(41,len(contents)):
        contents[i] = contents[i][:169] + "-- -" + contents[i][173:]

    inoutFile.seek(0)   #go at the begining of the read/write file
    inoutFile.truncate() #clean the file (delete all content)
    inoutFile.writelines(contents) #write the new content in the blank file
    inoutFile.close()


#Function to extract right ascension or declination from a array
#The index of specific columns (RA or Dec) is defined inside of indexList 
def getPositionFromOCCtable(dataArray, indexList):
    return [' '.join(pos) for pos in dataArray[:, indexList]]


#Function to convert data from ascii table (generate by PRAIA OCC) to csv file
def asciiTable2csv(inputFile, outputFile):
    data = np.loadtxt(inputFile, skiprows=41, dtype=str, ndmin=2)

    nRows, nCols = data.shape

    #To avoid 60 in seconds (provided by PRAIA occ), 
    date = []
    for d in data[:,range(6)]:
        if d[5] == '60.':
            d[4] = int(d[4]) + 1
            d[5] = '00.'
        date.append(datetime.strptime(' '.join(d), "%d %m %Y %H %M %S."))

    #use this definition when seconds = 0..59    
    #date = [datetime.strptime(' '.join(d), "%d %m %Y %H %M %S.") for d in data[:,range(6)]]


    dateAndPositions = []
    dateAndPositions.append(date)

    #Extracting positions of stars and objects and save it in a array
    for i in range(6,17,3):
        dateAndPositions.append(getPositionFromOCCtable(data, [i, i+1, i+2]))

    dateAndPositions = np.array(dateAndPositions)
    dateAndPositions = dateAndPositions.T

    #Extracting others parameters (C/A, P/A, etc.)
    otherParameters = data[:, range(18, nCols)]

    newData = np.concatenate((dateAndPositions, otherParameters), 1) 

    #Defining the column's names
    colNames = "occultation_date;ra_star_candidate;dec_star_candidate;ra_object;" \
                "dec_object;ca;pa;vel;delta;g;j;h;k;long;loc_t;" \
                "off_ra;off_de;pm;ct;f;e_ra;e_de;pmra;pmde"

    np.savetxt(outputFile, newData, fmt='%s', header=colNames, delimiter=';')


try:

    params = []
    with open(config_file, 'r') as fp:
        for line in fp:
            params.append(line.split()[0].strip())

    table = params[7]


    searchCandidates(config_file, log)

    fixtable(table)

    # Convert table to csv
    print("Convert table to csv")
    asciiTable2csv(os.path.join(data_dir, "g4_occ_data_JOHNSTON_2018_table"), csv_file)
    

    exit(0)

except Exception as e:
    raise(e)
    exit(1)