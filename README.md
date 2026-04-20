# CANInsight - Vehicle Diagnostics & Telemetry Intelligence System

CANInsight is a phase-1 automotive telemetry project that simulates vehicle CAN traffic, decodes raw payloads into signals, detects issues, and presents the result in a dashboard.

## What It Does

- Parses raw CAN-like logs.
- Decodes payload bytes into RPM, speed, throttle, engine temperature, and brake.
- Runs rule-based diagnostics for overheating, RPM spikes, harsh braking, acceleration bursts, and signal anomalies.
- Converts alerts into readable findings and recommendations.
- Visualizes the trip in a Streamlit dashboard.

## System Flow

CAN Data -> Decoder -> Signal Extraction -> Analysis -> Insights -> Dashboard

## Key Modules

- [data/generate_can_data.py](data/generate_can_data.py) generates synthetic CAN logs for demos.
- [src/decoder.py](src/decoder.py) parses and decodes raw payloads.
- [src/analysis.py](src/analysis.py) runs event-based diagnostics and computes trip metrics.
- [src/insights.py](src/insights.py) turns alerts into risk summaries, findings, and recommendations.
- [app/dashboard.py](app/dashboard.py) presents telemetry, risk, metrics, alerts, and actions.

## Project Structure

```
.
├── app/
│   └── dashboard.py
├── data/
│   ├── can_simulated_day1.csv
│   └── generate_can_data.py
├── src/
│   ├── analysis.py
│   ├── decoder.py
│   ├── insights.py
│   └── pipeline.py
├── requirements.txt
└── README.md
```

## Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the dashboard:

```bash
streamlit run app/dashboard.py
```

3. Optional: regenerate the demo dataset:

```bash
python data/generate_can_data.py --rows 1200 --seed 42 --out data/can_simulated_day1.csv
```

4. Optional: export decoded signals to CSV:

```bash
python -m src.pipeline --in data/can_simulated_day1.csv --out data/can_decoded_day2.csv
```

## Phase 1 Scope

This repository is the stable base version. Phase 2 can extend it with streaming, Kafka, and deeper anomaly detection without changing the core decoding and diagnostics layer.

## Why It Matters

This project shows end-to-end automotive data handling: raw message parsing, signal extraction, diagnostics logic, insight generation, and a polished operator-facing UI.