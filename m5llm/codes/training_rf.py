import pandas as pd
import numpy as np
from pathlib import Path
from typing import Iterable, Optional, Set, Tuple
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.utils import resample
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score, roc_auc_score
from sklearn.ensemble import RandomForestClassifier

import joblib


# =========== #
# =  PATHS  = #
# =========== #
BASE_PATH = Path(__file__).resolve().parent.parent
PATH_DATA = BASE_PATH / 'data'
PATH_BENIGN = PATH_DATA / 'BenignTraffic'
PATH_DOS = PATH_DATA / 'DenialofService'
PATH_MODEL = BASE_PATH / 'models'
PATH_MODEL.mkdir(exist_ok=True)


# ================ #
# =  PARAMETERS  = #
# ================ #
RANDOM_STATE = 42
N_SPLITS = 5
N_ESTIMATORS = 200


# =============== #
# =  FUNCTIONS  = #
# =============== #
def load_excluded_columns(path: Path) -> Set[str]:
    """
    Load the set of feature names that must be excluded from the training process.
    
    The file is expected to contain one feature name per line. These features 
    are typically removed because they do not generalize well or are not 
    available during inference.

    :param path: Path to the text file containing the feature names to exclude.
    :type path: Path
    :return: Set of feature names to be excluded from the dataset.
    :rtype: Set[str]
    :raises FileNotFoundError: If the specified file does not exist.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return {line.strip() for line in f if line.strip()}
    
    except FileNotFoundError as e:
        raise FileNotFoundError(f"No se encontró el archivo {path}") from e


def load_csv_folder(folder: Path, usecols) -> pd.DataFrame:
    """
    Load and concatenate all CSV files contained in a directory.

    The function recursively searches for CSV files inside the given folder,
    loads them into pandas DataFrames, and concatenates them into a single
    DataFrame.
    
    :param folder: Directory containing the CSV files.
    :type folder: Path
    :param usecols: Function used to filter which columns are loaded.
    :return: Concatenated DataFrame containing all loaded CSV data.
    :rtype: pd.DataFrame
    :raises ValueError: If no CSV files are found in the specified directory.
    """
    csv_files = list(folder.rglob('*.csv'))

    if not csv_files:
        raise ValueError(f"No se encontraron CSV en {folder}")
    
    dfs = [pd.read_csv(f, usecols=usecols) for f in csv_files]
    
    return pd.concat(dfs, ignore_index=True)


def preprocess_dataframe(df: pd.DataFrame, excluded_cols: Set[str]) -> pd.DataFrame:
    """
    Perform preprocessing and basic cleaning of the dataset.

    This function removes excluded features, drops rows and columns containing
    only missing values, and shuffles the dataset to randomize the sample order.
    
    :param df: Input DataFrame containing raw network traffic data.
    :type df: pd.DataFrame
    :param excluded_cols: Set of feature names to be removed.
    :type excluded_cols: Set[str]
    :return: Cleaned and shuffled DataFrame.
    :rtype: DataFrame
    """
    df = df.drop(columns=excluded_cols, errors='ignore')
    
    df = df.dropna(axis=0, how='all')
    df = df.dropna(axis=1, how='all')
    
    return df.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)


def balance_dataset(X: pd.DataFrame, y: pd.Series) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Balance the training dataset using random undersampling.

    The function balances the dataset by reducing the number of samples
    in the majority class so that both classes contain the same number
    of samples. This operation is applied only to the training set.
    
    :param X: Feature matrix of the training set.
    :type X: pd.DataFrame
    :param y: Label vector of the training set.
    :type y: pd.Series
    :return: Balanced feature matrix and corresponding label vector.
    :rtype: Tuple[pd.DataFrame, pd.Series]
    """
    df = pd.concat([X, y], axis=1)
    
    benign = df[df.label == 0]
    attack = df[df.label == 1]
    
    n_samples = min(len(benign), len(attack))
    
    benign_resampled = resample(benign, n_samples=n_samples, random_state=RANDOM_STATE)
    attack_resampled = resample(attack, n_samples=n_samples, random_state=RANDOM_STATE)
    
    balanced_df = pd.concat([benign_resampled, attack_resampled])
    balanced_df = balanced_df.sample(frac=1, random_state=RANDOM_STATE)
    
    return balanced_df.drop(columns=['label']), balanced_df['label']


def create_model() -> RandomForestClassifier:
    """
    Initialize a Random Forest classifier for ensemble learning.

    The model is configured as a forest of trees with balanced class weights 
    to handle potential dataset imbalances. It utilizes parallel processing 
    to optimize training speed.

    :return: An unoptimized Random Forest classifier instance.
    :rtype: RandomForestClassifier
    """
    model = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        class_weight='balanced'
    )

    return model


