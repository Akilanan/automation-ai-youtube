from moviepy import *
import random
import os

class VideoEditor:
    def create_multiclip_video(self, segments_data: list, output_path: str, bg_music_path: str = None, remove_watermark: bool = True):
        """
        Assembles a video from multiple [audio, video] segments.
        segments_data: List of dicts {'audio': path, 'video': path}
        """
        try:
            clips = []
            
            for seg in segments_data:
                a_path = seg['audio']
                v_path = seg['video']
                
                # Check existence
                if not os.path.exists(a_path) or not os.path.exists(v_path):
                    print(f"Skipping segment due to missing files: {a_path}, {v_path}")
                    continue

                if os.path.exists(a_path) and os.path.getsize(a_path) > 2000:
                    audio_clip = AudioFileClip(a_path)
                else:
                    # Mock Audio (Silence)
                    # We will create a video without audio for this segment
                    audio_clip = None

                duration = 2.5 # Default mock duration
                if audio_clip:
                     duration = audio_clip.duration
                
                # Create Video Clip & Loop to match Audio
                if os.path.exists(v_path) and os.path.getsize(v_path) > 100000:
                    video_clip = VideoFileClip(v_path)
                else:
                    # Mock Video (Fallback to Professional Background)
                    bg_path = os.path.join(os.path.dirname(__file__), "..", "assets", "fallback_background.png")
                    if os.path.exists(bg_path):
                         # Create Image Clip with Zoom
                         img = ImageClip(bg_path).with_duration(duration).resized(height=1920)
                         # Simple crop center
                         video_clip = img.cropped(x_center=img.w/2, y_center=img.h/2, width=1080, height=1920)
                    else:
                         # Fallback to Color Clip
                         video_clip = ColorClip(size=(1080, 1920), color=(0,0,0), duration=duration)
                
                # Loop visuals to match Audio Duration
                video_clip = video_clip.without_audio() # Remove stock audio
                video_clip = video_clip.with_effects([vfx.Loop(duration=duration)])
                
                # Scale/Crop Logic
                # ... (Zoom/Crop handled below)
                
                if audio_clip:
                     video_clip = video_clip.with_audio(audio_clip)

                # Zoom/Crop for Watermark Removal (1.1x)
                if remove_watermark:
                     w, h = video_clip.size
                     video_clip = video_clip.resized(1.1)
                     video_clip = video_clip.cropped(x_center=video_clip.w/2, y_center=video_clip.h/2, width=w, height=h)
                
                # Pattern Interrupt: Random Zoom on this segment (Static for the whole segment to avoid dizziness, or splitting?)
                # Strategy: Apply a slight zoom movement or static zoom.
                # Here we just apply a static zoom randomly to 50% of clips to vary the visual.
                if random.random() > 0.5:
                     w, h = video_clip.size
                     video_clip = video_clip.cropped(x1=w*0.1, y1=h*0.1, x2=w*0.9, y2=h*0.9).resized(new_size=(w, h))

                clips.append(video_clip)

            if not clips:
                print("No clips created.")
                return None

            # Concatenate all segments using 'compose' method to prevent audio desync
            final_clip = concatenate_videoclips(clips, method="compose")

            # Audio Rotation Logic
            music_file = bg_music_path
            music_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "music")
            
            if not music_file and os.path.exists(music_dir):
                files = [f for f in os.listdir(music_dir) if f.endswith(".mp3")]
                if files:
                    music_file = os.path.join(music_dir, random.choice(files))
                    print(f"Selected viral background music: {music_file}")

            # Add Background Music (if provided or found)
            if music_file and os.path.exists(music_file):
                try:
                    music = AudioFileClip(music_file)
                    music = music.with_effects([vfx.Loop(duration=final_clip.duration)])
                    music = music.with_volume_multiplier(0.10) # 10% volume
                    
                    # Composite Audio
                    final_audio = CompositeAudioClip([final_clip.audio, music])
                    final_clip = final_clip.with_audio(final_audio)
                except Exception as e:
                    print(f"Warning: Could not load background music ({e}). Proceeding without music.")

            # FLASH PROMPT & CAPTIONS (Hormozi Style)
            # ... (Existing logic)

            # SAFETY DISCLAIMER (Mandatory)
            # Adds "Not Financial Advice" to bottom of screen for safety
            disclaimer_path = os.path.join(os.path.dirname(__file__), "..", "assets", "disclaimer.png")
            if os.path.exists(disclaimer_path):
                try:
                    print("Adding safety disclaimer overlay...")
                    # Create disclaimer clip (bottom third)
                    # We resize it to 80% of width to look professional
                    disclaimer = ImageClip(disclaimer_path).with_duration(final_clip.duration)
                    disclaimer = disclaimer.resized(width=final_clip.w * 0.9)
                    # Position at the very bottom
                    disclaimer = disclaimer.with_position(('center', final_clip.h - disclaimer.h - 50))
                    
                    # Composite
                    final_clip = CompositeVideoClip([final_clip, disclaimer])
                    print("✅ Disclaimer added.")
                except Exception as e:
                    print(f"Could not add disclaimer visual: {e}")
            else:
                print("Warning: disclaimer.png not found in assets. Skipping visual disclaimer.")

            # Export with Retry Logic
            # Export with Retry Logic
            try:
                print("Starting render (Safe Mode)...")
                final_clip.write_videofile(
                    output_path, 
                    fps=24, 
                    codec='libx264', 
                    audio_codec='aac', 
                    threads=1, 
                    preset='ultrafast',
                    temp_audiofile='temp-audio.m4a', 
                    remove_temp=True
                )
            except Exception as err:
                print(f"Render failed ({err}). Retrying with minimal settings...")
                final_clip.write_videofile(output_path, fps=24, codec='libx264', threads=1)
            
            return output_path

        except Exception as e:
            print(f"Error editing video: {e}")
            import traceback
            traceback.print_exc()
            return None

    def create_viral_video(self, audio_path: str, visual_path: str, output_path: str, script_data: dict, remove_watermark: bool = True):
        # Legacy single-clip method (kept for fallback)
        pass 
