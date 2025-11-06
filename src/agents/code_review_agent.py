"""
🌙 Moon Dev's Code Review Agent 🌙
AI-powered code review agent that analyzes code and suggests improvements

Features:
- Multi-model AI code review (Claude, GPT-4, DeepSeek, etc.)
- Multiple review types: security, performance, style, best practices
- Automatic improvement suggestions
- Optional auto-fix mode
- Detailed review reports (CSV, JSON, Markdown)
- Git integration for tracking reviews

Created with ❤️ by Moon Dev
"""

import os
import sys
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from termcolor import cprint
import ast
import subprocess

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.models import model_factory

# Import ML/RL module
try:
    from src.agents.code_review_ml import CodeReviewRL, CodeReviewML, FeedbackCollector
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    cprint("⚠️ ML/RL module not available", "yellow")

# Import Knowledge Base module
try:
    from src.agents.code_review_knowledge import search_knowledge, get_knowledge_stats, learn_from_youtube, learn_from_pdf
    KNOWLEDGE_AVAILABLE = True
except ImportError:
    KNOWLEDGE_AVAILABLE = False

# Define paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "src" / "data" / "code_review"
REPORTS_DIR = DATA_DIR / "reports"
FIXES_DIR = DATA_DIR / "fixes"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
FIXES_DIR.mkdir(parents=True, exist_ok=True)

# Review type prompts
REVIEW_PROMPTS = {
    "security": """
You are a security-focused code reviewer. Analyze the following code for:
- SQL injection vulnerabilities
- Command injection risks
- Hardcoded secrets or credentials
- Insecure cryptographic practices
- Authentication/authorization issues
- Input validation problems
- Path traversal vulnerabilities
- XSS vulnerabilities
- Unsafe deserialization

Provide specific, actionable security improvements.
""",
    "performance": """
You are a performance optimization expert. Analyze the following code for:
- Inefficient algorithms (time complexity)
- Memory leaks or excessive memory usage
- Database query optimization opportunities
- Unnecessary loops or redundant operations
- Caching opportunities
- Async/await optimization
- Resource cleanup issues

Provide specific, measurable performance improvements.
""",
    "style": """
You are a code style and readability expert. Analyze the following code for:
- PEP 8 compliance (for Python)
- Naming conventions
- Code organization and structure
- Documentation and comments
- Function/method length
- Code duplication
- Type hints usage
- Import organization

Provide specific style improvements that enhance readability.
""",
    "best_practices": """
You are a software engineering best practices expert. Analyze the following code for:
- SOLID principles violations
- Design pattern opportunities
- Error handling improvements
- Logging practices
- Testing considerations
- Configuration management
- Dependency management
- Code maintainability

Provide specific best practice improvements.
""",
    "all": """
You are an expert code reviewer. Perform a comprehensive code review covering:
- Security vulnerabilities
- Performance issues
- Code style and readability
- Best practices violations
- Potential bugs
- Maintainability concerns

Provide a thorough, prioritized list of improvements.
"""
}

