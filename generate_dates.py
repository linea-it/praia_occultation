#!/usr/bin/python2.7
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("start_date", help="Initial date. example '2018-JAN-01'")
parser.add_argument("final_date", help="Final date. example '2018-DEC-31 23:59:01'")
parser.add_argument("step", help="steps in seconds. Example 60")
parser.add_argument("--leap_sec", default="naif0012.tls", help="Name of the Leap Seconds file, it must be in the directory /data. example naif0012.tls")
parser.add_argument("--filename", default="dates.txt", help="Output file name. default is dates.txt")
args = parser.parse_args()

import subprocess
import os

start_date = args.start_date
final_date = args.final_date
step = args.step
leap_sec_filename = args.leap_sec
result_filename = args.filename

data_dir = os.environ.get("DIR_DATA")

dates_file = os.path.join(data_dir, result_filename)


def check_leapsec(dir_data, filename):
    """
        Verifica se o arquivo leapSec existe
    """
    in_leap_sec = os.path.join(dir_data, filename)

    if os.path.exists(filename):
        # Arquivo existe no diretorio local
        return filename

    elif os.path.exists(in_leap_sec):
        # arquivo existe no diretorio de /DATA
        os.symlink(in_leap_sec, filename)
        return filename
    else:
        raise (Exception("Leap Sec file does not exist. [%s]" % in_leap_sec))
        exit(1)

leap_sec = check_leapsec(data_dir, leap_sec_filename)


with open(dates_file, 'w') as fp:
    parameters = [start_date, final_date, step]
    strParameters = '\n'.join(map(str, parameters))    
    p = subprocess.Popen('./geradata', stdin=subprocess.PIPE, stdout=fp) 
    p.communicate(strParameters)
    exit(0)
