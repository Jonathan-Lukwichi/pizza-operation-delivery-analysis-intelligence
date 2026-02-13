"""
Complaint prediction model for PizzaOps Intelligence.
XGBoost binary classifier for predicting complaint risk.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import warnings

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import (
    f1_score, precision_score, recall_score, roc_auc_score,
    confusion_matrix, classification_report
)

from ml.feature_engineering import create_ml_features, get_complaint_features


class ComplaintPredictor:
    """
    Binary classifier for complaint prediction.

    Uses XGBoost with class balancing to handle minority complaint class.
    """

    def __init__(self):
        """Initialize the complaint predictor."""
        self.model = None
        self.features = None
        self.encoders = {}
        self.metrics = {}
        self.feature_importance = None
        self.is_trained = False

    def train(self, df: pd.DataFrame, target: str = "complaint") -> Dict:
        """
        Train the complaint prediction model.

        Args:
            df: Transformed DataFrame with all features
            target: Target column name

        Returns:
            Dict with training metrics
        """
        if not XGBOOST_AVAILABLE:
            return {"error": "XGBoost not installed. Run: pip install xgboost"}

        # Prepare features
        df_features, self.encoders = create_ml_features(df)
        self.features = get_complaint_features(df_features)

        # Validate target exists
        if target not in df_features.columns:
            return {"error": f"Target column '{target}' not found"}

        # Prepare data
        X = df_features[self.features].copy()
        y = df_features[target].copy()

        # Handle missing values
        for col in X.columns:
            if X[col].isna().any():
                X[col] = X[col].fillna(X[col].median())

        # Convert boolean to int
        y = y.astype(int)

        # Remove rows with NaN target
        valid_idx = ~y.isna()
        X = X[valid_idx]
        y = y[valid_idx]

        # Calculate class weights for imbalance
        n_neg = (y == 0).sum()
        n_pos = (y == 1).sum()
        scale_pos_weight = n_neg / n_pos if n_pos > 0 else 1

        # Initialize model
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            scale_pos_weight=scale_pos_weight,
            random_state=42,
            use_label_encoder=False,
            eval_metric='logloss'
        )

        # Cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

        cv_scores = {
            'f1': [],
            'precision': [],
            'recall': [],
            'roc_auc': []
        }

        for train_idx, val_idx in cv.split(X, y):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

            self.model.fit(X_train, y_train)
            y_pred = self.model.predict(X_val)
            y_prob = self.model.predict_proba(X_val)[:, 1]

            cv_scores['f1'].append(f1_score(y_val, y_pred))
            cv_scores['precision'].append(precision_score(y_val, y_pred))
            cv_scores['recall'].append(recall_score(y_val, y_pred))
            cv_scores['roc_auc'].append(roc_auc_score(y_val, y_prob))

        # Final training on full data
        self.model.fit(X, y)

        # Store metrics
        self.metrics = {
            'f1_mean': np.mean(cv_scores['f1']),
            'f1_std': np.std(cv_scores['f1']),
            'precision_mean': np.mean(cv_scores['precision']),
            'recall_mean': np.mean(cv_scores['recall']),
            'roc_auc_mean': np.mean(cv_scores['roc_auc']),
            'n_samples': len(y),
            'n_complaints': int(y.sum()),
            'complaint_rate': float(y.mean() * 100)
        }

        # Feature importance
        self.feature_importance = dict(zip(
            self.features,
            self.model.feature_importances_
        ))

        self.is_trained = True
        return self.metrics

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        """
        Predict complaint probability for new data.

        Args:
            df: DataFrame with same features as training data

        Returns:
            Array of complaint probabilities
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")

        df_features, _ = create_ml_features(df)
        X = df_features[self.features].copy()

        # Handle missing values
        for col in X.columns:
            if X[col].isna().any():
                X[col] = X[col].fillna(X[col].median())

        return self.model.predict_proba(X)[:, 1]

    def predict(self, df: pd.DataFrame, threshold: float = 0.5) -> np.ndarray:
        """
        Predict complaint (True/False) for new data.

        Args:
            df: DataFrame with features
            threshold: Probability threshold for positive prediction

        Returns:
            Array of predictions
        """
        probs = self.predict_proba(df)
        return probs >= threshold

    def get_feature_importance(self, top_n: int = 10) -> Dict[str, float]:
        """
        Get top N most important features.

        Args:
            top_n: Number of features to return

        Returns:
            Dict of feature name -> importance score
        """
        if not self.feature_importance:
            return {}

        sorted_features = sorted(
            self.feature_importance.items(),
            key=lambda x: -x[1]
        )
        return dict(sorted_features[:top_n])

    def explain_prediction(self, row: pd.Series) -> Dict:
        """
        Explain a single prediction using feature contributions.

        Args:
            row: Single row of feature data

        Returns:
            Dict with prediction and feature contributions
        """
        if not self.is_trained:
            raise ValueError("Model not trained.")

        # Convert row to DataFrame
        df_row = pd.DataFrame([row])
        df_features, _ = create_ml_features(df_row)
        X = df_features[self.features].copy()

        # Handle missing
        for col in X.columns:
            if X[col].isna().any():
                X[col] = X[col].fillna(0)

        prob = self.model.predict_proba(X)[0, 1]

        # Get feature values and importance
        contributions = []
        for feat in self.features:
            if feat in X.columns:
                contributions.append({
                    'feature': feat,
                    'value': X[feat].iloc[0],
                    'importance': self.feature_importance.get(feat, 0)
                })

        contributions.sort(key=lambda x: -x['importance'])

        return {
            'probability': float(prob),
            'prediction': prob >= 0.5,
            'top_factors': contributions[:5]
        }


def train_complaint_model(df: pd.DataFrame) -> Tuple[ComplaintPredictor, Dict]:
    """
    Convenience function to train complaint model.

    Args:
        df: Transformed DataFrame

    Returns:
        Tuple of (trained model, metrics dict)
    """
    model = ComplaintPredictor()
    metrics = model.train(df)
    return model, metrics


def get_high_risk_orders(
    df: pd.DataFrame,
    model: ComplaintPredictor,
    threshold: float = 0.5
) -> pd.DataFrame:
    """
    Identify orders with high complaint risk.

    Args:
        df: DataFrame with order data
        model: Trained ComplaintPredictor
        threshold: Risk threshold

    Returns:
        DataFrame of high-risk orders
    """
    df = df.copy()
    df['complaint_risk'] = model.predict_proba(df)
    high_risk = df[df['complaint_risk'] >= threshold].sort_values(
        'complaint_risk', ascending=False
    )
    return high_risk
