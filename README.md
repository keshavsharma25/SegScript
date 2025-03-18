# SegScript

A command-line tool for managing, enhancing, and interacting with YouTube transcripts.

<!-- mtoc-start -->

* [Overview](#overview)
* [Features](#features)
* [Installation](#installation)
* [Dependencies](#dependencies)
* [Usage](#usage)
  * [Basic Commands](#basic-commands)
  * [Interactive Mode](#interactive-mode)
* [File Structure](#file-structure)
* [Examples](#examples)
  * [Download a transcript](#download-a-transcript)
  * [View a transcript for a specific section of a video](#view-a-transcript-for-a-specific-section-of-a-video)
  * [Interactive browsing](#interactive-browsing)
* [Contributing](#contributing)
* [License](#license)
* [Acknowledgments](#acknowledgments)

<!-- mtoc-end -->

## Overview

SegScript allows you to download, view, and query YouTube video transcripts directly from your terminal. It provides a clean interface for working with transcripts, including the ability to extract specific time ranges and view enhanced transcript content.

## Features

* **Download transcripts** from any YouTube video using its ID
* **List all downloaded transcripts** stored in your local collection
* **View full transcripts** or segments based on time ranges
* **Interactive mode** for browsing and working with your transcript collection
* **Rich text formatting** for improved readability in the terminal

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/segscript.git
cd segscript

# Install dependencies
pip install -r requirements.txt

# Install the package (optional)
pip install -e .
```

## Dependencies

* *youtube-transcript-api*: Fetch youtube transcripts with ease
* *click*: Command-line interface creation kit
* *rich*: Terminal formatting and styling
* *python-dotenv*: Load `GOOGLE_API_KEY` from the command line environment
* *pathlib*: Object-oriented filesystem paths
* *langchain-google-genai*: For synthesizing transcript into a well structured format

## Usage

### Basic Commands

```bash
# List all downloaded transcripts
segscript list

# Download a transcript for a YouTube video
segscript download VIDEO_ID

# Get a transcript (downloads if not already available)
segscript get VIDEO_ID

# Get a transcript for a specific time range
segscript get VIDEO_ID --time-range "10:00;20:00"

# Start interactive mode
segscript interactive
```

### Interactive Mode

Interactive mode provides a user-friendly interface for:

1. Browsing your transcript collection
2. Selecting a transcript to work with
3. Viewing full transcripts or specific segments
4. Querying transcripts by time range

## File Structure

Transcripts are stored in the `~/.segscript/` directory with the following structure:

```
~/.segscript/
├── .env                    # Environment variables file
├── VIDEO_ID_1/
│   ├── VIDEO_ID_1.json     # Raw transcript data
│   └── metadata.json       # Video metadata
├── VIDEO_ID_2/
│   ├── VIDEO_ID_2.json
│   └── metadata.json
└── ...
```

## Examples

### Download a transcript

```bash
segscript download dQw4w9WgXcQ
```

### View a transcript for a specific section of a video

```bash
segscript get dQw4w9WgXcQ --time-range "1:30;2:45"
```

### Interactive browsing

```bash
segscript interactive
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

* A huge thanks to [Youtube Transcript API](https://github.com/jdepoix/youtube-transcript-api) to make my idea into a project.
* Built with [Rich](https://github.com/Textualize/rich) for beautiful terminal output
* Uses [Click](https://click.palletsprojects.com/) for command-line interface

---

*Note: SegScript is not affiliated with YouTube or Google.*
