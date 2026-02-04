import pandas as pd
from pathlib import Path


# =========== #
# =  RUTAS  = #
# =========== #
PATH_DATA = Path(__file__).resolve().parent.parent / 'data'
PATH_BENIGN = PATH_DATA / 'BenignTraffic'
PATH_DOS = PATH_DATA / 'DenialofService'


# ============== #
# =  DATASETS  = #
# ============== #
# Cargar archivo con columnas a filtrar
with open(PATH_DATA / 'palabras.txt', 'r', encoding='utf-8') as f:
    columns_no_gen = [linea.strip() for linea in f if linea.strip()]


# Obtener todos los csv de la carpeta BenignTraffic
benign_df = [pd.read_csv(f) for f in list(PATH_BENIGN.glob('*.csv'))]
# Crear único DataFrame
benign_df = pd.concat(benign_df, ignore_index=True)
benign_df["label"] = (benign_df["label"].replace("BENIGN", 0).astype("Int64"))


# Obtener todos los csv de la carpeta DenialofService (y subcarpetas)
attack_df = [pd.read_csv(f) for f in list(PATH_DOS.rglob('*.csv'))]
# Crear único DataFrame
attack_df = pd.concat(attack_df, ignore_index=True)


# Unión de los csv
traffic_df = pd.concat([benign_df, attack_df], ignore_index=True)
# Eliminar columnas que no generalizan
traffic_df.drop(columns=columns_no_gen)
# Filtrado de datos (filas que sean 100% NaN)
traffic_df = traffic_df.dropna(axis=0, how='all')
# Filtrado de datos (columnas que sean 100% NaN)
traffic_df = traffic_df.dropna(axis=1, how='all')





# Mezcla de los datos
traffic_df = traffic_df.sample(frac=1).reset_index(drop=True)


'''
División train-test
Validación K-Fold Cross Validation -> https://deepnote.com/app/a_mas/Cross-Validation-en-Python-685fa851-b5b2-4c5b-b5fb-3dc5ae64838f
'''