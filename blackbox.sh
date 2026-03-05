while true; do
  # 1. Get a list of all APKs in the seeds folder into an array
  shopt -s nullglob
  FILES=(seeds/*)
  
  # 2. Check if the folder is empty
  if [ ${#FILES[@]} -eq 0 ]; then
    echo "No Seeds found in seeds/ folder. Exiting."
    break
  fi

  # 3. Pick a random index and copy that file to F-Droid1.apk
  RANDOM_FILE="${FILES[$((RANDOM % ${#FILES[@]}))]}"
  echo "Testing: $RANDOM_FILE"

  # 4. Run your test
  python3 test.py <TODO-inputs> <TODO-outputs>

  # 5. Check results
  if True; then
    echo "Seeds OK. Keeping into Seeds folder"
  else
    echo "Seeds BROKEN"
  fi
  
  echo ">>>>>>>>>>>>>>>>>>>>"
done
