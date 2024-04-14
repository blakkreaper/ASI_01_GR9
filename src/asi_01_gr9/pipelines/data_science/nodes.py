

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report, roc_auc_score
from dask_ml.wrappers import ParallelPostFit
from sklearn.ensemble import RandomForestClassifier
import dask.dataframe as dd
import dask.array as da
from sklearn.model_selection import StratifiedKFold


def train_evaluate_model(x_train: dd.DataFrame, y_train: dd.DataFrame, n_splits: int, random_state: int,
                         participant_col: str = 'Participant') -> ParallelPostFit:
    """
    Train a model using K-Fold cross-validation, evaluate it, and write the statistics to a text file,
    returning only the best performing model and ensuring participant identifiers are managed correctly.

    Args:
        x_train (dd.DataFrame): Training features, excluding the 'Participant' column.
        y_train (dd.DataFrame): Training labels, encoded as integers.
        n_splits (int): Number of folds for K-Fold cross-validation.
        random_state (int): Random state for reproducibility.
        participant_col (str): Column name for participant identifiers.

    Returns:
        best_model (ParallelPostFit): The best performing model.
    """
    # Separate participant identifiers from training data
    participants = x_train[[participant_col]]
    x_train = x_train.drop(columns=[participant_col])
    x_train = x_train.to_dask_array(lengths=True)
    y_train = y_train.to_dask_array(lengths=True).ravel()

    kf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    best_score = 0.0
    best_model = None
    best_auc = -np.inf  # Initialize with negative infinity
    best_cm = None
    best_participants = None

    for train_index, test_index in kf.split(x_train, y_train):
        X_train, X_test = x_train[train_index], x_train[test_index]
        y_train_fold, y_test_fold = y_train[train_index], y_train[test_index]
        participants_test_fold = participants.loc[participants.index.isin(test_index)].compute()

        # Ensure the estimator is a multi-class classifier
        model = ParallelPostFit(estimator=RandomForestClassifier(n_estimators=100, random_state=random_state))
        model.fit(X_train, y_train_fold)

        y_pred_fold = model.predict(X_test)
        y_pred_proba_fold = model.predict_proba(X_test)

        score = accuracy_score(y_test_fold.compute(), y_pred_fold.compute())

        # ROC AUC calculation for multi-class classification
        if len(da.unique(y_test_fold).compute()) > 1:
            auc = roc_auc_score(y_test_fold.compute(), y_pred_proba_fold.compute(), multi_class="ovo", average="macro")
        else:
            auc = None

        cm = confusion_matrix(y_test_fold.compute(), y_pred_fold.compute())

        if score > best_score:
            best_score = score
            best_auc = auc if auc is not None else best_auc
            best_model = model
            best_cm = cm
            best_participants = participants_test_fold

    # Write results to a text file
    with open('data/08_reporting/training_result.txt', 'w') as f:
        f.write(f'Best Accuracy: {best_score}\n\n')
        if best_auc is not None:
            f.write(f'Best ROC AUC: {best_auc}\n\n')
        else:
            f.write('Best ROC AUC: Not computed due to single class in y_test_fold\n\n')
        f.write('Best Confusion Matrix:\n\n')
        f.write(pd.DataFrame(best_cm, index=model.classes_, columns=model.classes_).to_string())
        f.write('\nParticipants in best model testing:\n\n')
        f.write(best_participants.to_string())

    return best_model


def evaluate_model_on_test_data(model: ParallelPostFit, x_test: dd.DataFrame, y_test: dd.DataFrame) -> None:
    """
    Evaluates the trained model on the test dataset and writes the performance metrics to a text file.

    Args:
        model (ParallelPostFit): The trained model.
        x_test (dd.DataFrame): Test dataset features, excluding the 'Participant' column.
        y_test (dd.DataFrame): Test dataset labels.

    Returns:
        None: This function writes the results to a text file instead of returning them.
    """
    # Ensure the test data does not include the 'Participant' column
    if 'Participant' in x_test.columns:
        x_test = x_test.drop(columns=['Participant'])
    x_test_array = x_test.to_dask_array(lengths=True)
    y_test_array = y_test.to_dask_array(lengths=True).ravel()

    # Perform predictions
    y_pred = model.predict(x_test_array).compute()
    y_pred_proba = model.predict_proba(x_test_array).compute()

    # Compute metrics
    accuracy = accuracy_score(y_test_array.compute(), y_pred)
    if len(da.unique(y_test_array).compute()) > 1:
        auc_score = roc_auc_score(y_test_array.compute(), y_pred_proba, multi_class="ovo", average="macro")
    else:
        auc_score = None

    cm = confusion_matrix(y_test_array.compute(), y_pred)

    # Write results to a text file
    with open('data/08_reporting/test_data_evaluation.txt', 'w') as f:
        f.write(f'Accuracy: {accuracy}\n\n')
        if auc_score is not None:
            f.write(f'ROC AUC: {auc_score}\n\n')
        else:
            f.write('ROC AUC: Not computed due to single class in y_test\n\n')
        f.write('Confusion Matrix:\n\n')
        f.write(pd.DataFrame(cm, index=model.classes_, columns=model.classes_).to_string())


def make_predictions(model, trainval_df: dd.DataFrame) -> dd.DataFrame:
    trainval_pd = trainval_df.compute()

    predictions_array = model.predict(trainval_pd)

    predictions_df = dd.from_pandas(pd.DataFrame(predictions_array, columns=['Predicted_Label']), npartitions=1)

    return predictions_df