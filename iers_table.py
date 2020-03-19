#!/usr/bin/env python3
from astropy.utils import iers
from astropy.time import Time


# https://docs.astropy.org/en/stable/utils/iers.html#iers-data-access-astropy-utils-iers
# Download do Arquivo finals2000A.all
try:

    # Download manual, parou de funcionar em 04/02/2020
    #finalFile = iers.IERS_A_URL
    #iers.IERS.iers_table = iers.IERS_A.open(finalFile

    # Fix: Sugerido nesta thread: https://github.com/astropy/astroplan/issues/410
    # essa é a thead para o problema do download: https://github.com/astropy/astropy/issues/5059
    finalFile = 'ftp://cddis.gsfc.nasa.gov/pub/products/iers/finals2000A.all'
    iers.IERS.iers_table = iers.IERS_A.open(finalFile)

except Exception as e:
    print(e)
    print("Warning: Failed to download finals2000A.all")