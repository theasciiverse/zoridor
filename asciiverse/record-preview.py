#!/usr/bin/env python3
"""Records asciiverse/zoridor.cast, the catalog preview, at 100x30
(hub/RECORDING.md): you (player 1) against the machine, played through the
game's own controls.

The game's machine player plays without randomness by default, so it always
answers the same position the same way. First the script lets two machine
players play one quick game, off camera, and reads the move record the game
prints at the end. Then it records a normal game against the machine and
plays player 1's side of that record with the keys a person would press:
arrows and Enter for a pawn move; Tab, arrows, Space to turn and Enter for a
fence. The machine answers as it did before, player 1 wins, the next board
comes up with the win counted, and the script quits with q.

The binary is named by bare command, so the cast's header holds no local
path. Needs asciinema 3.x. Usage, from the repo root, with the binary on PATH
or in zig-out/bin:
  python3 asciiverse/record-preview.py
Any extra argument is used as the cast's path instead (for test runs);
DEBUG=1 (with pyte) prints each turn as planned and as the screen shows it.
Run it under a memory cap: systemd-run --user --scope -p MemoryMax=4G ..."""
import base64, fcntl, os, pty, select, struct, sys, termios, time

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cast = sys.argv[1] if len(sys.argv) > 1 else f"{root}/asciiverse/zoridor.cast"
COLS, ROWS = 100, 30
LEFT, RIGHT, UP, DOWN = b"\x1b[D", b"\x1b[C", b"\x1b[A", b"\x1b[B"
env = dict(os.environ, TERM="xterm-256color", LANG="C.UTF-8",
           PATH=f"{root}/zig-out/bin:{os.environ['PATH']}")
for v in ("VTE_VERSION", "TERM_PROGRAM", "TERM_PROGRAM_VERSION", "TMUX", "KITTY_WINDOW_ID"):
    env.pop(v, None)


def spawn(argv):
    pid, fd = pty.fork()
    if pid == 0:
        os.execvpe(argv[0], argv, env)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))
    return pid, fd


def pump(fd, seconds, sink=None):
    end = time.time() + seconds
    while True:
        left = end - time.time()
        r, _, _ = select.select([fd], [], [], max(0.0, min(0.02, left)))
        if r:
            try:
                data = os.read(fd, 65536)
            except OSError:
                return False
            if sink is not None:
                sink.append(data)
        if left <= 0:
            return True


# 1. the machine against itself, to learn the game
pid, fd = spawn(["zoridor", "-1", "machine", "-2", "machine"])
out = []
while pump(fd, 0.2, out):
    if os.waitpid(pid, os.WNOHANG)[0]:
        pump(fd, 0.2, out)
        break
text = b"".join(out).split(b"\x1b[?1049l")[-1].decode()
record = base64.b64decode([l.strip() for l in text.splitlines() if l.strip()][-1])
moves = []
for c in record:
    if c & 0x80:
        moves.append(("pawn", (c & 0x7F) % 9, (c & 0x7F) // 9))
    else:
        cell = (c >> 1) & 0x3F
        moves.append(("fence", cell % 8, cell // 8, "h" if c & 1 else "v"))
assert len(moves) % 2 == 1, "player 1 should make the winning move"
print(f"{len(moves)} moves, player 1 plays {len(moves[0::2])}", file=sys.stderr)

# 2. the recorded game: player 1 by keys, the machine as player 2
pid, fd = pty.fork()
if pid == 0:
    os.execvpe("asciinema", ["asciinema", "rec", "--overwrite", "-q", "--idle-time-limit", "2",
        "--window-size", f"{COLS}x{ROWS}", "--capture-env", "TERM,LANG",
        "--title", "zoridor", "--command", "zoridor -f", cast], env)
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))


screen = None
if os.environ.get("DEBUG"):
    import pyte
    screen = pyte.Screen(COLS, ROWS)
    stream = pyte.ByteStream(screen)


def key(k, wait):
    os.write(fd, k)
    sink = [] if screen else None
    pump(fd, wait, sink)
    if screen:
        stream.feed(b"".join(sink))


def name(m):
    return f"{chr(97 + m[1])}{m[2] + 1}" + (m[3] if m[0] == "fence" else "")


pump(fd, 1.5)
pawn = (4, 0)
for n, m in enumerate(moves[0::2]):
    if m[0] == "pawn":
        x, y = m[1], m[2]
        for _ in range(abs(x - pawn[0])):
            key(RIGHT if x > pawn[0] else LEFT, 0.16)
        for _ in range(abs(y - pawn[1])):
            key(DOWN if y > pawn[1] else UP, 0.16)
        pump(fd, 0.2)
        key(b"\r", 0.8)
        pawn = (x, y)
    else:
        _, x, y, d = m
        key(b"\t", 0.3)          # fence mode: a horizontal fence in the middle
        for _ in range(abs(x - 4)):
            key(RIGHT if x > 4 else LEFT, 0.08)
        for _ in range(abs(y - 4)):
            key(DOWN if y > 4 else UP, 0.08)
        if d == "v":
            key(b" ", 0.2)
        pump(fd, 0.25)
        key(b"\r", 0.85)
    if screen:
        turn = [l.strip() for l in screen.display if "Turn:" in l]
        want = " ".join(name(x) for x in moves[2 * n:2 * n + 2])
        print(f"{n + 1}. want {want}, screen {turn}", file=sys.stderr)
pump(fd, 2.5)                    # the next board, with the win counted
key(b"q", 0.5)
for _ in range(50):
    if os.waitpid(pid, os.WNOHANG)[0]:
        break
    time.sleep(0.2)
