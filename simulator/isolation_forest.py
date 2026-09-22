"""Isolation Forest comparison detector.

Trained on the pre-fault baseline of a run. Not used by ingest, the API,
or the dashboard. Rolling Z-score remains the live detector.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


PRESSURE_COLUMNS = ["pressure_x"]
TRAIN_END_SECOND = 400
SCORE_PERCENTILE = 1.0
# Slightly longer than the live rolling-Z persistence so the
# speed-change nuisance on the normal run does not become a flag.
PERSISTENCE = 15


def isolation_forest_detector(
    df: pd.DataFrame,
    columns=None,
    train_end_second: int = TRAIN_END_SECOND,
    percentile: float = SCORE_PERCENTILE,
    persistence: int = PERSISTENCE,
    random_state: int = 42,
):
    result = df.copy()
    features = list(columns or PRESSURE_COLUMNS)
    train = result.loc[result["second"] < train_end_second, features]

    if len(train) < 30:
        raise ValueError("Not enough baseline samples to train Isolation Forest")

    model = IsolationForest(
        n_estimators=200,
        contamination="auto",
        random_state=random_state,
    )
    model.fit(train)

    train_scores = model.score_samples(train)
    threshold = float(np.percentile(train_scores, percentile))
    scores = model.score_samples(result[features])
    raw = pd.Series(scores < threshold, index=result.index)
    persistent = raw.rolling(persistence).sum() >= persistence

    result["iforest_score"] = scores
    result["iforest_anomaly"] = persistent.fillna(False)
    return result


def detector_summary(df: pd.DataFrame, flag_column: str, fault_second: int | None = None):
    flagged = df[df[flag_column]]
    first = int(flagged["second"].iloc[0]) if len(flagged) else None
    after_fault = None
    if fault_second is not None:
        after_fault = bool(df.loc[df["second"] >= fault_second, flag_column].any())

    return {
        "count": int(df[flag_column].sum()),
        "first_second": first,
        "after_fault": after_fault,
    }
