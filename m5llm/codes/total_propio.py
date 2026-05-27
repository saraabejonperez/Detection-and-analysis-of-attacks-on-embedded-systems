import pandas as pd
from utils import (
    PATH_DATA, PATH_BENIGN, PATH_DOS, 
    load_excluded_columns, load_csv_folder, preprocess_dataframe, run_training_pipeline
)

def main():
    """
    Execute the complete training and evaluation pipeline.
    """
    excluded_cols = load_excluded_columns(PATH_DATA / 'columns_no_gen_rf.txt')
    
    def keep_column(col: str) -> bool:
        """
        Determine whether a column should be included in the dataset.
        
        This helper function is used to filter out features that are listed 
        as non-generalizable or not available during inference.
        
        :param col: Name of the column to evaluate.
        :type col: str
        :return: True if the column should be kept, False otherwise.
        :rtype: bool
        """
        return col not in excluded_cols

    traffic_df = pd.concat([
        load_csv_folder(PATH_BENIGN, keep_column), 
        load_csv_folder(PATH_DOS, keep_column)
    ], ignore_index=True)

    traffic_df = preprocess_dataframe(traffic_df, excluded_cols)
    
    run_training_pipeline(traffic_df, suffix="totalPropio")

if __name__ == "__main__":
    main()