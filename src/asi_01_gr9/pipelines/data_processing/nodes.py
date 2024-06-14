import os
import dask.dataframe as dd
from .tran_dataframe import DataTransformation
from sklearn.impute import SimpleImputer
from dask_ml.model_selection import train_test_split


def extract_to_parquet(raw_data_dir: str) -> dd.DataFrame:
    """
    Extracts text data files from a directory, reads them into Dask DataFrames, and concatenates them into a single DataFrame.

    Parameters:
    raw_data_dir (str): The directory containing raw text data files.

    Returns:
    dd.DataFrame: A concatenated Dask DataFrame containing data from all text files.
    """
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


def transform_parquet(parquet_file: dd.DataFrame, column_mapping, columns_to_select) -> dd.DataFrame:
    """
    Transforms a Dask DataFrame by renaming columns and selecting a subset of columns.

    Parameters:
    parquet_file (dd.DataFrame): The input Dask DataFrame to be transformed.
    column_mapping (dict): A dictionary mapping old column names to new column names.
    columns_to_select (list): A list of column names to select from the DataFrame.

    Returns:
    dd.DataFrame: The transformed Dask DataFrame with renamed and selected columns.
    """
    # Rename columns
    joined_df = parquet_file.rename(columns=column_mapping)

    # Select columns
    joined_df = joined_df[columns_to_select]

    return joined_df


def impute_and_drop(data: dd.DataFrame, columns_to_impute: list, columns_to_drop: list, strategy: str) -> dd.DataFrame:
    """
    Impute missing values in specified columns using SimpleImputer in a Dask DataFrame and drop specified columns.

    Parameters:
    data (dd.DataFrame): The input Dask DataFrame with missing values.
    columns_to_impute (list): List of column names to impute.
    columns_to_drop (list): List of column names to drop.
    strategy (str): The strategy for imputation, e.g., 'mean', 'median', 'most_frequent'.

    Returns:
    dd.DataFrame: Dask DataFrame with missing values imputed and specified columns dropped.
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

    return imputed_data


def features_engineering(data: dd.DataFrame) -> dd.DataFrame:
    """
    Performs feature engineering on a Dask DataFrame by aggregating numerical columns and calculating category counts.

    Parameters:
    data (dd.DataFrame): The input Dask DataFrame.

    Returns:
    dd.DataFrame: The Dask DataFrame with engineered features.
    """
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

    Parameters:
    anxious (dd.DataFrame): DataFrame containing anxious data.
    depressive (dd.DataFrame): DataFrame containing depressive data.
    control (dd.DataFrame): DataFrame containing control group data.
    test_size (float): The proportion of the dataset to include in the test split.
    random_state (int): The seed used by the random number generator.

    Returns:
    tuple: A tuple containing:
        - X_trainval (dd.DataFrame): Training/validation set features.
        - X_test (dd.DataFrame): Test set features.
        - Y_trainval (dd.DataFrame): Training/validation set target.
        - Y_test (dd.DataFrame): Test set target.
    """
    # Add 'Class' column to each DataFrame
    anxious = anxious.assign(Class='Anxious')
    depressive = depressive.assign(Class='Depressive')
    control = control.assign(Class='Control')

    # Concatenate DataFrames
    combined_df = dd.concat([anxious, depressive, control])

    # Globally shuffle the combined DataFrame to mix classes across all partitions
    combined_df = combined_df.sample(frac=1).reset_index(drop=True)

    # Split the data into training/validation and test sets
    train_data, test_data = train_test_split(combined_df, test_size=test_size, random_state=random_state, shuffle='True')

    return train_data, test_data
