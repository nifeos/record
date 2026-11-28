# What the review read and ran

An appendix to [the milestone](../1165-terminal-contract-release-review.md).

## The crate

`partsfoundry/terminal_contract` at `591aed99de4997584efdd74cd34bcb1ac22bd4e1`, version 0.1.0, no
tag, a fresh clone of `main`. The census of milestone 1129 (the combine review) counted it at the
same commit.

The lane read in full: `Cargo.toml`, `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`,
`SECURITY.md`, `docs/stranger-test.md`, `.github/mutants-exempts`, `.github/coverage-exemptions`,
`src/lib.rs` and `src/verification.rs`. It read the names of the seven unit tests in
`src/tests.rs` and not their bodies.

## The commands

Every command ran on a Linux x86_64 host under rustc 1.100.0, with `CARGO_TARGET_DIR` set to a
directory apart from the clone. Afterward `git status --short` printed nothing.

- `cargo build` passes.
- `cargo test` passes: 7 unit tests and 1 doctest.
- `RUSTDOCFLAGS="-D warnings" cargo doc --no-deps` passes with no warning.
- `cargo clippy --all-targets` passes with no warning.
- `cargo build --lib --target x86_64-unknown-none` passes, as the README gives it, and so do
  the builds for `aarch64-unknown-none-softfloat` and `riscv64imac-unknown-none-elf`.
- `cargo package --list --allow-dirty` lists 41 files, 20 of them under `.github/`, `.githooks/`
  or named `.gitignore` (P2-4).
- The crate declares no features, so there is one feature combination.
- `grep -c '^pub const [A-Z]' src/lib.rs` counts 30 constants, and
  `grep -c 'pub const fn\|pub fn' src/lib.rs` counts 6 functions (P0-6). One function, `decode`,
  carries an example and `#[must_use]` (P1-4).
- `grep -n 'forbid' src/lib.rs` finds nothing (P1-5).

A scratch program that depends on the crate by path printed, in a release build:

- `req(257, 5)` is `0x100000000000005`, and `decode` of it is `Some((1, 5))`: operation 257
  became operation 1 (P0-1).
- `req(OPERATION_WRITE, 1 << 32 | 7)` is `0x100000000000007`: the length became 7 (P0-1).
- `admits(OPERATION_QUIESCE, SUPERVISOR_BADGE)`, with its arguments swapped, compiles and is
  false. `admits(RAW_ONLY_BADGE, CTL_QUIT)` and `admits(STDIN_BADGE, NOTE_ABSORBED)` compile and
  are false (P0-1).
- `FLAG_RETRY == NOTE_NOT_WRITTEN` is true. `CTL_RESUME`, `RAW_ONLY_BADGE`, `OPERATION_WRITE`,
  `FLAG_EOF`, `START_HANDOFF` and `NOTE_ABSORBED` are all 1 (P0-1).
- `decode(0)` is `Some((0, 0))`, and `admits(0, 0)` is false. `decode(req(200, 0))` is
  `Some((200, 0))` (P0-2).
- `is_retry(0, FLAG_RETRY)` is true. `is_retry(0, FLAG_RETRY | FLAG_INTERRUPTED)` and
  `is_retry(0, FLAG_RETRY | 1 << 3)` are false (P0-4).
- `decode(req(OPERATION_BYTES, 9))` is `Some((3, 9))` (P0-5).
- `BAD_REQUEST` is 18446744073709551615. `operation(BAD_REQUEST)` is 255 and `len(BAD_REQUEST)`
  is 4294967295 (P0-3, P1-3).
- The low four bytes of `QUIESCED`, most significant first, are `QUIT` (P0-6).

## The search for a comparator

On 2026-11-26 (UTC), `https://crates.io/api/v1/crates?q=<words>&sort=recent-downloads&per_page=8`
for each of: "terminal protocol", "tty no_std", "termios", "pty", "line discipline", "terminal
ipc", "serial console no_std" and "raw mode". No result publishes a terminal protocol over a
message call. "termios" found `termios`, `rustix`, `termion` and `redox_termios`. `termios` and
`redox_termios` publish the words a program and a terminal share, so they rank. `rustix` is a
system call layer; the lane read its `termios` module as the strongest typing of the same words.
The demand appendix of milestone 1129 lists no comparator for this crate.

## The comparators read

Each crate came as its `.crate` file from `static.crates.io`, at the version the block's table
names, into a directory of its own.

- `termios` 0.3.3, the crate page and the list of public items in `src/lib.rs`, and the file
  list of `src/os/`. The root exports the POSIX constants by their C names (`ICANON`, `VMIN`,
  `TCSANOW`) and the functions `tcgetattr`, `tcsetattr`, `cfmakeraw` and their kin, each over a
  `RawFd` and returning `std::io::Result`. `Termios` wraps the C structure and gives it out
  through `Deref`. The crate page carries three examples under "Getting Started". It needs `std`
  and `libc`.
- `redox_termios` 0.1.4, `src/lib.rs` whole. It is `no_std` with no dependency. The words are
  constants of two type aliases, `tcflag_t` and `cc_t`. `Termios` and `Winsize` are `#[repr(C)]`
  structs with public fields, each handed out as bytes through `Deref` and `DerefMut` over
  `slice::from_raw_parts`. `Termios::make_raw` clears the canonical and signal flags. No function
  can fail, and no item carries documentation beyond one constant.
- `rustix` 1.1.6, `src/termios/types.rs` (the struct `Termios`, the four `bitflags` mode types,
  `SpecialCodes`, `SpecialCodeIndex`, `OptionalActions`, `QueueSelector`, `Action` and
  `Winsize`) and the file list of `src/termios/`. Each mode word is a `bitflags` type whose last
  member admits bits the crate does not name. `SpecialCodeIndex` is a newtype over `usize` with
  one associated constant for each code, and `SpecialCodes` indexes by it alone.
  `OptionalActions` is a `#[repr(u32)]` enum with a `#[doc(alias)]` for each C name. `Debug` for
  a control code prints `^C` and not 3.
- `crossterm`, `console`, `vte`, `termion`, `nix` and `embedded-io`: measured, not downloaded,
  not read.

## The systems outside Rust

Each file came from a public mirror at the named commit.

- Fuchsia at `8ff2539fd32def0c2b9ed84b8c8873c31af81d22`,
  `sdk/fidl/fuchsia.hardware.pty/pty.fidl`, whole. `Device` is a closed protocol of strict
  methods. `OpenClient` makes a client with an identifier, and the client with identifier 0
  alone may open others, read events and choose the active client. `ClrSetFeature` takes a mask
  to clear and a mask to set and returns the features in force; `FEATURE_RAW` is the one
  feature. `ReadEvents` returns the pending events (`EVENT_HANGUP`, `EVENT_INTERRUPT`,
  `EVENT_SUSPEND`, `EVENT_WINDOW_SIZE`) and clears them, and `Describe` hands the client an
  event to wait on. `GetWindowSize` and `SetWindowSize` carry a `WindowSize`. Every reply opens
  with a `zx.Result`. The library carries `@available(added=11)`.
- 9front at `d7e009b7866219fa6b2302941b939759ef2c2b68`, `sys/man/8/kbdfs`, the section on
  `cons` and `consctl`. A read of `cons` returns one line once a newline or `^D` ends it, and a
  later read returns the rest of a line a short read left. Writing `rawon` to `consctl` starts
  raw mode, which ends when `rawoff` is written or the file is closed. The lane also fetched
  `sys/man/3/cons`, which no longer describes `consctl`.

## The benchmark

A scratch crate outside the clone depends on `terminal_contract` by path and on nothing else.
The command is `cargo run --release`. The host is Linux x86_64, an Intel Xeon Platinum 8160 at
2.10 GHz with 80 threads, rustc 1.100.0. The benchmark runs on one thread.

Each measurement starts at 64 calls and doubles the count until one pass lasts 50 ms. It then
runs seven passes and reports the lowest, divided by the count. `black_box` wraps the loop
counter, which is the length, and the sum of the results.

| measurement | what a call includes | run 1 | run 2 |
|---|---|---|---|
| `req` | one shift, one mask, one OR | 0.65 ns | 0.74 ns |
| `req`, then `decode` | the above, the reserved-bits test, two field reads | 0.68 ns | 0.73 ns |
| `req`, `decode`, then `admits` | the above through one more `black_box`, and the badge match | 3.69 ns | 3.96 ns |

The block's table gives run 1. The lane ran no comparator: `termios` and `rustix` make a system
call for each operation, and `redox_termios` is constants and two structures.

## What the lane did not run

- Kani and the falsification replay; the harness and patch counts are from the source.
- Mutation testing.
- The build at the minimum Rust version, 1.88.
- Any terminal or client that speaks the words; P1-7 and P2-3 rest on the documentation.
- The tests of the comparators.
