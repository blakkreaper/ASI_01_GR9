import subprocess
import requests
import time
import logging
import sys

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, filename='launcher.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_PORT = 8001
API_URL = f"http://localhost:{API_PORT}/"


def start_fastapi():
    logger.info("Starting FastAPI server...")
    api_process = subprocess.Popen(["python", "app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in api_process.stdout:
        logger.info(line.decode().strip())
    for line in api_process.stderr:
        logger.error(line.decode().strip())
    return api_process


def start_streamlit():
    logger.info("Starting Streamlit application...")
    streamlit_process = subprocess.Popen(["streamlit", "run", "streamlit.py"], stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
    for line in streamlit_process.stdout:
        logger.info(line.decode().strip())
    for line in streamlit_process.stderr:
        logger.error(line.decode().strip())
    return streamlit_process


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
        # Uruchom FastAPI w osobnym wątku
        api_process = start_fastapi()

        # Czekaj na dostępność API
        wait_for_api()

        # Uruchom Streamlit
        streamlit_process = start_streamlit()

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
