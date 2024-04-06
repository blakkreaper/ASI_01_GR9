from kedro.pipeline import node

from .nodes import split_data, train_model

split_node = node(
            func=split_data,
            inputs=["preprocessed_data", "parameters"],
            outputs="folds",
    )

train_node = node(
            func=train_model,
            inputs=dict(train="folds", test="folds", parameters="parameters"),
            outputs="model_accuracy_scores",
)