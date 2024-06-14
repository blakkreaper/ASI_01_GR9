"""Project pipelines."""
from asi_01_gr9.pipelines.data_processing.pipeline import create_preprocess_pipeline, create_predict_preprocess_pipeline
from asi_01_gr9.pipelines.data_science.pipeline import create_train_pipeline, create_prediction_pipeline


def register_pipelines():
    return {
        "training_data_preprocessing": create_preprocess_pipeline(),
        "training_train_model": create_train_pipeline(),
        "preprocess_and_train": create_preprocess_pipeline() + create_train_pipeline(),
        "predict_data": create_predict_preprocess_pipeline() + create_prediction_pipeline(),
        # Add any additional pipelines here
    }
