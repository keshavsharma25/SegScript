from youtube_transcript_api._api import YouTubeTranscriptApi
from youtube_transcript_api._transcripts import FetchedTranscript
from youtube_transcript_api._errors import YouTubeTranscriptApiException

from pathlib import Path
import json
from typing import Literal, Union, List
from dataclasses import dataclass, field


@dataclass
class Snippet:
    text: str
    start: float
    duration: float


@dataclass
class Transcript:
    video_id: str
    language: str
    language_code: str
    is_generated: bool
    snippets: List[Snippet] = field(default_factory=list)
    transcript: str = ""


def parse_time_to_seconds(time_str: str) -> float:
    """
    Convert time string in format MM:SS or HH:MM:SS to seconds.

    Args:
        time_str: Time string in format MM:SS or HH:MM:SS

    Returns:
        Time in seconds as a float
    """
    parts = time_str.split(":")

    if len(parts) == 2:  # MM:SS format
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    elif len(parts) == 3:  # HH:MM:SS format
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    else:
        raise ValueError("Invalid time format. Use MM:SS or HH:MM:SS")


def save_transcript(video_id: str) -> Union[Literal[0], Literal[1]]:
    """
    Save transcript to $HOME/.segscript of a given video id if available.

    Args:
        video_id: Youtube video ID

    Returns:
        0 if transcript saved successfully else 1

    """
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript: FetchedTranscript = ytt_api.fetch(video_id)
    except YouTubeTranscriptApiException:
        return 1

    Path("~/.segscript").expanduser().mkdir(exist_ok=True)

    output_path = Path(f"~/.segscript/{video_id}.json").expanduser()

    raw_transcript = ""

    for snippet in transcript.snippets:
        raw_transcript = raw_transcript + " " + snippet.text

    transcript_dict = {
        "video_id": transcript.video_id,
        "language": transcript.language,
        "language_code": transcript.language_code,
        "is_generated": transcript.is_generated,
        "snippets": [
            {"text": snippet.text, "start": snippet.start, "duration": snippet.duration}
            for snippet in transcript.snippets
        ],
        "transcript": raw_transcript,
    }

    # Write to JSON file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transcript_dict, f, indent=2)

    return 0


def query_transcript(video_id: str, time_range: str) -> str:
    """
    Query transcript for a specific video within a given time range.

    Args:
        video_id: YouTube video ID
        time_range: Time range in the format "start_time;end_time" (e.g., "10:00;20:00")
                    Times can be in MM:SS or HH:MM:SS format

    Returns:
        The transcript text within the specified time range
    """
    transcript_file = Path(f"~/.segscript/{video_id}.json").expanduser()

    if not transcript_file.exists():
        print(f"Transcript for video {video_id} not found. Fetching...")
        success = save_transcript(video_id)
        if success != 0:
            return "Error: Failed to fetch transcript!"

    with open(transcript_file, "r", encoding="utf-8") as f:
        transcript_data = json.load(f)

    snippets = transcript_data["snippets"]

    # If no time range specified, return the full transcript
    if not time_range:
        return transcript_data["transcript"]

    # Parse time range
    try:
        start_time_str, end_time_str = time_range.split(";")
        start_seconds = parse_time_to_seconds(start_time_str)
        end_seconds = parse_time_to_seconds(end_time_str)
    except ValueError:
        return "Error: Invalid time range format. Use 'start_time;end_time' (e.g., '10:00;20:00')"

    # Find snippets within the time range
    filtered_snippets = []
    for snippet in snippets:
        snippet_start = snippet["start"]
        snippet_end = snippet_start + snippet["duration"]

        # Include snippet if it overlaps with the specified range
        if snippet_start <= end_seconds and snippet_end >= start_seconds:
            filtered_snippets.append(snippet)

    # Concatenate the text of the filtered snippets
    result_text = " ".join(snippet["text"] for snippet in filtered_snippets)

    return result_text


def get_raw_transcripts(video_id: str) -> Union[str, None]:
    """
    Get raw transcript of a given video id if it is stored in [.segscript]

    Args:
        video_id: Youtube video ID.

    Returns:
        raw_transcript: Raw transcript of a given video ID.

    """
    try:
        transcript_path = Path(f"~/.segscript/{video_id}.json").expanduser()
        with open(transcript_path, mode="r", encoding="utf-8") as f:
            transcript_data: Transcript = json.load(f)
        return transcript_data.transcript

    except FileNotFoundError:
        print(f"The transcript for video id: {video_id} does not exist")
        return None


def main():
    video_id = input("Enter YouTube video ID (the 11-character code in the URL): ")
    transcript_file = Path(f"~/.segscript/{video_id}.json").expanduser()

    # Check if transcript already exists
    if transcript_file.exists():
        print(f"Transcript for video {video_id} already exists. Loading from file...")
        with open(transcript_file, "r", encoding="utf-8") as f:
            transcript_data = json.load(f)
            print(f"Loaded transcript for video: {transcript_data['video_id']}")
    else:
        print(f"Fetching transcript for video {video_id}...")
        success = save_transcript(video_id)
        if success == 0:
            print("Transcript saved successfully.")
        else:
            print("YouTube video ID incorrect or transcript unavailable!")
            return

    # Query options
    print("\nOptions:")
    print("1. Get full transcript")
    print("2. Get transcript within a time range")
    choice = input("Enter your choice (1 or 2): ")

    if choice == "1":
        transcript_text = video_id
        transcript_text = get_raw_transcripts(video_id)
        print("\nFull transcript:")
        print(transcript_text)
    elif choice == "2":
        time_range = input("Enter time range (e.g., '10:00;20:00'): ")
        transcript_text = query_transcript(video_id, time_range)
        print(f"\nTranscript from {time_range}:")
        print(transcript_text)
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
