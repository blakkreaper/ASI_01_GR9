import pandas as pd
from autogluon.tabular import TabularPredictor
import wandb
from dask_ml.wrappers import ParallelPostFit
import dask.dataframe as dd


def train_model(train_data: dd.DataFrame, test_data: dd.DataFrame) -> ParallelPostFit:
    train_data: pd.DataFrame = train_data.compute()
    test_data: pd.DataFrame = test_data.compute()

    hyperparameters = {
        'GBM': [
            {'extra_trees': True, 'ag_args': {'name_suffix': 'XT'}},
            {},
            {'extra_trees': True, 'ag_args': {'name_suffix': '1m', 'max_memory_usage_ratio': 1.0}}
        ],
        'CAT': {'iterations': 10000, 'learning_rate': 0.01},
        'XGB': {'booster': 'gbtree', 'verbosity': 1},
    }

    # Inicjalizacja sesji WANDB
    wandb.init(project="depression_prediction", entity="mlody1230")
    label = 'Class'

    # Trenowanie modelu z AutoGluon
    predictor = TabularPredictor(label=label, eval_metric='accuracy').fit(train_data, hyperparameters=hyperparameters,
                                                                          presets='best_quality', time_limit=3600)

    # Ewaluacja modelu
    performance = predictor.evaluate(test_data)

    # Przygotowanie danych do wizualizacji w WANDB
    data_for_plot = [[metric, value] for metric, value in performance.items()]
    table = wandb.Table(data=data_for_plot, columns=["Metric", "Value"])

    # Logowanie wyników do WANDB
    wandb.log({"Evaluation Metrics": table})

    # Logowanie wykresu przy użyciu wandb.plot.bar
    wandb.log({"Metrics Bar Chart": wandb.plot.bar(table, "Metric", "Value", title="Performance Metrics")})

    # Zakończenie sesji WANDB
    wandb.finish()

    return predictor
