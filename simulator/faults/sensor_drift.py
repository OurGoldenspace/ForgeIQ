from simulator.state import MachineState


def apply_sensor_drift(
    state: MachineState,
    sensor_name: str,
    severity: float,
    max_bias: float,
) -> MachineState:

    severity = max(0.0, min(1.0, severity))

    state.sensor_biases[sensor_name] = severity * max_bias

    return state
