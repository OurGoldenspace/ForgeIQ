from simulator.state import MachineState


def apply_guide_rail_fault(
    state: MachineState,
    severity: float,
) -> MachineState:
    """
    Represents increasing contact forces caused by an
    incorrectly positioned guide rail.

    Severity must be between 0 and 1.
    """

    severity = max(0.0, min(1.0, severity))

    state.pressure_x += severity * 7.0
    state.pressure_y += severity * 2.5

    state.vibration += severity * 0.12

    state.motor_current += severity * 0.60

    state.velocity -= severity * 0.03

    state.active_faults["guide_rail_misalignment"] = severity

    return state
