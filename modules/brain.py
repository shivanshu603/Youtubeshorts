import os
import json
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class ContentBrain:
    
    def __init__(self):
        self.state_file = "stories_state.json"
        self.state = self.load_state()

    def load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "current_story": {"title": "", "genre": "", "part_number": 1, "max_parts": 10, "summary_so_far": "", "characters": []},
            "last_run": ""
        }

    def save_state(self, new_state):
        self.state["current_story"] = new_state
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=4, ensure_ascii=False)

    def generate_script(self):
        print("🎬 Autonomous Movie Story Mode Started...")

        current = self.state["current_story"]

        prompt = f"""
You are an autonomous Cinematic Storyteller AI running a never-ending YouTube Shorts mini-movie series.

CURRENT STATE:
{json.dumps(current, indent=2)}

IMPORTANT RULES:
- Script **MUST be in English only**.
- Write dramatic, emotional, cinematic style.
- Length: 45-60 seconds when spoken.
- Strong hook at start.
- End with powerful cliffhanger.

Return ONLY this JSON format:
[
  {{
    "id": 1,
    "text": "Full spoken English script here (45-60 seconds)",
    "visual_1": "first scene stock footage keywords",
    "visual_2": "second scene stock footage keywords"
  }}
]
"""

        models = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-3.1-flash"]

        for model_name in models:
            for attempt in range(3):
                try:
                    print(f"🔄 Trying {model_name} (Attempt {attempt+1})")
                    response = client.models.generate_content(model=model_name, contents=prompt)
                    clean = response.text.strip().replace("```json", "").replace("```", "").strip()
                    result = json.loads(clean)

                    # Save state for continuity
                    if isinstance(result, list) and len(result) > 0:
                        updated_state = result[0].get("updated_state", current)
                        self.save_state(updated_state)

                    print(f"✅ SUCCESS with {model_name}")
                    return result   # Return list (jo audio.py expect karta hai)

                except Exception as e:
                    err = str(e)
                    print(f"❌ Failed {model_name}: {err[:120]}")
                    if "503" in err or "high demand" in err or "UNAVAILABLE" in err:
                        time.sleep(10)
                        continue
                    else:
                        break

        print("❌ All models failed")
        return None


# For local testing
if __name__ == "__main__":
    brain = ContentBrain()
    output = brain.generate_script()
    if output:
        with open("latest_script.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        print("✅ latest_script.json saved")
