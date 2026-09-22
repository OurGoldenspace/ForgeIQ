from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Machine(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    machine_code: str
    name: str
    station_type: str
    manufacturer: str | None = None
    model: str | None = None
    criticality: str


class TelemetryPoint(BaseModel):
    timestamp: datetime
    machine_id: UUID
    production_run_id: UUID | None = None
    pressure_x: float | None = None
    pressure_y: float | None = None
    vibration: float | None = None
    velocity: float | None = None
    temperature: float | None = None
    motor_current: float | None = None
    line_speed: float | None = None
    operating_mode: str | None = None
    scenario_id: str | None = None
    anomaly_detected: bool = False


class MaintenanceEvent(BaseModel):
    maintenance_code: str
    machine_id: UUID
    component_id: UUID | None = None
    started_at: datetime
    completed_at: datetime | None = None
    maintenance_type: str
    parameter_name: str | None = None
    old_value: float | None = None
    new_value: float | None = None
    notes: str | None = None
    scenario_id: str | None = Field(
        default=None,
        description="Present for scenario-generated events only.",
    )


class Incident(BaseModel):
    incident_code: str
    machine_id: UUID
    production_run_id: UUID | None = None
    detected_at: datetime
    resolved_at: datetime | None = None
    incident_type: str
    severity: str
    status: str
    resolution: str | None = None
    review_decision: str | None = None
    human_root_cause: str | None = None
    review_notes: str | None = None
    scenario_id: str | None = None


class Hypothesis(BaseModel):
    name: str
    score: float
    supporting: list[str]
    contradictory: list[str]
    recommended_checks: list[str]


class SimilarIncident(BaseModel):
    incident_code: str
    score: float
    reasons: list[str]
    resolution: str | None = None


class DocumentHit(BaseModel):
    document_code: str
    title: str
    document_type: str
    excerpt: str
    why: str


class ExpertRecommendation(BaseModel):
    name: str
    role: str
    reasons: list[str]


class Investigation(BaseModel):
    incident: Incident
    changes: list[MaintenanceEvent]
    similar: list[SimilarIncident]
    documents: list[DocumentHit]
    hypotheses: list[Hypothesis]
    expert: ExpertRecommendation | None = None


class ReviewRequest(BaseModel):
    decision: str
    root_cause: str | None = None
    notes: str | None = None


class ResolveRequest(BaseModel):
    resolution: str
