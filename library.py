#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import os


def check_leapsec(filename):
    """
        Verifica se o arquivo leapSec existe
    """
    app_path = os.environ.get("APP_PATH").rstrip('/')
    data_dir = os.environ.get("DIR_DATA").rstrip('/')

    # local_leap_sec = os.path.join(app_path, filename)
    in_leap_sec = os.path.join(data_dir, filename)

    dest = os.path.join(app_path, filename)

    # Verifica se o Arquivo existe no diretorio local
    if os.path.exists(dest):
        return filename

    else:
        # Verifica se o arquivo existe no diretório /Data
        if os.path.exists(in_leap_sec):
            # Cria um link simbolico no Diretório do app
            os.symlink(in_leap_sec, dest)
            return filename
        else:
            raise (Exception("Leap Sec %s file does not exist." % filename))


def check_bsp_planetary(filename):
    """
        Verifica se o arquivo BSP Planetary existe
    """
    app_path = os.environ.get("APP_PATH").rstrip('/')
    data_dir = os.environ.get("DIR_DATA").rstrip('/')

    in_bsp = os.path.join(data_dir, filename)

    dest = os.path.join(app_path, filename)

    # Verifica se o Arquivo existe no diretorio local
    if os.path.exists(dest):
        return filename
    else:
        # Verifica se o arquivo existe no diretório /Data
        if os.path.exists(in_bsp):
            # Cria um link simbolico no Diretório do app
            os.symlink(in_bsp, dest)
            return filename
        else:
            raise (Exception("BSP Planetary %s file does not exist." % filename))


def check_bsp_object(filename):
    """
        Verifica se o arquivo BSP Object existe e cria um link no diretório app
    """
    app_path = os.environ.get("APP_PATH").rstrip('/')
    data_dir = os.environ.get("DIR_DATA").rstrip('/')

    in_bsp = os.path.join(data_dir, filename)

    dest = os.path.join(app_path, filename)

    # Verifica se o Arquivo existe no diretorio data
    if os.path.exists(in_bsp):
        # Cria um link simbolico no Diretório do app
        os.symlink(in_bsp, dest)
        return filename
    else:
        raise (Exception("BSP Object %s file does not exist." % filename))


def HMS2deg(ra='', dec=''):
    RA, DEC, rs, ds = '', '', 1, 1
    if dec:
        D, M, S = [float(i) for i in dec.split()]
        if str(D)[0] == '-':
            ds, D = -1, abs(D)
        deg = D + (M/60) + (S/3600)
        DEC = deg*ds

    if ra:
        H, M, S = [float(i) for i in ra.split()]
        if str(H)[0] == '-':
            rs, H = -1, abs(H)
        deg = (H*15) + (M/4) + (S/240)
        RA = deg*rs

    if ra and dec:
        return [RA, DEC]
    else:
        return RA or DEC


def clear_for_rerun(input_files, output_files):
    """Remove os arquivos de input e output utilizados no processo. 
    - para arquivos de input remove só os links simbolicos em /app
    - para arquivos de output remove os links em /app e os arquivos originais em /data

    Args:
        input_files (list): Lista com os nomes de arquivos a serem removidos
        output_files (list): Lista com os nomes de arquivos a serem removidos
    """

    app_path = os.environ.get("APP_PATH").rstrip('/')
    data_dir = os.environ.get("DIR_DATA").rstrip('/')

    # Remover o arquivo bsp_object apenas o link
    for filename in input_files:
        a = os.path.join(app_path, filename)
        if os.path.exists(a):
            os.unlink(a)

    # Para os demais arquivos que tem link no diretório app e o arquivo no diretório data
    for filename in output_files:
        a = os.path.join(app_path, filename)
        d = os.path.join(data_dir, filename)
        if os.path.exists(a):
            os.unlink(a)
        if os.path.exists(d):
            os.remove(d)


def write_gaia_catalog(self, rows, path):

    # Propriedades do GAIA http://vizier.u-strasbg.fr/viz-bin/VizieR-3?-source=I/345/gaia2&-out.add=_r
    # RA_ICRS   = ra                     = 0
    # e_RA_ICRS = ra_error               = 1
    # DE_ICRS   = dec                    = 2
    # e_DE_ICRS = dec_error              = 3
    # Plx       = parallax               = 4
    # pmRA      = pmra                   = 5
    # e_pmRA    = pmra_error             = 6
    # pmDE      = pmdec                  = 7
    # e_pmDE    = pmdec_error            = 8
    # Dup       = duplicated_source      = 9
    # FG        = phot_g_mean_flux       = 10
    # e_FG      = phot_g_mean_flux_error = 11
    # Gmag      = phot_g_mean_mag        = 12
    # Var       = phot_variable_flag     = 13

    magJ, magH, magK = 99.000, 99.000, 99.000
    JD = 15.0 * 365.25 + 2451545

    filename = os.path.join(path, "gaia_catalog.cat")
    with open(filename, 'w') as fp:
        for row in rows:

            # Converter os valores nulos para 0
            for prop in row:
                if row[prop] is None:
                    row[prop] = 0

            fp.write(" ".ljust(64))
            fp.write(("%.3f" % row['phot_g_mean_mag']).rjust(6))
            fp.write(" ".ljust(7))
            fp.write(" " + ("%.3f" % magJ).rjust(6))
            fp.write(" " + ("%.3f" % magH).rjust(6))
            fp.write(" " + ("%.3f" % magK).rjust(6))
            fp.write(" ".rjust(35))
            fp.write(" " + ("%.3f" % (row["pmra"] / 1000.0)).rjust(7))
            fp.write(" " + ("%.3f" % (row["pmdec"] / 1000.0)).rjust(7))
            fp.write(" " + ("%.3f" % (row["pmra_error"] / 1000.0)).rjust(7))
            fp.write(" " + ("%.3f" % (row["pmdec_error"] / 1000.0)).rjust(7))
            fp.write(" ".rjust(71))
            fp.write(" " + ("%.9f" % (row["ra"] / 15.0)).rjust(13))
            fp.write(" " + ("%.9f" % row["dec"]).rjust(13))
            fp.write(" ".ljust(24))
            fp.write(("%.8f" % JD).rjust(16))
            fp.write(" ".ljust(119))
            fp.write("  " + ("%.3f" % (row["ra_error"] / 1000.0)).rjust(6))
            fp.write("  " + ("%.3f" % (row["dec_error"] / 1000.0)).rjust(6))
            fp.write("\n")

        fp.close()

    return filename
