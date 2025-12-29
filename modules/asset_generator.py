import os

# Try importing ElevenLabs, gracefully disable if missing
try:
    from elevenlabs import ElevenLabs
except ImportError:
    ElevenLabs = None
    print("Warning: 'elevenlabs' module not found or failed to import. Audio generation will be mocked.")
    
import requests
import random

import edge_tts
import asyncio

class AssetGenerator:
    def __init__(self):
        self.eleven = None
        if ElevenLabs and os.getenv("ELEVENLABS_API_KEY"):
            try:
                self.eleven = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
            except Exception as e:
                print(f"Error initializing ElevenLabs: {e}")
        
        self.pexels_key = os.getenv("PEXELS_API_KEY")

    def generate_audio(self, text: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb") -> str:
        """
        Generates audio using ElevenLabs or Edge-TTS (Free).
        """
        if not self.eleven:
            print("ElevenLabs key missing. Using FREE Edge-TTS.")
            return self.generate_audio_free(text)

        print(f"Generating audio (ElevenLabs) for: {text[:30]}...")
        try:
            audio = self.eleven.generate(
                text=text,
                voice=voice_id,
                model="eleven_monolingual_v1"
            )
            output_path = f"output_audio_{random.randint(1000,9999)}.mp3"
            with open(output_path, "wb") as f:
                for chunk in audio:
                    f.write(chunk)
            return output_path
        except Exception as e:
            print(f"ElevenLabs Error: {e}. Falling back to Free TTS.")
            return self.generate_audio_free(text)

    def generate_audio_free(self, text: str, voice: str = "en-US-JennyNeural") -> str:
        """Generates audio using Microsoft Edge TTS (Free)."""
        output_path = f"output_audio_free_{random.randint(1000,9999)}.mp3"
        # Alternatives: en-US-GuyNeural, en-US-AriaNeural, en-GB-RyanNeural
        
        async def _save():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            
        try:
            asyncio.run(_save())
            print(f"Generated FREE audio: {output_path} ({voice})")
            return output_path
        except Exception as e:
            print(f"EdgeTTS Error: {e}")
            return "mock_audio.mp3"

    def get_stock_footage(self, query: str, duration_min: int = 3) -> str:
        """
        Fetches a stock video from Pexels based on the query.
        """
        print(f"Fetching stock footage from Pexels for: {query}")
        
        if not self.pexels_key:
            print("No PEXELS_API_KEY found. Using mock stock.")
            return "mock_stock.mp4"
            
        try:
            headers = {"Authorization": self.pexels_key}
            url = f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=portrait"
            response = requests.get(url, headers=headers)
            data = response.json()
            
            if data['videos']:
                # Get the first video file url (HD or SD)
                video_files = data['videos'][0]['video_files']
                # Prefer HD
                best_video = next((v for v in video_files if v['width'] == 1080 and v['height'] == 1920), video_files[0])
                download_url = best_video['link']
                
                # Download
                local_filename = f"stock_{query.replace(' ', '_')}_{random.randint(100,999)}.mp4"
                print(f"Downloading {local_filename}...")
                with requests.get(download_url, stream=True) as r:
                    r.raise_for_status()
                    with open(local_filename, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                return local_filename
            else:
                print("No videos found on Pexels.")
                return "mock_stock.mp4"

        except Exception as e:
            print(f"Pexels Error: {e}")
            return "mock_stock.mp4"

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    assets = AssetGenerator()
    # Mock test
    # assets.get_stock_footage("Money")
