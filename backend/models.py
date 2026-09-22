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
