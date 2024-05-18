from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from kedro.framework.session import KedroSession
from kedro.framework.startup import bootstrap_project
import wandb

app = FastAPI()


class PipelineRequest(BaseModel):
    pipeline_name: str


project_path = "D:/PROJEKTY/Python/ASI/ASI_01/asi-01-gr9"
bootstrap_project(project_path)


@app.post("/run_pipeline")
async def run_pipeline(request: PipelineRequest):
    pipeline_name = request.pipeline_name
    try:
        with KedroSession.create(project_path=project_path) as session:
            # Start a new wandb run
            wandb_run = wandb.init(project="depression_prediction", reinit=True)

            # Run the Kedro pipeline
            result = session.run(pipeline_name=pipeline_name)

            # Finish the wandb run
            wandb.finish()

            # Get the wandb run URL
            wandb_url = wandb_run.url

            return {"status": "Pipeline executed", "result": result, "wandb_url": wandb_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
