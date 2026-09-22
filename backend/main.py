from typing import Annotated

from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from psycopg import Connection

from backend.db import get_connection
from backend.models import Machine, MaintenanceEvent, TelemetryPoint
from backend import queries


app = FastAPI(title="ForgeIQ", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET"],
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
