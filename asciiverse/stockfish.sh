#!/bin/sh
# Builds Stockfish 11, the engine chess-tui plays against, into stage/:
# the binary (stockfish, or stockfish.exe for MinGW), its licence as
# STOCKFISH-COPYING.txt and its AUTHORS as STOCKFISH-AUTHORS. The source is
# the official sf_11 tag, checked against its sha256; dist/ gets a copy of
# that tarball, attached to the release so the GPL source travels with the
# binary (PATCHES.md, Stockfish).
#
#   ARCH=x86-64 asciiverse/stockfish.sh                         # Linux, x86-64
#   ARCH=general-64 asciiverse/stockfish.sh                     # Linux, ARM64
#   ARCH=x86-64 COMP=clang MAKEARGS="arch=x86_64" asciiverse/stockfish.sh   # macOS
#   ARCH=general-64 COMP=clang MAKEARGS="arch=arm64" asciiverse/stockfish.sh # macOS
#   ARCH=x86-64 COMP=mingw CXX=x86_64-w64-mingw32-g++ EXE=.exe \
#     LDEXTRA="-static -Wl,--whole-archive -lwinpthread -Wl,--no-whole-archive" \
#     asciiverse/stockfish.sh                                   # Windows
#
# Stockfish 11 (2020) is the last version without a neural network: a few
# MB instead of about 77, and still far stronger than any human player.
set -eu
cd "$(dirname "$0")/.."
URL=https://github.com/official-stockfish/Stockfish/archive/refs/tags/sf_11.tar.gz
SHA256=802261cc601b67bed00c0ef7d21e2125959630f0852a06db9fc9bd74f440b199
ARCH="${ARCH:-x86-64}"
COMP="${COMP:-gcc}"
EXE="${EXE:-}"
STRIP="${STRIP:-strip}"
# static where the platform allows it (not macOS)
LDEXTRA="${LDEXTRA:--static}"
# Alpine's fortified headers do not survive Stockfish's link-time optimisation
CXXEXTRA="${CXXEXTRA:--U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0}"

mkdir -p build stage dist
tarball=dist/stockfish-11-source.tar.gz
[ -f "$tarball" ] || curl -sSL -o "$tarball" "$URL"
echo "$SHA256  $tarball" | sha256sum -c - 2>/dev/null || echo "$SHA256  $tarball" | shasum -a 256 -c -
rm -rf build/Stockfish-sf_11
tar -xzf "$tarball" -C build
# shellcheck disable=SC2086
make -C build/Stockfish-sf_11/src -j4 build ARCH="$ARCH" COMP="$COMP" ${CXX:+CXX="$CXX"} \
  EXTRACXXFLAGS="$CXXEXTRA" EXTRALDFLAGS="$LDEXTRA" ${MAKEARGS:-}
cp "build/Stockfish-sf_11/src/stockfish$EXE" "stage/stockfish$EXE"
"$STRIP" "stage/stockfish$EXE"
cp build/Stockfish-sf_11/Copying.txt stage/STOCKFISH-COPYING.txt
cp build/Stockfish-sf_11/AUTHORS stage/STOCKFISH-AUTHORS
echo "built stockfish$EXE ($ARCH)"
