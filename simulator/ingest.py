import argparse
import math
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import psycopg
from psycopg.types.json import Jsonb


MACHINE_CODE = "M-003"
COMPONENT_CODE = "COMP-001"
TECHNICIAN_CODE = "P-002"
DEFAULT_ORIGIN = datetime(2026, 9, 21, 14, 0, tzinfo=timezone.utc)
NAMESPACE = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

OBSERVED_VIEW_SQL = """
CREATE OR REPLACE VIEW telemetry_observed AS
SELECT
    id,
    timestamp,
    machine_id,
    production_run_id,
    pressure_x,
    pressure_y,
    vibration,
    velocity,
    temperature,
    motor_current,
    line_speed,
    operating_mode,
    scenario_id
FROM telemetry;
"""


def _clean(value):
    if value is None or pd.isna(value):
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def _operating_mode(row) -> str:
    if bool(row["maintenance_active"]):
        return "maintenance"
    if bool(row["production_active"]):
        return "production"
    return "stopped"


def build_telemetry_rows(df: pd.DataFrame, machine_id, run_id, origin: datetime):
    rows = []

    for record in df.to_dict(orient="records"):
        physical_fault = _clean(record.get("physical_fault"))
        sensor_fault = _clean(record.get("sensor_fault"))
        severity = _clean(record.get("physical_fault_severity")) or 0.0
        fault_type = physical_fault or sensor_fault
        timestamp = origin + timedelta(seconds=int(record["second"]))

        metadata = {
            "true_pressure_x": float(record["_true_pressure_x"]),
            "true_pressure_y": float(record["_true_pressure_y"]),
            "guide_clearance_mm": float(record["guide_clearance_mm"]),
            "physical_fault": physical_fault,
            "sensor_fault": sensor_fault,
            "physical_fault_severity": float(severity),
        }

        rows.append(
            (
                timestamp,
                machine_id,
                run_id,
                float(record["pressure_x"]),
                float(record["pressure_y"]),
                float(record["vibration"]),
                float(record["velocity"]),
                float(record["temperature"]),
                float(record["motor_current"]),
                float(record["line_speed"]),
                _operating_mode(record),
                str(record["scenario_id"]),
                bool(fault_type),
                fault_type,
                float(severity) if fault_type else None,
                Jsonb(metadata),
            )
        )

    return rows


def maintenance_window(df: pd.DataFrame):
    if not df["maintenance_active"].any():
        return None

    start = int(df.loc[df["maintenance_active"], "second"].min())
    resumed = df[(df["second"] > start) & (~df["maintenance_active"])]
    completed = int(resumed["second"].iloc[0]) if len(resumed) else None

    clearance = df["guide_clearance_mm"]
    changed = df[clearance.ne(clearance.shift()) & (df["second"] > 0)]
    old_value = None
    new_value = None
    if len(changed):
        at = int(changed.iloc[0]["second"])
        previous = df[df["second"] < at]
        old_value = float(previous["guide_clearance_mm"].iloc[-1]) if len(previous) else None
        new_value = float(changed.iloc[0]["guide_clearance_mm"])

    return {
        "start": start,
        "completed": completed,
        "old_value": old_value,
        "new_value": new_value,
    }


def _lookup_id(cur, table: str, code_column: str, code: str):
    cur.execute(
        f"SELECT id FROM {table} WHERE {code_column} = %s",
        (code,),
    )
    row = cur.fetchone()
    if row is None:
        raise RuntimeError(f"{table} row not found for {code}")
    return row[0]


