"""CAN message decoding and signal extraction utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import pandas as pd


@dataclass
class DecodedSignals:
    timestamp: float
    can_id: str
    speed_kph: float
    rpm: float
    throttle_pct: float
    engine_temp_c: float
    brake_pct: float


# Hardcoded mapping for demo-scale CANInsight prototype.
CAN_ID_MAPPING: Dict[str, str] = {
    "0x0CFF0500": "powertrain",
}

SIGNAL_COLUMNS = [
    "timestamp",
    "can_id",
    "speed_kph",
    "rpm",
    "throttle_pct",
    "engine_temp_c",
    "brake_pct",
]


def _u16(msb: int, lsb: int) -> int:
    """Convert two bytes to an unsigned 16-bit integer."""
    return (msb << 8) | lsb


def parse_data_hex(data_hex: str) -> bytes:
    """Convert CAN data like '0E FE 18 00 76 00 00 00' into 8 raw bytes."""
    parts = data_hex.strip().split()
    if len(parts) != 8:
        raise ValueError(f"Expected 8 hex bytes, got {len(parts)} in: {data_hex}")

    try:
        values = [int(part, 16) for part in parts]
    except ValueError as exc:
        raise ValueError(f"Invalid hex payload: {data_hex}") from exc

    return bytes(values)


def decode_message(timestamp: float, can_id: str, data_bytes: bytes) -> DecodedSignals:
    """Decode 8-byte CAN payload into meaningful vehicle signals.

    Byte mapping (demo):
    - byte[0:2] -> RPM (0.25 rpm resolution)
    - byte[2]   -> Throttle % (0-100)
    - byte[3]   -> Speed kph (0-250)
    - byte[4]   -> Engine temp C (offset by 40)
    - byte[5]   -> Brake % (0-100)
    """
    if len(data_bytes) != 8:
        raise ValueError(f"Expected 8 data bytes, got {len(data_bytes)}")

    rpm_raw = _u16(data_bytes[0], data_bytes[1])
    rpm = rpm_raw * 0.25
    throttle_pct = data_bytes[2] / 255 * 100
    speed_kph = data_bytes[3]
    engine_temp_c = data_bytes[4] - 40
    brake_pct = data_bytes[5] / 255 * 100

    return DecodedSignals(
        timestamp=timestamp,
        can_id=can_id,
        speed_kph=round(speed_kph, 2),
        rpm=round(rpm, 2),
        throttle_pct=round(throttle_pct, 2),
        engine_temp_c=round(engine_temp_c, 2),
        brake_pct=round(brake_pct, 2),
    )


def decode_dataframe(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Decode a raw CAN dataframe containing timestamp/can_id/data_hex columns."""
    required = {"timestamp", "can_id", "data_hex"}
    missing = required - set(df_raw.columns)
    if missing:
        missing_cols = ", ".join(sorted(missing))
        raise ValueError(f"Missing required CAN columns: {missing_cols}")

    decoded_rows = []
    for row in df_raw.itertuples(index=False):
        payload = parse_data_hex(str(row.data_hex))
        decoded = decode_message(
            timestamp=float(row.timestamp),
            can_id=str(row.can_id),
            data_bytes=payload,
        )
        decoded_rows.append(decoded.__dict__)

    return pd.DataFrame(decoded_rows, columns=SIGNAL_COLUMNS)
