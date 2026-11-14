import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QFrame
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtCore import QUrl, QThread, Signal

from function import execute_function, parse_site_command, parse_play_command
from voice_output import speak
from voice_input import listen
from ai_brain import ask_ai
from memory import handle_memory_command
from hindi_commands import normalize_hindi

def route_command(command: str):
    text = normalize_hindi(command).lower()

    # 1. Memory commands: "remember ...", "forget ...", "what do you remember"
    memory_reply = handle_memory_command(command)
    if memory_reply:
        return memory_reply

    # 2. "play ... on youtube"
    q = parse_play_command(text)
    if q:
        return execute_function("play_youtube", {"query": q})

    # 3. "open github and search ...", "search ... on flipkart", "open youtube"
    parsed = parse_site_command(text)
    if parsed:
        site, query = parsed
        return execute_function("open_site", {"site": site, "query": query})

    # 4. System commands
    if "battery" in text:
        return execute_function("get_battery_status")
    elif "time" in text:
        return execute_function("get_time")
    elif "cpu" in text:
        return execute_function("get_cpu_usage")
    elif "ram" in text or "memory" in text:
        return execute_function("get_ram_usage")
    elif "screenshot" in text:
        return execute_function("take_screenshot")
    elif "open notepad" in text:
        return execute_function("open_app", {"app_name": "notepad"})
    elif "open calculator" in text:
        return execute_function("open_app", {"app_name": "calculator"})
    elif "open chrome" in text:
        return execute_function("open_app", {"app_name": "chrome"})
    elif "search" in text:
        query = text.replace("search", "").strip(" ,.")
        return execute_function("search_web", {"query": query})
    return None


class JarvisWorker(QThread):
    state_changed = Signal(str)
    user_said = Signal(str)
    jarvis_said = Signal(str)
    stopped = Signal()

    def __init__(self):
        super().__init__()
        self._running = True

    def run(self):
        while self._running:
            self.state_changed.emit("listening")
            command = listen()
            if not command:
                continue

            self.user_said.emit(command)

            if "stop" in command.lower() or "goodbye" in command.lower() or "bye" in command.lower():
                self.state_changed.emit("speaking")
                self.jarvis_said.emit("Goodbye.")
                speak("Goodbye.")
                self._running = False
                self.stopped.emit()
                break

            self.state_changed.emit("thinking")
            try:
                result = route_command(command)
            except Exception as e:
                result = f"Sorry, that command failed. {e}"

            reply = result if result is not None else ask_ai(command)

            self.jarvis_said.emit(reply)
            self.state_changed.emit("speaking")
            speak(reply)

        self.state_changed.emit("idle")

    def stop(self):
        self._running = False


class JarvisWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("J.A.R.V.I.S.")
        self.resize(1100, 680)

        qss_path = os.path.join(os.path.dirname(__file__), "gui", "style.qss")
        with open(qss_path, "r") as f:
            self.setStyleSheet(f.read())

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Left: 3D waveform panel
        self.webview = QWebEngineView()
        self.webview.settings().setAttribute(QWebEngineSettings.WebGLEnabled, True)
        self.webview.settings().setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        html_path = os.path.join(os.path.dirname(__file__), "gui", "waveform.html")
        self.webview.load(QUrl.fromLocalFile(html_path))
        layout.addWidget(self.webview, 2)

        # Right: control panel
        right_container = QFrame()
        right_container.setFixedWidth(360)
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(16, 10, 16, 16)
        right_layout.setSpacing(10)

        self.status_label = QLabel("STATUS: IDLE")
        self.status_label.setObjectName("statusLabel")
        right_layout.addWidget(self.status_label)

        self.chat_log = QTextEdit()
        self.chat_log.setObjectName("chatLog")
        self.chat_log.setReadOnly(True)
        right_layout.addWidget(self.chat_log, 1)

        self.mic_button = QPushButton("🎙  START LISTENING")
        self.mic_button.setObjectName("micButton")
        self.mic_button.clicked.connect(self.toggle_listening)
        right_layout.addWidget(self.mic_button)

        layout.addWidget(right_container)

        self.worker = None

    def toggle_listening(self):
        if self.worker is None or not self.worker.isRunning():
            self.worker = JarvisWorker()
            self.worker.state_changed.connect(self.on_state_changed)
            self.worker.user_said.connect(self.on_user_said)
            self.worker.jarvis_said.connect(self.on_jarvis_said)
            self.worker.stopped.connect(self.on_stopped)
            self.worker.start()
            self.mic_button.setText("⏹  STOP")
        else:
            self.worker.stop()
            self.worker.wait()
            self.mic_button.setText("🎙  START LISTENING")

    def on_state_changed(self, state):
        self.status_label.setText(f"STATUS: {state.upper()}")
        self.webview.page().runJavaScript(f"setJarvisState('{state}')")

    def on_user_said(self, text):
        self.chat_log.append(f"<div style='margin:6px 0;'><b style='color:#7fffd4'>You</b><br>{text}</div>")

    def on_jarvis_said(self, text):
        self.chat_log.append(f"<div style='margin:6px 0;'><b style='color:#00d4ff'>Jarvis</b><br>{text}</div>")

    def on_stopped(self):
        self.mic_button.setText("🎙  START LISTENING")

    def closeEvent(self, event):
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JarvisWindow()
    window.show()
    sys.exit(app.exec())