"""Project pipelines."""
from typing import Dict

from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline

from .pipelines.data_science import split_node, train_node

from .pipelines.data_processing import participants_raw_node, aoi_statistics_node, stimulus_anxious_node, \
    event_statistics_node, \
    joined_anxious_node, impute_drop_node


def create_preprocess_pipeline(**kwargs):
    return Pipeline(
        [participants_raw_node, aoi_statistics_node, event_statistics_node,stimulus_anxious_node, joined_anxious_node, impute_drop_node]
    )


def create_model_pipeline(**kwargs):
    return Pipeline(
        [split_node, train_node]
    )


def register_pipelines():
    return {
        "__default__": create_preprocess_pipeline(),
        "training_pipeline": create_model_pipeline(),
        # Add any additional pipelines here
    }
