"""
🌙 Moon Dev's Code Review ML/RL Module
Machine Learning and Reinforcement Learning for code review improvement

Features:
- Learn from review feedback (accepted/rejected suggestions)
- Track review quality metrics over time
- Adaptive review strategies based on historical data
- Pattern recognition for common issues
- Reward-based learning from user feedback

Created with ❤️ by Moon Dev
"""

import os
import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import numpy as np
from termcolor import cprint

# Training data storage
TRAINING_DATA_DIR = Path(__file__).parent.parent / "data" / "code_review" / "training"
TRAINING_DATA_DIR.mkdir(parents=True, exist_ok=True)

FEEDBACK_FILE = TRAINING_DATA_DIR / "feedback.jsonl"
METRICS_FILE = TRAINING_DATA_DIR / "metrics.json"
MODEL_FILE = TRAINING_DATA_DIR / "review_model.pkl"

class CodeReviewRL:
    """Reinforcement Learning for code review optimization"""

    def __init__(self):
        """Initialize RL system"""
        self.q_table = self._load_q_table()
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.2  # Exploration rate

        # State features
        self.states = {
            'file_type': ['agent', 'strategy', 'util', 'model', 'other'],
            'issue_type': ['security', 'performance', 'style', 'best_practices'],
            'severity': ['critical', 'high', 'medium', 'low']
        }

        # Actions (review strategies)
        self.actions = {
            'detailed': 'Provide detailed, comprehensive review',
            'focused': 'Focus on high-severity issues only',
            'quick': 'Quick scan for critical issues',
            'educational': 'Include explanations and examples'
        }

    def _load_q_table(self) -> Dict:
        """Load Q-table from disk"""
        q_file = TRAINING_DATA_DIR / "q_table.pkl"
        if q_file.exists():
            try:
                with open(q_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                cprint(f"⚠️ Failed to load Q-table: {e}", "yellow")

        # Initialize empty Q-table
        return defaultdict(lambda: defaultdict(float))

    def _save_q_table(self):
        """Save Q-table to disk"""
        q_file = TRAINING_DATA_DIR / "q_table.pkl"
        try:
            with open(q_file, 'wb') as f:
                pickle.dump(dict(self.q_table), f)
        except Exception as e:
            cprint(f"❌ Failed to save Q-table: {e}", "red")

    def get_state(self, file_path: str, issue_type: str, severity: str) -> str:
        """Convert review context to state string"""
        # Determine file type
        if 'agent' in file_path:
            file_type = 'agent'
        elif 'strategy' in file_path:
            file_type = 'strategy'
        elif 'util' in file_path or 'nice_func' in file_path:
            file_type = 'util'
        elif 'model' in file_path:
            file_type = 'model'
        else:
            file_type = 'other'

        return f"{file_type}_{issue_type}_{severity}"

    def choose_action(self, state: str) -> str:
        """Choose review action based on current policy (epsilon-greedy)"""
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(list(self.actions.keys()))
        else:
            # Exploit: best known action
            if state in self.q_table:
                return max(self.q_table[state], key=self.q_table[state].get)
            return 'detailed'  # Default action

    def update_q_value(self, state: str, action: str, reward: float, next_state: Optional[str] = None):
        """Update Q-value based on feedback"""
        current_q = self.q_table[state][action]

        if next_state and next_state in self.q_table:
            max_next_q = max(self.q_table[next_state].values()) if self.q_table[next_state] else 0
        else:
            max_next_q = 0

        # Q-learning update rule
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )

        self.q_table[state][action] = new_q
        self._save_q_table()

    def get_reward_from_feedback(self, feedback: str, was_applied: bool) -> float:
        """Calculate reward from user feedback"""
        rewards = {
            'excellent': 10.0,
            'good': 5.0,
            'ok': 2.0,
            'poor': -2.0,
            'wrong': -5.0
        }

        base_reward = rewards.get(feedback, 0.0)

        # Bonus if suggestion was actually applied
        if was_applied:
            base_reward *= 1.5

        return base_reward


