"""Project pipelines."""
from typing import Dict

from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline

from .pipelines.data_processing import anxious_participants_raw_node, anxious_joined_anxious_node, \
    anxious_impute_drop_node, depressive_participants_raw_node, depressive_joined_anxious_node, \
    depressive_impute_drop_node, control_joined_anxious_node, control_participants_raw_node, control_impute_drop_node, \
    concat_parquet_node, encode_node

from .pipelines.data_processing import prediction_participants_raw_node, prediction_joined_anxious_node, prediction_impute_drop_node, prediction_encoded_node

from .pipelines.data_science import train_node, prediction_node


def create_preprocess_pipeline(**kwargs):
    return Pipeline(
        [anxious_participants_raw_node,
         anxious_joined_anxious_node,
         anxious_impute_drop_node,
         depressive_participants_raw_node,
         depressive_joined_anxious_node,
         depressive_impute_drop_node,
         control_participants_raw_node,
         control_joined_anxious_node,
         control_impute_drop_node,
         concat_parquet_node,
         encode_node
         ])


def create_preprocess_prediction_pipeline(**kwargs):
    return Pipeline(
        [
         prediction_participants_raw_node,
         prediction_joined_anxious_node,
         prediction_impute_drop_node,
         prediction_encoded_node
         ]
    )


def create_model_pipeline(**kwargs):
    return Pipeline(
        [train_node]
    )


def create_model_prediction_pipeline(**kwargs):
    return Pipeline(
        [prediction_node]
    )


def register_pipelines():
    return {
        "__default__": create_preprocess_pipeline(),
        "training_pipeline": create_model_pipeline(),
        "prediction_processing": create_preprocess_prediction_pipeline(),
        "prediction_prediciton": create_model_prediction_pipeline()
        # Add any additional pipelines here
    }
