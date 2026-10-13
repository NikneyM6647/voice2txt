import sys
import threading

import speech_recognition as sr

from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QTextEdit, QFrame
)


STYLE = """
QMainWindow, QWidget#Central { background-color: #0f172a; }
QLabel { color: #e2e8f0; font-family: 'Segoe UI', 'Inter', sans-serif; }
QLabel#Title    { font-size: 22px; font-weight: 600; color: #f1f5f9; }
QLabel#Subtitle { font-size: 12px; color: #94a3b8; }
QLabel#StatusText { font-size: 15px; font-weight: 500; }

QFrame#Card {
    background-color: #1e293b;
    border-radius: 16px;
    border: 1px solid #334155;
}

QComboBox {
    background-color: #1e293b; color: #e2e8f0;
    border: 1px solid #334155; border-radius: 8px;
    padding: 8px 12px; font-size: 13px;
}
QComboBox:hover { border: 1px solid #475569; }
QComboBox:focus { border: 1px solid #38bdf8; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background-color: #1e293b; color: #e2e8f0;
    selection-background-color: #334155;
    border: 1px solid #334155;
}

QPushButton#Toggle {
    background-color: #22c55e; color: white;
    border: none; border-radius: 12px;
    padding: 14px; font-size: 15px; font-weight: 600;
}
QPushButton#Toggle:hover { background-color: #16a34a; }
QPushButton#Toggle[recording="true"]       { background-color: #ef4444; }
QPushButton#Toggle[recording="true"]:hover { background-color: #dc2626; }

QTextEdit#History {
    background-color: #1e293b; color: #e2e8f0;
    border: 1px solid #334155; border-radius: 12px;
    padding: 10px; font-size: 13px;
}

QPushButton#Secondary {
    background-color: transparent; color: #94a3b8;
    border: 1px solid #334155; border-radius: 8px;
    padding: 6px 12px; font-size: 12px;
}
QPushButton#Secondary:hover { color: #e2e8f0; border-color: #475569; }
"""


