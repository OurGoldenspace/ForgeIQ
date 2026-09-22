from backend.models import Machine, MaintenanceEvent, TelemetryPoint


def list_machines(conn) -> list[Machine]:
    rows = conn.execute(
        """
        SELECT id, machine_code, name, station_type,
               manufacturer, model, criticality
        FROM machines
        ORDER BY machine_code
        """
    ).fetchall()
    return [Machine.model_validate(row) for row in rows]


def list_telemetry(conn, scenario_id: str, limit: int) -> list[TelemetryPoint]:
    rows = conn.execute(
        """
        SELECT timestamp, machine_id, production_run_id,
               pressure_x, pressure_y, vibration, velocity,
               temperature, motor_current, line_speed,
               operating_mode, scenario_id, anomaly_detected
        FROM telemetry_observed
        WHERE scenario_id = %s
        ORDER BY timestamp
        LIMIT %s
        """,
        (scenario_id, limit),
    ).fetchall()
    return [TelemetryPoint.model_validate(row) for row in rows]


def list_maintenance(conn, scenario_id: str | None) -> list[MaintenanceEvent]:
    if scenario_id:
        rows = conn.execute(
            """
            SELECT maintenance_code, machine_id, component_id,
                   started_at, completed_at, maintenance_type,
                   parameter_name, old_value, new_value, notes,
                   metadata->>'scenario_id' AS scenario_id
            FROM maintenance_events
            WHERE metadata->>'scenario_id' = %s
            ORDER BY started_at
            """,
            (scenario_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT maintenance_code, machine_id, component_id,
                   started_at, completed_at, maintenance_type,
                   parameter_name, old_value, new_value, notes,
                   metadata->>'scenario_id' AS scenario_id
            FROM maintenance_events
            ORDER BY started_at
            """
        ).fetchall()
    return [MaintenanceEvent.model_validate(row) for row in rows]