class CodeReviewAgent:
    """AI-powered code review agent"""

    def __init__(self, model_type: str = "claude", model_name: Optional[str] = None):
        """Initialize the code review agent

        Args:
            model_type: Type of model to use (claude, openai, deepseek, etc.)
            model_name: Specific model name (optional)
        """
        cprint("\n🌙 Initializing Code Review Agent...", "cyan")

        self.model_type = model_type
        self.model_name = model_name
        self.model = model_factory.get_model(model_type, model_name)

        if not self.model:
            raise ValueError(f"Failed to initialize model: {model_type}")

        cprint(f"✨ Using model: {self.model.model_name}", "green")

        # Initialize ML/RL systems
        if ML_AVAILABLE:
            self.rl_system = CodeReviewRL()
            self.ml_system = CodeReviewML()
            cprint("🧠 ML/RL systems initialized", "green")
        else:
            self.rl_system = None
            self.ml_system = None

    def analyze_file(self, file_path: str, review_type: str = "all") -> Dict:
        """Analyze a single file

        Args:
            file_path: Path to the file to review
            review_type: Type of review (security, performance, style, best_practices, all)

        Returns:
            Dictionary containing review results
        """
        cprint(f"\n📝 Analyzing: {file_path}", "cyan")

        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
        except Exception as e:
            cprint(f"❌ Error reading file: {e}", "red")
            return {"error": str(e)}

        # Check if Python file and validate syntax
        if file_path.endswith('.py'):
            try:
                ast.parse(code_content)
                cprint("✅ Python syntax valid", "green")
            except SyntaxError as e:
                cprint(f"⚠️ Syntax error found: {e}", "yellow")
                return {
                    "file": file_path,
                    "review_type": review_type,
                    "syntax_error": str(e),
                    "line": e.lineno,
                    "issues": []
                }

        # Get appropriate prompt
        review_prompt = REVIEW_PROMPTS.get(review_type, REVIEW_PROMPTS["all"])

        # Create full prompt
        full_prompt = f"""
{review_prompt}

File: {file_path}
Lines of code: {len(code_content.splitlines())}

Code to review:
```
{code_content}
```

Please provide your review in the following JSON format:
{{
    "severity": "critical|high|medium|low",
    "issues": [
        {{
            "line": <line_number>,
            "type": "<issue_type>",
            "severity": "critical|high|medium|low",
            "description": "<detailed_description>",
            "suggestion": "<specific_fix>",
            "code_before": "<problematic_code>",
            "code_after": "<improved_code>"
        }}
    ],
    "summary": "<overall_summary>",
    "score": <0-100>
}}
"""

        cprint("🤖 Sending to AI model for review...", "cyan")

        # Get AI response
        try:
            response = self.model.generate_response(
                system_prompt="You are an expert code reviewer. Provide detailed, actionable feedback.",
                user_content=full_prompt,
                temperature=0.3,  # Lower temperature for more consistent reviews
                max_tokens=4000
            )

            # Extract JSON from response
            response_text = response.content if hasattr(response, 'content') else str(response)

            # Try to parse JSON from response
            try:
                # Find JSON block in response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1

                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    review_data = json.loads(json_str)
                else:
                    # Fallback: create structured response
                    review_data = {
                        "severity": "medium",
                        "issues": [],
                        "summary": response_text,
                        "score": 70
                    }
            except json.JSONDecodeError:
                cprint("⚠️ Failed to parse JSON, using raw response", "yellow")
                review_data = {
                    "severity": "unknown",
                    "issues": [],
                    "summary": response_text,
                    "score": None
                }

            # Add metadata
            review_data["file"] = file_path
            review_data["review_type"] = review_type
            review_data["model"] = self.model.model_name
            review_data["timestamp"] = datetime.now().isoformat()

            # ML/RL: Learn from this review
            if self.ml_system:
                self.ml_system.learn_from_review(review_data)

                # Predict risk for this file
                risk_score = self.ml_system.predict_file_risk(file_path)
                review_data["predicted_risk"] = risk_score

            cprint(f"✅ Review complete: {len(review_data.get('issues', []))} issues found", "green")

            return review_data

        except Exception as e:
            cprint(f"❌ Error during review: {e}", "red")
            return {
                "file": file_path,
                "review_type": review_type,
                "error": str(e),
                "issues": []
            }

    def analyze_directory(self, directory: str,
                         review_type: str = "all",
                         extensions: List[str] = ['.py'],
                         exclude_dirs: List[str] = ['__pycache__', '.git', 'venv', 'env', 'node_modules']) -> List[Dict]:
        """Analyze all files in a directory

        Args:
            directory: Directory path to analyze
            review_type: Type of review
            extensions: File extensions to include
            exclude_dirs: Directory names to exclude

        Returns:
            List of review results
        """
        cprint(f"\n📂 Analyzing directory: {directory}", "cyan")

        results = []
        dir_path = Path(directory)

        # Find all files
        files_to_review = []
        for ext in extensions:
            for file_path in dir_path.rglob(f"*{ext}"):
                # Skip excluded directories
                if any(excluded in file_path.parts for excluded in exclude_dirs):
                    continue
                files_to_review.append(file_path)

        cprint(f"📊 Found {len(files_to_review)} files to review", "cyan")

        # Review each file
        for i, file_path in enumerate(files_to_review, 1):
            cprint(f"\n[{i}/{len(files_to_review)}] Reviewing: {file_path.name}", "yellow")
            result = self.analyze_file(str(file_path), review_type)
            results.append(result)

        return results

    def generate_report(self, reviews: List[Dict], format: str = "markdown") -> str:
        """Generate a formatted report from reviews

        Args:
            reviews: List of review results
            format: Report format (markdown, json, csv)

        Returns:
            Report content as string
        """
        if format == "json":
            return json.dumps(reviews, indent=2)

        elif format == "csv":
            # Flatten issues for CSV
            rows = []
            for review in reviews:
                for issue in review.get('issues', []):
                    rows.append({
                        'file': review.get('file'),
                        'review_type': review.get('review_type'),
                        'line': issue.get('line'),
                        'severity': issue.get('severity'),
                        'type': issue.get('type'),
                        'description': issue.get('description'),
                        'suggestion': issue.get('suggestion'),
                        'timestamp': review.get('timestamp')
                    })

            if not rows:
                return "No issues found."

            # Convert to CSV string
            import io
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
            return output.getvalue()

        else:  # markdown
            report = "# Code Review Report\n\n"
            report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            # Summary stats
            total_issues = sum(len(r.get('issues', [])) for r in reviews)
            files_with_issues = sum(1 for r in reviews if r.get('issues'))

            report += "## Summary\n\n"
            report += f"- Files reviewed: {len(reviews)}\n"
            report += f"- Files with issues: {files_with_issues}\n"
            report += f"- Total issues: {total_issues}\n\n"

            # Severity breakdown
            severities = {}
            for review in reviews:
                for issue in review.get('issues', []):
                    sev = issue.get('severity', 'unknown')
                    severities[sev] = severities.get(sev, 0) + 1

            if severities:
                report += "### Issues by Severity\n\n"
                for severity, count in sorted(severities.items()):
                    emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")
                    report += f"- {emoji} {severity.title()}: {count}\n"
                report += "\n"

            # Detailed results
            report += "## Detailed Results\n\n"

            for review in reviews:
                if review.get('error'):
                    report += f"### ❌ {review['file']}\n\n"
                    report += f"**Error:** {review['error']}\n\n"
                    continue

                issues = review.get('issues', [])
                score = review.get('score')

                report += f"### {review['file']}\n\n"
                report += f"**Review Type:** {review.get('review_type')}\n\n"

                if score is not None:
                    report += f"**Score:** {score}/100\n\n"

                if review.get('summary'):
                    report += f"**Summary:** {review['summary']}\n\n"

                if issues:
                    report += f"**Issues Found:** {len(issues)}\n\n"

                    for i, issue in enumerate(issues, 1):
                        severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(
                            issue.get('severity', 'unknown'), "⚪"
                        )

                        report += f"#### {i}. {severity_emoji} {issue.get('type', 'Issue')} (Line {issue.get('line', 'N/A')})\n\n"
                        report += f"**Description:** {issue.get('description', 'No description')}\n\n"

                        if issue.get('code_before'):
                            report += f"**Before:**\n```python\n{issue.get('code_before')}\n```\n\n"

                        if issue.get('suggestion'):
                            report += f"**Suggestion:** {issue.get('suggestion')}\n\n"

                        if issue.get('code_after'):
                            report += f"**After:**\n```python\n{issue.get('code_after')}\n```\n\n"
                else:
                    report += "✅ No issues found!\n\n"

                report += "---\n\n"

            return report

    def save_report(self, reviews: List[Dict], report_name: Optional[str] = None) -> str:
        """Save review report to files

        Args:
            reviews: List of review results
            report_name: Optional custom report name

        Returns:
            Path to saved report
        """
        if not report_name:
            report_name = f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Save in all formats
        formats = {
            'md': self.generate_report(reviews, 'markdown'),
            'json': self.generate_report(reviews, 'json'),
            'csv': self.generate_report(reviews, 'csv')
        }

        saved_paths = []
        for ext, content in formats.items():
            file_path = REPORTS_DIR / f"{report_name}.{ext}"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            saved_paths.append(str(file_path))
            cprint(f"💾 Saved {ext.upper()} report: {file_path}", "green")

        return saved_paths[0]  # Return markdown path

    def review_git_changes(self, review_type: str = "all") -> List[Dict]:
        """Review only files that have git changes

        Args:
            review_type: Type of review

        Returns:
            List of review results
        """
        cprint("\n🔍 Finding modified files in git...", "cyan")

        try:
            # Get list of modified files
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD'],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT
            )

            modified_files = [f.strip() for f in result.stdout.splitlines() if f.strip().endswith('.py')]

            if not modified_files:
                cprint("✅ No Python files modified", "green")
                return []

            cprint(f"📊 Found {len(modified_files)} modified Python files", "cyan")

            # Review each modified file
            reviews = []
            for file_path in modified_files:
                full_path = PROJECT_ROOT / file_path
                if full_path.exists():
                    review = self.analyze_file(str(full_path), review_type)
                    reviews.append(review)

            return reviews

        except Exception as e:
            cprint(f"❌ Error getting git changes: {e}", "red")
            return []

    def provide_feedback(self, review_id: str, feedback_data: Dict):
        """Provide feedback on a review for ML/RL learning

        Args:
            review_id: ID of the review
            feedback_data: Feedback data (accepted, rejected, ratings, etc.)
        """
        if not self.rl_system or not self.ml_system:
            cprint("⚠️ ML/RL not available for feedback", "yellow")
            return

        cprint("\n📝 Processing feedback...", "cyan")

        # Save feedback
        FeedbackCollector.save_feedback(
            review_id=review_id,
            issue_id=0,
            feedback=feedback_data
        )

        # Update ML system with feedback
        self.ml_system.learn_from_review({}, feedback_data)

        cprint("✅ Feedback recorded! Agent will learn from this.", "green")

    def get_statistics(self) -> Dict:
        """Get ML/RL statistics

        Returns:
            Dictionary with review statistics
        """
        if not self.ml_system:
            return {"error": "ML/RL not available"}

        return self.ml_system.get_review_statistics()

    def print_statistics(self):
        """Print comprehensive statistics"""
        if not self.ml_system:
            cprint("⚠️ ML/RL statistics not available", "yellow")
            return

        stats = self.get_statistics()

        cprint("\n🌙 Code Review Agent Statistics", "cyan", attrs=["bold"])
        cprint("=" * 60, "cyan")

        cprint(f"\n📊 Overview:", "yellow")
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

        cprint(f"\n📈 Reviews by Type:", "yellow")
        for review_type, count in stats['reviews_by_type'].items():
            cprint(f"  {review_type}: {count}", "white")


