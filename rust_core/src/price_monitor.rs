//! Real-time price monitoring service
//!
//! Monitors multiple tokens simultaneously with WebSocket connections
//! and triggers alerts on significant price changes.

use crate::types::{PriceData, PriceAlert};
use chrono::Utc;
use std::collections::HashMap;
use std::sync::{Arc, RwLock};

/// Global price monitor state
pub struct PriceMonitor {
    /// Active price alerts
    alerts: Arc<RwLock<HashMap<String, PriceAlert>>>,

    /// Latest prices
    prices: Arc<RwLock<HashMap<String, PriceData>>>,
}

impl PriceMonitor {
    /// Create a new price monitor
    pub fn new() -> Self {
        Self {
            alerts: Arc::new(RwLock::new(HashMap::new())),
            prices: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    /// Add a price alert
    pub fn add_alert(&self, token: String, threshold_percent: f64) -> Result<(), String> {
        let mut alerts = self.alerts.write().map_err(|e| e.to_string())?;

        let alert = PriceAlert {
            token: token.clone(),
            threshold_percent,
            last_price: 0.0,  // Will be set on first price update
            active: true,
        };

        alerts.insert(token, alert);
        Ok(())
    }

    /// Remove a price alert
    pub fn remove_alert(&self, token: &str) -> Result<(), String> {
        let mut alerts = self.alerts.write().map_err(|e| e.to_string())?;
        alerts.remove(token);
        Ok(())
    }

    /// Update price and check for alerts
    pub fn update_price(&self, token: String, price: f64) -> Result<Option<f64>, String> {
        // Update prices cache
        let price_data = PriceData {
            token: token.clone(),
            price,
            timestamp: Utc::now(),
            volume_24h: None,
            change_24h: None,
        };

        let mut prices = self.prices.write().map_err(|e| e.to_string())?;
        prices.insert(token.clone(), price_data);

        // Check for alerts
        let mut alerts = self.alerts.write().map_err(|e| e.to_string())?;

        if let Some(alert) = alerts.get_mut(&token) {
            if alert.last_price > 0.0 {
                let change_percent = ((price - alert.last_price) / alert.last_price) * 100.0;

                if change_percent.abs() >= alert.threshold_percent {
                    alert.last_price = price;
                    return Ok(Some(change_percent));
                }
            } else {
                // First price update
                alert.last_price = price;
            }
        }

        Ok(None)
    }

    /// Get current price for a token
    pub fn get_price(&self, token: &str) -> Result<Option<f64>, String> {
        let prices = self.prices.read().map_err(|e| e.to_string())?;
        Ok(prices.get(token).map(|p| p.price))
    }

    /// Get all monitored tokens
    pub fn get_monitored_tokens(&self) -> Result<Vec<String>, String> {
        let alerts = self.alerts.read().map_err(|e| e.to_string())?;
        Ok(alerts.keys().cloned().collect())
    }
}

impl Default for PriceMonitor {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_price_monitor_basic() {
        let monitor = PriceMonitor::new();

        // Add alert
        assert!(monitor.add_alert("SOL".to_string(), 2.0).is_ok());

        // First update
        let result = monitor.update_price("SOL".to_string(), 100.0);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), None); // No alert on first update

        // Small change (should not trigger)
        let result = monitor.update_price("SOL".to_string(), 101.0);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), None);

        // Large change (should trigger)
        let result = monitor.update_price("SOL".to_string(), 103.0);
        assert!(result.is_ok());
        assert!(result.unwrap().is_some());
    }

    #[test]
    fn test_get_price() {
        let monitor = PriceMonitor::new();
        monitor.update_price("SOL".to_string(), 145.50).unwrap();

        let price = monitor.get_price("SOL").unwrap();
        assert_eq!(price, Some(145.50));

        let missing = monitor.get_price("BTC").unwrap();
        assert_eq!(missing, None);
    }
}
