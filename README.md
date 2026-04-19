# CANInsight - Vehicle Diagnostics & Telemetry Intelligence System

CANInsight is a mini onboard diagnostics and performance intelligence system built on simulated vehicle CAN data.

Simulates real-world vehicle CAN communication and builds an intelligent layer for diagnostics and performance insights.

## Problem

Modern vehicles generate large volumes of ECU communication through CAN messages. Raw CAN frames are not directly useful for engineers or drivers unless they are decoded, analyzed, and translated into actionable insights.

## Goal

Build an end-to-end CAN pipeline that:

1. Reads raw CAN-like logs.
2. Decodes payload bytes into vehicle signals.
3. Detects operational issues and behavior anomalies.
4. Surfaces plain-English diagnostics insights via a dashboard.

## System Architecture

CAN Data -> Decoder -> Signal Extraction -> Analysis Engine -> Insight Engine -> Dashboard

## Core Features

1. CAN Decoder
        - Input: CAN ID + 8-byte data payload.
        - Output: speed, RPM, throttle, engine temperature, brake.

2. Signal Extraction
        - Raw byte mapping to meaningful units.
        - Demo mapping in `src/decoder.py`:
          - byte[0:2] -> RPM
          - byte[2] -> throttle
          - byte[3] -> speed
          - byte[4] -> engine temperature
          - byte[5] -> brake

3. Analysis Engine
        - Engine health monitoring:
          - overheat detection
          - abnormal RPM spike detection
        - Driving behavior analysis:
          - aggressive acceleration
          - harsh braking
        - Rule-based anomaly detection for sudden jumps.

4. Insight Engine
        - Converts alerts into plain English summary lines for quick diagnostics interpretation.

5. Dashboard (Streamlit)
        - Speed vs time graph.
        - RPM vs time graph.
        - Alerts panel.
        - Insights panel.

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
│   └── insights.py
├── requirements.txt
└── README.md
```

## Day 1 Status

Completed:

1. CANInsight folder structure setup.
2. Synthetic CAN dataset generator.
3. Generated dataset (`data/can_simulated_day1.csv`, 1200 rows).
4. Initial decoder, analysis, insight, and dashboard starter modules.

## Day 2 Status

Completed:

1. Raw payload parser (`data_hex` -> 8 bytes).
2. Signal extraction pipeline (`decode_dataframe`) from raw CAN CSV.
3. Streamlit dashboard support for direct raw CAN decoding.
4. CLI decode pipeline to export signal-level CSV.

## Day 3 Status

Completed:

1. Event-based analysis engine with severity scoring.
2. Added anomaly detection for sudden signal jumps.
3. Added trip-level metrics (driving score, event counters, max operating values).
4. Dashboard now displays Day 3 trip metrics and upgraded alerts.

## Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Regenerate synthetic dataset:

```bash
python data/generate_can_data.py --rows 1200 --seed 42 --out data/can_simulated_day1.csv
```

3. Run dashboard:

```bash
streamlit run app/dashboard.py
```

4. Decode raw CAN CSV into a clean signal CSV:

```bash
python -m src.pipeline --in data/can_simulated_day1.csv --out data/can_decoded_day2.csv
```

## 1-Week Execution Plan

1. Day 1: CAN basics + dataset creation.
2. Day 2: decoder + signal extraction.
3. Day 3: analysis engine.
4. Day 4: insight engine.
5. Day 5: dashboard.
6. Day 6: polish, visuals, and demo flow.
7. Day 7: final README, screenshots, and demo video.

## Engineering Impact

This project demonstrates practical understanding of automotive telemetry workflows: CAN-style data ingestion, signal decoding, diagnostics logic, and operator-facing intelligence.