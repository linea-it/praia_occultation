#!/bin/bash
#########################################################################
#									#
#	sc_diffjplomc.sh 					 	#
#		- orbit determination, then comparison with JPL 	#
#		  ephemeris and plot with O-C				#
#		- sc_diffjplomc.sh -f : input required			#
#									#
#								JD-2017	#
#########################################################################
aster=10199		# Asteroid number/name				#
			#						#
jplephem=1              # center for JPL ephemeris (0 = SSB, 1 = Sun)   #
			#						#
### Perturbations #######################################################
use_pla=1		# Planet perturbations				#
			#	0: no 					#
			#	1: Me,V,EMB,Ma,J,S,U,N			#
			#	2: Me,V,EMB,Ma,J,S,U,N,P		#
			#	3: Me,V,T,L,Ma,J,S,U,N			#
			#	4: Me,V,T,L,Ma,J,S,U,N,P		#
### Fitting process / O-C computation ###################################
use_rms=2		# Weighting process				#
			# 	0: rms					#
			# 	1: rms constant				#
			# 	2: rms astdys				#
use_bias=1		# biais correction (bias in stellar catalogues)	#
naj=6			# number of fiiting steps			#
use_rejet=1		# Rejection of outliers				#
			# 	0: threshold values			#
			# 	1: flag astdys				#
seuil=8			# threshold for outliers (arcsec)		#
plot_omc=1		# plot of residuals				#
			# 		0 = no				#
			#		1 = yes				#
format_plot=1		# format of the plot				#
			# 		0 = png (default)		#
			#		1 = pdf				#
### Positions ###########################################################
pas=4			# step between each position			#
unit=d			# unit (d/j : day; h: hour; m: min, s: sec) 	#
format=2		# date format (start and end dates)		#
			#	0: Julian date				#
			#	1: year					#
			#	2: yyyy-mm-day@hh:mm:ss			#
			#						#
datdeb=2012-01-01@00:00	# Starting date of ephemerides			#
datfin=2020-01-01@00:00	# Last date of ephemerides			#
			#						#
mina=000		# range for plot R.A.				#
maxa=000		#						#
mind=-200		# range for plot Dec.				#
maxd=100		#						#
#########################################################################
export LC_COLLATE=C
if [ "$1" == "-f" ]; then
	echo "Input directly read in sc_diffjplomc.sh"
	echo " "
	if [ ! -e results/$aster/JPL${aster}*.bsp ]; then
		echo "No bsp JPL file";
		echo "Please, import bsp file from JPL";
		exit
	fi
else
	echo ">>> Asteroid number (or name if unumbered)?"
	read aster
	if [ ! -e "ci/ci_$aster.dat" -o ! -e "obs/$aster.obs" ]; then
		echo ">>>>>>>>>> No observation file and/or orbital elements file <<<<<<<<<<";
		echo " "
		exit
	fi
	if [ ! -e results/$aster/JPL${aster}*.bsp ]; then
		echo "No bsp JPL file";
		echo "Please, import bsp file from JPL";
		exit
	fi
	echo ">>> Center of ephemeris in JPL (0: SSB -default-, 1: Sun) ?"
	read jplephem
	if [ -f $jplephem ]; then
		jplephem=0
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
	echo "    1 = yes	"
	read plot_omc
	if [ -f $plot_omc ]; then
		plot_omc=0
	fi
	echo ">>> Format of plots"
	echo "    0 = png (default)	"
	echo "    1 = pdf"
	read format_plot
	if [ -f $format_plot ]; then
		format_plot=0
	fi
        fmt=png
        if [ $format_plot -eq 1 ]; then
                fmt=pdf
        fi

 	echo ">>> Difference with JPL Ephemeris		"
 	echo ">>> Step between each position (default: 4)"
	read pas
	if [ -f $pas ]; then
		pas=4
	fi
 	echo ">>> Unit  (d/j : day; h: hour; m: min, s: sec) (default: d)"
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
	echo ">>> Ephemeris"
	echo ">>> Date of beginning  (default:2012-01-01)"
	read datdeb
	if [ -f $datdeb ]; then
		datdeb=2012-01-01
	fi
	echo ">>> Date of end  (default:2020-01-01)"
	read datfin
	if [ -f $datfin ]; then
		datfin=2020-01-01
	fi
	echo ">>> Scale for plot (R.A. and Dec. range) "
	echo ">>> min R.A. in mas (default : automatic) "
	read mina
	if [ -f $mina ]; then
		mina=000
		maxa=000
		mind=000
		maxd=000
	else
		echo ">>> max R.A. (in mas) "
		read maxa
		echo ">>> min Dec. (in mas) "
		read mind
		echo ">>> max Dec. (in mas) "
		read maxd
	fi
	echo "Ok, let's go..."
fi
echo "Nom de l'asteroide : $aster"
if [ ! -d "results/$aster"  ]; then
	echo "creation du repertoire results/$aster/" 
	mkdir results/$aster
