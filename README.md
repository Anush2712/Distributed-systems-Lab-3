# Lab-3
# Distributed Systems Lab 3 – Resilience Engineering

This project demonstrates the design and implementation of **resilient distributed systems** using Python microservices deployed on **Kubernetes**.  
It explores key resilience mechanisms: **Circuit Breaker**, **Retry with Backoff**, and **Chaos Engineering**.

---

## Project Overview

The goal of this lab is to understand how distributed applications can **withstand, recover from, and gracefully degrade** during partial failures.

### Key Objectives

- Implement and analyze **Circuit Breaker** and **Retry/Backoff** patterns in Python.
- Use **Chaos Engineering** to simulate backend failures.
- Observe system behavior under stress and analyze **resilience trade-offs**.
- Relate design decisions to **fault tolerance** and **high availability** principles.

---

## System Architecture

The application consists of two Python microservices:

1. **ClientService**
   - Sends HTTP requests to the backend.
   - Implements multiple modules:
     - `client_basic.py` – basic request handling
     - `client_resilient.py` – resilient client with circuit breaker and retry logic
     - `circuit_breaker.py` – circuit breaker implementation
     - `retry_logic.py` – retry with exponential backoff
     - `config.py` – configuration parameters for requests
   - Collects response latency, status codes, and error types.

2. **BackendService**
   - Responds with a simple JSON payload:
     ```json
     { "message": "Hello from Backend!" }
     ```
   - Randomly simulates latency and HTTP 500 errors for testing resilience.
   - Main script: `backend.py`

Both services are containerized using **Docker** and deployed on **Kubernetes** as separate Deployments.


## Installation

Before running locally or building Docker images, install the required dependencies.

Each service has its own `requirements.txt`.  
From the project root, run:

```bash
# Backend dependencies
cd Backend
pip install -r requirements.txt

# Client dependencies
cd ../Client
pip install -r requirements.txt

Docker Setup

Each service includes its own Dockerfile.

Example (BackendService):

FROM python:3.11
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5001
CMD ["python", "backend.py"]


Build images locally:

docker build -t backend-service ./Backend
docker build -t client-service ./Client

Kubernetes Deployment

Deployment files are located in the k8s/ directory.

Example (backend-deployment.yaml):

apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-deployment
  labels:
    app: backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
        - name: backend
          image: backend-service:latest
          ports:
            - containerPort: 5001


Apply all manifests:

kubectl apply -f k8s/


Check status:

kubectl get pods

Chaos Engineering

Chaos experiments are defined in the Chaos/ directory.
Example: backend_failure.json simulates backend pod failures to test system resilience.

Experiments
Part A – Baseline Setup

Deployed services without resilience mechanisms.

Measured response times and error propagation under simulated backend delays.

Part B – Resilience Patterns

Circuit Breaker: Implemented in circuit_breaker.py.

Retry with Backoff: Implemented in retry_logic.py.

Part C – Chaos Engineering

Terminated backend pod using Chaos experiment.

Verified that client continues operation and system recovers automatically.

Key Observations

Circuit Breaker prevented cascading failures.

Retry pattern improved reliability, at a slight cost of latency.

Chaos experiments validated graceful degradation and fault tolerance.

Project Structure
LAB-3/
├── Backend/
│   ├── backend.py
│   ├── Dockerfile
│   └── requirements.txt
├── Client/
│   ├── client_basic.py
│   ├── client_resilient.py
│   ├── circuit_breaker.py
│   ├── retry_logic.py
│   ├── config.py
│   ├── Dockerfile
│   └── requirements.txt
├── k8s/
│   ├── backend-deployment.yaml
│   └── client-deployment.yaml
└── Chaos/
    └── backend_failure.json

References

Python requests library: https://docs.python-requests.org/

Chaos Toolkit Documentation: https://chaostoolkit.org

License

This project is for academic purposes as part of the COMP Distributed Systems Lab 3 coursework at University College Dublin (UCD).

Author

Anush Choudhary
MSc Student, Computer Science
University College Dublin



