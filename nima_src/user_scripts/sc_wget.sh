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
echo "Asteroid name (ex: Quaoar, 2007JH43) :"
read name
echo "Creation of observations file (0:no;1:yes)"
read obs
echo "Creation of orbital elements file (0:no;1:yes)"
read ci
echo "Source of data (0: AstDys, 1: MPC)"
read src
#########################################################################
if [ -f $name ]; then
	name=$aster
fi
if [ -f $obs ]; then
	obs=1
fi
if [ -f $ci ]; then
	ci=1
fi
if [ -f $src ]; then
	src=0
fi
if [ $src -eq 1 ]; then
	if [ "$aster" != "$name" ]; then
	    echo "The object $aster/$name should have only a designation (no name, no number)"
	    echo "In that case, use AstDyS as source of data"
	    exit
	fi
	ci=1
	obs=1
fi
export LC_COLLATE=C
if [ ! -d "results/$aster"  ]; then
	echo "creation of directory results/$aster/" 
	mkdir results/$aster
fi
if [ $ci -eq 1 ]; then
	cd exe/
	if [ $src -eq 0 ]; then # Source AstDys
	 	echo "Download orbital elements"
		((ind = $aster / 1000 ))
		wget http://hamilton.dm.unipi.it/~astdys2/epoch/numbered/$ind/$aster.eq0	
		if [ ! -e $aster.eq0 ]; then
			echo "No file in the numbered asteroids in AstDys"
			echo "Try to download from unumbered "
			ind=$(echo ${aster:0:5})
			wget http://hamilton.dm.unipi.it/~astdys2/epoch/unumbered/$ind/$aster.eq0
			if [ ! -e $aster.eq0 ]; then
				echo "No orbital elements file for $name"
				exit
			fi
		fi
		if [ -f $name ]; then
			echo "No name for asteroid"
			name=$aster
			echo "     Asteroid name : $name "
			echo " "
		fi
		cp $aster.eq0 fich.eq0
		echo "0
		$name"|./transfci.out
		mv ci.dat ../ci/ci_$aster.dat
		mv $aster.eq0 ../ci/
		rm fich.eq0
	else # source MPC	
		objidtmp=$(echo "${aster:0:4}+${aster:4:6}")
		echo "objid : $objidtmp"	
		curl https://minorplanetcenter.net/db_search/show_object?object_id=${objidtmp} >tmp.html 
		cp tmp.html tmp.tmp
		echo "$aster" >tmp1.tmp
		if [ -e tmp2.tmp ]; then
			rm tmp2.tmp
		fi
		grep "+" tmp1.tmp >tmp2.tmp
		if [ -s tmp2.tmp ]; then
			sed 's/\+/_/g' tmp1.tmp >tmp7.tmp
			objid1=$(awk -v l=1 'NR==l{ print $1 }' tmp7.tmp)
			sed 's/\+//g' tmp1.tmp >tmp7.tmp
			objid=$(awk -v l=1 'NR==l{ print $1 }' tmp7.tmp)
		else
			objid=$(awk -v l=1 'NR==l{ print $1 }' tmp1.tmp)
			objid1=$(awk -v l=1 'NR==l{ print $1 }' tmp1.tmp)
		fi
		grep 'name="number"' tmp.tmp >tmp1.tmp
		cat tmp1.tmp| tr " " "\n" >tmp2.tmp
		grep "value" tmp2.tmp >tmp3.tmp
		sed 's/value=//g' tmp3.tmp >tmp4.tmp
		sed 's/"//g' tmp4.tmp >tmp5.tmp
		number=$(awk -v l=1 'NR==l{ print $1 }' tmp5.tmp)
		if [ -f $number ]; then
			number="no"
		fi

		grep 'name="name"' tmp.tmp >tmp1.tmp
		cat tmp1.tmp| tr " " "\n" >tmp2.tmp
		sed -n '/value/,/\/>"/p' tmp2.tmp >tmp3.tmp
		cat tmp3.tmp| tr "\n" " " >tmp4.tmp
		sed 's/value="//g' tmp4.tmp >tmp5.tmp
		sed 's/"\ \/>\ //g' tmp5.tmp >tmp6.tmp
		sed 's/\ /_/g' tmp6.tmp >tmp7.tmp
		name=$(awk -v l=1 'NR==l{ print $1 }' tmp7.tmp)
		if [ -f $name ]; then
			name="no"
		fi
	
		grep 'name="designation"' tmp.tmp >tmp1.tmp
		cat tmp1.tmp| tr " " "\n" >tmp2.tmp
		sed -n '/value/,/\/>"/p' tmp2.tmp >tmp3.tmp
		cat tmp3.tmp| tr "\n" " " >tmp4.tmp
		sed 's/value="//g' tmp4.tmp >tmp5.tmp
		sed 's/"\ \/>\ //g' tmp5.tmp >tmp6.tmp
		sed 's/\ /_/g' tmp6.tmp >tmp7.tmp
		designation=$(awk -v l=1 'NR==l{ print $1 }' tmp7.tmp)
		if [ -f $designation ]; then
			designation="no"
		fi
	
		if [ "$number" != "no" ]; then
			objid=$number
			echo "rename : $objid"
		fi


		grep 'name="epoch"' tmp.tmp >tmp1.tmp
		cat tmp1.tmp| tr " " "\n" >tmp2.tmp
		grep "value" tmp2.tmp >tmp3.tmp
		sed 's/value=//g' tmp3.tmp >tmp4.tmp
		sed 's/"//g' tmp4.tmp >tmp5.tmp
		epoch=$(awk -v l=1 'NR==l{ print $1,$2 }' tmp5.tmp)
		
		grep '<tr><td>epoch\ JD</td>' tmp.html >tmp1.tmp
		sed 's/<tr><td>epoch\ JD<\/td><td\ class="rj">//g' tmp1.tmp >tmp2.tmp
		sed 's/<\/td><\/tr>//g' tmp2.tmp >tmp3.tmp
		epochjd=$(awk -v l=1 'NR==l{ print $1 }' tmp3.tmp)
		
		grep 'name="peri"' tmp.tmp >tmp1.tmp
		cat tmp1.tmp| tr " " "\n" >tmp2.tmp
		grep "value" tmp2.tmp >tmp3.tmp
		sed 's/value=//g' tmp3.tmp >tmp4.tmp
		sed 's/"//g' tmp4.tmp >tmp5.tmp
		peri=$(awk -v l=1 'NR==l{ print $1 }' tmp5.tmp)
		
		grep 'name="m"' tmp.tmp >tmp1.tmp
		cat tmp1.tmp| tr " " "\n" >tmp2.tmp
		grep "value" tmp2.tmp >tmp3.tmp
		sed 's/value=//g' tmp3.tmp >tmp4.tmp
		sed 's/"//g' tmp4.tmp >tmp5.tmp
		m=$(awk -v l=1 'NR==l{ print $1 }' tmp5.tmp)
		
		grep 'name="node"' tmp.tmp >tmp1.tmp
		cat tmp1.tmp| tr " " "\n" >tmp2.tmp
		grep "value" tmp2.tmp >tmp3.tmp
		sed 's/value=//g' tmp3.tmp >tmp4.tmp
		sed 's/"//g' tmp4.tmp >tmp5.tmp
		node=$(awk -v l=1 'NR==l{ print $1 }' tmp5.tmp)
	
		grep 'name="incl"' tmp.tmp >tmp1.tmp
		cat tmp1.tmp| tr " " "\n" >tmp2.tmp
		grep "value" tmp2.tmp >tmp3.tmp
		sed 's/value=//g' tmp3.tmp >tmp4.tmp
		sed 's/"//g' tmp4.tmp >tmp5.tmp
		incl=$(awk -v l=1 'NR==l{ print $1 }' tmp5.tmp)

		grep 'name="e"' tmp.tmp >tmp1.tmp
		cat tmp1.tmp| tr " " "\n" >tmp2.tmp
		grep "value" tmp2.tmp >tmp3.tmp
		sed 's/value=//g' tmp3.tmp >tmp4.tmp
		sed 's/"//g' tmp4.tmp >tmp5.tmp
		exc=$(awk -v l=1 'NR==l{ print $1 }' tmp5.tmp)
	
		grep 'name="a"' tmp.tmp >tmp1.tmp
		cat tmp1.tmp| tr " " "\n" >tmp2.tmp
		grep "value" tmp2.tmp >tmp3.tmp
		sed 's/value=//g' tmp3.tmp >tmp4.tmp
		sed 's/"//g' tmp4.tmp >tmp5.tmp
		dga=$(awk -v l=1 'NR==l{ print $1 }' tmp5.tmp)
	
		grep '<tr><td>absolute\ magnitude</td>' tmp.html >tmp1.tmp
		sed 's/<tr><td>absolute\ magnitude<\/td><td\ class="rj">//g' tmp1.tmp >tmp2.tmp
		sed 's/<\/td><\/tr>//g' tmp2.tmp >tmp3.tmp
		Hmag=$(awk -v l=1 'NR==l{ print $1 }' tmp3.tmp)
	
		grep '<tr><td>phase\ slope</td>' tmp.html >tmp1.tmp
		sed 's/<tr><td>phase\ slope<\/td><td\ class="rj">//g' tmp1.tmp >tmp2.tmp
		sed 's/<\/td><\/tr>//g' tmp2.tmp >tmp3.tmp
		Gslop=$(awk -v l=1 'NR==l{ print $1 }' tmp3.tmp)
		### O R B I T A L   E L E M E N T S ###
		echo "object id: $objid"
		echo "number : $number"
		echo "name : $name"
		echo "designation : $designation $desig1 $desig2 $desig3 $desig4 $desig5"
		echo "epoch : $epoch"
		echo "epoch JD : $epochjd"
		echo "arg.peri. : $peri"
		echo "mean anomaly : $m"
		echo "node : $node"
		echo "incl. : $incl"
		echo "exc : $exc"
		echo "sma : $dga"
		echo "Hmag : $Hmag"
		echo "Gslop : $Gslop"
		echo "1E-15" >mass.tmp
		echo "$objid" >ci.eqm
		echo "$number" >>ci.eqm
		echo "$name" >>ci.eqm
		echo "$epoch" >>ci.eqm
		echo "$epochjd" >>ci.eqm
		echo "$peri" >>ci.eqm
		echo "$m" >>ci.eqm
		echo "$node" >>ci.eqm
		echo "$incl" >>ci.eqm
		echo "$exc" >>ci.eqm
		echo "$dga" >>ci.eqm
		echo "$Hmag" >>ci.eqm
		echo "$Gslop" >>ci.eqm
		./transfciMPC.out
		mv ci.dat ../ci/ci_$aster.dat
