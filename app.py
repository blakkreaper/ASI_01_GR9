import io
import os
import shutil
import json
from typing import Hashable, Any, Dict

import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from kedro.framework.session import KedroSession
from kedro.framework.startup import bootstrap_project
from pydantic import BaseModel

app = FastAPI()

project_path: str = ""
bootstrap_project(project_path)

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

@app.post("/upload_prediction_data")
async def upload_prediction_data(file: UploadFile = File(...)):
    try:
        # Directory where prediction files will be saved
        upload_directory: str = "data/01_raw/prediction/"

        # Create directory if it doesn't exist
        os.makedirs(upload_directory, exist_ok=True)

        file_path = os.path.join(upload_directory, file.filename)

        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# @app.post("/upload_file")
# async def upload_file(file: UploadFile = File(...)):
#     try:
#         # Directory where CSV files will be saved
#         upload_directory: str = "data/01_raw/prediction/"

#         # Create directory if it doesn't exist
#         os.makedirs(upload_directory, exist_ok=True)

#         file_path = os.path.join(upload_directory, "patients_raw.csv")

#         # Save the uploaded file
#         with open(file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/run_pipeline")
# async def run_pipeline(str: pipeline):#jak dac string zamiast file

#     try:
#         # Run the Kedro pipeline
#         with KedroSession.create(project_path=project_path) as session:
#             result = session.run(pipeline_name=pipeline)
#             context = session.load_context()
#             catalog = context.catalog
#             result_is_scam: pd.DataFrame = catalog.load("p_result")

#             # Convert the DataFrame to CSV
#             csv_buffer = io.StringIO()
#             result_is_scam.to_csv(csv_buffer, index=False, sep='~')
#             csv_buffer.seek(0)

#             # Create a StreamingResponse with the CSV file
#             response = StreamingResponse(
#                 iter(csv_buffer),
#                 media_type="text/csv"
#             )
#             response.headers["Content-Disposition"] = "attachment; filename=result_is_scam.csv"

#         return {"status": "Pipeline executed", "result": result, "filename": file.filename}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


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


class Hyperparameters(BaseModel):
    GBM: Dict[str, Any] = None
    RF: Dict[str, Any] = None
    KNN: Dict[str, Any] = None
    CAT: Dict[str, Any] = None
    XGB: Dict[str, Any] = None

@app.post("/upload_hyperparameters")
async def upload_hyperparameters(hyperparams: Hyperparameters):
    try:
        # Directory where hyperparameters will be saved
        save_directory = "data/05_model_input/"
        
        # Create directory if it doesn't exist
        os.makedirs(save_directory, exist_ok=True)
        
        hyperparams_path = os.path.join(save_directory, "hyperparameters.json")

        # Save the hyperparameters to a file
        with open(hyperparams_path, "w") as f:
            json.dump(hyperparams.dict(), f, indent=4)

        return {"status": "Hyperparameters saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))