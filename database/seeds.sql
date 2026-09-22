-- Deterministic V1 seed. IDs are stable so scenarios can reference them.

INSERT INTO machines (
    id, machine_code, name, station_type,
    manufacturer, model, criticality, commissioned_at
) VALUES
    ('11111111-0000-0000-0000-000000000001', 'M-001', 'Infeed Conveyor', 'infeed', 'NovaPack Systems', 'IC-200', 'medium', '2024-03-01'),
    ('11111111-0000-0000-0000-000000000002', 'M-002', 'Filler', 'filler', 'NovaPack Systems', 'FL-900', 'high', '2024-03-12'),
    ('11111111-0000-0000-0000-000000000003', 'M-003', 'Transfer Wheel', 'transfer', 'NovaPack Systems', 'TW-400', 'high', '2024-04-16'),
    ('11111111-0000-0000-0000-000000000004', 'M-004', 'Capper', 'capper', 'NovaPack Systems', 'CP-310', 'high', '2024-04-20'),
    ('11111111-0000-0000-0000-000000000005', 'M-005', 'Inspection Station', 'inspection', 'NovaPack Systems', 'IS-110', 'medium', '2024-05-02');

INSERT INTO people (
    id, employee_code, name, role, department, years_experience, email
) VALUES
    ('44444444-0000-0000-0000-000000000001', 'P-001', 'Sarah Chen', 'Process Engineer', 'Manufacturing Engineering', 7, 'sarah.chen@forgeiq.local'),
    ('44444444-0000-0000-0000-000000000002', 'P-002', 'Mark Patel', 'Maintenance Engineer', 'Maintenance', 11, 'mark.patel@forgeiq.local'),
    ('44444444-0000-0000-0000-000000000003', 'P-003', 'Rachel Wong', 'Controls Engineer', 'Controls', 6, 'rachel.wong@forgeiq.local'),
    ('44444444-0000-0000-0000-000000000004', 'P-004', 'Alex Morgan', 'Quality Engineer', 'Quality', 5, 'alex.morgan@forgeiq.local'),
    ('44444444-0000-0000-0000-000000000005', 'P-005', 'Daniel Kim', 'Engineering Manager', 'Manufacturing Engineering', 14, 'daniel.kim@forgeiq.local'),
    ('44444444-0000-0000-0000-000000000006', 'P-006', 'Priya Nair', 'Technician', 'Maintenance', 4, 'priya.nair@forgeiq.local'),
    ('44444444-0000-0000-0000-000000000007', 'P-007', 'James Okonkwo', 'Manufacturing Engineer', 'Manufacturing Engineering', 8, 'james.okonkwo@forgeiq.local'),
    ('44444444-0000-0000-0000-000000000008', 'P-008', 'Elena Rossi', 'Supplier Engineer', 'Procurement', 9, 'elena.rossi@forgeiq.local'),
    ('44444444-0000-0000-0000-000000000009', 'P-009', 'Tom Hughes', 'Quality Manager', 'Quality', 12, 'tom.hughes@forgeiq.local'),
    ('44444444-0000-0000-0000-000000000010', 'P-010', 'Maya Singh', 'Technician', 'Maintenance', 3, 'maya.singh@forgeiq.local');

INSERT INTO components (
    id, component_code, machine_id, name, component_type,
    part_number, revision, supplier_name, installed_at, metadata
) VALUES
    (
        '22222222-0000-0000-0000-000000000001',
        'COMP-001',
        '11111111-0000-0000-0000-000000000003',
        'Guide Rail Assembly',
        'guide_rail',
        'GR-400-18',
        'REV-D',
        'NovaPack Systems',
        '2026-08-21',
        '{"nominal_clearance_mm": 4.8, "allowed_min_mm": 4.5, "allowed_max_mm": 5.0}'::jsonb
    ),
    (
        '22222222-0000-0000-0000-000000000002',
        'COMP-002',
        '11111111-0000-0000-0000-000000000003',
        'Main Bearing',
        'bearing',
        'BR-400-09',
        'REV-B',
        'NovaPack Systems',
        '2026-01-15',
        '{}'::jsonb
    ),
    (
        '22222222-0000-0000-0000-000000000003',
        'COMP-003',
        '11111111-0000-0000-0000-000000000003',
        'Servo Motor',
        'motor',
        'SM-400-22',
        'REV-C',
        'NovaPack Systems',
        '2025-11-02',
        '{}'::jsonb
    ),
    (
        '22222222-0000-0000-0000-000000000004',
        'COMP-004',
        '11111111-0000-0000-0000-000000000003',
        'Position Encoder',
        'encoder',
        'EN-400-05',
        'REV-A',
        'NovaPack Systems',
        '2025-11-02',
        '{}'::jsonb
    ),
    (
        '22222222-0000-0000-0000-000000000005',
        'COMP-005',
        '11111111-0000-0000-0000-000000000003',
        'Pressure Sensor Array',
        'pressure_sensor',
        'PS-400-11',
        'REV-B',
        'NovaPack Systems',
        '2026-03-08',
        '{}'::jsonb
    );