#		mv $aster.eqm ../ci/
		rm *.tmp tmp.html
	fi
	echo " "
	cd ../
fi
if [ $obs -eq 1 ]; then
	cd exe/
	if [ $src -eq 0 ]; then	# source : AstDys
		((ind = $aster / 1000 ))
		wget http://hamilton.dm.unipi.it/~astdys2/mpcobs/numbered/$ind/$aster.rwo	
		if [ ! -e $aster.rwo ]; then
			echo "No file in the numbered asteroids in AstDys"
			echo "Try to download from unumbered "
			ind=$(echo ${aster:0:5})
			wget http://hamilton.dm.unipi.it/~astdys2/mpcobs/unumbered/$ind/$aster.rwo
			if [ ! -e $aster.rwo ]; then
				echo "No observation file for $name"
				exit
			fi
		fi
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
	else # source : MPC
		echo " -> Observations file"	
		objidtmp=$(echo "${aster:0:4}_${aster:4:6}")
		wget http://www.minorplanetcenter.net/tmp/$objidtmp.txt
		if [ -e $objidtmp.txt ]; then
			cp $objidtmp.txt obs.mpc 
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
			mv $objidtmp.txt ../obs/$aster.mpc
			rm obs*.* fich*.obs
		fi
	fi
	echo " "
	cd ../
fi

#########################################################################
