# What the review read and ran

An appendix to [the milestone](../1154-boot-ladder-release-review.md).

## The crate

`partsfoundry/boot_ladder` at `019d76c8e5b64d44c7eb863008c4fa16b89602d8`, version 0.1.0,
`publish = false`. Read in full: `Cargo.toml`, `README.md`, `CHANGELOG.md`,
`docs/stranger-test.md`, the `ci`, `proofs` and `ruled` workflow callers under
`.github/workflows/`, and all four files under `src/` (`lib.rs`, `heads.rs`, `rungs.rs`, `verdict.rs`), tests and
the two Kani harnesses included. The baseline read: milestone 1078's block, its prior-art
appendix and the cleared package.

## The commands

Run on a Linux x86_64 host with rustc 1.100.0, with the build directory outside the clone.

- `cargo build` and `cargo clippy --all-targets` pass with no warning.
- `cargo test` passes: 19 unit tests and 2 documentation tests, both from the README.
- `cargo doc --no-deps` passes with no warning.
- `cargo build --lib --target <t>` passes for `x86_64-unknown-none`,
  `aarch64-unknown-none-softfloat` and `riscv64imac-unknown-none-elf`.
- `cargo package --list --allow-dirty` lists 41 files, 18 of them under `.github/` (P1-4).
- `grep -c must_use src/*.rs` prints 0 for each file, and no doc comment under `src/` opens a
  code block (P1-2, P2-5).
- The crate has no features, so there is one combination.
- `git status --short` in the clone printed nothing afterward.

## The probe

A scratch binary that depends on the crate by path, run in a debug and a release build. What it
printed:

| call | result |
|---|---|
| `parse("99 of 3 passed")` | passed 99, total 3, not red |
| `parse("1 of 2 passed, 5 FAILED: a")` | failed count 5, one name |
| `parse("1 of 2 passed, 1 FAILED: a  b")` | failed count 1, names `a` and `b` |
| `parse("0 of 0 passed")` | passed 0, total 0, not red |
| `parse("2 of 3 passed, 1 FAILED: not_a_check")` | accepted, since names are not checked against the list |
| `parse("3 of 3 passed, 0 FAILED: ")`, `parse("1 of 2 passed, 1 FAILED: a, 1 absent: b")`, `parse("3 of 3 passed and more")`, a count of 2 to the 64th | `None` each |
| `parse("3 of 3 passed\r\n")` | accepted; trailing white space is trimmed |
| `record(20, Passed)` on a full tally | prints `16 of 15 passed`; `from_words(to_words())` differs from the tally |
| `record(64, Failed)` | debug: panics, attempt to shift left with overflow; release: words `[0, 1, 0]`, check 0 failed |
| `is_recorded(64)` | debug: the same panic; release: `false` |
| `Heads::new("").banner().find_in("the cat sat on the mat")` | `Some(11..15)` |
| `subject_thread` on a 20-digit thread number | `None` |

The index in `record` is the caller's own constant, and every text the reader takes ends in
`None` or a value, so the probe found nothing a hostile transcript can turn into a panic.

## The benchmark

A scratch crate that depends on `boot_ladder` by path and on `expectrl` at `=0.9.0`, built with
`cargo run --release` on a Linux x86_64 host (an Intel Xeon Platinum 8160 at 2.10 GHz). Each measurement starts at 64 repeats and doubles until a pass lasts 50
ms, then runs seven passes and reports the lowest time divided by the count. Inputs and results
pass through `std::hint::black_box`. The three texts:

- one verdict line of 86 bytes: a replacement character, then
  `example self-test: 12 of 15 passed, 2 absent: block_device clock, 1 FAILED: entropy`;
- a transcript of 65,687 bytes: 80-byte lines that each hold the name `example` without the
  shape, and the verdict line last;
- 4,096 bytes of `a`, searched for the head of the name `aaaaaaaa`, which is absent.