def ingest_file(conn, path: Path, origin: datetime, machine_code: str):
    df = pd.read_parquet(path)
    scenario_id = str(df["scenario_id"].iloc[0])
    started_at = origin
    ended_at = origin + timedelta(seconds=int(df["second"].max()))
    run_id = uuid.uuid5(NAMESPACE, f"production_run:{scenario_id}")
    run_code = f"RUN-{scenario_id}"

    with conn.cursor() as cur:
        machine_id = _lookup_id(cur, "machines", "machine_code", machine_code)

        cur.execute(
            "DELETE FROM telemetry WHERE scenario_id = %s",
            (scenario_id,),
        )
        cur.execute(
            "DELETE FROM maintenance_events WHERE metadata->>'scenario_id' = %s",
            (scenario_id,),
        )
        cur.execute(
            "DELETE FROM production_runs WHERE metadata->>'scenario_id' = %s",
            (scenario_id,),
        )

        cur.execute(
            """
            INSERT INTO production_runs (
                id, run_code, started_at, ended_at,
                product_type, container_format,
                target_line_speed, status, metadata
            ) VALUES (
                %s, %s, %s, %s,
                '10mL-vial', 'glass-vial',
                100, 'completed', %s
            )
            """,
            (
                run_id,
                run_code,
                started_at,
                ended_at,
                Jsonb({"scenario_id": scenario_id}),
            ),
        )

        window = maintenance_window(df)
        if window:
            component_id = _lookup_id(
                cur, "components", "component_code", COMPONENT_CODE
            )
            technician_id = _lookup_id(
                cur, "people", "employee_code", TECHNICIAN_CODE
            )
            maintenance_id = uuid.uuid5(
                NAMESPACE, f"maintenance:{scenario_id}"
            )
            completed_at = (
                origin + timedelta(seconds=window["completed"])
                if window["completed"] is not None
                else None
            )
            cur.execute(
                """
                INSERT INTO maintenance_events (
                    id, maintenance_code, machine_id, component_id,
                    started_at, completed_at, maintenance_type,
                    performed_by, parameter_name, old_value, new_value,
                    notes, metadata
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, 'adjustment',
                    %s, 'guide_clearance_mm', %s, %s,
                    %s, %s
                )
                """,
                (
                    maintenance_id,
                    f"MNT-{scenario_id}",
                    machine_id,
                    component_id,
                    origin + timedelta(seconds=window["start"]),
                    completed_at,
                    technician_id,
                    window["old_value"],
                    window["new_value"],
                    "Guide rail repositioned after reported bottle instability.",
                    Jsonb({"scenario_id": scenario_id}),
                ),
            )

        rows = build_telemetry_rows(df, machine_id, run_id, origin)
        cur.executemany(
            """
            INSERT INTO telemetry (
                timestamp, machine_id, production_run_id,
                pressure_x, pressure_y, vibration, velocity,
                temperature, motor_current, line_speed,
                operating_mode, scenario_id,
                fault_active, fault_type, fault_severity,
                metadata
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s, %s,
                %s
            )
            """,
            rows,
        )
        cur.execute(OBSERVED_VIEW_SQL)

    conn.commit()
    return scenario_id, len(df)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file",
        help="Single parquet file. Default: all telemetry parquet files.",
    )
    parser.add_argument(
        "--input-dir",
        default="data/generated",
    )
    parser.add_argument(
        "--database-url",
        default=os.environ.get(
            "DATABASE_URL",
            "postgresql://forgeiq:forgeiq@localhost:5433/forgeiq",
        ),
    )
    parser.add_argument(
        "--machine-code",
        default=MACHINE_CODE,
    )
    args = parser.parse_args()

    if args.file:
        files = [Path(args.file)]
    else:
        files = sorted(
            path
            for path in Path(args.input_dir).glob("*.parquet")
            if not path.name.endswith("_events.parquet")
        )

    if not files:
        raise SystemExit("No parquet files found. Run the simulator first.")

    with psycopg.connect(args.database_url) as conn:
        for path in files:
            scenario_id, rows = ingest_file(
                conn,
                path,
                DEFAULT_ORIGIN,
                args.machine_code,
            )
            print(f"Ingested {scenario_id}: {rows} rows from {path}")


if __name__ == "__main__":
    main()
