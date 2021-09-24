#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import traceback
import os
import subprocess
import argparse
import shutil
from library import check_leapsec, check_bsp_planetary, check_bsp_object, clear_for_rerun
from generate_dates import generate_dates_file
from generate_ephemeris import generate_ephemeris, generate_positions, run_elimina, centers_positions_to_deg

parser = argparse.ArgumentParser()
parser.add_argument("name", help="Object name without spaces")
parser.add_argument("start_date", help="Initial date. example '2018-JAN-01'")
parser.add_argument(
    "final_date", help="Final date. example '2018-DEC-31 23:59:01'")
parser.add_argument("step",
                    help="steps in seconds. Example 60")
parser.add_argument("--leap_sec", default="naif0012.tls",
                    help="Name of the Leap Seconds file, it must be in the directory /data. example naif0012.tls")
parser.add_argument("--bsp_planetary", default="de435.bsp",
                    help="Name of the BSP Planetary file, it must be in the directory /data. example de435.bsp")
parser.add_argument("--bsp_object", default=None,
                    help="Name of the Asteroid BSP file, it must be in the directory /data. example Eris.bsp. default <name>.bsp")

# parser.add_argument("--filename", default="dates.txt",
#                     help="Output file name. default is dates.txt")
args = parser.parse_args()


if __name__ == "__main__":

    try:

        # Tratar os Parametros de entrada
        name = args.name.replace(' ', '').replace('_', '')
        start_date = args.start_date
        final_date = args.final_date
        step = args.step
        leap_sec_filename = args.leap_sec
        bsp_planetary_filename = args.bsp_planetary
        bsp_object_filename = args.bsp_object
        if bsp_object_filename is None:
            bsp_object_filename = "%s.bsp" % name

        dates_filename = "dates.txt"
        eph_filename = "%s.eph" % name
        radec_filename = "radec.txt"
        positions_filename = "positions.txt"
        centers_filename = "centers.txt"

        data_dir = os.environ.get("DIR_DATA").rstrip('/')

        # Limpa o diretório app e data removendo os links simbolicos e resultados
        # Util só no desenvolimento quando se roda varias vezes o mesmo job.
        clear_for_rerun(
            input_files=[bsp_object_filename],
            output_files=[dates_filename, eph_filename, radec_filename, positions_filename, centers_filename])

        # Checar o arquivo de leapserconds
        leap_sec = check_leapsec(leap_sec_filename)
        print("Leap Second: [%s]" % leap_sec_filename)

        # Checa o arquivo bsp_planetary
        bsp_planetary = check_bsp_planetary(bsp_planetary_filename)
        print("BSP Planetary: [%s]" % bsp_planetary)

        # Checa o arquivo bsp_object
        bsp_object = check_bsp_object(bsp_object_filename)
        print("BSP Object: [%s]" % bsp_object)

        # Gerar arquivo de datas
        dates_file = generate_dates_file(
            start_date, final_date, step, dates_filename)
        print("Dates File: [%s]" % dates_file)

        # Gerar a ephemeris
        eph_file = generate_ephemeris(
            dates_file, bsp_object, bsp_planetary,
            leap_sec, eph_filename, radec_filename)

        print("Ephemeris File: [%s]" % eph_file)

        # TODO: Verificar se é mesmo necessário!
        # Gerar aquivo de posições
        positions_file = generate_positions(
            eph_filename, positions_filename)

        print("Positions File: [%s]" % positions_file)

        # TODO: Gerar plot Orbit in Sky se for necessário
        # plotOrbit(object_name, footprint, ecliptic_galactic,
        #         positions, orbit_in_sky)
        # os.chmod(orbit_in_sky, 0776)

        # Executar o Elimina e gerar o Centers.txt
        centers_file = run_elimina(eph_filename, centers_filename)
        print("Centers File: [%s]" % centers_file)

        # Converter as posições do Centers.txt para graus
        center_positions_deg = centers_positions_to_deg(centers_file)
        # print(center_positions_deg)
        # TODO: Para cada posição executar a query no banco de dados.

    except Exception as e:
        print(e)
        traceback.print_exc()

    finally:
        print("Terminou!")

# Exemplo da execução do comando
# python run.py 1999RB216 2021-JAN-01 2022-JAN-01 600 --bsp_object 1999RB216.bsp
