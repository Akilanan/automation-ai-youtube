import time

class EngagementManager:
    def __init__(self, uploaders: list):
        self.uploaders = uploaders

    def start_calculated_loop(self, video_ids: dict, first_comment: str):
        """
        1. Posts the binary question immediately.
        2. (Mock) Enters a loop to reply to comments for 60 minutes.
        """
        print("\n--- Starting 'Calculated Comment Loop' ---")
        
        # 1. Post Binary Question (The "Ghost" preventer)
        for platform, vid_id in video_ids.items():
            uploader = self._get_uploader(platform)
            if uploader and vid_id:
               uploader.post_comment(vid_id, first_comment)
        
        print("Initial questions posted. Entering 60min engagement monitoring (Mock)...")
        # In a real app, this would be a background task or cron job
        # self.monitor_comments(video_ids)

    def _get_uploader(self, platform_name):
        for u in self.uploaders:
            if platform_name.lower() in str(type(u)).lower():
                return u
        return None
        
    def monitor_comments(self, video_ids):
        # Mock logic
        pass
