import argparse
import json
from pathlib import Path

from simulator.engine import ManufacturingSimulator
from simulator.anomaly import rolling_zscore_detector


SCENARIOS = {
    "normal": "simulator/scenarios/normal.yaml",
    "guide_rail": "simulator/scenarios/guide_rail.yaml",
    "sensor_drift": "simulator/scenarios/sensor_drift.yaml",
}


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--scenario",
        choices=SCENARIOS.keys(),
        required=True,
    )

    parser.add_argument(
        "--output-dir",
        default="data/generated",
    )

    args = parser.parse_args()

    simulator = ManufacturingSimulator(
        SCENARIOS[args.scenario]
    )

    df = simulator.run()

    df = rolling_zscore_detector(df)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    telemetry_path = (
        output_dir
        / f"{simulator.scenario_id}.parquet"
    )

    events_path = (
        output_dir
        / f"{simulator.scenario_id}_events.json"
    )

    df.to_parquet(
        telemetry_path,
        index=False,
    )

    with events_path.open(
        "w"
    ) as file:

        json.dump(
            simulator.event_log,
            file,
            indent=2,
        )

    print()
    print("Simulation complete")
    print(f"Rows: {len(df)}")
    print(f"Telemetry: {telemetry_path}")
    print(f"Events: {events_path}")

    anomalies = df[
        df["anomaly_detected"]
    ]

    if len(anomalies):

        first = anomalies.iloc[0]

        print()
        print(
            "First anomaly detected at "
            f"{int(first['second'])} seconds"
        )

    else:

        print()
        print("No anomaly detected.")


if __name__ == "__main__":
    main()
