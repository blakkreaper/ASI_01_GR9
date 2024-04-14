import os

import dask.dataframe as dd
import pandas as pd

from .tran_dataframe import DataTransformation
from dask_ml.preprocessing import StandardScaler, DummyEncoder
from sklearn.impute import SimpleImputer
import joblib
from dask_ml.model_selection import train_test_split


def extract_to_parquet(raw_data_dir: str) -> dd.DataFrame:
    # List all txt files in the directory
    txt_files = [os.path.join(raw_data_dir, f) for f in os.listdir(raw_data_dir) if f.endswith('.txt')]

    # Define data types for columns
    dtype_dict = {'Participant': str, 'Index Right': str}

    # Initialize an empty list to hold the Dask DataFrames
    dfs = []

    for file_path in txt_files:
        # Read each file into a Dask DataFrame
        df = dd.read_csv(file_path, sep='\t', assume_missing=True, dtype=dtype_dict).astype(str)

        dfs.append(df)

    # Concatenate all DataFrames vertically since merging large datasets on a key might be intensive
    # and may not be needed if you're aiming to concatenate data. If a merge is necessary, adjust accordingly.
    combined_df = dd.concat(dfs, axis=0)

    # Repartition to optimize partition size based on the combined data
    combined_df = combined_df.repartition(npartitions=max(1, int(combined_df.npartitions / len(dfs))))

    return combined_df


def transform_parquet(
    parquet_file: dd.DataFrame,
    column_mapping,
    columns_to_select
) -> dd.DataFrame:

    # Rename columns
    joined_df = parquet_file.rename(columns=column_mapping)

    # Select columns
    joined_df = joined_df[columns_to_select]

    return joined_df


def impute_and_drop(data: dd.DataFrame, columns_to_impute: list, columns_to_drop: list, strategy: str) -> dd.DataFrame:
    """
    Impute missing values in specified columns using SimpleImputer in a Dask DataFrame.

    Parameters:
    data (dd.DataFrame): The input Dask DataFrame with missing values.
    columns_to_impute (list): List of column names to impute.
    strategy (str): The strategy for imputation, e.g., 'mean', 'median', 'most_frequent'.

    Returns:
    dd.DataFrame: Dask DataFrame with missing values imputed.
    """
    # Drop not needed columns
    data = data.drop(columns_to_drop, axis=1, errors='ignore')
    data = data[data['Pupil Diameter Right [mm]'] != '-']

    # Initialize the SimpleImputer
    imputer_cat = SimpleImputer(missing_values='-', strategy=strategy)

    # Compute the imputer statistics on the first partition (a sample)
    sample = data.get_partition(0).compute()
    imputer_cat.fit(sample[columns_to_impute])

    # Define the function to apply to each partition
    def impute_partition(partition, imputer):
        # Impute the missing values in the partition
        imputed_values = imputer.transform(partition[columns_to_impute])
        partition[columns_to_impute] = imputed_values
        return partition

    # Apply the function to each partition of the DataFrame
    meta = data._meta
    imputed_data = data.map_partitions(impute_partition, imputer_cat, meta=meta)

    # # Add the new column with the specified string value
    # imputed_data['Class'] = new_column_value

    return imputed_data


def features_engineering(data: dd.DataFrame) -> dd.DataFrame:
    assert 'Participant' in data.columns, "'Participant' column is not in the DataFrame"

    # Convert numeric columns to float, handling cases where columns might be missing or conversions could fail
    numeric_cols = [
        'Pupil Diameter Right [mm]', 'Point of Regard Right X [px]',
        'Point of Regard Right Y [px]', 'Gaze Vector Right X',
        'Gaze Vector Right Y', 'Gaze Vector Right Z'
    ]
    numeric_cols = [col for col in numeric_cols if col in data.columns]
    for col in numeric_cols:
        data[col] = data[col].astype(float)

    # Aggregation dictionary
    agg_dict = {
        'Pupil Diameter Right [mm]': 'median',
        'Point of Regard Right X [px]': 'mean',
        'Point of Regard Right Y [px]': 'mean',
        'Gaze Vector Right X': 'mean',
        'Gaze Vector Right Y': 'mean',
        'Gaze Vector Right Z': 'mean'
    }
    agg_dict = {k: v for k, v in agg_dict.items() if k in data.columns}

    # Perform aggregations
    result_agg = data.groupby('Participant').agg(agg_dict, shuffle='tasks').reset_index()

    # Categories to calculate max counts for
    categories = ['Stimulus', 'Category Right', 'AOI Name Right']
    max_counts_df_list = []

    for category in categories:
        max_counts_df = DataTransformation.get_max_count_per_category(data, category).rename(columns={'count': f'count_{category}'})
        max_counts_df_list.append(max_counts_df)

    # Concatenate all max count DataFrames
    max_counts_concatenated = dd.concat(max_counts_df_list, axis=1)

    # Ensure 'Participant' column is not duplicated
    max_counts_concatenated = max_counts_concatenated.loc[:, ~max_counts_concatenated.columns.duplicated()]

    # Merge the max count information with the aggregated data
    final_result = dd.merge(result_agg, max_counts_concatenated, on='Participant', how='left')

    # Remove columns that start with 'count_'
    final_result = final_result.drop([col for col in final_result.columns if col.startswith('count_')], axis=1)

    return final_result


