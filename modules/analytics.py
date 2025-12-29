import json
import os

class FeedbackLoop:
    def __init__(self, history_file="training_data/video_history.json"):
        self.history_file = history_file
        # Ensure dir exists
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        
    def log_upload(self, video_data: dict, platform_ids: dict):
        """
        Log the upload details to tracking file.
        """
        entry = {
            "title": video_data.get('title'),
            "hook": video_data.get('hook_text'),
            "flash_prompt": video_data.get('flash_prompt_content'),
            "platform_ids": platform_ids,
            "metrics": {"views": 0, "shares": 0, "saves": 0} # Init metrics
        }
        
        history = self._load_history()
        history.append(entry)
        self._save_history(history)
        print(f"Logged video to history: {video_data.get('title')}")

    def analyze_and_refine(self):
        """
        Analyzes logged videos. Returns insights to improve 'IdeaGenerator'.
        Mock implementation: Returns a string to append to system prompt.
        """
        history = self._load_history()
        if not history:
            return ""

        # Mock Logic: Find videos with > 1000 views (simulated)
        # In reality, this would fetch updated stats from APIs first.
        high_performers = [v for v in history if v['metrics']['views'] > 1000]
        
        if high_performers:
            hooks = [v['hook'] for v in high_performers]
            return f"Proven viral hooks from history: {hooks}"
        return ""

    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_history(self, data):
        with open(self.history_file, 'w') as f:
            json.dump(data, f, indent=2)
