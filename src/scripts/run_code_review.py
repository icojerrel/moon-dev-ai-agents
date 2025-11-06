#!/usr/bin/env python3
"""
🌙 Quick Code Review Runner
Convenient script to run code reviews with common configurations
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.agents.code_review_agent import CodeReviewAgent
from termcolor import cprint

def review_agents_directory():
    """Review all agents in src/agents/"""
    cprint("\n🌙 Moon Dev Code Review - Agents Directory", "cyan", attrs=["bold"])
    cprint("=" * 60, "cyan")

    agent = CodeReviewAgent(model_type="claude")

    # Review agents directory
    reviews = agent.analyze_directory(
        directory="src/agents/",
        review_type="all",
        extensions=['.py'],
        exclude_dirs=['__pycache__', 'data']
    )

    # Save report
    report_path = agent.save_report(reviews, report_name="agents_review")

    # Print summary
    total_issues = sum(len(r.get('issues', [])) for r in reviews)
    cprint(f"\n✅ Review complete! Total issues: {total_issues}", "green", attrs=["bold"])
    cprint(f"📄 Report: {report_path}", "cyan")

def review_single_file(file_path, review_type="all"):
    """Review a single file"""
    cprint(f"\n🌙 Moon Dev Code Review - {file_path}", "cyan", attrs=["bold"])
    cprint("=" * 60, "cyan")

    agent = CodeReviewAgent(model_type="claude")
    review = agent.analyze_file(file_path, review_type)

    # Print results
    issues = review.get('issues', [])
    cprint(f"\n📊 Found {len(issues)} issues", "yellow")

    for i, issue in enumerate(issues, 1):
        severity = issue.get('severity', 'unknown')
        emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")

        cprint(f"\n{emoji} Issue {i}: {issue.get('type', 'Unknown')}", "white", attrs=["bold"])
        cprint(f"   Line: {issue.get('line', 'N/A')}", "cyan")
        cprint(f"   {issue.get('description', 'No description')}", "white")

        if issue.get('suggestion'):
            cprint(f"   💡 Suggestion: {issue.get('suggestion')}", "green")

def review_git_changes():
    """Review files modified in git"""
    cprint("\n🌙 Moon Dev Code Review - Git Changes", "cyan", attrs=["bold"])
    cprint("=" * 60, "cyan")

    agent = CodeReviewAgent(model_type="claude")
    reviews = agent.review_git_changes(review_type="all")

    if not reviews:
        cprint("\n✅ No Python files modified", "green")
        return

    # Save report
    report_path = agent.save_report(reviews, report_name="git_changes_review")

    # Print summary
    total_issues = sum(len(r.get('issues', [])) for r in reviews)
    cprint(f"\n✅ Review complete! Total issues: {total_issues}", "green", attrs=["bold"])
    cprint(f"📄 Report: {report_path}", "cyan")

def security_audit():
    """Run security audit on critical files"""
    cprint("\n🔒 Moon Dev Security Audit", "red", attrs=["bold"])
    cprint("=" * 60, "red")

    critical_files = [
        "src/nice_funcs.py",
        "src/config.py",
        "src/agents/trading_agent.py",
        "src/agents/risk_agent.py"
    ]

    agent = CodeReviewAgent(model_type="claude")
    reviews = []

    for file_path in critical_files:
        full_path = project_root / file_path
        if full_path.exists():
            cprint(f"\n🔍 Auditing: {file_path}", "yellow")
            review = agent.analyze_file(str(full_path), review_type="security")
            reviews.append(review)

    # Save report
    report_path = agent.save_report(reviews, report_name="security_audit")

    # Print critical issues
    critical_issues = []
    for review in reviews:
        for issue in review.get('issues', []):
            if issue.get('severity') in ['critical', 'high']:
                critical_issues.append({
                    'file': review['file'],
                    'issue': issue
                })

    if critical_issues:
        cprint(f"\n🔴 CRITICAL SECURITY ISSUES: {len(critical_issues)}", "red", attrs=["bold"])
        for item in critical_issues:
            cprint(f"\n📁 {item['file']}", "red")
            cprint(f"   Line {item['issue'].get('line')}: {item['issue'].get('description')}", "white")
    else:
        cprint(f"\n✅ No critical security issues found!", "green", attrs=["bold"])

    cprint(f"\n📄 Full report: {report_path}", "cyan")

def main():
    """Main menu"""
    import argparse

    parser = argparse.ArgumentParser(
        description="🌙 Moon Dev Quick Code Review Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Review all agents
  python src/scripts/run_code_review.py --agents

  # Review git changes
  python src/scripts/run_code_review.py --git

  # Security audit
  python src/scripts/run_code_review.py --security

  # Review specific file
  python src/scripts/run_code_review.py --file src/agents/trading_agent.py
        """
    )

    parser.add_argument('--agents', action='store_true', help='Review all agents')
    parser.add_argument('--git', action='store_true', help='Review git changes')
    parser.add_argument('--security', action='store_true', help='Security audit')
    parser.add_argument('--file', help='Review specific file')
    parser.add_argument('--type', default='all', help='Review type (default: all)')

    args = parser.parse_args()

    if args.agents:
        review_agents_directory()
    elif args.git:
        review_git_changes()
    elif args.security:
        security_audit()
    elif args.file:
        review_single_file(args.file, args.type)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
