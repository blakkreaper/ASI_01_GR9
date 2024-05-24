
import dask.dataframe as dd


class DataTransformation:

    @staticmethod
    def get_max_count_per_category(data: dd.DataFrame, category: str) -> dd.DataFrame:
        # Group by 'Participant' and 'category' and compute the size of each group
        counts = data.groupby(['Participant', category]).size()
        counts = counts.rename('count').reset_index()  # Correctly assign the name and reset index

        # Get the maximum count for each 'Participant'
        max_counts = counts.groupby('Participant')['count'].max().reset_index()
        max_counts = max_counts.rename(columns={'count': f'max_count_of_{category}'})

        # Get the category name corresponding to the maximum count
        max_counts_category = counts[counts['count'] == counts.groupby('Participant')['count'].transform(max)]
        max_counts_category = max_counts_category.drop_duplicates(subset=['Participant'])
        max_counts_category = max_counts_category.rename(columns={category: f'Max_{category}'})

        # Merge to associate the max count with its category
        max_counts = dd.merge(max_counts, max_counts_category, on='Participant', how='left')

        return max_counts
