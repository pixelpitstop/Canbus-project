"""Convert alerts into plain-English insights."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import List

from src.analysis import Alert, TripMetrics


@dataclass
class InsightReport:
    risk_level: str
    headline: str
    summary_lines: List[str]
    priority_findings: List[str]
    recommendations: List[str]


def _risk_level_from_score(score: int) -> str:
    if score >= 80:
        return "Low"
    if score >= 60:
        return "Moderate"
    if score >= 40:
        return "Elevated"
    return "High"


def _build_priority_findings(alerts: List[Alert], metrics: TripMetrics) -> List[str]:
    findings: List[str] = []

    if metrics.overheating_events > 0:
        findings.append("Engine thermal stress detected. Cooling behavior should be reviewed first.")

    if metrics.rpm_spike_events > 0:
        findings.append("RPM transients indicate abrupt torque demand or unstable control input.")

    if metrics.harsh_braking_events + metrics.aggressive_accel_events >= 20:
        findings.append("Driving dynamics are consistently aggressive, impacting efficiency and comfort.")

    anomaly_count = sum(1 for a in alerts if a.category == "anomaly")
    if anomaly_count > 0:
        findings.append("Signal jump anomalies observed; sensor noise or rapid transients should be validated.")

    if not findings:
        findings.append("No critical control or health findings in this trip window.")

    return findings


def _build_recommendations(metrics: TripMetrics) -> List[str]:
    recommendations: List[str] = []

    if metrics.overheating_events > 0:
        recommendations.append("Inspect cooling loop and fan strategy; verify sustained high-load operation limits.")

    if metrics.rpm_spike_events > 0:
        recommendations.append("Review throttle mapping and shift behavior to reduce abrupt RPM excursions.")

    if metrics.harsh_braking_events > 0:
        recommendations.append("Coach smoother deceleration and increase anticipation distance to reduce harsh braking.")

    if metrics.aggressive_accel_events > 0:
        recommendations.append("Apply progressive throttle control to improve efficiency and drivetrain smoothness.")

    if metrics.anomaly_events > 0:
        recommendations.append("Run signal quality checks for CAN decoding and validate outlier sensor traces.")

    if not recommendations:
        recommendations.append("Maintain current calibration and monitor over longer drive cycles.")

    return recommendations


def generate_insight_report(alerts: List[Alert], metrics: TripMetrics) -> InsightReport:
    risk_level = _risk_level_from_score(metrics.driving_score)
    category_counts = Counter(alert.category for alert in alerts)

    headline = (
        f"Trip risk is {risk_level.lower()} with score {metrics.driving_score}/100. "
        f"Detected {len(alerts)} events across engine health, behavior, and anomaly checks."
    )

    summary_lines = [
        (
            f"Trip summary: duration {metrics.duration_s:.1f}s | max speed {metrics.max_speed_kph:.1f} kph | "
            f"max RPM {metrics.max_rpm:.0f} | max temp {metrics.max_engine_temp_c:.1f}C."
        ),
        (
            f"Event counts: engine health {category_counts.get('engine_health', 0)}, "
            f"driving behavior {category_counts.get('driving_behavior', 0)}, "
            f"anomaly {category_counts.get('anomaly', 0)}."
        ),
    ]

    priority_findings = _build_priority_findings(alerts, metrics)
    recommendations = _build_recommendations(metrics)

    return InsightReport(
        risk_level=risk_level,
        headline=headline,
        summary_lines=summary_lines,
        priority_findings=priority_findings,
        recommendations=recommendations,
    )


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
        report = generate_insight_report(alerts, metrics)
        insight_lines.append(report.headline)
        insight_lines.append(
            f"Trip score: {metrics.driving_score}/100 | Harsh braking: {metrics.harsh_braking_events} | Aggressive acceleration: {metrics.aggressive_accel_events}."
        )

    if not insight_lines:
        insight_lines.append("Minor anomalies detected; continue monitoring across longer trips.")

    return insight_lines
