"""Project pipelines."""

from kedro.pipeline import Pipeline

from .pipelines.data_processing import anxious_participants_raw_node, anxious_joined_anxious_node, \
    anxious_impute_drop_node, depressive_participants_raw_node, depressive_joined_anxious_node, \
    depressive_impute_drop_node, control_joined_anxious_node, control_participants_raw_node, control_impute_drop_node, \
    concat_parquet_node, depressive_features_engineering, control_features_engineering, \
    anxious_features_engineering
from .pipelines.data_science import train_node


def create_preprocess_pipeline(**kwargs) -> Pipeline:
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
         ])


def create_train_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [train_node
         ])


def register_pipelines():
    return {
        "training_data_preprocessing": create_preprocess_pipeline(),
        "training_train_model": create_train_pipeline()
        # Add any additional pipelines here
    }
