"""Project pipelines."""
from asi_01_gr9.pipelines.data_processing.pipeline import create_preprocess_pipeline
from asi_01_gr9.pipelines.data_science.pipeline import create_train_pipeline


def register_pipelines():
    return {
        "training_data_preprocessing": create_preprocess_pipeline(),
        "training_train_model": create_train_pipeline(),
        # Add any additional pipelines here
    }
