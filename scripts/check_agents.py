#!/usr/bin/env python3
"""
🌙 Moon Dev Agent Health Checker
Analyzes all agents for proper structure and potential issues
"""

import os
import sys
import ast
from pathlib import Path
from collections import defaultdict

# Try to import colored output
try:
    from termcolor import cprint
except ImportError:
    def cprint(text, color=None, on_color=None, attrs=None):
        print(text)

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))


class AgentAnalyzer:
    """Analyzes agent files for structure and issues"""

    def __init__(self, agent_path):
        self.path = Path(agent_path)
        self.name = self.path.stem
        self.issues = []
        self.warnings = []
        self.features = []

    def analyze(self):
        """Run all checks on the agent"""
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check syntax
            try:
                ast.parse(content)
                self.features.append("✅ Valid Python syntax")
            except SyntaxError as e:
                self.issues.append(f"❌ Syntax error: {e.msg} at line {e.lineno}")
                return  # Can't continue if syntax is broken

            # Check file length
            lines = content.count('\n')
            if lines > 800:
                self.warnings.append(f"⚠️  File is {lines} lines (recommended: <800)")
            else:
                self.features.append(f"✅ File length OK ({lines} lines)")

            # Check for main execution
            if 'if __name__ == "__main__":' in content:
                self.features.append("✅ Standalone executable")
            else:
                self.warnings.append("⚠️  Not standalone (missing __main__ block)")

            # Check for imports
            self.check_imports(content)

            # Check for error handling
            if 'try:' in content and 'except' in content:
                self.features.append("✅ Has error handling")
            else:
                self.warnings.append("⚠️  Limited error handling")

            # Check for AI usage
            self.check_ai_usage(content)

            # Check for configuration
            if 'from config import' in content or 'import config' in content:
                self.features.append("✅ Uses configuration")

            # Check for output
            if 'src/data/' in content:
                self.features.append("✅ Outputs to data directory")

            # Check for colored output
            if 'cprint' in content or 'termcolor' in content:
                self.features.append("✅ Colored console output")

            # Check for docstrings
            if '"""' in content[:500]:  # Check first 500 chars
                self.features.append("✅ Has docstring")
            else:
                self.warnings.append("⚠️  Missing module docstring")

        except Exception as e:
            self.issues.append(f"❌ Error analyzing file: {str(e)}")

    def check_imports(self, content):
        """Check for common imports"""
        required_imports = {
            'os': False,
            'sys': False,
            'termcolor': False,
            'dotenv': False,
        }

        for imp in required_imports.keys():
            if f'import {imp}' in content or f'from {imp}' in content:
                required_imports[imp] = True

    def check_ai_usage(self, content):
        """Check for AI model usage"""
        ai_indicators = [
            'ModelFactory',
            'anthropic',
            'openai',
            'groq',
            'deepseek',
            'gemini',
        ]

        found_ai = []
        for indicator in ai_indicators:
            if indicator in content:
                found_ai.append(indicator)

        if found_ai:
            self.features.append(f"🤖 Uses AI: {', '.join(found_ai)}")
        else:
            self.warnings.append("⚠️  No AI usage detected")

    def get_summary(self):
        """Get analysis summary"""
        return {
            'name': self.name,
            'issues': self.issues,
            'warnings': self.warnings,
            'features': self.features,
            'status': 'ERROR' if self.issues else ('WARNING' if self.warnings else 'OK')
        }


def find_all_agents():
    """Find all agent files"""
    agents_dir = project_root / 'src' / 'agents'

    if not agents_dir.exists():
        cprint("❌ src/agents directory not found", "red")
        return []

    # Find all *_agent.py files
    agent_files = list(agents_dir.glob('*_agent.py'))

    # Also check for other agent patterns
    agent_files.extend(agents_dir.glob('*agent.py'))

    # Remove duplicates
    agent_files = list(set(agent_files))

    return sorted(agent_files)


