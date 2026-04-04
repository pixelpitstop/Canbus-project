# 🚗 Real-Time Vehicle Telemetry Pipeline (CAN Bus Simulation)

A scalable, event-driven data pipeline that simulates vehicle CAN Bus telemetry and processes high-frequency data streams in real time using Apache Kafka.

---

## 📖 Overview

This project aims to replicate how modern connected vehicles stream telemetry data (speed, RPM, temperature, etc.) into backend systems for real-time processing and analytics.

The system is designed as a **distributed streaming pipeline**, where data flows from simulated vehicle sensors -> Kafka -> backend services -> storage/API layers.

---

## ⚙️ Architecture

```
[ CAN Bus Simulator ]
        ↓
[ Kafka Producer ]
        ↓
[ Kafka Topic: vehicle.telemetry ]
        ↓
[ Kafka Consumer / Stream Processor ]
        ↓
[ Backend API + Processing Layer ]
        ↓
[ PostgreSQL (Planned) / Output ]
```

---

## 🚀 Features

- 📡 Simulated CAN Bus vehicle telemetry (speed, RPM, temperature)
- ⚡ Real-time streaming using Apache Kafka
- 🔁 Producer-Consumer architecture
- 🔍 Basic stream processing & transformation
- 🌐 REST API for exposing processed telemetry (in progress)
- 📊 Designed for scalability with partitioning & consumer groups

---

## 🛠️ Tech Stack

- **Languages:** Python / JavaScript (extendable to Java)
- **Streaming:** Apache Kafka
- **Backend:** Node.js / Express (Spring Boot planned)
- **Database:** PostgreSQL (planned)
- **Tools:** Docker (planned)

---

## 📂 Project Structure

```
vehicle-data-pipeline/
│
├── producer/
│   └── telemetry_producer.py
│
├── consumer/
│   └── telemetry_consumer.py
│
├── backend/
│   └── api_server.js
│
├── data/
│   └── sample_events.json
│
├── docker/
│   └── docker-compose.yml
│
└── README.md
```

---

## 🔄 Data Flow

1. Vehicle telemetry is simulated using a producer script
2. Data is published to Kafka topic `vehicle.telemetry`
3. Consumer reads and processes incoming events
4. Processed data is:
   - Logged
   - Stored (planned)
   - Exposed via API (planned)

---

## 📊 Sample Event

```json
{
  "vehicle_id": "Ather_450X_01",
  "speed": 62,
  "rpm": 3400,
  "temperature": 36.5,
  "timestamp": "2026-04-04T10:15:30Z"
}
```

---

## 🧠 Key Concepts Explored

- Event-driven architecture
- Real-time stream processing
- Kafka topics, partitions, and offsets
- Consumer groups and scalability
- Data pipeline reliability & latency optimization

---

## 🏗️ Roadmap

- [ ] Integrate PostgreSQL for persistent storage
- [ ] Add anomaly detection on telemetry streams
- [ ] Build Spring Boot microservices
- [ ] Dockerize the entire pipeline
- [ ] Deploy on cloud (AWS/GCP)
- [ ] Add dashboard for real-time visualization

---

## ▶️ Getting Started

### 1. Start Kafka (Docker recommended)

```bash
docker-compose up -d
```

### 2. Run Producer

```bash
python producer/telemetry_producer.py
```

### 3. Run Consumer

```bash
python consumer/telemetry_consumer.py
```

---

## 🎯 Motivation

Modern EV platforms rely heavily on real-time data pipelines to monitor vehicle performance, detect anomalies, and improve user experience.

This project is an attempt to understand and build such systems from scratch.

---

## 🤝 Contributions

Open to improvements, optimizations, and architectural suggestions!