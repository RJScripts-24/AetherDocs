#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Add FFmpeg if it's missing (Render's native environment often lacks it)
# We download a static build to avoid sudo/apt-get issues
FFMPEG_DIR="$HOME/ffmpeg_bin"
mkdir -p "$FFMPEG_DIR"

if [ ! -f "$FFMPEG_DIR/ffmpeg" ]; then
    echo "--- Downloading FFmpeg ---"
    cd "$FFMPEG_DIR"
    curl -L https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz | tar -xJ --strip-components=1
    chmod +x bin/ffmpeg bin/ffprobe
    mv bin/ffmpeg bin/ffprobe .
    rm -rf bin doc presets share
    cd -
fi

# Add FFmpeg to PATH for the current process and future starts
export PATH="$FFMPEG_DIR:$PATH"

echo "--- Build Complete ---"
