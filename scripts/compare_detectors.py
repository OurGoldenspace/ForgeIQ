"""Compare lagged rolling Z-score with Isolation Forest on the three runs.

Isolation Forest is a notebook/script comparison only. Ingest still writes
rolling-Z flags.
"""

import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulator.anomaly import rolling_zscore_detector
from simulator.engine import ManufacturingSimulator
from simulator.isolation_forest import detector_summary, isolation_forest_detector


SCENARIOS = ROOT / "simulator" / "scenarios"

RUNS = (
    ("normal", "normal_operation", None),
    ("guide_rail", "guide_rail_misalignment", 600),
    ("sensor_drift", "sensor_calibration_drift", 420),
)


def run_scenario(name: str):
    simulator = ManufacturingSimulator(SCENARIOS / f"{name}.yaml")
    with redirect_stdout(StringIO()):
        df = simulator.run()
    scored = rolling_zscore_detector(df)
    return isolation_forest_detector(scored)


def main():
    print("Detector comparison (pressure_x)")
    print("Live detector: lagged rolling Z-score")
    print("Comparison: Isolation Forest trained on seconds 0-399")
    print()
    print(f"{'scenario':<28} {'z_count':>8} {'z_first':>8} {'if_count':>8} {'if_first':>8}")

    for name, scenario_id, fault_second in RUNS:
        df = run_scenario(name)
        z = detector_summary(df, "pressure_x_anomaly", fault_second)
        forest = detector_summary(df, "iforest_anomaly", fault_second)
        print(
            f"{scenario_id:<28} "
            f"{z['count']:>8} "
            f"{str(z['first_second'] or '-'):>8} "
            f"{forest['count']:>8} "
            f"{str(forest['first_second'] or '-'):>8}"
        )


if __name__ == "__main__":
    main()
