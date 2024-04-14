"""Project pipelines."""
from typing import Dict

from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline

from .pipelines.data_processing import anxious_participants_raw_node, anxious_joined_anxious_node, \
    anxious_impute_drop_node, depressive_participants_raw_node, depressive_joined_anxious_node, \
    depressive_impute_drop_node, control_joined_anxious_node, control_participants_raw_node, control_impute_drop_node, \
    concat_parquet_node, encode_train_node, depressive_features_engineering, control_features_engineering, \
    anxious_features_engineering, prediction_features_engineering, encode_test_node

from .pipelines.data_processing import prediction_participants_raw_node, prediction_joined_anxious_node, prediction_impute_drop_node, prediction_encoded_node

from .pipelines.data_science import train_node, prediction_node, test_evaluate_node


def create_preprocess_pipeline(**kwargs):
    return Pipeline(
        [anxious_participants_raw_node,
         anxious_joined_anxious_node,
         anxious_impute_drop_node,
         anxious_features_engineering,
         depressive_participants_raw_node,
         depressive_joined_anxious_node,
         depressive_impute_drop_node,
         depressive_features_engineering,
         control_participants_raw_node,
         control_joined_anxious_node,
         control_impute_drop_node,
         control_features_engineering,
         concat_parquet_node,
         encode_train_node,
         encode_test_node
         ])


def create_preprocess_prediction_pipeline(**kwargs):
    return Pipeline(
        [
         prediction_participants_raw_node,
         prediction_joined_anxious_node,
         prediction_impute_drop_node,
         prediction_features_engineering,
         prediction_encoded_node
         ]
    )


def create_model_pipeline(**kwargs):
    return Pipeline(
        [train_node]
    )


def create_test_model_pipeline(**kwargs):
    return Pipeline(
        [test_evaluate_node]
    )


def create_model_prediction_pipeline(**kwargs):
    return Pipeline(
        [prediction_node]
    )


def register_pipelines():
    return {
        "training_data_preprocessing": create_preprocess_pipeline(),
        "training_train_model": create_model_pipeline(),
        "training_test_model": create_test_model_pipeline(),
        "prediction_data_preprocessing": create_preprocess_prediction_pipeline(),
        "prediction_predict_result": create_model_prediction_pipeline(),
        # Add any additional pipelines here
    }
