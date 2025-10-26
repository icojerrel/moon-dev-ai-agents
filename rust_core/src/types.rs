//! Common types and data structures for the trading system

use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

/// Price data point
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PriceData {
    pub token: String,
    pub price: f64,
    pub timestamp: DateTime<Utc>,
    pub volume_24h: Option<f64>,
    pub change_24h: Option<f64>,
}

/// Order side
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub enum OrderSide {
    Buy,
    Sell,
}

/// Order status
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub enum OrderStatus {
    Pending,
    PartiallyFilled,
    Filled,
    Cancelled,
    Failed,
}

/// Order parameters
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OrderParams {
    pub token: String,
    pub side: OrderSide,
    pub amount: f64,
    pub price: Option<f64>,  // None for market orders
}

/// Order result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OrderResult {
    pub order_id: String,
    pub status: OrderStatus,
    pub filled_amount: f64,
    pub average_price: f64,
    pub latency_ms: u64,
}

/// Price alert configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PriceAlert {
    pub token: String,
    pub threshold_percent: f64,
    pub last_price: f64,
    pub active: bool,
}