def train_with_cross_validation(X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
    """
    Train the neural network using stratified K-fold cross-validation.

    This function evaluates the stability of the model across multiple
    stratified splits of the training data.
    
    :param X: Scaled feature matrix of the training set.
    :type X: np.ndarray
    :param y: Label vector corresponding to the training set.
    :type y: pd.Series
    :return: Metrics for the evaluation of each fold
    :rtype pd.DataFrame
    """
    skf = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    
    metrics = []
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y), 1):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        X_train, y_train = balance_dataset(X_train, y_train)

        model = create_model()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_val)

        metrics.append({
            "fold": fold,
            "accuracy": accuracy_score(y_val, y_pred),
            "f1": f1_score(y_val, y_pred),
            "auc": roc_auc_score(y_val, y_pred)
        })

    results = pd.DataFrame(metrics)
    
    print("\n--- Cross-validation results ---")
    print(results)
    print("\n--- Mean ± Std ---")
    print(results.drop(columns="fold").agg(["mean", "std"]))
    
    return results


def save_preprocessing_artifacts(feature_names: pd.Index, output_path: Path, model: RandomForestClassifier) -> None:
    """
    Save preprocessing parameters required for inference.

    This function stores the ordered list of feature names and the final model. These
    artifacts are required to reproduce the same preprocessing pipeline
    during inference on an embedded device.
    
    :param feature_names: Ordered list of feature names used during training.
    :type feature_names: pd.Index
    :param output_path: Directory where the preprocessing artifacts are saved.
    :type output_path: Path
    :param model: Final model
    :type model: RandomForestClassifier
    :raises RuntimeError: If an error occurs while saving the artifacts.
    """
    try:
        np.save(output_path / 'features_rf.npy', feature_names.to_numpy())
        joblib.dump(model, output_path / 'dos_classifier_rf.pkl')
    
    except Exception as e:
        raise RuntimeError("Error al guardar los artefactos de preprocesado") from e


def plot_confusion_matrix(y_true: Iterable[int], y_pred: Iterable[int], 
                          class_names: Tuple[str, str]=('Benign', 'DoS'), 
                          normalize: bool=False, save_path: Optional[Path]=None) -> None:
    """
    Plot and optionally save the confusion matrix as a heatmap.

    The confusion matrix can be displayed using absolute values or
    normalized per class. The generated figure can also be saved
    to disk for reporting and documentation purposes.
    
    :param y_true: Ground truth labels.
    :param y_pred: Predicted labels produced by the model.
    :param class_names: Names of the classes displayed on the axes.
    :param normalize: Whether to normalize the confusion matrix by true labels.
    :param save_path: Path to save the generated figure. If None, the figure is not saved.
    """
    cm = confusion_matrix(y_true, y_pred)
    
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    
    plt.figure(figsize=(6, 5))
    sns.heatmap(
        cm, annot=True,
        fmt='.2f' if normalize else 'd',
        cmap='Blues',
        xticklabels=class_names,
        yticklabels=class_names
    )
    plt.xlabel('Predicted label')
    plt.ylabel('True label')
    plt.title('Confusion Matrix')
    plt.tight_layout()
    
    if save_path is not None:
        plt.savefig(save_path, dpi=300)
    
    plt.show()


def main() -> None:
    """
    Execute the complete training and evaluation pipeline.

    This function loads and preprocesses the dataset, splits the data
    into training and test sets, balances and scales the training data,
    trains and evaluates the neural network model, generates evaluation
    metrics and confusion matrices, and finally exports the trained model.
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

    benign_df = load_csv_folder(PATH_BENIGN, keep_column)
    
    attack_df = load_csv_folder(PATH_DOS, keep_column)

    traffic_df = pd.concat([benign_df, attack_df], ignore_index=True)
    traffic_df = preprocess_dataframe(traffic_df, excluded_cols)

    X = traffic_df.drop(columns=['label'])
    y = traffic_df['label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)

    train_with_cross_validation(X_train, y_train)

    feature_names = X_train.columns

    final_model = create_model()
    
    X_train_bal, y_train_bal = balance_dataset(X_train, y_train)
    
    final_model.fit(X_train_bal, y_train_bal)

    y_pred = final_model.predict(X_test)

    plot_confusion_matrix(y_test, y_pred, class_names=('Benign', 'DoS'), save_path=PATH_MODEL / 'confusion_matrix_rf.png')
    plot_confusion_matrix(y_test, y_pred, class_names=('Benign', 'DoS'), normalize=True, save_path=PATH_MODEL / 'confusion_matrix_normalized_rf.png')

    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel().tolist()
    print(cm)
    print(f"\t{tp} True Positives")
    print(f"\t{tn} True Negatives")
    print(f"\t{fp} False Positives")
    print(f"\t{fn} False Negatives")
    print(classification_report(y_test, y_pred))

    save_preprocessing_artifacts(feature_names=feature_names, output_path=PATH_MODEL, model=final_model)


if __name__ == "__main__":
    main()