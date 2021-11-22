#!/bin/bash
#########################################################################
#									#
#	sc_wget.sh 						 	#
#		- download observations file and/or orbital elements	#
#		  from AstDys or MPC			 		#
#		- convert the files into NIMA format			#
#									#
#								JD-2018	#
#########################################################################
echo "Asteroid number (ex: 50000, 2007JH43) :"
read aster
#aster=137295
#aster=1999_RC216
#aster=145452
echo "Asteroid name (ex: Quaoar, 2007JH43) :"
read name
#name=1999_RB216
#name=1999_RC216
#name=2005_RN43
echo "Path of observation files:"
read pathObs
#pathObs=/home/usuario/Documents/doutorado/NIMA/AstDySMPC/observations
echo "Path of orbital parameters files:"
read pathOrb
#pathOrb=/home/usuario/Documents/doutorado/NIMA/AstDySMPC/orbitalParametes
#########################################################################

cd exe/
#AstDyS
if [ -f $pathObs/$name.rwo ] && [ -f $pathOrb/$name.eq0 ]; then
    cp $pathObs/$name.rwo $aster.rwo
    cp $pathOrb/$name.eq0 $aster.eq0
    # -> orbital elements
    cp $aster.eq0 fich.eq0
	echo "0
	$name"|./transfci.out
	mv ci.dat ../ci/ci_$aster.dat
	mv $aster.eq0 ../ci/
	rm fich.eq0
    # -> observations
    cp $aster.rwo fich.rwo
    nlig=$(wc -l  fich.rwo | awk '{print $1}')
    echo "$nlig"|./transfobs.out
    sort -k2 fich.obs >ficht.obs
    cat fich.obs fich.spc >	ficha.obs
    sort -k2 ficha.obs >ficht.obs
    cp ficht.obs ../obs/${aster}_a.obs
    mv ficht.obs ../obs/$aster.obs
    rm ficha.obs
    mv $aster.rwo ../obs/
    rm fich*.obs fich.rwo fich.spc
#MPC
elif [ -f $pathObs/$name.rwm ] && [ -f $pathOrb/$name.eqm ]; then
    cp $pathObs/$name.rwm $name.txt
    cp $pathOrb/$name.eqm ci.eqm
    echo "1E-15" >mass.tmp
    ./transfciMPC.out
    mv ci.dat ../ci/ci_$aster.dat
    #		mv $aster.eqm ../ci/
    # -> observations
    echo " -> Observations file"
    if [ -e $name.txt ]; then
        cp $name.txt obs.mpc
        nl=$(wc -l  obs.mpc | awk '{print $1}')
        echo "$nl"|./transfobsMPC.out
        sort -k7,7 -k2,4 obs.obs > obst.obs
        nl=$(wc -l  obst.obs | awk '{print $1}')
        if [ $nl -ne 0 ]; then
            echo "$nl"|./compnuit.out
            sort -k2 obsn.obs >obs.obs
        else
            cp obst.obs obs.obs
        fi
        cat obs.sob obs.obs obs.spc obs.rad > ficha.obs
        sort -k2 ficha.obs > fichb.obs
        cat obs.inf fichb.obs >../obs/$aster.obs
        cp ../obs/$aster.obs ../obs/${aster}_a.obs
        mv $name.txt ../obs/$aster.mpc
        rm obs*.* fich*.obs
    fi
else
    echo "There are no files of the $name "
fi






















