#!/usr/bin/env /opt/anaconda3/bin/python3
"""
Export all LinkedIn post slides as 1080x1080 @2x PNGs using local Chrome.
Usage: python3 export_all.py

If Playwright browsers aren't installed, run first:
  /opt/anaconda3/bin/playwright install chromium

Or this script will try to use your local Google Chrome.
"""

import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

SCRIPT_DIR = Path(__file__).parent.resolve()
CONTENT_DIR = SCRIPT_DIR / "Content"
OUTPUT_DIR = SCRIPT_DIR / "Post"

POSTS = [
    {"file": "Post0/post0.html", "folder": "Post0"},
    {"file": "Post1/post1.html", "folder": "Post1"},
    {"file": "Post2/post2.html", "folder": "Post2"},
    {"file": "Post3/post3.html", "folder": "Post3"},
    {"file": "Post4/post4.html", "folder": "Post4"},
    {"file": "Post5/post5.html", "folder": "Post5"},
]

CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
]


def find_chrome():
    for p in CHROME_PATHS:
        if os.path.exists(p):
            return p
    return None


def clean_output():
    if OUTPUT_DIR.exists():
        import shutil
        for item in OUTPUT_DIR.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            elif item.is_file():
                item.unlink()
        print("🧹 Cleaned previous exports from Post/\n")


def export_all():
    total = 0
    print("\n🚀 Starting PNG export...\n")

    clean_output()

    chrome_path = find_chrome()

    with sync_playwright() as p:
        if chrome_path:
            print(f"Using local Chrome: {chrome_path}\n")
            browser = p.chromium.launch(
                headless=True,
                executable_path=chrome_path,
            )
        else:
            print("Using Playwright bundled Chromium\n")
            browser = p.chromium.launch(headless=True)

        for post in POSTS:
            html_path = CONTENT_DIR / post["file"]
            if not html_path.exists():
                print(f"  ⚠  Skipping {post['file']} (not found)")
                continue

            out_dir = OUTPUT_DIR / post["folder"]
            out_dir.mkdir(parents=True, exist_ok=True)

            print(f"📂 {post['folder']}/")

            page = browser.new_page(
                viewport={"width": 1200, "height": 10000},
                device_scale_factor=2,
            )
            page.goto(f"file://{html_path}", wait_until="networkidle", timeout=30000)

            page.evaluate("() => document.fonts.ready")
            page.wait_for_timeout(1500)

            page.evaluate("""() => {
                document.querySelectorAll('.toolbar, .slide-label, .btn-sm, .spacer, .divider, .section-title')
                    .forEach(el => el.style.display = 'none');
            }""")

            elements = page.query_selector_all("[data-name]")

            for el in elements:
                name = el.get_attribute("data-name")
                box = el.bounding_box()
                if not box:
                    print(f"   ⚠  {name} — not visible, skipped")
                    continue

                out_path = out_dir / f"{name}.png"

                el.screenshot(
                    path=str(out_path),
                    type="png",
                )

                size_kb = out_path.stat().st_size / 1024
                print(f"   ✅ {name}.png ({size_kb:.0f} KB)")
                total += 1

            page.close()

        browser.close()

    print(f"\n✅ Done! {total} PNGs exported to: {OUTPUT_DIR}\n")
    print("Folder structure:")
    for post in POSTS:
        d = OUTPUT_DIR / post["folder"]
        if d.exists():
            pngs = sorted(f.name for f in d.iterdir() if f.suffix == ".png")
            print(f"  {post['folder']}/ ({len(pngs)} images)")
            for f in pngs:
                print(f"    └─ {f}")


if __name__ == "__main__":
    export_all()
