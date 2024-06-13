import subprocess
import threading
import signal
import sys
import time
import requests

# Function to run FastAPI
def run_fastapi():
    process = subprocess.Popen(["uvicorn", "app:app", "--reload"])
    return process

# Function to run Streamlit
def run_streamlit():
    process = subprocess.Popen(["streamlit", "run", "streamlit.py"])
    return process

# Function to check if FastAPI is running
def check_fastapi_running(url, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.ConnectionError:
            pass
        time.sleep(1)
    return False

# Function to handle termination signals
def signal_handler(sig, frame):
    print("Terminating processes...")
    if fastapi_process:
        fastapi_process.terminate()
    if streamlit_process:
        streamlit_process.terminate()
    sys.exit(0)

if __name__ == "__main__":
    # Set up signal handler for graceful termination
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start FastAPI in a separate thread
    fastapi_process = run_fastapi()

    # Check if FastAPI is running
    fastapi_url = "http://127.0.0.1:8000/docs"
    if check_fastapi_running(fastapi_url):
        print("FastAPI is running. Starting Streamlit...")
        streamlit_process = run_streamlit()
    else:
        print("Failed to start FastAPI within the timeout period.")
        fastapi_process.terminate()
        sys.exit(1)

    # Wait for processes to finish (or be terminated)
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            signal_handler(signal.SIGINT, None)
