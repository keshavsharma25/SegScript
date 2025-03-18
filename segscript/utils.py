from youtube_transcript_api._api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    YouTubeTranscriptApiException,
    NoTranscriptFound,
)

import requests

from pathlib import Path
import json
from typing import Dict, Literal, TypedDict, Union, List

from .model import enhance_transcript


class Snippet(TypedDict):
    text: str
    start: float
    duration: float


class Transcript(TypedDict):
    video_id: str
    language: str
    language_code: str
    is_generated: bool
    snippets: List[Snippet]
    transcript: str


def parse_time_to_seconds(time_str: str) -> float:
    """
    Convert time string in format MM:SS or HH:MM:SS to seconds.

    Args:
        time_str: Time string in format MM:SS or HH:MM:SS

    Returns:
        Time in seconds as a float
    """
    parts = time_str.split(':')

    if len(parts) == 2:  # MM:SS format
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    elif len(parts) == 3:  # HH:MM:SS format
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    else:
        raise ValueError('Invalid time format. Use MM:SS or HH:MM:SS')


def get_metadata(
    video_id: str,
) -> Union[Dict[str, str], None]:
    oembed_url = f'https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json'

    response = requests.get(oembed_url)
    if response.status_code == 200:
        data = response.json()
        return {
            'title': data.get('title'),
            'channel': data.get('author_name'),
        }
    else:
        return None


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

        # First, get the list of available transcripts
        transcript_list = ytt_api.list_transcripts(video_id)

        # Define various English language codes to check
        english_codes = ['en', 'en-US', 'en-GB', 'en-CA', 'en-AU']

        # Initialize transcript variable
        transcript = None

        # Try to find a manually created English transcript first
        try:
            transcript = transcript_list.find_manually_created_transcript(english_codes)
        except NoTranscriptFound:
            # If no manually created English transcript, try to find a generated English transcript
            try:
                transcript = transcript_list.find_generated_transcript(english_codes)
            except NoTranscriptFound:
                # If no English transcript at all, get any available transcript
                try:
                    # This will get the first available transcript (manually created first, then generated)
                    transcript = next(iter(transcript_list))
                except StopIteration:
                    # No transcripts available at all
                    return 1

        # Now we have a single transcript, fetch it
        if transcript:
            transcript = transcript.fetch()
        else:
            return 1

    except YouTubeTranscriptApiException:
        return 1

    Path(f'~/.segscript/{video_id}').expanduser().mkdir(exist_ok=True)

    video_id_path = Path(f'~/.segscript/{video_id}').expanduser()

    metadata_file = video_id_path / 'metadata.json'
    output_file = video_id_path / f'{video_id}.json'

    raw_transcript = ''

    snippets: List[Snippet] = []

    for snippet in transcript.snippets:
        raw_transcript = raw_transcript + ' ' + snippet.text

        snippets.append(
            {
                'text': snippet.text,
                'start': snippet.start,
                'duration': snippet.duration,
            }
        )

    transcript_dict: Transcript = {
        'video_id': transcript.video_id,
        'language': transcript.language,
        'language_code': transcript.language_code,
        'is_generated': transcript.is_generated,
        'snippets': snippets,
        'transcript': raw_transcript,
    }

    metadata = get_metadata(video_id)
    if metadata:
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
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
    transcript_file = Path(f'~/.segscript/{video_id}/{video_id}.json').expanduser()

    if not transcript_file.exists():
        print(f'Transcript for video {video_id} not found. Fetching...')
        success = save_transcript(video_id)
        if success != 0:
            return 'Error: Failed to fetch transcript!'

    with open(transcript_file, 'r', encoding='utf-8') as f:
        transcript_data = json.load(f)

    snippets = transcript_data['snippets']

    # Parse time range
    try:
        start_time_str, end_time_str = time_range.split(';')
        start_seconds = parse_time_to_seconds(start_time_str)
        end_seconds = parse_time_to_seconds(end_time_str)
    except ValueError:
        return "Error: Invalid time range format. Use 'start_time;end_time' (e.g., '10:00;20:00')"

    # Find snippets within the time range
    filtered_snippets = []
    for snippet in snippets:
        snippet_start = snippet['start']
        snippet_end = snippet_start + snippet['duration']

        # Include snippet if it overlaps with the specified range
        if snippet_start <= end_seconds and snippet_end >= start_seconds:
            filtered_snippets.append(snippet)

    # Concatenate the text of the filtered snippets
    result_text = ' '.join(snippet['text'] for snippet in filtered_snippets)

    enhanced_dir = Path(f'~/.segscript/{video_id}').expanduser()

    # Generate a filename based on the time rang
    time_range_str = (
        time_range.replace(':', '_').replace(';', '-') if time_range else 'full'
    )
    enhanced_file = enhanced_dir / f'{time_range_str}.txt'

    # Check if we already have an enhanced version
    if enhanced_file.exists():
        with open(enhanced_file, 'r', encoding='utf-8') as f:
            return f.read()

    # Otherwise, enhance the transcript
    enhanced_text = enhance_transcript(result_text)

    if enhanced_text and not enhanced_text.startswith('Error:'):
        with open(enhanced_file, 'w', encoding='utf-8') as f:
            f.write(enhanced_text)

        return enhanced_text

    else:
        return f"Enhanced Transcript is not available hence here's the raw-transcript of the segment: \n{result_text}"


def get_raw_transcripts(video_id: str) -> Union[str, None]:
    """
    Get raw transcript of a given video id if it is stored in [.segscript]

    Args:
        video_id: Youtube video ID.

    Returns:
        raw_transcript: Raw transcript of a given video ID.

    """
    try:
        transcript_path = Path(f'~/.segscript/{video_id}/{video_id}.json').expanduser()
        with open(transcript_path, mode='r', encoding='utf-8') as f:
            transcript_data: Transcript = json.load(f)
        if transcript_data:
            return transcript_data.get('transcript', 'Transcript is unavailable')

    except FileNotFoundError:
        print(f'The transcript for video id: {video_id} does not exist')
        return None
