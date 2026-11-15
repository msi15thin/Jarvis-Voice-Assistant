import re
import urllib.request
from urllib.parse import quote_plus
import psutil
import webbrowser
import subprocess
import datetime
import pyautogui
import os

def get_battery_status():
    battery = psutil.sensors_battery()
    if battery is None:
        return "No battery detected (desktop PC?)."
    plugged = "charging" if battery.power_plugged else "not charging"
    return f"Battery is at {battery.percent}%, {plugged}."

def get_time():
    return datetime.datetime.now().strftime("The time is %I:%M %p.")

#def get_cpu_usage():
    return f"CPU usage is at {psutil.cpu_percent(interval=1)}%."

#def get_ram_usage():
    ram = psutil.virtual_memory()
    return f"RAM usage is at {ram.percent}%."

def search_web(query: str):
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Searching the web for {query}."

def open_app(app_name: str):
    allowed_apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "chrome": "chrome.exe",
    }
    app_name = app_name.lower()
    if app_name not in allowed_apps:
        return f"'{app_name}' is not in my allowed app list."
    subprocess.Popen(allowed_apps[app_name])
    return f"Opening {app_name}."
# name -> (homepage, search URL template)
SITES = {
    "github": ("https://github.com", "https://github.com/search?q={q}"),
    "youtube": ("https://www.youtube.com", "https://www.youtube.com/results?search_query={q}"),
    "google": ("https://www.google.com", "https://www.google.com/search?q={q}"),
    "wikipedia": ("https://en.wikipedia.org", "https://en.wikipedia.org/w/index.php?search={q}"),
    "amazon": ("https://www.amazon.in", "https://www.amazon.in/s?k={q}"),
    "flipkart": ("https://www.flipkart.com", "https://www.flipkart.com/search?q={q}"),
    "stack overflow": ("https://stackoverflow.com", "https://stackoverflow.com/search?q={q}"),
    "reddit": ("https://www.reddit.com", "https://www.reddit.com/search/?q={q}"),
    "gmail": ("https://mail.google.com", "https://mail.google.com/mail/u/0/#search/{q}"),
    "google maps": ("https://www.google.com/maps", "https://www.google.com/maps/search/{q}"),
    "spotify": ("https://open.spotify.com", "https://open.spotify.com/search/{q}"),
}

APP_NAMES = {"notepad", "calculator", "chrome"}


def open_site(site: str, query: str = None):
    name = site.lower().strip()
    name = name.replace(" dot com", "").replace(".com", "").strip()
    if name in ("chrome", "google chrome", "browser", "the browser"):
        name = "google"

    if name in SITES:
        home, search = SITES[name]
        if query:
            webbrowser.open(search.format(q=quote_plus(query)))
            return f"Searching {name} for {query}."
        webbrowser.open(home)
        return f"Opening {name}."

    # Unknown site: fall back to a Google search
    term = f"{site} {query}" if query else site
    webbrowser.open(f"https://www.google.com/search?q={quote_plus(term)}")
    return f"I don't have {site} saved, so I searched Google for {term}."


def parse_site_command(text: str):
    text = text.lower().strip(" .,!?")

    # "play honey singh song on youtube" -> YouTube search
    if "play" in text and "youtube" in text:
        q = text.split("play", 1)[1]
        q = re.sub(r"\s*(on|in)\s+youtube.*$", "", q).strip(" ,.")
        if q:
            return "youtube", q

    # "open github and search msi-15"
    m = re.match(r"(?:open|go to)\s+(.+?)\s*(?:,|and|then)?\s+(?:search for|search|find|look for)\s+(.+)", text)
    if m:
        return m.group(1).strip(" ,"), m.group(2).strip()

    # "search lofi music on youtube"
    m = re.match(r"(?:search for|search|find|look for)\s+(.+)\s+(?:on|in)\s+(.+)$", text)
    if m:
        return m.group(2).strip(), m.group(1).strip()

    # "open github"
    m = re.match(r"(?:open|go to)\s+(.+)$", text)
    if m and m.group(1).strip() not in APP_NAMES:
        return m.group(1).strip(), None

    return None
def take_screenshot():
    folder = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "jarvis_screenshot.png")
    pyautogui.screenshot(path)
    return f"Screenshot saved to {path}."
def play_youtube(query: str):
    url = "https://www.youtube.com/results?search_query=" + quote_plus(query)
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"},
        )
        html = urllib.request.urlopen(req, timeout=8).read().decode("utf-8", errors="ignore")
        ids = re.findall(r'"videoId":"([A-Za-z0-9_-]{11})"', html)
        if ids:
            webbrowser.open(f"https://www.youtube.com/watch?v={ids[0]}")
            return f"Playing {query} on YouTube."
    except Exception:
        pass
    webbrowser.open(url)
    return f"I couldn't find a video directly, so I opened the YouTube search for {query}."


def parse_play_command(text: str):
    """'play honey singh song on youtube' -> 'honey singh song'"""
    text = text.lower().strip(" .,!?")
    m = re.match(r"play\s+(.+)", text)
    if not m:
        return None
    q = re.sub(r"\s*(on|in)\s+(youtube|chrome).*$", "", m.group(1)).strip(" ,.")
    return q or None
FUNCTION_MAP = {
    "get_battery_status": get_battery_status,
    "get_time": get_time,
   # "get_cpu_usage": get_cpu_usage,
   # "get_ram_usage": get_ram_usage,
    "search_web": search_web,
    "open_app": open_app,
    "open_site": open_site,
    "take_screenshot": take_screenshot,
    "play_youtube": play_youtube,
}

def execute_function(name: str, args: dict = None):
    if name not in FUNCTION_MAP:
        return "I'm not allowed to do that."
    args = args or {}
    return FUNCTION_MAP[name](**args)

def execute_function(name: str, args: dict = None):
    if name not in FUNCTION_MAP:
        return "I'm not allowed to do that."
    args = args or {}
    return FUNCTION_MAP[name](**args)