class CodeReviewML:
    """Machine Learning for pattern recognition and quality prediction"""

    def __init__(self):
        """Initialize ML system"""
        self.patterns = self._load_patterns()
        self.metrics = self._load_metrics()

    def _load_patterns(self) -> Dict:
        """Load learned patterns from disk"""
        pattern_file = TRAINING_DATA_DIR / "patterns.json"
        if pattern_file.exists():
            try:
                with open(pattern_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                cprint(f"⚠️ Failed to load patterns: {e}", "yellow")

        return {
            'common_issues': defaultdict(int),
            'issue_correlations': {},
            'file_risk_scores': {},
            'developer_patterns': {}
        }

    def _save_patterns(self):
        """Save learned patterns to disk"""
        pattern_file = TRAINING_DATA_DIR / "patterns.json"
        try:
            # Convert defaultdict to regular dict for JSON serialization
            patterns_dict = {
                'common_issues': dict(self.patterns['common_issues']),
                'issue_correlations': self.patterns['issue_correlations'],
                'file_risk_scores': self.patterns['file_risk_scores'],
                'developer_patterns': self.patterns['developer_patterns']
            }
            with open(pattern_file, 'w') as f:
                json.dump(patterns_dict, f, indent=2)
        except Exception as e:
            cprint(f"❌ Failed to save patterns: {e}", "red")

    def _load_metrics(self) -> Dict:
        """Load historical metrics"""
        if METRICS_FILE.exists():
            try:
                with open(METRICS_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                cprint(f"⚠️ Failed to load metrics: {e}", "yellow")

        return {
            'total_reviews': 0,
            'total_issues': 0,
            'acceptance_rate': 0.0,
            'avg_score': 0.0,
            'reviews_by_type': defaultdict(int),
            'issues_by_severity': defaultdict(int)
        }

    def _save_metrics(self):
        """Save metrics to disk"""
        try:
            # Convert defaultdicts to regular dicts
            metrics_dict = {
                'total_reviews': self.metrics['total_reviews'],
                'total_issues': self.metrics['total_issues'],
                'acceptance_rate': self.metrics['acceptance_rate'],
                'avg_score': self.metrics['avg_score'],
                'reviews_by_type': dict(self.metrics.get('reviews_by_type', {})),
                'issues_by_severity': dict(self.metrics.get('issues_by_severity', {})),
                'last_updated': datetime.now().isoformat()
            }
            with open(METRICS_FILE, 'w') as f:
                json.dump(metrics_dict, f, indent=2)
        except Exception as e:
            cprint(f"❌ Failed to save metrics: {e}", "red")

    def learn_from_review(self, review: Dict, feedback: Optional[Dict] = None):
        """Learn patterns from completed review"""
        # Update issue frequency
        for issue in review.get('issues', []):
            issue_type = issue.get('type', 'unknown')
            severity = issue.get('severity', 'unknown')

            self.patterns['common_issues'][issue_type] += 1
            self.metrics['issues_by_severity'][severity] = \
                self.metrics['issues_by_severity'].get(severity, 0) + 1

        # Update file risk score
        file_path = review.get('file', '')
        issue_count = len(review.get('issues', []))

        if file_path not in self.patterns['file_risk_scores']:
            self.patterns['file_risk_scores'][file_path] = {
                'reviews': 0,
                'avg_issues': 0.0,
                'last_review': None
            }

        file_data = self.patterns['file_risk_scores'][file_path]
        file_data['reviews'] += 1
        file_data['avg_issues'] = (
            (file_data['avg_issues'] * (file_data['reviews'] - 1) + issue_count)
            / file_data['reviews']
        )
        file_data['last_review'] = datetime.now().isoformat()

        # Update global metrics
        self.metrics['total_reviews'] += 1
        self.metrics['total_issues'] += issue_count
        self.metrics['reviews_by_type'][review.get('review_type', 'unknown')] = \
            self.metrics['reviews_by_type'].get(review.get('review_type', 'unknown'), 0) + 1

        if review.get('score'):
            current_avg = self.metrics['avg_score']
            total = self.metrics['total_reviews']
            self.metrics['avg_score'] = (
                (current_avg * (total - 1) + review['score']) / total
            )

        # Learn from feedback if provided
        if feedback:
            accepted = feedback.get('accepted', 0)
            rejected = feedback.get('rejected', 0)
            total_suggestions = accepted + rejected

            if total_suggestions > 0:
                current_rate = self.metrics['acceptance_rate']
                current_total = self.metrics['total_reviews']

                # Update acceptance rate
                self.metrics['acceptance_rate'] = (
                    (current_rate * (current_total - 1) + (accepted / total_suggestions))
                    / current_total
                )

        self._save_patterns()
        self._save_metrics()

    def predict_file_risk(self, file_path: str) -> float:
        """Predict risk score for a file based on historical data"""
        if file_path in self.patterns['file_risk_scores']:
            return self.patterns['file_risk_scores'][file_path]['avg_issues']

        # Predict based on file type
        if 'trading' in file_path or 'risk' in file_path:
            return 5.0  # High risk
        elif 'agent' in file_path:
            return 3.0  # Medium risk
        else:
            return 2.0  # Low risk

    def get_common_issues(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """Get most common issue types"""
        issues = self.patterns['common_issues']
        if isinstance(issues, dict):
            return sorted(issues.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return []

    def get_review_statistics(self) -> Dict:
        """Get comprehensive review statistics"""
        return {
            'total_reviews': self.metrics['total_reviews'],
            'total_issues': self.metrics['total_issues'],
            'acceptance_rate': f"{self.metrics['acceptance_rate']*100:.1f}%",
            'avg_score': f"{self.metrics['avg_score']:.1f}/100",
            'reviews_by_type': dict(self.metrics.get('reviews_by_type', {})),
            'issues_by_severity': dict(self.metrics.get('issues_by_severity', {})),
            'top_issues': self.get_common_issues(5)
        }


class FeedbackCollector:
    """Collect and store user feedback on reviews"""

    @staticmethod
    def save_feedback(review_id: str, issue_id: int, feedback: Dict):
        """Save user feedback for a specific issue"""
        feedback_entry = {
            'timestamp': datetime.now().isoformat(),
            'review_id': review_id,
            'issue_id': issue_id,
            'feedback': feedback
        }

        # Append to JSONL file
        with open(FEEDBACK_FILE, 'a') as f:
            f.write(json.dumps(feedback_entry) + '\n')

    @staticmethod
    def load_feedback() -> List[Dict]:
        """Load all feedback from disk"""
        if not FEEDBACK_FILE.exists():
            return []

        feedback_list = []
        with open(FEEDBACK_FILE, 'r') as f:
            for line in f:
                try:
                    feedback_list.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        return feedback_list

    @staticmethod
    def provide_feedback_interactive(review: Dict):
        """Interactive feedback collection (CLI)"""
        cprint("\n📊 Review Feedback", "cyan", attrs=["bold"])
        cprint("Help the agent learn from this review!\n", "cyan")

        feedback_data = {
            'accepted': 0,
            'rejected': 0,
            'ratings': []
        }

        for i, issue in enumerate(review.get('issues', []), 1):
            cprint(f"\nIssue {i}: {issue.get('type')} (Line {issue.get('line')})", "yellow")
            cprint(f"  {issue.get('description')}", "white")

            response = input("\n  Was this useful? (y/n/s to skip): ").lower()

            if response == 'y':
                feedback_data['accepted'] += 1
                rating = input("  Rate quality (1-5): ")
                try:
                    feedback_data['ratings'].append(int(rating))
                except ValueError:
                    pass
            elif response == 'n':
                feedback_data['rejected'] += 1

        return feedback_data


def train_from_feedback():
    """Train models from collected feedback"""
    cprint("\n🎓 Training from feedback...", "cyan")

    feedback_list = FeedbackCollector.load_feedback()

    if not feedback_list:
        cprint("⚠️ No feedback data available for training", "yellow")
        return

    rl_system = CodeReviewRL()
    ml_system = CodeReviewML()

    trained_count = 0

    for feedback_entry in feedback_list:
        # Extract state from feedback
        review_id = feedback_entry.get('review_id')
        feedback = feedback_entry.get('feedback', {})

        # Update RL system
        if 'state' in feedback and 'action' in feedback:
            state = feedback['state']
            action = feedback['action']
            reward = feedback.get('reward', 0)

            rl_system.update_q_value(state, action, reward)
            trained_count += 1

    cprint(f"✅ Trained on {trained_count} feedback entries", "green")

    # Save updated models
    rl_system._save_q_table()
    ml_system._save_patterns()

    cprint(f"💾 Models saved to {TRAINING_DATA_DIR}", "green")


if __name__ == "__main__":
    # Display current statistics
    ml_system = CodeReviewML()
    stats = ml_system.get_review_statistics()

    cprint("\n🌙 Code Review ML/RL Statistics", "cyan", attrs=["bold"])
    cprint("=" * 60, "cyan")

    cprint(f"\n📊 Review Statistics:", "yellow")
    cprint(f"  Total Reviews: {stats['total_reviews']}", "white")
    cprint(f"  Total Issues: {stats['total_issues']}", "white")
    cprint(f"  Acceptance Rate: {stats['acceptance_rate']}", "white")
    cprint(f"  Average Score: {stats['avg_score']}", "white")

    cprint(f"\n🔝 Top Issues:", "yellow")
    for issue_type, count in stats['top_issues']:
        cprint(f"  {issue_type}: {count}", "white")

    cprint(f"\n⚖️ Issues by Severity:", "yellow")
    for severity, count in stats['issues_by_severity'].items():
        cprint(f"  {severity}: {count}", "white")
