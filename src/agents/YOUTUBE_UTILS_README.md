# 🌙 YouTube Utils - Usage Guide

Shared YouTube utility functions for all Moon Dev AI agents.

## 📦 Installation

```bash
# Required for transcript features
pip install youtube-transcript-api

# Required for advanced features (metadata, comments, search)
pip install yt-dlp

# Update requirements
pip freeze > requirements.txt
```

## 🚀 Quick Start

```python
from src.agents.youtube_utils import YouTubeUtils

# Create instance
yt = YouTubeUtils()

# Extract video ID from URL
video_id = yt.extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Get transcript
transcript = yt.get_transcript("dQw4w9WgXcQ")
# or
transcript = yt.get_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
```

## 📚 API Reference

### 1. Video ID Extraction

```python
video_id = YouTubeUtils.extract_video_id(url)
```

**Supported formats:**
- `https://www.youtube.com/watch?v=ABC123`
- `https://youtu.be/ABC123`
- `https://m.youtube.com/watch?v=ABC123`
- `ABC123` (direct video ID)

**Example:**
```python
video_id = YouTubeUtils.extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
# Returns: "dQw4w9WgXcQ"
```

---

### 2. Transcript Extraction

```python
transcript = YouTubeUtils.get_transcript(video_id_or_url, languages=['en'])
```

**Args:**
- `video_id_or_url`: YouTube video ID or full URL
- `languages`: List of language codes (default: `['en']`)

**Returns:** Full transcript as string or `None`

**Example:**
```python
# Get English transcript
transcript = YouTubeUtils.get_transcript("dQw4w9WgXcQ")

# Try multiple languages
transcript = YouTubeUtils.get_transcript("dQw4w9WgXcQ", languages=['en', 'nl', 'de'])
```

---

### 3. Transcript with Timestamps

```python
segments = YouTubeUtils.get_transcript_with_timestamps(video_id_or_url, languages=['en'])
```

**Returns:** List of dicts with `'text'`, `'start'`, `'duration'`

**Example:**
```python
segments = YouTubeUtils.get_transcript_with_timestamps("dQw4w9WgXcQ")

for seg in segments[:5]:
    print(f"{seg['start']:.1f}s: {seg['text']}")

# Output:
# 0.0s: We're no strangers to love
# 2.5s: You know the rules and so do I
```

---

### 4. Video Metadata

```python
metadata = YouTubeUtils.get_video_metadata(video_id_or_url)
```

**Returns:** Dict with:
- `title`, `description`, `duration`, `duration_string`
- `view_count`, `like_count`, `upload_date`
- `channel`, `channel_id`, `channel_url`
- `tags`, `categories`, `thumbnail`, `url`

**Example:**
```python
metadata = YouTubeUtils.get_video_metadata("dQw4w9WgXcQ")

print(metadata['title'])
print(f"Views: {metadata['view_count']:,}")
print(f"Duration: {metadata['duration_string']}")
```

---

### 5. Comments

```python
comments = YouTubeUtils.get_comments(video_id_or_url, max_comments=100)
```

**Returns:** List of dicts with `'author'`, `'text'`, `'likes'`, `'reply_count'`, `'timestamp'`

**Example:**
```python
comments = YouTubeUtils.get_comments("dQw4w9WgXcQ", max_comments=50)

# Sentiment analysis
for comment in comments[:10]:
    print(f"{comment['author']}: {comment['text'][:100]}")
    print(f"  👍 {comment['likes']} likes")
```

---

### 6. Search Videos

```python
videos = YouTubeUtils.search_videos(query, max_results=10)
```

**Returns:** List of video dicts

**Example:**
```python
videos = YouTubeUtils.search_videos("bitcoin trading strategy", max_results=10)

for video in videos:
    print(f"{video['title']}")
    print(f"  Channel: {video['channel']}")
    print(f"  Views: {video['views']:,}")
    print(f"  URL: {video['url']}")
```

---

### 7. Channel Latest Videos

```python
videos = YouTubeUtils.get_channel_latest(channel_id_or_handle, max_videos=10)
```

**Supports:**
- Channel handles: `@moondevonyt`
- Channel IDs: `UCxxxxxxxxxxxxxxxxxxx`

**Example:**
```python
# Using handle
videos = YouTubeUtils.get_channel_latest("@moondevonyt", max_videos=5)

# Using channel ID
videos = YouTubeUtils.get_channel_latest("UCxxxxxxxxxxxxxxxxxxx", max_videos=5)

for video in videos:
    print(f"{video['title']} - {video['upload_date']}")
```

---

### 8. Trending Crypto Videos

```python
trending = YouTubeUtils.get_trending_crypto_videos(max_results=20)
```

**Returns:** List of trending crypto/trading videos sorted by views

**Example:**
```python
trending = YouTubeUtils.get_trending_crypto_videos(max_results=10)

for video in trending:
    print(f"{video['title']} - {video['views']:,} views")
```

---

## 🎯 Agent Integration Examples

### Example 1: Research Agent with YouTube

```python
# src/agents/research_agent.py

from src.agents.youtube_utils import YouTubeUtils

yt = YouTubeUtils()

# Search for trading strategies
videos = yt.search_videos("crypto trading strategy 2025", max_results=5)

for video in videos:
    # Get transcript
    transcript = yt.get_transcript(video['video_id'])

    if transcript:
        # Use AI to extract strategy
        strategy = model.generate_response(
            system_prompt="Extract trading strategy from this video transcript",
            user_content=transcript
        )

        # Save to ideas.txt
        with open("src/data/rbi/ideas.txt", "a") as f:
            f.write(f"{video['url']}\n")
```

