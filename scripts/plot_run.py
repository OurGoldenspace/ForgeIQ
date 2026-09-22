import argparse
import pandas as pd
import matplotlib.pyplot as plt


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--file",
        required=True,
    )

    args = parser.parse_args()

    df = pd.read_parquet(
        args.file
    )

    plt.figure(
        figsize=(12, 6)
    )

    plt.plot(
        df["second"],
        df["pressure_x"],
        label="Pressure X",
    )

    plt.plot(
        df["second"],
        df["pressure_y"],
        label="Pressure Y",
    )

    anomaly_rows = df[
        df["anomaly_detected"]
    ]

    if len(anomaly_rows):

        plt.scatter(
            anomaly_rows["second"],
            anomaly_rows["pressure_x"],
            label="Detected anomaly",
            s=20,
        )

    plt.xlabel("Simulation time (seconds)")
    plt.ylabel("Pressure")
    plt.title(
        f"ForgeIQ - {df['scenario_id'].iloc[0]}"
    )

    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
