import speech_recognition as sr
from groq import Groq
import os
import tempfile
import array
import math
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MIC_INDEX = 9            # your working mic number
ENERGY_THRESHOLD = 200
MIN_VOLUME = 100
LANGUAGE = None          # None = auto-detect Hindi/English. Or force "en" / "hi".
PROMPT_HINT = ""         # optional: names/words it keeps mishearing, e.g. "Jarvis, Rahul."

HALLUCINATIONS = {
    "thank you.", "thank you", "thanks for watching.", "thanks for watching!",
    "you", "you.", "thank you for watching.", "thank you for watching!",
    "धन्यवाद", "धन्यवाद।", "शुक्रिया", "सब्सक्राइब करें",
}


def get_volume(frame_data: bytes) -> float:
    samples = array.array("h", frame_data)
    if not samples:
        return 0
    return math.sqrt(sum(s * s for s in samples) / len(samples))


def field(seg, key, default):
    if isinstance(seg, dict):
        return seg.get(key, default)
    return getattr(seg, key, default)


def listen():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = False
    recognizer.energy_threshold = ENERGY_THRESHOLD
    recognizer.pause_threshold = 0.8

    mic = sr.Microphone(device_index=MIC_INDEX)
    with mic as source:
        print(f"Listening... (threshold: {ENERGY_THRESHOLD}, mic: {MIC_INDEX})")
        try:
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            return ""

    wav_data = audio.get_wav_data()
    with open("last_recording.wav", "wb") as f:
        f.write(wav_data)

    volume = get_volume(audio.frame_data)
    print(f"(volume: {int(volume)})")
    if volume < MIN_VOLUME:
        print("Too quiet, ignoring.")
        return ""

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(wav_data)
        temp_path = f.name

    text = ""
    try:
        kwargs = dict(
            model="whisper-large-v3-turbo",
            temperature=0.0,
            response_format="verbose_json",
        )
        if LANGUAGE:
            kwargs["language"] = LANGUAGE
        if PROMPT_HINT:
            kwargs["prompt"] = PROMPT_HINT

        with open(temp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(file=audio_file, **kwargs)

        segments = getattr(transcription, "segments", None) or []
        if segments:
            real = [
                s for s in segments
                if field(s, "no_speech_prob", 0) < 0.5
                and field(s, "avg_logprob", 0) > -1.0
            ]
            text = " ".join(field(s, "text", "") for s in real).strip()
        else:
            text = transcription.text.strip()
    except Exception as e:
        print(f"Transcription error: {e}")
    finally:
        os.remove(temp_path)

    if not any(c.isalnum() for c in text):
        text = ""

    if text.lower() in HALLUCINATIONS:
        print(f"Ignored likely false transcription: {text}")
        return ""

    if text:
        print(f"You said: {text}")
        return text

    print("Sorry, I didn't catch that.")
    return ""