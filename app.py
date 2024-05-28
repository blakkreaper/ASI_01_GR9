from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from kedro.framework.session import KedroSession
from kedro.framework.startup import bootstrap_project
import wandb
from pathlib import Path
import uvicorn
import os
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


class LoadDataRequest(BaseModel):
    data_paths: str


class PipelineRequest(BaseModel):
    pipeline_name: str
    data_paths: str


class PredictRequest(BaseModel):
    plikcsv: str


@app.get("/")
def get_root():
    logger.info("Root endpoint called.")
    return "API is running!"


@app.post("/load_data")
async def load_data(request: LoadDataRequest):
    logger.info(f"Received data paths: {request.data_paths}")
    data_paths = request.data_paths.split(',')
    for path in data_paths:
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if not os.path.isfile(file_path):
                        logger.error(f"File {file_path} does not exist")
                        raise HTTPException(status_code=400, detail=f"File {file_path} does not exist")
                    logger.info(f"Loading data from file: {file_path}")
                    # Zaimplementuj logikę ładowania danych z pliku
        elif os.path.isfile(path):
            logger.info(f"Loading data from file: {path}")
            # Zaimplementuj logikę ładowania danych z pliku
        else:
            logger.error(f"Path {path} is not valid")
            raise HTTPException(status_code=400, detail=f"Path {path} is not valid")
    return {"message": "Data successfully loaded"}


@app.post("/run_pipeline")
async def run_pipeline(request: PipelineRequest):
    logger.info(f"Running pipeline: {request.pipeline_name} with data paths: {request.data_paths}")
    project = Path.cwd()
    bootstrap_project(project)

    data_paths = request.data_paths.split(',')
    # Użyj data_paths do przetwarzania danych w Kedro

    with KedroSession.create(project) as session:
        wandb_run = wandb.init(project="depression_prediction", reinit=True)
        result = session.run(pipeline_name=request.pipeline_name)
        wandb.finish()
        wandb_url = wandb_run.url
        logger.info(f"Pipeline {request.pipeline_name} ran successfully.")
        return {"wandb_url": wandb_url, "message": f"Pipeline {request.pipeline_name} ran successfully"}


@app.post("/predict")
async def predict(request: PredictRequest):
    logger.info(f"Predicting with CSV file: {request.plikcsv}")
    project = Path.cwd()
    bootstrap_project(project)

    plikcsv = request.plikcsv
    if not os.path.isfile(plikcsv):
        logger.error(f"File {plikcsv} does not exist")
        raise HTTPException(status_code=400, detail=f"File {plikcsv} does not exist")

    with KedroSession.create(project) as session:
        wandb_run = wandb.init(project="depression_prediction", reinit=True)
        result = session.run(pipeline_name='predict_model')
        wandb.finish()
        wandb_url = wandb_run.url
        logger.info(f"Prediction completed successfully.")
        return {"wandb_url": wandb_url, "message": "Prediction completed successfully"}


if __name__ == '__main__':
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
