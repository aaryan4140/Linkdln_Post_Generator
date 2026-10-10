#!/usr/bin/env /opt/anaconda3/bin/python3
"""
Create animated GIF + MP4 from LinkedIn post PNGs.

Features:
- Build-up animation: elements fade in on each slide
- Fade transition between slides
- Infinite loop
- Medium pace (8-12 seconds total)

Usage:
  python3 create_gif.py                    # All posts
  python3 create_gif.py Post0             # Single post
"""

import sys
import os
from pathlib import Path
from PIL import Image, ImageFilter
import subprocess

SCRIPT_DIR = Path(__file__).parent.resolve()
POST_DIR = SCRIPT_DIR / "Post"
OUTPUT_DIR = SCRIPT_DIR / "animated GIF"

# Timing config (medium pace)
HOLD_DURATION_MS = 4000      # How long each slide is fully visible
FADE_STEPS = 15              # Number of frames in fade transition
FADE_STEP_MS = 80            # Duration per fade frame (total fade = 1.2s)
BUILDUP_STEPS = 8            # Number of frames for build-up reveal
BUILDUP_STEP_MS = 100        # Duration per build-up frame (total = 0.8s)
FINAL_HOLD_MS = 2000         # Extra hold on last slide before loop restart
FPS = 12                     # Frames per second for MP4


def create_buildup_frames(img):
    """Create build-up animation: slide reveals from top to bottom with fade."""
    w, h = img.size
    frames = []
    for i in range(BUILDUP_STEPS):
        progress = (i + 1) / BUILDUP_STEPS
        frame = Image.new("RGBA", (w, h), (13, 18, 36, 255))

        # Reveal portion of the image from top
        reveal_h = int(h * progress)
        if reveal_h > 0:
            cropped = img.crop((0, 0, w, reveal_h))
            # Apply slight fade to the revealed portion
            alpha = int(255 * (0.4 + 0.6 * progress))
            overlay = Image.new("RGBA", cropped.size, (255, 255, 255, 0))
            blended = Image.blend(
                Image.new("RGBA", cropped.size, (13, 18, 36, 255)),
                cropped.convert("RGBA"),
                alpha / 255
            )
            frame.paste(blended, (0, 0))

        frames.append(frame.convert("RGB"))

    return frames


def create_fade_frames(img_from, img_to):
    """Create crossfade transition frames between two slides."""
    frames = []
    for i in range(FADE_STEPS):
        alpha = (i + 1) / FADE_STEPS
        blended = Image.blend(
            img_from.convert("RGBA"),
            img_to.convert("RGBA"),
            alpha
        )
        frames.append(blended.convert("RGB"))
    return frames


