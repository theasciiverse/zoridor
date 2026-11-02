# Zoridor (Asciiverse packaging)

Ringtail Software's Quoridor in Zig (mibu for the terminal, yazap for
options); packaged for the Asciiverse catalog and as system packages. Not
our code: keep changes small, list every one in PATCHES.md, and offer
fixes upstream.

- Remotes: `upstream` is github.com/ringtailsoftware/zoridor, `origin` is
  github.com/theasciiverse/zoridor.
- Branch `asciiverse` = upstream main plus our commits. Upstream has no
  releases (0.0.0), so tags carry the upstream commit's date:
  `v0.0.0+20250117-av.1`.
- Needs Zig 0.14.0 exactly (the CI pins it with its sha256). Local static
  build: `docker run --rm --memory=4g -v "$PWD":/src -v <zig-0.14.0>:/zig:ro
  -w /src alpine:3 /zig/zig build -Doptimize=ReleaseSafe
  -Dtarget=x86_64-linux-musl` (as root, then chown `zig-out/` and
  `.zig-cache/`); `zig build test` runs upstream's unit tests.
- Run tests and recordings under `systemd-run --user --scope -p
  MemoryMax=4G`.
- No Windows build: mibu is POSIX only.
- Needs 80x29 (80x24 with `-m`); draws a fixed 80 by 29 screen at the top
  left. Keys: arrows and Enter move the pawn, Tab switches to a fence,
  Space turns it, q quits. Saves nothing; prints the game's moves (and a
  base64 record `-l` loads) after a game.
- The machine player uses no randomness unless `-r` is given, so it always
  answers a position the same way; the preview script relies on that.
