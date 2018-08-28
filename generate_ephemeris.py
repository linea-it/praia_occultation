#!/usr/bin/python2.7
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("dates_file", help="")
parser.add_argument("bsp_object", help="")
parser.add_argument("bsp_planets", help="")
parser.add_argument("filename", help="")
parser.add_argument("--leap_sec", default="naif0012.tls", help="")
parser.add_argument("--radec_filename", default="radec.txt", help="")

args = parser.parse_args()

import subprocess
import os
import spiceypy as spice
import math



def findIDSPK(n, key):
    loc = 2 #order setting bsp files (1=DEXXX.bsp,2=Ast.bsp)
    m, header, flag = spice.dafec(loc, n)
    spk = ''
    for row in header:
        if row[:len(key)] == key:
            spk = row[len(key):].strip()
    return spk


#Function to compute the angle between two vector (return the angle in degrees)
def angle(v1, v2):
    rad = math.acos(dotproduct(v1, v2) / (norm(v1) * norm(v2)))
    return math.degrees(rad)

def dotproduct(v1, v2):
    return sum((a*b) for a, b in zip(v1, v2))

def norm(v):
    return math.sqrt(dotproduct(v, v))

def ra2HMS(rarad=''):
    radeg = math.degrees(rarad)
    raH = int(radeg/15.0)
    raM = int((radeg/15.0 - raH)*60)
    raS = 60*((radeg/15.0 - raH)*60 - raM)
    RA = '{:02d} {:02d} {:07.4f}'.format(raH, raM, raS)
    return RA


def dec2DMS(decrad=''):
    decdeg = math.degrees(decrad)
    ds = '+'
    if decdeg < 0:
        ds, decdeg = '-', abs(decdeg)
    deg = int(decdeg)
    decM = abs(int((decdeg - deg)*60))
    decS = 60*(abs((decdeg - deg)*60)-decM)
    DEC = '{}{:02d} {:02d} {:06.3f}'.format(ds, deg, decM, decS)
    return DEC

def generateEphemeris(datesFile, bsp, dexxx, leapSec, nameFile, radec):
    #Load the asteroid and planetary ephemeris and the leap second (in order)
    spice.furnsh(dexxx)
    spice.furnsh(leapSec)
    spice.furnsh(bsp)


    #Values specific for extract all comments of header from bsp files (JPL, NIMA)
    source = {'NIMA':(45, 'ASTEROID_SPK_ID ='), 'JPL':(74, 'Target SPK ID   :')}
    n, key = source['NIMA']
    idspk = findIDSPK(n, key)
    if idspk == '':
        n, key = source['JPL']
        idspk = findIDSPK(n, key)

    #Read the file with dates
    with open(datesFile, 'r') as inFile:
        dates = inFile.read().splitlines()

    n = len(dates)

    #Convert dates from utc to et format
    datesET = [spice.utc2et(utc) for utc in dates]

    #Compute geocentric positions (x,y,z) for each date with light time correction
    rAst, ltAst = spice.spkpos(idspk, datesET, 'J2000', 'LT', 'EARTH')
    rSun, ltSun = spice.spkpos('SUN', datesET, 'J2000', 'NONE', 'EARTH')
    
    elongation = [angle(rAst[i], rSun[i]) for i in range(n)]

    data = [spice.recrad(xyz) for xyz in rAst]
    distance, rarad, decrad = zip(*data)

    #================= for graphics =================
    radecFile = open(radec, 'w')
    for row in data:
        radecFile.write(str(row[1]) + ';' + str(row[2]) + '\n')
    radecFile.close()
    #================================================

    ra = [ra2HMS(alpha) for alpha in rarad]
    dec = [dec2DMS(delta) for delta in decrad]

    #Convert cartesian to angular coordinates and save it in a ascii file
    outFile = open(nameFile,'w')
    outFile.write('\n\n     Data Cal. UTC' + ' '.ljust(51) + 'R.A.__(ICRF//J2000.0)__DEC')
    outFile.write(' '.ljust(43) + 'DIST (km)' + ' '.ljust(24) + 'S-O-A\n')
    for i in range(n):
        outFile.write(dates[i] + ' '.ljust(44) + ra[i] + '  ' + dec[i] + ' '.ljust(35)) 
        outFile.write('{:.16E}'.format(distance[i]) + ' '.ljust(17))
        outFile.write('{:.4f}'.format(elongation[i]) + '\n')
    outFile.close()




# ============ Generating ephemeris =============

dates_file = args.dates_file
bsp_object = args.bsp_object
bsp_planets = args.bsp_planets
leap_sec = args.leap_sec


result_filename = args.filename

data_dir = os.environ.get("DIR_DATA")
radec_filename = args.radec_filename

in_dates_file = os.path.join(data_dir, dates_file)
in_bsp_object = os.path.join(data_dir, bsp_object)
in_bsp_planets = os.path.join(data_dir, bsp_planets)
in_leap_sec = os.path.join(data_dir, leap_sec)

ephemeris = os.path.join(data_dir, result_filename)
radec = os.path.join(data_dir, radec_filename)

if not os.path.exists(dates_file):
    if os.path.exists(in_dates_file):
        os.symlink(in_dates_file, dates_file)
    else:
        raise(Exception("Missing dates file"))

if not os.path.exists(bsp_object):
    if os.path.exists(in_bsp_object):
        os.symlink(in_bsp_object, bsp_object)
    else:
        raise(Exception("Missing Object bsp file"))

if not os.path.exists(bsp_planets):
    if os.path.exists(in_bsp_planets):
        os.symlink(in_bsp_planets, bsp_planets)
    else:
        raise(Exception("Missing Planets bsp file"))

if not os.path.exists(leap_sec):
    if os.path.exists(in_leap_sec):
        os.symlink(in_leap_sec, leap_sec)
    else:
        raise(Exception("Missing leap sec file"))

try:
    generateEphemeris(dates_file, bsp_object, bsp_planets, leap_sec, ephemeris, radec)

    # Clear inputs
    os.unlink(dates_file)
    os.unlink(bsp_object)
    os.unlink(bsp_planets)
    os.unlink(leap_sec)

    if os.path.exists(ephemeris):
        exit(0)
    else:
        exit(1)

except Exception as e:
    raise(e)
    exit(1)