from kedro.pipeline import node
from .nodes import train_evaluate_model, make_predictions

train_node = node(
    func=train_evaluate_model,
    inputs={
        "X": "x_trainval_encoded",
        "y": "y_trainval",
        "n_splits": "params:n_splits",
        "random_state": "params:random_state"
    },
    outputs=["best_model", "best_score"]
)

prediction_node = node(
    func=make_predictions,
    inputs={
        "model": "best_model",
        "trainval_df": "prediction_model_input_final_parquet",
    },
    outputs="prediction_parquet"
)

