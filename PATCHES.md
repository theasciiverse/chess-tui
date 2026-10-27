# Changes from upstream

This is the Asciiverse packaging of [chess-tui](https://github.com/thomas-mauran/chess-tui)
by Thomas Mauran and contributors: chess in the terminal (Rust and
Ratatui), against a friend on the same computer or over the network,
against a chess engine, or on Lichess. Upstream is the `upstream` remote;
the `asciiverse` branch carries the changes below.

Built from upstream `main` at `58b3f5e` (2026-10-17), 49 commits after
its latest release, 2.7.1 (2026-05-21). The catalog title is "chess-tui",
the project's own name.

## Licence

MIT (LICENSE, Thomas Mauran). Stockfish, shipped beside it (below), is
GPL-3.0-or-later; it is a separate program that chess-tui starts and talks
to over UCI, so the two keep their own licences.

## Stockfish

chess-tui plays against any UCI engine but ships none; upstream asks for
an engine path on first use. Our archives carry Stockfish 11 (2020, the
last version without a neural network: about 1.5 MB, where Stockfish 19
is about 77 MB a platform, and still far stronger than any human player),
built by `asciiverse/stockfish.sh` from the official `sf_11` tag
(`https://github.com/official-stockfish/Stockfish/archive/refs/tags/sf_11.tar.gz`,
sha256 `802261cc601b67bed00c0ef7d21e2125959630f0852a06db9fc9bd74f440b199`),
unchanged: static `x86-64` for x86-64 Linux, `general-64` for ARM64 Linux
and Apple silicon (Stockfish 11 has no ARM64 or Apple silicon target of
its own), MinGW for Windows. Each archive has Stockfish's licence
(`STOCKFISH-COPYING.txt`) and authors (`STOCKFISH-AUTHORS`), and each
release has the source tarball itself, `stockfish-11-source.tar.gz`.

chess-tui's difficulty presets ask the engine for 400, 900, 1500 and 2700
Elo. Stockfish 11 accepts 1350 to 2850 (Stockfish 19, 1320 to 3190), and
both ignore a value out of range, so Easy and Medium are made easier only
by the presets' short search (depth 1 and 4, 25 and 120 ms). That is as
upstream, with any Stockfish.

## Saved files

Configuration, skins, logs and saved games are in `dirs::config_dir()`'s
`chess-tui` folder (`~/.config/chess-tui` on Linux, `~/Library/Application
Support/chess-tui` on macOS, `%APPDATA%\chess-tui` on Windows). Nothing to
change.

## Code

Written to be offered upstream as a pull request:

- **feat: find Stockfish beside chess-tui or on the PATH when no engine is
  set.** With no engine path in the config or on the command line,
  chess-tui looks for `stockfish` (`stockfish.exe` on Windows) next to its
  own binary, as in a package that ships both, and then in each directory
  of the `PATH`. A configured or `-e` path still wins; nothing is written
  to the config.

## Packaging

- Upstream's workflows (build and test, lint, its releases, Docker,
  crates.io, the website, the blog post generator) and Dependabot are
  removed in this fork.
- `.github/workflows/release.yml`: av archives `chess-tui-<target>` for
  Linux (static, built in Alpine, x86-64 and ARM64, without the sound
  feature, as rodio links ALSA), macOS (x86-64 and ARM64) and Windows
  (x86-64, MSVC, with a MinGW Stockfish), each with `chess-tui`,
  `stockfish`, LICENSE, README.md, this file and Stockfish's licence and
  authors; plus SHA256SUMS and the Stockfish source. Runs on our tags only
  (`*-av.*`).
- `asciiverse/stockfish.sh` and `asciiverse/package.sh` do the building
  and packing for the workflow and by hand.
- `asciiverse/drive.py` records the catalog preview,
  `asciiverse/chess-tui.cast`: Play Bot as White against the shipped
  Stockfish at full strength, White's moves chosen by the same binary at
  Skill Level 3 and typed through the move box, the game read back from
  the History panel (python-chess). The catalog's take is 12 moves with
  three captures, the best of six.

## Checked

Linux, static build (Alpine, rustc 1.99): upstream's 149 tests pass with
the change; with Stockfish 11 beside it, a fresh home and nothing on the
`PATH`, Play Bot shows the engine found and Stockfish answers (it opened
1. e4 as White). Stockfish 11 builds static on Alpine (fortify off for its
link-time optimisation) and answers UCI for x86-64 and `general-64`.
Windows: chess-tui cross-built for x86_64-pc-windows-gnu (with sound) and
Stockfish with MinGW; Stockfish answers UCI under Wine, and chess-tui
starts there, but Wine's console mangles the screen, so finding the engine
on Windows is not confirmed here. macOS: not built here.

## Ours

- **How to play it, at the top of README.md.** A short note on installing and
  starting it with av, or from a release archive; the original text follows
  unchanged.
