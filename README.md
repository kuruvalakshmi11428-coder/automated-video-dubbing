<img width="1470" height="956" alt="Screenshot 2026-07-29 at 10 51 05 PM" src="https://github.com/user-attachments/assets/09b5361a-cc6c-4d85-afc6-382c5036957e" /># 🎬 Automated Video Dubbing System

An AI-powered Python application that automatically downloads a YouTube video, transcribes the speech using Whisper, translates it into English, generates natural English voice using Edge TTS, and merges the dubbed audio back into the original video using FFmpeg.

---

## 🚀 Features

- 🎥 Download YouTube videos
- 🔊 Extract audio from video
- 📝 Speech-to-Text using Whisper
- 🌍 Translate speech into English
- 🗣 Generate English voice using Edge TTS
- 🎬 Merge dubbed audio with original video
- 💾 Save translated transcript as JSON
- 📊 Clean and modular Python project structure

---

## 🛠 Technologies Used

- Python 3
- Whisper
- Edge TTS
- FFmpeg
- yt-dlp
- Pydub
- JSON

---

## 📂 Project Structure

```
automated-video-dubbing/
│
├── src/
│   ├── downloader.py
│   ├── audio_processor.py
│   ├── transcriber.py
│   ├── synthesizer.py
│   ├── video_processor.py
│   └── utils.py
│
├── output/
│   └── Automated_Video_Dubbing_Final.mp4
│
├── transcripts/
│   └── english_translation.json
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚙ Installation

Clone the repository:

```bash
git clone https://github.com/kuruvalakshmi11428-coder/automated-video-dubbing.git
cd automated-video-dubbing
```

Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install FFmpeg (macOS):

```bash
brew install ffmpeg
```

---

## ▶ Usage

Run the project:

```bash
python main.py
```

Enter a YouTube URL when prompted.

Example:

```
https://youtu.be/sdxLqbAObF0
```

---

## 🎥 Demo Video

Watch the demo here:

https://youtu.be/sdxLqbAObF0

---
## 📸 Project Demo

![Project Demo](<img width="1470" height="956" alt="demo" src="https://github.com/user-attachments/assets/0a626cac-d29e-45ca-8ba2-cb7aba08ad90" />)
<img width="1470" height="956" alt="Screenshot 2026-07-29 at 10 51 05 PM" src="https://github.com/user-attachments/assets/37f91458-4cba-4c10-921d-9387de9c1378" />




## 📄 Output

The project generates:

- Final dubbed English video
- English transcript in JSON format

Example output:

```
output/
└── Automated_Video_Dubbing_Final.mp4
```

---

## 🔮 Future Improvements

- Multiple language dubbing
- Voice cloning
- Speaker diarization
- Lip-sync improvement
- Web interface using Streamlit
- Batch video processing

---

## 👩‍💻 Author

**K. Lakshmi**

- GitHub: https://github.com/kuruvalakshmi11428-coder

---

## ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.
