# What the review read and ran

An appendix to [the milestone](../1140-line-editor-release-review.md).

## The crate

`partsfoundry/line_editor` at `2c625ef614fe84da91a712aa258d54f3810663d0`, version 0.1.0 with
`publish = false`, read in full: `src/lib.rs`, `src/line_disc.rs`, `src/output.rs`,
`src/raw_queue.rs`, `src/handoff.rs`, `Cargo.toml`, `README.md`, `CHANGELOG.md` and the fuzz
targets.

## The measurements

`GET /api/v1/crates/<name>` and `GET /api/v1/crates/<name>/reverse_dependencies` on crates.io,
2026-11-26 (UTC), with a generic User-Agent. The 90-day figure is the API's `recent_downloads`.

## The comparators read

Each `.crate` from crates.io at the version in the prior-art table, unpacked and read, not run.

- `noline` 0.5.1: `Line::advance(byte) -> Option<Output>`, the editor over caller slices or over
  an allocator, UTF-8 cells, `NolineError { ParserError, Aborted, IoError(embedded_io::ErrorKind) }`,
  features `alloc` and `std`, sync and async front ends over `embedded_io::Read + Write`.
- `embedded-cli` 0.2.1: `process_byte` over a `Buffer` trait the caller sizes, output through
  `embedded_io::Write` and `ufmt`, features `autocomplete`, `help`, `history` and `macros`.
- `menu` 0.6.1: `Runner::input_byte(u8)` over `embedded_io::Write`.
- `rustyline` 19.0.0: `ReadlineError` with `Eof` and `Interrupted` as variants, and the
  `Helper` traits for completion, hints and highlighting.

## Not run

- The benchmark, for the reason the block gives.
- No comparator was built.
