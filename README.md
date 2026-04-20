# CANInsight - Vehicle Diagnostics & Telemetry Intelligence System

CANInsight is a phase-1 automotive telemetry project that simulates vehicle CAN traffic, decodes raw payloads into signals, runs diagnostics, and presents the result in a dashboard.

This repository is the stable base version. It is designed to look and feel like a real automotive systems project, not a generic ML demo.

## Problem Statement

Modern vehicles exchange large volumes of ECU data over the CAN bus. Raw CAN frames are not useful on their own. They need to be decoded into engineering signals, analyzed for operational issues, and translated into insights that a human can act on.

CANInsight demonstrates that pipeline end to end.

## System Flow

```mermaid
flowchart LR
	A[Raw CAN CSV] --> B[Decoder]
	B --> C[Signal Extraction]
	C --> D[Analysis Engine]
	D --> E[Insight Engine]
	E --> F[Streamlit Dashboard]
```

## Core Working Principles

### 1. Raw CAN messages are parsed first

The project starts with CAN-like log rows that contain a timestamp, CAN ID, and an 8-byte hex payload.

Example payload:

```text
0E FE 18 00 76 00 00 00
```

The parser converts this hex string into actual bytes.

### 2. Bytes are mapped into vehicle signals

The decoder converts the raw payload into meaningful telemetry values.

Core mapping in [src/decoder.py](src/decoder.py):

```python
rpm_raw = _u16(data_bytes[0], data_bytes[1])
rpm = rpm_raw * 0.25
throttle_pct = data_bytes[2] / 255 * 100
speed_kph = data_bytes[3]
engine_temp_c = data_bytes[4] - 40
brake_pct = data_bytes[5] / 255 * 100
```

This is the signal extraction step: raw CAN bytes become engineering signals that can be analyzed.

### 3. Signals are evaluated by rule-based diagnostics

The analysis engine looks for operational patterns and anomalies:

- overheating
- RPM spikes
- harsh braking
- aggressive acceleration
- sudden signal jumps

The logic is event-based rather than sample-by-sample noise.

Example logic in [src/analysis.py](src/analysis.py):

```python
alerts.extend(detect_overheating(df))
alerts.extend(detect_rpm_spikes(df))
alerts.extend(detect_harsh_braking(df))
alerts.extend(detect_aggressive_acceleration(df))
alerts.extend(detect_signal_jumps(df))
```

Each detector produces structured alerts with severity, category, timestamp, and message.

### 4. Alerts are converted into user-friendly insights

The insight layer turns alerts into human-readable outputs:

- risk level
- headline summary
- priority findings
- recommended actions

Example logic in [src/insights.py](src/insights.py):

```python
risk_level = _risk_level_from_score(metrics.driving_score)
priority_findings = _build_priority_findings(alerts, metrics)
recommendations = _build_recommendations(metrics)
```

This makes the project feel like a real diagnostics product rather than a script that only prints alerts.

### 5. The dashboard presents the whole story

The Streamlit app shows:

- telemetry charts
- trip score
- max speed / RPM / temperature
- alerts table
- insight summary
- recommended actions

This is the operator-facing layer.

## Key Modules

- [data/generate_can_data.py](data/generate_can_data.py) generates synthetic CAN logs.
- [src/decoder.py](src/decoder.py) parses payloads and performs signal extraction.
- [src/analysis.py](src/analysis.py) runs event-based diagnostics and computes trip metrics.
- [src/insights.py](src/insights.py) converts alerts into findings and recommendations.
- [src/pipeline.py](src/pipeline.py) exports decoded CSVs from raw logs.
- [app/dashboard.py](app/dashboard.py) displays the full diagnostics experience.

## Why the Project Works

1. It follows a realistic automotive data flow.
2. It separates decoding, analysis, and insight generation into clean modules.
3. It uses structured outputs instead of one-off print statements.
4. It is easy to explain in interviews because each layer has a clear purpose.
5. It is visually presentable and demo-ready.

## Project Structure

```text
.
├── app/
│   ├── __init__.py
│   └── dashboard.py
├── data/
│   ├── can_simulated_day1.csv
│   └── generate_can_data.py
├── src/
│   ├── __init__.py
│   ├── analysis.py
│   ├── decoder.py
│   ├── insights.py
│   └── pipeline.py
├── requirements.txt
└── README.md
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the dashboard

```bash
streamlit run app/dashboard.py
```

### 3. Regenerate the sample dataset

```bash
python data/generate_can_data.py --rows 1200 --seed 42 --out data/can_simulated_day1.csv
```

### 4. Export decoded signals

```bash
python -m src.pipeline --in data/can_simulated_day1.csv --out data/can_decoded_day2.csv
```

## Phase 1 Scope

This repo intentionally focuses on the core diagnostics layer:

- CAN parsing
- signal extraction
- diagnostics logic
- insight generation
- dashboard presentation

Phase 2 can extend this foundation with Kafka streaming, deeper anomaly detection, and more production-style ingestion.

## Deployment Note

For Streamlit Community Cloud, the entry point is:

```text
app/dashboard.py
```

Live app: [https://caninsight.streamlit.app](https://caninsight.streamlit.app)

## Summary

CANInsight simulates real-world vehicle CAN communication, decodes raw payloads, applies diagnostics logic, and builds an intelligent dashboard for vehicle telemetry insights.

It shows practical understanding of:

- automotive communication systems
- data decoding pipelines
- event-based analysis
- insight generation
- dashboard-driven product presentation

## Future Extensions

- Kafka-based streaming ingestion
- ML-based anomaly detection
- DBC/config-driven decoding
- stronger unit test coverage
- cloud deployment with persistent demo data
