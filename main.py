from pathlib import Path
import json





    """

    Returns:
    """
















    transcript_file = Path(f"~/.segscript/{video_id}/{video_id}.json").expanduser()

    if not transcript_file.exists():
        success = save_transcript(video_id)
        if success != 0:


    else:









    else:


if __name__ == "__main__":
