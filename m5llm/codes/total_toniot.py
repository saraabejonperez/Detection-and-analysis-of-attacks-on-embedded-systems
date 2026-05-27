import pandas as pd
from utils import (
    PATH_DATA, PATH_TONIOT, 
    load_excluded_columns, preprocess_dataframe, run_training_pipeline
)

def main():
    """
    Execute the complete training and evaluation pipeline.
    """
    excluded_cols = load_excluded_columns(PATH_DATA / 'columns_no_gen_rf.txt')

    traffic_df = pd.read_csv(PATH_TONIOT)
    traffic_df.columns = traffic_df.columns.str.strip().str.lower()

    traffic_df = preprocess_dataframe(traffic_df, excluded_cols)
    
    run_training_pipeline(traffic_df, suffix="totalTONIoT")

if __name__ == "__main__":
    main()