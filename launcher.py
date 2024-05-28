import subprocess
import requests
import time
import logging
import threading
import sys

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, filename='launcher.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_PORT = 8001
API_URL = f"http://localhost:{API_PORT}/"


def start_fastapi():
    logger.info("Starting FastAPI server...")
    api_process = subprocess.Popen(["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return api_process


def start_streamlit():
    logger.info("Starting Streamlit application...")
    streamlit_process = subprocess.Popen(["streamlit", "run", "streamlit.py"], stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
    return streamlit_process


def log_process_output(process, name):
    for line in process.stdout:
        logger.info(f"{name}: {line.decode().strip()}")
    for line in process.stderr:
        logger.error(f"{name}: {line.decode().strip()}")


def wait_for_api():
    logger.info("Waiting for API to be available...")
    while True:
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            if response.status_code == 200:
                logger.info("API is running!")
                break
        except requests.RequestException as e:
            logger.error(f"Error while checking API status: {e}")
            time.sleep(1)


def stop_process(process, name):
    if process:
        logger.info(f"Stopping {name}...")
        process.terminate()
        process.wait()


def main():
    api_process = None
    streamlit_process = None

    try:
        # Uruchom FastAPI
        api_process = start_fastapi()

        # Uruchom wątek do logowania wyjścia FastAPI
        threading.Thread(target=log_process_output, args=(api_process, "FastAPI")).start()

        # Czekaj na dostępność API
        wait_for_api()

        # Uruchom Streamlit
        streamlit_process = start_streamlit()

        # Uruchom wątek do logowania wyjścia Streamlit
        threading.Thread(target=log_process_output, args=(streamlit_process, "Streamlit")).start()

        # Poczekaj na zakończenie Streamlit
        streamlit_process.wait()

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        # Zakończ oba procesy
        stop_process(api_process, "FastAPI")
        stop_process(streamlit_process, "Streamlit")


if __name__ == "__main__":
    main()
