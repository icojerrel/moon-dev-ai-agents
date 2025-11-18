#!/usr/bin/env python3
"""
COLLECTIVE INTELLIGENCE
========================

Agents die van elkaar leren en collectieve beslissingen nemen
Vervangt individuele silo's door samenwerkende intelligentie
"""

import asyncio
import json
import logging
import sqlite3
import redis
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MessageType(Enum):
    SIGNAL_BROADCAST = "signal_broadcast"
    PERFORMANCE_REPORT = "performance_report"
    RISK_ALERT = "risk_alert"
    MARKET_REGIME_CHANGE = "regime_change"
    LEARNING_UPDATE = "learning_update"
    COORDINATION_REQUEST = "coordination_request"

class AgentType(Enum):
    MARKET_ANALYZER = "market_analyzer"
    STRATEGY_GENERATOR = "strategy_generator"
    RISK_MANAGER = "risk_manager"
    EXECUTION_ENGINE = "execution_engine"
    PERFORMANCE_MONITOR = "performance_monitor"

@dataclass
class AgentMessage:
    """Communication bericht tussen agents"""
    message_id: str
    sender: AgentType
    receiver: Optional[AgentType]  # None = broadcast
    message_type: MessageType
    payload: Dict[str, Any]
    priority: int  # 1-10, hoger = belangrijker
    timestamp: datetime
    ttl_minutes: int = 60  # Time to live

@dataclass
class CollectiveInsight:
    """Collectieve inzichten van alle agents"""
    insight_id: str
    topic: str
    consensus_value: float
    confidence: float
    contributing_agents: List[AgentType]
    reasoning: str
    metadata: Dict[str, Any]
    timestamp: datetime

