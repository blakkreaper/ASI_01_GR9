import dask.dataframe as dd
import pandas as pd
from dask.diagnostics import ProgressBar


class DataFeatures:

    @staticmethod
    def calculate_unique_values(df: dd.DataFrame, key_column: str, specific_column: str) -> dd.DataFrame:
        """
        Calculate the number of unique values for a specific column grouped by key column.

        Parameters:
        df (dd.DataFrame): The input Dask DataFrame.
        key_column (str): The name of the column to group by.
        specific_column (str): The name of the column for which to calculate the unique values.

        Returns:
        dd.DataFrame: A Dask DataFrame with the count of unique values for the specific column within each group of the key column.
        """

        # Group the dataframe by the key column and count unique values in the specific column
        unique_values_count = df.groupby(key_column)[specific_column].nunique().compute()

        # Convert the Series object to a DataFrame
        unique_values_count_df = unique_values_count.reset_index()

        # Rename the column to reflect the count of unique values
        unique_values_count_df.columns = [key_column, f"{specific_column}_unique_count"]

        return unique_values_count_df

