import argparse
parser = argparse.ArgumentParser()
parser.add_argument("ephemeris", help="File with the ephemeris, like 1999RB216.eph")
parser.add_argument("catalog", help="csv with the star catalog.")
parser.add_argument("positions", help="File with the positions used in the querys.")
parser.add_argument("--filename", default="neighborhood_stars.png", help="name of the output file, plot with the ephemeris of the object and the stars. default: neighborhood_stars.png")
parser.add_argument("--radius", default=0.15, help="Radius used in star query, default is 0.15 degrees")

args = parser.parse_args()


import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

def plotGAIAstars(radius, ephemeris, catalogue, positions, output):
    raH,raM,raS,decD,decM,decS = np.loadtxt(ephemeris,usecols=(2,3,4,5,6,7),skiprows=3,unpack=True)

    ra = [15.0*(h + m/60.0 + s/3600.0) for h,m,s in zip(raH, raM, raS)]
    dec = [d + m/60.0 + s/3600.0 for d,m,s in zip(decD, decM, decS)]

    ra_star, dec_star = np.loadtxt(catalogue, delimiter=';', unpack=True)

    ra_cen, dec_cen = np.loadtxt(positions, unpack=True)

    fig = plt.figure(dpi=90, figsize=(10, 8))

    l0, = plt.plot(ra_star, dec_star, '.b', zorder=1)

    phi = np.linspace(0, 2*np.pi, 100)
    for xo, yo in zip(ra_cen, dec_cen):
        x = xo + radius * np.cos(phi)
        y = yo + radius * np.sin(phi)
        l1, = plt.plot(x, y, 'r', lw=0.8, zorder=2)

    l2, = plt.plot(ra, dec, '--k', zorder=3)
    l3, = plt.plot(ra_cen, dec_cen, 'ok', zorder=4)

    plt.xlabel("R. A. (degrees)", fontsize=15, weight='bold')
    plt.ylabel("Dec. (degrees)", fontsize=15, weight='bold')

    plt.xticks(fontsize=15, weight='bold')
    plt.yticks(fontsize=15, weight='bold')
    leg = ['Positions of stars', 'Limit of query', 'Orbit of object', 'Coordinates for query']
    plt.legend([l0,l1,l2,l3], leg)

    plt.savefig(output, bbox_inches='tight')


try:
    data_dir = os.environ.get("DIR_DATA")

    # Read arguments 
    #Inputs
    ephemeris = os.path.join(data_dir, args.ephemeris)
    catalog = os.path.join(data_dir, args.catalog)
    positions = os.path.join(data_dir, args.positions)
    radius = float(args.radius)

    # Output
    output = os.path.join(data_dir, args.filename)

    if not os.path.exists(ephemeris):
            raise(Exception("Missing Ephemeris file"))

    if not os.path.exists(catalog):
            raise(Exception("Missing Catalog csv file"))

    if not os.path.exists(positions):
            raise(Exception("Missing Positions file"))

    plotGAIAstars(radius, ephemeris, catalog, positions, output)


    if not os.path.exists(output):
        raise("Plot Neighborhood Stars was not created. output [%s]" % output)

    os.chmod(output, 0664)
except Exception as e:
    raise e