INSERT INTO sensors (
    id, sensor_code, machine_id, component_id, sensor_type, unit,
    baseline_mean, baseline_std, min_operating_value, max_operating_value, metadata
) VALUES
    (
        '33333333-0000-0000-0000-000000000001',
        'S-001',
        '11111111-0000-0000-0000-000000000003',
        '22222222-0000-0000-0000-000000000005',
        'pressure_x',
        'N',
        12.0, 0.35, 8.0, 22.0,
        '{"last_calibrated_at": "2026-07-14", "calibration_interval_days": 60, "health_score": 0.71}'::jsonb
    ),
    (
        '33333333-0000-0000-0000-000000000002',
        'S-002',
        '11111111-0000-0000-0000-000000000003',
        '22222222-0000-0000-0000-000000000005',
        'pressure_y',
        'N',
        8.0, 0.25, 5.0, 16.0,
        '{"last_calibrated_at": "2026-08-20", "calibration_interval_days": 60, "health_score": 0.92}'::jsonb
    ),
    (
        '33333333-0000-0000-0000-000000000003',
        'S-003',
        '11111111-0000-0000-0000-000000000003',
        '22222222-0000-0000-0000-000000000002',
        'vibration',
        'mm/s',
        0.55, 0.025, 0.2, 2.0,
        '{}'::jsonb
    ),
    (
        '33333333-0000-0000-0000-000000000004',
        'S-004',
        '11111111-0000-0000-0000-000000000003',
        '22222222-0000-0000-0000-000000000004',
        'velocity',
        'm/s',
        1.8, 0.02, 0.5, 3.0,
        '{}'::jsonb
    ),
    (
        '33333333-0000-0000-0000-000000000005',
        'S-005',
        '11111111-0000-0000-0000-000000000003',
        '22222222-0000-0000-0000-000000000003',
        'temperature',
        '°C',
        24.5, 0.05, 15.0, 80.0,
        '{}'::jsonb
    ),
    (
        '33333333-0000-0000-0000-000000000006',
        'S-006',
        '11111111-0000-0000-0000-000000000003',
        '22222222-0000-0000-0000-000000000003',
        'motor_current',
        'A',
        9.5, 0.15, 4.0, 20.0,
        '{}'::jsonb
    ),
    (
        '33333333-0000-0000-0000-000000000007',
        'S-007',
        '11111111-0000-0000-0000-000000000003',
        '22222222-0000-0000-0000-000000000003',
        'line_speed',
        'units/min',
        100.0, 1.5, 40.0, 140.0,
        '{}'::jsonb
    );

INSERT INTO production_runs (
    id, run_code, started_at, ended_at, product_type,
    container_format, target_line_speed, status
) VALUES
    (
        '77777777-0000-0000-0000-000000000001',
        'RUN-0001',
        '2026-02-18T08:00:00Z',
        '2026-02-18T12:00:00Z',
        '10mL-vial',
        'glass-vial',
        100,
        'completed'
    );

INSERT INTO documents (
    id, document_code, title, document_type, current_revision, content
) VALUES
    (
        '55555555-0000-0000-0000-000000000042',
        'ENG-042',
        'Transfer Wheel Guide Rail Specification',
        'engineering_standard',
        'REV-D',
        'For 10 mL glass vial production, the guide rail clearance should be maintained between 4.5 mm and 5.0 mm. Clearances below 4.5 mm may result in elevated lateral contact forces, increased container instability, and accelerated component wear. After adjustment, operators should verify pressure patterns during the first production cycle.'
    ),
    (
        '55555555-0000-0000-0000-000000000022',
        'MAINT-022',
        'Pressure Sensor Calibration Procedure',
        'maintenance_manual',
        'REV-B',
        'A pressure increase affecting one sensor without corresponding changes in velocity, motor current, vibration, or adjacent sensors may indicate sensor calibration drift rather than a physical process fault. Calibrate pressure sensors on a 60-day interval.'
    ),
    (
        '55555555-0000-0000-0000-000000000017',
        'INC-0017-RPT',
        'Elevated Lateral Pressure at Transfer Wheel 2',
        'incident_report',
        'REV-A',
        'Elevated lateral pressure detected at Transfer Wheel 2. Root cause: guide rail clearance configured at 4.2 mm. Resolution: clearance restored to 4.8 mm. Observed result: average lateral pressure decreased by 34%.'
    );

