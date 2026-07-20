#!/usr/bin/env python3
import sys
import json
import time
import subprocess

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
            
        payload = line.strip()
        if not payload:
            continue
            
        start_time = time.perf_counter()
        
        try:
            res = subprocess.run(
                ["./native_harness", payload],
                capture_output=True,
                text=True,
                timeout=5.0  
            )
            
            runtime = time.perf_counter() - start_time
            
            telemetry = {
                "status": "success" if res.returncode == 0 else "crash",
                "return_code": res.returncode,
                "runtime_sec": runtime,
                "output": res.stdout.strip() if res.returncode == 0 else res.stderr.strip()
            }
        except subprocess.TimeoutExpired:
            telemetry = {
                "status": "hang",
                "return_code": -1,
                "runtime_sec": 5.0,
                "output": "TIMEOUT"
            }
            
        print(json.dumps(telemetry), flush=True)

if __name__ == "__main__":
    main()
