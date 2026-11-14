import asyncio
import edge_tts
import pyttsx3
import os
import re
import uuid
import pygame
import keyboard

VOICE_EN = "en-US-ChristopherNeural"
VOICE_HI = "hi-IN-MadhurNeural"
PITCH = "-6Hz"
RATE = "-8%"


def is_hindi(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    devanagari = len(re.findall(r"[\u0900-\u097F]", text))
    return devanagari / len(letters) > 0.3


async def _generate_edge(text: str, filename: str, voice: str):
    communicate = edge_tts.Communicate(text, voice, pitch=PITCH, rate=RATE)
    await communicate.save(filename)


def speak_offline(text: str):
    engine = pyttsx3.init()
    engine.setProperty("rate", 175)
    engine.say(text)
    engine.runAndWait()


def speak(text: str):
    print(f"Jarvis: {text}")
    voice = VOICE_HI if is_hindi(text) else VOICE_EN
    filename = f"jarvis_voice_{uuid.uuid4().hex}.mp3"
    try:
        asyncio.run(_generate_edge(text, filename, voice))

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        print("(Press ESC to interrupt)")
        while pygame.mixer.music.get_busy():
            if keyboard.is_pressed("esc"):
                pygame.mixer.music.stop()
                print("Interrupted.")
                break
            pygame.time.wait(100)
        pygame.mixer.music.unload()
        os.remove(filename)
    except Exception as e:
        print(f"[edge-tts failed, using offline voice] {e}")
        speak_offline(text)