"""
Model evaluation utilities for PizzaOps Intelligence.
Cross-validation, metrics, and comparison.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import plotly.graph_objects as go
import plotly.express as px

from sklearn.model_selection import (
    StratifiedKFold, TimeSeriesSplit, cross_val_score
)
from sklearn.metrics import (
    f1_score, precision_score, recall_score, roc_auc_score,
    accuracy_score, confusion_matrix, classification_report,
    mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
)

from ui.theme import COLORS, apply_plotly_theme


def evaluate_classifier(
    model: Any,
    X: pd.DataFrame,
    y: pd.Series,
    cv: int = 5
) -> Dict:
    """
    Evaluate a classification model with stratified k-fold CV.

    Args:
        model: Classifier to evaluate
        X: Feature matrix
        y: Target labels
        cv: Number of folds

    Returns:
        Dict with evaluation metrics
    """
    y = y.astype(int)

    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)

    metrics = {
        'f1': [],
        'precision': [],
        'recall': [],
        'accuracy': [],
        'roc_auc': []
    }

    all_y_true = []
    all_y_pred = []

    for train_idx, val_idx in skf.split(X, y):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        model.fit(X_train, y_train)
        y_pred = model.predict(X_val)

        metrics['f1'].append(f1_score(y_val, y_pred))
        metrics['precision'].append(precision_score(y_val, y_pred))
        metrics['recall'].append(recall_score(y_val, y_pred))
        metrics['accuracy'].append(accuracy_score(y_val, y_pred))

        if hasattr(model, 'predict_proba'):
            y_prob = model.predict_proba(X_val)[:, 1]
            metrics['roc_auc'].append(roc_auc_score(y_val, y_prob))

        all_y_true.extend(y_val.tolist())
        all_y_pred.extend(y_pred.tolist())

    # Compute confusion matrix from all predictions
    cm = confusion_matrix(all_y_true, all_y_pred)

    return {
        'f1_mean': np.mean(metrics['f1']),
        'f1_std': np.std(metrics['f1']),
        'precision_mean': np.mean(metrics['precision']),
        'precision_std': np.std(metrics['precision']),
        'recall_mean': np.mean(metrics['recall']),
        'recall_std': np.std(metrics['recall']),
        'accuracy_mean': np.mean(metrics['accuracy']),
        'roc_auc_mean': np.mean(metrics['roc_auc']) if metrics['roc_auc'] else None,
        'confusion_matrix': cm,
        'cv_scores': metrics
    }


def evaluate_forecaster(
    model: Any,
    ts: pd.Series,
    n_splits: int = 3
) -> Dict:
    """
    Evaluate a time series forecaster with TimeSeriesSplit.

    Args:
        model: Forecaster to evaluate
        ts: Time series data
        n_splits: Number of time-based splits

    Returns:
        Dict with evaluation metrics
    """
    tscv = TimeSeriesSplit(n_splits=n_splits)

    metrics = {
        'rmse': [],
        'mae': [],
        'mape': []
    }

    fold_results = []

    for fold, (train_idx, test_idx) in enumerate(tscv.split(ts)):
        train = ts.iloc[train_idx]
        test = ts.iloc[test_idx]

        # Fit model
        model.fit(train)

        # Predict
        forecast = model.predict(len(test))

        if isinstance(forecast, pd.DataFrame):
            y_pred = forecast['forecast'].values
        else:
            y_pred = np.array(forecast)

        y_true = test.values

        # Calculate metrics
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        mape = mean_absolute_percentage_error(y_true, y_pred) * 100

        metrics['rmse'].append(rmse)
        metrics['mae'].append(mae)
        metrics['mape'].append(mape)

        fold_results.append({
            'fold': fold + 1,
            'train_size': len(train),
            'test_size': len(test),
            'rmse': round(rmse, 2),
            'mae': round(mae, 2),
            'mape': round(mape, 2)
        })

    return {
        'rmse_mean': np.mean(metrics['rmse']),
        'rmse_std': np.std(metrics['rmse']),
        'mae_mean': np.mean(metrics['mae']),
        'mae_std': np.std(metrics['mae']),
        'mape_mean': np.mean(metrics['mape']),
        'mape_std': np.std(metrics['mape']),
        'fold_results': fold_results
    }


def plot_confusion_matrix(cm: np.ndarray, labels: List[str] = None) -> go.Figure:
    """
    Plot confusion matrix as heatmap.

    Args:
        cm: Confusion matrix array
        labels: Class labels

    Returns:
        Plotly Figure
    """
    if labels is None:
        labels = ['No Complaint', 'Complaint']

    # Calculate percentages
    cm_pct = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100

    # Create text annotations
    text = [[f"{cm[i][j]}<br>({cm_pct[i][j]:.1f}%)" for j in range(len(labels))]
            for i in range(len(labels))]

    fig = go.Figure(data=go.Heatmap(
        z=cm,
        x=labels,
        y=labels,
        text=text,
        texttemplate="%{text}",
        colorscale='Blues',
        showscale=True
    ))

    fig.update_layout(
        title="Confusion Matrix",
        xaxis_title="Predicted",
        yaxis_title="Actual",
        height=400,
        width=450
    )

    fig = apply_plotly_theme(fig)
    return fig


def plot_roc_curve(y_true: np.ndarray, y_prob: np.ndarray) -> go.Figure:
    """
    Plot ROC curve.

    Args:
        y_true: True labels
        y_prob: Predicted probabilities

    Returns:
        Plotly Figure
    """
    from sklearn.metrics import roc_curve, auc

    fpr, tpr, thresholds = roc_curve(y_true, y_prob)
    roc_auc = auc(fpr, tpr)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=fpr,
        y=tpr,
        mode='lines',
        name=f'ROC (AUC = {roc_auc:.3f})',
        line=dict(color=COLORS["primary"], width=2)
    ))

    # Diagonal line
    fig.add_trace(go.Scatter(
        x=[0, 1],
        y=[0, 1],
        mode='lines',
        name='Random',
        line=dict(color=COLORS["text_muted"], dash='dash')
    ))

    fig.update_layout(
        title="ROC Curve",
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate",
        height=400
    )

    fig = apply_plotly_theme(fig)
    return fig


def plot_precision_recall_curve(y_true: np.ndarray, y_prob: np.ndarray) -> go.Figure:
    """
    Plot precision-recall curve.

    Args:
        y_true: True labels
        y_prob: Predicted probabilities

    Returns:
        Plotly Figure
    """
    from sklearn.metrics import precision_recall_curve, average_precision_score

    precision, recall, thresholds = precision_recall_curve(y_true, y_prob)
    avg_precision = average_precision_score(y_true, y_prob)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=recall,
        y=precision,
        mode='lines',
        name=f'PR (AP = {avg_precision:.3f})',
        line=dict(color=COLORS["primary"], width=2)
    ))

    fig.update_layout(
        title="Precision-Recall Curve",
        xaxis_title="Recall",
        yaxis_title="Precision",
        height=400
    )

    fig = apply_plotly_theme(fig)
    return fig


def plot_forecast_comparison(
    actual: pd.Series,
    forecasts: Dict[str, np.ndarray]
) -> go.Figure:
    """
    Plot actual vs multiple forecasts.

    Args:
        actual: Actual values
        forecasts: Dict of model_name -> predictions

    Returns:
        Plotly Figure
    """
    fig = go.Figure()

    # Actual values
    fig.add_trace(go.Scatter(
        x=actual.index,
        y=actual.values,
        mode='lines',
        name='Actual',
        line=dict(color=COLORS["text_primary"], width=2)
    ))

    # Forecasts
    colors = COLORS["chart_palette"]
    for i, (name, preds) in enumerate(forecasts.items()):
        fig.add_trace(go.Scatter(
            x=actual.index,
            y=preds,
            mode='lines',
            name=name,
            line=dict(color=colors[i % len(colors)], width=1, dash='dash')
        ))

    fig.update_layout(
        title="Forecast Comparison",
        xaxis_title="Date",
        yaxis_title="Orders",
        height=400
    )

    fig = apply_plotly_theme(fig)
    return fig


def create_metrics_table(metrics: Dict) -> pd.DataFrame:
    """
    Create formatted metrics table.

    Args:
        metrics: Dict of metric values

    Returns:
        DataFrame formatted for display
    """
    rows = []

    metric_labels = {
        'f1_mean': ('F1 Score', True),
        'precision_mean': ('Precision', True),
        'recall_mean': ('Recall', True),
        'accuracy_mean': ('Accuracy', True),
        'roc_auc_mean': ('ROC AUC', True),
        'rmse_mean': ('RMSE', False),
        'mae_mean': ('MAE', False),
        'mape_mean': ('MAPE (%)', False)
    }

    for key, (label, higher_better) in metric_labels.items():
        if key in metrics and metrics[key] is not None:
            value = metrics[key]
            std_key = key.replace('_mean', '_std')
            std = metrics.get(std_key, 0)

            rows.append({
                'Metric': label,
                'Value': f"{value:.3f} ± {std:.3f}" if std else f"{value:.3f}",
                'Direction': '↑ Higher is better' if higher_better else '↓ Lower is better'
            })

    return pd.DataFrame(rows)


def compare_models(model_metrics: Dict[str, Dict]) -> pd.DataFrame:
    """
    Compare multiple models.

    Args:
        model_metrics: Dict of model_name -> metrics dict

    Returns:
        DataFrame comparison
    """
    rows = []

    for model_name, metrics in model_metrics.items():
        row = {'Model': model_name}

        if 'f1_mean' in metrics:
            row['F1'] = f"{metrics['f1_mean']:.3f}"
        if 'precision_mean' in metrics:
            row['Precision'] = f"{metrics['precision_mean']:.3f}"
        if 'recall_mean' in metrics:
            row['Recall'] = f"{metrics['recall_mean']:.3f}"
        if 'roc_auc_mean' in metrics:
            row['AUC'] = f"{metrics['roc_auc_mean']:.3f}"
        if 'rmse_mean' in metrics:
            row['RMSE'] = f"{metrics['rmse_mean']:.2f}"
        if 'mae_mean' in metrics:
            row['MAE'] = f"{metrics['mae_mean']:.2f}"

        rows.append(row)

    return pd.DataFrame(rows)
