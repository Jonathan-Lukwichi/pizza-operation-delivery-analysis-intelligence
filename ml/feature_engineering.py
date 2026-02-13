"""
ML-specific feature engineering for PizzaOps Intelligence.
Creates features optimized for machine learning models.
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Optional
from sklearn.preprocessing import LabelEncoder, StandardScaler


def create_ml_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """
    Transform DataFrame into ML-ready feature matrix.

    Args:
        df: Transformed DataFrame from data pipeline

    Returns:
        Tuple of (feature DataFrame, encoders dict)
    """
    df = df.copy()
    encoders = {}

    # ── Numerical Features ──
    numerical_cols = [
        "dough_prep_time", "styling_time", "oven_time", "boxing_time",
        "delivery_duration", "total_prep_time", "total_process_time",
        "oven_temperature", "oven_temp_deviation", "hour_of_day"
    ]

    available_numerical = [col for col in numerical_cols if col in df.columns]

    # ── Categorical Features - One-Hot Encoding ──
    if "delivery_area" in df.columns:
        area_dummies = pd.get_dummies(df["delivery_area"], prefix="area")
        df = pd.concat([df, area_dummies], axis=1)

    if "order_mode" in df.columns:
        mode_dummies = pd.get_dummies(df["order_mode"], prefix="mode")
        df = pd.concat([df, mode_dummies], axis=1)

    # ── Categorical Features - Label Encoding ──
    label_encode_cols = ["stylist", "oven_operator", "delivery_driver", "dough_prep_staff", "boxer"]

    for col in label_encode_cols:
        if col in df.columns:
            le = LabelEncoder()
            # Handle NaN
            df[f"{col}_encoded"] = df[col].fillna("Unknown")
            df[f"{col}_encoded"] = le.fit_transform(df[f"{col}_encoded"])
            encoders[col] = le

    # ── Binary Features ──
    binary_cols = ["is_peak_hour", "is_weekend", "is_peak_lunch", "is_peak_dinner"]
    for col in binary_cols:
        if col in df.columns:
            df[col] = df[col].astype(int)

    # ── Cyclical Encoding for Day of Week ──
    if "day_of_week_num" in df.columns:
        df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week_num"] / 7)
        df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week_num"] / 7)

    # ── Cyclical Encoding for Hour ──
    if "hour_of_day" in df.columns:
        df["hour_sin"] = np.sin(2 * np.pi * df["hour_of_day"] / 24)
        df["hour_cos"] = np.cos(2 * np.pi * df["hour_of_day"] / 24)

    # ── Interaction Features ──
    if "is_peak_hour" in df.columns and "delivery_area" in df.columns:
        # Peak hour × Area E interaction
        if "area_E" in df.columns:
            df["peak_x_area_E"] = df["is_peak_hour"] * df["area_E"]
        if "area_C" in df.columns:
            df["peak_x_area_C"] = df["is_peak_hour"] * df["area_C"]

    if "oven_temperature" in df.columns and "oven_time" in df.columns:
        df["oven_temp_x_time"] = df["oven_temperature"] * df["oven_time"]

    return df, encoders


def get_complaint_features(df: pd.DataFrame) -> List[str]:
    """
    Get list of features to use for complaint prediction.

    Args:
        df: Feature-engineered DataFrame

    Returns:
        List of column names to use as features
    """
    features = []

    # Numerical
    numerical = [
        "total_prep_time", "delivery_duration", "oven_temperature",
        "oven_temp_deviation", "hour_of_day", "dough_prep_time",
        "styling_time", "oven_time", "boxing_time"
    ]
    features.extend([col for col in numerical if col in df.columns])

    # Binary
    binary = ["is_peak_hour", "is_weekend"]
    features.extend([col for col in binary if col in df.columns])

    # Cyclical
    cyclical = ["dow_sin", "dow_cos", "hour_sin", "hour_cos"]
    features.extend([col for col in cyclical if col in df.columns])

    # One-hot encoded
    for prefix in ["area_", "mode_"]:
        features.extend([col for col in df.columns if col.startswith(prefix)])

    # Label encoded
    encoded = [col for col in df.columns if col.endswith("_encoded")]
    features.extend(encoded)

    # Interaction
    interactions = ["peak_x_area_E", "peak_x_area_C", "oven_temp_x_time"]
    features.extend([col for col in interactions if col in df.columns])

    return features


def get_forecast_features(df: pd.DataFrame) -> List[str]:
    """
    Get list of features for demand forecasting.

    Args:
        df: Aggregated time series DataFrame

    Returns:
        List of column names to use as features
    """
    features = []

    # Lag features
    lag_cols = [col for col in df.columns if "lag_" in col]
    features.extend(lag_cols)

    # Rolling features
    rolling_cols = [col for col in df.columns if "rolling_" in col]
    features.extend(rolling_cols)

    # Time features
    time_cols = ["hour_of_day", "day_of_week_num", "is_weekend", "is_peak_hour"]
    features.extend([col for col in time_cols if col in df.columns])

    # Cyclical features
    cyclical = ["dow_sin", "dow_cos", "hour_sin", "hour_cos"]
    features.extend([col for col in cyclical if col in df.columns])

    return features


def create_lag_features(
    ts: pd.Series,
    lags: List[int] = [1, 2, 3, 7, 14]
) -> pd.DataFrame:
    """
    Create lag features for time series forecasting.

    Args:
        ts: Time series (order counts)
        lags: List of lag periods

    Returns:
        DataFrame with lag features
    """
    result = pd.DataFrame(index=ts.index)

    for lag in lags:
        result[f"lag_{lag}"] = ts.shift(lag)

    return result


def create_rolling_features(
    ts: pd.Series,
    windows: List[int] = [3, 7, 14]
) -> pd.DataFrame:
    """
    Create rolling window features for time series.

    Args:
        ts: Time series
        windows: List of window sizes

    Returns:
        DataFrame with rolling features
    """
    result = pd.DataFrame(index=ts.index)

    for window in windows:
        result[f"rolling_mean_{window}"] = ts.rolling(window=window).mean()
        result[f"rolling_std_{window}"] = ts.rolling(window=window).std()
        result[f"rolling_min_{window}"] = ts.rolling(window=window).min()
        result[f"rolling_max_{window}"] = ts.rolling(window=window).max()

    return result


def prepare_train_test_split(
    df: pd.DataFrame,
    features: List[str],
    target: str,
    test_size: float = 0.2,
    time_based: bool = False
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Prepare train/test split for ML.

    Args:
        df: Feature DataFrame
        features: List of feature columns
        target: Target column name
        test_size: Proportion for test set
        time_based: If True, use temporal split (last N% as test)

    Returns:
        Tuple of (X_train, X_test, y_train, y_test)
    """
    # Filter to rows with valid target
    df_valid = df.dropna(subset=[target])

    # Get features
    X = df_valid[features].copy()
    y = df_valid[target].copy()

    # Fill any remaining NaN in features with median
    for col in X.columns:
        if X[col].isna().any():
            X[col] = X[col].fillna(X[col].median())

    if time_based and "order_date" in df_valid.columns:
        # Temporal split
        split_idx = int(len(df_valid) * (1 - test_size))
        X_train = X.iloc[:split_idx]
        X_test = X.iloc[split_idx:]
        y_train = y.iloc[:split_idx]
        y_test = y.iloc[split_idx:]
    else:
        # Random split
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

    return X_train, X_test, y_train, y_test


def scale_features(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    columns: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, pd.DataFrame, StandardScaler]:
    """
    Scale numerical features.

    Args:
        X_train: Training features
        X_test: Test features
        columns: Columns to scale (if None, scale all numerical)

    Returns:
        Tuple of (scaled X_train, scaled X_test, scaler)
    """
    scaler = StandardScaler()

    if columns is None:
        columns = X_train.select_dtypes(include=[np.number]).columns.tolist()

    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()

    X_train_scaled[columns] = scaler.fit_transform(X_train[columns])
    X_test_scaled[columns] = scaler.transform(X_test[columns])

    return X_train_scaled, X_test_scaled, scaler
