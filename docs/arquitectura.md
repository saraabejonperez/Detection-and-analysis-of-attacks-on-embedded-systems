# System Architecture Design  
The system is designed to detect network anomalies and DoS attacks (SYN Flood and ICMP Flood) using an embedded device running a machine learning model. The architecture separates the web management layer from the embedded detection layer to ensure modularity, scalability and maintainability.  

The system is composed of two main components:  
- Web Application (Docker + Flask)
- Embedded Detection Service running on the M5Stack LLM630 Compute Kit  

Both components communicate via REST API over a local network.

## Component Responsibilities
#### Web Application (Flask + Docker)
Responsibilities:
- Device registration and selection (dynamic IP handling)
- Model upload and management
- Model lifecycle management (archiving and deletion after 60 days)
- Trigger start/stop detection
- Display real-time alarms
- Execute batch model evaluation
- Generate metrics and confusion matrices
- Provide user interface

The web application does NOT perform real-time detection. It only orchestrates and manages the embedded system.

#### Embedded Detection Service (M5)
Responsibilities:
- Capture network traffic using NFStream
- Extract flow-based features
- Load and manage the ML model (.tflite)
- Perform real-time inference
- Generate attack alerts
- Expose REST API endpoints
- Provide system status information

The embedded system is fully autonomous once detection is started.

## Communication Model
The system uses REST over HTTP for communication between the web server and the M5 device.
Reasons for choosing REST:
- Platform independence
- Simplicity
- Easy debugging
- Clear separation of concerns
- Scalability for future expansion

No SSH or direct script execution is used. All interactions are performed via structured JSON messages.

## Design Decisions
**1. Separation of Concerns**  
The web application and embedded detection service are independent systems. This reduces coupling and improves maintainability.

**2. Device-Oriented Architecture**  
The M5 acts as a service provider exposing its functionality through an API, allowing future support for multiple devices.

**3. Model Portability**  
Models are uploaded dynamically to the embedded device, allowing model updates without firmware modification.

**4. Containerized Web Deployment**  
Docker is used to ensure reproducibility, simplify deployment and isolate dependencies.

## Scalability Considerations
The architecture allows:
- Adding multiple M5 devices
- Supporting different models
- Extending to other attack types

## Risks
|           RISK            |            MITIGATION           |
|---------------------------|:-------------------------------:|
|     Dynamic IP address    |    Device registration module   |
|    Network instability    |      Health-check endpoint      |
|   Model incompatibility   |     Validation before upload    |	
| Resource limitation in M5 |           Use of TFLite         |