The `Head::find_in` column times the call alone. The `str::find` column searches for the head
joined into a `String` before the timed loop. The `expectrl` column calls `Needle::check` on the
joined `str` with the text as bytes, and includes the `Vec` of matches it returns. The harness
asserts that `find_in` and `str::find` agree on each text before it times them. The results are
in [the comparison](comparison.md#the-benchmarks-results).

## The comparators read

The six neighbor crates of `boot_ladder`, each downloaded as a `.crate` file at the version the
prior-art table gives and read in a directory of its own.

- `sd-notify` 0.5.0, `src/lib.rs`: `NotifyState` is an enum of states with `Display`
  (`READY=1`, `STATUS=...`), `notify` sends them, and nothing parses one; `Custom(&str)` prints
  any text. The enum derives `Clone` and `Debug` and is exhaustive. The crate page opens with an
  example. It needs `std`.
- `expectrl` 0.9.0, `src/needle.rs`: the `Needle` trait is
  `check(&self, buf: &[u8], eof: bool) -> Result<Vec<Match>, Error>`, implemented for `str`,
  `[u8]`, `Regex`, `Eof`, `NBytes` and `Any`. The needle is whatever the caller passes. The crate
  page (`src/lib.rs`) opens with examples.
- `rexpect` 0.7.2, `src/reader.rs` and `src/session.rs`: `ReadUntil` is an enum of `String`,
  `Regex`, `NBytes` and others; `exp_string` and `exp_regex` take the needle from the caller and
  return owned `String`s.
- `embedded-test` 0.7.3, `src/lib.rs` and `src/export.rs`: a sealed `TestOutcome` trait over `()`
  and `Result`; `check_outcome` reports a test to the host by a semihosting exit or abort, not by
  a console line. `no_std`, with features for `defmt`, `log` and several executors.
- `testanything` 0.4.3, `src/tap_test.rs`, `src/tap_suite.rs` and `src/tap_writer.rs`: a TAP
  writer whose `TapTest` holds a `String` name, a `bool` and a `Vec<String>` of diagnostics, and
  whose `status_line` returns a new `String`.
- `tap_parser` 0.1.1, `src/lib.rs`: `TapParser` reads a `&str` into `Vec<TapStatement>`,
  borrowing descriptions; it requires `TAP version 14` on the first line, counts tests against
  the plan, and returns an `Error` of eleven variants derived with `thiserror`.
- `libtest-mimic` 0.8.2: measured, not read.

Seventeen crates.io queries found no peer. Among them were `ktap`, `boot log`, `boot stage`,
`bootstage`, `self-test`, `serial console expect`, `console harness`, `log matcher`,
`tap parser`, `tap producer` and `test output parser`. The names `ktest` 0.1.6 (50 downloads in
90 days) and `kunit` 0.1.1 (6) are test runners for Rust kernels, too small to rank.

## The systems outside Rust

- Linux v6.12, `Documentation/dev-tools/ktap.rst`: the format has version lines
  (`KTAP version 1`), plan lines (`1..N`), result lines
  (`<result> <number> [<description>][ # [<directive>] [<diagnostic data>]]`) and diagnostic
  lines, and it expects parsers to accept `TAP version 13` and `TAP version 14` too.
- Linux v6.12, `tools/testing/kunit/kunit_parser.py`. `extract_tap_lines` measures the prefix
  before the version line and cuts it from every later line. `check_version` records an error for
  a version outside the accepted lists. `parse_test_result` records an error when a result's
  number is not the expected one. `parse_test` records `missing expected subtest!` and
  `missing subtest result line!`. `TestStatus` has `SUCCESS`, `FAILURE`, `SKIPPED`,
  `TEST_CRASHED`, `NO_TESTS` and `FAILURE_TO_PARSE_TESTS`.

Both files are GPL-2.0; the review read them for their interface shape only.

## What was not run

- Kani and mutation testing; the harness count, two, is from source.
- No comparator's own tests, and no comparator but `expectrl`'s `Needle::check` was executed.
- No boot of any system that prints these lines.
- `cargo +1.88`, the stated minimum Rust version.
