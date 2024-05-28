import streamlit as st
import requests

API_URL = "http://localhost:8001"  # URL API

st.title('Machine Learning Pipeline App')

# Funkcja do wykonywania żądań
def make_request(endpoint, success_message, error_message, params=None):
    try:
        response = requests.post(f"{API_URL}/{endpoint}", json=params)
        if response.status_code == 200:
            st.success(success_message)
            return response.json()
        else:
            st.error(f"{error_message}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"ConnectionError: {e}")
        return None

# Sekcja ładowania danych
st.header("1. Load New Data")
st.write("Enter the paths to files or directories (separated by commas):")

data_paths = st.text_area("", placeholder="e.g., C:/path/to/file1.txt, C:/path/to/directory/")

if st.button('Load New Data'):
    if data_paths:
        st.session_state['data_paths'] = data_paths
        st.success("Data paths successfully saved!")
    else:
        st.warning('Please enter at least one path to a file or directory.')

# Sekcja wyboru pipeline'u i uruchamiania
st.header("2. Run Pipeline")
pipeline_choice = st.selectbox('Choose a pipeline:',
                               options=['training_data_preprocessing', 'training_train_model'])

if st.button('Run Selected Pipeline'):
    if 'data_paths' in st.session_state:
        params = {'pipeline_name': pipeline_choice, 'data_paths': st.session_state['data_paths']}
        pipeline_response = make_request('run_pipeline', 'Pipeline ran successfully!', 'Failed to run pipeline.', params=params)
        if pipeline_response is not None:
            st.write(pipeline_response)
    else:
        st.warning('Please load data first using the "Load New Data" button.')

# Sekcja predykcji i wyświetlania statystyk modelu
st.header("3. Predict and Show Model Statistics")
plikcsv = st.text_input('Enter the path to the CSV file for prediction:')

if st.button('Predict and Show Model Statistics'):
    if plikcsv:
        params = {'plikcsv': plikcsv}
        prediction_response = make_request('predict', 'Prediction completed successfully!', 'Failed to perform prediction.', params=params)
        if prediction_response is not None:
            st.write(prediction_response)
    else:
        st.warning('Please enter the path to the CSV file.')

# Dodanie stópki z informacją o aplikacji
st.markdown("---")
st.markdown("Developed by Your Name. This application uses Kedro, FastAPI, and Streamlit for data processing and model management.")
