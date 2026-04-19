"""Generate synthetic CAN log CSV for Day 1 CANInsight development."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import random
from typing import List

import pandas as pd


@dataclass
class Row:
    timestamp: float
    can_id: str
    data_hex: str
    speed_kph: float
    rpm: float
    throttle_pct: float
    engine_temp_c: float
    brake_pct: float


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _encode_payload(rpm: float, throttle_pct: float, speed_kph: float, temp_c: float, brake_pct: float) -> str:
    rpm_raw = int(_clamp(rpm, 0, 16000) / 0.25)
    b0 = (rpm_raw >> 8) & 0xFF
    b1 = rpm_raw & 0xFF
    b2 = int(_clamp(throttle_pct, 0, 100) / 100 * 255)
    b3 = int(_clamp(speed_kph, 0, 250))
    b4 = int(_clamp(temp_c + 40, 0, 255))
    b5 = int(_clamp(brake_pct, 0, 100) / 100 * 255)
    b6 = 0
    b7 = 0
    return " ".join(f"{b:02X}" for b in [b0, b1, b2, b3, b4, b5, b6, b7])


def generate(rows: int, seed: int) -> List[Row]:
    random.seed(seed)

    speed = 0.0
    rpm = 850.0
    throttle = 8.0
    temp = 78.0
    brake = 0.0

    out: List[Row] = []

    for i in range(rows):
        t = i * 0.1

        throttle += random.uniform(-4, 5)
        throttle = _clamp(throttle, 0, 100)

        brake = random.uniform(0, 15)
        if random.random() < 0.04:
            brake = random.uniform(70, 100)

        speed += (throttle / 100) * 7 - (brake / 100) * 15 + random.uniform(-1, 1)
        speed = _clamp(speed, 0, 160)

        rpm_target = 900 + speed * 45 + throttle * 22
        rpm += (rpm_target - rpm) * 0.25 + random.uniform(-90, 90)
        rpm = _clamp(rpm, 700, 7000)

        temp += 0.02 * (rpm / 1000) - 0.015 * (speed / 100) + random.uniform(-0.2, 0.2)
        temp = _clamp(temp, 70, 125)

        # Inject occasional anomalies for analysis testing.
        if random.random() < 0.02:
            rpm = _clamp(rpm + random.uniform(1300, 2300), 700, 7000)
        if random.random() < 0.015:
            temp = _clamp(temp + random.uniform(8, 18), 70, 125)

        can_id = "0x0CFF0500"
        data_hex = _encode_payload(rpm, throttle, speed, temp, brake)

        out.append(
            Row(
                timestamp=round(t, 2),
                can_id=can_id,
                data_hex=data_hex,
                speed_kph=round(speed, 2),
                rpm=round(rpm, 2),
                throttle_pct=round(throttle, 2),
                engine_temp_c=round(temp, 2),
                brake_pct=round(brake, 2),
            )
        )

    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic CAN CSV dataset")
    parser.add_argument("--rows", type=int, default=1200, help="Number of rows")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--out", type=str, default="data/can_simulated_day1.csv", help="Output CSV path")
    args = parser.parse_args()

    rows = generate(rows=args.rows, seed=args.seed)
    df = pd.DataFrame(asdict(r) for r in rows)
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df)} rows to {args.out}")


if __name__ == "__main__":
    main()
