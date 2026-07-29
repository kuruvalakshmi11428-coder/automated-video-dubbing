import json
from pathlib import Path
from typing import Any

from faster_whisper import WhisperModel


class TranscriptionError(RuntimeError):
    """Raised when audio transcription or translation fails."""


def translate_audio_to_english(
    audio_path: Path,
    transcript_path: Path,
    model_size: str = "small",
) -> dict[str, Any]:
    """
    Detect the spoken language and translate speech into English.

    The result includes:
    - Detected language
    - Language probability
    - Timestamped English segments
    - Complete English text
    """

    if not audio_path.exists():
        raise FileNotFoundError(
            f"Audio file was not found: {audio_path}"
        )

    transcript_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        print(f"      Loading Whisper model: {model_size}")

        model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",
        )

        segments_generator, information = model.transcribe(
            str(audio_path),
            task="translate",
            beam_size=5,
            vad_filter=True,
        )

        translated_segments: list[dict[str, Any]] = []
        complete_text: list[str] = []

        # faster-whisper returns a generator.
        # We must loop through it to perform transcription.
        for index, segment in enumerate(segments_generator, start=1):
            text = segment.text.strip()

            if not text:
                continue

            segment_data = {
                "id": index,
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "duration": round(segment.end - segment.start, 2),
                "text": text,
            }

            translated_segments.append(segment_data)
            complete_text.append(text)

            print(
                f"      [{segment.start:.2f}s - "
                f"{segment.end:.2f}s] {text}"
            )

        result: dict[str, Any] = {
            "detected_language": information.language,
            "language_probability": round(
                information.language_probability,
                4,
            ),
            "target_language": "English",
            "segment_count": len(translated_segments),
            "segments": translated_segments,
            "complete_text": " ".join(complete_text),
        }

        with transcript_path.open(
            "w",
            encoding="utf-8",
        ) as transcript_file:
            json.dump(
                result,
                transcript_file,
                ensure_ascii=False,
                indent=4,
            )

        return result

    except Exception as error:
        raise TranscriptionError(
            f"Transcription failed: {error}"
        ) from error