fi
cd exe/
cp ../ci/ci_$aster.dat CI_ast.dat
cp ../obs/$aster.obs obs.dat
cp ../obs/$aster.obs obs0.dat
if [ -e omc_occ.res ]; then
	rm omc_occ.res
fi
echo " "
echo ">>>>>>>>>> Orbit determination of $aster <<<<<<<<<<"
echo " "
echo "$use_pla
1
$use_bias
$use_rms
$use_rejet
$naj	
$seuil
0"|./fitobs.out
name=$(awk -v l=1 'NR==l{ print $2 }' CIn.dat)
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
        echo "import matplotlib" > plot.py
        echo "matplotlib.use('Agg')" >> plot.py
        echo "import numpy as np" >> plot.py
        echo "import matplotlib.pyplot as plt" >> plot.py
        echo "" >> plot.py
        echo "def makeResidualPlot(xlimits, ylimits, outFile):" >> plot.py
        echo "    c1, c2, c3, c4, c5 = np.loadtxt('omc_opt.res', usecols=(0, 1, 2, 3, 4), unpack=True)" >> plot.py
        echo "    fig = plt.figure(dpi=300)" >> plot.py
        echo "" >> plot.py
        echo "    plt.subplot(2, 1, 1)" >> plot.py
        echo "    plt.ticklabel_format(useOffset=False)" >> plot.py
        echo "    plt.axhline(color='k', zorder=-32)" >> plot.py
        echo "    sc = plt.scatter(c1, c2, s=30, c=c4, cmap='plasma', edgecolors='none')" >> plot.py
        echo "    plt.colorbar(sc, aspect=8)" >> plot.py
        echo "    plt.xlim(xlimits)" >> plot.py
        echo "    plt.ylim(ylimits)" >> plot.py
        echo "    plt.xlabel('Date')" >> plot.py
        echo "    plt.ylabel('Residual in R.A.(arcsec)')" >> plot.py
        echo "" >> plot.py
        echo "    plt.subplot(2, 1, 2)" >> plot.py
        echo "    plt.ticklabel_format(useOffset=False)" >> plot.py
        echo "    plt.axhline(color='k', zorder=-32)" >> plot.py
        echo "    sc = plt.scatter(c1, c3, s=30, c=c5, cmap='plasma', edgecolors='none')" >> plot.py
        echo "    plt.colorbar(sc, aspect=8)" >> plot.py
        echo "    plt.xlim(xlimits)" >> plot.py
        echo "    plt.ylim(ylimits)" >> plot.py
        echo "    plt.xlabel('Date')" >> plot.py
        echo "    plt.ylabel('Residual in Dec.(arcsec)')" >> plot.py
        echo "" >> plot.py
        echo "    plt.tight_layout()" >> plot.py
        echo "    plt.savefig(outFile)" >> plot.py
        echo "" >> plot.py
        echo "makeResidualPlot([$yb,$ye], [-2,2], 'omc_sep_all.$fmt')" >> plot.py
        echo "makeResidualPlot([2012,2020], [-0.3,0.3], 'omc_sep_recent.$fmt')" >> plot.py

        python2.7 plot.py

        mv omc_sep_all.$fmt omc_sep_recent.$fmt ../results/$aster/

	rm plot.py tmp.tmp
fi
rm omc_opt.res
mv CIn.dat ../results/$aster/CI_ast.dat
mv correl.mat ../results/$aster
mv cov.mat ../results/$aster/cov.mat
sort -k2 omc_ast.res >../results/$aster/omc_ast.res
tail -1 omc_ast.res >last.tmp
./modat.out >tmp.tmp
datpb=$(awk -v l=1 'NR==l{ print $1 }' tmp.tmp)
datpe=$(awk -v l=2 'NR==l{ print $1 }' tmp.tmp)
rm *.tmp
rm omc_ast.res
cp ../results/$aster/CI_ast.dat CI_ast.dat
cp ../results/$aster/cov.mat cov.mat
ddat=$( date -u '+%Y-%m-%d %H:%M (%Z)' )
echo "$ddat" >dat.tmp
echo " Ephemeris precision every 6 months (${datpb}-${datpe})"
echo " "
echo "180
d
1
$use_pla
0
0
1
500
$format
$datpb
$datpe"|./ephemni.out
grep -v "#" ephem.res >../results/$aster/sigyr.res
echo " "
echo "Ephemeris computation with numerical integration"
echo " "
echo "$pas
$unit
1
$use_pla
0
0
0
500
$format
$datdeb
$datfin"|./ephemni.out
grep -v "#" ephem.res >ephemnima.dat
mv ephem.res ../results/$aster/ephemni.res
rm CI_ast.dat dat.tmp
echo "Ephemeris computation with JPL bsp"
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
if [ $jplephem -eq 0 ]; then
	echo "JPL ephem centered on SSB"
	echo "$target
	$pas
	$unit
	0
	0
	1
	500
	$format
	$datdeb
	$datfin"|./ephembspSSB.out
