# Voice → Text

Компактное десктопное приложение для голосового ввода: нажимаете кнопку, говорите — текст сам печатается в активном окне.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PySide6](https://img.shields.io/badge/UI-PySide6-41cd52)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Возможности

- 🎙 Голосовой ввод в любое активное окно (редактор, браузер, мессенджер)
- 🌙 Тёмная минималистичная тема
- 🔍 Автоматический поиск микрофона
- 🧹 Отсеивание выходных устройств и дублей
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

| PySide6 | Графический интерфейс |
| SpeechRecognition | Обёртка над Google Speech API |
| PyAudio | Запись с микрофона |
| keyboard | Эмуляция нажатий клавиш |


## Лицензия

MIT — используйте, изменяйте и распространяйте свободно.