def main():
    """Main function for standalone execution"""
    import argparse

    parser = argparse.ArgumentParser(description="🌙 Moon Dev's Code Review Agent")
    parser.add_argument('path', nargs='?', help='File or directory to review')
    parser.add_argument('--type', '-t', choices=['security', 'performance', 'style', 'best_practices', 'all'],
                       default='all', help='Type of review to perform')
    parser.add_argument('--model', '-m', default='claude', help='AI model to use')
    parser.add_argument('--model-name', help='Specific model name')
    parser.add_argument('--git', '-g', action='store_true', help='Review only git-modified files')
    parser.add_argument('--format', '-f', choices=['markdown', 'json', 'csv'],
                       default='markdown', help='Report format')
    parser.add_argument('--stats', '-s', action='store_true', help='Show ML/RL statistics')
    parser.add_argument('--feedback', action='store_true', help='Provide feedback on review')

    args = parser.parse_args()

    # Initialize agent
    try:
        agent = CodeReviewAgent(model_type=args.model, model_name=args.model_name)
    except Exception as e:
        cprint(f"❌ Failed to initialize agent: {e}", "red")
        return

    # Show statistics if requested
    if args.stats:
        agent.print_statistics()
        return

    # Perform review
    if args.git:
        reviews = agent.review_git_changes(review_type=args.type)
    elif args.path:
        path = Path(args.path)
        if path.is_file():
            review = agent.analyze_file(str(path), review_type=args.type)
            reviews = [review]
        elif path.is_dir():
            reviews = agent.analyze_directory(str(path), review_type=args.type)
        else:
            cprint(f"❌ Path not found: {args.path}", "red")
            return
    else:
        # Default: review current directory
        reviews = agent.analyze_directory('.', review_type=args.type)

    if not reviews:
        cprint("✅ No files to review", "green")
        return

    # Generate and save report
    report_path = agent.save_report(reviews)

    # Print summary
    cprint("\n" + "="*50, "cyan")
    cprint("📊 REVIEW SUMMARY", "cyan")
    cprint("="*50, "cyan")

    total_issues = sum(len(r.get('issues', [])) for r in reviews)
    files_with_issues = sum(1 for r in reviews if r.get('issues'))

    cprint(f"\n✅ Files reviewed: {len(reviews)}", "green")
    cprint(f"⚠️  Files with issues: {files_with_issues}", "yellow")
    cprint(f"🔍 Total issues: {total_issues}", "yellow")
    cprint(f"\n📄 Report saved: {report_path}", "green")

    # Print report preview
    if args.format == 'markdown':
        print("\n" + agent.generate_report(reviews, 'markdown'))

    # Collect feedback if requested
    if args.feedback and ML_AVAILABLE:
        cprint("\n" + "="*50, "cyan")
        cprint("📝 FEEDBACK", "cyan")
        cprint("="*50, "cyan")

        for review in reviews:
            feedback = FeedbackCollector.provide_feedback_interactive(review)
            agent.provide_feedback(
                review_id=review.get('timestamp', 'unknown'),
                feedback_data=feedback
            )

        cprint("\n✅ Thank you for your feedback! The agent will improve over time.", "green")


if __name__ == "__main__":
    main()