def concat_dfs_and_add_class(anxious: dd.DataFrame, depressive: dd.DataFrame, control: dd.DataFrame, test_size: float, random_state: int):
    """
    Concatenate three Dask DataFrames, add a 'Class' column, globally shuffle, and then split into training/validation and test sets.

    Args:
        anxious (dd.DataFrame): DataFrame containing anxious data.
        depressive (dd.DataFrame): DataFrame containing depressive data.
        control (dd.DataFrame): DataFrame containing control group data.
        test_size (float): The proportion of the dataset to include in the test split.
        random_state (int): The seed used by the random number generator.

    Returns:
        X_trainval (dd.DataFrame): Training/validation set features.
        X_test (dd.DataFrame): Test set features.
        Y_trainval (dd.DataFrame): Training/validation set target.
        Y_test (dd.DataFrame): Test set target.
    """
    # Add 'Class' column to each DataFrame
    anxious = anxious.assign(Class='Anxious')
    depressive = depressive.assign(Class='Depressive')
    control = control.assign(Class='Control')

    # Concatenate DataFrames
    combined_df = dd.concat([anxious, depressive, control])

    # Globally shuffle the combined DataFrame to mix classes across all partitions
    combined_df = combined_df.shuffle(on='Participant')

    # combined_df = combined_df.repartition(npartitions='auto')

    # Reset index post-shuffling to maintain a proper sequence
    combined_df = combined_df.reset_index(drop=True)

    # Split into features (X) and target (Y)
    Y = combined_df[['Class']]
    X = combined_df.drop('Class', axis=1)

    # Split the data into training/validation and test sets
    X_trainval, X_test, Y_trainval, Y_test = train_test_split(X, Y, test_size=test_size, random_state=random_state)

    return X_trainval, X_test, Y_trainval, Y_test


def encoders_and_features_generation(x: dd.DataFrame, categorical_cols: list, numerical_cols: list,
                                     extra_numerical_cols: list = None) -> tuple[dd.DataFrame, DummyEncoder, StandardScaler]:
    """
    Encodes categorical variables and scales numerical variables in a Dask DataFrame while preserving identifiers.
    Returns the processed DataFrame along with the encoder and scaler for later use.

    Returns:
        - Tuple: (Processed DataFrame, encoder, scaler)
    """
    # Separate identifiers to keep them unchanged
    identifiers = x[['Participant']]  # Ensure it's a DataFrame

    # Encoding categorical variables
    encoder = None
    if categorical_cols:
        encoder = DummyEncoder()
        features_cat = x[categorical_cols].categorize()
        features_encoded = encoder.fit_transform(features_cat)
    else:
        features_encoded = dd.from_pandas(pd.DataFrame(index=x.index), npartitions=x.npartitions)

    # Scaling primary numerical columns
    scaler = None
    if numerical_cols:
        scaler = StandardScaler()
        features_num = x[numerical_cols].astype(float)
        features_scaled = scaler.fit_transform(features_num)
    else:
        features_scaled = dd.from_pandas(pd.DataFrame(index=x.index), npartitions=x.npartitions)

    # Convert extra numerical columns to integers, if present
    if extra_numerical_cols:
        integer_features = x[extra_numerical_cols].astype(int)
        processed_features = dd.concat([features_encoded, features_scaled, integer_features], axis=1)
    else:
        processed_features = dd.concat([features_encoded, features_scaled], axis=1)

    # Reattach identifiers
    x_processed = dd.concat([identifiers, processed_features], axis=1).reset_index(drop=True)

    return x_processed, encoder, scaler


def apply_existing_encoders_and_scale(x: dd.DataFrame, categorical_cols: list, numerical_cols: list,
                                      extra_numerical_cols: list = None, encoder: DummyEncoder = None, scaler: StandardScaler = None,
                                      expected_columns=None) -> dd.DataFrame:
    """
    Applies existing encoders and scalers to categorical and numerical variables in a Dask DataFrame
    while ensuring that all expected columns are present and correctly initialized if missing.

    Args:
        x (dd.DataFrame): The input Dask DataFrame.
        categorical_cols (list of str): List of categorical column names to encode.
        numerical_cols (list of str): List of primary numerical column names to scale.
        extra_numerical_cols (list of str, optional): Additional numerical column names to keep as integers.
        encoder (DummyEncoder): Preloaded encoder.
        scaler (StandardScaler): Preloaded scaler.
        expected_columns (list of str, optional): List of all expected column names to ensure are present in the output.

    Returns:
        dd.DataFrame: The processed Dask DataFrame with encoded and scaled features, including identifiers.
    """
    # Separate identifiers to keep them unchanged
    identifiers = x[['Participant']]  # Assuming 'Participant' is the identifier column

    # Apply encoding to categorical variables
    features_cat = x[categorical_cols].categorize()
    features_encoded = encoder.transform(features_cat)

    # Apply scaling to numerical columns
    features_num = x[numerical_cols].astype(float)
    features_scaled = scaler.transform(features_num)

    # Handle extra numerical columns, if present
    if extra_numerical_cols:
        integer_features = x[extra_numerical_cols].astype(int)
        processed_features = dd.concat([features_encoded, features_scaled, integer_features], axis=1)
    else:
        processed_features = dd.concat([features_encoded, features_scaled], axis=1)

    # Reattach identifiers
    x_processed = dd.concat([identifiers, processed_features], axis=1).reset_index(drop=True)

    # Ensure all expected columns are present, initializing missing ones as required
    if expected_columns:
        for column in expected_columns:
            if column not in x_processed.columns:
                # Initialize 'Max_' columns with False or others with a suitable default value
                if column.startswith('Max_'):
                    x_processed[column] = False
                else:
                    x_processed[column] = None  # Adjust according to your needs

    return x_processed
