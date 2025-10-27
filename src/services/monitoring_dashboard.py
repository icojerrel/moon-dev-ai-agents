#!/usr/bin/env python3
"""
🌙 Moon Dev's Monitoring Dashboard 🌙

Real-time web-based monitoring for the trading system

Features:
- Live price updates
- System metrics
- Trade history
- Risk monitoring
- Performance graphs

Usage:
    python src/services/monitoring_dashboard.py

    # Then open browser to: http://localhost:5000
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add project root to path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from flask import Flask, render_template_string, jsonify, request
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("⚠️  Flask not installed. Install with: pip install flask flask-cors")

from src import config


app = Flask(__name__)
if FLASK_AVAILABLE:
    CORS(app)


# HTML Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌙 Moon Dev Trading Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 30px;
        }

        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .status {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            background: #4CAF50;
            font-weight: bold;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }

        .card h2 {
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 2px solid rgba(255, 255, 255, 0.3);
            padding-bottom: 10px;
        }

        .metric {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 10px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
        }

        .metric-label {
            font-weight: 600;
        }

        .metric-value {
            font-family: 'Courier New', monospace;
            font-weight: bold;
        }

        .positive {
            color: #4CAF50;
        }

        .negative {
            color: #f44336;
        }

        .price-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            margin: 8px 0;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            transition: all 0.3s;
        }

        .price-item:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        .token-symbol {
            font-weight: bold;
            font-size: 1.2em;
        }

        .price {
            font-family: 'Courier New', monospace;
            font-size: 1.1em;
        }

        .change {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.9em;
        }

        footer {
            text-align: center;
            margin-top: 30px;
            opacity: 0.7;
        }

        .refresh-btn {
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
        }

        .refresh-btn:hover {
            background: rgba(255, 255, 255, 0.3);
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .updating {
            animation: pulse 1s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌙 Moon Dev Trading Dashboard</h1>
            <div class="status" id="status">● RUNNING</div>
            <p style="margin-top: 10px;">Real-time monitoring • Last update: <span id="last-update">--:--:--</span></p>
        </header>

        <div class="grid">
            <!-- System Metrics -->
            <div class="card">
                <h2>⚡ System Metrics</h2>
                <div class="metric">
                    <span class="metric-label">Uptime</span>
                    <span class="metric-value" id="uptime">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Cycles Completed</span>
                    <span class="metric-value" id="cycles">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Avg Cycle Time</span>
                    <span class="metric-value" id="cycle-time">-- ms</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Errors</span>
                    <span class="metric-value" id="errors">0</span>
                </div>
            </div>

            <!-- Trading Metrics -->
            <div class="card">
                <h2>📊 Trading Metrics</h2>
                <div class="metric">
                    <span class="metric-label">Today's PnL</span>
                    <span class="metric-value positive" id="pnl">$0.00</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Trades Today</span>
                    <span class="metric-value" id="trades">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Win Rate</span>
                    <span class="metric-value" id="win-rate">0%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Current Balance</span>
                    <span class="metric-value" id="balance">$--</span>
                </div>
            </div>

            <!-- Risk Metrics -->
            <div class="card">
                <h2>🛡️ Risk Management</h2>
                <div class="metric">
                    <span class="metric-label">Max Loss Limit</span>
                    <span class="metric-value" id="max-loss">$1,000</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Position Limit</span>
                    <span class="metric-value" id="pos-limit">20%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Active Positions</span>
                    <span class="metric-value" id="positions">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Risk Status</span>
                    <span class="metric-value positive" id="risk-status">SAFE</span>
                </div>
            </div>
        </div>

        <!-- Live Prices -->
        <div class="card">
            <h2>💹 Live Prices</h2>
            <div id="prices-container">
                <p style="text-align: center; padding: 20px;">Loading prices...</p>
            </div>
        </div>

        <div style="text-align: center; margin-top: 20px;">
            <button class="refresh-btn" onclick="updateDashboard()">🔄 Refresh Now</button>
            <p style="margin-top: 10px; opacity: 0.7;">Auto-refresh every 5 seconds</p>
        </div>

        <footer>
            <p>🌙 Moon Dev AI Trading System v2.0 • Hybrid Python+Rust Architecture</p>
            <p>Made with ❤️ by Moon Dev</p>
        </footer>
    </div>

    <script>
        let updateInterval;

        async function updateDashboard() {
            try {
                const response = await fetch('/api/metrics');
                const data = await response.json();

                // Update timestamp
                document.getElementById('last-update').textContent = new Date().toLocaleTimeString();

                // System metrics
                document.getElementById('uptime').textContent = data.uptime || '--';
                document.getElementById('cycles').textContent = data.cycles_completed || 0;
                document.getElementById('cycle-time').textContent = (data.avg_cycle_time_ms || 0).toFixed(0) + ' ms';
                document.getElementById('errors').textContent = data.errors || 0;

                // Trading metrics
                const pnl = data.pnl || 0;
                const pnlElem = document.getElementById('pnl');
                pnlElem.textContent = '$' + pnl.toFixed(2);
                pnlElem.className = 'metric-value ' + (pnl >= 0 ? 'positive' : 'negative');

                document.getElementById('trades').textContent = data.trades || 0;
                document.getElementById('win-rate').textContent = (data.win_rate || 0).toFixed(1) + '%';
                document.getElementById('balance').textContent = '$' + (data.balance || 0).toFixed(2);

                // Risk metrics
                document.getElementById('max-loss').textContent = '$' + (data.max_loss || 1000).toLocaleString();
                document.getElementById('pos-limit').textContent = (data.position_limit || 20) + '%';
                document.getElementById('positions').textContent = data.active_positions || 0;

                const riskStatus = data.risk_status || 'UNKNOWN';
                const riskElem = document.getElementById('risk-status');
                riskElem.textContent = riskStatus;
                riskElem.className = 'metric-value ' + (riskStatus === 'SAFE' ? 'positive' : 'negative');

                // Prices
                if (data.prices) {
                    const pricesHTML = Object.entries(data.prices).map(([token, priceData]) => {
                        const change = priceData.change || 0;
                        const changeClass = change >= 0 ? 'positive' : 'negative';

                        return `
                            <div class="price-item">
                                <span class="token-symbol">${token}</span>
                                <span class="price">$${priceData.price.toFixed(4)}</span>
                                <span class="change ${changeClass}">${change >= 0 ? '+' : ''}${change.toFixed(2)}%</span>
                            </div>
                        `;
                    }).join('');

                    document.getElementById('prices-container').innerHTML = pricesHTML || '<p style="text-align: center;">No price data available</p>';
                }

            } catch (error) {
                console.error('Update failed:', error);
                document.getElementById('status').textContent = '● ERROR';
                document.getElementById('status').style.background = '#f44336';
            }
        }

        // Initial update
        updateDashboard();

        // Auto-refresh every 5 seconds
        updateInterval = setInterval(updateDashboard, 5000);
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Dashboard home page"""
    return render_template_string(DASHBOARD_HTML)


