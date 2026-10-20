#!/usr/bin/env python3
"""Records asciiverse/chess-tui.cast, the catalog preview, at 100x30.

Usage: drive.py <folder with chess-tui and stockfish> <out.cast> [seconds]

Needs tmux, asciinema 3 and python-chess (`pip install python-chess`).

asciinema rec runs `chess-tui` (by name, from a throwaway folder on PATH,
with a throwaway home) in a detached 100x30 tmux session, with Stockfish
beside it, so chess-tui finds the engine itself. This script opens Play
Game, Play Bot, and starts a game as White against the engine at full
strength (depth 10). Its own moves come from the same Stockfish binary,
asked for a weaker move (Skill Level 3, depth 6), so the game lasts: each
is typed through chess-tui's move box (m, the move in algebraic notation,
Enter). The game so far is read back from chess-tui's History panel. After
`seconds` (default 45), or when the game ends, it quits with q."""
import os, re, shutil, subprocess, sys, tempfile, time

import chess

folder, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
secs = float(sys.argv[3]) if len(sys.argv) > 3 else 45.0

S = f"chess-tui-preview-{os.getpid()}"
TMUX = ["tmux", "-L", S]
home = tempfile.mkdtemp()
# the binaries in a folder named chess-tui, as av installs them, since Play
# Bot shows the engine's path (".../chess-tui/stockfish")
bindir = os.path.join(home, "chess-tui")
os.mkdir(bindir)
for name in ("chess-tui", "stockfish"):
    shutil.copy(os.path.join(folder, name), os.path.join(bindir, name))
env = dict(os.environ, HOME=home, PATH=bindir + ":" + os.environ["PATH"],
           XDG_CONFIG_HOME=os.path.join(home, ".config"),
           TERM="xterm-256color", COLORTERM="truecolor", LANG="C.UTF-8",
           USER="player", LOGNAME="player")
for k in ("VTE_VERSION", "TERM_PROGRAM", "TERM_PROGRAM_VERSION", "TMUX"):
    env.pop(k, None)

def key(*k):
    subprocess.run(TMUX + ["send-keys", "-t", S, *k])

def screen():
    return subprocess.run(TMUX + ["capture-pane", "-p", "-t", S],
                          capture_output=True, text=True).stdout

def running():
    return subprocess.run(TMUX + ["has-session", "-t", S], capture_output=True).returncode == 0

PIECE = "♙♘♗♖♕♔♟♞♝♜♛♚"
MOVE = re.compile("[" + PIECE + r"] (\S+)")

def history():
    """The moves in the History panel, in order (its rows hold a White and
    a Black move each)."""
    moves = []
    inside = False
    for line in screen().split("\n"):
        if "History" in line:
            inside = True
            continue
        if inside:
            if "╰" in line:
                break
            moves += MOVE.findall(line)
    return moves

class Engine:
    """Our own Stockfish, for White's moves."""
    def __init__(self, path):
        self.p = subprocess.Popen([path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        self.send("uci"); self.wait("uciok")
        self.send("setoption name Skill Level value 3")
        self.send("isready"); self.wait("readyok")
    def send(self, line):
        self.p.stdin.write(line + "\n"); self.p.stdin.flush()
    def wait(self, word):
        while True:
            line = self.p.stdout.readline()
            if line.startswith(word):
                return line
    def move(self, board):
        self.send("position fen " + board.fen())
        self.send("go depth 6")
        return chess.Move.from_uci(self.wait("bestmove").split()[1])
    def quit(self):
        self.send("quit")

cmd = ("env TERM=xterm-256color asciinema rec --overwrite -q --window-size 100x30 --idle-time-limit 2"
       " --title chess-tui --capture-env TERM,COLORTERM,LANG -c chess-tui " + out)
subprocess.run(TMUX + ["new-session", "-d", "-s", S, "-x", "100", "-y", "30",
                       "-c", home, cmd], env=env, check=True)
engine = Engine(os.path.join(bindir, "stockfish"))
try:
    time.sleep(2.5)
    # Play Game, Play Bot; Enter through the form (it starts as White)
    key("Enter"); time.sleep(1.5)
    key("Down"); time.sleep(0.6); key("Down"); time.sleep(1.2)
    for _ in range(8):
        key("Enter"); time.sleep(1.0)
        if "Game setup" not in screen():
            break
    time.sleep(1.5)
    t0 = time.time()
    while running() and time.time() - t0 < secs:
        board = chess.Board()
        for san in history():
            try:
                board.push_san(san)
            except ValueError:
                break
        if board.is_game_over() or board.turn != chess.WHITE:
            time.sleep(0.5)
            if board.is_game_over():
                break
            continue
        san = board.san(engine.move(board))
        # open the move box, type the move a key at a time, play it, close
        key("m"); time.sleep(0.6)
        for ch in san:
            key(ch); time.sleep(0.18)
        time.sleep(0.5); key("Enter")
        before = len(board.move_stack)
        for _ in range(40):
            time.sleep(0.25)
            key("Escape") if "Input a move" in screen() else None
            if len(history()) >= before + 2:
                break
        time.sleep(1.2)
    time.sleep(2.0)
    key("Escape"); time.sleep(0.3); key("q")
    for _ in range(50):
        if not running():
            break
        time.sleep(0.1)
finally:
    engine.quit()
    subprocess.run(TMUX + ["kill-server"], capture_output=True)
    shutil.rmtree(home, ignore_errors=True)