def process_post(post_name):
    """Create GIF + MP4 for a single post."""
    post_path = POST_DIR / post_name
    out_path = OUTPUT_DIR / post_name
    out_path.mkdir(parents=True, exist_ok=True)

    # Find all PNGs in order
    pngs = sorted(post_path.glob("*.png"))
    if not pngs:
        print(f"  ⚠  No PNGs found in {post_path}")
        return False

    print(f"📂 {post_name}/ ({len(pngs)} slides)")

    # Load images
    images = []
    for p in pngs:
        img = Image.open(p).convert("RGB")
        # Resize to 1080x1080 if needed
        if img.size != (1080, 1080):
            img = img.resize((1080, 1080), Image.LANCZOS)
        images.append(img)

    # Build frame sequence
    all_frames = []
    all_durations = []

    for idx, img in enumerate(images):
        # Build-up animation ONLY on the first slide
        # Other slides are introduced by fade transition — no double reveal
        if idx == 0:
            buildup = create_buildup_frames(img)
            all_frames.extend(buildup)
            all_durations.extend([BUILDUP_STEP_MS] * len(buildup))

        # Hold on the full slide
        hold_frames = max(1, HOLD_DURATION_MS // 100)
        for _ in range(hold_frames):
            all_frames.append(img)
            all_durations.append(100)

        # Fade transition to next slide (or back to first for loop)
        if idx < len(images) - 1:
            fade = create_fade_frames(img, images[idx + 1])
            all_frames.extend(fade)
            all_durations.extend([FADE_STEP_MS] * len(fade))
        else:
            # Extra hold on last slide
            extra_frames = max(1, FINAL_HOLD_MS // 100)
            for _ in range(extra_frames):
                all_frames.append(img)
                all_durations.append(100)

            # Fade back to first slide for seamless loop
            fade = create_fade_frames(img, images[0])
            all_frames.extend(fade)
            all_durations.extend([FADE_STEP_MS] * len(fade))

    # === EXPORT HIGH-QUALITY GIF via ffmpeg ===
    # ffmpeg produces far better GIFs than Pillow — proper dithering + palette optimization
    gif_path = out_path / f"{post_name.lower()}_animated.gif"
    print(f"   Creating high-quality GIF ({len(all_frames)} frames @ 1080x1080)...")

    # Save full-res frames to temp
    temp_dir = out_path / "_temp_frames"
    temp_dir.mkdir(exist_ok=True)

    for i, frame in enumerate(all_frames):
        frame.save(str(temp_dir / f"frame_{i:04d}.png"), "PNG")

    # Create concat file with durations
    concat_path = temp_dir / "concat.txt"
    with open(concat_path, "w") as f:
        for i, dur in enumerate(all_durations):
            f.write(f"file 'frame_{i:04d}.png'\n")
            f.write(f"duration {dur / 1000:.3f}\n")
        f.write(f"file 'frame_{len(all_frames)-1:04d}.png'\n")

    # Step 1: Generate optimized palette from all frames
    palette_path = temp_dir / "palette.png"
    palette_cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_path),
        "-vf", "scale=1080:1080:flags=lanczos,palettegen=max_colors=256:stats_mode=full",
        str(palette_path)
    ]
    subprocess.run(palette_cmd, capture_output=True, text=True, cwd=str(temp_dir))

    # Step 2: Create GIF using the optimized palette with dithering
    gif_cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_path),
        "-i", str(palette_path),
        "-lavfi", "scale=1080:1080:flags=lanczos[x];[x][1:v]paletteuse=dither=floyd_steinberg",
        "-loop", "0",
        str(gif_path)
    ]
    result = subprocess.run(gif_cmd, capture_output=True, text=True, cwd=str(temp_dir))

    if result.returncode == 0 and gif_path.exists():
        gif_size = gif_path.stat().st_size / (1024 * 1024)
        print(f"   ✅ {gif_path.name} ({gif_size:.1f} MB)")
    else:
        print(f"   ⚠  GIF failed: {result.stderr[-300:]}")
    gif_size = gif_path.stat().st_size / (1024 * 1024)
    print(f"   ✅ {gif_path.name} ({gif_size:.1f} MB)")

    # === EXPORT MAX QUALITY MP4 (reuses same temp frames) ===
    mp4_path = out_path / f"{post_name.lower()}_animated.mp4"
    print(f"   Creating max-quality MP4...")

    # Use ffmpeg with concat demuxer for precise timing
    # CRF 0 = lossless, but huge. CRF 1 = near-lossless, much smaller.
    # preset veryslow = maximum compression efficiency at given quality
    # tune stillimage = optimized for slides/graphics (not live video)
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_path),
        "-vf", "scale=1080:1080:flags=lanczos",
        "-c:v", "libx264",
        "-pix_fmt", "yuv444p",
        "-crf", "1",
        "-preset", "veryslow",
        "-tune", "stillimage",
        "-movflags", "+faststart",
        "-color_range", "pc",
        str(mp4_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(temp_dir))

    if result.returncode == 0:
        mp4_size = mp4_path.stat().st_size / (1024 * 1024)
        print(f"   ✅ {mp4_path.name} ({mp4_size:.1f} MB)")
    else:
        print(f"   ⚠  MP4 failed: {result.stderr[-200:]}")

    # Cleanup temp frames
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)

    return True


def main():
    posts = sys.argv[1:] if len(sys.argv) > 1 else None

    if posts is None:
        # Process all posts
        posts = sorted([d.name for d in POST_DIR.iterdir() if d.is_dir() and d.name.startswith("Post")])

    print(f"\n🎬 Creating animated GIF + MP4...\n")

    for post in posts:
        process_post(post)

    print(f"\n✅ Done! Output in: {OUTPUT_DIR}\n")


if __name__ == "__main__":
    main()
