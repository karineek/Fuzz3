#!/usr/bin/env python3
import subprocess
import json
import sys
import time

def test_standalone_worker():
    IMAGE_TAG = "fuzz3-gpu-worker:thrust-cpu"
    
    print(f"[*] Starting container loop for image: {IMAGE_TAG}")
    print("[*] (Running in CPU mode - omitting GPU hardware access flags)")
    
    try:
        container = subprocess.Popen(
            ["docker", "run", "-i", "--rm", IMAGE_TAG],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line buffered
        )
    except FileNotFoundError:
        print("[!] Error: Docker does not appear to be installed or accessible via PATH.")
        sys.exit(1)

    test_cases = [
        "10.5,2.3,99.1,0.05,43.2",
        "500.0,-12.5,0.0,22.4,10.1",
        "42.0"
    ]

    for idx, payload in enumerate(test_cases, start=1):
        print(f"\n--------------------------------------------------")
        print(f"[ Test #{idx} ] Sending Input: '{payload}'")
        
        send_start = time.perf_counter()
        
        try:
            container.stdin.write(payload + "\n")
            container.stdin.flush()
        except Exception as e:
            print(f"[!] Pipe Write Error: {e}")
            break

        response_line = container.stdout.readline().strip()
        total_roundtrip = time.perf_counter() - send_start
        
        if not response_line:
            print("[!] Empty response received. Container may have terminated.")
            break
            
        try:
            metrics = json.loads(response_line)
            print(f"  -> Status : {metrics.get('status')}")
            print(f"  -> Exit Code: {metrics.get('return_code')}")
            print(f"  -> Runtime : {metrics.get('runtime_sec'):.6f} seconds")
            print(f"  -> Roundtrip  : {total_roundtrip:.6f} seconds")
            print(f"  -> Output    : {metrics.get('output')}")
        except json.JSONDecodeError:
            print(f"[!] Failed to decode JSON string: {response_line}")

    print(f"\n--------------------------------------------------")
    print("[*] Tearing down worker container...")
    try:
        container.stdin.close()
        container.terminate()
        container.wait(timeout=2)
        print("[+] Teardown successful.")
    except Exception as e:
        print(f"[-] Teardown cleanup note: {e}")

if __name__ == "__main__":
    test_standalone_worker()
