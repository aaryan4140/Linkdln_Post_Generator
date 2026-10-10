#!/bin/bash
# ============================================
# LinkedIn Post Production — Master Runner
# ============================================
#
# Usage:
#   ./run.sh              → Export PNGs + create GIFs/MP4s
#   ./run.sh export       → Export PNGs only
#   ./run.sh gif          → Create GIFs/MP4s only
#   ./run.sh gif Post0    → Single post GIF/MP4
#
# To create NEW posts:
#   Open Claude Code → "Create posts from Docs/filename.md"
#   Then run ./run.sh to export everything
# ============================================

PYTHON="/opt/anaconda3/bin/python3"
DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "============================================"
echo "  LinkedIn Post Production Pipeline"
echo "============================================"
echo ""

case "${1:-all}" in

  export)
    echo "📸 Exporting PNGs..."
    echo ""
    $PYTHON "$DIR/export_all.py"
    ;;

  gif)
    if [ -n "$2" ]; then
      echo "🎬 Creating GIF + MP4 for $2..."
      echo ""
      $PYTHON "$DIR/create_gif.py" "$2"
    else
      echo "🎬 Creating GIFs + MP4s for all posts..."
      echo ""
      $PYTHON "$DIR/create_gif.py"
    fi
    ;;

  all)
    echo "STEP 1: Exporting PNGs..."
    echo "--------------------------------------------"
    $PYTHON "$DIR/export_all.py"

    echo ""
    echo "STEP 2: Creating GIFs + MP4s..."
    echo "--------------------------------------------"
    $PYTHON "$DIR/create_gif.py"

    echo ""
    echo "============================================"
    echo "  All done!"
    echo "============================================"
    echo ""
    echo "  PNGs   → $DIR/Post/"
    echo "  GIFs   → $DIR/animated GIF/"
    echo "  MP4s   → $DIR/animated GIF/"
    echo ""
    ;;

  *)
    echo "Usage:"
    echo "  ./run.sh              Run everything (PNGs + GIFs + MP4s)"
    echo "  ./run.sh export       Export PNGs only"
    echo "  ./run.sh gif          Create GIFs + MP4s for all posts"
    echo "  ./run.sh gif Post0    Create GIF + MP4 for a single post"
    echo ""
    echo "To create NEW posts:"
    echo "  Open Claude Code → 'Create posts from Docs/filename.md'"
    echo "  Then run ./run.sh"
    echo ""
    ;;

esac
