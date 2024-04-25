from kedro.pipeline import node
from .nodes import train_model

train_node = node(
    func=train_model,
    inputs={
        "train_data": "train_data",
        "test_data": "test_data",
    },
    outputs="best_model"
)


