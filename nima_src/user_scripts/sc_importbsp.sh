#!/bin/bash
#########################################################################
#									#
#	sc_importbsp.sh 					 	#
#		- check and import bsp files from JPL	 		#
#		- bsp files from JPL have to be stored jplbsp/		#
#									#
#								JD-2014	#
#########################################################################
echo "Asteroid number (ex: 50000, 2007JH43) :"
read aster
echo "Asteroid name (ex: Quaoar, 2007JH43) :"
read name
#########################################################################
if [ -f $name ]; then
	echo "No asteroid number "
	name=$aster
	echo "     asteroid name: $name "
	echo " "
fi
rep=jplbsp
export LC_COLLATE=C
echo ">>> file list <<<"
echo " "
ls $rep/*${name:4:7}*.bsp
echo " "
echo " "
echo "bsp file?"
read infile
cp ${infile} results/$aster
cd results/$aster/
if [ -h JPL${aster}.bsp ]; then
	echo "delete previous JPL bsp"
	rm JPL${aster}.bsp
fi
ln -s *${name:4:7}*.bsp JPL${aster}.bsp
echo "results/${aster}/JPL${aster}.bsp   ${name:4:7}"
cd ../../
#########################################################################
