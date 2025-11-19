"""
Stop a running script after a timeout.

This script waits for a specified time and then stops the target Python process.
"""

import time
import subprocess
import sys
from datetime import datetime, timedelta

def stop_process_after_timeout(timeout_seconds: int, target_script: str):
    """
    Wait for timeout and then stop the target script.

    Args:
        timeout_seconds: Seconds to wait before stopping
        target_script: Part of the script name to find and kill
    """
    end_time = datetime.now() + timedelta(seconds=timeout_seconds)

    print(f"Will stop '{target_script}' at {end_time.strftime('%H:%M:%S')}")
    print(f"Timeout: {timeout_seconds} seconds ({timeout_seconds/3600:.1f} hours)")
    print("This script is running in background...")

    # Wait
    time.sleep(timeout_seconds)

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Timeout reached! Stopping {target_script}...")

    # Find and kill the process on Windows
    # Use taskkill to find Python processes with the script name
    try:
        # List all python processes
        result = subprocess.run(
            ['wmic', 'process', 'where', 'name="python.exe"', 'get', 'processid,commandline'],
            capture_output=True, text=True
        )

        lines = result.stdout.strip().split('\n')
        killed = False

        for line in lines:
            if target_script in line:
                # Extract PID (last number in line)
                parts = line.strip().split()
                if parts:
                    pid = parts[-1]
                    if pid.isdigit():
                        print(f"Found process PID: {pid}")
                        subprocess.run(['taskkill', '/PID', pid, '/F'], check=True)
                        print(f"Process {pid} terminated successfully")
                        killed = True

        if not killed:
            print(f"No process found running {target_script}")

    except Exception as e:
        print(f"Error stopping process: {e}")

if __name__ == "__main__":
    # 3 hours = 10800 seconds
    timeout = 3 * 60 * 60  # 3 hours
    target = "PAPAPIN_dsox4034a_vrms-fast.py"

    stop_process_after_timeout(timeout, target)
