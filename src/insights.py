"""Convert alerts into plain-English insights."""

from __future__ import annotations

from collections import Counter
from typing import List

from src.analysis import Alert, TripMetrics


def generate_insights(alerts: List[Alert], metrics: TripMetrics | None = None) -> List[str]:
    if not alerts:
        if metrics is None:
            return ["No major issues detected in this session. Vehicle behavior appears stable."]
        return [
            "No major issues detected in this session. Vehicle behavior appears stable.",
            f"Trip summary: max speed {metrics.max_speed_kph:.1f} kph, max RPM {metrics.max_rpm:.0f}, max temp {metrics.max_engine_temp_c:.1f}C.",
        ]

    category_counts = Counter(alert.category for alert in alerts)
    insight_lines = []

    if category_counts.get("engine_health", 0) > 0:
        insight_lines.append("Engine health warnings detected. Check cooling and load patterns.")

    if category_counts.get("driving_behavior", 0) >= 3:
        insight_lines.append("Frequent aggressive driving patterns detected, which may reduce efficiency.")

    if category_counts.get("driving_behavior", 0) > 0:
        insight_lines.append("Braking and acceleration behavior suggests opportunities for smoother control.")

    if category_counts.get("anomaly", 0) > 0:
        insight_lines.append("Signal consistency anomalies were detected; review sensor integrity and transient events.")

    if metrics is not None:
        insight_lines.append(
            f"Trip score: {metrics.driving_score}/100 | Harsh braking: {metrics.harsh_braking_events} | Aggressive acceleration: {metrics.aggressive_accel_events}."
        )

    if not insight_lines:
        insight_lines.append("Minor anomalies detected; continue monitoring across longer trips.")

    return insight_lines
