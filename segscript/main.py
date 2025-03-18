import click
from pathlib import Path
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from typing import List, Dict


# Import your existing functions
from .utils import save_transcript, query_transcript, get_raw_transcripts

# Initialize Rich console
console = Console()


def get_all_transcripts() -> List[Dict]:
    """
    Get all downloaded transcripts from the .segscript directory

    Returns:
        List of dictionaries with video_id and title (if available)
    """
    segscript_dir = Path('~/.segscript').expanduser()
    if not segscript_dir.exists():
        return []

    transcripts = []
    for video_dir in segscript_dir.iterdir():
        if video_dir.is_dir():
            video_id = video_dir.name
            metadata_file = video_dir / 'metadata.json'

            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)

                    # Try to get video title if available
                    title = metadata.get('title', 'Unknown Title')

                    transcripts.append({'video_id': video_id, 'title': title})
                except Exception as e:
                    console.print(
                        f'[yellow]Warning: Could not read {metadata_file}: {e}[/yellow]'
                    )

    return transcripts


@click.group()
def main():
    """SegScript - A tool for managing and enhancing YouTube transcripts."""
    pass


@main.command()
def list():
    """List all downloaded transcripts."""
    transcripts = get_all_transcripts()

    if not transcripts:
        console.print(
            "[yellow]No transcripts found. Use the 'download' command to download a transcript.[/yellow]"
        )
        return

    table = Table(title='Downloaded Transcripts', box=box.ROUNDED)
    table.add_column('Video ID', style='cyan')
    table.add_column('Title', style='green')

    for transcript in transcripts:
        table.add_row(transcript['video_id'], transcript['title'])

    console.print(table)


@main.command()
@click.argument('video_id')
def download(video_id):
    """Download a transcript for a YouTube video."""
    console.print(f'[bold blue]Downloading transcript for {video_id}...[/bold blue]')

    success = save_transcript(video_id)

    if success == 0:
        console.print(
            f'[bold green]Transcript for {video_id} downloaded successfully![/bold green]'
        )
    else:
        console.print(
            f'[bold red]Failed to download transcript for {video_id}. Check the video ID or try again later.[/bold red]'
        )


@main.command()
@click.argument('video_id')
@click.option(
    '--time-range',
    '-t',
    help="Time range in format 'start_time;end_time' (e.g. '10:00;20:00')",
)
def get(video_id, time_range):
    """Get transcript for a video, optionally within a time range and enhanced."""
    transcript_file = Path(f'~/.segscript/{video_id}/{video_id}.json').expanduser()

    if not transcript_file.exists():
        console.print(
            f'[yellow]Transcript for video {video_id} not found. Downloading...[/yellow]'
        )
        success = save_transcript(video_id)
        if success != 0:
            console.print('[bold red]Failed to download transcript![/bold red]')
            return

    if time_range:
        console.print(
            f'[bold blue]Getting transcript for {video_id} from {time_range}...[/bold blue]'
        )
        transcript_text = query_transcript(video_id, time_range)

        header_text = f'Transcript for {time_range.replace(";", " ; ")}'

        console.print(
            Panel(
                Text(header_text, justify='center', style='bold magenta'),
                border_style='blue',
                expand=True,
            )
        )
        console.print(transcript_text)
    else:
        console.print(
            f'[bold blue]Getting full transcript for {video_id}...[/bold blue]'
        )
        transcript_text = get_raw_transcripts(video_id)

        if transcript_text:
            console.print(
                Panel(
                    Text('Preview Transcript', justify='center', style='bold magenta'),
                    border_style='blue',
                    expand=True,
                )
            )
            console.print(Text(transcript_text[:1000] + '...', overflow='fold'))
            if click.confirm('Show full transcript?'):
                console.print(
                    Panel(
                        Text('Full Transcript', justify='center', style='bold magenta'),
                        border_style='blue',
                        expand=True,
                    )
                )
                console.print(transcript_text)
        else:
            console.print('[bold red]Failed to get transcript![/bold red]')


@main.command()
def prompt():
    """Start interactive mode for working with transcripts."""
    transcripts = get_all_transcripts()

    if not transcripts:
        console.print(
            '[yellow]No transcripts found. Downloading a new transcript...[/yellow]'
        )
        video_id = click.prompt('Enter YouTube video ID')
        success = save_transcript(video_id)
        if success != 0:
            console.print('[bold red]Failed to download transcript![/bold red]')
            return
        transcripts = get_all_transcripts()

    # Display available transcripts
    table = Table(title='Available Transcripts', box=box.ROUNDED)
    table.add_column('#', style='cyan')
    table.add_column('Video ID', style='green')
    table.add_column('Title', style='blue')

    for i, transcript in enumerate(transcripts, 1):
        table.add_row(str(i), transcript['video_id'], transcript['title'])

    console.print(table)

    # Let user select a transcript
    selection = click.prompt('Select a transcript number', type=int, default=1)
    if selection < 1 or selection > len(transcripts):
        console.print('[bold red]Invalid selection![/bold red]')
        return

    selected_video = transcripts[selection - 1]['video_id']
    console.print(f'[bold green]Selected video: {selected_video}[/bold green]')

    # Ask what to do with the selected transcript
    console.print('\n[bold]What would you like to do?[/bold]')
    console.print('[cyan]1.[/cyan] View full transcript')
    console.print('[cyan]2.[/cyan] Get Enhanced query transcript by time range')

    action = click.prompt('Enter your choice', type=int, default=1)

    if action == 1:
        transcript_text = get_raw_transcripts(selected_video)
        if transcript_text:
            console.print(
                Panel(
                    Text('Preview Transcript', justify='center', style='bold magenta'),
                    border_style='blue',
                    expand=True,
                )
            )
            console.print(Text(transcript_text[:1000] + '...', overflow='fold'))
            if click.confirm('Show full transcript?'):
                console.print(
                    Panel(
                        Text('Full Transcript', justify='center', style='bold magenta'),
                        border_style='blue',
                        expand=True,
                    )
                )
                console.print(transcript_text)

    elif action == 2:
        time_range = click.prompt("Enter time range (e.g., '10:00;20:00')")
        transcript_text = query_transcript(selected_video, time_range)

        header_text = f'Transcript for {time_range}'

        console.print(
            Panel(
                Text(header_text, justify='center', style='bold magenta'),
                border_style='blue',
                expand=True,
            )
        )
        console.print(Text(transcript_text, overflow='fold', no_wrap=False))
    else:
        console.print('[bold red]Invalid choice![/bold red]')
