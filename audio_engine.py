import os
import asyncio
import edge_tts
import hashlib

VOICE_MAP = {
    "English": "en-US-ChristopherNeural",
    "Hindi": "hi-IN-MadhurNeural",
    "Hinglish": "en-IN-PrabhatNeural"
}

CACHE_DIR = "generated_audio"
os.makedirs(CACHE_DIR, exist_ok=True)

async def _save_audio(text: str, voice: str, path: str):
    comm = edge_tts.Communicate(text=text, voice=voice)
    await comm.save(path)

def generate_scene_audio(text: str, language: str = "Hinglish") -> str:
    voice = VOICE_MAP.get(language, "en-IN-PrabhatNeural")
    filename = hashlib.md5((text + voice).encode()).hexdigest() + ".mp3"
    filepath = os.path.join(CACHE_DIR, filename)

    if not os.path.exists(filepath):
        asyncio.run(_save_audio(text, voice, filepath))
        
    return filepath