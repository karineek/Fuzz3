#WBL 7 March 2026  $Revision: 1.3 $

if(0) then
#echo compile like...
cc -o latlngolc latlngolc.c -lm
if($status) exit $status;

echo "one test should give 8FVC2222+22GCCCC"

latlngolc 47.0000625 8.0000625
if($status) exit $status
endif #0

gunzip -c open_postcode_geo.dat.gz >! /tmp/open_postcode_geo.dat
wc -l /tmp/open_postcode_geo.dat
if($status) exit $status

gawk -v rev='$Revision: 1.3 $' '\
BEGIN{rev=substr(rev,2,length(rev)-3);\
  print "#run_latlngolc.bat",rev,strftime();\
  print "rm -f /tmp/latlngolc.out";\
  print "cp /dev/null /tmp/latlngolc.out";\
  print "echo \"#run_latlngolc.bat\"",rev,"`date` >> /tmp/latlngolc.out";\
}\
(FNR>0){print "latlngolc",$1,$2,">> /tmp/latlngolc.out"}\
END{print "echo \"#run_latlngolc.bat done\" `date` >> /tmp/latlngolc.out"}'\
  /tmp/open_postcode_geo.dat >! /tmp/latlngolc.bat
if($status) exit $status

#exit 99;

chmod +x /tmp/latlngolc.bat
if($status) exit $status

/tmp/latlngolc.bat
if($status) exit $status

echo "$0 done" `date`
