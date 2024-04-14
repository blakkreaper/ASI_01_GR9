from kedro.pipeline import node
from .nodes import train_evaluate_model, make_predictions, evaluate_model_on_test_data

train_node = node(
    func=train_evaluate_model,
    inputs={
        "x_train": "x_trainval_encoded",
        "y_train": "y_trainval",
        "n_splits": "params:n_splits",
        "random_state": "params:random_state"
    },
    outputs="best_model"
)

test_evaluate_node = node(
    func=evaluate_model_on_test_data,
    inputs={
        "model": "best_model",
        "x_test": "x_test_encoded",
        "y_test": "y_test",
    },
    outputs=None
)

prediction_node = node(
    func=make_predictions,
    inputs={
        "model": "best_model",
        "trainval_df": "prediction_model_input_final_parquet",
    },
    outputs="prediction_parquet"
)

