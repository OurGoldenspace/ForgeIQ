from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from simulator.state import MachineState
from simulator.signals import update_physical_signals
from simulator.events import parse_events
from simulator.faults.guide_rail import apply_guide_rail_fault
from simulator.faults.sensor_drift import apply_sensor_drift


class ManufacturingSimulator:
    def __init__(self, scenario_path: str):

        scenario_path = Path(scenario_path)

        with scenario_path.open("r") as file:
            self.config = yaml.safe_load(file)

        self.scenario_id = self.config["id"]
        self.seed = self.config.get("seed", 42)

        self.duration = int(
            self.config.get("duration_seconds", 1200)
        )

        self.sample_rate = int(
            self.config.get("sample_rate_hz", 1)
        )

        self.rng = np.random.default_rng(self.seed)

        baseline = self.config.get("baseline", {})

        self.state = MachineState(
            line_speed=float(
                baseline.get("line_speed", 100)
            ),
            ambient_temperature=float(
                baseline.get("ambient_temperature", 22)
            ),
            guide_clearance_mm=float(
                baseline.get("guide_clearance_mm", 4.8)
            ),
        )

        self.events = parse_events(
            self.config.get("events", [])
        )

        self.active_physical_fault = None
        self.active_sensor_fault = None

        self.event_log = []

    def _log_event(self, second: int, message: str):
        event = {
            "second": second,
            "scenario_id": self.scenario_id,
            "message": message,
        }

        self.event_log.append(event)

        print(
            f"[{second:04d}s] {message}"
        )

    def _process_event(self, event, second):

        if event.type == "operating_change":

            parameter = event.params["parameter"]
            value = event.params["value"]

            setattr(
                self.state,
                parameter,
                float(value),
            )

            self._log_event(
                second,
                f"{parameter} changed to {value}",
            )

        elif event.type == "maintenance_start":

            self.state.maintenance_active = True
            self.state.production_active = False

            self._log_event(
                second,
                "Maintenance started",
            )

        elif event.type == "maintenance_complete":

            self.state.maintenance_active = False
            self.state.production_active = True

            self._log_event(
                second,
                "Maintenance completed; production resumed",
            )

        elif event.type == "parameter_change":

            parameter = event.params["parameter"]

            old_value = getattr(
                self.state,
                parameter,
                event.params.get("old_value"),
            )

            new_value = float(
                event.params["new_value"]
            )

            setattr(
                self.state,
                parameter,
                new_value,
            )

            self._log_event(
                second,
                f"{parameter}: {old_value} -> {new_value}",
            )

        elif event.type == "physical_fault_start":

            self.active_physical_fault = {
                **event.params,
                "start_time": second,
            }

            self._log_event(
                second,
                f"Physical fault started: "
                f"{event.params['fault']}",
            )

        elif event.type == "sensor_fault_start":

            self.active_sensor_fault = {
                **event.params,
                "start_time": second,
            }

            self._log_event(
                second,
                f"Sensor fault started: "
                f"{event.params['fault']} "
                f"on {event.params['sensor']}",
            )

    @staticmethod
    def _severity(
        current_time: int,
        start_time: int,
        ramp_seconds: int,
        max_severity: float,
    ) -> float:

        elapsed = max(
            0,
            current_time - start_time,
        )

        fraction = min(
            1.0,
            elapsed / ramp_seconds,
        )

        return fraction * max_severity

    def _apply_physical_faults(
        self,
        second: int,
    ):

        if not self.active_physical_fault:
            return

        fault = self.active_physical_fault

        severity = self._severity(
            second,
            fault["start_time"],
            int(fault.get("ramp_seconds", 300)),
            float(fault.get("max_severity", 1.0)),
        )

        if fault["fault"] == "guide_rail_misalignment":

            apply_guide_rail_fault(
                self.state,
                severity,
            )

    def _apply_sensor_faults(
        self,
        second: int,
    ):

        self.state.sensor_biases = {}

        if not self.active_sensor_fault:
            return

        fault = self.active_sensor_fault

        severity = self._severity(
            second,
            fault["start_time"],
            int(fault.get("ramp_seconds", 300)),
            1.0,
        )

        if fault["fault"] == "calibration_drift":

            apply_sensor_drift(
                self.state,
                sensor_name=fault["sensor"],
                severity=severity,
                max_bias=float(
                    fault.get("max_bias", 6.0)
                ),
            )

    def _measurement(
        self,
        name: str,
        true_value: float,
        sigma: float,
    ):

        bias = self.state.sensor_biases.get(
            name,
            0.0,
        )

        value = (
            true_value
            + bias
            + self.rng.normal(0, sigma)
        )

        # Rare measurement spike.
        if self.rng.random() < 0.002:
            value += self.rng.normal(
                0,
                sigma * 6,
            )

        return value

    def step(self, second: int):

        # Process events scheduled for this second.
        for event in self.events:
            if event.time == second:
                self._process_event(
                    event,
                    second,
                )

        # Physical dynamics first.
        if self.state.production_active:

            update_physical_signals(
                self.state,
                self.rng,
            )

            # Faults are a this-timestep overlay on unfaulted physics.
            # Restore the unfaulted values after the row is built so
            # the offset does not compound across seconds.
            unfaulted = (
                self.state.pressure_x,
                self.state.pressure_y,
                self.state.vibration,
                self.state.velocity,
                self.state.motor_current,
            )

            self._apply_physical_faults(
                second
            )

        # Sensors can fail even if physical machine is fine.
        self._apply_sensor_faults(
            second
        )

        physical_fault_name = None
        physical_fault_severity = 0.0

        if self.active_physical_fault:

            physical_fault_name = (
                self.active_physical_fault["fault"]
            )

            physical_fault_severity = (
                self._severity(
                    second,
                    self.active_physical_fault[
                        "start_time"
                    ],
                    int(
                        self.active_physical_fault.get(
                            "ramp_seconds",
                            300,
                        )
                    ),
                    float(
                        self.active_physical_fault.get(
                            "max_severity",
                            1.0,
                        )
                    ),
                )
            )

        sensor_fault_name = None

        if self.active_sensor_fault:
            sensor_fault_name = (
                self.active_sensor_fault["fault"]
            )

        row = {
            "second": second,
            "scenario_id": self.scenario_id,

            "production_active":
                self.state.production_active,

            "maintenance_active":
                self.state.maintenance_active,

            "line_speed":
                self._measurement(
                    "line_speed",
                    self.state.line_speed,
                    0.4,
                ),

            "pressure_x":
                self._measurement(
                    "pressure_x",
                    self.state.pressure_x,
                    0.20,
                ),

            "pressure_y":
                self._measurement(
                    "pressure_y",
                    self.state.pressure_y,
                    0.15,
                ),

            "vibration":
                self._measurement(
                    "vibration",
                    self.state.vibration,
                    0.015,
                ),

            "velocity":
                self._measurement(
                    "velocity",
                    self.state.velocity,
                    0.01,
                ),

            "temperature":
                self._measurement(
                    "temperature",
                    self.state.temperature,
                    0.03,
                ),

            "motor_current":
                self._measurement(
                    "motor_current",
                    self.state.motor_current,
                    0.08,
                ),

            # Evaluation-only fields.
            "physical_fault":
                physical_fault_name,

            "physical_fault_severity":
                physical_fault_severity,

            "sensor_fault":
                sensor_fault_name,

            "guide_clearance_mm":
                self.state.guide_clearance_mm,

            # Hidden physical truth, useful while debugging.
            "_true_pressure_x":
                self.state.pressure_x,

            "_true_pressure_y":
                self.state.pressure_y,
        }

        if self.state.production_active:
            (
                self.state.pressure_x,
                self.state.pressure_y,
                self.state.vibration,
                self.state.velocity,
                self.state.motor_current,
            ) = unfaulted

        return row

    def run(self):

        rows = []

        for second in range(
            0,
            self.duration,
            1 // self.sample_rate
            if self.sample_rate < 1
            else 1,
        ):
            rows.append(
                self.step(second)
            )

        return pd.DataFrame(rows)
