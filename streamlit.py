import streamlit as st
import os
import requests

API_URL = "http://127.0.0.1:8000"  # Zaktualizuj URL API, jeśli jest inny

# Global dictionary to store hyperparameters
stored_hyperparameters = {}

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
                    else:
                        st.success(f"Successfully uploaded file {file}")

def main():
    st.title("Data Upload and Model Operation")

    # Section to upload and configure hyperparameters
    option = st.selectbox(
        "Choose an algorithm",
        ("", "GBM", "RF", "KNN", "CAT", "XGB"),
        index=0
    )

    if option:
        st.header(f"Configure hyperparameters for {option}")

        form = st.form(key=f"{option}_form")

        if option == "GBM":
            extra_trees = form.checkbox("Extra Trees", value=True)
            hyperparameters = {'GBM': {'extra_trees': extra_trees}}
        elif option == "RF":
            n_estimators = form.number_input("Number of Estimators", value=100, step=1)
            max_depth = form.number_input("Max Depth", value=10, step=1)
            hyperparameters = {'RF': {'n_estimators': n_estimators, 'max_depth': max_depth}}
        elif option == "KNN":
            weights = form.selectbox("Weights", options=['uniform', 'distance'])
            n_neighbors = form.number_input("Number of Neighbors", value=5, step=1)
            hyperparameters = {'KNN': {'weights': weights, 'n_neighbors': n_neighbors}}
        elif option == "CAT":
            iterations = form.number_input("Iterations", value=10000, step=1)
            learning_rate = form.number_input("Learning Rate", value=0.01, step=0.001, format="%.3f")
            hyperparameters = {'CAT': {'iterations': iterations, 'learning_rate': learning_rate}}
        elif option == "XGB":
            booster = form.selectbox("Booster", options=['gbtree', 'gblinear', 'dart'])
            verbosity = form.number_input("Verbosity", value=1, step=1)
            hyperparameters = {'XGB': {'booster': booster, 'verbosity': verbosity}}

        submit_button = form.form_submit_button(label="Save hyperparameters")

        if submit_button:
            stored_hyperparameters.update(hyperparameters)
            st.success(f"Hyperparameters for {option} saved successfully!")
            st.json(stored_hyperparameters)
            response = requests.post(f"{API_URL}/upload_hyperparameters", json=stored_hyperparameters)
            if response.status_code == 200:
                st.success("Hyperparameters saved!")
                st.json(response.json())
            else:
                st.error("Hyperparameters couldn't be saved!")
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
