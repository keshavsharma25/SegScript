# SegScript

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/segscript.svg)](https://badge.fury.io/py/segscript)

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
* [Next TODOs](#next-todos)
* [Contributing](#contributing)
* [License](#license)
* [Acknowledgments](#acknowledgments)

<!-- mtoc-end -->

## Overview

SegScript allows you to download, view, and query YouTube video transcripts directly from your terminal. It provides a clean interface for working with transcripts, including the ability to extract specific time ranges and view enhanced transcript content. I've used the `langchain-google-genai` package in conjunction with Google's Gemini Flash 2.0 model, which has delivered exceptional results in transcript enhancement.

## Features

* **Download transcripts** from any YouTube video using its ID
* **List all downloaded transcripts** stored in your local collection
* **View full transcripts** or segments based on time ranges
* **Interactive mode** for browsing and working with your transcript collection
* **Rich text formatting** for improved readability in the terminal

## Installation

```bash
pip install segscript
```

For testing purposes,

```bash
# Clone the repository
git clone https://github.com/keshavsharma25/segscript.git
cd segscript

# Install dependencies
pip install -r pyproject.toml

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
segscript prompt
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
segscript prompt
```

## Next TODOs

* [ ] Add transcript summary support.
* [x] Add a prompt to make the each sentence be have its own line for better readibility.
* [x] In `prompt`, improve the UX by clearing the screen before running the command (like after download in `prompt`).
* [x] Improve the copy of the segscript prompt for better understanding.

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

* A huge thanks to [Youtube Transcript API](https://github.com/jdepoix/youtube-transcript-api) for making transcript retrieval so easy and accessible.
* Also kudos to [Langchain Google](https://github.com/langchain-ai/langchain-google) for the `langchain-google-genai`.
* Built with [Rich](https://github.com/Textualize/rich) for beautiful terminal output.
* Uses [Click](https://click.palletsprojects.com/) for command-line interface.

---

*Note: SegScript is not affiliated with YouTube or Google.*
