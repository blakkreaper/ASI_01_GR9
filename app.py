import io
import os
import shutil
import json
from typing import Hashable, Any, Dict
import wandb
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from kedro.framework.session import KedroSession
from kedro.framework.startup import bootstrap_project
from pydantic import BaseModel
from pathlib import Path

app = FastAPI()

project_path = Path.cwd()
bootstrap_project(project_path)

# ------------------------------------------------------------------
@app.post("/upload_training_data")
async def upload_training_data(file: UploadFile = File(...)):
    try:
        # Directory where training files will be saved
        upload_directory: str = "data/01_raw/training/"

        # Create directory if it doesn't exist
        os.makedirs(upload_directory, exist_ok=True)

        file_path = os.path.join(upload_directory, file.filename)

        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------------------------------
@app.post("/upload_prediction_data")
async def upload_prediction_data(file: UploadFile = File(...)):
    try:
        # Directory where prediction files will be saved
        file_path: str = "data/01_raw/prediction/patients_raw.csv"

        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------------------------------

@app.get("/get_pipelines")
async def get_pipelines():
    try:
        from src.asi_01_gr9.pipeline_registry import register_pipelines
        pipelines = register_pipelines()
        return list(pipelines.keys())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------------------------------
@app.post("/run_pipeline")
async def run_pipeline(pipeline_data: dict):
    try:
        pipeline_name = pipeline_data.get("pipeline_name")
        if not pipeline_name:
            raise HTTPException(status_code=400, detail="Pipeline name not provided")

        with KedroSession.create(project_path=project_path) as session:
            result = session.run(pipeline_name=pipeline_name)
        
        return {"status": "Pipeline executed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------------------------------

@app.post("/run_training")
async def run_training():
    try:
        # Wylogowanie z obecnej sesji wandb, jeśli użytkownik jest zalogowany
        if wandb.run:
            print("Logging out of current wandb session")
            wandb.finish()

        # Inicjalizacja nowej sesji wandb
        print("Initializing wandb")
        wandb.login(key = "09b772345b60d5ad099e94c30941f58858e2b835")  # Upewnij się, że klucz API jest poprawnie skonfigurowany lub podaj go tutaj
        wandb.init(project="depression_prediction", entity="s16943")
        print("wandb initialized")
        run_id = wandb.run.id

        # Uruchomienie sesji Kedro
        with KedroSession.create(project_path=project_path) as session:
            result = session.run(pipeline_name="training_train_model")

        # Zakończenie sesji wandb
        wandb.finish()
        wandb_url = f"https://wandb.ai/s16943/depression_prediction/runs/{run_id}"

        return {"status": "Pipeline executed", "result": result, "wandb_url": wandb_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------------------------------

@app.post("/run_preprocessing")
async def run_preprocessing():
    try:
        with KedroSession.create(project_path=project_path) as session:
            result = session.run(pipeline_name="training_data_preprocessing")
        
        return {"status": "Pipeline executed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------------------------------
# @app.post("/run_prediction")
# async def run_prediction():
#     try:
#         with KedroSession.create(project_path=project_path) as session:
#             result = session.run(pipeline_name="prediction_pipeline")
#
#         return {"status": "Pipeline executed", "result": result}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

 # ------------------------------------------------------------------
    @app.post("/upload_and_run_pipeline")
    async def upload_and_run_pipeline(file: UploadFile = File(...)):

        try:
            # Directory where CSV files will be saved
            upload_directory: str = "data/01_raw/prediction/"

            # Create directory if it doesn't exist
            os.makedirs(upload_directory, exist_ok=True)

            file_path = os.path.join(upload_directory, "patients_raw.csv")

            # Save the uploaded file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Run the Kedro pipeline
            with KedroSession.create(project_path=project_path) as session:
                result = session.run(pipeline_name='predict_data')
                context = session.load_context()
                catalog = context.catalog
                result_is_scam: pd.DataFrame = catalog.load("p_result")

            # Convert the DataFrame to CSV
            csv_buffer = io.StringIO()
            result_is_scam.to_csv(csv_buffer, index=False, sep='~')
            csv_buffer.seek(0)

            # Create a StreamingResponse with the CSV file
            response = StreamingResponse(
                iter([csv_buffer.getvalue()]),
                media_type="text/csv"
            )
            response.headers["Content-Disposition"] = "attachment; filename=result_is_scam.csv"

            return response

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------------------------------
@app.post("/upload_hyperparameters_and_run_pipeline")
async def upload_hyperparameters_and_run_pipeline(hyperparams_file: UploadFile = File(...)):
    """
    Endpoint to upload a CSV file with hyperparameters and run the Kedro pipeline.

    This endpoint accepts a CSV file with hyperparameters, saves it to the predefined directory,
    and then runs a specified Kedro pipeline using these hyperparameters. The result of the pipeline
    execution is returned as a CSV file.

    Args:
        hyperparams_file (UploadFile): The uploaded CSV file with hyperparameters.

    Returns:
        dict: A dictionary containing the status, result, and the filename of the uploaded file.

    Raises:
        HTTPException: If any error occurs during the process, an HTTPException is raised with
        status code 500.
    """
    try:
        # Directory where CSV files will be saved
        upload_directory: str = "data/02_intermediate/"

        # Create directory if it doesn't exist
        os.makedirs(upload_directory, exist_ok=True)

        hyperparams_path = os.path.join(upload_directory, "hyperparameters.csv")

        # Save the uploaded file
        with open(hyperparams_path, "wb") as buffer:
            shutil.copyfileobj(hyperparams_file.file, buffer)

        # Run the Kedro pipeline with hyperparameters
        with KedroSession.create(project_path=project_path) as session:
            result = session.run(pipeline_name='training_train_model')
            context = session.load_context()
            catalog = context.catalog
            result_is_scam: pd.DataFrame = catalog.load("p_result")

            # Convert the DataFrame to CSV
            csv_buffer = io.StringIO()
            result_is_scam.to_csv(csv_buffer, index=False, sep='~')
            csv_buffer.seek(0)

            # Create a StreamingResponse with the CSV file
            response = StreamingResponse(
                iter(csv_buffer),
                media_type="text/csv"
            )
            response.headers["Content-Disposition"] = "attachment; filename=result_is_scam.csv"

        return {"status": "Pipeline executed with hyperparameters", "result": result, "filename": hyperparams_file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------------------------------
class Hyperparameters(BaseModel):
    XGB: dict = {}
    GBM: dict = {}
    RF: dict = {}
    KNN: dict = {}
    CAT: dict = {}

# ------------------------------------------------------------------
default_hyperparameters = {
        'XGB': {'booster': 'gbtree', 'verbosity': 1},
        'GBM': {'extra_trees': True},
        'RF': {'n_estimators': 100, 'max_depth': 10},
        'KNN': {'weights': 'uniform', 'n_neighbors': 5},
        'CAT': {'iterations': 10000, 'learning_rate': 0.01}
    }

# ------------------------------------------------------------------
@app.post("/upload_hyperparameters")
async def upload_hyperparameters(hyperparams: Hyperparameters):
    try:
        # Directory where hyperparameters will be saved
        save_directory = "data/05_model_input/"
        os.makedirs(save_directory, exist_ok=True)
        hyperparams_path = os.path.join(save_directory, "hyperparameters.json")

        # Load existing hyperparameters if file exists
        if os.path.exists(hyperparams_path):
            with open(hyperparams_path, "r") as f:
                existing_hyperparams = json.load(f)
                print(existing_hyperparams)
            for model in default_hyperparameters:
                if model in existing_hyperparams:
                    default_hyperparameters[model].update(existing_hyperparams[model])

        # Merge provided hyperparameters with default hyperparameters
        updated_hyperparams = default_hyperparameters.copy()
        provided_hyperparams = hyperparams.dict()
        for model, params in provided_hyperparams.items():
            if params is not None:  # Ensure that params is not None
                for param, value in params.items():
                    if value is not None:
                        updated_hyperparams[model][param] = value

        # Save the updated hyperparameters to a file
        with open(hyperparams_path, "w") as f:
            json.dump(updated_hyperparams, f, indent=4)

        return {"status": "Hyperparameters saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

