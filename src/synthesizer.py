import asyncio
import json
from pathlib import Path
from typing import Any

import edge_tts
from pydub import AudioSegment


class SpeechSynthesisError(RuntimeError):
    """Raised when English speech generation fails."""


def prepare_text_for_speech(text: str) -> str:
    """Clean translated text so TTS speaks more naturally."""

    cleaned = " ".join(text.split())

    if not cleaned:
        return cleaned

    # Add sentence-ending punctuation if Whisper misses it.
    if cleaned[-1] not in ".!?":
        cleaned += "."

    return cleaned


async def generate_speech_file(
    text: str,
    output_path: Path,
    voice: str,
    rate: str = "-5%",
    pitch: str = "-2Hz",
    volume: str = "+0%",
) -> None:
    """Generate one natural-sounding English speech segment."""

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    cleaned_text = prepare_text_for_speech(text)

    if not cleaned_text:
        raise SpeechSynthesisError(
            "Cannot generate speech from empty text."
        )

    communication = edge_tts.Communicate(
        text=cleaned_text,
        voice=voice,
        rate=rate,
        pitch=pitch,
        volume=volume,
    )

    await communication.save(str(output_path))


def change_audio_speed(
    audio: AudioSegment,
    speed_factor: float,
) -> AudioSegment:
    """
    Change the audio speed.

    A value greater than 1 makes the audio faster.
    A value below 1 makes the audio slower.
    """

    if speed_factor <= 0:
        return audio

    altered_frame_rate = int(
        audio.frame_rate * speed_factor
    )

    changed_audio = audio._spawn(
        audio.raw_data,
        overrides={
            "frame_rate": altered_frame_rate,
        },
    )

    return changed_audio.set_frame_rate(
        audio.frame_rate
    )


def fit_audio_to_duration(
    audio: AudioSegment,
    target_duration_ms: int,
) -> AudioSegment:
    """
    Fit speech close to its original timestamp while
    avoiding extreme speed changes.
    """

    if target_duration_ms <= 0:
        return audio

    current_duration_ms = len(audio)

    if current_duration_ms == 0:
        return AudioSegment.silent(
            duration=target_duration_ms
        )

    speed_factor = (
        current_duration_ms / target_duration_ms
    )

    # Restrict speed adjustment to keep the voice natural.
    speed_factor = max(
        0.90,
        min(speed_factor, 1.18),
    )

    adjusted_audio = change_audio_speed(
        audio,
        speed_factor,
    )

    # Do not cut the final words if speech is slightly longer.
    if len(adjusted_audio) >= target_duration_ms:
        return adjusted_audio

    silence_needed = (
        target_duration_ms - len(adjusted_audio)
    )

    return adjusted_audio + AudioSegment.silent(
        duration=silence_needed
    )


def load_translation(
    transcript_path: Path,
) -> dict[str, Any]:
    """Load translated transcript data from JSON."""

    if not transcript_path.exists():
        raise FileNotFoundError(
            f"Transcript file was not found: "
            f"{transcript_path}"
        )

    with transcript_path.open(
        "r",
        encoding="utf-8",
    ) as transcript_file:
        return json.load(transcript_file)


async def create_dubbed_audio_async(
    transcript_path: Path,
    output_path: Path,
    segments_directory: Path,
    video_duration_seconds: float,
    voice: str = "en-IN-NeerjaNeural",
) -> Path:
    """
    Convert translated English segments into one complete
    dubbed audio track.
    """

    translation_data = load_translation(
        transcript_path
    )

    segments = translation_data.get(
        "segments",
        [],
    )

    if not segments:
        raise SpeechSynthesisError(
            "No translated speech segments were found."
        )

    segments_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    total_duration_ms = int(
        video_duration_seconds * 1000
    )

    dubbed_timeline = (
    AudioSegment.silent(
        duration=total_duration_ms,
        frame_rate=48000,
    )
    .set_channels(2)
    )
    previous_end_ms = 0
    for index, segment in enumerate(
        segments,
        start=1,
    ):
        segment_text = segment.get(
            "text",
            "",
        ).strip()

        if not segment_text:
            continue

        original_start_ms = int(
            float(segment.get("start", 0)) * 1000
        )

        original_end_ms = int(
            float(
                segment.get(
                    "end",
                    segment.get("start", 0),
                )
            ) * 1000
        )

        # Get the next segment's starting time.
        if index < len(segments):
            next_start_ms = int(
                float(
                    segments[index].get(
                        "start",
                        original_end_ms / 1000,
                    )
                ) * 1000
            )
        else:
            next_start_ms = total_duration_ms

        # Never begin before the previous speech has ended.
        start_ms = max(
            original_start_ms,
            previous_end_ms + 80,
        )

        # Leave a small gap before the next sentence.
        available_end_ms = min(
            next_start_ms - 80,
            total_duration_ms,
        )

        target_duration_ms = max(
            available_end_ms - start_ms,
            300,
        )

        segment_path = (
            segments_directory
            / f"segment_{index:04d}.mp3"
        )

        print(
            f"      Generating segment "
            f"{index}/{len(segments)}: "
            f"{segment_text}"
        )

        await generate_speech_file(
            text=segment_text,
            output_path=segment_path,
            voice=voice,
        )

        generated_audio = AudioSegment.from_file(
            segment_path
        )

        adjusted_audio = fit_audio_to_duration(
            generated_audio,
            target_duration_ms,
        )

        # Ensure speech does not enter the next segment.
        if len(adjusted_audio) > target_duration_ms:
            adjusted_audio = adjusted_audio[
                :target_duration_ms
            ]

        fade_out_duration = min(
            80,
            max(len(adjusted_audio) // 4, 1),
        )

        adjusted_audio = adjusted_audio.fade_in(
            40
        ).fade_out(
            fade_out_duration
        )

        # Increase volume slightly and create consistent audio.
        adjusted_audio = (
            adjusted_audio
            .set_channels(2)
            .set_frame_rate(48000)
            .apply_gain(3)
        )

        dubbed_timeline = dubbed_timeline.overlay(
            adjusted_audio,
            position=start_ms,
        )

        previous_end_ms = start_ms + len(
            adjusted_audio
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dubbed_timeline = (
    dubbed_timeline
    .set_channels(2)
    .set_frame_rate(48000)
    )
    dubbed_timeline.export(
        output_path,
        format="wav",
        parameters=[
            "-ac",
            "2",
            "-ar",
            "48000",
            ],
    )

    

    if not output_path.exists():
        raise SpeechSynthesisError(
            "The dubbed audio file was not created."
        )

    return output_path


def create_dubbed_audio(
    transcript_path: Path,
    output_path: Path,
    segments_directory: Path,
    video_duration_seconds: float,
    voice: str = "en-IN-NeerjaNeural",
) -> Path:
    """Run asynchronous speech generation synchronously."""

    try:
        return asyncio.run(
            create_dubbed_audio_async(
                transcript_path=transcript_path,
                output_path=output_path,
                segments_directory=segments_directory,
                video_duration_seconds=video_duration_seconds,
                voice=voice,
            )
        )

    except Exception as error:
        raise SpeechSynthesisError(
            f"Speech generation failed: {error}"
        ) from error