#!/bin/bash
#########################################################################
#									#
#	sc_cat.sh 						 	#
#		- list observation files (.obs)		 		#
#		- concatenate different files				#
#									#
#								JD-2014	#
#########################################################################
echo "Asteroid number (ex: 50000, 2007JH43) :"
read aster
#########################################################################
export LC_COLLATE=C
echo ">>> file list <<<"
echo " "
ls -1 obs/${aster}_a.obs
nb=$(find results/$aster -name '*.obs' | wc -l)
if [ $nb -ne 0 ]; then
	ls -1 results/$aster/*.obs
fi
echo " "
echo " "
while [ 1 == 1 ];
do
	echo "file to merge (ENTER to exit, 0 for all files)"
	read infile
	if [ "$infile" == "0" ]; then
		echo "cat all files"
		ls -1 obs/${aster}_a.obs >list.tmp
		if [ $nb -ne 0 ]; then
			ls -1 results/$aster/*.obs >>list.tmp
		fi
		nl=$(wc -l list.tmp | awk '{print $1}')
		for i in $(seq 1 1 $nl ) 
		do
			file=$(awk -v l=$i 'NR==l{ print $1 }' list.tmp)
			sed '1d' $file >fich.obs
			cat fich.obs >> merge.obs
		done
		mv merge.obs obs/${aster}_m.obs
		rm fich.obs  list.tmp
		exit; 
	fi	
	if [ -n "$infile" ]; then
		sed '1d' $infile >fich.obs
		cat fich.obs >> merge.obs
	else
		mv merge.obs obs/${aster}_m.obs
		rm fich.obs 
		exit; 
	fi
done
#########################################################################
