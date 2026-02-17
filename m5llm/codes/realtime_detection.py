import numpy as np
import pandas as pd
from pathlib import Path
import time

import tflite_runtime.interpreter as tflite
from nfstream import NFStreamer


# =========== #
# =  PATHS  = #
# =========== #
BASE_PATH = Path("/home/Detection_M5LLM")
MODEL_PATH = BASE_PATH / "dos_classifier.tflite"
MEAN_PATH = BASE_PATH / "mean.npy"
SCALE_PATH = BASE_PATH / "scale.npy"
FEATURES_PATH = BASE_PATH / "features.npy"


# ============ #
# =  CONFIG  = #
# ============ #
interpreter = tflite.Interpreter(model_path=str(MODEL_PATH))
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

mean = np.load(MEAN_PATH).astype(np.float32)
scale = np.load(SCALE_PATH).astype(np.float32)
feature_names = list(np.load(FEATURES_PATH, allow_pickle=True))


# =============== #
# =  FUNCTIONS  = #
# =============== #
def preprocess_flow(flow) -> np.ndarray:
    values = []

    for feature in feature_names:
        if hasattr(flow, feature):
            value = getattr(flow, feature)
        else:
            value = 0
        values.append(value)

    X = np.array([values], dtype=np.float32)
    X = (X - mean) / scale

    return X


def classify_flow(flow) -> None:
    try:
        X = preprocess_flow(flow)

        interpreter.set_tensor(input_details[0]['index'], X)
        interpreter.invoke()

        prediction = interpreter.get_tensor(output_details[0]['index'])[0][0]
        label = "DoS ATTACK" if prediction > 0.5 else "BENIGN"

        print(f"[{time.strftime('%H:%M:%S')}] "
              f"{flow.src_ip}:{flow.src_port} -> {flow.dst_ip}:{flow.dst_port} "
              f"| Score: {prediction:.4f} | {label}")

    except Exception as e:
        print(f"[ERROR] No se pudo clasificar flujo: {e}")


def main() -> None:
    print("[INFO] Iniciando captura con NFStream...")
    
    streamer = NFStreamer(
        source="wlan0",
        statistical_analysis=True,
        idle_timeout=10,
        active_timeout=30
    )

    for flow in streamer:
        classify_flow(flow)


if __name__ == "__main__":
    main()