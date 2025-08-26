import os
import time

import click
from pathlib import Path
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.markdown import Markdown
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
            "[yellow]⚠️ No transcripts found. Use the 'download' command to download a transcript.[/yellow]"
        )
        return

    table = Table(
        title='[bold]Available Transcripts[/bold]',
        box=box.ROUNDED,
        show_header=True,
        header_style='bold magenta',
    )
    table.add_column('#', style='dim cyan', justify='center')
    table.add_column('Video ID', style='cyan', no_wrap=True)
    table.add_column('Title', style='green')

    for i, transcript in enumerate(transcripts, 1):
        table.add_row(str(i), transcript['video_id'], transcript['title'])

    console.print(table)


@main.command()
@click.argument('video_id')
def download(video_id):
    """Download a transcript for a YouTube video."""
    console.print(f'[bold blue]⏳ Downloading transcript for {video_id}...[/bold blue]')

    success = save_transcript(video_id)

    if success == 0:
        console.print(
            f'[bold green]✅ Transcript for {video_id} downloaded successfully![/bold green]'
        )
    else:
        console.print(
            f'[bold red]❌ Failed to download transcript for {video_id}. Check the video ID or try again later.[/bold red]'
        )


@main.command()
@click.argument('video_id')
@click.option(
    '--time-range',
    '-t',
    help="Time range in format 'start_time;end_time' (e.g. '10:00;20:00')",
)
@click.option(
    '--width',
    '-w',
    help='Maximum characters per line for wrapping the transcript text.',
)
def get(video_id, time_range, width):
    """
    Get transcript for a video, optionally within a time range and enhanced.

    If your VIDEO_ID starts with a hyphen '-', use '--' before it, e.g.:
    `segscript get -- --your-video-id`
    """
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
        transcript_text = query_transcript(video_id, time_range, width)

        header_text = f'Transcript for {time_range.replace(";", " ; ")}'

        console.print(
            Panel(
                Text(header_text, justify='center', style='bold magenta'),
                border_style='blue',
                expand=True,
            )
        )
        console.print(Markdown(transcript_text))
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
                console.print(Markdown(transcript_text))
        else:
            console.print('[bold red]Failed to get transcript![/bold red]')


@main.command()
def prompt():
    """Start interactive mode for working with transcripts."""
    while True:
        time.sleep(0.5)
        os.system('cls' if os.name == 'nt' else 'clear')

        transcripts = get_all_transcripts()

        # Display available transcripts
        table = Table(
            title='[bold]Available Transcripts[/bold]',
            box=box.ROUNDED,
            show_header=True,
            header_style='bold magenta',
        )
        table.add_column('#', style='dim cyan', justify='right')
        table.add_column('Video ID', style='cyan', no_wrap=True)
        table.add_column('Title', style='green')

        table.add_row('0', '[yellow i]-- Download New Transcript --[/yellow i]', '')

        for i, transcript in enumerate(transcripts, 1):
            table.add_row(str(i), transcript['video_id'], transcript['title'])

        console.print(table)

        # Let user select a transcript

        console.print(
            f'➡️ Select # (0 to download, 1-{len(transcripts)} to use existing):'
        )
        selection = click.prompt('> ', type=int)
        if selection < 0 or selection > len(transcripts):
            console.print('[bold red]Invalid selection![/bold red]')
            return

        if selection == 0:
            console.print('\nEnter the YouTube Video ID to download:')
            video_id_to_download = click.prompt('> ')
            console.print(
                f'[bold blue]⏳ Downloading transcript for [cyan]{video_id_to_download}[/cyan]...[/bold blue]'
            )
            # Call save_transcript directly.
            success = save_transcript(video_id_to_download)
            if success == 0:
                console.print(
                    f'[bold green]✅ Transcript for [cyan]{video_id_to_download}[/cyan] downloaded successfully![/bold green]'
                )
            else:
                console.print(
                    f'[bold red]❌ Failed to download transcript for {video_id_to_download}. Check ID or API limits.[/bold red]'
                )

            time.sleep(1.5)
            os.system('cls' if os.name == 'nt' else 'clear')

            continue
        else:
            selected_transcript = transcripts[selection - 1]
            selected_video_id = selected_transcript['video_id']
            selected_title = selected_transcript.get('title', 'Unknown Title')

            console.print(
                f'[bold green]Selected video: [/bold green] [{selected_video_id}] {selected_title}'
            )

            # Ask what to do with the selected transcript
            console.print('\n[bold underline]Choose an action:[/bold underline]')
            console.print('[cyan] 1.[/] View full [dim]raw[/dim] transcript')
            console.print(
                '[cyan] 2.[/] Get [dim]enhanced[/dim] transcript segment by time range'
            )

            action = click.prompt('> ', type=int, default=1)

            if action == 1:
                transcript_text = get_raw_transcripts(selected_video_id)
                if transcript_text:
                    console.print(
                        Panel(
                            Text(
                                'Raw Transcript Preview',
                                justify='center',
                                style='bold magenta',
                            ),
                            border_style='blue',
                            expand=True,
                        )
                    )
                    console.print(
                        Text(transcript_text[:1000] + '...', overflow='fold'),
                        highlight=False,
                    )
                    if click.confirm('Show full transcript?'):
                        console.print(
                            Panel(
                                Text(
                                    f'Full Raw Transcript: {selected_video_id}',
                                    justify='center',
                                    style='bold magenta',
                                ),
                                border_style='blue',
                                expand=True,
                            )
                        )
                        console.print(Markdown(transcript_text))

            elif action == 2:
                console.print("Enter time range (e.g., '1:23;4:56' or '10:00;25:30'):")
                time_range = click.prompt('> ')
                console.print(
                    'Enter the max characters per line to format the transcript text (Default=60)'
                )
                width: int = click.prompt('> ', default=60)

                console.print(
                    f'\n[bold blue]Processing transcript segment for [cyan]{selected_video_id}[/cyan] ({time_range})...[/bold blue]'
                )
                transcript_text = query_transcript(selected_video_id, time_range, width)

                header_text = f'Transcript for {time_range}'

                console.print(
                    Panel(
                        Text(header_text, justify='center', style='bold magenta'),
                        border_style='blue',
                        expand=True,
                    )
                )
                console.print(Markdown(transcript_text))
            else:
                console.print('[bold red]Invalid choice![/bold red]')
            break
