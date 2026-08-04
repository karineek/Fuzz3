echo ">> Start installation of Fuzz3..."
python -m pip install -e external/Fuzz3
rc=`echo $?`
echo ">> Done installing Fuzz3 (rc=$rc)"
