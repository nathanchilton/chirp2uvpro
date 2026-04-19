import os
import sys
import subprocess

# Add src to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Try to import pandas to see if it's visible
try:
    import pandas
    print("Pandas imported successfully")
except ImportError as e:
    print(f"Pandas import failed: {e}")

# Try to run the reproduction script with PYTHONPATH set
env = os.environ.copy()
env["PYTHONPATH"] = os.path.abspath(os.path.join(os.getcwd(), "src")) + os.pathsep + env.get("PYTHONPATH", "")

print(f"Running reproduction script with PYTHONPATH={env['PYTHONPATH']}")
result = subprocess.run(["./venv/bin/python3", "reproduce_error.py"], env=env, capture_output=True, text=True)
print("STDOUT:")
print(result.stdout)
print("STDERR:")
print(result.stderr)
