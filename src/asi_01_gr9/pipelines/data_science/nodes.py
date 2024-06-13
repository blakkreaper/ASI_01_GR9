import dask.dataframe as dd
import pandas as pd
import numpy as np
import wandb
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
from autogluon.tabular import TabularPredictor
import json 
import os
from typing import Any, Dict


def train_model_and_evaluate(train_data: dd.DataFrame, test_data: dd.DataFrame) -> TabularPredictor:
    train_data: pd.DataFrame = train_data.compute()
    test_data: pd.DataFrame = test_data.compute()

    # Ścieżka do pliku z hiperparametrami
hyperparams_path = "data/05_model_input/hyperparameters.json"

# Domyślne hiperparametry
default_hyperparameters = {
    'XGB': {'booster': 'gbtree', 'verbosity': 1},
    'GBM': {'extra_trees': True},
    'RF': {'n_estimators': 100, 'max_depth': 10},
    'KNN': {'weights': 'uniform', 'n_neighbors': 5},
    'CAT': {'iterations': 10000, 'learning_rate': 0.01}
}

# Sprawdzenie, czy plik istnieje i załadowanie hiperparametrów
if os.path.exists(hyperparams_path):
    with open(hyperparams_path, "r") as f:
        loaded_hyperparameters = json.load(f)
        
    # Uzupełnienie brakujących wartości domyślnymi
    hyperparameters = {}
    for key, default_params in default_hyperparameters.items():
        loaded_params = loaded_hyperparameters.get(key, {})
        hyperparameters[key] = {param: loaded_params.get(param, default_value) for param, default_value in default_params.items()}
else:
    hyperparameters = default_hyperparameters

    # Inicjalizacja sesji WANDB
    wandb.init(project="depression_prediction", entity="mlody1230")
    label: str = 'Class'

    # Trenowanie modelu z AutoGluon
    predictor: TabularPredictor = TabularPredictor(label=label, eval_metric='accuracy').fit(train_data,
                                                                                            hyperparameters=hyperparameters,
                                                                                            presets='best_quality',
                                                                                            time_limit=3600)

    # Ewaluacja modelu
    performance: dict = predictor.evaluate(test_data)
    y_pred: np.ndarray = predictor.predict(test_data)
    y_score: np.ndarray = predictor.predict_proba(test_data)

    # Przygotowanie danych do wizualizacji w WANDB
    data_for_plot = [[metric, value] for metric, value in performance.items()]
    table = wandb.Table(data=data_for_plot, columns=["Metric", "Value"])

    # Logowanie wyników do WANDB
    wandb.log({"Evaluation Metrics": table})

    # Logowanie wykresu przy użyciu wandb.plot.bar
    wandb.log({"Metrics Bar Chart": wandb.plot.bar(table, "Metric", "Value", title="Performance Metrics")})

    # Logowanie krzywej ROC
    wandb.log({"ROC Curve": wandb.plot.roc_curve(y_true=test_data[label], y_probas=y_score)})

    # Generowanie i logowanie macierzy omyłek
    cm = confusion_matrix(test_data[label], y_pred)
    cm_display = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=predictor.class_labels)

    fig, ax = plt.subplots(figsize=(10, 10))
    cm_display.plot(ax=ax)
    plt.title("Confusion Matrix")
    wandb.log({"Confusion Matrix": wandb.Image(fig)})

    # Zakończenie sesji WANDB
    wandb.finish()

    # Tabela ze statystykami algorytmow
    print(predictor.leaderboard())

    return predictor
