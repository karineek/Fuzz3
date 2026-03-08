#WBL 8 March 2026  

#Modifications:
#WBL 8 Mar 2026 use local copy of ~/gp/info_lgp/entropy.awk

echo $0 '$Revision: 1.2 $' `date`

gcc -o time_me execution-time-of-c-program.c
if($status) exit $status;

rm -f /tmp/time_me.out
cp /dev/null /tmp/time_me.out
if($status) exit $status;

set i=1
while ( $i <= 10 )
  time_me >> /tmp/time_me.out
  if($status) exit $status;
  set i=(`expr $i + 1`)
end #while

echo -n "Input entropy = 0, output entropy = "
gawk -f entropy.awk -v ncol1=0 /tmp/time_me.out | head -1
#gawk -f ~/oops/mutual_information/entropy.awk -v ncol1=0 /tmp/time_me.out
if($status) exit $status;

echo "$0 done $i" `date`
