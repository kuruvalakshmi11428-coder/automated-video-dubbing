import argparse
import shutil
import sys
import time
from pathlib import Path

from rich.console import Console

from src.audio_processor import extract_audio
from src.downloader import download_video
from src.synthesizer import create_dubbed_audio
from src.transcriber import translate_audio_to_english
from src.video_processor import replace_video_audio


console = Console()


def check_required_programs() -> None:
    """Verify that FFmpeg is installed."""

    missing = [
        program
        for program in ("ffmpeg", "ffprobe")
        if shutil.which(program) is None
    ]

    if missing:
        names = ", ".join(missing)

        raise RuntimeError(
            f"Missing required program(s): {names}. "
            "Install FFmpeg using: brew install ffmpeg"
        )


def parse_arguments() -> argparse.Namespace:
    """Read command-line arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Download a YouTube video and create "
            "an English-dubbed audio track."
        )
    )

    parser.add_argument(
        "url",
        help="YouTube video URL",
    )

    parser.add_argument(
        "--model",
        default="small",
        choices=[
            "tiny",
            "base",
            "small",
            "medium",
            "large-v3",
        ],
        help="Whisper model size. Default: small",
    )

    parser.add_argument(
        "--voice",
        default="en-IN-NeerjaNeural",
        help=(
            "English edge-tts voice. "
            "Default: en-IN-NeerjaNeural"
        ),
    )

    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    project_directory = Path(
        __file__
    ).resolve().parent

    temp_directory = (
        project_directory / "temp"
    )

    transcript_directory = (
        project_directory / "transcripts"
    )

    output_directory = (
        project_directory / "output"
    )

    segment_directory = (
        temp_directory / "tts_segments"
    )

    audio_path = (
        temp_directory / "source_audio.wav"
    )

    transcript_path = (
        transcript_directory
        / "english_translation.json"
    )

    dubbed_audio_path = (
        output_directory
        / "english_dubbed_audio.wav"
    )
    final_video_path = (
        output_directory
        / "final_english_dubbed_video.mp4"
    )

    start_time = time.perf_counter()

    try:
        check_required_programs()

        console.print(
            "\n[bold]"
            "Automated Video Dubbing System"
            "[/bold]"
        )

        console.print(
            "\n[bold cyan][1/5][/bold cyan] "
            "Downloading source video..."
        )

        video_path, metadata = download_video(
            args.url,
            temp_directory,
        )

        title = metadata.get(
            "title",
            "Unknown title",
        )

        duration = float(
            metadata.get("duration", 0)
        )

        if duration <= 0:
            raise RuntimeError(
                "Unable to determine video duration."
            )

        console.print(
            f"      Title: {title}"
        )

        console.print(
            f"      Duration: {duration:.2f} seconds"
        )

        console.print(
            f"      Video saved: {video_path}"
        )

        console.print(
            "\n[bold cyan][2/5][/bold cyan] "
            "Extracting source audio..."
        )

        extract_audio(
            video_path,
            audio_path,
        )

        console.print(
            f"      Audio saved: {audio_path}"
        )

        console.print(
            "\n[bold cyan][3/5][/bold cyan] "
            "Translating speech into English..."
        )

        translation_result = (
            translate_audio_to_english(
                audio_path=audio_path,
                transcript_path=transcript_path,
                model_size=args.model,
            )
        )

        console.print(
            f"\n      Detected language: "
            f"{translation_result['detected_language']}"
        )

        console.print(
            f"      Segments: "
            f"{translation_result['segment_count']}"
        )

        console.print(
            f"      Translation saved: "
            f"{transcript_path}"
        )

        console.print(
            "\n[bold cyan][4/5][/bold cyan] "
            "Generating English dubbed audio..."
        )

        create_dubbed_audio(
            transcript_path=transcript_path,
            output_path=dubbed_audio_path,
            segments_directory=segment_directory,
            video_duration_seconds=duration,
            voice=args.voice,
        )
        console.print(
            "\n[bold cyan][5/5][/bold cyan] "
            "Creating final English-dubbed video..."
        )

        replace_video_audio(
            video_path=video_path,
            dubbed_audio_path=dubbed_audio_path,
            output_path=final_video_path,
        )
        console.print(
            f"      Final video saved: {final_video_path}"
            )

        elapsed_time = (
            time.perf_counter() - start_time
        )

        console.print(
            f"\n      Dubbed audio saved: "
            f"{dubbed_audio_path}"
        )

        console.print(
            f"      Processing time: "
            f"{elapsed_time:.2f} seconds"
        )

        console.print(
            "\n[bold green]"
            "English dubbed audio created successfully."
            "[/bold green]"
        )

        return 0

    except KeyboardInterrupt:
        console.print(
            "\n[yellow]"
            "Process cancelled."
            "[/yellow]"
        )

        return 130

    except Exception as error:
        console.print(
            f"\n[bold red]Error:[/bold red] "
            f"{error}"
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())