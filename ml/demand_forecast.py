"""
Demand forecasting models for PizzaOps Intelligence.
Ensemble of ARIMA, Prophet, and XGBoost for order volume prediction.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import timedelta
import warnings

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

from sklearn.metrics import mean_squared_error, mean_absolute_error

from ml.feature_engineering import create_lag_features, create_rolling_features


class DemandForecaster:
    """
    Ensemble forecaster combining multiple approaches.

    Models:
    1. Exponential Smoothing (Holt-Winters)
    2. ARIMA (if enough data)
    3. XGBoost (lag-based features)

    Ensemble weights based on validation performance.
    """

    def __init__(self):
        """Initialize the demand forecaster."""
        self.models = {}
        self.weights = {}
        self.metrics = {}
        self.is_fitted = False
        self.ts_data = None
        self.freq = 'D'

    def fit(self, ts: pd.Series, freq: str = 'D') -> Dict:
        """
        Train all forecasting models.

        Args:
            ts: Time series of order counts (index should be datetime)
            freq: Frequency ('D' for daily, 'H' for hourly)

        Returns:
            Dict with training metrics for each model
        """
        self.freq = freq
        self.ts_data = ts.copy()

        # Ensure datetime index
        if not isinstance(ts.index, pd.DatetimeIndex):
            ts.index = pd.to_datetime(ts.index)

        ts = ts.sort_index()
        ts = ts.asfreq(freq, fill_value=ts.mean())

        metrics = {}

        # Split for validation (last 20%)
        split_idx = int(len(ts) * 0.8)
        train = ts.iloc[:split_idx]
        test = ts.iloc[split_idx:]

        # 1. Exponential Smoothing
        try:
            es_model = ExponentialSmoothing(
                train,
                seasonal_periods=7 if freq == 'D' else 24,
                trend='add',
                seasonal='add'
            ).fit()

            es_forecast = es_model.forecast(len(test))
            es_rmse = np.sqrt(mean_squared_error(test, es_forecast))

            self.models['exp_smoothing'] = es_model
            metrics['exp_smoothing'] = {
                'rmse': es_rmse,
                'mae': mean_absolute_error(test, es_forecast)
            }
        except Exception as e:
            metrics['exp_smoothing'] = {'error': str(e)}

        # 2. ARIMA (simplified - auto selection would be better)
        if STATSMODELS_AVAILABLE and len(train) >= 30:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    arima_model = ARIMA(train, order=(1, 1, 1)).fit()

                arima_forecast = arima_model.forecast(len(test))
                arima_rmse = np.sqrt(mean_squared_error(test, arima_forecast))

                self.models['arima'] = arima_model
                metrics['arima'] = {
                    'rmse': arima_rmse,
                    'mae': mean_absolute_error(test, arima_forecast)
                }
            except Exception as e:
                metrics['arima'] = {'error': str(e)}

        # 3. XGBoost with lag features
        if XGBOOST_AVAILABLE and len(train) >= 14:
            try:
                # Create features
                lag_features = create_lag_features(ts, lags=[1, 2, 3, 7])
                rolling_features = create_rolling_features(ts, windows=[3, 7])

                xgb_df = pd.concat([ts.rename('target'), lag_features, rolling_features], axis=1)
                xgb_df = xgb_df.dropna()

                train_xgb = xgb_df.iloc[:split_idx]
                test_xgb = xgb_df.iloc[split_idx:]

                X_train = train_xgb.drop('target', axis=1)
                y_train = train_xgb['target']
                X_test = test_xgb.drop('target', axis=1)
                y_test = test_xgb['target']

                xgb_model = xgb.XGBRegressor(
                    n_estimators=100,
                    max_depth=4,
                    learning_rate=0.1,
                    random_state=42
                )
                xgb_model.fit(X_train, y_train)

                xgb_forecast = xgb_model.predict(X_test)
                xgb_rmse = np.sqrt(mean_squared_error(y_test, xgb_forecast))

                self.models['xgboost'] = xgb_model
                metrics['xgboost'] = {
                    'rmse': xgb_rmse,
                    'mae': mean_absolute_error(y_test, xgb_forecast)
                }
            except Exception as e:
                metrics['xgboost'] = {'error': str(e)}

        # Calculate ensemble weights (inverse RMSE)
        valid_models = {k: v for k, v in metrics.items() if 'rmse' in v}
        if valid_models:
            total_inv_rmse = sum(1/v['rmse'] for v in valid_models.values())
            self.weights = {k: (1/v['rmse'])/total_inv_rmse for k, v in valid_models.items()}
        else:
            self.weights = {}

        # Calculate ensemble metrics
        if len(valid_models) > 1:
            metrics['ensemble'] = {
                'weights': self.weights,
                'models_used': list(valid_models.keys())
            }

        self.metrics = metrics
        self.is_fitted = True
        return metrics

    def predict(self, horizon: int) -> pd.DataFrame:
        """
        Generate forecasts for specified horizon.

        Args:
            horizon: Number of periods to forecast

        Returns:
            DataFrame with columns: date, forecast, lower_ci, upper_ci
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        # Generate future dates
        last_date = self.ts_data.index.max()
        if self.freq == 'D':
            future_dates = pd.date_range(last_date + timedelta(days=1), periods=horizon, freq='D')
        else:
            future_dates = pd.date_range(last_date + timedelta(hours=1), periods=horizon, freq='H')

        forecasts = {}

        # Get predictions from each model
        if 'exp_smoothing' in self.models:
            try:
                forecasts['exp_smoothing'] = self.models['exp_smoothing'].forecast(horizon)
            except:
                pass

        if 'arima' in self.models:
            try:
                forecasts['arima'] = self.models['arima'].forecast(horizon)
            except:
                pass

        # XGBoost needs iterative forecasting
        if 'xgboost' in self.models:
            try:
                xgb_preds = self._xgboost_iterative_forecast(horizon)
                forecasts['xgboost'] = xgb_preds
            except:
                pass

        # Ensemble
        if forecasts:
            ensemble_forecast = np.zeros(horizon)
            total_weight = 0

            for model_name, preds in forecasts.items():
                weight = self.weights.get(model_name, 1/len(forecasts))
                ensemble_forecast += np.array(preds) * weight
                total_weight += weight

            ensemble_forecast /= total_weight if total_weight > 0 else 1

            # Simple confidence interval (based on historical std)
            historical_std = self.ts_data.std()
            ci_width = historical_std * 1.96

            result = pd.DataFrame({
                'date': future_dates,
                'forecast': ensemble_forecast,
                'lower_ci': ensemble_forecast - ci_width,
                'upper_ci': ensemble_forecast + ci_width
            })

            # Add individual model forecasts
            for model_name, preds in forecasts.items():
                result[f'{model_name}_pred'] = np.array(preds)

            return result

        return pd.DataFrame({'date': future_dates, 'forecast': [self.ts_data.mean()] * horizon})

    def _xgboost_iterative_forecast(self, horizon: int) -> List[float]:
        """Generate XGBoost forecasts iteratively."""
        if 'xgboost' not in self.models:
            return []

        ts = self.ts_data.copy()
        preds = []

        for i in range(horizon):
            # Create features from current data
            lag_features = create_lag_features(ts, lags=[1, 2, 3, 7])
            rolling_features = create_rolling_features(ts, windows=[3, 7])

            features_df = pd.concat([lag_features, rolling_features], axis=1)
            last_features = features_df.iloc[-1:].fillna(0)

            # Predict next value
            pred = self.models['xgboost'].predict(last_features)[0]
            preds.append(max(0, pred))

            # Add prediction to series for next iteration
            next_date = ts.index[-1] + timedelta(days=1 if self.freq == 'D' else hours=1)
            ts = pd.concat([ts, pd.Series([pred], index=[next_date])])

        return preds

    def compare_models(self) -> pd.DataFrame:
        """
        Compare model performance.

        Returns:
            DataFrame with model comparison metrics
        """
        if not self.metrics:
            return pd.DataFrame()

        rows = []
        for model, metrics in self.metrics.items():
            if 'rmse' in metrics:
                rows.append({
                    'Model': model.replace('_', ' ').title(),
                    'RMSE': round(metrics['rmse'], 2),
                    'MAE': round(metrics.get('mae', 0), 2),
                    'Weight': f"{self.weights.get(model, 0)*100:.1f}%"
                })

        return pd.DataFrame(rows)

    def staffing_recommendation(
        self,
        forecast: pd.DataFrame,
        orders_per_prep: int = 10,
        orders_per_driver: int = 5
    ) -> List[Dict]:
        """
        Generate staffing recommendations based on forecast.

        Args:
            forecast: Forecast DataFrame from predict()
            orders_per_prep: Orders one prep staff can handle per hour
            orders_per_driver: Orders one driver can handle per hour

        Returns:
            List of dicts with staffing recommendations
        """
        recommendations = []

        # Assume 8 active hours per day for daily forecasts
        active_hours = 8

        for _, row in forecast.iterrows():
            daily_orders = row['forecast']
            hourly_avg = daily_orders / active_hours

            prep_needed = max(2, int(np.ceil(hourly_avg / orders_per_prep)))
            drivers_needed = max(2, int(np.ceil(hourly_avg / orders_per_driver)))

            recommendations.append({
                'date': row['date'],
                'predicted_orders': int(daily_orders),
                'recommended_prep_staff': prep_needed,
                'recommended_drivers': drivers_needed,
                'confidence': 'high' if row.get('lower_ci', 0) > 0 else 'medium'
            })

        return recommendations


def train_forecaster(df: pd.DataFrame, date_col: str = 'order_date') -> Tuple[DemandForecaster, Dict]:
    """
    Convenience function to train forecaster.

    Args:
        df: DataFrame with order data
        date_col: Date column name

    Returns:
        Tuple of (trained forecaster, metrics dict)
    """
    # Aggregate to daily counts
    daily_counts = df.groupby(date_col).size()
    daily_counts.index = pd.to_datetime(daily_counts.index)

    forecaster = DemandForecaster()
    metrics = forecaster.fit(daily_counts, freq='D')

    return forecaster, metrics
