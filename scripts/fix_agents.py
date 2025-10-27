#!/usr/bin/env python3
"""
🌙 Moon Dev Agent Auto-Fixer
Automatically fixes common agent issues
"""

import os
import sys
from pathlib import Path

# Try to import colored output
try:
    from termcolor import cprint
except ImportError:
    def cprint(text, color=None, on_color=None, attrs=None):
        print(text)

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))


def add_docstring(agent_path, agent_name):
    """Add docstring to agent file if missing"""
    with open(agent_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if docstring exists in first 500 chars
    if '"""' in content[:500]:
        cprint(f"  ℹ️  {agent_name}: Already has docstring", "white")
        return False

    # Create appropriate docstring
    docstring = f'''"""
🌙 Moon Dev's {agent_name.replace('_', ' ').title().replace('Agent', 'Agent')}
{get_agent_description(agent_name)}
"""

'''

    # Find first import or code line
    lines = content.split('\n')
    insert_pos = 0

    # Skip shebang and encoding
    for i, line in enumerate(lines):
        if line.startswith('#!') or line.startswith('# -*-'):
            insert_pos = i + 1
        elif line.strip() and not line.startswith('#'):
            insert_pos = i
            break

    # Insert docstring
    lines.insert(insert_pos, docstring.strip())
    new_content = '\n'.join(lines)

    # Write back
    with open(agent_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    cprint(f"  ✅ {agent_name}: Added docstring", "green")
    return True


def get_agent_description(agent_name):
    """Get description for agent based on name"""
    descriptions = {
        'clips_agent': 'Creates video clips from longer content',
        'compliance_agent': 'Ensures trading compliance and regulatory adherence',
        'research_agent': 'Researches trading strategies and market conditions',
        'sentiment_agent': 'Analyzes market sentiment from social media',
        'sniper_agent': 'Snipes new token launches on Solana',
        'solana_agent': 'Analyzes Solana meme tokens for trading opportunities',
        'tx_agent': 'Monitors and analyzes blockchain transactions',
        'tiktok_agent': 'Extracts consumer insights from TikTok for market analysis',
    }

    return descriptions.get(agent_name, f'Specialized agent for {agent_name.replace("_", " ")}')


def add_main_block(agent_path, agent_name):
    """Add __main__ block to agent if missing"""
    with open(agent_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'if __name__ == "__main__":' in content:
        cprint(f"  ℹ️  {agent_name}: Already has __main__ block", "white")
        return False

    # Try to find main function or run method
    main_block = '''

if __name__ == "__main__":
    """Run agent standalone"""
    try:
        agent = Agent()
        agent.run()
    except KeyboardInterrupt:
        print("\\n👋 Agent stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
'''

    # Append to file
    with open(agent_path, 'a', encoding='utf-8') as f:
        f.write(main_block)

    cprint(f"  ✅ {agent_name}: Added __main__ block", "green")
    return True


def fix_all_agents():
    """Fix all agents with known issues"""
    cprint("\n" + "="*60, "cyan")
    cprint("🔧 Moon Dev Agent Auto-Fixer", "cyan", attrs=['bold'])
    cprint("="*60 + "\n", "cyan")

    agents_dir = project_root / 'src' / 'agents'

    # Agents that need docstrings based on check_agents.py output
    needs_docstring = [
        'clips_agent.py',
        'compliance_agent.py',
        'research_agent.py',
        'sentiment_agent.py',
        'sniper_agent.py',
        'solana_agent.py',
        'tx_agent.py',
        'tiktok_agent.py',
    ]

    # Agents that need __main__ blocks
    needs_main = [
        'base_agent.py',
        'strategy_agent.py',
    ]

    fixed_count = 0

    # Fix docstrings
    if needs_docstring:
        cprint("📝 Fixing missing docstrings...\n", "cyan")
        for agent_file in needs_docstring:
            agent_path = agents_dir / agent_file
            if agent_path.exists():
                if add_docstring(agent_path, agent_path.stem):
                    fixed_count += 1
            else:
                cprint(f"  ⚠️  {agent_file}: File not found", "yellow")

    # Fix __main__ blocks
    if needs_main:
        cprint("\n🎯 Fixing missing __main__ blocks...\n", "cyan")
        for agent_file in needs_main:
            agent_path = agents_dir / agent_file
            if agent_path.exists():
                if add_main_block(agent_path, agent_path.stem):
                    fixed_count += 1
            else:
                cprint(f"  ⚠️  {agent_file}: File not found", "yellow")

    # Summary
    cprint("\n" + "="*60, "cyan")
    cprint("📊 Summary", "cyan", attrs=['bold'])
    cprint("="*60, "cyan")
    cprint(f"  Agents fixed: {fixed_count}", "white")

    if fixed_count > 0:
        cprint("\n✅ Fixes applied successfully!", "green")
        cprint("💡 Run check_agents.py to verify improvements", "cyan")
        return 0
    else:
        cprint("\n✅ All agents already have proper structure", "green")
        return 0


def main():
    """Main entry point"""
    return fix_all_agents()


if __name__ == "__main__":
    sys.exit(main())
