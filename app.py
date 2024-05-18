import os
import pandas as pd
from pathlib import Path
from kedro.framework.startup import bootstrap_project
from kedro.framework.session import KedroSession
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

project_path = Path.cwd()
metadata = bootstrap_project(project_path)
session = KedroSession.create(metadata.package_name, project_path)
context = session.load_context()

app = FastAPI(
    title="FastAPI",
    version="0.1.0",
    description="""
        ChimichangApp API helps you do awesome stuff. 🚀
## Items
You can **read items**.
## Users
You will be able to:
* **Create users** (_not implemented_). * **Read users** (_not implemented_).

    """,
    openapi_tags=[{'name': 'users', 'description': 'Operations with users. The **login** logic is also here.'}, {'name': 'items', 'description': 'Manage items. So _fancy_ they have their own docs.'}]
)


@app.get('/')
async def docs_redirect():
    return RedirectResponse(url='/docs')


@app.post("/run_api_train_model_pipeline", tags=["Pipeline"])
def run_api_train_model_pipeline():
    try:
        project_name = metadata.package_name
        project_path = Path.cwd()
        with KedroSession.create(project_name, project_path) as session:
            session.run(pipeline_name="api_train_model")
        return {"message": "Pipeline api_train_model has been successfully run."}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
