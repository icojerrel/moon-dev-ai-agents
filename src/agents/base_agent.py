"""
🌙 Moon Dev's Base Agent
Parent class for all trading agents
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd

class BaseAgent:
    def __init__(self, agent_type):
        """Initialize base agent with type"""
        self.type = agent_type
        self.start_time = datetime.now()
        
    def run(self):
        """Default run method - should be overridden by child classes"""
        raise NotImplementedError("Each agent must implement its own run method") 

if __name__ == "__main__":
    """Run agent standalone"""
    try:
        agent = Agent()
        agent.run()
    except KeyboardInterrupt:
        print("\n👋 Agent stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
