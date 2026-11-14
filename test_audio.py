import speech_recognition as sr

for i, name in enumerate(sr.Microphone.list_microphone_names()):
    try:
        with sr.Microphone(device_index=i) as source:
            r = sr.Recognizer()
            print(f"SPEAK NOW -> {i}: {name}")
            audio = r.record(source, duration=3)
            with open(f"rec_{i}.wav", "wb") as f:
                f.write(audio.get_wav_data())
    except Exception:
        pass

print("Done. Play the rec_*.wav files in your jarvis folder.")