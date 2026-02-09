import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf


# =========== #
# =  RUTAS  = #
# =========== #
PATH_DATA = Path(__file__).resolve().parent.parent / 'data'
PATH_BENIGN = PATH_DATA / 'BenignTraffic'
PATH_DOS = PATH_DATA / 'DenialofService'
PATH_MODEL = Path(__file__).resolve().parent.parent / 'models'
#PATH_MODEL.mkdir(exists_ok=True)


# ============== #
# =  DATASETS  = #
# ============== #
# Cargar archivo con columnas a filtrar
with open(PATH_DATA / 'columns_no_gen.txt', 'r', encoding='utf-8') as f:
    columns_no_gen = [line.strip() for line in f if line.strip()]

columns_no_gen = set(columns_no_gen)

def keep_column(col_name):
    return col_name not in columns_no_gen

# Obtener todos los csv de la carpeta BenignTraffic
benign_df = [pd.read_csv(f, usecols=keep_column) for f in list(PATH_BENIGN.glob('*.csv'))]
# Crear único DataFrame
benign_df = pd.concat(benign_df, ignore_index=True)
benign_df["label"] = (benign_df["label"].replace("BENIGN", 0).astype("int"))


# Obtener todos los csv de la carpeta DenialofService (y subcarpetas)
attack_df = [pd.read_csv(f, usecols=keep_column) for f in list(PATH_DOS.rglob('*.csv'))]
# Crear único DataFrame
attack_df = pd.concat(attack_df, ignore_index=True)


# Unión de los csv
traffic_df = pd.concat([benign_df, attack_df], ignore_index=True)
# Eliminar columnas que no generalizan
traffic_df = traffic_df.drop(columns=columns_no_gen, errors = 'ignore')
# Filtrado de datos (filas que sean 100% NaN)
traffic_df = traffic_df.dropna(axis=0, how='all')
# Filtrado de datos (columnas que sean 100% NaN)
traffic_df = traffic_df.dropna(axis=1, how='all')
# Mezcla de los datos
traffic_df = traffic_df.sample(frac=1).reset_index(drop=True)

X = traffic_df.drop(columns=["label"])
y = traffic_df["label"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

train_df = pd.concat([X_train, y_train], axis=1)
train_benign = train_df[train_df.label == 0]
train_attack = train_df[train_df.label == 1]

n_samples = min(len(train_benign), len(train_attack))

train_benign = resample(train_benign, n_samples=n_samples, random_state=42)
train_attack = resample(train_attack, n_samples=n_samples, random_state=42)

train_df = pd.concat([train_benign, train_attack])
train_df = train_df.sample(frac=1, random_state=42)

X_train = train_df.drop(columns=["label"])
y_train = train_df["label"]

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

def create_model(input_dim):
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(input_dim,)),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])

    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    return model

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

for fold, (train_idx, val_idx) in enumerate(skf.split(X_train, y_train), 1):
    model = create_model(X_train.shape[1])

    model.fit(
        X_train[train_idx], y_train.iloc[train_idx],
        validation_data=(X_train[val_idx], y_train.iloc[val_idx]),
        epochs=15,
        batch_size=256,
        verbose=0
    )

final_model = create_model(X_train.shape[1])

final_model.fit(
    X_train, y_train,
    epochs=20,
    batch_size=256,
    validation_split=0.1,
    verbose=1
)

# Evaluación
y_pred = (final_model.predict(X_test) > 0.5).astype(int)

print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

converter = tf.lite.TFLiteConverter.from_keras_model(final_model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]

tflite_model = converter.convert()

tflite_path = PATH_MODEL / 'dos_classifier.tflite'
with open(tflite_path, "wb") as f:
    f.write(tflite_model)