from typing import Optional, Tuple

import pandas as pd
from dask.array import Array
from dask_ml.model_selection import KFold
from numpy import ndarray
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from dask_ml.wrappers import ParallelPostFit
from sklearn.ensemble import RandomForestClassifier
import dask.dataframe as dd


def train_evaluate_model(X: dd.DataFrame, y: dd.DataFrame, n_splits: int, random_state: int) -> Tuple[Optional[ParallelPostFit], float]:
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    best_score = 0.0
    best_model = None
    best_cm = None

    X_array = X.to_dask_array(lengths=True)
    y_array = y.to_dask_array(lengths=True).ravel()

    index = 0

    for train_index, test_index in kf.split(X_array):
        index += 1
        print(f'Training batch: {index}')
        X_train, X_test = X_array[train_index], X_array[test_index]
        y_train, y_test = y_array[train_index], y_array[test_index]

        model = ParallelPostFit(estimator=RandomForestClassifier(n_estimators=100, random_state=random_state))
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        score = accuracy_score(y_test.compute(), y_pred.compute())
        cm = confusion_matrix(y_test.compute(), y_pred.compute())

        if score > best_score:
            best_score = score
            best_model = model
            best_cm = cm

    print(f'Best Score: {best_score}')
    print(f'Best Confusion Matrix:\n{best_cm}')

    return best_model, best_score


def make_predictions(model, trainval_df: dd.DataFrame) -> dd.DataFrame:
    # Assuming the model expects a Pandas DataFrame, convert Dask DataFrame to Pandas
    # This step assumes that your data is small enough to fit into memory after preprocessing
    # If your dataset is too large, consider using dask_ml's ParallelPostFit or another strategy
    trainval_pd = trainval_df.compute()

    # Make predictions with the model
    # Ensure that 'model.predict' is capable of handling a pandas DataFrame if not, adjust accordingly
    predictions_array = model.predict(trainval_pd)

    # Convert predictions to a Dask DataFrame for further processing if necessary
    # Note: This conversion assumes 'predictions_array' can be large and thus benefits from parallel processing
    # If not, you might keep it as a pandas Series/DataFrame
    predictions_df = dd.from_pandas(pd.DataFrame(predictions_array, columns=['Predicted_Label']), npartitions=1)

    return predictions_df