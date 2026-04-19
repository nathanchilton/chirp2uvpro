import subprocess
import time
import os
import signal
import threading

def monitor_stderr(stderr_file):
    with open(stderr_file, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            print(f"[SERVER STDERR] {line.strip()}")

def run_server():
    env = os.environ.copy()
    env["FLASK_APP"] = "src.app.main:app"
    env["PYTHONPATH"] = os.getcwd()
    
    # Use a new process group so we can kill the whole tree
    process = subprocess.Popen(
        ["./venv/bin/python", "-m", "flask", "run", "--port=5001"],
        env=env,
        stderr=open("server_stderr.log", "w"),
        stdout=subprocess.PIPE,
        text=True,
        preexec_fn=os.setsid
    )
    return process

if __name__ == "__main__":
    server_process = run_server()
    
    # Start monitoring thread
    monitor_thread = threading.Thread(target=monitor_stderr, args=("server_stderr.log",), daemon=True)
    monitor_thread.start()
    
    # Wait for server to start
    time.sleep(5)
    
    # Run the tests
    test_process = subprocess.Popen(["./venv/bin/pytest", "tests/e2e/test_conversion_flow.py"], stdout=subprocess.PIPE, text=True)
    
    # Print pytest output as it comes
    for line in test_process.stdout:
        print(f"[PYTEST] {line.strip()}")
        
    test_process.wait()
    
    # Kill the server and its group
    try:
        os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
    except ProcessLookupError:
        pass
    
    print("Tests finished and server stopped.")
