#!/bin/bash
#########################################################################
#									#
#	sc_ephem.sh							#
#		script to compute ephemeris				#
#		- sc_ephem.sh -f : input required			#
#									#
### Asteroid ############################################################
aster=10199		# Asteroid number (or name if unumbered)	#
			#						#
### Options #############################################################
file=1			# Type of computation				#
			# 	- 0 : Numerical integration (uncert.)	#
			# 	- 1 : bsp (no uncertainty)		#
			# 	- 2 : bsp/JPL (no uncertainty)		#
use_prec=1		# Uncertainty of ephemerides (0:N,1:Y)		#
			# 	only available with num. integration 	#
ech=1			# Time scale					#
			# 	- 0 : TT				#
			# 	- 1 : UTC				#
date=0			# Type of date					#
			# 	- 0 : Julian date			#
			# 	- 1 : Gregorian date			#
typ=0			# Type of ephemerides				#
			# 	- 0 : astrometric (with light corr.)	#
			# 	- 1 : geometric	(without light corr.)	#
codeobs=500		# Observatory code IAU				#
### Positions ###########################################################
pas=30			# step between each position			#
unit=m			# unit (d/j : day; h: hour; m: min, s: sec) 	#
format=2		# date format (start and end dates)		#
			#	0: Julian date				#
			#	1: year					#
			#	2: yyyy-mm-day@hh:mm:ss			#
			#						#
datdeb=2017-01-01@00:00	# Starting date of ephemerides			#
datfin=2019-01-01@00:00	# Last date of ephemerides			#
			#						#
### Perturbations (if file=0) ###########################################
use_pla=1		# Planets perturbations				#
			#	0: no - 2body problem			#
			#	1: Me,V,EMB,Ma,J,S,U,N			#
			#	2: Me,V,EMB,Ma,J,S,U,N,P		#
			#	3: Me,V,T,L,Ma,J,S,U,N			#
			#	4: Me,V,T,L,Ma,J,S,U,N,P		#
#########################################################################
if [ "$1" == "-f" ]; then
	echo "Input directly read in sc_ephem.sh"
	echo " "
else
	echo ">>> Asteroid number (or name if unumbered)?"
	read aster
	if [ ! -e "ci/ci_$aster.dat" -o ! -e "obs/$aster.obs" ]; then
		echo ">>>>>>>>>> No observation file and/or orbital elements file <<<<<<<<<<";
		echo " "
		exit
	fi
	echo ">>> Source of ephemeris#"
	echo "    0: Numerical integration (possible uncert.)"
	echo "    1 : bsp (default) "
	echo "    2 : bsp/JPL "
	read file
	if [ -f $file ]; then
		file=1
	fi
	
	if [ $file -eq 0 ]; then
		echo ">>> Uncertainty of ephemeris (0:N,1:Y(default))"
		read use_prec
		if [ -f $use_prec ]; then
			use_prec=1
		fi
		echo ">>> Planets perturbations ?"
		echo "    0: no - 2body problem	"
		echo "    1: Me,V,EMB,Ma,J,S,U,N (default)	"
		echo "    2: Me,V,EMB,Ma,J,S,U,N,P"
		echo "    3: Me,V,T,L,Ma,J,S,U,N	"
		echo "    4: Me,V,T,L,Ma,J,S,U,N,P"
		read use_pla
		if [ -f $use_pla ]; then
			use_pla=1
		fi
	fi

	echo ">>> Time scale"
	echo "    0: TT (default)"
	echo "    1: UTC "
	read ech
	if [ -f $ech ]; then
		ech=0
	fi
	echo ">>> Type of date "
	echo "    0: Julian date"
	echo "    1: Gregorian date (default)"
	read date
	if [ -f $date ]; then
		date=1
	fi
	echo ">>> Type of ephemeris"
	echo "    0: astrometric (with light corr.)(default)"
	echo "    1: geometric (without light corr.)"
	read typ
	if [ -f $typ ]; then
		typ=0
	fi
	echo ">>> Observatory code IAU	(default:500)"
	read codeobs
	if [ -f $codeobs ]; then
		codeobs=500
	fi
	echo ">>> Positions "
	echo ">>> Step between each position (default:1)	"
	read pas
	if [ -f $pas ]; then
		pas=1
	fi
	echo ">>> Unit of step (default: d)"
	echo "    d: day"
	echo "    h: hour"
	echo "    m: minute"
	echo "    s: second"
	read unit
	if [ -f $unit ]; then
		unit=d
	fi
	echo ">>> Date format"
	echo "    0: julian date    "
	echo "    1: year "
	echo "    2: yyyy-mm-dd@hh:mm:ss (default)"
	read format
	if [ -f $format ]; then
		format=2
	fi
	echo ">>> Period of validity"
	echo ">>> Date of beginning  (default:2018-01-01)"
	read datdeb
	if [ -f $datdeb ]; then
		datdeb=2018-01-01
	fi
	echo ">>> Date of end  (default:2019-01-01)"
	read datfin
	if [ -f $datfin ]; then
		datfin=2019-01-01
	fi
	echo "Ok, let's go..."
