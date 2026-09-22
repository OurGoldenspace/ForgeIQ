import inspect
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from simulator.anomaly import rolling_zscore_detector
from simulator.engine import ManufacturingSimulator
from simulator.isolation_forest import isolation_forest_detector
from simulator import ingest


ROOT = Path(__file__).resolve().parents[2]
SCENARIOS = ROOT / "simulator" / "scenarios"


def run_both(name: str):
    simulator = ManufacturingSimulator(SCENARIOS / f"{name}.yaml")
    with redirect_stdout(StringIO()):
        df = simulator.run()
    zscored = rolling_zscore_detector(df)
    return isolation_forest_detector(zscored)


class IsolationForestComparisonTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.normal = run_both("normal")
        cls.guide_rail = run_both("guide_rail")
        cls.sensor_drift = run_both("sensor_drift")

    def test_does_not_replace_live_zscore_flags(self):
        df = self.guide_rail
        self.assertIn("pressure_x_anomaly", df.columns)
        self.assertIn("iforest_anomaly", df.columns)
        self.assertFalse(df["iforest_anomaly"].equals(df["pressure_x_anomaly"]))

    def test_normal_stays_quiet(self):
        df = self.normal
        self.assertFalse(df["pressure_x_anomaly"].any())
        self.assertFalse(df["iforest_anomaly"].any())

    def test_guide_rail_is_caught_after_fault(self):
        df = self.guide_rail
        after = df[df["second"] >= 600]
        self.assertTrue(after["pressure_x_anomaly"].any())
        self.assertTrue(after["iforest_anomaly"].any())
        first = after[after["iforest_anomaly"]].iloc[0]
        self.assertGreaterEqual(int(first["second"]), 600)

    def test_sensor_drift_is_caught_after_bias_starts(self):
        df = self.sensor_drift
        after = df[df["second"] >= 420]
        self.assertTrue(after["pressure_x_anomaly"].any())
        self.assertTrue(after["iforest_anomaly"].any())
        first = after[after["iforest_anomaly"]].iloc[0]
        self.assertGreaterEqual(int(first["second"]), 420)

    def test_speed_change_is_not_a_pressure_fault_for_either(self):
        df = self.normal
        after = df[df["second"] >= 900]
        self.assertFalse(after["pressure_x_anomaly"].any())
        self.assertFalse(after["iforest_anomaly"].any())

    def test_ingest_still_keys_off_rolling_z(self):
        source = inspect.getsource(ingest)
        self.assertIn("pressure_x_anomaly", source)
        self.assertNotIn("iforest", source)


if __name__ == "__main__":
    unittest.main()
