import subprocess
import time
import sys
import os

# Paths to Python (auto-uses your current one)
PYTHON = sys.executable

def run_command(cmd, background=False):
    if background:
        return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        subprocess.run(cmd, shell=True, check=True)

if __name__ == "__main__":
    print("Launching the whole playground with one command!")
    
    # Step 1: Start SuperLink (teacher/server) in background
    superlink_proc = run_command(f"{PYTHON} -m flower-superlink --insecure", background=True)
    print("SuperLink started—waiting a sec for it to warm up...")
    time.sleep(5)  # Give it time to start
    
    # Step 2: Start SuperNode 1 (first kid/client) in background
    supernode1_proc = run_command(f"{PYTHON} -m flower-supernode --insecure --superlink=127.0.0.1:9092", background=True)
    print("SuperNode 1 joining the game...")
    
    # Step 3: Start SuperNode 2 (second kid/client) in background
    supernode2_proc = run_command(f"{PYTHON} -m flower-supernode --insecure --superlink=127.0.0.1:9092", background=True)
    print("SuperNode 2 joining—learning should start!")
    time.sleep(10)  # Wait for learning round
    
    # Step 4: Start FastAPI (playground doors) in main process
    print("Starting FastAPI—visit http://127.0.0.1:8000/static/index.html!")
    port = os.environ.get("PORT", "8000")
    host = os.environ.get("HOST", "127.0.0.1")
    run_command(f"{PYTHON} -m uvicorn app:app --host {host} --port {port}")
    
    # Cleanup (when you Ctrl+C)
    print("Shutting down...")
    for proc in [superlink_proc, supernode1_proc, supernode2_proc]:
        if proc:
            proc.terminate()
