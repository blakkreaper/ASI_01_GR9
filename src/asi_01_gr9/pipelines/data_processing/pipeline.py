from kedro.pipeline import Pipeline

from asi_01_gr9.pipelines import anxious_participants_raw_node, anxious_joined_anxious_node, anxious_impute_drop_node, \
    anxious_features_engineering, depressive_participants_raw_node, depressive_joined_anxious_node, \
    depressive_impute_drop_node, depressive_features_engineering, control_participants_raw_node, \
    control_joined_anxious_node, control_impute_drop_node, control_features_engineering
from asi_01_gr9.pipelines.data_processing import concat_parquet_node


def create_preprocess_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [anxious_participants_raw_node,
         anxious_joined_anxious_node,
         anxious_impute_drop_node,
         anxious_features_engineering,
         depressive_participants_raw_node,
         depressive_joined_anxious_node,
         depressive_impute_drop_node,
         depressive_features_engineering,
         control_participants_raw_node,
         control_joined_anxious_node,
         control_impute_drop_node,
         control_features_engineering,
         concat_parquet_node,
         ])
