#!/bin/bash
#########################################################################
#									#
#	sc_esoopd.sh							#
#		- convert observation from offset format to nima format	#
#									#
#########################################################################
echo "Asteroid number (ex: 50000, 2007JH43) :"
read aster
echo "Asteroid name (ex: Quaoar, 2007JH43) :"
read name
#########################################################################
export LC_COLLATE=C
export LC_NUMERIC=C
if [ -f $name ]; then
	name=$aster
fi
if [ ! -e results/$aster/${name}.txt ]; then
	echo "No file : results/$aster/${name}.txt"
	echo ""
else
	cd exe/
	supobs=DIV 
	opd=4	
	echo "$aster   $supobs "
	cp ../results/$aster/${name}.txt ../results/$aster/offset_oth.dat
	jd=$(awk -v l=$n2 'NR==l{ print $8 }' ../results/$aster/offset_oth.dat )
	cp ../results/$aster/offset_oth.dat offset.dat
	noboffset=$(wc -l  offset.dat | awk '{print $1}')
	(( n2 = $noboffset / 2 ))
	echo "nbre obs fichier offset : $noboffset"
	echo "$noboffset
	$opd
	1
	0"|./offset.out
	yonb=$(awk -v l=$n2 'NR==l{ print $2 }' offset.obs )
	mv offset.obs ../results/$aster/offset_oth.obs
	sort -k2 ../results/$aster/offset_oth.obs >tmp.txt
	mv tmp.txt ../results/$aster/offset_oth.obs
	echo "year: $yonb"
	rm *.dat
	cd ../
fi
#########################################################################
