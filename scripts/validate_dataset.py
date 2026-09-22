import argparse
import pandas as pd


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

    print("\nDATASET")
    print("=" * 50)

    print(
        f"Scenario: {df['scenario_id'].iloc[0]}"
    )

    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Duration: {df['second'].max()} sec"
    )

    print("\nMissing values")

    print(
        df.isna()
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
    )

    print("\nSignal ranges")

    columns = [
        "pressure_x",
        "pressure_y",
        "vibration",
        "velocity",
        "temperature",
        "motor_current",
        "line_speed",
    ]

    print(
        df[columns]
        .describe()
        .T[
            [
                "mean",
                "std",
                "min",
                "max",
            ]
        ]
    )

    print("\nGround-truth faults")

    print(
        df[
            [
                "physical_fault",
                "sensor_fault",
            ]
        ]
        .value_counts(
            dropna=False
        )
    )

    print("\nDetector")

    if "anomaly_detected" in df:

        print(
            df["anomaly_detected"]
            .value_counts()
        )


if __name__ == "__main__":
    main()
