import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Set
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample
from sklearn.metrics import classification_report, confusion_matrix

import tensorflow as tf


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
# =  CONSTANTES  = #
# ================ #
RANDOM_STATE = 42
N_SPLITS = 5
BATCH_SIZE = 256
EPOCHS_CV = 15
EPOCHS_FT = 20


# ============= #
# =  MÉTODOS  = #
# ============= #
def load_excluded_columns(path: Path) -> Set[str]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return {line.strip() for line in f if line.strip()}

    except FileNotFoundError as e:
        raise FileNotFoundError(f"No se encontró el archivo {path}") from e


def load_csv_folder(folder: Path, usecols) -> pd.DataFrame:
    csv_files = list(folder.rglob('*.csv'))

    if not csv_files:
        raise ValueError(f"No se encontraron CSV en {folder}")

    dfs = [pd.read_csv(f, usecols=usecols) for f in csv_files]

    return pd.concat(dfs, ignore_index=True)


def preprocess_dataframe(df: pd.DataFrame, excluded_cols: Set[str]) -> pd.DataFrame:
    df = df.drop(columns=excluded_cols, errors='ignore')

    df = df.dropna(axis=0, how='all')
    df = df.dropna(axis=1, how='all')

    return df.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)


def balance_dataset(X: pd.DataFrame, y: pd.Series) -> Tuple[pd.DataFrame, pd.Series]:
    df = pd.concat([X, y], axis=1)

    benign = df[df.label == 0]
    attack = df[df.label == 1]

    n_samples = min(len(benign), len(attack))

    benign_resampled = resample(benign, n_samples=n_samples, random_state=RANDOM_STATE)
    attack_resampled = resample(attack, n_samples=n_samples, random_state=RANDOM_STATE)

    balanced_df = pd.concat([benign_resampled, attack_resampled])
    balanced_df = balanced_df.sample(frac=1, random_state=RANDOM_STATE)

    return (balanced_df.drop(columns=['label']), balanced_df['label'])


def create_model(input_dim: int) -> tf.keras.Model:
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(input_dim,)),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    return model


def train_with_cross_validation(X: np.ndarray, y: pd.Series) -> None:
    skf = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)

    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y), 1):
        model = create_model(X.shape[1])

        model.fit(
            X[train_idx], y.iloc[train_idx],
            validation_data=(X[val_idx], y.iloc[val_idx]),
            epochs=EPOCHS_CV,
            batch_size=BATCH_SIZE,
            verbose=0
        )


def save_preprocessing_artifacts(scaler: StandardScaler, feature_names: pd.Index, output_path: Path) -> None:
    try:
        np.save(output_path / 'mean.npy', scaler.mean_)
        np.save(output_path / 'scale.npy', scaler.scale_)
        np.save(output_path / 'features.npy', feature_names.to_numpy())

    except Exception as e:
        raise RuntimeError("Error al guardar los artefactos de preprocesado") from e


def plot_confusion_matrix(y_true, y_pred, class_names=('Benign', 'DoS'), normalize=False, save_path=None) -> None:
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
    excluded_cols = load_excluded_columns(PATH_DATA / 'columns_no_gen.txt')

    def keep_column(col: str) -> bool:
        return col not in excluded_cols
    
    benign_df = load_csv_folder(PATH_BENIGN, keep_column)
    benign_df['label'] = 0

    attack_df = load_csv_folder(PATH_DOS, keep_column)

    traffic_df = pd.concat([benign_df, attack_df], ignore_index=True)
    traffic_df = preprocess_dataframe(traffic_df, excluded_cols)

    X = traffic_df.drop(columns=['label'])
    y = traffic_df['label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)

    X_train, y_train = balance_dataset(X_train, y_train)

    feature_names = X_train.columns

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    save_preprocessing_artifacts(scaler=scaler, feature_names=feature_names, output_path=PATH_MODEL)

    train_with_cross_validation(X_train, y_train)

    final_model = create_model(X_train.shape[1])
    final_model.fit(
        X_train, y_train,
        epochs=EPOCHS_FT,
        validation_split=0.1,
        verbose=1
    )

    y_pred = (final_model.predict(X_test) > 0.5).astype(int)

    plot_confusion_matrix(y_test, y_pred, class_names=('Benign', 'DoS'), save_path=PATH_MODEL / 'confusion_matrix.png')
    plot_confusion_matrix(y_test, y_pred, class_names=('Benign', 'DoS'), normalize=True, save_path=PATH_MODEL / 'confusion_matrix_normalized.png')

    print(confusion_matrix(y_test, y_pred))
    print(classification_report(y_test, y_pred))

    converter = tf.lite.TFLiteConverter.from_keras_model(final_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()

    model_path = PATH_MODEL / 'dos_classifier.tflite'
    model_path.write_bytes(tflite_model)


if __name__ == "__main__":
    main()