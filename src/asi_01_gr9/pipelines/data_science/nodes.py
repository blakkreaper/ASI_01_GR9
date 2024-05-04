import numpy as np
import pandas as pd
from autogluon.tabular import TabularPredictor
import wandb
from dask_ml.wrappers import ParallelPostFit
import dask.dataframe as dd
from sklearn.metrics import roc_curve


def train_model(train_data: dd.DataFrame, test_data: dd.DataFrame) -> ParallelPostFit:
    train_data: pd.DataFrame = train_data.compute()
    test_data: pd.DataFrame = test_data.compute()

    hyperparameters = {
        'GBM': {'extra_trees': True},
        'RF': {'n_estimators': 100, 'max_depth': 10},
        'KNN': {'weights': 'uniform', 'n_neighbors': 5},
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

    y_score = predictor.predict_proba(test_data)

    print(test_data)

    # # Krzywa ROC
    # roc_auc = roc_curve(y_true=test_data[label], y_score=y_score, average='weighted', multi_class='ovo')

    # Przygotowanie danych do wizualizacji w WANDB
    data_for_plot = [[metric, value] for metric, value in performance.items()]
    table = wandb.Table(data=data_for_plot, columns=["Metric", "Value"])

    # Logowanie wyników do WANDB
    wandb.log({"Evaluation Metrics": table})

    # Logowanie wykresu przy użyciu wandb.plot.bar
    wandb.log({"Metrics Bar Chart": wandb.plot.bar(table, "Metric", "Value", title="Performance Metrics")})

    # Logowanie krzywej ROC
    wandb.log({"ROC Curve": wandb.plot.roc_curve(y_true=test_data[label], y_probas=y_score)})

    # Zakończenie sesji WANDB
    wandb.finish()

    print(predictor.leaderboard())

    return predictor
