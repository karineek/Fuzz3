#WBL Fuzz3 PYTHON olc decode 4 April 2026
#based on KEM command line 5 April 2026 Ms. Teams chat
#run on ushort's /tmp/ disk

#Modifications:
#WBL 29 Apr 2026 clear tmp's OLC/in out_olc_d crashes_olc_d out_olc_d_end
#WBL  6 Apr 2026 Karine Even-Mendoza yesterday 22:52 my new seeds + her cmdline
#  more mutators and olc_decoder_generator_semi_legal, only seedsno=20
#  update with KEM's new executors.py generators.py blackbox.py
#  Note bug in olc_seeds_decode_finecluster.zip 1st seed is broken
#WBL  5 Apr 2026 Karine Even-Mendoza 12:27 added new generators.py REMOVE EPSILON_SIZE
#WBL  5 Apr 2026 Karine wants -r 1 added
#WBL  4 Apr 2026 based on fuzz_olc_encode.bat r1.2
#  Extend olc_decoder_generator with: gunzip -c latlngolc.out.gz | gawk -f 1000.bat
  
#Inputs:
# $1 iterations and $2 ENTROPY_WINDOW_SIZE

if(!(-e blackbox.py)) then
  echo "blackbox.py missing"
  echo "start $0 from at apex of Fuzz3 directory tree"
  exit 1
endif

setenv iterations 400
if($1) setenv iterations $1
setenv ENTROPY_WINDOW_SIZE 1024
if($2) setenv ENTROPY_WINDOW_SIZE $2
#setenv EPSILON_SIZE -0.01 #disable Entropy in is near entropy out

echo $0 '$Revision: 1.11 $' "iterations=$iterations ENTROPY_WINDOW_SIZE=$ENTROPY_WINDOW_SIZE" `date` $HOST

#make sure to use recent python3
setenv PATH /opt/Python/Python-3.11.5/bin:"$PATH"

#record all versions esp glibc version used for system timing
gcc --version
ldd --version
python3 --version
pip show openlocationcode
if($status) exit $status

mkdir -p /tmp/fuzz3/olc_decoder
if($status) exit $status

rsync -av \
  --exclude="seed*.txt" \
  --exclude="crashes*" \
  --exclude="out*" \
  --exclude="fuzz3_177*" \
   * /tmp/fuzz3/olc_decoder/

cd /tmp/fuzz3/olc_decoder
if($status) exit $status

rm -rf /tmp/fuzz3/olc_decoder/OLC/in
rm -rf /tmp/fuzz3/olc_decoder/OLC/out_olc_d
rm -rf /tmp/fuzz3/olc_decoder/OLC/crashes_olc_d
rm -rf /tmp/fuzz3/olc_decoder/OLC/out_olc_d_end

if(-e OLC/in) then
  echo "OLC/in exists stoping"
  exit 1;
endif
if(-e OLC/out_olc_d) then
  echo "OLC/out_olc_d exists stoping"
  exit 1;
endif
if(-e OLC/crashes_olc_d) then
  echo "OLC/crashes_olc_d exists stoping"
  exit 1;
endif
if(-e OLC/out_olc_d_end) then
  echo "OLC/out_olc_d_end exists stoping"
  exit 1;
endif

ls -l blackbox.py
if($status) exit $status

ls -l Fuzz3/generators.py
if($status) exit $status

ls -l Fuzz3/executors.py
if($status) exit $status

ls -l Fuzz3/observers.py
if($status) exit $status

ls -l Fuzz3/mutators.py
if($status) exit $status

setenv save_dir `pwd`
mkdir -p OLC/in
cd OLC/in
if($status) exit $status
unzip ~/ssbse2026/olc/olc_seeds_decode_finecluster.zip|& grep -v " seed.....txt"
if($status) exit $status
cd $save_dir
if($status) exit $status

echo "ls OLC/in"
ls OLC/in |wc
if($status) exit $status

python3 blackbox.py	\
  -i OLC/in	\
  -o OLC/out_olc_d	\
  -c OLC/crashes_olc_d	\
  --executor olc_decode_executor	\
  --mutators	\
    bit_flip	\
    delete_char	\
    duplicate_char	\
    add_one_mixed_tokens	\
  --generators	\
    olc_decoder_generator_legal	\
    olc_decoder_generator_illegal	\
    olc_decoder_generator_semi_legal	\
  --observers entropy_sliding_window_observer	\
  --oracles entropy_oracle	\
  --seedsno 20	\
  --iterations $iterations

setenv save $status

echo -n "OLC/in            "
ls OLC/in                 |wc
echo -n "OLC/out_olc_d     "
ls OLC/out_olc_d          |wc
echo -n "OLC/crashes_olc_d "
ls OLC/crashes_olc_d      |wc
echo -n "OLC/out_olc_d_end "
ls OLC/out_olc_d_end      |wc

echo "$0 done, status $save" `date`
exit $save
