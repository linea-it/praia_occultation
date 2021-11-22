#!/bin/bash
#########################################################################
#									#
#	sc_fit.sh							#
#		script for fitting process				#
#		- sc_fit.sh -f : no input required			#
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
### Fitting process / O-C computation ###################################
use_ddp=1		# 1: Fitting 0: O-C computation only		#
use_rms=2		# Weighting process				#
			# 	0: rms					#
			# 	1: rms constant				#
			# 	2: rms astdys				#
use_bias=1		# biais correction (bias in stellar catalogues)	#
naj=6			# number of fiiting steps			#
use_rejet=1		# Rejection of outliers				#
			# 	0: threshold values			#
			# 	1: flag astdys				#
seuil=3			# threshold for outliers (arcsec)		#
plot_omc=0		# plot of residuals				#
			# 		0 = no				#
			#		1 = png file			#
#########################################################################
if [ "$1" == "-f" ]; then
	echo "Input directly read in sc_fit.sh"
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
	echo ">>> Fitting process"
	echo "    0: O-C computation only"
	echo "    1: Fitting (default)"
	read use_ddp
	if [ -f $use_ddp ]; then
		use_ddp=1
	fi
	echo ">>> Weighting process "
	echo "    0: computed rms    "
	echo "    1: constant rms"
	echo "    2: rms astdys (default)	"
	read use_rms
	if [ -f $use_rms ]; then
		use_rms=2
	fi
	echo ">>> Bias correction (0:no; 1:yes (default))"
	read use_bias
	if [ -f $use_bias ]; then
		use_bias=1
	fi
	echo ">>> Maximum number of fitting steps  (default:6)"
	read naj
	if [ -f $naj ]; then
		naj=6
	fi
	echo ">>> Rejection of outliers	"
	echo "    0: threshold values	"	
	echo "    1: flag astdys (default)	"
	echo "    2: Khi2 rejection"
	read use_rejet
	if [ -f $use_rejet ]; then
		use_rejet=1
	fi
	if [ $use_rejet -eq 0 ]; then
		echo ">>> Threshold in arcsec (default:1arcsec)"
		read seuil
		if [ -f $seuil ]; then
			seuil=1
		fi
	else
		seuil=1
	fi 
	if [ $use_rejet -eq 2 ]; then
		echo ">>> Threshold sqrt(X) (default: X=8)"
		read seuil
		if [ -f $seuil ]; then
			seuil=8
		fi
	else
		seuil=1
	fi 
	echo ">>> Plot of residuals (O-C)"
	echo "    0 = no (default)	"
	echo "    1 = png file	"
	read plot_omc
	if [ -f $plot_omc ]; then
		plot_omc=0
	fi
	echo "Ok, let's go..."
fi
if [ ! -e "ci/ci_$aster.dat" -o ! -e "obs/$aster.obs" ]; then
	echo ">>>>>>>>>> No observation file and/or orbital elements file <<<<<<<<<<";
	echo " "
	exit
fi
if [ ! -d "results/$aster"  ]; then
	echo ">>>>>>>>>> Creation of  results/$aster/ directory <<<<<<<<<< "
	mkdir results/$aster
	echo " "
	echo " "
fi
cd exe/
cp ../ci/ci_$aster.dat CI_ast.dat
cp ../obs/$aster.obs obs.dat
echo ">>>>>>>>>> Orbit determination of $aster <<<<<<<<<<"
echo " "
echo "$use_pla
$use_ddp
$use_bias
$use_rms
$use_rejet
$naj	
$seuil
0"|./fitobs.out
if [ $use_ddp -ge 1 ]; then
	mv CIn.dat ../results/$aster/CI_ast.dat
	mv correl.mat ../results/$aster
	mv cov.mat ../results/$aster/cov.mat
fi
sort -k2 omc_ast.res >../results/$aster/omc_ast.res
rm omc_ast.res
if [ $plot_omc -ge 1 ]; then
	cat omc_opt.res | cut -c '-7' >tmp.tmp
	ntmp=$(wc -l tmp.tmp | awk '{print $1}')
	yb1=$(awk -v l=1 'NR==l{ print $1 }' tmp.tmp )
	ye1=$(awk -v l=$ntmp 'NR==l{ print $1 }' tmp.tmp )
	echo "$yb1 - $ye1"
	(( yb = $yb1 - 5 ))
	(( ye = $ye1 + 5 ))
	(( diff= $ye- $yb ))
	echo "$yb - $ye"
	tic=5
	if [  $diff -ge 25 ]; then
		tic=5
	fi
	if [  $diff -ge 50 ]; then
		tic=10
	fi
	if [  $diff -ge 100 ]; then
		tic=20
	fi
	echo "unset key" >plot.gp
	echo "set term svg" >>plot.gp
	echo "set output 'omc_sep.png'" >>plot.gp
	echo "set multiplot layout 2, 1 " >>plot.gp
	echo "set view map" >>plot.gp
	echo "set xtics 1900, $tic" >>plot.gp
	echo "set ytics -2, 0.5" >>plot.gp
	echo "set xrange[$yb:$ye]" >>plot.gp
	echo "set yrange [-2:2]" >>plot.gp
	echo "set xlabel 'date'" >>plot.gp
	echo "set ylabel 'residual in R.A.(arcsec)'" >>plot.gp
	echo "plot 'omc_opt.res' u 1:2:4 w points ps 0.5 pt 6 palette t 'R.A.',0 lc rgb '#000000 't ''" >>plot.gp
	echo "set ylabel 'residual in Dec.(arcsec)'" >>plot.gp
	echo "plot 'omc_opt.res' u 1:3:5 w points ps 0.5 pt 6 palette t 'R.A.',0 lc rgb '#000000 't ''" >>plot.gp
	gnuplot -background white plot.gp
	montage omc_sep.png -mode concatenate -tile 1x1 ../results/$aster/omc_sep.png
	rm plot.gp tmp.tmp *.png
fi
echo " "
rm omc_*.res 
rm CI_ast.dat obs.dat
cd ../
#########################################################################

