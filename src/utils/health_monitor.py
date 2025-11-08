"""
🌙 Moon Dev's Health Monitoring System
Built with love by Moon Dev 🚀

Monitors system health and sends alerts for issues:
- Agent heartbeats
- API connectivity
- Resource usage (CPU, memory, disk)
- Error rates
- Trade execution health
"""

import os
import sys
import time
import psutil
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import deque

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.utils.logger import get_logger
from src.utils.alerts import AlertLevel, system_alert, error_alert

logger = get_logger(__name__, 'health_monitor')


class HealthMonitor:
    """System health monitoring"""

    def __init__(
        self,
        check_interval: int = 300,  # 5 minutes
        cpu_threshold: float = 90.0,
        memory_threshold: float = 90.0,
        disk_threshold: float = 90.0,
        error_rate_threshold: float = 0.1,  # 10% error rate
    ):
        """
        Initialize health monitor

        Args:
            check_interval: Seconds between health checks
            cpu_threshold: CPU usage % threshold for alert
            memory_threshold: Memory usage % threshold
            disk_threshold: Disk usage % threshold
            error_rate_threshold: Error rate threshold (0-1)
        """
        self.check_interval = check_interval
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold
        self.error_rate_threshold = error_rate_threshold

        # Track agent heartbeats
        self.agent_heartbeats = {}

        # Track errors
        self.error_window = deque(maxlen=100)
        self.success_window = deque(maxlen=100)

        # Last alert times (to prevent spam)
        self.last_alerts = {}
        self.alert_cooldown = 3600  # 1 hour

        logger.info("Health monitor initialized")

    def check_system_resources(self) -> Dict[str, any]:
        """
        Check system resource usage

        Returns:
            Dict with resource metrics
        """
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent

            # Network stats (if available)
            try:
                net_io = psutil.net_io_counters()
                network_stats = {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                }
            except:
                network_stats = {}

            metrics = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk_percent,
                'disk_free_gb': disk.free / (1024**3),
                **network_stats
            }

            # Check thresholds
            if cpu_percent > self.cpu_threshold:
                self._send_alert_throttled(
                    'high_cpu',
                    f"High CPU usage: {cpu_percent:.1f}%",
                    AlertLevel.WARNING,
                    cpu_usage=f"{cpu_percent:.1f}%"
                )

            if memory_percent > self.memory_threshold:
                self._send_alert_throttled(
                    'high_memory',
                    f"High memory usage: {memory_percent:.1f}%",
                    AlertLevel.WARNING,
                    memory_usage=f"{memory_percent:.1f}%",
                    available_memory=f"{memory.available / (1024**3):.2f} GB"
                )

            if disk_percent > self.disk_threshold:
                self._send_alert_throttled(
                    'high_disk',
                    f"High disk usage: {disk_percent:.1f}%",
                    AlertLevel.CRITICAL,
                    disk_usage=f"{disk_percent:.1f}%",
                    disk_free=f"{disk.free / (1024**3):.2f} GB"
                )

            return metrics

        except Exception as e:
            logger.error(f"Error checking system resources: {str(e)}", exc_info=True)
            return {}

    def check_api_health(self) -> Dict[str, bool]:
        """
        Check health of external APIs

        Returns:
            Dict of API name -> is_healthy
        """
        apis = {
            'BirdEye': os.getenv('BIRDEYE_API_KEY'),
            'CoinGecko': os.getenv('COINGECKO_API_KEY'),
        }

        results = {}

        for api_name, api_key in apis.items():
            if not api_key:
                continue

            try:
                if api_name == 'BirdEye':
                    # Test BirdEye API
                    response = requests.get(
                        'https://public-api.birdeye.so/public/tokenlist',
                        headers={'X-API-KEY': api_key},
                        timeout=10
                    )
                    results[api_name] = response.status_code == 200

                elif api_name == 'CoinGecko':
                    # Test CoinGecko API
                    response = requests.get(
                        'https://api.coingecko.com/api/v3/ping',
                        timeout=10
                    )
                    results[api_name] = response.status_code == 200

            except Exception as e:
                logger.warning(f"{api_name} API health check failed: {str(e)}")
                results[api_name] = False

                self._send_alert_throttled(
                    f'api_{api_name.lower()}',
                    f"{api_name} API is unreachable",
                    AlertLevel.ERROR,
                    api=api_name,
                    error=str(e)
                )

        return results

    def check_log_errors(self) -> Dict[str, any]:
        """
        Check recent logs for errors

        Returns:
            Dict with error statistics
        """
        try:
            log_dir = Path(__file__).parent.parent.parent / 'logs'
            error_log = log_dir / 'moondev_errors.log'

            if not error_log.exists():
                return {'error_count': 0, 'recent_errors': []}

            # Read last 100 lines
            with open(error_log, 'r') as f:
                lines = f.readlines()
                recent_lines = lines[-100:] if len(lines) > 100 else lines

            # Count errors in last hour
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_errors = []

            for line in recent_lines:
                try:
                    # Parse timestamp (assuming format: YYYY-MM-DD HH:MM:SS)
                    if len(line) > 19:
                        timestamp_str = line[:19]
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

                        if timestamp > one_hour_ago:
                            recent_errors.append(line.strip())
                except:
                    continue

            error_count = len(recent_errors)

            # Alert if too many errors
            if error_count > 10:
                self._send_alert_throttled(
                    'high_error_rate',
                    f"High error rate detected: {error_count} errors in last hour",
                    AlertLevel.ERROR,
                    error_count=error_count
                )

            return {
                'error_count': error_count,
                'recent_errors': recent_errors[-5:]  # Last 5 errors
            }

        except Exception as e:
            logger.error(f"Error checking logs: {str(e)}", exc_info=True)
            return {'error_count': 0, 'recent_errors': []}

    def record_agent_heartbeat(self, agent_name: str):
        """Record agent heartbeat"""
        self.agent_heartbeats[agent_name] = datetime.now()

    def check_agent_heartbeats(self, timeout_minutes: int = 30) -> Dict[str, bool]:
        """
        Check if agents are still alive

        Args:
            timeout_minutes: Minutes without heartbeat before considering dead

        Returns:
            Dict of agent_name -> is_alive
        """
        cutoff_time = datetime.now() - timedelta(minutes=timeout_minutes)
        results = {}

        for agent_name, last_heartbeat in self.agent_heartbeats.items():
            is_alive = last_heartbeat > cutoff_time
            results[agent_name] = is_alive

            if not is_alive:
                self._send_alert_throttled(
                    f'agent_{agent_name}_dead',
                    f"Agent {agent_name} appears to be dead",
                    AlertLevel.CRITICAL,
                    agent=agent_name,
                    last_heartbeat=last_heartbeat.strftime('%Y-%m-%d %H:%M:%S')
                )

        return results

    def _send_alert_throttled(
        self,
        alert_key: str,
        message: str,
        level: AlertLevel,
        **data
    ):
        """
        Send alert with cooldown to prevent spam

        Args:
            alert_key: Unique key for this alert type
            message: Alert message
            level: Alert level
            **data: Additional data
        """
        now = datetime.now()
        last_alert = self.last_alerts.get(alert_key)

        # Check if enough time has passed
        if last_alert and (now - last_alert).total_seconds() < self.alert_cooldown:
            return

        # Send alert
        system_alert(message, level, **data)
        self.last_alerts[alert_key] = now

    def run_health_check(self) -> Dict[str, any]:
        """
        Run complete health check

        Returns:
            Dict with all health metrics
        """
        logger.info("Running health check...")

        health_report = {
            'timestamp': datetime.now().isoformat(),
            'system_resources': self.check_system_resources(),
            'api_health': self.check_api_health(),
            'log_errors': self.check_log_errors(),
            'agent_heartbeats': {
                name: heartbeat.isoformat()
                for name, heartbeat in self.agent_heartbeats.items()
            }
        }

        # Log summary
        logger.info(
            f"Health check complete - "
            f"CPU: {health_report['system_resources'].get('cpu_percent', 0):.1f}% | "
            f"Memory: {health_report['system_resources'].get('memory_percent', 0):.1f}% | "
            f"Errors: {health_report['log_errors'].get('error_count', 0)}"
        )

        return health_report

    def run_continuous(self):
        """Run health monitoring continuously"""
        logger.info(f"Starting continuous health monitoring (interval: {self.check_interval}s)")

        # Send startup alert
        system_alert(
            "Health monitoring system started",
            AlertLevel.SUCCESS,
            check_interval=f"{self.check_interval}s"
        )

        try:
            while True:
                self.run_health_check()
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("Health monitoring stopped by user")
            system_alert(
                "Health monitoring system stopped",
                AlertLevel.INFO
            )
        except Exception as e:
            logger.error(f"Health monitoring error: {str(e)}", exc_info=True)
            error_alert(
                "Health monitoring system crashed",
                context="HealthMonitor",
                exception=e
            )
            raise


if __name__ == "__main__":
    """Run health monitor standalone"""
    print("🌙 Moon Dev Health Monitor\n")

    # Create monitor
    monitor = HealthMonitor(
        check_interval=int(os.getenv('HEALTH_CHECK_INTERVAL', 300)),
        cpu_threshold=float(os.getenv('CPU_THRESHOLD', 90.0)),
        memory_threshold=float(os.getenv('MEMORY_THRESHOLD', 90.0)),
        disk_threshold=float(os.getenv('DISK_THRESHOLD', 90.0)),
    )

    # Run continuous monitoring
    monitor.run_continuous()
