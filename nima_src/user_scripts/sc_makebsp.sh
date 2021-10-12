#!/bin/bash
#########################################################################
#									#
#	sc_makebsp.sh							#
#		script to produce bsp file (spicelib)			#
#		- sc_makebsp.sh -i : input required			#
#									#
#									#
### Asteroid ############################################################
aster=10199		# Asteroid number (or name if unumbered)	#
			#						#
### Perturbations #######################################################
use_pla=1		# Planets perturbations				#
			#	0: no - 2body problem			#
			#	1: Me,V,EMB,Ma,J,S,U,N			#
			#	2: Me,V,EMB,Ma,J,S,U,N,P		#
			#	3: Me,V,T,L,Ma,J,S,U,N			#
			#	4: Me,V,T,L,Ma,J,S,U,N,P		#
### Computation of positions ############################################
pas=60			# length of each interval (days)		#
npol=20			# polynomia degree 				#
format=2		# date format 					#
			#	0: julian date				#
			#	1: year yy				#
			#	2: yyyy-mm-dd@hh:mm:ss			#
			#						#
datdeb=2010-01-01	# Date of beginning				#
datfin=2020-01-01	# Date of end					#
			#						#
comp=1			# Comparison between bsp and numerical int.	#
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
	echo ">>> Computation of Chebychev polynomia "
	echo ">>> Length of each intervals (default:60days)"
	read pas
	if [ -f $pas ]; then
		pas=60
	fi
	echo ">>> Polynomia degree (default:20) "
	read npol
	if [ -f $npol ]; then
		npol=20
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
	echo ">>> Date of beginning  (default:2010-01-01)"
	read datdeb
	if [ -f $datdeb ]; then
		datdeb=2010-01-01
	fi
	echo ">>> Date of end  (default:2020-01-09)"
	read datfin
	if [ -f $datfin ]; then
		datfin=2020-01-09
	fi
	echo ">>> Comparison between bsp and numerical integration  (0:No;1:Yes(default))"
	read comp
	if [ -f $comp ]; then
		comp=1
	fi
	echo "Ok, let's go..."
fi
if [ ! -d "results/$aster"  ]; then
	echo "Asteroid has not been fitted " 
	echo "Proceed to its fitting 'sc_fit.sh'" 
	exit
