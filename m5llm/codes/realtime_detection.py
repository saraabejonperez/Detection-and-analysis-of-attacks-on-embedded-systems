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

