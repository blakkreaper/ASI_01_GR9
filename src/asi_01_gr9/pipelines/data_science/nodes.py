from typing import Dict, Any

import dask.dataframe as dd
from sklearn import clone
from sklearn.metrics import accuracy_score
from sklearn.model_selection import KFold


def split_data(data: dd.DataFrame, parameters: Dict[str, Any]):
    kf = KFold(n_splits=parameters['n_splits'], shuffle=True, random_state=parameters['random_state'])
    return [(data.iloc[train_idx], data.iloc[test_idx]) for train_idx, test_idx in kf.split(data)]


def train_model(train: dd.DataFrame, test: dd.DataFrame, parameters: Dict[str, Any]):
    model = clone(parameters['model'])  # Clone the model to ensure a fresh model for each fold
    model.fit(train.drop(columns=[parameters['target']]), train[parameters['target']])
    predictions = model.predict(test.drop(columns=[parameters['target']]))
    return accuracy_score(test[parameters['target']], predictions)