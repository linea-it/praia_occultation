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

data_dir = os.environ.get("DIR_DATA")
config_file = args.config
log_filename = args.log

log = os.path.join(data_dir, log_filename)

def searchCandidates(config_file, log):

    print (config_file)

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

try:

    params = []
    with open(config_file, 'r') as fp:
        for line in fp:
            params.append(line.split()[0].strip())


    searchCandidates(config_file, log)

    fixtable(params[7])

    exit(0)

except Exception as e:
    raise(e)
    exit(1)