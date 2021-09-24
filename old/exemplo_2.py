from astropy.table import Table, unique
from datetime import datetime
import spiceypy as spice
import subprocess
import warnings
import math
import os
​
warnings.filterwarnings("ignore")
​
def findIDSPK(n, key):
    loc = 2 #order setting bsp files (1=DEXXX.bsp,2=Ast.bsp)
    m, header, flag = spice.dafec(loc, n)
    spk = ''
    for row in header:
        if row[:len(key)] == key:
            spk = row[len(key):].strip()
    return spk
​
​
def ra2HMS(rarad=''):
    radeg = math.degrees(rarad)
    raH = int(radeg/15.0)
    raM = int((radeg/15.0 - raH)*60)
    raS = 60*((radeg/15.0 - raH)*60 - raM)
    RA = '{:02d} {:02d} {:07.4f}'.format(raH, raM, raS)
    return RA
​
​
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
​
​
def dotproduct(v1, v2):
    return sum((a*b) for a, b in zip(v1, v2))
​
​
def norm(v):
    return math.sqrt(dotproduct(v, v))
​
​
#Function to compute the angle between two vector (return the angle in degrees)
def angle(v1, v2):
    rad = math.acos(dotproduct(v1, v2) / (norm(v1) * norm(v2)))
    return math.degrees(rad)
​
​
def generateEphemeris(datesFile, bsp, dexxx, leapSec, nameFile):
    #Load the asteroid and planetary ephemeris and the leap second (in order)
    spice.furnsh(dexxx)
    spice.furnsh(leapSec)
    spice.furnsh(bsp)
​
​
    #Values specific for extract all comments of header from bsp files (JPL, NIMA)
    source = {'NIMA':(45, 'ASTEROID_SPK_ID ='), 'JPL':(74, 'Target SPK ID   :')}
    n, key = source['NIMA']
    idspk = findIDSPK(n, key)
    if idspk == '':
        n, key = source['JPL']
        idspk = findIDSPK(n, key)
​
    #Read the file with dates
    with open(datesFile, 'r') as inFile:
        dates = inFile.read().splitlines()
​
    n = len(dates)
​
    #Convert dates from utc to et format
    datesET = [spice.utc2et(utc) for utc in dates]
​
    #Compute geocentric positions (x,y,z) for each date with light time correction
    rAst, ltAst = spice.spkpos(idspk, datesET, 'J2000', 'LT', 'EARTH')
    rSun, ltSun = spice.spkpos('SUN', datesET, 'J2000', 'NONE', 'EARTH')
    
    elongation = [angle(rAst[i], rSun[i]) for i in range(n)]
​
    data = [spice.recrad(xyz) for xyz in rAst]
    distance, rarad, decrad = zip(*data)
​
    #================= for graphics =================
    tempFile = open('radec.txt', 'w')
    for row in data:
        tempFile.write(str(row[1]) + '  ' + str(row[2]) + '\n')
    tempFile.close()
    #================================================
​
    ra = [ra2HMS(alpha) for alpha in rarad]
    dec = [dec2DMS(delta) for delta in decrad]
​
    #Convert cartesian to angular coordinates and save it in a ascii file
    outFile = open(nameFile,'w')
    outFile.write('\n\n     Data Cal. UTC' + ' '.ljust(51) + 'R.A.__(ICRF//J2000.0)__DEC')
    outFile.write(' '.ljust(43) + 'DIST (km)' + ' '.ljust(24) + 'S-O-A\n')
    for i in range(n):
        outFile.write(dates[i] + ' '.ljust(44) + ra[i] + '  ' + dec[i] + ' '.ljust(35)) 
        outFile.write('{:.16E}'.format(distance[i]) + ' '.ljust(17))
        outFile.write('{:.4f}'.format(elongation[i]) + '\n')
    outFile.close()
​
​
​
def executeScript(script, parameters, filename):
    strParameters = '\n'.join(map(str, parameters))
    with open(filename, 'w') as outFile:
        #open the script .sh with the necessary configurations
        p = subprocess.Popen(script, stdin=subprocess.PIPE, stdout=outFile, shell=True)
​
    #set the input parameters to the script
    p.communicate(strParameters)
​
​
#Function to set some input parameters to PRAIA_occ.dat file
def setParameters2PRAIAdat(parameters, inputOutputFile):
    inoutFile = open(inputOutputFile, "r+")
    contents = inoutFile.readlines()
    
    for i in range(len(parameters)):
        newlinei = parameters[i].ljust(50) + contents[i][50:]
        if contents[i] != newlinei:
            contents[i] = newlinei
    
    inoutFile.seek(0)
    inoutFile.writelines(contents)
  
    inoutFile.close()
​
​
def executeVizquery(script, centersFile, outputFile):
    #query = '-c.bm=20 -out=RA_ICRS -out=e_RA_ICRS -out=DE_ICRS -out=e_DE_ICRS -out=Plx '
    #query+= '-out=pmRA -out=e_pmRA -out=pmDE -out=e_pmDE -out=Dup -out="<FG>" -out="e_<FG>" '
    #query+= '-out="<Gmag>" -out=Var -source=I/337/gaia -out.max=1150000000 -out.form=mini '
    #query+= '-mime=vot -list=-c=' + centersFile + ' -sort="RA_ICRS"'
