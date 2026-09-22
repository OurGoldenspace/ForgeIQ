import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from simulator.anomaly import rolling_zscore_detector
from simulator.engine import ManufacturingSimulator


ROOT = Path(__file__).resolve().parents[2]
SCENARIOS = ROOT / "simulator" / "scenarios"


def run_scenario(name: str):
    simulator = ManufacturingSimulator(SCENARIOS / f"{name}.yaml")
    with redirect_stdout(StringIO()):
        df = simulator.run()
    return rolling_zscore_detector(df)


class ScenarioTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.normal = run_scenario("normal")
        cls.guide_rail = run_scenario("guide_rail")
        cls.sensor_drift = run_scenario("sensor_drift")

    def test_runs_are_deterministic(self):
        again = run_scenario("guide_rail")
        self.assertTrue(
            self.guide_rail["pressure_x"].equals(again["pressure_x"])
        )

    def test_normal_has_no_ground_truth_fault(self):
        df = self.normal
        self.assertFalse(df["physical_fault"].notna().any())
        self.assertFalse(df["sensor_fault"].notna().any())
        self.assertFalse(df["pressure_x_anomaly"].any())

    def test_normal_speed_change_is_not_a_pressure_fault(self):
        df = self.normal
        after_change = df[df["second"] >= 900]
        self.assertFalse(after_change["pressure_x_anomaly"].any())
        self.assertGreater(after_change["line_speed"].mean(), 105)

    def test_guide_rail_raises_true_pressure(self):
        df = self.guide_rail
        before = df[df["second"].between(100, 250)]
        after = df[df["second"] >= 900]

        self.assertEqual(
            df.loc[df["second"] >= 600, "physical_fault"].iloc[0],
            "guide_rail_misalignment",
        )
        self.assertGreater(
            after["pressure_x"].mean(),
            before["pressure_x"].mean() + 3,
        )
        residual = (
            after["pressure_x"] - after["_true_pressure_x"]
        ).abs().mean()
        self.assertLess(residual, 0.5)

    def test_guide_rail_detector_flags_pressure_after_fault(self):
        df = self.guide_rail
        after_fault = df[df["second"] >= 600]
        self.assertTrue(after_fault["pressure_x_anomaly"].any())
        first = after_fault[after_fault["pressure_x_anomaly"]].iloc[0]
        self.assertGreaterEqual(int(first["second"]), 600)

    def test_sensor_drift_is_measurement_only(self):
        df = self.sensor_drift
        after = df[df["second"] >= 720]
        before = df[df["second"].between(100, 350)]

        self.assertEqual(
            df.loc[df["second"] >= 420, "sensor_fault"].iloc[0],
            "calibration_drift",
        )
        self.assertFalse(df["physical_fault"].notna().any())
        self.assertGreater(
            after["pressure_x"].mean(),
            before["pressure_x"].mean() + 3,
        )
        self.assertAlmostEqual(
            after["_true_pressure_x"].mean(),
            before["_true_pressure_x"].mean(),
            delta=0.5,
        )
        self.assertAlmostEqual(
            after["pressure_y"].mean(),
            before["pressure_y"].mean(),
            delta=0.5,
        )
        self.assertAlmostEqual(
            after["motor_current"].mean(),
            before["motor_current"].mean(),
            delta=0.5,
        )

    def test_sensor_drift_detector_flags_only_pressure_x(self):
        df = self.sensor_drift
        after = df[df["second"] >= 420]
        self.assertTrue(after["pressure_x_anomaly"].any())
        self.assertFalse(after["pressure_y_anomaly"].any())

    def test_fault_scenarios_do_not_look_like_normal(self):
        normal_px = self.normal["pressure_x_anomaly"].sum()
        rail_px = self.guide_rail["pressure_x_anomaly"].sum()
        drift_px = self.sensor_drift["pressure_x_anomaly"].sum()

        self.assertEqual(normal_px, 0)
        self.assertGreater(rail_px, 50)
        self.assertGreater(drift_px, 50)


if __name__ == "__main__":
    unittest.main()
