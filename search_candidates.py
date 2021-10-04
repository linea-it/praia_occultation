#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import subprocess
import os
import spiceypy as spice
import math
from library import HMS2deg
import csv


def praia_occ_input_file(star_catalog, object_ephemeris, filename):

    # TODO: Precisa de um refactoring, os parametros podem vir da interface.
    try:
        app_path = os.environ.get("APP_PATH").rstrip('/')
        data_dir = os.environ.get("DIR_DATA").rstrip('/')

        output = os.path.join(data_dir, filename)
        out_link = os.path.join(app_path, filename)

        stars_catalog_mini_filename = 'g4_micro_catalog_JOHNSTON_2018'
        stars_catalog_xy_filename = 'g4_occ_catalog_JOHNSTON_2018'
        stars_parameters_of_occultation_filename = 'g4_occ_data_JOHNSTON_2018'
        stars_parameters_of_occultation_plot_filename = 'g4_occ_data_JOHNSTON_2018_table'

        with open("praia_occ_input_template.txt") as file:

            data = file.read()

            data = data.replace('{stellar_catalog}', star_catalog.ljust(50))

            data = data.replace('{object_ephemeris}',
                                object_ephemeris.ljust(50))

            name = os.path.join(data_dir, stars_catalog_mini_filename)
            data = data.replace('{stars_catalog_mini}', name.ljust(50))

            name = os.path.join(data_dir, stars_catalog_xy_filename)
            data = data.replace('{stars_catalog_xy}', name.ljust(50))

            name = os.path.join(
                data_dir, stars_parameters_of_occultation_filename)
            data = data.replace(
                '{stars_parameters_of_occultation}', name.ljust(50))

            name = os.path.join(
                data_dir, stars_parameters_of_occultation_plot_filename)
            data = data.replace(
                '{stars_parameters_of_occultation_plot}', name.ljust(50))

            with open(output, 'w') as new_file:
                new_file.write(data)

        if os.path.exists(output):
            # Altera permissão do arquivo para escrita do grupo
            os.chmod(output, 0664)
            # Cria um link simbolico no diretório app
            os.symlink(output, out_link)

            return output
        else:
            raise (Exception("%s not generated. [%s]" % (filename, output)))

    except Exception as e:
        raise (e)