def analyze_all_agents():
    """Analyze all agents and generate report"""
    cprint("\n" + "="*60, "cyan")
    cprint("🌙 Moon Dev Agent Health Checker", "cyan", attrs=['bold'])
    cprint("="*60 + "\n", "cyan")

    cprint("🔍 Scanning for agents...", "cyan")
    agent_files = find_all_agents()

    if not agent_files:
        cprint("❌ No agent files found", "red")
        return 1

    cprint(f"✅ Found {len(agent_files)} agent files\n", "green")

    # Analyze each agent
    results = []
    for agent_file in agent_files:
        cprint(f"📊 Analyzing {agent_file.name}...", "white")
        analyzer = AgentAnalyzer(agent_file)
        analyzer.analyze()
        results.append(analyzer.get_summary())

    # Generate report
    cprint("\n" + "="*60, "cyan")
    cprint("📈 Analysis Report", "cyan", attrs=['bold'])
    cprint("="*60 + "\n", "cyan")

    ok_count = 0
    warning_count = 0
    error_count = 0

    # Group by status
    by_status = defaultdict(list)
    for result in results:
        by_status[result['status']].append(result)

    # Show errors first
    if by_status['ERROR']:
        cprint(f"\n❌ ERRORS ({len(by_status['ERROR'])} agents):", "red", attrs=['bold'])
        for result in by_status['ERROR']:
            cprint(f"\n  📄 {result['name']}", "red")
            for issue in result['issues']:
                cprint(f"    {issue}", "red")
            error_count += 1

    # Show warnings
    if by_status['WARNING']:
        cprint(f"\n⚠️  WARNINGS ({len(by_status['WARNING'])} agents):", "yellow", attrs=['bold'])
        for result in by_status['WARNING']:
            cprint(f"\n  📄 {result['name']}", "yellow")
            for warning in result['warnings']:
                cprint(f"    {warning}", "yellow")
            warning_count += 1

    # Show OK agents (summary only)
    if by_status['OK']:
        cprint(f"\n✅ OK ({len(by_status['OK'])} agents):", "green", attrs=['bold'])
        for result in by_status['OK']:
            cprint(f"  ✅ {result['name']}", "green")
            ok_count += 1

    # Detailed features for OK agents (optional)
    show_details = False  # Set to True to see all features
    if show_details and by_status['OK']:
        cprint("\n📋 Detailed Features:", "cyan")
        for result in by_status['OK']:
            cprint(f"\n  📄 {result['name']}", "cyan")
            for feature in result['features']:
                cprint(f"    {feature}", "white")

    # Summary statistics
    cprint("\n" + "="*60, "cyan")
    cprint("📊 Summary Statistics", "cyan", attrs=['bold'])
    cprint("="*60, "cyan")

    total = len(results)
    cprint(f"  Total Agents: {total}", "white")
    cprint(f"  ✅ OK: {ok_count} ({ok_count*100//total if total else 0}%)", "green")
    cprint(f"  ⚠️  Warnings: {warning_count} ({warning_count*100//total if total else 0}%)", "yellow")
    cprint(f"  ❌ Errors: {error_count} ({error_count*100//total if total else 0}%)", "red")

    # Common issues
    all_warnings = []
    for result in results:
        all_warnings.extend(result['warnings'])

    if all_warnings:
        warning_types = defaultdict(int)
        for warning in all_warnings:
            # Simplify warning text for grouping
            if 'File is' in warning and 'lines' in warning:
                warning_types['Long files (>800 lines)'] += 1
            elif 'Not standalone' in warning:
                warning_types['Missing __main__ block'] += 1
            elif 'Limited error handling' in warning:
                warning_types['Limited error handling'] += 1
            elif 'No AI usage' in warning:
                warning_types['No AI usage'] += 1
            elif 'Missing module docstring' in warning:
                warning_types['Missing docstrings'] += 1
            else:
                warning_types['Other'] += 1

        if warning_types:
            cprint("\n📋 Common Issues:", "cyan")
            for issue_type, count in sorted(warning_types.items(), key=lambda x: -x[1]):
                cprint(f"  • {issue_type}: {count} agents", "white")

    cprint("\n" + "="*60 + "\n", "cyan")

    # Return status
    if error_count > 0:
        cprint("❌ Some agents have errors - review above", "red")
        return 1
    elif warning_count > 0:
        cprint("⚠️  Some agents have warnings - consider addressing", "yellow")
        return 0
    else:
        cprint("✅ All agents look good!", "green")
        return 0


def main():
    """Main entry point"""
    return analyze_all_agents()


if __name__ == "__main__":
    sys.exit(main())
