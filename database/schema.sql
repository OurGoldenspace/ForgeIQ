CREATE TABLE machines (
    id UUID PRIMARY KEY,
    machine_code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    station_type TEXT NOT NULL,

    manufacturer TEXT,
    model TEXT,

    criticality TEXT NOT NULL
        CHECK (criticality IN ('low', 'medium', 'high')),

    commissioned_at DATE,

    metadata JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE components (
    id UUID PRIMARY KEY,
    component_code TEXT UNIQUE NOT NULL,

    machine_id UUID NOT NULL
        REFERENCES machines(id),

    name TEXT NOT NULL,
    component_type TEXT NOT NULL,

    part_number TEXT,
    revision TEXT,

    supplier_name TEXT,

    installed_at TIMESTAMPTZ,

    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE sensors (
    id UUID PRIMARY KEY,
    sensor_code TEXT UNIQUE NOT NULL,

    machine_id UUID NOT NULL
        REFERENCES machines(id),

    component_id UUID
        REFERENCES components(id),

    sensor_type TEXT NOT NULL,
    unit TEXT NOT NULL,

    baseline_mean DOUBLE PRECISION,
    baseline_std DOUBLE PRECISION,

    min_operating_value DOUBLE PRECISION,
    max_operating_value DOUBLE PRECISION,

    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE production_runs (
    id UUID PRIMARY KEY,
    run_code TEXT UNIQUE NOT NULL,

    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,

    product_type TEXT NOT NULL,
    container_format TEXT,

    target_line_speed DOUBLE PRECISION,

    status TEXT NOT NULL,

    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE people (
    id UUID PRIMARY KEY,

    employee_code TEXT UNIQUE NOT NULL,

    name TEXT NOT NULL,
    role TEXT NOT NULL,
    department TEXT,

    years_experience INTEGER,

    email TEXT,

    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE telemetry (
    id BIGSERIAL PRIMARY KEY,

    timestamp TIMESTAMPTZ NOT NULL,

    machine_id UUID NOT NULL
        REFERENCES machines(id),

    production_run_id UUID
        REFERENCES production_runs(id),

    pressure_x DOUBLE PRECISION,
    pressure_y DOUBLE PRECISION,

    vibration DOUBLE PRECISION,
    velocity DOUBLE PRECISION,
    temperature DOUBLE PRECISION,

    motor_current DOUBLE PRECISION,
    line_speed DOUBLE PRECISION,

    operating_mode TEXT,

    scenario_id TEXT,

    fault_active BOOLEAN DEFAULT FALSE,

    fault_type TEXT,
    fault_severity DOUBLE PRECISION,

    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_telemetry_machine_time
ON telemetry(machine_id, timestamp DESC);

-- Application-facing telemetry. Ground truth stays on telemetry.metadata
-- and the fault_* columns for evaluation only.
CREATE VIEW telemetry_observed AS
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

CREATE TABLE maintenance_events (
    id UUID PRIMARY KEY,

    maintenance_code TEXT UNIQUE NOT NULL,

    machine_id UUID NOT NULL
        REFERENCES machines(id),

    component_id UUID
        REFERENCES components(id),

    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,

    maintenance_type TEXT NOT NULL,

    performed_by UUID REFERENCES people(id),

    parameter_name TEXT,

    old_value DOUBLE PRECISION,
    new_value DOUBLE PRECISION,

    notes TEXT,

    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE documents (
    id UUID PRIMARY KEY,

    document_code TEXT UNIQUE NOT NULL,

    title TEXT NOT NULL,

    document_type TEXT NOT NULL,

    current_revision TEXT,

    content TEXT NOT NULL,

    metadata JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE document_revisions (
    id UUID PRIMARY KEY,

    document_id UUID NOT NULL
        REFERENCES documents(id),

    revision TEXT NOT NULL,

    effective_at TIMESTAMPTZ,

    content TEXT NOT NULL,

    changed_by UUID REFERENCES people(id),

    change_summary TEXT,

    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE incidents (
    id UUID PRIMARY KEY,

    incident_code TEXT UNIQUE NOT NULL,

    machine_id UUID NOT NULL
        REFERENCES machines(id),

    production_run_id UUID
        REFERENCES production_runs(id),

    detected_at TIMESTAMPTZ NOT NULL,
    resolved_at TIMESTAMPTZ,

    incident_type TEXT NOT NULL,

    severity TEXT NOT NULL,

    status TEXT NOT NULL
        CHECK (
            status IN (
                'detected',
                'investigating',
                'review',
                'resolved'
            )
        ),

    -- Evaluation-only. Do not expose to the investigation agent.
    actual_root_cause TEXT,
    root_cause_component_id UUID REFERENCES components(id),

    resolution TEXT,

    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE relationships (
    id UUID PRIMARY KEY,

    source_type TEXT NOT NULL,
    source_id UUID NOT NULL,

    relationship_type TEXT NOT NULL,

    target_type TEXT NOT NULL,
    target_id UUID NOT NULL,

    weight DOUBLE PRECISION DEFAULT 1.0,

    occurred_at TIMESTAMPTZ,

    metadata JSONB DEFAULT '{}'::jsonb
);
