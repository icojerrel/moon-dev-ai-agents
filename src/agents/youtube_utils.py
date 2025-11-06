"""
🌙 Moon Dev's YouTube Utility Functions
Shared across all agents for YouTube integration

Features:
- Transcript extraction (auto & manual)
- Video metadata fetching
- Comment analysis
- Channel monitoring
- Search functionality

Usage:
    from src.agents.youtube_utils import YouTubeUtils

    yt = YouTubeUtils()

    # Get transcript
    transcript = yt.get_transcript("dQw4w9WgXcQ")

    # Search videos
    videos = yt.search_videos("bitcoin trading strategy")

    # Get metadata
    metadata = yt.get_video_metadata("dQw4w9WgXcQ")

Created with ❤️ by Moon Dev
"""

import re
from typing import Optional, Dict, List

# Optional imports - gracefully handle missing dependencies
try:
    from termcolor import cprint
except ImportError:
    # Fallback if termcolor is not installed
    def cprint(text, color=None, bg_color=None, attrs=None):
        print(text)

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None
    cprint("⚠️ youtube-transcript-api not installed. Transcript features will be unavailable.", "yellow")
    cprint("   Install with: pip install youtube-transcript-api", "yellow")

try:
    import yt_dlp
except ImportError:
    yt_dlp = None
    cprint("⚠️ yt-dlp not installed. Advanced features (metadata, comments, search) will be unavailable.", "yellow")
    cprint("   Install with: pip install yt-dlp", "yellow")


