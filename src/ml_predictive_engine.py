#!/usr/bin/env python3
"""
ML PREDICTIVE ENGINE
====================

Machine Learning integration voor voorspellende marktanalyse
Vervangt reactieve analyse door anticiperende intelligentie
"""

import asyncio
import json
import logging
import sqlite3
import pickle
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@dataclass
class MLPrediction:
    """Machine Learning prediction result"""
    token: str
    prediction_type: str  # 'price_direction', 'volatility', 'liquidity'
    prediction: float     # Voorspelde waarde
    confidence: float     # 0-100 confidence score
    feature_importance: Dict[str, float]
    prediction_horizon: str  # '1h', '4h', '24h'
    model_version: str
    timestamp: datetime

class MLPredictiveEngine:
    """
    Machine Learning engine voor trading predictions
    """

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_history = []
        self.model_path = "data/ml_models"
        self.data_path = "data/market_data"

        # Maak directories
        os.makedirs(self.model_path, exist_ok=True)
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs("data", exist_ok=True)

        # Initialize modellen
        self.initialize_models()

    def print_message(self, message, msg_type="info"):
        """Print zonder Unicode issues"""
        if msg_type == "success":
            print(f"[SUCCESS] {message}")
        elif msg_type == "warning":
            print(f"[WARNING] {message}")
        elif msg_type == "error":
            print(f"[ERROR] {message}")
        elif msg_type == "alert":
            print(f"[ALERT] {message}")
        else:
            print(f"[INFO] {message}")

    def initialize_models(self):
        """Initialize verschillende ML modellen"""

        # Price direction classifier (up/down/sideways)
        self.models['price_direction'] = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            random_state=42
        )

        # Volatility predictor
        self.models['volatility'] = RandomForestRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )

        # Liquidity gap detector
        self.models['liquidity'] = RandomForestRegressor(
            n_estimators=50,
            max_depth=3,
            random_state=42
        )

        # Scalers voor data preprocessing
        self.scalers['price_direction'] = StandardScaler()
        self.scalers['volatility'] = MinMaxScaler()
        self.scalers['liquidity'] = StandardScaler()

        self.print_message("ML modellen geïnitialiseerd", "success")

    def generate_mock_market_data(self, days: int = 30) -> pd.DataFrame:
        """
        Genereer realistische mock data voor training
        In productie: vervang met echte market data API calls
        """

        data_points = days * 24  # Uurlijkse data

        timestamps = pd.date_range(
            start=datetime.now() - timedelta(days=days),
            end=datetime.now(),
            freq='1H'
        )

        # Genereer realistische prijsdata met trends en volatility
        np.random.seed(42)  # Voor reproduceerbare resultaten

        # BTC price simulatie
        base_price = 45000
        trend = np.random.normal(0.001, 0.005, data_points).cumsum()
        noise = np.random.normal(0, 0.02, data_points)
        prices = base_price * (1 + trend + noise)

        # Volume correlatie met price changes
        price_changes = np.diff(prices, prepend=prices[0])
        volumes = np.abs(price_changes) * 1000000 + np.random.normal(50000000, 20000000, data_points)
        volumes = np.maximum(volumes, 10000000)  # Min volume

        # Volatility (GARCH-style simulation)
        volatility = np.abs(price_changes) / prices[:-1] * np.sqrt(24)  # Daily vol
        volatility = np.concatenate([[0.025], volatility])  # Start met 2.5% vol

        # Market regime (0=sideeways, 1=uptrend, 2=downtrend, 3=chaotic)
        regimes = []
        current_regime = 0
        for i in range(data_points):
            if np.random.random() < 0.05:  # 5% kans op regime change
                current_regime = np.random.choice([0, 1, 2, 3])
            regimes.append(current_regime)

        # Funding rates
        funding_rates = np.random.normal(0.001, 0.002, data_points)
        funding_rates = np.clip(funding_rates, -0.01, 0.01)

        # Liquidity score
        liquidity = volumes / np.abs(price_changes + 0.001)  # Liquidity measure
        liquidity = liquidity / np.max(liquidity)  # Normalize

        df = pd.DataFrame({
            'timestamp': timestamps,
            'btc_price': prices,
            'btc_volume': volumes,
            'btc_volatility': volatility,
            'market_regime': regimes,
            'funding_rate': funding_rates,
            'liquidity_score': liquidity,
            'price_change': price_changes,
            'price_change_pct': price_changes / np.roll(prices, 1)
        })

        return df

    def extract_features(self, df: pd.DataFrame, lookback_hours: int = 24) -> pd.DataFrame:
        """
        Extract features voor ML modellen
        """
        features = df.copy()

        # Technical indicators
        for window in [6, 12, 24]:  # 6h, 12h, 24h windows
            features[f'price_ma_{window}'] = features['btc_price'].rolling(window=window).mean()
            features[f'volume_ma_{window}'] = features['btc_volume'].rolling(window=window).mean()
            features[f'vol_ma_{window}'] = features['btc_volatility'].rolling(window=window).mean()
            features[f'price_std_{window}'] = features['btc_price'].rolling(window=window).std()

            # Price momentum
            features[f'price_momentum_{window}'] = features['btc_price'] / features[f'price_ma_{window}'] - 1
            features[f'volume_ratio_{window}'] = features['btc_volume'] / features[f'volume_ma_{window}']

        # Volatility features
        features['volatility_trend'] = features['btc_volatility'].rolling(12).mean()
        features['volatility_change'] = features['btc_volatility'] - features['btc_volatility'].rolling(6).mean()

        # Market regime features
        regime_dummies = pd.get_dummies(features['market_regime'], prefix='regime')
        features = pd.concat([features, regime_dummies], axis=1)

        # Time-based features
        features['hour'] = pd.to_datetime(features['timestamp']).dt.hour
        features['day_of_week'] = pd.to_datetime(features['timestamp']).dt.dayofweek

        # Lag features
        for lag in [1, 3, 6, 12]:
            features[f'price_lag_{lag}'] = features['btc_price'].shift(lag)
            features[f'volume_lag_{lag}'] = features['btc_volume'].shift(lag)
            features[f'vol_lag_{lag}'] = features['btc_volatility'].shift(lag)

        # Fill NaN values
        features = features.fillna(method='bfill').fillna(0)

        return features

    def create_targets(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create target variables voor supervised learning
        """
        targets = df.copy()

        # Price direction target (0=down, 1=sideways, 2=up)
        future_returns = df['price_change_pct'].shift(-1)  # Next hour return

        # Define thresholds
        down_threshold = -0.005  # -0.5%
        up_threshold = 0.005     # +0.5%

        targets['price_direction'] = np.where(
            future_returns < down_threshold, 0,
            np.where(future_returns > up_threshold, 2, 1)
        )

        # Volatility target (next hour volatility)
        targets['future_volatility'] = df['btc_volatility'].shift(-1)

        # Liquidity gap target
        targets['future_liquidity'] = df['liquidity_score'].shift(-1)

        return targets

    def train_models(self):
        """
        Train alle ML modellen met historische data
        """
        self.print_message("Starten van ML model training...", "info")

        # Genereer training data
        df = self.generate_mock_market_data(days=90)  # 90 dagen data

        # Extract features en targets
        features = self.extract_features(df)
        targets = self.create_targets(df)

        # Remove NaN targets (laatste rij)
        valid_rows = ~targets[['price_direction', 'future_volatility', 'future_liquidity']].isna().any(axis=1)
        features_clean = features[valid_rows]
        targets_clean = targets[valid_rows]

        # Feature columns (non-target columns)
        feature_columns = [col for col in features_clean.columns
                          if col not in ['timestamp', 'price_direction', 'future_volatility', 'future_liquidity']]

        X = features_clean[feature_columns]

        results = {}

        # 1. Train price direction classifier
        y_direction = targets_clean['price_direction']

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_direction, test_size=0.2, random_state=42, stratify=y_direction
        )

        # Scale features
        X_train_scaled = self.scalers['price_direction'].fit_transform(X_train)
        X_test_scaled = self.scalers['price_direction'].transform(X_test)

        # Train model
        self.models['price_direction'].fit(X_train_scaled, y_train)

        # Evaluate
        y_pred = self.models['price_direction'].predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        results['price_direction'] = {
            'accuracy': accuracy,
            'samples': len(X_train)
        }

        # 2. Train volatility predictor
        y_volatility = targets_clean['future_volatility']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_volatility, test_size=0.2, random_state=42
        )

        X_train_scaled = self.scalers['volatility'].fit_transform(X_train)
        X_test_scaled = self.scalers['volatility'].transform(X_test)

        self.models['volatility'].fit(X_train_scaled, y_train)

        y_pred = self.models['volatility'].predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        results['volatility'] = {
            'mse': mse,
            'rmse': np.sqrt(mse),
            'samples': len(X_train)
        }

        # 3. Train liquidity predictor
        y_liquidity = targets_clean['future_liquidity']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_liquidity, test_size=0.2, random_state=42
        )

        X_train_scaled = self.scalers['liquidity'].fit_transform(X_train)
        X_test_scaled = self.scalers['liquidity'].transform(X_test)

        self.models['liquidity'].fit(X_train_scaled, y_train)

        y_pred = self.models['liquidity'].predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        results['liquidity'] = {
            'mse': mse,
            'rmse': np.sqrt(mse),
            'samples': len(X_train)
        }

        # Save models
        self.save_models()

        # Print results
        self.print_message("ML Training voltooid!", "success")
        print("\nTraining Resultaten:")
        print(f"Price Direction Accuracy: {results['price_direction']['accuracy']:.3f}")
        print(f"Volatility RMSE: {results['volatility']['rmse']:.4f}")
        print(f"Liquidity RMSE: {results['liquidity']['rmse']:.4f}")

        return results

    def save_models(self):
        """Save trained modellen naar disk"""
        for model_name, model in self.models.items():
            model_path = os.path.join(self.model_path, f"{model_name}.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)

        for scaler_name, scaler in self.scalers.items():
            scaler_path = os.path.join(self.model_path, f"scaler_{scaler_name}.pkl")
            with open(scaler_path, 'wb') as f:
                pickle.dump(scaler, f)

        self.print_message("Modellen opgeslagen", "success")

    def load_models(self):
        """Load getrainde modellen van disk"""
        try:
            for model_name in self.models.keys():
                model_path = os.path.join(self.model_path, f"{model_name}.pkl")
                if os.path.exists(model_path):
                    with open(model_path, 'rb') as f:
                        self.models[model_name] = pickle.load(f)

            for scaler_name in self.scalers.keys():
                scaler_path = os.path.join(self.model_path, f"scaler_{scaler_name}.pkl")
                if os.path.exists(scaler_path):
                    with open(scaler_path, 'rb') as f:
                        self.scalers[scaler_name] = pickle.load(f)

            self.print_message("Modellen geladen", "success")
            return True

        except Exception as e:
            self.print_message(f"Fout bij laden modellen: {e}", "error")
            return False

    def generate_predictions(self, current_data: Dict) -> List[MLPrediction]:
        """
        Genereer real-time predictions met ML modellen
        """
        predictions = []

        try:
            # Genereer features van current data
            # In productie: vervang met real-time feature extraction
            df = self.generate_mock_market_data(days=2)  # Laatste 2 dagen
            features = self.extract_features(df)

            # Get laatste rij (current data)
            current_features = features.iloc[-1:][[col for col in features.columns
                                                  if col not in ['timestamp']]]

            # 1. Price direction prediction
            if 'price_direction' in self.models:
                X_scaled = self.scalers['price_direction'].transform(current_features)
                pred_proba = self.models['price_direction'].predict_proba(X_scaled)[0]
                pred_class = self.models['price_direction'].predict(X_scaled)[0]

                confidence = max(pred_proba) * 100

                direction_map = {0: 'DOWN', 1: 'SIDEWAYS', 2: 'UP'}
                prediction_value = pred_class  # 0, 1, of 2

                predictions.append(MLPrediction(
                    token='BTC',
                    prediction_type='price_direction',
                    prediction=float(prediction_value),
                    confidence=confidence,
                    feature_importance=self.get_feature_importance('price_direction', current_features.columns),
                    prediction_horizon='1h',
                    model_version='v1.0',
                    timestamp=datetime.now()
                ))

            # 2. Volatility prediction
            if 'volatility' in self.models:
                X_scaled = self.scalers['volatility'].transform(current_features)
                vol_pred = self.models['volatility'].predict(X_scaled)[0]

                # Confidence based on prediction consistency
                confidence = max(0, min(100, (0.05 - abs(vol_pred - 0.025)) * 1000))  # Closer to 2.5% = higher confidence

                predictions.append(MLPrediction(
                    token='BTC',
                    prediction_type='volatility',
                    prediction=float(vol_pred),
                    confidence=confidence,
                    feature_importance=self.get_feature_importance('volatility', current_features.columns),
                    prediction_horizon='1h',
                    model_version='v1.0',
                    timestamp=datetime.now()
                ))

            # 3. Liquidity prediction
            if 'liquidity' in self.models:
                X_scaled = self.scalers['liquidity'].transform(current_features)
                liq_pred = self.models['liquidity'].predict(X_scaled)[0]

                confidence = liq_pred * 100  # Liquidity score * 100

                predictions.append(MLPrediction(
                    token='BTC',
                    prediction_type='liquidity',
                    prediction=float(liq_pred),
                    confidence=confidence,
                    feature_importance=self.get_feature_importance('liquidity', current_features.columns),
                    prediction_horizon='1h',
                    model_version='v1.0',
                    timestamp=datetime.now()
                ))

        except Exception as e:
            self.print_message(f"Fout bij genereren predictions: {e}", "error")

        return predictions

    def get_feature_importance(self, model_name: str, feature_names: List[str]) -> Dict[str, float]:
        """Get feature importance voor een model"""
        try:
            if hasattr(self.models[model_name], 'feature_importances_'):
                importances = self.models[model_name].feature_importances_

                # Map to feature names
                feature_importance = {}
                for i, importance in enumerate(importances):
                    if i < len(feature_names):
                        feature_importance[feature_names[i]] = float(importance)

                # Sort by importance
                return dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10])
            else:
                return {}
        except:
            return {}

    def print_predictions_dashboard(self, predictions: List[MLPrediction]):
        """Print ML predictions dashboard"""
        if not predictions:
            print("Geen ML predictions beschikbaar")
            return

        print(f"\nML PREDICTIONS DASHBOARD")
        print("=" * 60)

        for pred in predictions:
            pred_type = pred.prediction_type.replace('_', ' ').title()

            print(f"\n{pred.token} - {pred_type} ({pred.prediction_horizon})")
            print(f"Prediction: {pred.prediction:.4f}")
            print(f"Confidence: {pred.confidence:.1f}%")

            if pred.prediction_type == 'price_direction':
                direction_map = {0.0: 'DOWN', 1.0: 'SIDEWAYS', 2.0: 'UP'}
                direction = direction_map.get(pred.prediction, 'UNKNOWN')
                print(f"Direction: {direction}")
            elif pred.prediction_type == 'volatility':
                print(f"Expected Volatility: {pred.prediction:.3f} ({pred.prediction*100:.1f}%)")
            elif pred.prediction_type == 'liquidity':
                print(f"Liquidity Score: {pred.prediction:.3f}")

            # Show top 5 feature importance
            if pred.feature_importance:
                print("Top Features:")
                for feature, importance in list(pred.feature_importance.items())[:5]:
                    print(f"  {feature}: {importance:.3f}")

async def main():
    """Test de ML Predictive Engine"""
    print("ML PREDICTIVE ENGINE")
    print("=" * 40)
    print("Machine Learning voor voorspellende trading analyse")

    engine = MLPredictiveEngine()

    try:
        # Check of we getrainde modellen hebben
        if not engine.load_models():
            print("Geen getrainde modellen gevonden - starten met training...")
            training_results = engine.train_models()

        # Genereer predictions
        print("\nGenereren van ML predictions...")
        predictions = engine.generate_predictions({})

        # Print dashboard
        engine.print_predictions_dashboard(predictions)

        # Save predictions
        predictions_data = []
        for pred in predictions:
            pred_dict = {
                'timestamp': pred.timestamp.isoformat(),
                'token': pred.token,
                'prediction_type': pred.prediction_type,
                'prediction': pred.prediction,
                'confidence': pred.confidence,
                'prediction_horizon': pred.prediction_horizon,
                'model_version': pred.model_version,
                'feature_importance': pred.feature_importance
            }
            predictions_data.append(pred_dict)

        # Save to JSON
        os.makedirs("data/predictions", exist_ok=True)
        with open(f"data/predictions/ml_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(predictions_data, f, indent=2)

        print(f"\n[SUCCESS] {len(predictions)} ML predictions opgeslagen")

        return engine, predictions

    except Exception as e:
        engine.print_message(f"ML engine failed: {e}", "error")
        return engine, []

if __name__ == "__main__":
    engine, predictions = asyncio.run(main())