else 
	cd exe/
	cp ../results/$aster/CI_ast.dat CI_ast.dat
	echo " "
	echo ">Computation of positions"
	echo "1
	$pas
	$npol
	$use_pla
	$format
	$datdeb
	$datfin"|./compposcheb.out
	echo " "
	nint=$(awk -v l=1 'NR==l{ print $1 }' nint.tmp)
	rm nint.tmp
	echo ">Computation of Chebychev coefficients"
	echo " "
	echo "$nint
	$npol	
	$datdeb
	$datfin
	"|./cheby.out
	echo "$use_pla " >tmp.tmp
	head -1 coeff_cheby.dat >fst.tmp
	cat fst.tmp CI_ast.dat tmp.tmp coeff_cheby.dat >cheb.dat
	rm func.res
	if [ -e ast.bsp ]; then 
		rm ast.bsp 
	fi
	name=$(awk -v l=2 'NR==l{ print $2 }' cheb.dat)
	date=$( date -u "+%Y-%m-%d %H:%M" )
	valephem=$(awk -v l=1 'NR==l{ print $7 }' cheb.dat)
	nint=$(awk -v l=1 'NR==l{ print $6 }' cheb.dat)
	npol=$(awk -v l=1 'NR==l{ print $5 }' cheb.dat)
	rms=$(awk -v l=5 'NR==l{ print $1 }' cheb.dat)
	nba=$(awk -v l=5 'NR==l{ print $2 }' cheb.dat)
	nbr=$(awk -v l=5 'NR==l{ print $3 }' cheb.dat)
	yrb=$(awk -v l=5 'NR==l{ print $4 }' cheb.dat)
	yre=$(awk -v l=5 'NR==l{ print $5 }' cheb.dat)
	mean_anomaly=$(awk -v l=6 'NR==l{ print $1 }' cheb.dat)
	per_arg=$(awk -v l=6 'NR==l{ print $2 }' cheb.dat)
	lon_node=$(awk -v l=6 'NR==l{ print $3 }' cheb.dat)
	inc=$(awk -v l=6 'NR==l{ print $4 }' cheb.dat)
	exc=$(awk -v l=6 'NR==l{ print $5 }' cheb.dat)
	dga=$(awk -v l=6 'NR==l{ print $6 }' cheb.dat)
	epoch=$(awk -v l=2 'NR==l{ print $1 }' cheb.dat)
	plaper=$(awk -v l=7 'NR==l{ print $1 }' cheb.dat)
	astper=$(awk -v l=7 'NR==l{ print $2 }' cheb.dat)
	rel=$(awk -v l=7 'NR==l{ print $3 }' cheb.dat)
	yarko=$(awk -v l=7 'NR==l{ print $5 }' cheb.dat)
	datdt=$(awk -v l=4 'NR==l{ print $1 }' cheb.dat)
	nbast=$(awk -v l=7 'NR==l{ print $6 }' cheb.dat)
	Hmag=$(awk -v l=3 'NR==l{ print $9 }' cheb.dat)
	Gslop=$(awk -v l=3 'NR==l{ print $10 }' cheb.dat)
	target=$(echo "$aster"|../idspk.sh)
	if [ $target -eq -1 ]; then
		echo "asteroide non repertorie dans le script idspk.sh "
		stop
	fi
	echo ">Production of bsp file"
	echo " Target ID : $target"
	echo "=============================================" >comments.txt
	echo "DATE_OF_CREATION = $date(UT)" >>comments.txt
	echo "PURPOSE = Ephemeris generated by NIMA" >>comments.txt
	echo "ASTEROID_NUMBER = $aster" >>comments.txt
	echo "ASTEROID_NAME = $name" >>comments.txt	
	echo "ASTEROID_SPK_ID = $target" >>comments.txt	
	echo "SOURCE = NIMA_V3" >>comments.txt
	echo "=============================================" >>comments.txt	
	echo "EPOCH_OSCULATING_ELEMENTS = ${epoch:0:15}" >>comments.txt
	echo "ASTEROID_SMA = $dga" >>comments.txt
	echo "ASTEROID_EXC = $exc" >>comments.txt
	echo "ASTEROID_INC = $inc" >>comments.txt
	echo "ASTEROID_LONG_NODE = $lon_node" >>comments.txt
	echo "ASTEROID_ARG_PER = $per_arg" >>comments.txt
	echo "ASTEROID_MEAN_ANO = $mean_anomaly" >>comments.txt
	echo "=============================================" >>comments.txt
	echo "ABSOLUTE_MAGNITUDE_H = $Hmag" >>comments.txt
	echo "G_SLOP = $Gslop" >>comments.txt
	echo "=============================================" >>comments.txt
	echo "OBSERVATIONS_USED = $nba" >>comments.txt
	echo "OBSERVATIONS_REJECTED = $nbr" >>comments.txt
	echo "OBSERVATIONS_TIME_SPAN = $yrb-$yre" >>comments.txt
	echo "OBSERVATIONS_RMS = ${rms:0:5}arcsec" >>comments.txt
	echo "=============================================" >>comments.txt
	if [ $plaper -eq 0 ]; then
		perp=$(echo "No")
	fi
	if [ $plaper -eq 1 ]; then
		perp=$(echo "Me,V,EMB,Ma,J,S,U,N")
	fi
	if [ $plaper -eq 2 ]; then
		perp=$(echo "Me,V,EMB,Ma,J,S,U,N,P")
	fi
	if [ $plaper -eq 3 ]; then
		perp=$(echo "Me,V,E,Mo,Ma,J,S,U,N")
	fi
	if [ $plaper -eq 4 ]; then
		perp=$(echo "Me,V,E,Mo,Ma,J,S,U,N,P")
	fi
	echo "PLANET_PERTURBATIONS = $perp" >>comments.txt
	echo "MAIN_AST_PERTURBATIONS = No" >>comments.txt
	echo "RELATIVITY = No" >>comments.txt
	echo "YARKOVSKY_DRIFT = No" >>comments.txt
	echo "=============================================" >>comments.txt
	echo "VALIDITY_EPHEMERIS_START = ${valephem:0:10} " >>comments.txt
	echo "VALIDITY_EPHEMERIS_END = ${valephem:11:21} " >>comments.txt
	echo "CHEBYCHEV_INTERVAL = $nint" >>comments.txt
	echo "CHEBYCHEV_POL_DEGREE = $npol" >>comments.txt
	echo "=============================================" >>comments.txt
	echo "NUMBER_OF_MAIN_AST = 0" >>comments.txt
	echo " ">>comments.txt
	echo " ">>comments.txt
	echo " ">>comments.txt
	echo "H= $Hmag   G= $Gslop" >>comments.txt
	echo "E>>>>">>comments.txt
	cat comments.txt CI_ast.dat tmp.tmp >tmp.txt
	mv tmp.txt comments.txt
	echo "S>>>>">>comments.txt
	echo "$target"|./makebsp.out
	if [ "$aster" = "$name" ]; then
		mv ast.bsp ../results/$aster/${aster}_nima.bsp
	else
		mv ast.bsp ../results/$aster/${aster}_${name}_nima.bsp
	
	fi
	if [ $comp -eq 1 ]; then
		echo " "
		echo " "
		echo "Comparison bsp/num.int. "
		cp ../ci/ci_$aster.dat CI0.dat
		cp ../results/$aster/${aster}*nima*.bsp ast.bsp
		echo " "
		echo "Positions with Numerical Integration"
		echo "720
		$use_pla
		1
		${datdeb:0:4}
		${datfin:0:4}
		0
		0"|./calposn.out
		cp posvit_ast.res posvit1.res
		echo " "
		echo "Positions with bsp file"
		target=$(echo "$aster"|../idspk.sh)
		echo "$target
		720
		1
		${datdeb:0:4}
		${datfin:0:4}
		0
		0"|./calposb.out
		cp posvit_ast.res posvit2.res
		./diff.out
		echo "import matplotlib" >diff.py
		echo "matplotlib.use('Agg')" >>diff.py
		echo "import matplotlib.pyplot as plt" >>diff.py
		echo "import numpy as np" >>diff.py
		echo "" >>diff.py
		echo "namefile = 'diff.res'" >>diff.py
		echo "" >>diff.py
		echo "diff, date = np.loadtxt(namefile, usecols=(1,2), unpack=True)" >>diff.py
		echo "" >>diff.py
		echo "plt.figure(figsize=(10, 8), dpi=90)" >>diff.py
		echo "plt.semilogy(date, diff, 'k')" >>diff.py
		echo "plt.title('Difference between bsp and numerical integration', fontsize=15, y=1.02, weight='bold')" >>diff.py
		echo "plt.xlim([${datdeb:0:4},${datfin:0:4}])" >>diff.py
		echo "plt.xlabel('Date', fontsize=15, labelpad=5, weight='bold')" >>diff.py
		echo "plt.xticks(fontweight='bold')" >>diff.py
		echo "plt.yticks(fontweight='bold')" >>diff.py
		echo "plt.ylabel('Difference (km) ', fontsize=15, labelpad=5, weight='bold')" >>diff.py
		echo "plt.savefig('diff_bsp-ni.png', bbox_inches='tight')" >>diff.py
		python2.7 diff.py
		echo " "
		echo "png file of difference "
		mv diff_bsp-ni.png ../results/$aster/diff_bsp-ni.png
		rm *.res diff.py ast.bsp
	fi
	rm *.dat
	rm *.tmp comments.txt 
	cd ..
fi
#########################################################################