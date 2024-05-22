from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from kedro.framework.session import KedroSession
from kedro.framework.startup import bootstrap_project
import wandb
from pathlib import Path

app = FastAPI()


class PipelineRequest(BaseModel):
    pipeline_name: str

@app.get("/")
def get_root():
    return "string"#RedirectResponse()

@app.get("/process_data")
async def process_data():
    project = Path.cwd()
    bootstrap_project(project)
    with KedroSession.create(project) as session:
        # Start a new wandb run
        wandb_run = wandb.init(project="depression_prediction", reinit=True)

        # Run the Kedro pipeline
        result = session.run(pipeline_name='training_data_preprocessing')

        # Finish the wandb run
        wandb.finish()

        # Get the wandb run URL
        wandb_url = wandb_run.url

@app.get("/train_model")
async def train_model():
    project = Path.cwd()
    bootstrap_project(project)
    with KedroSession.create(project) as session:
        # Start a new wandb run
        wandb_run = wandb.init(project="depression_prediction", reinit=True)

        # Run the Kedro pipeline
        result = session.run(pipeline_name='training_train_model')

        # Finish the wandb run
        wandb.finish()

        # Get the wandb run URL
        wandb_url = wandb_run.url
