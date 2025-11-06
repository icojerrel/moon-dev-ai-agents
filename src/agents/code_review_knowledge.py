"""
🌙 Moon Dev's Code Review Knowledge Base
Learn from YouTube videos, PDFs, and other sources to improve code reviews

Features:
- YouTube transcript extraction
- PDF content extraction
- AI-powered insight extraction
- Knowledge storage and retrieval
- Pattern learning from expert content
- Continuous improvement through external knowledge

Created with ❤️ by Moon Dev
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from termcolor import cprint
import hashlib

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.models import model_factory

# Knowledge base paths
DATA_DIR = Path(__file__).parent.parent / "data" / "code_review" / "knowledge"
DATA_DIR.mkdir(parents=True, exist_ok=True)

KNOWLEDGE_DB = DATA_DIR / "knowledge_base.jsonl"
VIDEO_INDEX = DATA_DIR / "video_index.json"
INSIGHTS_DIR = DATA_DIR / "insights"
INSIGHTS_DIR.mkdir(exist_ok=True)

def get_youtube_transcript(video_id: str) -> Optional[str]:
    """Extract transcript from YouTube video

    Args:
        video_id: YouTube video ID

    Returns:
        Transcript text or None if failed
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        cprint(f"\n📥 Fetching transcript for video: {video_id}", "cyan")

        # Get transcript
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try to get English transcript (generated or manual)
        try:
            transcript = transcript_list.find_transcript(['en'])
        except:
            # Fallback to first available transcript
            transcript = transcript_list.find_generated_transcript(['en'])

        # Extract text
        transcript_data = transcript.fetch()
        transcript_text = ' '.join([entry['text'] for entry in transcript_data])

        cprint(f"✅ Transcript extracted: {len(transcript_text)} characters", "green")
        return transcript_text

    except ImportError:
        cprint("❌ youtube-transcript-api not installed", "red")
        cprint("Install with: pip install youtube-transcript-api", "yellow")
        return None
    except Exception as e:
        cprint(f"❌ Error fetching transcript: {e}", "red")
        return None

def get_pdf_text(pdf_path: str) -> Optional[str]:
    """Extract text from PDF file

    Args:
        pdf_path: Path to PDF file (local or URL)

    Returns:
        Extracted text or None if failed
    """
    try:
        import PyPDF2
        import requests
        from io import BytesIO

        cprint(f"\n📄 Extracting text from PDF: {pdf_path}", "cyan")

        # Handle URL vs local file
        if pdf_path.startswith('http'):
            response = requests.get(pdf_path)
            pdf_file = BytesIO(response.content)
        else:
            pdf_file = open(pdf_path, 'rb')

        # Extract text
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"

        if not pdf_path.startswith('http'):
            pdf_file.close()

        cprint(f"✅ PDF extracted: {len(text)} characters", "green")
        return text

    except ImportError:
        cprint("❌ PyPDF2 not installed", "red")
        cprint("Install with: pip install PyPDF2", "yellow")
        return None
    except Exception as e:
        cprint(f"❌ Error extracting PDF: {e}", "red")
        return None

def extract_coding_insights(content: str, source_info: Dict, model_type: str = "claude") -> Optional[Dict]:
    """Use AI to extract coding insights from content

    Args:
        content: Raw content (transcript, PDF text, etc.)
        source_info: Information about the source
        model_type: AI model to use

    Returns:
        Dictionary with extracted insights
    """
    cprint("\n🤖 Analyzing content for coding insights...", "cyan")

    try:
        model = model_factory.get_model(model_type)

        if not model:
            cprint(f"❌ Failed to get model: {model_type}", "red")
            return None

        prompt = f"""
You are an expert code reviewer analyzing educational content about software development.

Extract actionable coding insights from the following content:

SOURCE: {source_info.get('title', 'Unknown')}
TYPE: {source_info.get('type', 'Unknown')}

CONTENT:
{content[:10000]}  # Limit to first 10k chars

Please extract and categorize insights in JSON format:

{{
    "security_insights": [
        {{
            "principle": "Brief principle name",
            "description": "Detailed description",
            "examples": ["code example or explanation"],
            "severity": "critical|high|medium|low"
        }}
    ],
    "performance_insights": [
        {{
            "principle": "Brief principle name",
            "description": "Detailed description",
            "examples": ["code example or explanation"],
            "impact": "high|medium|low"
        }}
    ],
    "style_insights": [
        {{
            "principle": "Brief principle name",
            "description": "Detailed description",
            "examples": ["code example or explanation"]
        }}
    ],
    "best_practices": [
        {{
            "principle": "Brief principle name",
            "description": "Detailed description",
            "examples": ["code example or explanation"],
            "category": "architecture|testing|maintenance|etc"
        }}
    ],
    "common_mistakes": [
        {{
            "mistake": "Common mistake description",
            "why_bad": "Explanation of why it's bad",
            "better_approach": "How to do it better",
            "severity": "critical|high|medium|low"
        }}
    ],
    "key_takeaways": [
        "Most important lesson 1",
        "Most important lesson 2",
        "Most important lesson 3"
    ]
}}

Focus on:
- Concrete, actionable advice
- Real-world examples
- Common pitfalls to avoid
- Best practices that can be applied in code reviews
"""

        response = model.generate_response(
            system_prompt="You are an expert at extracting actionable coding insights from educational content.",
            user_content=prompt,
            temperature=0.3,
            max_tokens=3000
        )

        # Extract JSON from response
        response_text = response.content if hasattr(response, 'content') else str(response)

        # Find JSON block
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1

        if start_idx >= 0 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            insights = json.loads(json_str)

            cprint(f"✅ Extracted {len(insights.get('key_takeaways', []))} key insights", "green")
            return insights
        else:
            cprint("⚠️ Failed to extract structured insights", "yellow")
            return None

    except Exception as e:
        cprint(f"❌ Error extracting insights: {e}", "red")
        return None

