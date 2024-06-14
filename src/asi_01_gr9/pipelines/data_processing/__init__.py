from kedro.pipeline import node

from .nodes import (extract_to_parquet, transform_parquet, impute_and_drop,
                    concat_dfs_and_add_class, features_engineering)

# Node def Anxious
anxious_participants_raw_node = node(
    func=extract_to_parquet,
    inputs={
        "raw_data_dir": "params:anxious_participants_raw_dir",
    },
    outputs="anxious_participant_raw_parquet"
)

anxious_joined_anxious_node = node(
    func=transform_parquet,
    inputs={
        "parquet_file": "anxious_participant_raw_parquet",
        "column_mapping": "params:column_mapping_participants",
        "columns_to_select": "params:columns_to_select_participants"
    },
    outputs="anxious_trans_participants_parquet"
)

anxious_impute_drop_node = node(
    func=impute_and_drop,
    inputs={
        "data": "anxious_trans_participants_parquet",
        "columns_to_impute": "params:columns_to_impute",
        "columns_to_drop": "params:columns_to_drop_participants",
        "strategy": "params:strategy",
    },
    outputs="anxious_imputed_parquet"
)

anxious_features_engineering = node(
    func=features_engineering,
    inputs={
        "data": "anxious_imputed_parquet",
    },
    outputs="anxious_feature_engineering_parquet"
)

# Depressive----------------------------------------------------------------------------------------
depressive_participants_raw_node = node(
    func=extract_to_parquet,
    inputs={
        "raw_data_dir": "params:depressive_participants_raw_dir",
    },
    outputs="depressive_participant_raw_parquet"
)

depressive_joined_anxious_node = node(
    func=transform_parquet,
    inputs={
        "parquet_file": "depressive_participant_raw_parquet",
        "column_mapping": "params:column_mapping_participants",
        "columns_to_select": "params:columns_to_select_participants"
    },
    outputs="depressive_trans_participants_parquet"
)

depressive_impute_drop_node = node(
    func=impute_and_drop,
    inputs={
        "data": "depressive_trans_participants_parquet",
        "columns_to_impute": "params:columns_to_impute",
        "columns_to_drop": "params:columns_to_drop_participants",
        "strategy": "params:strategy",
    },
    outputs="depressive_imputed_parquet"
)

depressive_features_engineering = node(
    func=features_engineering,
    inputs={
        "data": "depressive_imputed_parquet",
    },
    outputs="depressive_feature_engineering_parquet"
)

# Control----------------------------------------------------------------------------------------
control_participants_raw_node = node(
    func=extract_to_parquet,
    inputs={
        "raw_data_dir": "params:control_participants_raw_dir",
    },
    outputs="control_participant_raw_parquet"
)

control_joined_anxious_node = node(
    func=transform_parquet,
    inputs={
        "parquet_file": "control_participant_raw_parquet",
        "column_mapping": "params:column_mapping_participants",
        "columns_to_select": "params:columns_to_select_participants"
    },
    outputs="control_trans_participants_parquet"
)

control_impute_drop_node = node(
    func=impute_and_drop,
    inputs={
        "data": "control_trans_participants_parquet",
        "columns_to_impute": "params:columns_to_impute",
        "columns_to_drop": "params:columns_to_drop_participants",
        "strategy": "params:strategy",
    },
    outputs="control_imputed_parquet"
)

control_features_engineering = node(
    func=features_engineering,
    inputs={
        "data": "control_imputed_parquet",
    },
    outputs="control_feature_engineering_parquet"
)

# Transforming for evaluation----------------------------------------------------------
concat_parquet_node = node(
    func=concat_dfs_and_add_class,
    inputs={
        "anxious": "anxious_feature_engineering_parquet",
        "depressive": "depressive_feature_engineering_parquet",
        "control": "control_feature_engineering_parquet",
        "test_size": "params:test_size",
        "random_state": "params:random_state"
    },
    outputs=["train_data", "test_data"]
)

# PREDICTION -----------------------------------------------------------------------------

predict_raw_node = node(
    func=extract_to_parquet,
    inputs={
        "raw_data_dir": "params:prediction_participants_raw_dir",
    },
    outputs="prediction_participant_raw_parquet"
)

predict_joined_anxious_node = node(
    func=transform_parquet,
    inputs={
        "parquet_file": "prediction_participant_raw_parquet",
        "column_mapping": "params:column_mapping_participants",
        "columns_to_select": "params:columns_to_select_participants"
    },
    outputs="prediction_trans_participants_parquet"
)

predict_impute_drop_node = node(
    func=impute_and_drop,
    inputs={
        "data": "prediction_trans_participants_parquet",
        "columns_to_impute": "params:columns_to_impute",
        "columns_to_drop": "params:columns_to_drop_participants",
        "strategy": "params:strategy",
    },
    outputs="prediction_imputed_parquet"
)

predict_features_engineering = node(
    func=features_engineering,
    inputs={
        "data": "prediction_imputed_parquet",
    },
    outputs="prediction_feature_engineering_parquet"
)