---

### Example 2: Sentiment Agent with YouTube

```python
# src/agents/sentiment_agent.py

from src.agents.youtube_utils import YouTubeUtils

yt = YouTubeUtils()

# Monitor specific crypto influencer
videos = yt.get_channel_latest("@CryptoInfluencer", max_videos=3)

for video in videos:
    # Get video metadata
    metadata = yt.get_video_metadata(video['video_id'])

    # Get comments for sentiment
    comments = yt.get_comments(video['video_id'], max_comments=100)

    # Analyze sentiment
    bullish_count = sum(1 for c in comments if 'moon' in c['text'].lower() or 'bullish' in c['text'].lower())
    bearish_count = sum(1 for c in comments if 'dump' in c['text'].lower() or 'bearish' in c['text'].lower())

    print(f"{metadata['title']}")
    print(f"  Bullish: {bullish_count}, Bearish: {bearish_count}")
    print(f"  Views: {metadata['view_count']:,}")
```

---

### Example 3: Whale Agent with YouTube

```python
# src/agents/whale_agent.py

from src.agents.youtube_utils import YouTubeUtils

yt = YouTubeUtils()

# Monitor whale influencers
whale_channels = [
    "@CryptoWhale1",
    "@BitcoinBillionaire",
    "@MegaTrader"
]

for channel in whale_channels:
    videos = yt.get_channel_latest(channel, max_videos=1)

    if videos:
        latest = videos[0]

        # Alert if new video in last 24 hours
        if is_recent(latest['upload_date']):
            transcript = yt.get_transcript(latest['video_id'])

            # Extract tokens mentioned
            tokens = extract_tokens(transcript)

            print(f"🐋 Whale alert: {channel}")
            print(f"   Video: {latest['title']}")
            print(f"   Tokens mentioned: {', '.join(tokens)}")
```

---

### Example 4: Tweet Agent with YouTube

```python
# src/agents/tweet_agent.py

from src.agents.youtube_utils import YouTubeUtils

yt = YouTubeUtils()

# Get latest video
videos = yt.get_channel_latest("@moondevonyt", max_videos=1)

if videos:
    video = videos[0]
    transcript = yt.get_transcript(video['video_id'])

    # Extract key moments
    segments = yt.get_transcript_with_timestamps(video['video_id'])

    # Find interesting segments (longer than 30 seconds)
    key_moments = [s for s in segments if s['duration'] > 30]

    # Generate tweet
    tweet = f"🚀 New video: {video['title']}\n\n"
    tweet += f"Key topics:\n"
    for moment in key_moments[:3]:
        tweet += f"• {moment['text'][:100]}...\n"
    tweet += f"\nWatch: {video['url']}"

    print(tweet)
```

---

## 🔄 Backward Compatibility

For agents already using the old functions:

```python
# Old way (still works)
from src.agents.youtube_utils import get_youtube_transcript, extract_video_id

transcript = get_youtube_transcript("dQw4w9WgXcQ")
video_id = extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# New way (recommended)
from src.agents.youtube_utils import YouTubeUtils

transcript = YouTubeUtils.get_transcript("dQw4w9WgXcQ")
video_id = YouTubeUtils.extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
```

---

## ⚠️ Error Handling

The library gracefully handles missing dependencies:

```python
# If youtube-transcript-api not installed
transcript = YouTubeUtils.get_transcript("dQw4w9WgXcQ")
# Prints: ❌ youtube-transcript-api not installed. Run: pip install youtube-transcript-api
# Returns: None

# If yt-dlp not installed
metadata = YouTubeUtils.get_video_metadata("dQw4w9WgXcQ")
# Prints: ❌ yt-dlp not installed. Run: pip install yt-dlp
# Returns: {}
```

Always check for `None` or empty returns:

```python
transcript = YouTubeUtils.get_transcript("dQw4w9WgXcQ")

if transcript:
    # Process transcript
    pass
else:
    print("Failed to get transcript")
```

---

## 🧪 Testing

Run the built-in tests:

```bash
python src/agents/youtube_utils.py
```

Expected output:
```
🌙 Moon Dev's YouTube Utils Test 🌙

📝 Testing video ID extraction...
  https://www.youtube.com/watch?v=dQw4w9WgXcQ → dQw4w9WgXcQ
  https://youtu.be/dQw4w9WgXcQ → dQw4w9WgXcQ
  dQw4w9WgXcQ → dQw4w9WgXcQ

📝 Testing transcript extraction...
  Transcript length: 1234 characters
  First 100 chars: We're no strangers to love...

✅ Tests complete!
🚀 Ready to use in your agents!
```

---

## 📋 Summary

| Feature | Library Required | Returns |
|---------|-----------------|---------|
| **extract_video_id()** | None | str or None |
| **get_transcript()** | youtube-transcript-api | str or None |
| **get_transcript_with_timestamps()** | youtube-transcript-api | List[Dict] or None |
| **get_video_metadata()** | yt-dlp | Dict |
| **get_comments()** | yt-dlp | List[Dict] |
| **search_videos()** | yt-dlp | List[Dict] |
| **get_channel_latest()** | yt-dlp | List[Dict] |
| **get_trending_crypto_videos()** | yt-dlp | List[Dict] |

---

## 🚀 Next Steps

1. **Install dependencies:**
   ```bash
   pip install youtube-transcript-api yt-dlp
   pip freeze > requirements.txt
   ```

2. **Import in your agent:**
   ```python
   from src.agents.youtube_utils import YouTubeUtils
   ```

3. **Start using!**

Built with ❤️ by Moon Dev 🌙
