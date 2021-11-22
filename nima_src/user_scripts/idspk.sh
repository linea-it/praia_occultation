read aster
echo "${aster}" | grep -q '[A-Z]'
if [ $? = 0 ]; then
	idspk=-1	    
	
else
	(( idspk= 2000000 + $aster ))
fi
echo "$idspk" 
