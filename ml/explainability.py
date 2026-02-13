"""
Model explainability for PizzaOps Intelligence.
SHAP-based explanations for ML model predictions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import plotly.graph_objects as go
import plotly.express as px

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

from ui.theme import COLORS, apply_plotly_theme


def compute_shap_values(model: Any, X: pd.DataFrame) -> Optional[np.ndarray]:
    """
    Compute SHAP values for model predictions.

    Args:
        model: Trained model (XGBoost, sklearn, etc.)
        X: Feature DataFrame

    Returns:
        SHAP values array or None if SHAP not available
    """
    if not SHAP_AVAILABLE:
        return None

    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)

        # For binary classification, may return list
        if isinstance(shap_values, list):
            shap_values = shap_values[1]  # Positive class

        return shap_values
    except Exception as e:
        print(f"SHAP computation error: {e}")
        return None


def shap_feature_importance(
    model: Any,
    X: pd.DataFrame,
    top_n: int = 10
) -> go.Figure:
    """
    Create global SHAP feature importance bar chart.

    Args:
        model: Trained model
        X: Feature DataFrame
        top_n: Number of top features to show

    Returns:
        Plotly Figure
    """
    shap_values = compute_shap_values(model, X)

    if shap_values is None:
        # Fallback to model's built-in feature importance
        if hasattr(model, 'feature_importances_'):
            importance = dict(zip(X.columns, model.feature_importances_))
        else:
            return _empty_chart("SHAP not available")
    else:
        # Mean absolute SHAP value per feature
        importance = dict(zip(X.columns, np.abs(shap_values).mean(axis=0)))

    # Sort and get top N
    sorted_importance = sorted(importance.items(), key=lambda x: -x[1])[:top_n]
    features = [x[0] for x in sorted_importance][::-1]
    values = [x[1] for x in sorted_importance][::-1]

    # Clean feature names
    features = [f.replace("_", " ").title() for f in features]

    fig = go.Figure(go.Bar(
        x=values,
        y=features,
        orientation='h',
        marker_color=COLORS["primary"]
    ))

    fig.update_layout(
        title="Feature Importance (Mean |SHAP Value|)",
        xaxis_title="Impact on Prediction",
        yaxis_title="Feature",
        height=max(300, top_n * 30)
    )

    fig = apply_plotly_theme(fig)
    return fig


def shap_waterfall(
    model: Any,
    X_single: pd.DataFrame,
    base_value: Optional[float] = None
) -> go.Figure:
    """
    Create SHAP waterfall chart for single prediction.

    Args:
        model: Trained model
        X_single: Single row DataFrame
        base_value: Expected value (average prediction)

    Returns:
        Plotly Figure
    """
    shap_values = compute_shap_values(model, X_single)

    if shap_values is None:
        return _empty_chart("SHAP not available for waterfall")

    shap_row = shap_values[0] if len(shap_values.shape) > 1 else shap_values

    # Get feature contributions
    contributions = list(zip(X_single.columns, X_single.iloc[0].values, shap_row))
    contributions.sort(key=lambda x: abs(x[2]), reverse=True)
    contributions = contributions[:10]  # Top 10

    features = []
    values = []
    colors = []

    for feat, feat_val, shap_val in contributions:
        feat_name = f"{feat.replace('_', ' ').title()}"
        features.append(feat_name)
        values.append(shap_val)
        colors.append(COLORS["danger"] if shap_val > 0 else COLORS["success"])

    fig = go.Figure(go.Bar(
        x=values,
        y=features,
        orientation='h',
        marker_color=colors
    ))

    fig.update_layout(
        title="Prediction Explanation (SHAP Waterfall)",
        xaxis_title="Impact on Complaint Probability",
        yaxis_title="Feature",
        height=max(300, len(features) * 35)
    )

    # Add zero line
    fig.add_vline(x=0, line_dash="dash", line_color=COLORS["text_muted"])

    fig = apply_plotly_theme(fig)
    return fig


def shap_dependence(
    model: Any,
    X: pd.DataFrame,
    feature_name: str,
    interaction_feature: Optional[str] = None
) -> go.Figure:
    """
    Create SHAP dependence plot for a feature.

    Args:
        model: Trained model
        X: Feature DataFrame
        feature_name: Feature to analyze
        interaction_feature: Optional feature for coloring

    Returns:
        Plotly Figure
    """
    shap_values = compute_shap_values(model, X)

    if shap_values is None or feature_name not in X.columns:
        return _empty_chart("Cannot compute dependence plot")

    feature_idx = list(X.columns).index(feature_name)
    feature_values = X[feature_name].values
    feature_shap = shap_values[:, feature_idx]

    # Create scatter plot
    if interaction_feature and interaction_feature in X.columns:
        color_values = X[interaction_feature].values
        fig = px.scatter(
            x=feature_values,
            y=feature_shap,
            color=color_values,
            labels={'x': feature_name, 'y': 'SHAP Value', 'color': interaction_feature}
        )
    else:
        fig = px.scatter(
            x=feature_values,
            y=feature_shap,
            labels={'x': feature_name, 'y': 'SHAP Value'}
        )
        fig.update_traces(marker_color=COLORS["primary"])

    fig.update_layout(
        title=f"SHAP Dependence: {feature_name.replace('_', ' ').title()}",
        height=400
    )

    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color=COLORS["text_muted"])

    fig = apply_plotly_theme(fig)
    return fig


def explain_single_prediction(
    model: Any,
    X_single: pd.DataFrame,
    feature_names: List[str]
) -> Dict:
    """
    Get explanation for a single prediction.

    Args:
        model: Trained model
        X_single: Single row DataFrame
        feature_names: List of feature names

    Returns:
        Dict with prediction and explanations
    """
    result = {
        'prediction': None,
        'probability': None,
        'top_positive_factors': [],
        'top_negative_factors': []
    }

    try:
        # Get prediction
        if hasattr(model, 'predict_proba'):
            prob = model.predict_proba(X_single)[0, 1]
            result['probability'] = float(prob)
            result['prediction'] = prob >= 0.5
        else:
            pred = model.predict(X_single)[0]
            result['prediction'] = float(pred)

        # Get SHAP values
        shap_values = compute_shap_values(model, X_single)

        if shap_values is not None:
            shap_row = shap_values[0] if len(shap_values.shape) > 1 else shap_values

            contributions = list(zip(feature_names, shap_row))

            # Positive factors (increase complaint risk)
            positive = sorted([c for c in contributions if c[1] > 0], key=lambda x: -x[1])
            result['top_positive_factors'] = [
                {'feature': f.replace('_', ' ').title(), 'impact': round(v, 4)}
                for f, v in positive[:5]
            ]

            # Negative factors (decrease complaint risk)
            negative = sorted([c for c in contributions if c[1] < 0], key=lambda x: x[1])
            result['top_negative_factors'] = [
                {'feature': f.replace('_', ' ').title(), 'impact': round(v, 4)}
                for f, v in negative[:5]
            ]

    except Exception as e:
        result['error'] = str(e)

    return result


def _empty_chart(message: str) -> go.Figure:
    """Create an empty chart with a message."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=16, color=COLORS["text_muted"])
    )
    fig.update_layout(
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False),
        height=300
    )
    fig = apply_plotly_theme(fig)
    return fig


def get_feature_importance_df(model: Any, feature_names: List[str]) -> pd.DataFrame:
    """
    Get feature importance as DataFrame.

    Args:
        model: Trained model
        feature_names: List of feature names

    Returns:
        DataFrame with feature importance
    """
    if hasattr(model, 'feature_importances_'):
        importance = model.feature_importances_
    else:
        return pd.DataFrame()

    df = pd.DataFrame({
        'feature': feature_names,
        'importance': importance
    })
    df = df.sort_values('importance', ascending=False)
    df['importance_pct'] = (df['importance'] / df['importance'].sum() * 100).round(2)

    return df
