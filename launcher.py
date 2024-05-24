import subprocess
import requests 
import time

# Uruchom api
subprocess.Popen(["python", "app.py"])

# Uruchom streamlit
while True:
    try:
        response = requests.get("http://localhost:8001/")
        response.raise_for_status()
        if response.status_code == 200:
            break
    except requests.RequestException:
        pass
    time.sleep(1)
 
print("API is running!")

subprocess.run(["streamlit", "run", "streamlit.py"])