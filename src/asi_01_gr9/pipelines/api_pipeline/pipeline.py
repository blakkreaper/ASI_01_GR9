from kedro.pipeline import Pipeline, node

from asi_01_gr9.pipelines.api_pipeline.nodes import run_data_science_pipeline


def create_api_train_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [node(func=run_data_science_pipeline,
              inputs=None,
              outputs=None)
         ]
    )