else
	echo "JPL ephem centered on Sun"
	echo "$target
	$pas
	$unit
	0
	0
	1
	500
	$format
	$datdeb
	$datfin"|./ephembspSUN.out
fi
grep -v "#" ephem.res >ephemjpl.dat
rm ast.bsp CI.txt 

nlephem=$(wc -l  ephemnima.dat | awk '{print $1}')
echo "nb lignes : $nlephem"
echo "$nlephem"|./diffephem.out

sort omc_occ.res >omc_occ.tmp
mv omc_occ.tmp omc_occ.res
nl=$(wc -l  omc_occ.res | awk '{print $1}')

if [ $nl -eq 0 ]; then
	echo "   2000.00000     0.000     0.000      0.0      0.0   0  Z">omc_stat.res
else
	echo "$nl"|./stat.out
fi
if [ $mina -eq $maxa ]; then
	export LC_COLLATE=C
	echo "automatic range for plot"
	awk -F" " '{print $4, $6}' diffephem.res > tmp.tmp
	awk -F" " '{print $5, $7}' diffephem.res >> tmp.tmp
	awk -F" " '{print $2, $3}' omc_stat.res >> tmp.tmp
	sort -k1g tmp.tmp >tmp.res
	mina=$(awk -v l=1 'NR==l{ print $1 }' tmp.res)
	sort -k1gr tmp.tmp >tmp.res
	maxa=$(awk -v l=1 'NR==l{ print $1 }' tmp.res)
	sort -k2g tmp.tmp >tmp.res
	mind=$(awk -v l=1 'NR==l{ print $2 }' tmp.res)
	sort -k2gr tmp.tmp >tmp.res
	maxd=$(awk -v l=1 'NR==l{ print $2 }' tmp.res)
	rm tmp.tmp tmp.res
fi

echo "limit ra : $mina, $maxa "
echo "limit de : $mind, $maxd "

echo "import matplotlib" > prec.py
echo "matplotlib.use('Agg')" >> prec.py
echo "import numpy as np" >> prec.py
echo "import matplotlib.pyplot as plt" >> prec.py

echo "" >> prec.py
echo "def makePlot(number, name, ref, x, y1, y2, y3, y4, y5, y6, limits, outName):" >> prec.py
echo "    plt.figure(figsize=(12, 8), dpi=90)" >> prec.py
echo "    plt.title('NIMA-JPL // (' + number + ')' + name, fontsize=20, y=1.04, fontweight='bold')" >> prec.py
echo "    plt.xlabel('Date', fontsize=20, labelpad=10, fontweight='bold')" >> prec.py
echo "    plt.ylabel('Difference in ' + ref + ' (mas)', fontsize=20, labelpad=10, fontweight='bold')" >> prec.py
echo "    plt.ylim(limits)" >> prec.py
echo "    plt.grid(True, axis='y', linestyle='dashed')" >> prec.py
echo "    plt.fill_between(x, y2, y3, color='gray',alpha=.4)" >> prec.py
echo "    plt.plot(x, y1, linewidth=2, c='black')" >> prec.py
echo "    for xo in y4:" >> prec.py
echo "        plt.axvline(x=xo, color='k', linestyle='dotted', zorder=-32)" >> prec.py
echo "    plt.errorbar(y4, y5, yerr=y6, elinewidth =1.2, markersize=16, fmt='.')" >> prec.py
echo "    plt.ticklabel_format(useOffset=False)" >> prec.py
echo "    plt.xticks(fontweight='bold', fontsize=20)" >> prec.py
echo "    plt.yticks(fontweight='bold', fontsize=20)" >> prec.py
echo "    plt.savefig(outName)" >> prec.py
echo "" >> prec.py
echo "c1, c2, c3, c4, c5, c6, c7 = np.loadtxt('diffephem.res', usecols=(0, 1, 2, 3, 4, 5, 6), unpack=True)" >> prec.py
echo "p1, p2, p3, p4, p5 = np.loadtxt('omc_stat.res', usecols=(0, 1, 2, 3, 4), unpack=True, ndmin = 2)" >> prec.py
echo "" >> prec.py
echo "makePlot('$aster', '$name', 'R.A.', c1, c2, c4, c5, p1, p2, p4, [$mina,$maxa], 'diff_nima_jpl_RA.$fmt')" >> prec.py
echo "makePlot('$aster', '$name', 'Dec.', c1, c3, c6, c7, p1, p3, p5, [$mind,$maxd], 'diff_nima_jpl_Dec.$fmt')" >> prec.py
python2.7 prec.py
mv diff_nima_jpl_RA.$fmt diff_nima_jpl_Dec.$fmt ../results/$aster/
rm prec.py cov.mat  
rm *.dat *.res

cd ..
#########################################################################