fi
if [ ! -d "results/$aster"  ]; then
	echo "Asteroid has not been fitted " 
	echo "Proceed to its fitting 'sc_fit.sh'" 
	exit
else 
	cd exe/
	ddat=$( date -u '+%Y-%m-%d %H:%M (%Z)' )
	echo "$ddat"
	echo "$ddat" >dat.tmp
	echo "$aster "
	if [ $file -eq 0 ]; then
		if [ $use_prec -eq 1 ]; then
			if [ -e ../results/$aster/cov.mat ]; then
				cp ../results/$aster/cov.mat cov.mat
			else
				echo "No covariance matrix available ";
				echo "Please, proceed to fitting process";
				rm *.tmp
				exit
			fi	
		fi
		cp ../results/$aster/CI_ast.dat CI_ast.dat
		echo " "
		echo "Ephemeris computation with numerical integration"
		echo " "
		echo "$pas
		$unit
		$use_prec
		$use_pla
		$ech
		$typ
		$date
		$codeobs
		$format
		$datdeb
		$datfin"|./ephemni.out
		mv ephem.res ../results/$aster/ephemni.res
		rm CI_ast.dat
		if [ -e cov.mat ]; then
			rm cov.mat
		fi	
	fi
		
	if [ $file -eq 1 ]; then
		if [ -e ../results/$aster/${aster}*nima*.bsp ]; then
			cp ../results/$aster/$aster*nima*.bsp ast.bsp
		else
			echo "No bsp file";
			echo "Please, proceed to make of bsp file";
			rm *.tmp
			exit
		fi
		echo " "
		echo "NIMA" >CI.txt
		cat ../results/$aster/CI_ast.dat >> CI.txt
		## Recherche parametres magnitudes
		#chem=$( pwd )
		#echo "$chem"
		#cd ../lib/toolkit/exe
		#cp $chem/ast.bsp .
		#./commnt -r ast.bsp >inf.txt
		#sed -n '/E>>>>/,/S>>>>/p' inf.txt >CI.txt
		#mv CI.txt $chem
		#rm ast.bsp inf.txt
		#cd $chem
		#
		echo "Ephemeris computation with bsp file"
		echo " "
		target=$(echo "$aster"|../idspk.sh)
		echo "$target
		$pas
		$unit
		$ech
		$typ
		$date
		$codeobs
		$format
		$datdeb
		$datfin"|./ephembspSUN.out
		mv ephem.res ../results/$aster/ephembsp.res
		rm ast.bsp CI.txt 
	fi
	if [ $file -eq 2 ]; then
		if [ -e ../results/$aster/JPL${aster}*.bsp ]; then
			cp ../results/$aster/JPL$aster*.bsp ast.bsp
		else
			echo "No bsp JPL file";
			echo "Please, import bsp file from JPL";
			rm *.tmp
			exit
		fi
		echo " "
		echo "JPL" >CI.txt
		echo "Ephemeris computation with bsp file"
		echo " "
		target=$(echo "$aster"|../idspk.sh)
		echo "$target
		$pas
		$unit
		$ech
		$typ
		$date
		$codeobs
		$format
		$datdeb
		$datfin"|./ephembspSUN.out
		mv ephem.res ../results/$aster/ephembspjpl.res
		rm ast.bsp CI.txt 
	fi
	rm *.tmp
	cd ../
fi
#########################################################################
