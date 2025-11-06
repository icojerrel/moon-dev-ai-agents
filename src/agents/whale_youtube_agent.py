'''
🌙 Moon Dev's Whale YouTube Monitor Agent
Built with love by Moon Dev 🚀

This agent monitors YouTube channels of known crypto whales and influencers.
Alerts when new videos are posted and extracts tokens/strategies mentioned.

Features:
- Monitors whale/influencer YouTube channels
- Alerts on new video uploads
- Extracts transcript and mentioned tokens
- Correlates with on-chain whale activity
- Voice alerts for important whale videos

Created with ❤️ by Moon Dev
'''

# Configuration
WHALE_CHANNELS = [
    "@moondevonyt",
    "@CoinBureau",
    "@AltcoinDaily",
    "@CryptoBanter",
    "@InvestAnswers",
]

CHECK_INTERVAL_MINUTES = 30  # How often to check for new videos
ALERT_ON_NEW_VIDEO = True  # Voice alert when whale posts new video
EXTRACT_TOKENS = True  # Extract token mentions from transcripts

# Voice settings
VOICE_MODEL = "tts-1"
VOICE_NAME = "onyx"  # Whale voice = deep onyx
VOICE_SPEED = 1.0

import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from termcolor import cprint
import pandas as pd
import openai
from src.agents.youtube_utils import YouTubeUtils
from dotenv import load_dotenv
import re

load_dotenv()
openai.api_key = os.getenv("OPENAI_KEY")

