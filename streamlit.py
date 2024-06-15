import streamlit as st
import os
import requests
import json

API_URL = "http://127.0.0.1:8000"  # Zaktualizuj URL API, jeśli jest inny

def upload_directory(path, use_for_training):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                with open(file_path, "rb") as f:
                    files = {'file': (file, f, 'text/plain')}
                    endpoint = "/upload_training_data" if use_for_training else "/upload_prediction_data"
                    response = requests.post(f"{API_URL}{endpoint}", files=files)
                    if response.status_code != 200:
                        st.error(f"Error uploading file {file}: {response.text}")

# ------------------------------------------------------------------

def main():
    st.title("Data Upload and Model Operation")

    # Section to upload and configure hyperparameters
    option = st.selectbox(
        "Choose an algorithm",
        ("", "GBM", "RF", "KNN", "CAT", "XGB"),
        index=0
    )
    save_directory = "data/05_model_input/"
    hyperparams_path = os.path.join(save_directory, "hyperparameters.json")
    existing_hyperparams = {}
    if os.path.exists(hyperparams_path):
        with open(hyperparams_path, "r") as f:
            existing_hyperparams = json.load(f)
    
    if option:
        st.header(f"Configure hyperparameters for {option}")

        form = st.form(key=f"{option}_form")

        hyperparameters = {
        'GBM': {'extra_trees': True},
        'RF': {'n_estimators': 100, 'max_depth': 10},
        'KNN': {'weights': 'uniform', 'n_neighbors': 5},
        'CAT': {'iterations': 10000, 'learning_rate': 0.01},
        'XGB': {'booster': 'gbtree', 'verbosity': 1}
        }
        if existing_hyperparams:
            for model in existing_hyperparams:
                hyperparameters[model].update(existing_hyperparams[model])
            
        if option == "GBM":
            extra_trees = form.checkbox("Extra Trees", value=hyperparameters['GBM'].get('extra_trees', True))
            hyperparameters = {'GBM': {'extra_trees': extra_trees}}
        elif option == "RF":
            n_estimators = form.number_input("Number of Estimators", value=hyperparameters['RF'].get('n_estimators', 100), step=1)
            max_depth = form.number_input("Max Depth", value=hyperparameters['RF'].get('max_depth', 10), step=1)
            hyperparameters = {'RF': {'n_estimators': n_estimators, 'max_depth': max_depth}}
        elif option == "KNN":
            weights = form.selectbox("Weights", options=['uniform', 'distance'], index=0 if hyperparameters['KNN'].get('weights') == 'uniform' else 1)
            n_neighbors = form.number_input("Number of Neighbors", value=hyperparameters['KNN'].get('n_neighbors', 5), step=1)
            hyperparameters = {'KNN': {'weights': weights, 'n_neighbors': n_neighbors}}
        elif option == "CAT":
            iterations = form.number_input("Iterations", value=hyperparameters['CAT'].get('iterations', 10000), step=1)
            learning_rate = form.number_input("Learning Rate", value=hyperparameters['CAT'].get('learning_rate', 0.01), step=0.001, format="%.3f")
            hyperparameters = {'CAT': {'iterations': iterations, 'learning_rate': learning_rate}}
        elif option == "XGB":
            booster = form.selectbox("Booster", options=['gbtree', 'gblinear', 'dart'], index=['gbtree', 'gblinear', 'dart'].index(hyperparameters['XGB'].get('booster', 'gbtree')))
            verbosity = form.number_input("Verbosity", value=hyperparameters['XGB'].get('verbosity', 1), step=1)
            hyperparameters = {'XGB': {'booster': booster, 'verbosity': verbosity}}

        submit_button = form.form_submit_button(label="Save hyperparameters")
        if submit_button:
            # Ensure hyperparameters is not None
            if hyperparameters:
                response = requests.post(f"{API_URL}/upload_hyperparameters", json=hyperparameters)
                if response.status_code == 200:
                    st.success("Hyperparameters saved!")
                else:
                    st.error("Hyperparameters couldn't be saved!")
                    st.json(response.json())
            else:
                st.error("No hyperparameters to save!")

    # Section to select and run pipeline
    st.header("Run Pipeline")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Run training_data_preprocessing"):
            response = requests.post(f"{API_URL}/run_preprocessing")
            if response.status_code == 200:
                st.success("Pipeline training_data_preprocessing executed successfully!")
            else:
                st.error("Pipeline training_data_preprocessing execution failed!")
                st.json(response.json())
    
    with col2:
        if st.button("Run training_train_model"):
            response = requests.post(f"{API_URL}/run_training")
            if response.status_code == 200:
                st.success("Pipeline training_train_model executed successfully!")
                wandb_url = response.json().get("wandb_url")
                if wandb_url:
                    st.markdown(f"[View training logs in WandB]({wandb_url})")
            else:
                st.error("Pipeline training_train_model execution failed!")
                st.json(response.json())

    with col3:
        if st.button("Run prediction_pipeline"):
            response = requests.post(f"{API_URL}/upload_and_run_pipeline")
            if response.status_code == 200:
                st.success("Pipeline prediction_pipeline executed successfully!")
            else:
                st.error("Pipeline prediction_pipeline execution failed!")
                st.json(response.json())

    # Section to upload data and choose usage
    st.header("Upload Data for Training or Prediction")
    data_path = st.text_input("Directory Path", help="Path to the directory containing subdirectories with .txt files")
    use_for_training = st.radio("Use data for", ("Training", "Prediction"))

    if st.button("Upload Data"):
        if data_path and os.path.isdir(data_path):
            upload_directory(data_path, use_for_training == "Training")
        else:
            st.error("Invalid directory path")

if __name__ == "__main__":
    main()
