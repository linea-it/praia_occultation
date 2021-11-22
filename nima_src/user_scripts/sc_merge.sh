#!/bin/bash
#########################################################################
#									#
#	sc_merge.sh 						 	#
#		- possible merge of observations per night 		#
#		- change the weight according to the merge choice	#
#									#
#								JD-2018	#
#########################################################################
echo "Asteroid number (ex: 50000, 2007JH43) :"
read aster
echo "Timing threshold in sec for doublons (default: 60s) :"
read stime
echo "Type of merging"
echo "   > 0 : No merging, weight unchanged (v1)"
echo "   > 1 : Night merging, weight changed (v2)"
echo "   > 2 : No merging, weight changed (default, v3)"
read merge
#########################################################################
export LC_COLLATE=C
export LC_NUMERIC=C
if [ -f $stime ]; then
	stime=60
fi
if [ -f $merge ]; then
	merge=2
fi
if [ -e obs/${aster}_m.obs ]; then
	# Recherche de doublons
	grep "^O" obs/${aster}_m.obs >tmp.obs
	sort -k7,7 -k2,2 tmp.obs >exe/fich.obs
	rm tmp.obs 
	cd exe/
	nl=$(wc -l fich.obs | awk '{print $1}')
	echo "$stime
	$nl"|./trackdoublon.out
	nd=$(wc -l doub.obs | awk '{print $1}')
	if [ $nd -ne 0 ]; then
		echo "There is suspicion of doublons"
		echo " -> see file : doub.obs"
		mv doub.obs ../
		echo " "
		echo " -> press ENTER to continue"
		read
	fi
	cd ../
	rm exe/fich.obs
	#
fi

if [ $merge -eq 1 ]; then
    if [ -e obs/${aster}_m.obs ]; then
    	cd exe/
        cp ../obs/${aster}_m.obs obs.dat
        grep "s " obs.dat > fich.spc
        grep -v "s " obs.dat > fich.obs
        #sort  +6 -7 fich.obs >obs.obs
        sort  -k7 -k12.1n fich.obs >obs.obs
        #sort -k7 fich.obs >obs.obs
        nl=$(wc -l  obs.obs | awk '{print $1}')
        echo "$nl"|./merge1.out
        sort -k2 obsn.obs >obs.obs
        ./numbernight.out
        cat obsn.obs fich.spc >	ficha.obs
        sort -k2 ficha.obs >../obs/${aster}_n.obs
        cp ../obs/${aster}_n.obs ../obs/$aster.obs
        rm obsn.obs
        rm obs.dat fich.obs fich.spc ficha.obs
	cd ../
    else
        echo "No merge file : use script_cat.sh"
    fi
fi
if [ $merge -eq 2 ]; then
    if [ -e obs/${aster}_m.obs ]; then
        cd exe/
	cp ../obs/${aster}_m.obs obs.dat
        grep "s " obs.dat > fich.spc
        grep -v "s " obs.dat > fich.obs
        #sort  +6 -7 +12 -13 fich.obs >obs.obs
        sort  -k7,7 -k13,14 fich.obs >obs.obs
        nl=$(wc -l  obs.obs | awk '{print $1}')
        echo "$nl"|./merge2.out
        #sort +1 -3 +12 -14 obsn.obs >obs.obs
        sort -k2,4 obsn.obs >obs.obs
        #./numbernight.out
        #cat obsn.obs fich.spc >	ficha.obs
        cat obs.obs fich.spc >	ficha.obs
        sort -k2 ficha.obs >../obs/${aster}_n.obs
        cp ../obs/${aster}_n.obs ../obs/$aster.obs
        rm obsn.obs obs.obs
        rm obs.dat fich.obs fich.spc ficha.obs
	cd ../
    else
        echo "No merge file : use script_cat.sh"
    fi
fi
echo " "

#########################################################################
