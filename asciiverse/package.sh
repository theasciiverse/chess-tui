#!/bin/sh
# Packs dist/chess-tui-<target>.tar.gz (or .zip for Windows) for av: the
# chess-tui and stockfish binaries at the top, with chess-tui's LICENSE,
# README.md and PATCHES.md, and Stockfish's licence and authors
# (asciiverse/stockfish.sh puts those in stage/).
#
#   asciiverse/package.sh x86_64-unknown-linux-musl target/release/chess-tui
#   EXE=.exe asciiverse/package.sh x86_64-pc-windows-msvc target/release/chess-tui.exe
set -eu
cd "$(dirname "$0")/.."
target="$1"
binary="$2"
EXE="${EXE:-}"
cp "$binary" "stage/chess-tui$EXE"
cp LICENSE README.md PATCHES.md stage/
mkdir -p dist
if [ -n "$EXE" ]; then
  # Git Bash on Windows runners has 7-Zip rather than zip
  if command -v zip >/dev/null; then
    (cd stage && zip -qr "../dist/chess-tui-$target.zip" .)
  else
    (cd stage && 7z a -tzip -bso0 "../dist/chess-tui-$target.zip" .)
  fi
else
  tar -czf "dist/chess-tui-$target.tar.gz" -C stage .
fi
ls dist
