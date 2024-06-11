from kedro.pipeline import Pipeline, node

from asi_01_gr9.pipelines.data_science import train_model_and_evaluate


def create_train_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                func=train_model_and_evaluate,
                inputs={
                    "train_data": "train_data",
                    "test_data": "test_data",
                },
                outputs="best_model"
            ),
         ]
    )