def save_knowledge(source_url: str, source_type: str, content: str, insights: Dict):
    """Save knowledge to the knowledge base

    Args:
        source_url: URL or path to source
        source_type: Type of source (youtube, pdf, text)
        content: Raw content
        insights: Extracted insights
    """
    # Create unique ID
    source_id = hashlib.md5(source_url.encode()).hexdigest()

    # Prepare knowledge entry
    entry = {
        'id': source_id,
        'source_url': source_url,
        'source_type': source_type,
        'timestamp': datetime.now().isoformat(),
        'content_length': len(content),
        'insights': insights
    }

    # Append to knowledge base
    with open(KNOWLEDGE_DB, 'a') as f:
        f.write(json.dumps(entry) + '\n')

    # Save detailed insights
    insight_file = INSIGHTS_DIR / f"{source_id}.json"
    with open(insight_file, 'w') as f:
        json.dump(entry, f, indent=2)

    # Update video index
    update_video_index(source_url, source_id, source_type, insights)

    cprint(f"💾 Knowledge saved: {source_id}", "green")

def update_video_index(source_url: str, source_id: str, source_type: str, insights: Dict):
    """Update the video/source index

    Args:
        source_url: Source URL
        source_id: Unique source ID
        source_type: Type of source
        insights: Extracted insights
    """
    # Load existing index
    if VIDEO_INDEX.exists():
        with open(VIDEO_INDEX, 'r') as f:
            index = json.load(f)
    else:
        index = {'sources': [], 'stats': {}}

    # Add new entry
    index['sources'].append({
        'id': source_id,
        'url': source_url,
        'type': source_type,
        'added': datetime.now().isoformat(),
        'insight_count': sum(len(v) if isinstance(v, list) else 1 for v in insights.values())
    })

    # Update stats
    index['stats']['total_sources'] = len(index['sources'])
    index['stats']['by_type'] = {}
    for source in index['sources']:
        source_type = source['type']
        index['stats']['by_type'][source_type] = index['stats']['by_type'].get(source_type, 0) + 1

    # Save index
    with open(VIDEO_INDEX, 'w') as f:
        json.dump(index, f, indent=2)

def learn_from_youtube(video_url: str, model_type: str = "claude") -> bool:
    """Learn from a YouTube video

    Args:
        video_url: YouTube video URL
        model_type: AI model to use for analysis

    Returns:
        True if successful
    """
    cprint("\n🎥 Learning from YouTube video...", "cyan", attrs=["bold"])
    cprint("="*60, "cyan")

    # Extract video ID
    if "v=" in video_url:
        video_id = video_url.split("v=")[1].split("&")[0]
    elif "youtu.be" in video_url:
        video_id = video_url.split("/")[-1].split("?")[0]
    else:
        cprint("❌ Invalid YouTube URL", "red")
        return False

    # Get transcript
    transcript = get_youtube_transcript(video_id)
    if not transcript:
        return False

    # Extract insights
    source_info = {
        'title': f"YouTube Video {video_id}",
        'type': 'youtube',
        'url': video_url
    }

    insights = extract_coding_insights(transcript, source_info, model_type)
    if not insights:
        return False

    # Save knowledge
    save_knowledge(video_url, 'youtube', transcript, insights)

    # Print summary
    print_insight_summary(insights)

    return True

