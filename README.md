cat > README.md <<'EOF'
# Automated Video Dubbing System

A Python-based system that downloads a YouTube video, extracts audio, transcribes speech using Whisper, translates it into English, generates English speech using Edge TTS, and merges the dubbed audio with the original video.

## Features

- YouTube video downloading using yt-dlp
- Audio extraction using FFmpeg
- Speech transcription using Faster Whisper
- Translation into English
- English speech generation using Edge TTS
- Audio and video merging using FFmpeg
- Progress display for every stage
- Transcript saved in JSON format

## Project Structure

```text
automated-video-dubbing/
├── src/
│   ├── downloader.py
│   ├── audio_processor.py
│   ├── transcriber.py
│   ├── synthesizer.py
│   └── video_processor.py
├── output/
├── transcripts/
├── temp/
├── main.py
├── requirements.txt
└── README.mds