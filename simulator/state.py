from dataclasses import dataclass, field


@dataclass
class MachineState:
    # Operating configuration
    line_speed: float = 100.0
    guide_clearance_mm: float = 4.8
    ambient_temperature: float = 22.0

    # True physical signals
    pressure_x: float = 12.0
    pressure_y: float = 8.0
    vibration: float = 0.55
    velocity: float = 1.8
    temperature: float = 24.5
    motor_current: float = 9.5

    # Sensor problems are applied AFTER physical simulation.
    sensor_biases: dict[str, float] = field(default_factory=dict)

    # Physical fault severities.
    active_faults: dict[str, float] = field(default_factory=dict)

    production_active: bool = True
    maintenance_active: bool = False
