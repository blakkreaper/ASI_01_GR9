import json

import dask.dataframe as dd
import pandas as pd
import numpy as np
import wandb
from kedro_datasets.json import JSONDataset
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
from autogluon.tabular import TabularPredictor


def train_model_and_evaluate(train_data: dd.DataFrame, test_data: dd.DataFrame, hyperparameters: JSONDataset) -> TabularPredictor:
    """
    Trains a model using AutoGluon on the given training data, evaluates it on the test data, logs the performance metrics and visualizations to Weights and Biases (WANDB).

    Parameters:
    train_data (dd.DataFrame): The training data in the form of a Dask DataFrame.
    test_data (dd.DataFrame): The test data in the form of a Dask DataFrame.
    hyperparameters (JSONDataset): The hyperparameters for training the model.

    Returns:
    TabularPredictor: The trained AutoGluon TabularPredictor.
    """
    train_data: pd.DataFrame = train_data.compute()
    test_data: pd.DataFrame = test_data.compute()

    # hyperparameters = {
    #     'GBM': {'extra_trees': True},
    #     'RF': {'n_estimators': 100, 'max_depth': 10},
    #     'KNN': {'weights': 'uniform', 'n_neighbors': 5},
    #     'CAT': {'iterations': 10000, 'learning_rate': 0.01},
    #     'XGB': {'booster': 'gbtree', 'verbosity': 1},
    # }

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


def predict_data(predictor: TabularPredictor, data: dd.DataFrame) -> pd.DataFrame:
    """
    Uses a trained AutoGluon predictor to make predictions on the given data.

    Parameters:
    predictor (TabularPredictor): The trained AutoGluon TabularPredictor.
    data (dd.DataFrame): The data to make predictions on, in the form of a Dask DataFrame.

    Returns:
    pd.DataFrame: A Pandas DataFrame containing the original data along with the predictions.
    """
    df_for_prediction: pd.DataFrame = data.compute()
    result: pd.DataFrame = predictor.predict(df_for_prediction)
    p_result_final: pd.DataFrame = pd.concat([df_for_prediction, result], axis=1)
    return p_result_final