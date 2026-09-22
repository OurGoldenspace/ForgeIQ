from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from psycopg import Connection

from backend.db import get_connection
from backend.investigation import (
    get_incident,
    investigate,
    list_incidents,
    resolve_incident,
    review_incident,
)
from backend.models import (
    Incident,
    Investigation,
    Machine,
    MaintenanceEvent,
    ResolveRequest,
    ReviewRequest,
    TelemetryPoint,
)
from backend import queries


app = FastAPI(title="ForgeIQ", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

Db = Annotated[Connection, Depends(get_connection)]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/machines", response_model=list[Machine])
def machines(conn: Db):
    return queries.list_machines(conn)


@app.get("/telemetry", response_model=list[TelemetryPoint])
def telemetry(
    conn: Db,
    scenario_id: str = Query(...),
    limit: int = Query(1200, ge=1, le=5000),
):
    return queries.list_telemetry(conn, scenario_id, limit)


@app.get("/maintenance", response_model=list[MaintenanceEvent])
def maintenance(
    conn: Db,
    scenario_id: str | None = None,
):
    return queries.list_maintenance(conn, scenario_id)


@app.get("/incidents", response_model=list[Incident])
def incidents(conn: Db, scenario_id: str | None = None):
    return list_incidents(conn, scenario_id)


@app.get("/incidents/{incident_code}", response_model=Incident)
def incident_detail(incident_code: str, conn: Db):
    incident = get_incident(conn, incident_code)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@app.get("/incidents/{incident_code}/investigation", response_model=Investigation)
def incident_investigation(incident_code: str, conn: Db):
    bundle = investigate(conn, incident_code)
    if bundle is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return bundle


@app.post("/incidents/{incident_code}/review", response_model=Incident)
def incident_review(incident_code: str, body: ReviewRequest, conn: Db):
    if body.decision not in {"confirm", "reject", "modify"}:
        raise HTTPException(status_code=400, detail="decision must be confirm, reject, or modify")
    try:
        incident = review_incident(
            conn,
            incident_code,
            body.decision,
            body.root_cause,
            body.notes,
        )
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@app.post("/incidents/{incident_code}/resolve", response_model=Incident)
def incident_resolve(incident_code: str, body: ResolveRequest, conn: Db):
    try:
        incident = resolve_incident(conn, incident_code, body.resolution)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident
