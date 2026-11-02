# Changes from upstream

This is the Asciiverse packaging of [Zoridor](https://github.com/ringtailsoftware/zoridor)
by Ringtail Software (Toby Jaffey, MIT), built from upstream's main as of
`960df4f` (17 January 2025). Upstream has no releases; its manifest says
0.0.0, so our tags read `v0.0.0+20250117-av.<n>`. Upstream is the
`upstream` remote; the `asciiverse` branch carries the changes below.

## Code

- **Builds with Zig 0.14.0.** Upstream followed Zig's development branch
  in January 2025, and neither 0.13.0 nor 0.14.0 built it: 0.14.0 wants
  the package named by an enum literal with a fingerprint, and the pinned
  yazap commit predates 0.14.0's stricter optionals. `build.zig.zon` now
  has the 0.14.0 form and yazap v0.6.3, its release for 0.14.0.
- **A fence is checked again after turning it.** Space turned the fence
  but kept the legality verdict of the old direction, so the colour and
  Enter were wrong: a legal turned fence was refused, and an illegal one
  (overlapping a fence already placed) was accepted, after which the game
  panicked. Worth offering upstream.
- **`-s` takes effect, and without it the seed comes from the clock.** The
  option was registered as `seedrand` but read as `randseed`, and the
  generators were seeded when the players were made, before the command
  line was read, from a clock that had just started at zero; so `-r` and
  the random player made the same choices on every run. They are now
  seeded on first use. Worth offering upstream.
- **The terminal comes back as it was.** The game drew on the normal
  screen, and on exit painted it blue, left colours set and printed the
  move record over the board; a terminal too small got the same over the
  message saying so. It now uses the alternate screen, resets colours on
  exit and checks the size before taking over the terminal (exit status 1
  if too small). The move record still prints after the game, on the
  normal screen. Worth offering upstream.

## Packaging

- `.github/workflows/release.yml` (new): av archives for Linux (static,
  x86-64 and ARM64) and macOS 11 and later (x86-64 and ARM64), all
  cross-compiled by Zig 0.14.0 on one runner, plus SHA256SUMS, and .deb,
  .rpm, .apk and Arch packages. No Windows: the mibu terminal library is
  POSIX only.
- `.github/workflows/build.yml` (removed): upstream's CI, which builds with
  Zig's development branch and deploys the web version to GitHub Pages.
- `asciiverse/nfpm.yaml` (new): the system packages.
- `asciiverse/record-preview.py` (new): records the catalog preview, a game
  against the machine played through the keys.

## Ours

- **How to play it, at the top of README.md.** A short note on installing
  and starting it with av; the original text follows unchanged.
