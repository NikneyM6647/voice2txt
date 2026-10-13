# Voice → Text

Компактное десктопное приложение для голосового ввода: нажимаете кнопку, говорите — текст сам печатается в активном окне.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PySide6](https://img.shields.io/badge/UI-PySide6-41cd52)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Возможности

- 🎙 Голосовой ввод в любое активное окно (редактор, браузер, мессенджер)
- 🌙 Тёмная минималистичная тема
- 🔍 Автоматический поиск микрофона (приоритет — `USB MIC PRO`)
- 🧹 Отсеивание выходных устройств и дублей
- 🛠 Исправление «кракозябр» в именах устройств Windows
- 📜 История распознанных фраз с кнопкой очистки
- 🖱 Управление одной кнопкой — никаких хоткеев

---

## Требования

- Windows 10/11
- Python 3.10 или новее
- Интернет (используется Google Speech Recognition)

---

## Установка

```powershell
python -m pip install PySide6 SpeechRecognition pyaudio keyboard
```

Если `pyaudio` не ставится, есть два обходных пути:

```powershell
python -m pip install pipwin
python -m pipwin install pyaudio
```

Либо скачайте готовое колесо с https://pypi.org/project/PyAudio/#files
(файл вида `PyAudio‑0.2.14‑cp312‑cp312‑win_amd64.whl`) и установите:

```powershell
python -m pip install "путь\к\PyAudio-0.2.14-cp312-cp312-win_amd64.whl"
```

---

## Запуск

```powershell
python voice2textintextboxactiveprogramm.py
```

1. Выберите микрофон в выпадающем списке (нужный подставится автоматически).
2. Нажмите **Начать запись**.
3. Говорите — текст появится в окне, которое было активным.
4. Нажмите **Остановить запись** для остановки.

---

## Зависимости

| Пакет | Назначение |
|---|---|
| PySide6 | Графический интерфейс |
| SpeechRecognition | Обёртка над Google Speech API |
| PyAudio | Запись с микрофона |
| keyboard | Эмуляция нажатий клавиш |

---

## Известные ограничения

- **Только Windows.** На Linux/macOS `keyboard.write` может работать нестабильно с кириллицей.
- **Нужен интернет.** `recognize_google` обращается к серверам Google, аудио уходит наружу.
- **Лимиты Google API.** При частых запросах возможны задержки или отказ `RequestError`.
- **Ввод идёт в активное окно.** Если переключиться во время распознавания, текст уйдёт не туда.

---

## Структура проекта

```
voice2textintextboxactiveprogramm.py   # основной файл
README.md                              # этот файл
```

---

## Лицензия

MIT — используйте, изменяйте и распространяйте свободно.
