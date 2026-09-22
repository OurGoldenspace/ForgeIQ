import uuid
from datetime import timedelta

from psycopg.types.json import Jsonb

from backend.models import (
    DocumentHit,
    ExpertRecommendation,
    Hypothesis,
    Incident,
    Investigation,
    MaintenanceEvent,
    SimilarIncident,
)


def _mean(rows, field):
    values = [row[field] for row in rows if row[field] is not None]
    if not values:
        return 0.0
    return sum(values) / len(values)


def _incident_row(conn, incident_code: str):
    row = conn.execute(
        """
        SELECT i.id, i.incident_code, i.machine_id, i.production_run_id,
               i.detected_at, i.resolved_at, i.incident_type, i.severity,
               i.status, i.resolution, i.review_decision, i.human_root_cause,
               i.review_notes, i.metadata->>'scenario_id' AS scenario_id
        FROM incidents i
        WHERE i.incident_code = %s
        """,
        (incident_code,),
    ).fetchone()
    return row


def get_incident(conn, incident_code: str) -> Incident | None:
    row = _incident_row(conn, incident_code)
    if row is None:
        return None
    return Incident.model_validate(row)


def list_incidents(conn, scenario_id: str | None) -> list[Incident]:
    if scenario_id:
        rows = conn.execute(
            """
            SELECT i.incident_code, i.machine_id, i.production_run_id,
                   i.detected_at, i.resolved_at, i.incident_type, i.severity,
                   i.status, i.resolution, i.review_decision, i.human_root_cause,
                   i.review_notes, i.metadata->>'scenario_id' AS scenario_id
            FROM incidents i
            WHERE i.metadata->>'scenario_id' = %s
            ORDER BY i.detected_at
            """,
            (scenario_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT i.incident_code, i.machine_id, i.production_run_id,
                   i.detected_at, i.resolved_at, i.incident_type, i.severity,
                   i.status, i.resolution, i.review_decision, i.human_root_cause,
                   i.review_notes, i.metadata->>'scenario_id' AS scenario_id
            FROM incidents i
            ORDER BY i.detected_at
            """
        ).fetchall()
    return [Incident.model_validate(row) for row in rows]


def _signal_profile(conn, incident):
    early = conn.execute(
        """
        SELECT pressure_x, pressure_y, vibration, velocity,
               motor_current, line_speed
        FROM telemetry_observed
        WHERE production_run_id = %s
          AND timestamp BETWEEN %s AND %s
        """,
        (
            incident.production_run_id,
            incident.detected_at - timedelta(minutes=8),
            incident.detected_at - timedelta(minutes=2),
        ),
    ).fetchall()
    late = conn.execute(
        """
        SELECT pressure_x, pressure_y, vibration, velocity,
               motor_current, line_speed
        FROM telemetry_observed
        WHERE production_run_id = %s
          AND timestamp BETWEEN %s AND %s
        """,
        (
            incident.production_run_id,
            incident.detected_at + timedelta(minutes=4),
            incident.detected_at + timedelta(minutes=10),
        ),
    ).fetchall()
    if not early or not late:
        early = conn.execute(
            """
            SELECT pressure_x, pressure_y, vibration, velocity,
                   motor_current, line_speed
            FROM telemetry_observed
            WHERE production_run_id = %s
            ORDER BY timestamp
            LIMIT 180
            """,
            (incident.production_run_id,),
        ).fetchall()
        late = conn.execute(
            """
            SELECT pressure_x, pressure_y, vibration, velocity,
                   motor_current, line_speed
            FROM telemetry_observed
            WHERE production_run_id = %s
            ORDER BY timestamp DESC
            LIMIT 180
            """,
            (incident.production_run_id,),
        ).fetchall()

    return {
        name: _mean(late, name) - _mean(early, name)
        for name in (
            "pressure_x",
            "pressure_y",
            "vibration",
            "velocity",
            "motor_current",
            "line_speed",
        )
    }


def _recent_changes(conn, incident):
    return conn.execute(
        """
        SELECT maintenance_code, machine_id, component_id,
               started_at, completed_at, maintenance_type,
               parameter_name, old_value, new_value, notes,
               metadata->>'scenario_id' AS scenario_id
        FROM maintenance_events
        WHERE machine_id = %s
          AND metadata->>'scenario_id' IS NOT DISTINCT FROM %s
          AND started_at BETWEEN %s AND %s
        ORDER BY started_at
        """,
        (
            incident.machine_id,
            incident.scenario_id,
            incident.detected_at - timedelta(hours=1),
            incident.detected_at + timedelta(minutes=5),
        ),
    ).fetchall()


def _hypotheses(delta, changes) -> list[Hypothesis]:
    isolated = (
        delta["pressure_x"] > 2
        and abs(delta["pressure_y"]) < 0.8
        and abs(delta["vibration"]) < 0.15
        and abs(delta["motor_current"]) < 0.6
    )
    mechanical = delta["pressure_x"] > 2 and delta["pressure_y"] > 0.8
    clearance_change = any(
        row["parameter_name"] == "guide_clearance_mm"
        and row["new_value"] is not None
        and row["new_value"] < 4.5
        for row in changes
    )
    speed_change = delta["line_speed"] > 5

    rail_score = 0.15
    if mechanical:
        rail_score = 0.62
    if mechanical and clearance_change:
        rail_score = 0.84
    if isolated:
        rail_score = 0.22

    drift_score = 0.18
    if isolated:
        drift_score = 0.81
    if mechanical:
        drift_score = 0.28

    speed_score = 0.31 if speed_change and not mechanical else 0.12

    return [
        Hypothesis(
            name="guide_rail_misalignment",
            score=rail_score,
            supporting=[
                item
                for item in [
                    f"pressure_x rose {delta['pressure_x']:.1f} N" if delta["pressure_x"] > 2 else None,
                    f"pressure_y also rose {delta['pressure_y']:.1f} N" if mechanical else None,
                    "guide clearance changed below 4.5 mm shortly before detection" if clearance_change else None,
                ]
                if item
            ],
            contradictory=[
                item
                for item in [
                    "Neighboring pressure and load signals stayed flat" if isolated else None,
                    "No recent guide-clearance change found"
                    if not clearance_change and not isolated
                    else None,
                ]
                if item
            ],
            recommended_checks=[
                "Verify guide rail clearance against ENG-042 (4.5–5.0 mm)",
                "Inspect Transfer Wheel contact pattern after the next cycle",
            ],
        ),
        Hypothesis(
            name="sensor_calibration_drift",
            score=drift_score,
            supporting=[
                item
                for item in [
                    "Only pressure_x is elevated" if isolated else None,
                    "Velocity, motor current, and vibration did not follow" if isolated else None,
                ]
                if item
            ],
            contradictory=[
                item
                for item in [
                    "pressure_y and mechanical load also moved" if mechanical else None,
                ]
                if item
            ],
            recommended_checks=[
                "Compare S-001 against adjacent pressure sensors",
                "Check calibration due date in MAINT-022",
            ],
        ),
        Hypothesis(
            name="increased_line_speed",
            score=speed_score,
            supporting=[
                item
                for item in [
                    f"line_speed increased by {delta['line_speed']:.1f}" if speed_change else None,
                ]
                if item
            ],
            contradictory=[
                item
                for item in [
                    "Speed change alone does not explain a large pressure_x shift"
                    if delta["pressure_x"] > 3
                    else None,
                ]
                if item
            ],
            recommended_checks=[
                "Confirm whether the speed change was an intended operating change",
            ],
        ),
    ]


def _similar(conn, incident, mechanical: bool) -> list[SimilarIncident]:
    rows = conn.execute(
        """
        SELECT incident_code, detected_at, incident_type, resolution, status
        FROM incidents
        WHERE incident_code <> %s
          AND machine_id = %s
          AND incident_type = %s
          AND status = 'resolved'
        ORDER BY detected_at DESC
        """,
        (incident.incident_code, incident.machine_id, incident.incident_type),
    ).fetchall()

    hits = []
    for row in rows:
        score = 0.61
        reasons = ["Same station and abnormal_pressure type"]
        if row["incident_code"] == "INC-0017" and mechanical:
            score = 0.91
            reasons.append("Similar lateral-pressure / guide-clearance story")
        elif row["incident_code"] == "INC-0017":
            score = 0.55
            reasons.append("Historical pressure incident; mechanical signature is weaker here")
        hits.append(
            SimilarIncident(
                incident_code=row["incident_code"],
                score=score,
                reasons=reasons,
                resolution=row["resolution"],
            )
        )
    return hits


def _documents(conn, isolated: bool, mechanical: bool) -> list[DocumentHit]:
    wanted = []
    if mechanical:
        wanted.append("ENG-042")
    if isolated:
        wanted.append("MAINT-022")
    if mechanical:
        wanted.append("INC-0017-RPT")
    if not wanted:
        wanted = ["MAINT-022", "ENG-042"]

    rows = conn.execute(
        """
        SELECT document_code, title, document_type, content
        FROM documents
        WHERE document_code = ANY(%s)
        """,
        (wanted,),
    ).fetchall()
    by_code = {row["document_code"]: row for row in rows}
    hits = []
    for code in wanted:
        row = by_code.get(code)
        if row is None:
            continue
        why = "Guide clearance limits for 10 mL vial production"
        if code == "MAINT-022":
            why = "Single-sensor rise without correlated load may be calibration drift"
        if code == "INC-0017-RPT":
            why = "Prior incident with the same station and pressure signature"
        hits.append(
            DocumentHit(
                document_code=row["document_code"],
                title=row["title"],
                document_type=row["document_type"],
                excerpt=row["content"][:280],
                why=why,
            )
        )
    return hits


def _expert(conn, incident, isolated: bool) -> ExpertRecommendation | None:
    rows = conn.execute(
        """
        SELECT p.name, p.role, r.relationship_type, r.target_type
        FROM relationships r
        JOIN people p ON p.id = r.source_id
        WHERE r.source_type = 'person'
          AND (
            (r.relationship_type = 'WORKED_ON' AND r.target_id = %s)
            OR (r.relationship_type = 'RESOLVED' AND r.target_type = 'incident')
            OR r.relationship_type = 'AUTHORED'
          )
        """,
        (incident.machine_id,),
    ).fetchall()
    if not rows:
        return None

    scores: dict[str, dict] = {}
    for row in rows:
        entry = scores.setdefault(
            row["name"],
            {"role": row["role"], "score": 0.0, "reasons": []},
        )
        if row["relationship_type"] == "RESOLVED":
            entry["score"] += 3
            entry["reasons"].append("Resolved a similar incident")
        elif row["relationship_type"] == "AUTHORED":
            if isolated and "Controls" in (row["role"] or ""):
                entry["score"] += 3
                entry["reasons"].append("Authored the pressure-sensor calibration procedure")
            else:
                entry["score"] += 2
                entry["reasons"].append("Authored a relevant engineering document")
        elif row["relationship_type"] == "WORKED_ON":
            entry["score"] += 2
            entry["reasons"].append("Worked on Transfer Wheel")

    name, entry = max(scores.items(), key=lambda item: item[1]["score"])
    return ExpertRecommendation(
        name=name,
        role=entry["role"],
        reasons=sorted(set(entry["reasons"])),
    )


def investigate(conn, incident_code: str) -> Investigation | None:
    incident = get_incident(conn, incident_code)
    if incident is None:
        return None

    delta = _signal_profile(conn, incident)
    change_rows = _recent_changes(conn, incident)
    isolated = (
        delta["pressure_x"] > 2
        and abs(delta["pressure_y"]) < 0.8
        and abs(delta["vibration"]) < 0.15
    )
    mechanical = delta["pressure_x"] > 2 and delta["pressure_y"] > 0.8
    hypotheses = sorted(
        _hypotheses(delta, change_rows),
        key=lambda item: item.score,
        reverse=True,
    )
    return Investigation(
        incident=incident,
        changes=[MaintenanceEvent.model_validate(row) for row in change_rows],
        similar=_similar(conn, incident, mechanical),
        documents=_documents(conn, isolated, mechanical),
        hypotheses=hypotheses,
        expert=_expert(conn, incident, isolated),
    )


def review_incident(conn, incident_code: str, decision: str, root_cause: str | None, notes: str | None):
    incident = get_incident(conn, incident_code)
    if incident is None:
        return None
    if incident.status == "resolved":
        raise ValueError("Resolved incidents cannot be reviewed again")

    chosen = root_cause
    if decision == "confirm" and not chosen:
        bundle = investigate(conn, incident_code)
        if bundle and bundle.hypotheses:
            chosen = bundle.hypotheses[0].name
    if decision == "reject":
        chosen = None

    conn.execute(
        """
        UPDATE incidents
        SET review_decision = %s,
            human_root_cause = %s,
            review_notes = %s,
            status = 'review'
        WHERE incident_code = %s
        """,
        (decision, chosen, notes, incident_code),
    )
    conn.commit()
    return get_incident(conn, incident_code)


def resolve_incident(conn, incident_code: str, resolution: str):
    incident = get_incident(conn, incident_code)
    if incident is None:
        return None
    if incident.review_decision not in {"confirm", "modify", "reject"}:
        raise ValueError("A human must confirm, modify, or reject before resolve")

    conn.execute(
        """
        UPDATE incidents
        SET resolution = %s,
            status = 'resolved',
            resolved_at = NOW()
        WHERE incident_code = %s
        """,
        (resolution, incident_code),
    )

    lesson_code = f"LL-{incident_code}"
    conn.execute(
        """
        INSERT INTO documents (
            id, document_code, title, document_type, current_revision, content, metadata
        ) VALUES (
            %s, %s, %s, 'lessons_learned', 'REV-A', %s, %s
        )
        ON CONFLICT (document_code) DO UPDATE
        SET content = EXCLUDED.content,
            metadata = EXCLUDED.metadata
        """,
        (
            uuid.uuid4(),
            lesson_code,
            f"Lesson learned from {incident_code}",
            (
                f"Incident {incident_code} was {incident.review_decision}ed. "
                f"Human root cause: {incident.human_root_cause or 'none'}. "
                f"Resolution: {resolution}"
            ),
            Jsonb({
                "scenario_id": incident.scenario_id,
                "incident_code": incident_code,
            }),
        ),
    )
    conn.commit()
    return get_incident(conn, incident_code)

