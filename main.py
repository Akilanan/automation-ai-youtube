import os
import sys
import requests
import subprocess
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None
    print("Warning: python-dotenv not found. Relying on system env vars.")

# Ensure modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.idea_generator import IdeaGenerator
from modules.asset_generator import AssetGenerator
from modules.video_editor import VideoEditor
from modules.uploader import YouTubeUploader, TikTokUploader, InstagramUploader, FacebookUploader
from modules.engagement import EngagementManager
from modules.analytics import FeedbackLoop

import argparse

def send_telegram_video(video_path, caption):
    """Sends the final video to Telegram via Bot API."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("Telegram credentials missing in .env. Skipping mobile delivery.")
        return

    # 1. Check Size & Compress if needed (> 50MB)
    max_size = 45 * 1024 * 1024 # 45MB safety threshold
    current_size = os.path.getsize(video_path)
    final_path = video_path

    if current_size > max_size:
        print(f"⚠️ Video size ({current_size / (1024*1024):.1f}MB) exceeds Telegram Bot limit. Compressing...")
        final_path = video_path.replace(".mp4", "_compressed.mp4")
        # Find FFmpeg binary
        try:
            import imageio_ffmpeg
            ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
            cmd = [
                ffmpeg_bin, '-y', '-i', video_path,
                '-vcodec', 'libx264', '-crf', '28', 
                '-preset', 'fast', '-acodec', 'aac', '-b:a', '128k',
                final_path
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Compression complete: {os.path.getsize(final_path) / (1024*1024):.1f}MB")
        except Exception as e:
            print(f"❌ Compression failed: {e}. Attempting original send anyway.")
            final_path = video_path

    # 2. Send to Telegram
    print(f"Sending video to Telegram chat {chat_id}...")
    url = f"https://api.telegram.org/bot{token}/sendVideo"
    
    try:
        with open(final_path, 'rb') as video_file:
            files = {'video': video_file}
            data = {'chat_id': chat_id, 'caption': caption}
            response = requests.post(url, files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                print("✅ Video successfully delivered to Telegram!")
            else:
                print(f"❌ Telegram delivery failed: {response.text}")
    except Exception as e:
        print(f"❌ Error sending to Telegram: {e}")
    finally:
        # Cleanup compressed file
        if final_path != video_path and os.path.exists(final_path):
            os.remove(final_path)

def main():
    if load_dotenv:
        load_dotenv()
    print("--- Advanced AI Trading Video Automation (Hyper-Realism Mode) ---")
    
    # Parse CLI Arguments (for n8n Automation)
    parser = argparse.ArgumentParser(description="AI Video Automation")
    parser.add_argument("--topic", type=str, help="Topic for the video (or 'Auto')", default="")
    args = parser.parse_args()
    print(f"DEBUG: main.py started with topic: '{args.topic}'")

    # 1. Feedback Loop: Get insights
    feedback = FeedbackLoop()
    insights = feedback.analyze_and_refine()
    
    # 2. Idea Generation
    idea_gen = IdeaGenerator() 
    
    topic = args.topic
    if not topic:
         # Fallback to interactive input if no arg provided
         topic = input("Enter Trading Topic (or press Enter to auto-detect High Momentum Trend): ")
    
    if not topic.strip() or topic.lower() == "auto":
        print("\n--- 1. MARKET REFLEX SCANNING ---")
        trends = idea_gen.scan_for_trends("Trading & Finance")
        print(f"Top 5 Viral Trends Detected:")
        for i, t in enumerate(trends):
            print(f"  {i+1}. {t}")
        
        # Autonomous Selection: Pick the #1 Trend
        topic = trends[0]
        print(f"\nLocked Target: {topic}")

    print("\n--- 2. DEEP DIVE RESEARCH ---")
    research = idea_gen.deep_research(topic)
    print(f"Research Attributes:\n{research[:500]}...") # Show snippet
    
    print(f"\n--- 3. VIRAL SCRIPT GENERATION ---")
    idea = idea_gen.generate_idea(topic, research_context=research)
    
    if not idea:
        print("Failed to generate idea.")
        return

    print(f"HOOK: {idea['hook_text']}")

    # 3. Asset Generation (Dynamic Multi-Segment)
    asset_gen = AssetGenerator()
    segments_data = [] # List of {audio: path, video: path}
    
    print("Generating assets for each script segment...")
    script_segments = idea.get('script_segments', [])
    
    # Fallback if no segments found (e.g. legacy prompt)
    if not script_segments:
        script_segments = [{"text": idea['hook_text'], "visual_keyword": "Money"}]

    for idx, seg in enumerate(script_segments):
        text = seg.get('text', "")
        keyword = seg.get('visual_keyword', topic)
        
        print(f"  [Segment {idx+1}] Keyword: {keyword}")
        
        # Audio
        # Audio (Auto: ElevenLabs or Edge-TTS)
        audio_path = asset_gen.generate_audio(text)
            
        # Video (Pexels)
        video_path = asset_gen.get_stock_footage(keyword)
        # Create dummy if mock
        if "mock" in video_path and not os.path.exists(video_path):
             with open(video_path, 'wb') as f: f.write(b'\0'*100000)
             
        segments_data.append({"audio": audio_path, "video": video_path})

    # 4. Video Editing (Multi-Clip Assembly)
    editor = VideoEditor()
    output_video = "final_viral_video.mp4"
    bg_music = "music.mp3" # User should provide this, or we mock/download
    if not os.path.exists(bg_music):
         print("No background music found (skipping).")
         bg_music = None
    
    print("Assembling Hyper-Realistic Video...")
    try:
        final_video_path = editor.create_multiclip_video(segments_data, output_video, bg_music_path=bg_music)
    except Exception as e:
        print(f"Editing failed: {e}")
        final_video_path = None

    if not final_video_path:
        print("Complex rendering failed. Using simplified backup video.")
        import shutil
        if os.path.exists("test_output.mp4"):
            shutil.copy("test_output.mp4", output_video)
            final_video_path = output_video
        else:
            print("No backup video found.")
            return

    # 5. Distribution
    uploaders = [
        YouTubeUploader(), 
        TikTokUploader(), 
        InstagramUploader(),
        FacebookUploader()
    ]
    
    uploaded_ids = {}
    for uploader in uploaders:
        platform_name = type(uploader).__name__
        vid_id = uploader.upload(final_video_path, idea['title'], idea['description'])
        uploaded_ids[platform_name] = vid_id

    # 6. Engagement
    engager = EngagementManager(uploaders)
    engager.start_calculated_loop(uploaded_ids, idea['first_comment_question'])
    
    # 7. Log
    feedback.log_upload(idea, uploaded_ids)

    # 8. Mobile Delivery (Fail-safe)
    send_telegram_video(final_video_path, f"🚀 AI Video Ready: {idea['title']}")

    print("--- Automation Cycle Complete ---")

if __name__ == "__main__":
    main()