INSERT INTO document_revisions (
    id, document_id, revision, effective_at, content, changed_by, change_summary
) VALUES
    (
        '55555555-1111-0000-0000-000000000001',
        '55555555-0000-0000-0000-000000000042',
        'REV-A',
        '2024-06-01T00:00:00Z',
        'Guide clearance for 10 mL vial operation shall remain between 4.8 mm and 5.2 mm.',
        '44444444-0000-0000-0000-000000000005',
        'Initial specification.'
    ),
    (
        '55555555-1111-0000-0000-000000000002',
        '55555555-0000-0000-0000-000000000042',
        'REV-B',
        '2025-01-15T00:00:00Z',
        'Guide clearance for 10 mL vial operation shall remain between 4.6 mm and 5.1 mm.',
        '44444444-0000-0000-0000-000000000001',
        'Tightened range after line-speed increase.'
    ),
    (
        '55555555-1111-0000-0000-000000000003',
        '55555555-0000-0000-0000-000000000042',
        'REV-C',
        '2025-08-20T00:00:00Z',
        'Guide clearance for 10 mL vial operation shall remain between 4.5 mm and 5.0 mm.',
        '44444444-0000-0000-0000-000000000001',
        'Updated after container instability review.'
    ),
    (
        '55555555-1111-0000-0000-000000000004',
        '55555555-0000-0000-0000-000000000042',
        'REV-D',
        '2026-03-04T00:00:00Z',
        'For 10 mL glass vial production, the guide rail clearance should be maintained between 4.5 mm and 5.0 mm. Clearances below 4.5 mm may result in elevated lateral contact forces, increased container instability, and accelerated component wear. After adjustment, operators should verify pressure patterns during the first production cycle.',
        '44444444-0000-0000-0000-000000000001',
        'Added post-adjustment pressure verification.'
    );

INSERT INTO maintenance_events (
    id, maintenance_code, machine_id, component_id, started_at, completed_at,
    maintenance_type, performed_by, parameter_name, old_value, new_value, notes
) VALUES
    (
        '88888888-0000-0000-0000-000000000184',
        'MNT-0184',
        '11111111-0000-0000-0000-000000000003',
        '22222222-0000-0000-0000-000000000001',
        '2026-02-18T10:02:00Z',
        '2026-02-18T10:16:00Z',
        'adjustment',
        '44444444-0000-0000-0000-000000000002',
        'guide_clearance_mm',
        4.8,
        4.2,
        'Guide rail repositioned after reported bottle instability.'
    ),
    (
        '88888888-0000-0000-0000-000000000185',
        'MNT-0185',
        '11111111-0000-0000-0000-000000000003',
        '22222222-0000-0000-0000-000000000001',
        '2026-02-18T11:10:00Z',
        '2026-02-18T11:28:00Z',
        'adjustment',
        '44444444-0000-0000-0000-000000000002',
        'guide_clearance_mm',
        4.2,
        4.8,
        'Clearance restored after elevated lateral pressure.'
    );

INSERT INTO incidents (
    id, incident_code, machine_id, production_run_id, detected_at, resolved_at,
    incident_type, severity, status, actual_root_cause,
    root_cause_component_id, resolution
) VALUES
    (
        '66666666-0000-0000-0000-000000000017',
        'INC-0017',
        '11111111-0000-0000-0000-000000000003',
        '77777777-0000-0000-0000-000000000001',
        '2026-02-18T10:35:00Z',
        '2026-02-18T11:44:00Z',
        'abnormal_pressure',
        'high',
        'resolved',
        'guide_rail_misalignment',
        '22222222-0000-0000-0000-000000000001',
        'Guide rail clearance restored to 4.8 mm. Average lateral pressure decreased by 34%.'
    );

INSERT INTO relationships (
    id, source_type, source_id, relationship_type, target_type, target_id, weight, occurred_at
) VALUES
    (
        '99999999-0000-0000-0000-000000000001',
        'person', '44444444-0000-0000-0000-000000000001',
        'WORKED_ON',
        'machine', '11111111-0000-0000-0000-000000000003',
        1.0, '2025-08-20T00:00:00Z'
    ),
    (
        '99999999-0000-0000-0000-000000000002',
        'person', '44444444-0000-0000-0000-000000000001',
        'RESOLVED',
        'incident', '66666666-0000-0000-0000-000000000017',
        1.0, '2026-02-18T11:44:00Z'
    ),
    (
        '99999999-0000-0000-0000-000000000003',
        'person', '44444444-0000-0000-0000-000000000001',
        'AUTHORED',
        'document', '55555555-0000-0000-0000-000000000042',
        1.0, '2026-03-04T00:00:00Z'
    ),
    (
        '99999999-0000-0000-0000-000000000004',
        'person', '44444444-0000-0000-0000-000000000002',
        'MAINTAINED',
        'component', '22222222-0000-0000-0000-000000000001',
        1.0, '2026-02-18T10:16:00Z'
    ),
    (
        '99999999-0000-0000-0000-000000000005',
        'person', '44444444-0000-0000-0000-000000000003',
        'AUTHORED',
        'document', '55555555-0000-0000-0000-000000000022',
        1.0, '2025-09-12T00:00:00Z'
    );
