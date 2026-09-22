import pandas as pd


SIGNALS = [
    "pressure_x",
    "pressure_y",
    "vibration",
    "velocity",
    "temperature",
    "motor_current",
]


def rolling_zscore_detector(
    df: pd.DataFrame,
    window: int = 120,
    threshold: float = 3.0,
    persistence: int = 10,
):

    result = df.copy()

    anomaly_columns = []

    for signal in SIGNALS:

        # Compare against a lagged window so a slow ramp is not
        # absorbed into the rolling mean/std of the current period.
        baseline = result[signal].shift(window)

        mean = (
            baseline
            .rolling(window)
            .mean()
        )

        std = (
            baseline
            .rolling(window)
            .std()
            .clip(lower=1e-6)
        )

        z_col = f"{signal}_z"

        result[z_col] = (
            result[signal] - mean
        ) / std

        flag_col = f"{signal}_anomaly"

        raw_flag = (
            result[z_col].abs()
            > threshold
        )

        persistent_flag = (
            raw_flag
            .rolling(persistence)
            .sum()
            >= persistence
        )

        result[flag_col] = (
            persistent_flag.fillna(False)
        )

        anomaly_columns.append(flag_col)

    result["anomaly_detected"] = (
        result[anomaly_columns]
        .any(axis=1)
    )

    return result
