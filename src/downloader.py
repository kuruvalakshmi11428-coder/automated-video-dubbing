from pathlib import Path
from typing import Any

import yt_dlp


class VideoDownloadError(RuntimeError):
    """Raised when a video cannot be downloaded."""


def download_video(url: str, output_directory: Path) -> tuple[Path, dict[str, Any]]:
    """
    Download a YouTube video and return its file path and metadata.

    The output is converted or merged into an MP4 container whenever possible.
    """
    output_directory.mkdir(parents=True, exist_ok=True)

    output_template = str(output_directory / "source_video.%(ext)s")

    options: dict[str, Any] = {
        "format": "bestvideo*+bestaudio/best",
        "outtmpl": output_template,
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": False,
        "no_warnings": False,
    }

    try:
        with yt_dlp.YoutubeDL(options) as downloader:
            information = downloader.extract_info(url, download=True)

            requested_downloads = information.get("requested_downloads") or []
            if requested_downloads:
                downloaded_path = requested_downloads[0].get("filepath")
                if downloaded_path:
                    path = Path(downloaded_path)
                    if path.exists():
                        return path, information

            prepared_path = Path(downloader.prepare_filename(information))

            possible_paths = [
                prepared_path,
                prepared_path.with_suffix(".mp4"),
                output_directory / "source_video.mp4",
            ]

            for path in possible_paths:
                if path.exists():
                    return path, information

    except Exception as error:
        raise VideoDownloadError(
            f"Unable to download the video: {error}"
        ) from error

    raise VideoDownloadError(
        "The download completed, but the resulting video file was not found."
    )