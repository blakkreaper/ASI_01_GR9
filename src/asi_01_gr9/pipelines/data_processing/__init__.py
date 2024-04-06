from kedro.pipeline import node

from .nodes import extract_to_parquet, transform_parquet, impute_and_drop

# Node def
participants_raw_node = node(
    func=extract_to_parquet,
    inputs={
        "raw_data_dir": "params:participants_raw_dir",
    },
    outputs="participant_raw_parquet"
)

aoi_statistics_node = node(
    func=extract_to_parquet,
    inputs={
        "raw_data_dir": "params:aoi_statistics_dir",
    },
    outputs="aoi_statistics_parquet"
)

event_statistics_node = node(
    func=extract_to_parquet,
    inputs={
        "raw_data_dir": "params:event_statistics_dir"
    },
    outputs="event_statistics_parquet"
)

stimulus_anxious_node = node(
    func=extract_to_parquet,
    inputs={
        "raw_data_dir": "params:stimulus_data_dir",
    },
    outputs="stimulus_parquet"
)

joined_anxious_node = node(
    func=transform_parquet,
    inputs={
        "parquet_file": "participant_raw_parquet",
        "column_mapping": "params:column_mapping_participants",
        "columns_to_select": "params:columns_to_select_participants"
    },
    outputs="trans_participants_parquet"
)

impute_drop_node = node(
    func=impute_and_drop,
    inputs={
        "data": "trans_participants_parquet",
        "columns_to_impute": "params:columns_to_impute",
        "columns_to_drop": "params:columns_to_drop_participants",
        "strategy": "params:strategy"
    },
    outputs="model_input_parquet"
)