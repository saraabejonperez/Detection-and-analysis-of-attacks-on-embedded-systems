import argparse
import logging
import csv
import time
import sys
import joblib
import requests
import pandas as pd
import numpy as np
from nfstream import NFStreamer

parser = argparse.ArgumentParser()
parser.add_argument('--model', required=True)
parser.add_argument('--features', required=True)
parser.add_argument('--ip', required=True)
parser.add_argument('--webhook', required=True)
parser.add_argument('--log', required=True)
parser.add_argument('--results', required=True)
args = parser.parse_args()

logging.basicConfig(filename=args.log, level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

try:
    MODEL = joblib.load(args.model)
    FEATURES = list(np.load(args.features, allow_pickle=True))
except Exception as e:
    logging.error(f"Archivo de modelo o parámetros no encontrado: {e}")
    sys.exit(1)

with open(args.results, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "src_ip", "dst_ip", "score", "label", "latency"])

def preprocess_flow(flow) -> pd.DataFrame:
    values = [getattr(flow, feature, 0) for feature in FEATURES]
    return pd.DataFrame([values], columns=FEATURES)

def classify_flow(flow):
    try:
        start_time = time.time()
        X = preprocess_flow(flow)
        
        probabilities = MODEL.predict_proba(X)[0]
        prediction = probabilities[1] if len(probabilities) > 1 else probabilities[0]
        label = "DoS ATTACK" if prediction > 0.5 else "BENIGN"
        
        latency = time.time() - start_time
        
        with open(args.results, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([time.time(), flow.src_ip, flow.dst_ip, prediction, label, latency])
        
        if label == "DoS ATTACK":
            try:
                requests.post(args.webhook, json={"src": flow.src_ip, "score": float(prediction)}, timeout=1)
            except requests.exceptions.RequestException as e:
                logging.warning(f"No se pudo enviar alarma a la web: {e}")

    except Exception as e:
        logging.error(f"Error al clasificar flujo: {e}")

def main():
    logging.info("Iniciando captura con NFStream...")
    streamer = NFStreamer(source="eth0", statistical_analysis=True, idle_timeout=10, active_timeout=30)
    try:
        for flow in streamer:
            if flow.dst_ip == args.ip:
                classify_flow(flow)
    except Exception as e:
        logging.error(f"Error durante la clasificación: {e}")

if __name__ == "__main__":
    main()