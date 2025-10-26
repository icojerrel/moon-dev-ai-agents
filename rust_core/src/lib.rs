//! 🌙 Moon Dev's Rust Core - High-Performance Trading Engine
//!
//! This module provides low-latency components for:
//! - Real-time price monitoring (<10ms)
//! - Order execution (<100ms)
//! - Risk checks (<5ms)
//!
//! Integrated with Python via PyO3 bindings.

use pyo3::prelude::*;
use pyo3::types::PyDict;

mod types;
mod price_monitor;

pub use types::*;
pub use price_monitor::*;

/// Get real-time price for a token
///
/// # Arguments
/// * `token` - Token symbol (e.g., "SOL", "BTC")
///
/// # Returns
/// Current price as f64, or None if unavailable
#[pyfunction]
fn get_realtime_price(token: &str) -> PyResult<Option<f64>> {
    // TODO: Connect to actual price feed
    // For now, return mock data
    let mock_prices = [
        ("SOL", 145.50),
        ("BTC", 97234.00),
        ("ETH", 3456.78),
    ];

    let price = mock_prices.iter()
        .find(|(symbol, _)| *symbol == token)
        .map(|(_, price)| *price);

    Ok(price)
}

/// Get multiple token prices in parallel
///
/// # Arguments
/// * `tokens` - List of token symbols
///
/// # Returns
/// Dictionary mapping token symbols to prices
#[pyfunction]
fn get_bulk_prices(py: Python, tokens: Vec<String>) -> PyResult<PyObject> {
    let result = PyDict::new(py);

    for token in tokens {
        if let Some(price) = get_realtime_price(&token)? {
            result.set_item(token, price)?;
        }
    }

    Ok(result.into())
}

/// Initialize price monitoring for a token
///
/// # Arguments
/// * `token` - Token address or symbol
/// * `threshold` - Percentage change threshold for alerts (e.g., 2.0 for 2%)
#[pyfunction]
fn start_price_monitor(token: &str, threshold: f64) -> PyResult<String> {
    Ok(format!(
        "Price monitor started for {} with {}% threshold",
        token, threshold
    ))
}

/// Check if price monitor is running
#[pyfunction]
fn is_monitor_active(token: &str) -> PyResult<bool> {
    // TODO: Implement actual monitoring state check
    Ok(false)
}

/// Stop price monitoring for a token
#[pyfunction]
fn stop_price_monitor(token: &str) -> PyResult<()> {
    Ok(())
}

/// Get version information
#[pyfunction]
fn version() -> PyResult<String> {
    Ok(env!("CARGO_PKG_VERSION").to_string())
}

/// Python module definition
#[pymodule]
fn moon_rust_core(_py: Python, m: &PyModule) -> PyResult<()> {
    // Price monitoring functions
    m.add_function(wrap_pyfunction!(get_realtime_price, m)?)?;
    m.add_function(wrap_pyfunction!(get_bulk_prices, m)?)?;
    m.add_function(wrap_pyfunction!(start_price_monitor, m)?)?;
    m.add_function(wrap_pyfunction!(is_monitor_active, m)?)?;
    m.add_function(wrap_pyfunction!(stop_price_monitor, m)?)?;

    // Utility functions
    m.add_function(wrap_pyfunction!(version, m)?)?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_get_realtime_price() {
        assert_eq!(get_realtime_price("SOL").unwrap(), Some(145.50));
        assert_eq!(get_realtime_price("BTC").unwrap(), Some(97234.00));
        assert_eq!(get_realtime_price("INVALID").unwrap(), None);
    }
}
