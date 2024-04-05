import pandas as pd
from kedro.pipeline import node


def read_csv() -> pd.DataFrame:
    df = pd.read_csv("./data/01_raw/Event Statistics - Trial Summary.csv", index_col=False)
    print(df)
    return df


reading_node = node(func=read_csv, inputs=None, outputs="raw_data")