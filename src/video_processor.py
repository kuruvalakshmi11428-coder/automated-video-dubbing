import subprocess
from pathlib import Path


class VideoProcessingError(RuntimeError):
    """Raised when FFmpeg cannot create the final video."""


def replace_video_audio(
    video_path: Path,
    dubbed_audio_path: Path,
    output_path: Path,
) -> Path:
    """Replace original audio with a verified English AAC track."""

    if not video_path.exists():
        raise FileNotFoundError(
            f"Source video was not found: {video_path}"
        )

    if not dubbed_audio_path.exists():
        raise FileNotFoundError(
            f"Dubbed audio was not found: {dubbed_audio_path}"
        )

    if dubbed_audio_path.stat().st_size == 0:
        raise VideoProcessingError(
            "The generated dubbed audio file is empty."
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = [
    "ffmpeg",
    "-y",

    "-i",
    str(video_path),

    "-i",
    str(dubbed_audio_path),

    "-map",
    "0:v:0",

    "-map",
    "1:a:0",

    # Re-encode to a QuickTime-compatible video.
    "-c:v",
    "libx264",

    "-preset",
    "fast",

    "-crf",
    "20",

    "-pix_fmt",
    "yuv420p",

    # Encode the dubbed speech as standard AAC stereo.
    "-c:a",
    "aac",

    "-b:a",
    "192k",

    "-ar",
    "48000",

    "-ac",
    "2",

    "-metadata:s:a:0",
    "language=eng",

    "-disposition:a:0",
    "default",

    "-shortest",

    "-movflags",
    "+faststart",

    str(output_path),
    ]

    

    try:
        result = subprocess.run(
            command,
            check=True,
            text=True,
            capture_output=True,
        )

    except FileNotFoundError as error:
        raise VideoProcessingError(
            "FFmpeg is not installed."
        ) from error

    except subprocess.CalledProcessError as error:
        message = (
            error.stderr.strip()
            if error.stderr
            else str(error)
        )

        raise VideoProcessingError(
            f"Final video creation failed: {message}"
        ) from error

    if not output_path.exists():
        raise VideoProcessingError(
            "The final video was not created."
        )

    if output_path.stat().st_size == 0:
        raise VideoProcessingError(
            "The final generated video is empty."
        )

    return output_path