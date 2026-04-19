"""Rule-based analysis engine for CANInsight."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import pandas as pd


@dataclass
class Alert:
    timestamp: float
    severity: str
    category: str
    message: str


@dataclass
class TripMetrics:
    duration_s: float
    max_speed_kph: float
    max_rpm: float
    max_engine_temp_c: float
    harsh_braking_events: int
    aggressive_accel_events: int
    rpm_spike_events: int
    overheating_events: int
    anomaly_events: int
    driving_score: int


def _severity_from_ratio(ratio: float) -> str:
    if ratio >= 1.35:
        return "high"
    if ratio >= 1.1:
        return "medium"
    return "low"


def _apply_cooldown(df: pd.DataFrame, idxs: List[int], min_gap_s: float) -> List[int]:
    filtered: List[int] = []
    last_ts: float | None = None
    for idx in idxs:
        ts = float(df.loc[idx, "timestamp"])
        if last_ts is None or (ts - last_ts) >= min_gap_s:
            filtered.append(idx)
            last_ts = ts
    return filtered


def detect_overheating(df: pd.DataFrame, threshold_c: float = 110.0) -> List[Alert]:
    alerts: List[Alert] = []
    over_mask = df["engine_temp_c"] > threshold_c
    starts = df.index[over_mask & (~over_mask.shift(1, fill_value=False))]
    for idx in starts:
        row = df.loc[idx]
        severity = _severity_from_ratio(float(row["engine_temp_c"]) / threshold_c)
        alerts.append(
            Alert(
                timestamp=float(row["timestamp"]),
                severity=severity,
                category="engine_health",
                message=f"Engine temperature {row['engine_temp_c']:.1f}C exceeds {threshold_c:.1f}C",
            )
        )
    return alerts


def detect_rpm_spikes(df: pd.DataFrame, delta_threshold: float = 1200.0) -> List[Alert]:
    alerts: List[Alert] = []
    rpm_delta = df["rpm"].diff().abs()
    spike_idx = rpm_delta[rpm_delta > delta_threshold].index.tolist()
    spike_idx = _apply_cooldown(df, spike_idx, min_gap_s=2.5)

    for idx in spike_idx:
        row = df.loc[idx]
        delta = float(rpm_delta.loc[idx])
        severity = _severity_from_ratio(delta / delta_threshold)
        alerts.append(
            Alert(
                timestamp=float(row["timestamp"]),
                severity=severity,
                category="engine_health",
                message=f"Abnormal RPM spike detected (delta={delta:.0f})",
            )
        )
    return alerts


def detect_harsh_braking(df: pd.DataFrame, brake_threshold: float = 70.0, min_speed_kph: float = 20.0) -> List[Alert]:
    alerts: List[Alert] = []
    harsh_mask = (df["brake_pct"] > brake_threshold) & (df["speed_kph"] > min_speed_kph)
    starts = df.index[harsh_mask & (~harsh_mask.shift(1, fill_value=False))].tolist()
    starts = _apply_cooldown(df, starts, min_gap_s=2.0)
    for idx in starts:
        row = df.loc[idx]
        severity = _severity_from_ratio(float(row["brake_pct"]) / brake_threshold)
        alerts.append(
            Alert(
                timestamp=float(row["timestamp"]),
                severity=severity,
                category="driving_behavior",
                message=f"Harsh braking event ({row['brake_pct']:.1f}%)",
            )
        )
    return alerts


def detect_aggressive_acceleration(df: pd.DataFrame, accel_threshold_kph_s: float = 28.0) -> List[Alert]:
    alerts: List[Alert] = []
    dt = df["timestamp"].diff().replace(0, pd.NA)
    accel = df["speed_kph"].diff() / dt
    accel_mask = accel > accel_threshold_kph_s
    idxs = df.index[accel_mask & (~accel_mask.shift(1, fill_value=False))].tolist()
    idxs = _apply_cooldown(df, idxs, min_gap_s=2.0)

    for idx in idxs:
        row = df.loc[idx]
        acc_value = float(accel.loc[idx])
        severity = _severity_from_ratio(acc_value / accel_threshold_kph_s)
        alerts.append(
            Alert(
                timestamp=float(row["timestamp"]),
                severity=severity,
                category="driving_behavior",
                message=f"Aggressive acceleration detected ({acc_value:.1f} kph/s)",
            )
        )
    return alerts


def detect_signal_jumps(
    df: pd.DataFrame,
    speed_jump_kph: float = 25.0,
    throttle_jump_pct: float = 40.0,
    temp_jump_c: float = 10.0,
) -> List[Alert]:
    alerts: List[Alert] = []

    speed_delta = df["speed_kph"].diff().abs()
    throttle_delta = df["throttle_pct"].diff().abs()
    temp_delta = df["engine_temp_c"].diff().abs()

    idxs = df.index[
        (speed_delta > speed_jump_kph)
        | (throttle_delta > throttle_jump_pct)
        | (temp_delta > temp_jump_c)
    ]

    for idx in idxs:
        row = df.loc[idx]
        ratio = max(
            float(speed_delta.loc[idx] / speed_jump_kph) if pd.notna(speed_delta.loc[idx]) else 0.0,
            float(throttle_delta.loc[idx] / throttle_jump_pct) if pd.notna(throttle_delta.loc[idx]) else 0.0,
            float(temp_delta.loc[idx] / temp_jump_c) if pd.notna(temp_delta.loc[idx]) else 0.0,
        )
        severity = _severity_from_ratio(ratio)
        alerts.append(
            Alert(
                timestamp=float(row["timestamp"]),
                severity=severity,
                category="anomaly",
                message=(
                    "Sudden signal jump detected "
                    f"(dSpeed={float(speed_delta.loc[idx] or 0):.1f}, "
                    f"dThrottle={float(throttle_delta.loc[idx] or 0):.1f}, "
                    f"dTemp={float(temp_delta.loc[idx] or 0):.1f})"
                ),
            )
        )
    return alerts


def _compute_driving_score(
    harsh_braking_events: int,
    aggressive_accel_events: int,
    rpm_spike_events: int,
    overheating_events: int,
    anomaly_events: int,
) -> int:
    score = 100.0
    score -= min(40.0, harsh_braking_events * 1.2 + aggressive_accel_events * 1.0)
    score -= min(25.0, rpm_spike_events * 6.0)
    score -= min(20.0, anomaly_events * 5.0)
    score -= min(20.0, overheating_events * 10.0)
    return max(0, min(100, int(round(score))))


def run_analysis(df: pd.DataFrame) -> Tuple[List[Alert], TripMetrics]:
    alerts: List[Alert] = []
    alerts.extend(detect_overheating(df))
    alerts.extend(detect_rpm_spikes(df))
    alerts.extend(detect_harsh_braking(df))
    alerts.extend(detect_aggressive_acceleration(df))
    alerts.extend(detect_signal_jumps(df))
    alerts = sorted(alerts, key=lambda a: a.timestamp)

    harsh_braking_events = sum(1 for a in alerts if "Harsh braking" in a.message)
    aggressive_accel_events = sum(1 for a in alerts if "Aggressive acceleration" in a.message)
    rpm_spike_events = sum(1 for a in alerts if "RPM spike" in a.message)
    overheating_events = sum(1 for a in alerts if "Engine temperature" in a.message)
    anomaly_events = sum(1 for a in alerts if a.category == "anomaly")

    metrics = TripMetrics(
        duration_s=float(df["timestamp"].max() - df["timestamp"].min()),
        max_speed_kph=float(df["speed_kph"].max()),
        max_rpm=float(df["rpm"].max()),
        max_engine_temp_c=float(df["engine_temp_c"].max()),
        harsh_braking_events=harsh_braking_events,
        aggressive_accel_events=aggressive_accel_events,
        rpm_spike_events=rpm_spike_events,
        overheating_events=overheating_events,
        anomaly_events=anomaly_events,
        driving_score=_compute_driving_score(
            harsh_braking_events,
            aggressive_accel_events,
            rpm_spike_events,
            overheating_events,
            anomaly_events,
        ),
    )
    return alerts, metrics


def run_rule_based_analysis(df: pd.DataFrame) -> List[Alert]:
    alerts, _ = run_analysis(df)
    return alerts
