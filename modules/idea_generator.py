import os
import json
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    print("Warning: openai module not found. Running in Free Mode.")
import google.generativeai as genai

class IdeaGenerator:
    def __init__(self, api_key=None):
        self.client = None
        key = api_key or os.getenv("OPENAI_API_KEY")
        if key:
            try:
                self.client = OpenAI(api_key=key)
            except Exception as e:
                print(f"Warning: OpenAI init failed: {e}")
        else:
            print("Warning: OPENAI_API_KEY not found. Idea generation will be mocked.")
        
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
        else:
            print("Warning: GEMINI_API_KEY not found.")
        
        self.strategies = [
            "Controversial Opinion", 
            "Historical Fact", 
            "Do This / Don't Do That", 
            "News Reaction", 
            "Personal Story"
        ]
        self.history_file = "training_data/video_history.json"

    def _get_history_constraints(self) -> str:
        """Loads video history and returns a string for negative prompt constraints."""
        print(f"DEBUG: Checking history file at: {os.path.abspath(self.history_file)}")
        if not os.path.exists(self.history_file):
            print("DEBUG: History file not found.")
            return ""
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
                # Get the last 15 unique titles to prevent repetition
                titles = list(set([v.get('title') for v in history if v.get('title')]))[-15:]
                if not titles:
                    return ""
                constraint_msg = f"\nCRITICAL: DO NOT REPEAT these previous video titles or concepts: {', '.join(titles)}"
                print(f"DEBUG: Content Constraints applied for {len(titles)} previous videos.")
                return constraint_msg
        except Exception as e:
            print(f"DEBUG: Error loading history for constraints: {e}")
            return ""

    def select_strategy(self, proven_hooks: list = None) -> str:
        """Autonomously selects a content strategy."""
        import random
        # Logic: If we had real stats, we would weight these. 
        # For now, random rotation ensures variety.
        return random.choice(self.strategies)

    def generate_idea(self, topic: str = "Trading", research_context: str = None) -> dict:
        """
        Generates a viral trading video idea.
        """
        if not self.client:
           if self.gemini_key:
               return self.generate_idea_free(topic, research_context)
           return self.get_emergency_fallback()

        strategy = self.select_strategy()
        
        system_prompt = f"""
        You are a highly successful viral content strategist for a Trading/Finance channel on TikTok.
        Your goal is to create content using the following STRATEGY: **{strategy}**.
        
        STRATEGY INSTRUCTIONS:
        - If 'Controversial': Challenge a popular belief (e.g. "DCA is for losers").
        - If 'Historical': Use a past crash/event to predict the future.
        - If 'Story': Start with "I lost $10k..." or "He turned $100 into...".
        
        CRITICAL RULES:
        
        CRITICAL RULES:
        1.  **Hook (0-3s)**: MUST start with a Contradiction or a Result. NEVER say "In this video...".
            - Example: "Stop using moving averages." or "I turned $100 into $1k in an hour."
        2.  **Pacing**: The script must be designed for visual changes every **2.5 seconds** (Hyper-Fast).
        3.  **Dopamine Engineering**: End every segment with an OPEN LOOP or Cliffhanger (e.g. "But here is the catch...", "Most people miss this...").
        4.  **Flash-Prompt**: You MUST include a "Flash Value" text (e.g., a cheat sheet, a formula, a specific setting) that appears for 0.5s to force users to pause/save.
        5.  **Strict Safety**: NEVER give financial advice. Pivot to "Psychology" or "History". Use phrases like "Educational purposes only".
        6.  **SEO**: The *first sentence* must contain the primary keyword (e.g., "Day Trading", "Crypto", "AI Trading").
        
        OUTPUT FORMAT:
        Return strict JSON with:
        - "title": Viral title.
        - "hook_text": The exact spoken hook.
        - "script_segments": Array of objects: 
             {"text": "spoken words", "visual_cue": "detailed description", "visual_keyword": "single search term for stock video (e.g. 'Bitcoin', 'Stock Chart', 'Money')", "duration_est": 2.5}
        - "flash_prompt_content": The text/data to display on the 0.5s overlay.
        - "flash_prompt_time_index": Suggested second mark to show the flash prompt (e.g., 15).
        - "caption_keywords": List of keywords for on-screen captions.
        - "first_comment_question": A binary question to ask in the comments (e.g. "Bullish or Bearish?").
        - "description": Description with hashtags.
        """
        
        
        user_prompt = f"Generate a viral trading video idea about: {topic}."
        if research_context:
            user_prompt += f"\n\nUSE THIS DEEP RESEARCH:\n{research_context}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"Error generating idea: {e}")
            return self.get_emergency_fallback()

    def get_emergency_fallback(self):
        """Returns a pre-written DEEP viral loop if AI fails."""
        print("[ALERT] Using Emergency Fallback Template (Deep Mode).")
        return {
            "title": "The Hidden Mathematics of Trading",
            "hook_text": "You are losing money because you don't understand this one math equation.",
            "script_segments": [
                {"text": "Most traders think patterns move the market. They are wrong.", "visual_keyword": "Stock Chart Red", "duration_est": 3.0},
                {"text": "The market is actually driven by liquidity algorithms hunting your stops.", "visual_keyword": "Matrix Code", "duration_est": 4.0},
                {"text": "When you buy, a machine is selling to you, trapping you in a liquidity pool.", "visual_keyword": "Trap", "duration_est": 4.0},
                {"text": "Look at this chart. See the wick? That was a stop hunt.", "visual_keyword": "Candlestick Chart", "duration_est": 4.0},
                {"text": "The banks bought exactly where you sold. That is the truth.", "visual_keyword": "Bank Vault", "duration_est": 3.0},
                {"text": "To win, you must trade like a robot, not a gambler.", "visual_keyword": "Robot Hand", "duration_est": 3.0},
                {"text": "The catch is that these traps always happen at previous highs and lows.", "visual_keyword": "Stock Chart Pattern", "duration_est": 4.0},
                {"text": "Subscribe and like for more random facts.", "visual_keyword": "Subscribe Button", "duration_est": 3.0}
            ],
            "flash_prompt_content": "Secret: Trade Liquidity, Not Patterns",
            "flash_prompt_time_index": 10,
            "caption_keywords": ["Liquidity", "Banks", "Trap", "Win"],
            "first_comment_question": "Do you trade Support/Resistance or Liquidity?",
            "description": "#trading #finance #smartmoney #shorts"
        }

    def generate_idea_free(self, topic: str, research_context: str = None) -> dict:
        """Generates idea using Google Gemini (Free Tier)."""
        print("Using Google Gemini (Free Tier)...")
        model = genai.GenerativeModel('gemini-flash-latest')
        
        constraints = self._get_history_constraints()
        prompt = f"""
        Act as a Master Trading Educator and Viral Content Strategist. 
        Create a DEEP, EDUCATIONAL, yet VIRAL video script about: {topic}.

        {constraints}

        RESEARCH CONTEXT to Use: 
        {research_context if research_context else "General Knowledge. Explain the core concept deeply."}

        SCRIPT REQUIREMENTS:
        1. **Educational Depth**: Do not just skim the surface. Explain the "HOW" and "WHY". 
           - If discussing a strategy, give the exact settings. 
           - If discussing a crash, explain the root cause.
        2. **Structure**: 
           - Segment 1: The Hook (The Lie/Common Mistake). 
           - Segment 2-5: The Step-by-Step Explanation (The Truth).
           - Segment 6: The "Aha!" Moment/Result.
           - Segment 7: The CTA "Subscribe and like for more random facts".
        3. **Length**: Create exactly 7 segments. Total duration ~45-60 seconds.
        4. **Visuals**: Suggest specific stock footage keywords (e.g. "Bitcoin Chart", "Money Printing", "Trader Stress").

        Return ONLY valid JSON (no markdown formatting) with this structure:
        {{
            "title": "Viral Title",
            "hook_text": "Spoken hook",
            "script_segments": [
                 {{"text": "spoken words (2-3 sentences)", "visual_keyword": "search term", "duration_est": 5.0}}
            ],
            "flash_prompt_content": "Quick text overlay (Value Bomb)",
            "flash_prompt_time_index": 10,
            "caption_keywords": ["Keyword1", "Keyword2"],
            "first_comment_question": "Engaging Question?",
            "description": "hashtags"
        }}
        """
        try:
            response = model.generate_content(prompt)
            # Cleanup markdown if present
            clean_text = response.text.replace("```json", "").replace("```", "")
            return json.loads(clean_text)
        except Exception as e:
            print(f"Gemini Error: {e}")
            return self.get_emergency_fallback()

    def get_trending_topic(self, niche: str = "Trading") -> str:
        """
        Asks ChatGPT for the #1 most viral trending topic.
        """
        if not self.client:
            print("Mocking trending topic request (No API Key).")
            return "Bitcoin Halving Impact (Mock)"

        system_prompt = f"""
        You are a Global Market Pulse Scanner for {niche}.
        SEARCH EVERYTHING: Scan Sentiment across Crypto Twitter, Reddit (WallStreetBets), Financial News (Bloomberg/CNBC), and Macro-Economic Calendars.
        Identify the #1 MOST VIRAL, "Breaking News" topic right now. It must be something people are actively searching for.
        Return ONLY the topic name as a plain string. No explanations.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "What is the #1 trending topic right now?"}],
                max_tokens=20
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error fetching trend: {e}")
            return "Bitcoin Price Action"

    def scan_for_trends(self, niche: str = "Trading") -> list:
        """Returns top 5 viral trends."""
        print(f"Scanning deep for top 5 {niche} trends...")
        if not self.gemini_key:
             return ["Bitcoin", "Nvidia", "Inflation", "Gold", "AI Bubble"] # Fallback

        model = genai.GenerativeModel('gemini-flash-latest')
        constraints = self._get_history_constraints()
        prompt = f"List the Top 5 Most Viral Trending Topics in {niche} right now. {constraints} Return ONLY a JSON list of strings."
        try:
            response = model.generate_content(prompt)
            clean_text = response.text.replace("```json", "").replace("```", "")
            return json.loads(clean_text)
        except:
             return ["Bitcoin", "AI Trading", "Market Crash", "Interest Rates", "Passive Income"]

    def deep_research(self, topic: str) -> str:
        """Performs deep research on the topic."""
        print(f"Performing Deep Research on: {topic}...")
        if not self.gemini_key:
            return "Mock Research: This topic is trending due to recent price action."
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"""
        Analyze the topic '{topic}' for a viral video.
        Return a short research summary covering:
        1. The Lie (Misconception).
        2. The Truth (Data-backed fact).
        3. The Anger (Why are people mad?).
        4. The Hook Angle.
        Keep it concise.
        """
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Research failed: {e}"


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    generator = IdeaGenerator()
    # Test with a common trading topic
    idea = generator.generate_idea("RSI Indicator Secrets")
    print(json.dumps(idea, indent=2))
