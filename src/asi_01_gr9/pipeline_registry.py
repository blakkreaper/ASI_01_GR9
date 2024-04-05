"""Project pipelines."""
from typing import Dict

from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline

from .pipelines.data_processing.nodes import reading_node


def create_pipeline(**kwargs):
    return Pipeline(
        [reading_node]
    )


def register_pipelines():

    return {
        "__default__": create_pipeline(),
        # Add any additional pipelines here
    }
