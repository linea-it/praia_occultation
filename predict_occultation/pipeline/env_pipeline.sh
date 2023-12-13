#!/bin/bash

export PIPELINE_PATH=`pwd`

export EUPS_USERDATA=/tmp/`whoami`/eups
. /mnt/eups/linea_eups_setup.sh
setup gcc 4.9.3+1
export PATH=$PATH:$PIPELINE_PATH/bin

export CONDAPATH=/lustre/t1/tmp/singulani/miniconda3/bin
source $CONDAPATH/activate
conda activate praia

export DB_URI=postgresql+psycopg2://untrustedprod:untrusted@desdb4.linea.gov.br:5432/prod_gavo

ulimit -s 100000
ulimit -u 100000
