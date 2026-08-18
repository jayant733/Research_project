import os
import subprocess
import sys
import time


def main():
    print("=== RATC End-to-End Federated Training ===")
    
    # 1. Generate Dataset
    print("\n[1/4] Generating Healthcare Dataset...")
    subprocess.run([sys.executable, "datasets/generate_healthcare_dataset.py", "--clients", "3"], check=True)
    
    # 2. Start Scheduler (Background)
    # Normally we'd start telemetry & scheduler. For this simplified script,
    # we just run the server and clients since telemetry/scheduler are mock-bound in client args.
    
    # 3. Start Server
    print("\n[2/4] Starting FL Server...")
    server_proc = subprocess.Popen([sys.executable, "-m", "apps.server.main"])
    time.sleep(3) # Wait for server to bind
    
    # 4. Start Clients
    print("\n[3/4] Starting FL Clients...")
    client_procs = []
    
    profiles = ["iot_device", "mobile", "workstation"]
    tiers = ["TIER_3_DP_PLAIN", "TIER_2_SECAGG", "TIER_3_DP_PLAIN"] # Mixing it up
    
    for i in range(3):
        print(f"  -> Launching Client {i} ({profiles[i]}, {tiers[i]})")
        proc = subprocess.Popen([
            sys.executable, "-m", "apps.client.main",
            "--client-id", f"client_{i}",
            "--profile", profiles[i],
            "--tier", tiers[i],
            "--data", f"data/healthcare/client_{i}.pt"
        ])
        client_procs.append(proc)
        
    print("\n[4/4] Training in progress. Waiting for completion...")
    
    for proc in client_procs:
        proc.wait()
        
    server_proc.wait()
    
    print("\n=== Federated Training Complete ===")

if __name__ == "__main__":
    main()
