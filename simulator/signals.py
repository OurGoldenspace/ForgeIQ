import numpy as np
from simulator.state import MachineState


def smooth(previous: float, target: float, alpha: float, noise: float, rng):
    """
    Autocorrelated signal:
        x_t = alpha*x_(t-1) + (1-alpha)*target + noise
    """
    return (
        alpha * previous
        + (1 - alpha) * target
        + rng.normal(0, noise)
    )


def update_physical_signals(
    state: MachineState,
    rng: np.random.Generator,
) -> MachineState:

    # Line speed changes relatively slowly.
    speed_target = state.line_speed

    # Normal physical relationships.
    pressure_x_target = (
        12.0
        + 0.06 * (speed_target - 100.0)
    )

    pressure_y_target = (
        8.0
        + 0.035 * (speed_target - 100.0)
    )

    vibration_target = (
        0.40
        + 0.0015 * speed_target
    )

    velocity_target = (
        1.8 * (speed_target / 100.0)
    )

    motor_current_target = (
        7.0
        + 0.025 * speed_target
    )

    # Temperature changes slowly based on motor load.
    heating = 0.0008 * state.motor_current
    cooling = 0.003 * (
        state.temperature - state.ambient_temperature
    )

    state.temperature += (
        heating
        - cooling
        + rng.normal(0, 0.01)
    )

    state.pressure_x = smooth(
        state.pressure_x,
        pressure_x_target,
        alpha=0.85,
        noise=0.12,
        rng=rng,
    )

    state.pressure_y = smooth(
        state.pressure_y,
        pressure_y_target,
        alpha=0.85,
        noise=0.08,
        rng=rng,
    )

    state.vibration = smooth(
        state.vibration,
        vibration_target,
        alpha=0.90,
        noise=0.008,
        rng=rng,
    )

    state.velocity = smooth(
        state.velocity,
        velocity_target,
        alpha=0.85,
        noise=0.008,
        rng=rng,
    )

    state.motor_current = smooth(
        state.motor_current,
        motor_current_target,
        alpha=0.90,
        noise=0.05,
        rng=rng,
    )

    return state
