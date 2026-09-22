ALTER TABLE telemetry
ADD COLUMN IF NOT EXISTS anomaly_detected BOOLEAN DEFAULT FALSE;

ALTER TABLE incidents
ADD COLUMN IF NOT EXISTS review_decision TEXT;

ALTER TABLE incidents
ADD COLUMN IF NOT EXISTS human_root_cause TEXT;

ALTER TABLE incidents
ADD COLUMN IF NOT EXISTS review_notes TEXT;

DROP VIEW IF EXISTS telemetry_observed;

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
    scenario_id,
    anomaly_detected
FROM telemetry;