def learn_from_pdf(pdf_path: str, model_type: str = "claude") -> bool:
    """Learn from a PDF document

    Args:
        pdf_path: Path to PDF (local or URL)
        model_type: AI model to use for analysis

    Returns:
        True if successful
    """
    cprint("\n📄 Learning from PDF document...", "cyan", attrs=["bold"])
    cprint("="*60, "cyan")

    # Extract text
    text = get_pdf_text(pdf_path)
    if not text:
        return False

    # Extract insights
    source_info = {
        'title': f"PDF Document",
        'type': 'pdf',
        'path': pdf_path
    }

    insights = extract_coding_insights(text, source_info, model_type)
    if not insights:
        return False

    # Save knowledge
    save_knowledge(pdf_path, 'pdf', text, insights)

    # Print summary
    print_insight_summary(insights)

    return True

def print_insight_summary(insights: Dict):
    """Print a summary of extracted insights

    Args:
        insights: Insights dictionary
    """
    cprint("\n📊 INSIGHTS SUMMARY", "cyan", attrs=["bold"])
    cprint("="*60, "cyan")

    if insights.get('key_takeaways'):
        cprint("\n🔑 Key Takeaways:", "yellow")
        for i, takeaway in enumerate(insights['key_takeaways'], 1):
            cprint(f"  {i}. {takeaway}", "white")

    counts = {
        'Security': len(insights.get('security_insights', [])),
        'Performance': len(insights.get('performance_insights', [])),
        'Style': len(insights.get('style_insights', [])),
        'Best Practices': len(insights.get('best_practices', [])),
        'Common Mistakes': len(insights.get('common_mistakes', []))
    }

    cprint("\n📈 Insight Categories:", "yellow")
    for category, count in counts.items():
        if count > 0:
            cprint(f"  • {category}: {count} insights", "green")

def get_knowledge_stats() -> Dict:
    """Get statistics about the knowledge base

    Returns:
        Dictionary with statistics
    """
    if not VIDEO_INDEX.exists():
        return {'total_sources': 0, 'by_type': {}}

    with open(VIDEO_INDEX, 'r') as f:
        index = json.load(f)

    return index.get('stats', {})

def search_knowledge(query: str, category: Optional[str] = None) -> List[Dict]:
    """Search the knowledge base

    Args:
        query: Search query
        category: Optional category filter

    Returns:
        List of matching insights
    """
    if not KNOWLEDGE_DB.exists():
        return []

    results = []

    with open(KNOWLEDGE_DB, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line)

                # Simple text search
                if query.lower() in json.dumps(entry).lower():
                    if category:
                        # Filter by category
                        if category in entry.get('insights', {}):
                            results.append(entry)
                    else:
                        results.append(entry)
            except json.JSONDecodeError:
                continue

    return results

def main():
    """Main function for standalone execution"""
    import argparse

    parser = argparse.ArgumentParser(description="🌙 Code Review Knowledge Base")
    parser.add_argument('source', nargs='?', help='YouTube URL or PDF path')
    parser.add_argument('--type', '-t', choices=['youtube', 'pdf'], help='Source type')
    parser.add_argument('--model', '-m', default='claude', help='AI model to use')
    parser.add_argument('--stats', '-s', action='store_true', help='Show knowledge base statistics')
    parser.add_argument('--search', help='Search knowledge base')

    args = parser.parse_args()

    if args.stats:
        stats = get_knowledge_stats()
        cprint("\n🌙 Knowledge Base Statistics", "cyan", attrs=["bold"])
        cprint("="*60, "cyan")
        cprint(f"\n📚 Total Sources: {stats.get('total_sources', 0)}", "yellow")
        cprint("\n📊 By Type:", "yellow")
        for source_type, count in stats.get('by_type', {}).items():
            cprint(f"  • {source_type}: {count}", "white")
        return

    if args.search:
        results = search_knowledge(args.search)
        cprint(f"\n🔍 Found {len(results)} results for: {args.search}", "cyan")
        for result in results[:5]:
            cprint(f"\n  • {result['source_type']}: {result['source_url']}", "yellow")
            cprint(f"    Added: {result['timestamp']}", "white")
        return

    if not args.source:
        parser.print_help()
        return

    # Learn from source
    if args.type == 'youtube' or 'youtube.com' in args.source or 'youtu.be' in args.source:
        success = learn_from_youtube(args.source, args.model)
    elif args.type == 'pdf' or args.source.endswith('.pdf'):
        success = learn_from_pdf(args.source, args.model)
    else:
        cprint("❌ Could not determine source type. Use --type flag.", "red")
        return

    if success:
        cprint("\n✅ Successfully learned from source!", "green", attrs=["bold"])
        cprint(f"💾 Knowledge saved to: {DATA_DIR}", "cyan")
    else:
        cprint("\n❌ Failed to learn from source", "red")

if __name__ == "__main__":
    main()