class Worker(QObject):
    recognized = Signal(str)
    status     = Signal(str)
    error      = Signal(str)

    def __init__(self, device_index, lang):
        super().__init__()
        self.device_index = device_index
        self.lang = lang
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def run(self):
        rec = sr.Recognizer()
        rec.energy_threshold = 300
        try:
            mic = sr.Microphone(device_index=self.device_index)
        except Exception as e:
            self.error.emit(f"Микрофон недоступен: {e}")
            return

        with mic as source:
            try:
                rec.adjust_for_ambient_noise(source, duration=0.4)
            except Exception:
                pass

            self.status.emit("Слушаю…")

            while not self._stop.is_set():
                try:
                    audio = rec.listen(source, timeout=1, phrase_time_limit=10)
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    self.error.emit(str(e))
                    break

                try:
                    text = rec.recognize_google(audio, language=self.lang)
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    self.error.emit(f"Сервис недоступен: {e}")
                    break

                if text.strip():
                    self.recognized.emit(text.strip())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voice → Text")
        self.resize(560, 680)

        self.is_recording = False
        self.worker = None
        self.worker_thread = None
        self.device_index = None
        self.lang = "ru-RU"

        self._build_ui()
        self._load_microphones()

    # ---------- UI ----------
    def _build_ui(self):
        central = QWidget()
        central.setObjectName("Central")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)

        title = QLabel("Voice → Text")
        title.setObjectName("Title")
        subtitle = QLabel("Голосовой ввод в активное окно")
        subtitle.setObjectName("Subtitle")
        root.addWidget(title)
        root.addWidget(subtitle)

        mic_label = QLabel("Микрофон")
        mic_label.setObjectName("Subtitle")
        self.mic_combo = QComboBox()
        self.mic_combo.currentIndexChanged.connect(self._on_mic_changed)
        root.addWidget(mic_label)
        root.addWidget(self.mic_combo)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 22, 24, 22)
        card_layout.setSpacing(10)

        self.status_dot = QLabel("●")
        self.status_dot.setAlignment(Qt.AlignCenter)
        f = QFont(); f.setPointSize(36)
        self.status_dot.setFont(f)
        self.status_dot.setStyleSheet("color: #64748b;")

        self.status_text = QLabel("Готово")
        self.status_text.setObjectName("StatusText")
        self.status_text.setAlignment(Qt.AlignCenter)

        self.hotkey_hint = QLabel("Нажмите кнопку ниже, чтобы начать")
        self.hotkey_hint.setObjectName("Subtitle")
        self.hotkey_hint.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(self.status_dot)
        card_layout.addWidget(self.status_text)
        card_layout.addWidget(self.hotkey_hint)
        root.addWidget(card)

        self.toggle_btn = QPushButton("Начать запись")
        self.toggle_btn.setObjectName("Toggle")
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_recording)
        root.addWidget(self.toggle_btn)

        hdr = QHBoxLayout()
        hist_label = QLabel("История")
        hist_label.setObjectName("Subtitle")
        clear_btn = QPushButton("Очистить")
        clear_btn.setObjectName("Secondary")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.clicked.connect(lambda: self.history.clear())
        hdr.addWidget(hist_label)
        hdr.addStretch()
        hdr.addWidget(clear_btn)
        root.addLayout(hdr)

        self.history = QTextEdit()
        self.history.setObjectName("History")
        self.history.setReadOnly(True)
        root.addWidget(self.history, 1)

    # ---------- Микрофоны ----------
    @staticmethod
    def _fix_encoding(name):
        """UTF-8, ошибочно прочитанный как CP1251 → правильная строка."""
        suspicious = "ЂЃ‚ѓ„…†‡€‰Љ‹ЊЌЋЏђ‘’“”•–—™љ›њќћџ"
        if not any(c in suspicious for c in name):
            return name
        try:
            return name.encode("cp1251").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return name

    def _load_microphones(self):
        try:
            import pyaudio
        except ImportError:
            self._append_history("[ошибка] PyAudio не установлен")
            return

        devices = []
        seen = set()
        p = pyaudio.PyAudio()
        try:
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                if info.get("maxInputChannels", 0) <= 0:
                    continue
                name = self._fix_encoding(info.get("name", f"Device {i}"))
                key = name.strip().lower()
                if key in seen:
                    continue
                seen.add(key)
                devices.append((i, name))
        finally:
            p.terminate()

        self.mic_combo.blockSignals(True)
        self.mic_combo.clear()

        target_pos = 0
        for pos, (dev_id, name) in enumerate(devices):
            self.mic_combo.addItem(name, dev_id)
            if "USB MIC PRO" in name.upper():
                target_pos = pos

        if devices:
            self.mic_combo.setCurrentIndex(target_pos)
            self.device_index = self.mic_combo.itemData(target_pos)
            self._append_history(f"Выбран микрофон: {devices[target_pos][1]}")
        else:
            self.device_index = None
            self._append_history("[!] Микрофоны не найдены")

        self.mic_combo.blockSignals(False)

    def _on_mic_changed(self, idx):
        if idx < 0:
            return
        self.device_index = self.mic_combo.itemData(idx)
        self._append_history(f"Микрофон: {self.mic_combo.itemText(idx)}")
        if self.is_recording:
            self._stop_recording()
            self._start_recording()

    # ---------- Управление ----------
    def toggle_recording(self):
        if self.device_index is None:
            self._append_history("[!] Микрофон не выбран")
            return
        if not self.is_recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        self.is_recording = True
        self.worker = Worker(self.device_index, self.lang)
        self.worker.recognized.connect(self._on_recognized)
        self.worker.status.connect(self.status_text.setText)
        self.worker.error.connect(self._on_error)
        self.worker_thread = threading.Thread(target=self.worker.run, daemon=True)
        self.worker_thread.start()

        self.toggle_btn.setText("Остановить запись")
        self.toggle_btn.setProperty("recording", True)
        self._repolish(self.toggle_btn)

        self.status_dot.setStyleSheet("color: #ef4444;")
        self.status_text.setText("Запись…")
        self.hotkey_hint.setText("Идёт распознавание речи")

    def _stop_recording(self):
        self.is_recording = False
        if self.worker:
            self.worker.stop()
            self.worker = None

        self.toggle_btn.setText("Начать запись")
        self.toggle_btn.setProperty("recording", False)
        self._repolish(self.toggle_btn)

        self.status_dot.setStyleSheet("color: #64748b;")
        self.status_text.setText("Готово")
        self.hotkey_hint.setText("Нажмите кнопку ниже, чтобы начать")

    @staticmethod
    def _repolish(w):
        w.style().unpolish(w)
        w.style().polish(w)

    # ---------- Обработчики ----------
    def _on_recognized(self, text):
        self._append_history(text)
        try:
            from keyboard import write as kb_write
            kb_write(text + " ")
        except Exception as e:
            self._append_history(f"[ошибка ввода] {e}")

    def _on_error(self, text):
        self._append_history(f"[!] {text}")
        self._stop_recording()

    def _append_history(self, text):
        self.history.append(text)
        sb = self.history.verticalScrollBar()
        sb.setValue(sb.maximum())

    def closeEvent(self, event):
        self._stop_recording()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()