class YouTubeUtils:
    """Centralized YouTube functionality for all agents"""

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats

        Supports:
        - https://www.youtube.com/watch?v=ABC123
        - https://youtu.be/ABC123
        - https://www.youtube.com/watch?v=ABC123&t=60s
        - https://m.youtube.com/watch?v=ABC123

        Args:
            url: YouTube URL or video ID

        Returns:
            Video ID string or None if not found

        Example:
            >>> YouTubeUtils.extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            'dQw4w9WgXcQ'
        """
        # If it's already a video ID (11 characters, alphanumeric + - and _)
        if len(url) == 11 and re.match(r'^[0-9A-Za-z_-]{11}$', url):
            return url

        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'youtu\.be\/([0-9A-Za-z_-]{11})',
            r'embed\/([0-9A-Za-z_-]{11})',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        cprint(f"⚠️ Could not extract video ID from: {url}", "yellow")
        return None

    @staticmethod
    def get_transcript(video_id_or_url: str, languages: List[str] = ['en']) -> Optional[str]:
        """
        Get transcript from YouTube video

        Args:
            video_id_or_url: YouTube video ID or full URL
            languages: List of language codes to try (default: ['en'])

        Returns:
            Full transcript as string or None if failed

        Example:
            >>> transcript = YouTubeUtils.get_transcript("dQw4w9WgXcQ")
            >>> print(transcript[:100])
        """
        if YouTubeTranscriptApi is None:
            cprint("❌ youtube-transcript-api not installed. Run: pip install youtube-transcript-api", "red")
            return None

        try:
            # Extract video ID if URL was provided
            video_id = YouTubeUtils.extract_video_id(video_id_or_url)
            if not video_id:
                cprint("❌ Invalid video ID or URL", "red")
                return None

            # Use the new API method
            api = YouTubeTranscriptApi()
            transcript_data = api.fetch(video_id, languages=languages)

            # Extract text from transcript data
            transcript_text = ' '.join([entry['text'] for entry in transcript_data])

            cprint(f"✅ Transcript extracted: {len(transcript_text)} chars", "green")
            return transcript_text

        except Exception as e:
            cprint(f"❌ Failed to get transcript: {e}", "red")
            return None

    @staticmethod
    def get_transcript_with_timestamps(video_id_or_url: str, languages: List[str] = ['en']) -> Optional[List[Dict]]:
        """
        Get transcript with timestamps from YouTube video

        Args:
            video_id_or_url: YouTube video ID or full URL
            languages: List of language codes to try

        Returns:
            List of dicts with 'text', 'start', 'duration' or None if failed

        Example:
            >>> segments = YouTubeUtils.get_transcript_with_timestamps("dQw4w9WgXcQ")
            >>> for seg in segments[:3]:
            >>>     print(f"{seg['start']:.1f}s: {seg['text']}")
        """
        if YouTubeTranscriptApi is None:
            cprint("❌ youtube-transcript-api not installed. Run: pip install youtube-transcript-api", "red")
            return None

        try:
            video_id = YouTubeUtils.extract_video_id(video_id_or_url)
            if not video_id:
                return None

            # Use the new API method
            api = YouTubeTranscriptApi()
            segments = api.fetch(video_id, languages=languages)

            cprint(f"✅ Transcript with timestamps extracted: {len(segments)} segments", "green")
            return segments

        except Exception as e:
            cprint(f"❌ Failed to get transcript with timestamps: {e}", "red")
            return None

    @staticmethod
    def get_video_metadata(video_id_or_url: str) -> Dict:
        """
        Get video metadata using yt-dlp

        Args:
            video_id_or_url: YouTube video ID or full URL

        Returns:
            Dict with: title, description, duration, view_count, like_count,
                      upload_date, channel, channel_id, tags, thumbnail, url

        Example:
            >>> metadata = YouTubeUtils.get_video_metadata("dQw4w9WgXcQ")
            >>> print(metadata['title'])
            >>> print(f"Views: {metadata['view_count']:,}")
        """
        if yt_dlp is None:
            cprint("❌ yt-dlp not installed. Run: pip install yt-dlp", "red")
            return {}

        try:
            video_id = YouTubeUtils.extract_video_id(video_id_or_url)
            if not video_id:
                return {}

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)

                metadata = {
                    'video_id': video_id,
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'title': info.get('title'),
                    'description': info.get('description'),
                    'duration': info.get('duration'),  # seconds
                    'duration_string': info.get('duration_string'),  # HH:MM:SS format
                    'view_count': info.get('view_count'),
                    'like_count': info.get('like_count'),
                    'upload_date': info.get('upload_date'),
                    'channel': info.get('uploader'),
                    'channel_id': info.get('channel_id'),
                    'channel_url': info.get('channel_url'),
                    'tags': info.get('tags', []),
                    'categories': info.get('categories', []),
                    'thumbnail': info.get('thumbnail'),
                }

                cprint(f"✅ Metadata fetched: {metadata['title']}", "green")
                return metadata

        except Exception as e:
            cprint(f"❌ Failed to get metadata: {e}", "red")
            return {}

    @staticmethod
    def get_comments(video_id_or_url: str, max_comments: int = 100) -> List[Dict]:
        """
        Get top comments from a video

        Args:
            video_id_or_url: YouTube video ID or full URL
            max_comments: Maximum number of comments to fetch (default: 100)

        Returns:
            List of dicts with: author, text, likes, reply_count, timestamp

        Example:
            >>> comments = YouTubeUtils.get_comments("dQw4w9WgXcQ", max_comments=50)
            >>> for comment in comments[:5]:
            >>>     print(f"{comment['author']}: {comment['text'][:100]}")
        """
        if yt_dlp is None:
            cprint("❌ yt-dlp not installed. Run: pip install yt-dlp", "red")
            return []

        try:
            video_id = YouTubeUtils.extract_video_id(video_id_or_url)
            if not video_id:
                return []

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'getcomments': True,
                'max_comments': max_comments,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)

                comments = []
                for comment in info.get('comments', [])[:max_comments]:
                    comments.append({
                        'author': comment.get('author'),
                        'text': comment.get('text'),
                        'likes': comment.get('like_count', 0),
                        'reply_count': comment.get('reply_count', 0),
                        'timestamp': comment.get('timestamp'),
                    })

                cprint(f"✅ Fetched {len(comments)} comments", "green")
                return comments

        except Exception as e:
            cprint(f"❌ Failed to get comments: {e}", "red")
            return []

    @staticmethod
    def search_videos(query: str, max_results: int = 10, sort_by: str = 'relevance') -> List[Dict]:
        """
        Search YouTube for videos

        Args:
            query: Search query string
            max_results: Maximum number of results (default: 10)
            sort_by: Sort order - 'relevance', 'upload_date', 'view_count', 'rating'

        Returns:
            List of dicts with: video_id, title, channel, duration, views, upload_date, url

        Example:
            >>> videos = YouTubeUtils.search_videos("bitcoin trading strategy", max_results=5)
            >>> for video in videos:
            >>>     print(f"{video['title']} - {video['views']:,} views")
        """
        if yt_dlp is None:
            cprint("❌ yt-dlp not installed. Run: pip install yt-dlp", "red")
            return []

        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'force_generic_extractor': False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_url = f"ytsearch{max_results}:{query}"
                info = ydl.extract_info(search_url, download=False)

                results = []
                for entry in info.get('entries', []):
                    results.append({
                        'video_id': entry.get('id'),
                        'title': entry.get('title'),
                        'channel': entry.get('uploader'),
                        'channel_id': entry.get('channel_id'),
                        'duration': entry.get('duration'),
                        'duration_string': entry.get('duration_string'),
                        'views': entry.get('view_count'),
                        'upload_date': entry.get('upload_date'),
                        'url': f"https://www.youtube.com/watch?v={entry.get('id')}"
                    })

                cprint(f"✅ Found {len(results)} videos for '{query}'", "green")
                return results

        except Exception as e:
            cprint(f"❌ Search failed: {e}", "red")
            return []

    @staticmethod
    def get_channel_latest(channel_id_or_handle: str, max_videos: int = 10) -> List[Dict]:
        """
        Get latest videos from a channel

        Args:
            channel_id_or_handle: YouTube channel ID or handle (@username)
            max_videos: Maximum number of videos to fetch (default: 10)

        Returns:
            List of video dicts with: video_id, title, duration, views, upload_date, url

        Example:
            >>> videos = YouTubeUtils.get_channel_latest("@moondevonyt", max_videos=5)
            >>> for video in videos:
            >>>     print(f"{video['title']} - {video['upload_date']}")
        """
        if yt_dlp is None:
            cprint("❌ yt-dlp not installed. Run: pip install yt-dlp", "red")
            return []

        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'playlistend': max_videos,
            }

            # Support both channel IDs and handles
            if channel_id_or_handle.startswith('@'):
                url = f"https://www.youtube.com/{channel_id_or_handle}/videos"
            else:
                url = f"https://www.youtube.com/channel/{channel_id_or_handle}/videos"

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                videos = []
                for entry in info.get('entries', [])[:max_videos]:
                    if entry:  # Skip None entries
                        videos.append({
                            'video_id': entry.get('id'),
                            'title': entry.get('title'),
                            'duration': entry.get('duration'),
                            'duration_string': entry.get('duration_string'),
                            'views': entry.get('view_count'),
                            'upload_date': entry.get('upload_date'),
                            'url': f"https://www.youtube.com/watch?v={entry.get('id')}"
                        })

                cprint(f"✅ Fetched {len(videos)} latest videos from channel", "green")
                return videos

        except Exception as e:
            cprint(f"❌ Failed to get channel videos: {e}", "red")
            return []

    @staticmethod
    def get_trending_crypto_videos(max_results: int = 20) -> List[Dict]:
        """
        Get trending cryptocurrency/trading videos

        Args:
            max_results: Maximum number of videos to return

        Returns:
            List of trending video dicts

        Example:
            >>> trending = YouTubeUtils.get_trending_crypto_videos(max_results=10)
            >>> for video in trending:
            >>>     print(f"{video['title']} - {video['views']:,} views")
        """
        queries = [
            "bitcoin price prediction today",
            "crypto trading live",
            "altcoin news today",
        ]

        all_videos = []
        for query in queries:
            videos = YouTubeUtils.search_videos(query, max_results=max_results // len(queries))
            all_videos.extend(videos)

        # Sort by views
        all_videos.sort(key=lambda x: x.get('views', 0) or 0, reverse=True)

        return all_videos[:max_results]


# Convenience functions for backward compatibility with existing agents
def get_youtube_transcript(video_id: str) -> Optional[str]:
    """
    Legacy function for backward compatibility
    Use YouTubeUtils.get_transcript() instead

    Example:
        >>> transcript = get_youtube_transcript("dQw4w9WgXcQ")
    """
    return YouTubeUtils.get_transcript(video_id)


def extract_video_id(url: str) -> Optional[str]:
    """
    Legacy function for backward compatibility
    Use YouTubeUtils.extract_video_id() instead

    Example:
        >>> video_id = extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    """
    return YouTubeUtils.extract_video_id(url)


if __name__ == "__main__":
    """
    Test the YouTube utilities
    Run: python src/agents/youtube_utils.py
    """
    cprint("\n🌙 Moon Dev's YouTube Utils Test 🌙\n", "cyan")

    # Test video ID extraction
    cprint("📝 Testing video ID extraction...", "yellow")
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "dQw4w9WgXcQ",
    ]
    for url in test_urls:
        video_id = YouTubeUtils.extract_video_id(url)
        print(f"  {url} → {video_id}")

    # Test transcript (use a real video ID)
    cprint("\n📝 Testing transcript extraction...", "yellow")
    test_video_id = "dQw4w9WgXcQ"
    transcript = YouTubeUtils.get_transcript(test_video_id)
    if transcript:
        print(f"  Transcript length: {len(transcript)} characters")
        print(f"  First 100 chars: {transcript[:100]}...")

    cprint("\n✅ Tests complete!", "green")
    cprint("🚀 Ready to use in your agents!", "cyan")