@app.route('/api/metrics')
def get_metrics():
    """Get current system metrics (API endpoint)"""

    # Try to get real metrics from async orchestrator
    # This is a simplified version - in production, you'd have a shared state
    metrics = {
        "uptime": "N/A",
        "cycles_completed": 0,
        "avg_cycle_time_ms": 0,
        "errors": 0,
        "pnl": 0,
        "trades": 0,
        "win_rate": 0,
        "balance": 0,
        "max_loss": getattr(config, 'MAX_LOSS_USD', 1000),
        "position_limit": getattr(config, 'MAX_POSITION_PERCENTAGE', 20),
        "active_positions": 0,
        "risk_status": "SAFE",
        "prices": {}
    }

    # Try to get live prices
    try:
        from src.nice_funcs import token_price

        tokens = getattr(config, 'MONITORED_TOKENS', ['SOL', 'BTC', 'ETH'])

        for token in tokens[:5]:  # Limit to 5 tokens
            try:
                price = token_price(token)
                if price:
                    metrics["prices"][token] = {
                        "price": price,
                        "change": 0  # Would need historical data for real change %
                    }
            except Exception:
                pass

    except Exception as e:
        print(f"Error fetching prices: {e}")

    return jsonify(metrics)


def run_dashboard(host='0.0.0.0', port=5000, debug=False):
    """
    Run the monitoring dashboard

    Args:
        host: Host to bind to
        port: Port to listen on
        debug: Enable Flask debug mode
    """
    if not FLASK_AVAILABLE:
        print("❌ Flask not available. Install with:")
        print("   pip install flask flask-cors")
        return

    print("\n" + "="*70)
    print("🌙 Moon Dev Monitoring Dashboard")
    print("="*70 + "\n")
    print(f"🌐 Dashboard running at: http://localhost:{port}")
    print(f"📊 API endpoint: http://localhost:{port}/api/metrics")
    print("\n Press Ctrl+C to stop\n")

    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_dashboard(debug=True)
