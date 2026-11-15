from function import execute_function
from voice_output import speak
from voice_input import listen
from ai_brain import ask_ai


def route_command(command: str):
    text = command.lower()

    if "battery" in text:
        return execute_function("get_battery_status")
    elif "time" in text:
        return execute_function("get_time")
   # elif "cpu" in text:
   #     return execute_function("get_cpu_usage")
   # elif "ram" in text or "memory" in text:
   #     return execute_function("get_ram_usage")
    elif "screenshot" in text:
        return execute_function("take_screenshot")
    elif "open notepad" in text:
        return execute_function("open_app", {"app_name": "notepad"})
    elif "open calculator" in text:
        return execute_function("open_app", {"app_name": "calculator"})
    elif "open chrome" in text:
        return execute_function("open_app", {"app_name": "chrome"})
    elif "search" in text:
        query = text.replace("search", "").strip()
        return execute_function("search_web", {"query": query})
    else:
        return None  # not a known command — send to AI instead


speak("Hello, I am Jarvis. I'm listening.")

while True:
    command = listen()
    if not command:
        continue

    if "stop" in command.lower() or "goodbye" in command.lower() or "bye" in command.lower():
        speak("Goodbye.")
        break

    result = route_command(command)

    if result is not None:
        speak(result)
    else:
        reply = ask_ai(command)
        speak(reply)