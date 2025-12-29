from abc import ABC, abstractmethod
import os

class Uploader(ABC):
    @abstractmethod
    def upload(self, video_path: str, title: str, description: str):
        pass
    
    @abstractmethod
    def post_comment(self, video_id: str, text: str):
        pass

class YouTubeUploader(Uploader):
    def upload(self, video_path: str, title: str, description: str):
        print(f"[YouTube] Uploading {video_path}...")
        # TODO: Google API
        return "mock_yt_video_id"
    
    def post_comment(self, video_id: str, text: str):
         print(f"[YouTube] Posting comment on {video_id}: {text}")

class TikTokUploader(Uploader):
    def upload(self, video_path: str, title: str, description: str):
        print(f"[TikTok] Uploading {video_path}...")
        # TODO: Selenium/Unofficial API
        return "mock_tiktok_video_id"
        
    def post_comment(self, video_id: str, text: str):
         print(f"[TikTok] Posting comment on {video_id}: {text}")

class InstagramUploader(Uploader):
    def upload(self, video_path: str, title: str, description: str):
        print(f"[Instagram] Uploading {video_path}...")
        # TODO: Instagram Graph API or Selenium
        return "mock_insta_video_id"

    def post_comment(self, video_id: str, text: str):
         print(f"[Instagram] Posting comment on {video_id}: {text}")

class FacebookUploader(Uploader):
    def upload(self, video_path: str, title: str, description: str):
        print(f"[Facebook] Uploading {video_path}...")
        # TODO: Graph API
        return "mock_fb_video_id"

    def post_comment(self, video_id: str, text: str):
         print(f"[Facebook] Posting comment on {video_id}: {text}")