class CollectiveIntelligence:
    """
    Coördinatie systeem voor inter-agent communication en collective learning
    """

    def __init__(self):
        self.agent_id = f"collective_intelligence_{uuid.uuid4().hex[:8]}"
        self.active_agents = {}
        self.message_queue = []
        self.insights_database = []
        self.learning_history = []

        # Redis voor real-time communication (fallback: in-memory)
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            self.redis_client.ping()
            self.use_redis = True
            print("[COLLECTIVE] Redis connected - real-time communication enabled")
        except:
            self.use_redis = False
            self.message_store = {}  # In-memory fallback
            print("[COLLECTIVE] Redis unavailable - using in-memory communication")

        # Database setup
        self.db_path = "data/collective_intelligence.db"
        self.setup_database()

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

    def setup_database(self):
        """Setup database voor collective intelligence data"""
        import os
        os.makedirs("data", exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_messages (
                message_id TEXT PRIMARY KEY,
                sender TEXT,
                receiver TEXT,
                message_type TEXT,
                payload TEXT,
                priority INTEGER,
                timestamp TEXT,
                processed BOOLEAN
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collective_insights (
                insight_id TEXT PRIMARY KEY,
                topic TEXT,
                consensus_value REAL,
                confidence REAL,
                contributing_agents TEXT,
                reasoning TEXT,
                metadata TEXT,
                timestamp TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_performance (
                agent_id TEXT,
                timestamp TEXT,
                metric_type TEXT,
                metric_value REAL,
                context TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def register_agent(self, agent_type: AgentType, capabilities: List[str]):
        """Registreer een agent in het collective intelligence systeem"""
        self.active_agents[agent_type] = {
            'capabilities': capabilities,
            'last_seen': datetime.now(),
            'performance_score': 0.5,  # Start met neutrale score
            'message_count': 0
        }

        self.print_message(f"Agent {agent_type.value} geregistreerd met capabilities: {capabilities}", "success")

    def broadcast_message(self, sender: AgentType, message_type: MessageType, payload: Dict[str, Any], priority: int = 5):
        """Stuur bericht naar alle agents"""
        message = AgentMessage(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            sender=sender,
            receiver=None,  # Broadcast
            message_type=message_type,
            payload=payload,
            priority=priority,
            timestamp=datetime.now()
        )

        self.deliver_message(message)

    def send_message(self, sender: AgentType, receiver: AgentType, message_type: MessageType, payload: Dict[str, Any], priority: int = 5):
        """Stuur direct bericht naar specifieke agent"""
        message = AgentMessage(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            sender=sender,
            receiver=receiver,
            message_type=message_type,
            payload=payload,
            priority=priority,
            timestamp=datetime.now()
        )

        self.deliver_message(message)

    def deliver_message(self, message: AgentMessage):
        """Lever bericht aan bestemmelde agents"""
        # Store bericht
        self.message_queue.append(message)

        # Opslaan in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO agent_messages
            (message_id, sender, receiver, message_type, payload, priority, timestamp, processed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            message.message_id,
            message.sender.value,
            message.receiver.value if message.receiver else None,
            message.message_type.value,
            json.dumps(message.payload),
            message.priority,
            message.timestamp.isoformat(),
            False
        ))
        conn.commit()
        conn.close()

        # Redis voor real-time delivery
        if self.use_redis:
            redis_key = f"ci_message:{message.message_id}"
            self.redis_client.setex(redis_key, message.ttl_minutes * 60, json.dumps(asdict(message)))

        # Directe processing voor hoge priority berichten
        if message.priority >= 8:
            self.process_high_priority_message(message)

    def process_high_priority_message(self, message: AgentMessage):
        """Verwerk hoge priority berichten direct"""
        if message.message_type == MessageType.RISK_ALERT:
            self.print_message(f"URGENT RISK ALERT from {message.sender.value}: {message.payload}", "alert")
            # Broadcast naar alle agents
            self.coordinate_risk_response(message.payload)

        elif message.message_type == MessageType.MARKET_REGIME_CHANGE:
            self.print_message(f"REGIME CHANGE detected by {message.sender.value}: {message.payload}", "alert")
            # Update alle agent strategies
            self.coordinate_regime_adaptation(message.payload)

    def get_messages_for_agent(self, agent_type: AgentType, limit: int = 10) -> List[AgentMessage]:
        """Haal berichten op voor specifieke agent"""
        messages = []

        # Haal uit message queue
        for message in self.message_queue:
            if message.receiver is None or message.receiver == agent_type:
                messages.append(message)

        # Sorteer op priority en timestamp
        messages.sort(key=lambda x: (-x.priority, x.timestamp))

        return messages[:limit]

    def share_performance_update(self, agent_type: AgentType, performance_metrics: Dict[str, float]):
        """Deel performance metrics met andere agents"""
        payload = {
            'agent': agent_type.value,
            'metrics': performance_metrics,
            'timestamp': datetime.now().isoformat()
        }

        self.broadcast_message(agent_type, MessageType.PERFORMANCE_REPORT, payload, priority=3)

        # Update local agent performance
        if agent_type in self.active_agents:
            # Calculate performance score
            avg_performance = np.mean(list(performance_metrics.values()))
            self.active_agents[agent_type]['performance_score'] = max(0, min(1, avg_performance))
            self.active_agents[agent_type]['last_seen'] = datetime.now()

        # Opslaan in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for metric_type, metric_value in performance_metrics.items():
            cursor.execute('''
                INSERT INTO agent_performance
                (agent_id, timestamp, metric_type, metric_value, context)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                agent_type.value,
                datetime.now().isoformat(),
                metric_type,
                metric_value,
                json.dumps(payload)
            ))
        conn.commit()
        conn.close()

    def generate_collective_insight(self, topic: str, agent_contributions: Dict[AgentType, Any]) -> CollectiveInsight:
        """Genereer collectief inzicht van bijdragen van alle agents"""
        if not agent_contributions:
            return None

        # Calculate consensus (gewogen gemiddelde op basis van performance scores)
        total_weight = 0
        weighted_sum = 0
        contributing_agents = []

        for agent_type, contribution in agent_contributions.items():
            if agent_type in self.active_agents:
                weight = self.active_agents[agent_type]['performance_score']

                # Convert contribution to numeric value
                if isinstance(contribution, (int, float)):
                    numeric_value = contribution
                elif isinstance(contribution, dict) and 'value' in contribution:
                    numeric_value = contribution['value']
                else:
                    continue  # Skip non-numeric contributions

                weighted_sum += numeric_value * weight
                total_weight += weight
                contributing_agents.append(agent_type)

        if total_weight == 0:
            return None

        consensus_value = weighted_sum / total_weight

        # Confidence gebaseerd op aantal agents en alignment
        base_confidence = len(contributing_agents) / len(self.active_agents) * 100

        # Calculate agreement level
        values = []
        for agent_type, contribution in agent_contributions.items():
            if isinstance(contribution, (int, float)):
                values.append(contribution)
            elif isinstance(contribution, dict) and 'value' in contribution:
                values.append(contribution['value'])

        if len(values) > 1:
            std_dev = np.std(values)
            agreement_factor = max(0, 1 - std_dev)  # Lower std = higher agreement
        else:
            agreement_factor = 0.5

        confidence = base_confidence * agreement_factor

        # Generate reasoning
        reasoning = f"Collectieve analyse van {len(contributing_agents)} agents"
        if len(contributing_agents) >= 3:
            reasoning += " - Sterke consensus"

        insight = CollectiveInsight(
            insight_id=f"insight_{uuid.uuid4().hex[:8]}",
            topic=topic,
            consensus_value=consensus_value,
            confidence=confidence,
            contributing_agents=contributing_agents,
            reasoning=reasoning,
            metadata={
                'agent_count': len(contributing_agents),
                'raw_contributions': {agent.value: contrib for agent, contrib in agent_contributions.items()}
            },
            timestamp=datetime.now()
        )

        # Opslaan
        self.insights_database.append(insight)
        self.save_insight_to_db(insight)

        return insight

    def save_insight_to_db(self, insight: CollectiveInsight):
        """Save insight naar database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO collective_insights
            (insight_id, topic, consensus_value, confidence, contributing_agents, reasoning, metadata, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            insight.insight_id,
            insight.topic,
            insight.consensus_value,
            insight.confidence,
            json.dumps([agent.value for agent in insight.contributing_agents]),
            insight.reasoning,
            json.dumps(insight.metadata),
            insight.timestamp.isoformat()
        ))
        conn.commit()
        conn.close()

    def coordinate_risk_response(self, risk_alert: Dict[str, Any]):
        """Coördineer response op risico alerts"""
        response_actions = []

        # Inform risk manager
        if AgentType.RISK_MANAGER in self.active_agents:
            response_actions.append(f"Risk manager: {risk_alert.get('recommended_action', 'Monitor closely')}")

        # Adjust strategy generator parameters
        if AgentType.STRATEGY_GENERATOR in self.active_agents:
            response_actions.append("Strategy generator: Reduce position sizes by 50%")

        # Alert execution engine
        if AgentType.EXECUTION_ENGINE in self.active_agents:
            response_actions.append("Execution engine: Halt new positions until risk normalizes")

        # Broadcast coordinated response
        coordination_payload = {
            'risk_alert': risk_alert,
            'coordinated_actions': response_actions,
            'timestamp': datetime.now().isoformat()
        }

        self.broadcast_message(
            AgentType.RISK_MANAGER,
            MessageType.COORDINATION_REQUEST,
            coordination_payload,
            priority=9
        )

    def coordinate_regime_adaptation(self, regime_data: Dict[str, Any]):
        """Coördineer aanpassing aan nieuw market regime"""
        new_regime = regime_data.get('regime', 'UNKNOWN')
        regime_change_confidence = regime_data.get('confidence', 0.5)

        adaptations = []

        # Strategy adjustments per regime
        if new_regime == 'BULL':
            adaptations.extend([
                "Strategy generator: Increase long-biased strategies",
                "Risk manager: Relax volatility thresholds by 20%",
                "Execution engine: Increase position sizes gradually"
            ])
        elif new_regime == 'BEAR':
            adaptations.extend([
                "Strategy generator: Increase short-biased and defensive strategies",
                "Risk manager: Tighten stop losses by 15%",
                "Execution engine: Reduce maximum position sizes"
            ])
        elif new_regime == 'CHAOTIC':
            adaptations.extend([
                "Strategy generator: Focus on mean-reversion strategies",
                "Risk manager: Implement circuit breakers",
                "Execution engine: High-frequency micro-positioning only"
            ])

        # Broadcast adaptations
        adaptation_payload = {
            'regime': new_regime,
            'confidence': regime_change_confidence,
            'adaptations': adaptations,
            'timestamp': datetime.now().isoformat()
        }

        self.broadcast_message(
            AgentType.MARKET_ANALYZER,
            MessageType.COORDINATION_REQUEST,
            adaptation_payload,
            priority=8
        )

    def print_collective_dashboard(self):
        """Print dashboard van collective intelligence status"""
        print(f"\nCOLLECTIVE INTELLIGENCE DASHBOARD")
        print("=" * 60)

        # Active agents
        print(f"Active Agents: {len(self.active_agents)}/5")
        for agent_type, info in self.active_agents.items():
            status = "ACTIVE" if (datetime.now() - info['last_seen']).seconds < 300 else "IDLE"
            print(f"  {agent_type.value}: {status} | Performance: {info['performance_score']:.2f} | Messages: {info['message_count']}")

        # Recent insights
        recent_insights = self.insights_database[-5:]  # Last 5 insights
        if recent_insights:
            print(f"\nRecent Collective Insights:")
            for insight in recent_insights:
                print(f"  {insight.topic}: {insight.consensus_value:.3f} ({insight.confidence:.0f}% confidence)")
                print(f"    {insight.reasoning}")

        # Message queue
        pending_messages = len([m for m in self.message_queue if m.timestamp > datetime.now() - timedelta(minutes=30)])
        print(f"\nPending Messages: {pending_messages}")

        # Top performing agents
        if self.active_agents:
            top_agents = sorted(self.active_agents.items(), key=lambda x: x[1]['performance_score'], reverse=True)[:3]
            print(f"\nTop Performing Agents:")
            for agent_type, info in top_agents:
                print(f"  {agent_type.value}: {info['performance_score']:.2f}")

async def main():
    """Test de Collective Intelligence system"""
    print("COLLECTIVE INTELLIGENCE")
    print("=" * 40)
    print("Agents die van elkaar leren en samenwerken")

    ci = CollectiveIntelligence()

    try:
        # Registreer agents
        ci.register_agent(AgentType.MARKET_ANALYZER, ['price_analysis', 'volume_analysis', 'regime_detection'])
        ci.register_agent(AgentType.STRATEGY_GENERATOR, ['signal_generation', 'portfolio_optimization'])
        ci.register_agent(AgentType.RISK_MANAGER, ['risk_assessment', 'position_monitoring'])
        ci.register_agent(AgentType.EXECUTION_ENGINE, ['trade_execution', 'order_management'])
        ci.register_agent(AgentType.PERFORMANCE_MONITOR, ['metrics_collection', 'performance_analysis'])

        # Simulate agent interactions
        print("\n[DEMO] Simulating agent interactions...")

        # Market analyzer signals regime change
        ci.broadcast_message(
            AgentType.MARKET_ANALYZER,
            MessageType.MARKET_REGIME_CHANGE,
            {
                'regime': 'BULL',
                'confidence': 0.75,
                'btc_trend': 0.025,
                'volume_increase': 0.45
            },
            priority=8
        )

        # Strategy generator shares performance
        ci.share_performance_update(
            AgentType.STRATEGY_GENERATOR,
            {
                'win_rate': 0.62,
                'avg_return': 0.018,
                'sharpe_ratio': 1.34,
                'max_drawdown': 0.045
            }
        )

        # Risk manager shares risk metrics
        ci.share_performance_update(
            AgentType.RISK_MANAGER,
            {
                'portfolio_risk': 0.08,
                'var_95': 0.032,
                'correlation_risk': 0.65,
                'regime_adjustment': -0.15
            }
        )

        # Execution engine reports execution quality
        ci.share_performance_update(
            AgentType.EXECUTION_ENGINE,
            {
                'slippage_avg': 0.0045,
                'execution_time': 1.8,
                'fill_rate': 0.94,
                'cost_efficiency': 0.87
            }
        )

        # Generate collective insights
        print("\n[DEMO] Generating collective insights...")

        # Price direction insight
        price_contributions = {
            AgentType.MARKET_ANALYZER: {'value': 0.72, 'reasoning': 'Technical indicators bullish'},
            AgentType.STRATEGY_GENERATOR: {'value': 0.68, 'reasoning': 'Strategy backtests positive'},
            AgentType.EXECUTION_ENGINE: {'value': 0.65, 'reasoning': 'Order flow favorable'}
        }

        price_insight = ci.generate_collective_insight("btc_price_direction", price_contributions)

        # Risk level insight
        risk_contributions = {
            AgentType.RISK_MANAGER: {'value': 0.35, 'reasoning': 'Low portfolio risk'},
            AgentType.MARKET_ANALYZER: {'value': 0.42, 'reasoning': 'Moderate market volatility'},
            AgentType.PERFORMANCE_MONITOR: {'value': 0.38, 'reasoning': 'Stable performance metrics'}
        }

        risk_insight = ci.generate_collective_insight("portfolio_risk_level", risk_contributions)

        # Print dashboard
        ci.print_collective_dashboard()

        return ci

    except Exception as e:
        ci.print_message(f"Collective intelligence demo failed: {e}", "error")
        return ci

if __name__ == "__main__":
    ci = asyncio.run(main())