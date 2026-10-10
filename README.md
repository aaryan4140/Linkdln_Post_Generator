# LinkedIn Post Generator

An automated pipeline that turns HTML carousel slides into production-ready LinkedIn post assets — PNGs, animated GIFs, and MP4 videos — using Playwright and FFmpeg.

## What It Does

1. **HTML → PNG**: Renders self-contained HTML carousel slides (1080×1080, @2x retina) into high-quality PNGs using headless Chrome via Playwright.
2. **PNG → GIF/MP4**: Assembles exported PNGs into animated GIFs and MP4 videos with build-up reveals, crossfade transitions, and seamless looping — powered by Pillow and FFmpeg.

Each post lives as a standalone HTML file in `Content/PostN/` with its own dark-themed design, typography, and layout. The pipeline exports everything into organized output folders.

## Project Structure

```
├── Content/            # HTML source files for each post
│   ├── Post0/
│   ├── Post1/
│   └── ...
├── Post/               # Exported PNGs (1080x1080 @2x)
│   ├── Post0/
│   └── ...
├── animated GIF/       # Exported GIFs and MP4s
│   ├── Post0/
│   └── ...
├── Docs/               # Source documents for post creation
├── export_all.py       # PNG export script (Playwright + Chrome)
├── create_gif.py       # GIF/MP4 creation script (Pillow + FFmpeg)
├── run.sh              # Master runner script
└── COMMANDS.md         # Quick command reference
```

## Prerequisites

- Python 3 (Anaconda recommended)
- Playwright (`pip install playwright`)
- Chromium browser (`playwright install chromium`)
- Pillow (`pip install Pillow`)
- FFmpeg (for GIF/MP4 generation)

## Usage

```bash
# Run the full pipeline (PNGs + GIFs + MP4s)
./run.sh

# Export PNGs only
./run.sh export

# Create GIFs + MP4s only
./run.sh gif

# Create GIF + MP4 for a single post
./run.sh gif Post0
```

## Creating New Posts

1. Drop your source document in `Docs/`
2. Open Claude Code and say: *"Create LinkedIn posts from Docs/filename.md"*
3. Run `./run.sh` to export everything

## Output

- **PNGs**: 1080×1080 retina-quality slides in `Post/`
- **GIFs**: Full-color animated carousels with crossfade transitions in `animated GIF/`
- **MP4s**: Near-lossless H.264 videos optimized for LinkedIn in `animated GIF/`
