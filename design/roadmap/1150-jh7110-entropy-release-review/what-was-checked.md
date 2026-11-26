# What the review read and ran

An appendix to [the milestone](../1150-jh7110-entropy-release-review.md).

## The crate

`partsfoundry/jh7110_entropy` at `eac91efd0381cc4cd7556a53e512bcfb2eeaaf17`, version 0.3.0-pre.2,
edition 2024, `rust-version` 1.85, no dependencies and no features. Read in full: `Cargo.toml`,
`README.md`, `CHANGELOG.md` and `src/lib.rs` up to its test module. Read for their shape only:
the 28 unit tests of `src/lib.rs` and the eight Kani harnesses of `src/verification.rs`. Listed
and not read: `docs/` and `falsifications/`. The crate has no `examples/`, `tests/` or `fuzz/`
directory.

## The commands

The review ran each command in a copy of the clone on a Linux x86_64 host, with rustc 1.100.0
and the build directory outside the copy.

- `cargo build` passes.
- `cargo test`: 28 unit tests and 3 doctests pass.
- `cargo +1.85 test`, the declared minimum: the same 28 and 3 pass.
- `cargo doc --no-deps`, and again with `RUSTDOCFLAGS="-D warnings"`: both pass.
- `cargo clippy --all-targets` passes with no warning.
- `cargo build --lib --target riscv64imac-unknown-none-elf`, `aarch64-unknown-none-softfloat` and
  `x86_64-unknown-none`: all pass.
- `cargo package --list --allow-dirty` lists 19 files: the manifest and lock files, the README,
  the changelog, the two licenses, one file of `docs/`, the eight falsification patches and the
  two source files. No repository scaffolding is in the list.
- `grep -n must_use src/lib.rs` finds two lines, on `Pool::new` and `Pool::remaining_bytes`
  (P1-3).
- `grep -rn 'pool ==\|== Pool' src` finds nothing: no test or proof compares two pools (P0-5).
- `grep -n Discovered src/lib.rs` finds the declaration and one mention in the crate
  documentation, and no function signature (P0-4).
- The crate has no features, so there is no feature combination to build.

## The comparators read

The review took each crate's `.crate` file from crates.io at the version the prior-art table
gives and unpacked it into a directory of its own. The download figures are the crates.io API's
on 2026-11-26 (UTC), asked for under the User-Agent `release-review-lane`. The searches were `jh7110`, `starfive`, `trng`,
`hwrng`, `true random number generator`, `rng driver` and `hardware rng`, sorted by recent
downloads.

- `rdrand` 0.9.0: `RdRand` and `RdSeed` (`src/lib.rs`) are unit-like structs made by `new() ->
  Result<Self, ErrorCode>` or `unsafe fn new_unchecked`. Both implement `rand_core` 0.10's
  `TryRng` with `type Error = ErrorCode`, and `TryCryptoRng`. `ErrorCode` (`src/errors.rs`) has
  `UnsupportedInstruction` and `HardwareFailure`, derives `Debug`, `Copy` and `Clone`, and
  implements `Display` and `core::error::Error`. One feature, `std`. License ISC.
- `esp-hal` 1.2.3: `rng::Rng` (`src/rng/mod.rs`) derives `Clone`, `Copy`, `Default` and `Debug`
  and has `random() -> u32` and `read(&self, buffer: &mut [u8])`, neither fallible.
  `rng::Trng` (`src/rng/trng.rs`) is made by `try_new() -> Result<Self, TrngError>` while a
  `TrngSource` lives; `TrngError` is `#[non_exhaustive]`. Both implement `RngCore` of `rand_core`
  0.6 and 0.9 and `TryRng` of 0.10 with `Error = Infallible`. The three optional dependencies are
  `rand_core-06`, `rand_core-09` and `rand_core-010`, turned on by the `unstable` feature.
- `embassy-stm32` 0.6.0: `rng::Rng<'d, T>` (`src/rng.rs`) owns the peripheral. It has
  `async_fill_bytes(&mut self, dest: &mut [u8]) -> Result<(), Error>`, blocking `next_u32`,
  `next_u64` and `fill_bytes`, and `reset` and `recover_seed_error`. `Error` has `SeedError` and
  `ClockError` and implements neither `Display` nor `core::error::Error`. It implements `RngCore`
  and `CryptoRng` of `rand_core` 0.6 and 0.9, through dependencies renamed `rand-core-06` and
  `rand-core-09`.