# Data storage
DATA_DIR = Path("src/data/whale_youtube")
DATA_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_FILE = DATA_DIR / "whale_videos_history.csv"
AUDIO_DIR = Path("src/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

class WhaleYouTubeAgent:
    def __init__(self):
        """Initialize Whale YouTube Monitor"""
        self.yt = YouTubeUtils()
        self.video_history = self.load_history()

        cprint("🐋 Moon Dev's Whale YouTube Monitor initialized!", "cyan")
        cprint(f"📹 Monitoring {len(WHALE_CHANNELS)} whale channels", "yellow")
        cprint(f"⏱️ Checking every {CHECK_INTERVAL_MINUTES} minutes", "magenta")

    def load_history(self):
        """Load video history to track what we've already seen"""
        if HISTORY_FILE.exists():
            df = pd.read_csv(HISTORY_FILE)
            cprint(f"📚 Loaded {len(df)} videos from history", "green")
            return set(df['video_id'].tolist())
        else:
            # Create empty history file
            pd.DataFrame(columns=['timestamp', 'channel', 'video_id', 'title', 'tokens_found']).to_csv(HISTORY_FILE, index=False)
            return set()

    def save_video(self, channel, video_id, title, tokens):
        """Save new video to history"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tokens_str = ','.join(tokens) if tokens else ''

        # Append to CSV
        df = pd.DataFrame([[timestamp, channel, video_id, title, tokens_str]],
                         columns=['timestamp', 'channel', 'video_id', 'title', 'tokens_found'])
        df.to_csv(HISTORY_FILE, mode='a', header=False, index=False)

        # Update in-memory history
        self.video_history.add(video_id)

    def extract_tokens(self, text):
        """Extract cryptocurrency token mentions from text"""
        # Common crypto tokens (expand this list as needed)
        known_tokens = [
            'bitcoin', 'btc', 'ethereum', 'eth', 'solana', 'sol',
            'cardano', 'ada', 'ripple', 'xrp', 'polkadot', 'dot',
            'avalanche', 'avax', 'polygon', 'matic', 'chainlink', 'link',
            'uniswap', 'uni', 'litecoin', 'ltc', 'monero', 'xmr'
        ]

        text_lower = text.lower()
        found_tokens = []

        for token in known_tokens:
            # Use word boundaries to avoid false matches
            pattern = r'\b' + re.escape(token) + r'\b'
            if re.search(pattern, text_lower):
                if token not in found_tokens:
                    found_tokens.append(token.upper())

        return found_tokens

    def announce(self, message):
        """Voice announcement"""
        if not ALERT_ON_NEW_VIDEO:
            return

        try:
            cprint(f"🔊 Announcing: {message}", "yellow")

            response = openai.audio.speech.create(
                model=VOICE_MODEL,
                voice=VOICE_NAME,
                input=message,
                speed=VOICE_SPEED
            )

            # Save and play
            audio_file = AUDIO_DIR / f"whale_alert_{int(time.time())}.mp3"
            response.stream_to_file(str(audio_file))

            # Play audio (macOS/Linux)
            os.system(f"afplay {audio_file} 2>/dev/null || mpg123 {audio_file} 2>/dev/null &")

        except Exception as e:
            cprint(f"❌ Voice announcement error: {str(e)}", "red")

    def check_channel(self, channel):
        """Check a channel for new videos"""
        try:
            cprint(f"\n🔍 Checking channel: {channel}", "cyan")

            # Get latest video
            videos = self.yt.get_channel_latest(channel, max_videos=1)

            if not videos:
                cprint(f"   ⚠️ No videos found", "yellow")
                return

            video = videos[0]
            video_id = video['video_id']
            title = video['title']

            # Check if we've seen this video before
            if video_id in self.video_history:
                cprint(f"   ✓ Already processed", "green")
                return

            # NEW VIDEO ALERT!
            cprint(f"   🚨 NEW WHALE VIDEO DETECTED!", "red")
            cprint(f"   📹 {title}", "yellow")
            cprint(f"   📅 Uploaded: {video['upload_date']}", "cyan")
            cprint(f"   👀 Views: {video.get('views', 'N/A'):,}" if video.get('views') else "   👀 Views: N/A", "magenta")

            # Extract tokens if enabled
            tokens_found = []

            if EXTRACT_TOKENS:
                cprint("   📝 Extracting transcript...", "yellow")
                transcript = self.yt.get_transcript(video_id)

                if transcript:
                    cprint(f"   ✅ Transcript: {len(transcript)} chars", "green")

                    # Extract tokens
                    tokens_found = self.extract_tokens(transcript)

                    if tokens_found:
                        cprint(f"   💎 Tokens mentioned: {', '.join(tokens_found)}", "cyan")
                    else:
                        cprint("   ℹ️ No specific tokens mentioned", "yellow")
                else:
                    cprint("   ⚠️ No transcript available", "yellow")

            # Save to history
            self.save_video(channel, video_id, title, tokens_found)

            # Voice alert
            if ALERT_ON_NEW_VIDEO:
                whale_name = channel.replace('@', '').replace('onyt', '')
                alert_msg = f"Whale alert! {whale_name} just posted a new video about "

                if tokens_found:
                    alert_msg += ', '.join(tokens_found[:3])  # Max 3 tokens
                else:
                    alert_msg += "crypto trading"

                self.announce(alert_msg)

            # Print summary
            cprint("\n" + "="*60, "green")
            cprint(f"🐋 WHALE VIDEO SUMMARY", "white")
            cprint(f"Channel: {channel}", "cyan")
            cprint(f"Title: {title[:60]}...", "yellow")
            cprint(f"URL: {video['url']}", "magenta")
            if tokens_found:
                cprint(f"Tokens: {', '.join(tokens_found)}", "green")
            cprint("="*60 + "\n", "green")

        except Exception as e:
            cprint(f"   ❌ Error: {str(e)}", "red")

    def run(self):
        """Run whale monitoring loop"""
        cprint("\n🐋 Starting Whale YouTube Monitor...\n", "cyan")

        try:
            while True:
                cprint(f"\n🔄 Checking whale channels... {datetime.now().strftime('%H:%M:%S')}", "yellow")

                for channel in WHALE_CHANNELS:
                    self.check_channel(channel)
                    time.sleep(2)  # Rate limiting between channels

                # Wait for next check
                next_check = datetime.now() + timedelta(minutes=CHECK_INTERVAL_MINUTES)
                cprint(f"\n😴 Next check at {next_check.strftime('%H:%M:%S')}", "cyan")
                time.sleep(60 * CHECK_INTERVAL_MINUTES)

        except KeyboardInterrupt:
            cprint("\n👋 Whale YouTube Monitor shutting down...", "yellow")
        except Exception as e:
            cprint(f"\n❌ Fatal error: {str(e)}", "red")

if __name__ == "__main__":
    agent = WhaleYouTubeAgent()
    agent.run()
