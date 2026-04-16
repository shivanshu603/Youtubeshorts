import os
import asyncio
import edge_tts
from mutagen.mp3 import MP3

class AudioEngine:
    def __init__(self):
        # Best Natural Indian Male Hindi Voice
        self.voice = "hi-IN-MadhurNeural"      # ← Yeh sabse real lagta hai
        self.output_dir = os.path.join(os.getcwd(), "assets", "audio_clips")
        os.makedirs(self.output_dir, exist_ok=True)

    async def generate_audio(self, text, output_filename, retries=3):
        """
        Generates MP3 with natural sounding Hindi Male voice
        """
        output_path = os.path.join(self.output_dir, output_filename)
       
        for attempt in range(retries):
            try:
                # Natural settings for less robotic sound
                communicate = edge_tts.Communicate(
                    text, 
                    self.voice,
                    rate="+0%",      # Normal speed (natural feel)
                    pitch="-2Hz",    # Thoda low pitch for more masculine feel
                    volume="+0%"
                )
                
                await communicate.save(output_path)
                print(f"   ✅ Audio generated with hi-IN-MadhurNeural")
                return output_path
           
            except Exception as e:
                print(f" ⚠️ Audio Error (Attempt {attempt+1}/{retries}): {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    print(" ❌ Failed to generate audio after max retries.")
                    raise e

    def get_audio_duration(self, file_path):
        try:
            audio = MP3(file_path)
            return audio.info.length
        except Exception as e:
            print(f"❌ Error reading audio length: {e}")
            return 0.0

    async def process_script(self, script_data):
        print(f"🎙️ Starting Audio Generation for {len(script_data)} scenes... (Hindi Male Voice)")

        for scene in script_data:
            scene_id = scene['id']
            text = scene['text']
            filename = f"voice_{scene_id}.mp3"
           
            try:
                file_path = await self.generate_audio(text, filename)
                duration = self.get_audio_duration(file_path)
               
                scene['audio_path'] = file_path
                scene['duration'] = duration
               
                print(f"   ✅ Scene {scene_id}: {duration:.2f}s generated (Natural Male Voice)")
                
                await asyncio.sleep(1)   # Polite delay for API
               
            except Exception as e:
                print(f"   ❌ Skipping Scene {scene_id} due to audio error.")
                continue
           
        return script_data
