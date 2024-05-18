from kedro.framework.session import KedroSession


def run_data_science_pipeline():
    project_name = "asi_01_gr9"
    project_path = "./src"
    with KedroSession.create(project_name, project_path) as session:
        context = session.load_context()
        session.run(pipeline_name="api_train_model")
