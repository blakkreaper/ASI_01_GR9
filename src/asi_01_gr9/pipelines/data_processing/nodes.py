import os

import dask.dataframe as dd
import numpy as np
from sklearn.impute import SimpleImputer

from .data_features import DataFeatures


def extract_to_parquet(raw_data_dir: str) -> dd.DataFrame:
    # List all txt files in the directory
    txt_files = [os.path.join(raw_data_dir, f) for f in os.listdir(raw_data_dir) if f.endswith('.txt')]

    # Define data types for columns
    dtype_dict = {'Participant': str, 'Index Right': str}

    # Initialize an empty list to hold the Dask DataFrames
    dfs = []

    for file_path in txt_files:
        # Read each file into a Dask DataFrame
        df = dd.read_csv(file_path, sep='\t', assume_missing=True, dtype=dtype_dict)

        # Ensure all columns are treated as strings to match dtype_dict definitions
        df = df.astype(str)

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
    imputer = SimpleImputer(missing_values='-', strategy=strategy)

    # Compute the imputer statistics on the first partition (a sample)
    sample = data.get_partition(0).compute()
    imputer.fit(sample[columns_to_impute])

    # Define the function to apply to each partition
    def impute_partition(partition, imputer):
        # Impute the missing values in the partition
        imputed_values = imputer.transform(partition[columns_to_impute])
        partition[columns_to_impute] = imputed_values
        return partition

    # Apply the function to each partition of the DataFrame
    meta = data._meta
    imputed_data = data.map_partitions(impute_partition, imputer, meta=meta)

    return imputed_data



