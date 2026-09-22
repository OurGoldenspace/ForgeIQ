import unittest
from datetime import datetime, timezone

import pandas as pd

from simulator.ingest import build_telemetry_rows, maintenance_window


ORIGIN = datetime(2026, 9, 21, 14, 0, tzinfo=timezone.utc)


def _frame():
    return pd.DataFrame(
        [
            {
                "second": 0,
                "scenario_id": "guide_rail_misalignment",
                "production_active": True,
                "maintenance_active": False,
                "pressure_x": 12.0,
                "pressure_y": 8.0,
                "vibration": 0.55,
                "velocity": 1.8,
                "temperature": 24.5,
                "motor_current": 9.5,
                "line_speed": 100.0,
                "physical_fault": None,
                "physical_fault_severity": 0.0,
                "sensor_fault": None,
                "guide_clearance_mm": 4.8,
                "_true_pressure_x": 12.1,
                "_true_pressure_y": 8.1,
            },
            {
                "second": 300,
                "scenario_id": "guide_rail_misalignment",
                "production_active": False,
                "maintenance_active": True,
                "pressure_x": 12.0,
                "pressure_y": 8.0,
                "vibration": 0.55,
                "velocity": 1.8,
                "temperature": 24.5,
                "motor_current": 9.5,
                "line_speed": 100.0,
                "physical_fault": None,
                "physical_fault_severity": 0.0,
                "sensor_fault": None,
                "guide_clearance_mm": 4.8,
                "_true_pressure_x": 12.1,
                "_true_pressure_y": 8.1,
            },
            {
                "second": 420,
                "scenario_id": "guide_rail_misalignment",
                "production_active": False,
                "maintenance_active": True,
                "pressure_x": 12.0,
                "pressure_y": 8.0,
                "vibration": 0.55,
                "velocity": 1.8,
                "temperature": 24.5,
                "motor_current": 9.5,
                "line_speed": 100.0,
                "physical_fault": None,
                "physical_fault_severity": 0.0,
                "sensor_fault": None,
                "guide_clearance_mm": 4.1,
                "_true_pressure_x": 12.1,
                "_true_pressure_y": 8.1,
            },
            {
                "second": 480,
                "scenario_id": "guide_rail_misalignment",
                "production_active": True,
                "maintenance_active": False,
                "pressure_x": 12.0,
                "pressure_y": 8.0,
                "vibration": 0.55,
                "velocity": 1.8,
                "temperature": 24.5,
                "motor_current": 9.5,
                "line_speed": 100.0,
                "physical_fault": None,
                "physical_fault_severity": 0.0,
                "sensor_fault": None,
                "guide_clearance_mm": 4.1,
                "_true_pressure_x": 12.1,
                "_true_pressure_y": 8.1,
            },
            {
                "second": 600,
                "scenario_id": "guide_rail_misalignment",
                "production_active": True,
                "maintenance_active": False,
                "pressure_x": 13.5,
                "pressure_y": 8.4,
                "vibration": 0.57,
                "velocity": 1.79,
                "temperature": 24.5,
                "motor_current": 9.6,
                "line_speed": 100.0,
                "physical_fault": "guide_rail_misalignment",
                "physical_fault_severity": 0.1,
                "sensor_fault": None,
                "guide_clearance_mm": 4.1,
                "_true_pressure_x": 13.4,
                "_true_pressure_y": 8.3,
            },
        ]
    )


class IngestMappingTests(unittest.TestCase):

    def test_observed_rows_keep_ground_truth_in_metadata(self):
        rows = build_telemetry_rows(
            _frame(),
            machine_id="machine",
            run_id="run",
            origin=ORIGIN,
        )
        first = rows[0]
        last = rows[-1]

        self.assertEqual(first[10], "production")
        self.assertFalse(first[12])
        self.assertIsNone(first[13])
        metadata = first[15].obj
        self.assertEqual(metadata["true_pressure_x"], 12.1)

        self.assertEqual(rows[1][10], "maintenance")
        self.assertTrue(last[12])
        self.assertEqual(last[13], "guide_rail_misalignment")
        self.assertNotIn("_true_pressure_x", last[15].obj)

    def test_maintenance_window_from_telemetry(self):
        window = maintenance_window(_frame())
        self.assertEqual(window["start"], 300)
        self.assertEqual(window["completed"], 480)
        self.assertEqual(window["old_value"], 4.8)
        self.assertEqual(window["new_value"], 4.1)


if __name__ == "__main__":
    unittest.main()
