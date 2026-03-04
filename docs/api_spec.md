# M5 REST API Specification
**Device:** M5Stack LLM630 Compute Kit  
**Purpose:** Remote management and control of the embedded DoS detection service.

### General Information
  - Protocol: HTTP
  - Data format: JSON
  - Default Port: 8000
  - Base URL: _http://<device_ip>:8000_
  - Content-Type: _application/json_

### Endpoints
- Health Check → _GET /health_    

Used to verify device availability and current status.  

**Response 200**  
```
{  
  "status": "ok",  
  "model_loaded": true/false,  
  "detecting": false,  
  "device_time": <timestamp>  
}  
```

**Possible Errors**  
|   CODE   |        TYPE       |
|----------|:-----------------:|
|    500   |   Internal error  |

- Load Model → _POST /load_model_  

Uploads a new .tflite model to the device.

**Request**
  - Content-Type: multipart/form-data
  - Form field: file → model file (.tflite)

**Response 200**
```
{
  "message": "Model loaded successfully",
  "model_name": <model_name>
  "input_shape": <model_shape>,
  "loaded_at": <timestamp>
}
```

**Possible Errors**
|   CODE   |            TYPE          |
|----------|:------------------------:|
|    400   |     Invalid file type    |
|    413   |       File too large     |
|    500   |   Model loading failure  |

- Start Detection → _POST /start_detection_  

Starts real-time traffic monitoring and inference.

**Request**
```
{
  "interface": <interface>,
  "confidence_threshold": <threshold>
}
```

**Response 200**
```
{
  "message": "Detection started",
  "interface": <interface>,
  "threshold": <threshold>
}
```

**Possible Errors**
|   CODE   |             TYPE             |
|----------|:----------------------------:|
|    400   |        No model loaded       |
|    409   |   Detection already running  |
|    500   |        Internal failure      |

- Stop Detection → _POST /stop_detection_  

Stops real-time monitoring.

**Response 200**
```
{
  "message": "Detection stopped"
}
```

**Possible Errors**
|   CODE   |           TYPE           |
|----------|:------------------------:|
|    409   |   Detection not running  |

- Status → _GET /status_  

Returns full device operational state.

**Response 200**
```
{
  "model_loaded": true/false,
  "model_name": <model_name>/None,
  "detecting": true/false,
  "interface": <interface>,
  "flows_processed": <flows>,
  "attacks_detected": <attacks>,
  "cpu_usage": <cpu>,
  "memory_usage": <memory>
}
```

- Get Alarms → _GET /alarms_  

Returns recent detected attack events.

**Response 200**
```
  {
    "timestamp": <timestamp>,
    "source_ip": <source_ip>,
    "destination_ip": <destination_ip>,
    "attack_type": "DoS",
    "confidence": <prediction>
  }
```

**Possible Errors**
|   CODE   |        TYPE        |
|----------|:------------------:|
|    500   |   Retrieval error  |

- Batch Prediction (Model Evaluation) → _POST /predict_batch_  

Used for offline evaluation with a dataset.

**Request**
- Content-Type: application/json
```
{
  "features": [
    [...],
    [...]
  ]
}
```

**Response 200**
```
{
  "predictions": <predictions>,
  "probabilities": <probabilities>,
  "inference_time_ms": <time>
}
```

**Possible Errors**
|   CODE   |              TYPE             |
|----------|:-----------------------------:|
|    400   |   Feature dimension mismatch  |
|    500   |         Inference error       |

### Error Format Standardization
All errors follow this format:
```
{
  "error": "Error description",
  "code": code_number
}
```
