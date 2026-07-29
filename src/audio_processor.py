import subprocess
from pathlib import Path


class AudioProcessingError(RuntimeError):
    """Raised when FFmpeg cannot process an audio file."""


def run_command(command: list[str]) -> None:
    """Run a command and raise a readable error when it fails."""
    try:
        subprocess.run(
            command,
            check=True,
            text=True,
            capture_output=True,
        )
    except FileNotFoundError as error:
        raise AudioProcessingError(
            "FFmpeg was not found. Install it using: brew install ffmpeg"
        ) from error
    except subprocess.CalledProcessError as error:
        message = error.stderr.strip() if error.stderr else str(error)
        raise AudioProcessingError(message) from error


def extract_audio(video_path: Path, output_path: Path) -> Path:
    """
    Extract mono, 16 kHz WAV audio for speech recognition.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(output_path),
    ]

    run_command(command)

    if not output_path.exists():
        raise AudioProcessingError("The extracted audio file was not created.")

    return output_path