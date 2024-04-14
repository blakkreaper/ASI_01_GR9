from kedro.pipeline import node

from .nodes import extract_to_parquet, transform_parquet, impute_and_drop, concat_dfs_and_add_class, \
    encoders_and_features_generation, \
    features_engineering, apply_existing_encoders_and_scale

# Node def Anxious
anxious_participants_raw_node = node(
    func=extract_to_parquet,
    inputs={
        "raw_data_dir": "params:anxious_participants_raw_dir",
    },
    outputs="anxious_participant_raw_parquet"
)
#
# aoi_statistics_node = node(
#     func=extract_to_parquet,
#     inputs={
#         "raw_data_dir": "params:anxious_aoi_statistics_dir",
#     },
#     outputs="aoi_statistics_parquet"
# )
#
# event_statistics_node = node(
#     func=extract_to_parquet,
#     inputs={
#         "raw_data_dir": "params:anxious_event_statistics_dir"
#     },
#     outputs="event_statistics_parquet"
# )
#
# stimulus_anxious_node = node(
#     func=extract_to_parquet,
#     inputs={
#         "raw_data_dir": "params:anxious_stimulus_data_dir",
#     },
#     outputs="stimulus_parquet"
# )

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
    outputs=["x_trainval", "x_test", "y_trainval", "y_test"]
)

encode_train_node = node(
    func=encoders_and_features_generation,
    inputs={
        "x": "x_trainval",
        "categorical_cols": "params:categorical_cols",
        "numerical_cols": "params:numerical_cols",
        "extra_numerical_cols": "params:extra_numerical_cols"
    },
    outputs=["x_trainval_encoded", "dummy_encoder", "scaler_encoder"],
    name="encode_train_node"
)

encode_test_node = node(
    func=apply_existing_encoders_and_scale,
    inputs={
        "x": "x_test",
        "categorical_cols": "params:categorical_cols",
        "numerical_cols": "params:numerical_cols",
        "extra_numerical_cols": "params:extra_numerical_cols",
        "expected_columns": "params:expected_columns",
        "encoder": "dummy_encoder",
        "scaler": "scaler_encoder"
    },
    outputs="x_test_encoded",
    name="encode_test_node"
)

# Prediction----------------------------------------------------------------------------------------
prediction_participants_raw_node = node(
    func=extract_to_parquet,
    inputs={
        "raw_data_dir": "params:prediction_participants_raw_dir",
    },
    outputs="prediction_participant_raw_parquet"
)

prediction_joined_anxious_node = node(
    func=transform_parquet,
    inputs={
        "parquet_file": "prediction_participant_raw_parquet",
        "column_mapping": "params:column_mapping_participants",
        "columns_to_select": "params:columns_to_select_participants"
    },
    outputs="prediction_trans_participants_parquet"
)

prediction_impute_drop_node = node(
    func=impute_and_drop,
    inputs={
        "data": "prediction_trans_participants_parquet",
        "columns_to_impute": "params:columns_to_impute",
        "columns_to_drop": "params:columns_to_drop_participants",
        "strategy": "params:strategy",
    },
    outputs="prediction_imputed_parquet"
)

prediction_features_engineering = node(
    func=features_engineering,
    inputs={
        "data": "prediction_imputed_parquet",
    },
    outputs="prediction_feature_engineering_parquet"
)

prediction_encoded_node = node(
    func=encoders_and_features_generation,
    inputs={
        "x": "prediction_feature_engineering_parquet",
        "categorical_cols": "params:categorical_cols",
        "numerical_cols": "params:numerical_cols"
    },
    outputs="prediction_encoded_parquet"
)
