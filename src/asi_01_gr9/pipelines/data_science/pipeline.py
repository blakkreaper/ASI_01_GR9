from kedro.pipeline import Pipeline, node

from asi_01_gr9.pipelines.data_science import train_model_and_evaluate
from asi_01_gr9.pipelines.data_science.nodes import predict_data


def create_train_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                func=train_model_and_evaluate,
                inputs={
                    "train_data": "train_data",
                    "test_data": "test_data",
                    "hyperparameters": "hyperparameters",
                },
                outputs="best_model"
            ),
         ]
    )


def create_prediction_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                func=predict_data,
                inputs={
                    "predictor": "best_model",
                    "data": "prediction_feature_engineering_parquet",
                },
                outputs="p_result"
            ),
         ]
    )