​
    query = '-c.bm=20 -out=RA_ICRS -out=e_RA_ICRS -out=DE_ICRS -out=e_DE_ICRS -out=Plx '
    query+= '-out=pmRA -out=e_pmRA -out=pmDE -out=e_pmDE -out=Dup -out="FG" -out="e_FG" '
    query+= '-out="Gmag" -out=Var -source=I/345/gaia2 -out.max=1150000000 -out.form=mini '
    query+= '-mime=vot -list=-c=' + centersFile + ' -sort="RA_ICRS"'
​
    os.system(script + " " + query + " > " + outputFile)
​
​
def doGaiaCat(inputFile, outputFile):
    table = Table.read(inputFile)
    table2 = table.filled(0)
​
    table3 = unique(table2)
​
    magJ, magH, magK = 99.000, 99.000, 99.000
    JD = 15.0 * 365.25 + 2451545
​
    catFile = open(outputFile, "w")
    
    for row in table3:
        catFile.write(" ".ljust(64))
        catFile.write(("%.3f" % row[12]).rjust(6) )
        catFile.write(" ".ljust(7))
        catFile.write(" " + ("%.3f" % magJ).rjust(6))
        catFile.write(" " + ("%.3f" % magH).rjust(6))
        catFile.write(" " + ("%.3f" % magK).rjust(6))
        catFile.write(" ".rjust(35))
        catFile.write(" " + ("%.3f" % (row[5]/1000.0)).rjust(7))
        catFile.write(" " + ("%.3f" % (row[7]/1000.0)).rjust(7))
        catFile.write(" " + ("%.3f" % (row[6]/1000.0)).rjust(7))
        catFile.write(" " + ("%.3f" % (row[8]/1000.0)).rjust(7))
        catFile.write(" ".rjust(71))
        catFile.write(" " + ("%.9f" % (row[0]/15.0)).rjust(13))
        catFile.write(" " + ("%.9f" % row[2]).rjust(13))
        catFile.write(" ".ljust(24))
        catFile.write(("%.8f" % JD).rjust(16))
        catFile.write(" ".ljust(119))
        catFile.write("  " + ("%.3f" % (row[1]/1000.0)).rjust(6))
        catFile.write("  " + ("%.3f" % (row[3]/1000.0)).rjust(6))
​
        catFile.write("\n")
    
    catFile.close()
​
def fixtable(filename):
    inoutFile = open(filename, 'r+b')
    contents = inoutFile.readlines()
​
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
​
    for i in range(41,len(contents)):
        contents[i] = contents[i][:169] + "-- -" + contents[i][173:]
​
    inoutFile.seek(0)   #go at the begining of the read/write file
    inoutFile.truncate() #clean the file (delete all content)
    inoutFile.writelines(contents) #write the new content in the blank file
    inoutFile.close()
   
​
if __name__ == "__main__":
​
    #============================================ INPUT ===========================================
    name = "2014PR70"
​
    datesFile = "dates.txt"
    bspObject = "2014PR70.bsp"
    bspPlanets = "de435.bsp"
    leapSec = "naif0012.tls"
    startDate = '2019-JAN-01'
    finalDate = '2019-DEC-31 23:59:01'
    step = '60'
​
    praiaDat =  'PRAIA_occ_star_search_12.dat'
​
    #praia dat with input and output parameters (see praia dat for details)
    ephFormat = "1"    #NAIF
    ephLabel = "DE435/JPL"
    outFile1 = "g4_micro_catalog_JOHNSTON"
    outFile2 = "g4_occ_catalog_JOHNSTON"
    outFile3 = "g4_occ_data_JOHNSTON"
    outFile4 = "g4_occ_data_JOHNSTON_table"
​
    #Fortran executables
    executables = ["./geradata", "./elimina", "./PRAIA_occ_star_search_12"]
​
    #derivated
    ephName = name + '.eph'
​
​
    #temporal files
    centersFile = "centers.txt"
    starCat = 'cds.xml'
    gaiaCat = 'gaia.cat'    
​
    #==============================================================================================
​
    t0 = datetime.now()
​
    print "========== Executing geradata script =========="
    #executeScript(executables[0], [startDate, finalDate, step], datesFile)
​
    print "============ Generating ephemeris ============="
    generateEphemeris(datesFile, bspObject, bspPlanets, leapSec, ephName)
​
    print "========== Executing elimina script ==========="
    executeScript(executables[1], [ephName], centersFile)
​
    print "============= Executing vizquery =============="
    executeVizquery('/home/usuario/bin/cdsclient-3.84/vizquery', centersFile, starCat)
​
    print "============ Doing GAIA Catalogue ============="
    doGaiaCat(starCat, gaiaCat)
​
    print "== Executing PRAIA_occ_star_search_12 script =="
    parameters = [gaiaCat, ephName, ephFormat, ephLabel, outFile1, outFile2, outFile3, outFile4]
    setParameters2PRAIAdat(parameters, praiaDat)
​
    os.system(executables[2] + " < " + praiaDat)
​
    print "============ Fixing the table OCC ============="
    fixtable(outFile4)
​
    #print "============ Drawing the OCC maps ============="
    #executeScript('./lisinp', ["g4_occ_data_JOHNSTON_" + year + "_table", name, "147", "121", "2"], 'plotting.log')
​
    tf = datetime.now()
​
    print "Duration: ", tf - t0