- `jh71xx-pac` 0.11.1: `trng::RegisterBlock` (`src/trng.rs`) is `#[repr(C)]` with `ctrl`, `stat`,
  `mode`, `smode`, `ie`, `istat`, eight `rand`, `auto_rqsts` and `auto_age`, and reserved bytes
  from `0x18` to `0x1F` and from `0x40` to `0x5F`; it ends at `0x68`. `Istat` implements `Readable` only
  (`src/trng/istat.rs`). `ctrl` has three one-bit fields, `exec_nop`, `gen_rand` and `reseed`, at
  bits 0, 1 and 2 (`src/trng/ctrl.rs`). `stat` gives `last_reseed` as eight one-bit fields at
  bits 16 to 23 (`src/trng/stat.rs`), where the crate under review has a three-bit field at bit
  16. `Peripherals::trng` points at `0x1600_c000` (`src/lib.rs`). GPL-3.0-only.
- `jh71xx-hal` 0.7.2: modules for clocks, DDR memory, delay, GPIO, I2C, the card controller, the
  phase-locked loops, PWM, SPI and the UART under `src/`, and none for the generator.
  GPL-3.0-only.
- `nrf-hal-common` 0.19.0: `rng::Rng` (`src/rng.rs`) owns the peripheral, has `random(&mut self,
  buf: &mut [u8])` and four integer methods, none fallible, and implements `RngCore` and
  `CryptoRng` of `rand_core` 0.9.
- `virtio-drivers` 0.13.0: `VirtIORng<H, T>` (`src/device/rng.rs`) owns its transport and has
  `request_entropy(&mut self, dst: &mut [u8]) -> Result<usize>`.
- `rand_core` 0.10.1: `TryRng` (`src/lib.rs`) has `type Error: core::error::Error`,
  `try_next_u32`, `try_next_u64` and `try_fill_bytes(&mut self, dst: &mut [u8]) -> Result<(),
  Self::Error>`; `Rng` is its infallible form, and `TryCryptoRng` a marker. `block::Generator`
  (`src/block.rs`) has `generate(&mut self, output: &mut Self::Output)` and a `drop` hook for
  the output buffer. `block::BlockRng<G>` derives `Clone`, has a `Debug` that leaves out its
  results, and has `next_word`, `next_u64_from_u32` and `fill_bytes`.

## The systems outside Rust

- Linux v6.12, `drivers/char/hw_random/jh7110-trng.c` (397 lines, fetched from the tagged raw
  address; SHA-256 `1cc7ced32bca61dd21e0b2c98c6cf423ac8f253235fc27ea19b6b007c591cc7f`).
  `struct starfive_trng` holds the base, two clocks, the reset and two completions.
  `starfive_trng_wait_idle` polls `STAT` until neither `RAND_GENERATING` nor `RAND_SEEDING` is
  set. `starfive_trng_cmd` writes `STARFIVE_CTRL_GENE_RANDNUM` (1) or
  `STARFIVE_CTRL_EXEC_RANDRESEED` (2) to `CTRL` and waits for a completion, up to 1 ms, or 40
  microseconds when the caller will not wait. `starfive_trng_init` writes the two automatic reseed
  registers, clears `ISTAT`, enables the interrupts, sets the output width and reseeds.
  `starfive_trng_irq` acknowledges each `ISTAT` bit by writing it back and reseeds on
  `LFSR_LOCKUP`. `starfive_trng_read` clamps to 32 or 16 bytes by the mode, issues a generate and
  copies with `memcpy_fromio`. The file defines `STARFIVE_STAT_SEEDED` and never reads it. GPL;
  read for its interface shape only.

## The benchmark

A scratch crate depending on the crate's copy by path and on `rand_core = "=0.10.1"`, built with
`cargo build --release` and run three times. The source of both sides is one counter that adds
`0x9E37_79B9` for each of eight `u32` words, passed through `black_box`. Each row starts at 64
repeats and doubles until a pass lasts 50 ms. It then runs seven passes and reports the lowest
divided by the repeats, with `black_box` on the output slice and on each result.

- `Pool` into a slice: `Pool::take_into` on a slice of 8, 32 or 1024 bytes. The generator calls
  `generation_outcome` on a seeded, ready, 256-bit snapshot of the counter's words and returns the
  bytes of `Ready`. The figure includes that decode, the copy and the zeroing of each byte.
- `BlockRng` into a slice: `BlockRng::fill_bytes` on a slice of the same length, over a
  `Generator` with `Output = [u32; 8]` that stores the counter's words.
- One `u64`: `Pool::take(8, ..)` with a generator that returns `output_bytes` of the counter's
  words, against `BlockRng::next_u64_from_u32`.
- `generation_outcome` alone: one call on the ready snapshot, with `black_box` on each argument.

The per-byte figure in the block is the 1024-byte row divided by 1024.

## What was not run

- No benchmark on the device: the host figures measure the pool and the decode against memory.
- No benchmark of a ranked comparator: `rdrand` measures a processor instruction, and `esp-hal`
  and `embassy-stm32` need their own chips.
- `cargo build --lib --target riscv64gc-unknown-none-elf`: the target is not installed on the
  host.
- Kani, mutation testing and the falsification patches were not run.
- NetBSD's `sys/arch/riscv/starfive/jh7110_trng.c` and the device-tree binding were not read.
