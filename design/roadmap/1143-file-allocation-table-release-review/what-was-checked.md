# What the review read and ran

An appendix to [the release review of `file_allocation_table`](../1143-file-allocation-table-release-review.md).

## The crate

`partsfoundry/file_allocation_table` at `77d47998705e05bf414cd82afcc969af5319795b`, version
0.1.0-pre.3, edition 2024, `rust-version` 1.88. Read: `Cargo.toml`, `README.md`, `CHANGELOG.md`,
`src/lib.rs` and every public module under `src/`. The lane read the tests and the Kani harnesses
for their count and their subjects only. The clone stayed unchanged; `git status` printed nothing
after every command.

## The commands

All ran on a Linux x86_64 host (Intel Xeon Platinum 8160 at 2.10 GHz, 80 threads), rustc 1.100.0,
with the target directory outside the clone.

- `cargo build` passes.
- `cargo test` passes 368 tests and ignores 2.
- `cargo test --features embedded-io-07` passes 381 tests and ignores 2.
- `RUSTDOCFLAGS="-D warnings" cargo doc --no-deps` is clean, with and without the feature.
- `cargo clippy --all-targets --all-features` is clean.
- `cargo build --lib` for `aarch64-unknown-none-softfloat`, `riscv64imac-unknown-none-elf` and
  `x86_64-unknown-none` passes on each target, with and without the feature.
- `cargo package --list --allow-dirty` lists 134 files.
- `grep -c 'kani::proof'` across `src/` counts 35 harnesses, the README's figure.
- A scratch binary printed `size_of` for a zero-sized device: `Volume` 4,216 bytes (P1-2),
  `Directory` 4,152, `FileReader` 4,152, `NamedEntry` 576. `fatfs`'s `FileSystem` over
  `Cursor<&mut [u8]>` is 200 bytes.

## The comparators read

The lane fetched each `.crate` from crates.io at the version in the prior-art table. Each went
into its own empty directory before the lane unpacked and read it.

- `fatfs` 0.3.6: `FileSystem<T: ReadWriteSeek>` holds the device in a `RefCell`. Errors are
  `io::Error` values with string messages. `DirEntry::attributes()` returns the `FileAttributes`
  bit set, and `format_volume` writes an image. Its default features are `chrono`, `std` and
  `alloc`.
- A probe crate with `fatfs` 0.3.6 at `default-features = false`, built for
  `x86_64-unknown-none`, fails: the crate cannot find `core_io`. With `features = ["core_io"]` the
  build script of `core_io` 0.1.20210325 fails instead.
- `fatfs`'s git main line is an unpublished 0.4 with its own I/O traits. The review read that line
  as `lamfat` 0.4.3, its republish. `lamfat` has `IoBase`, `Read`, `Write` and `Seek` of its own and
  a `#[non_exhaustive]` `Error<T>`. Its defaults are `std`, `alloc`, `lfn`, `unicode` and
  `log_level_trace`.
- `embedded-sdmmc` 0.10.0: `VolumeManager<D, T, MAX_DIRS, MAX_FILES, MAX_VOLUMES>` over a
  `RefCell`, with raw handles and a one-block cache. It exports `ClusterId` and an `Attributes`
  type with predicates. `Error<E>` comes from `thiserror`, is exhaustive and carries
  `FormatError(&'static str)`. `File` implements the `embedded-io` 0.7 traits, a required
  dependency.
- `hadris-fat` 2.5.0: features `read`, `write`, `lfn`, `alloc`, `std`, `sync`, `async`, `cache`
  and `unstable-exfat`, over five sibling `hadris` crates. Read for its manifest and error type only.
- `starry-fatfs` 0.4.1-preview.2: measured, not read.
- `embedded-io` 0.7.1 and `embedded-io-async` 0.7.0: `Read`, `Write`, `BufRead`, and `Seek` with
  `u64` positions, then the async forms.
- `embedded-storage` 0.3.2: `ReadStorage` and `Storage` at `u32` byte offsets.
- `block-device-driver` 0.2.0: an async `BlockDevice<const SIZE: usize>` with aligned buffers and
  `u32` block addresses.
- `embedded-sdmmc-types` 0.1.0: `BlockDevice` with `read(&self, &mut [Block], BlockIdx)`, a
  512-byte `Block`, and an error bound by `core::error::Error`.

## The benchmark

A scratch crate depends on this crate by path and on `fatfs = "=0.3.6"` with its default
features, so it runs over std with `alloc` and `chrono` on. `fatfs` 0.3 has no sector cache, and
its `DirEntry::file_name` (`src/dir_entry.rs`, line 512) returns a new `String` for each entry,
which the list column calls. `taskset -c 7 cargo run --release --bin fat_bench` runs it pinned to
one core.

- The image is 64 MiB in memory, formatted as FAT32 with 512-byte sectors by `fatfs::format_volume`.
  It holds `big.bin`, 1 MiB of the pattern `(i * 7 + 3) as u8`. It also holds a directory `dir`
  of 128 files named `file_NNN.txt`, 16 bytes each, which take long names.
- This crate reads through a `SectorDevice` over the byte slice that copies each sector. `fatfs`
  reads through `Cursor<&mut [u8]>`.
- The open column times `Volume::open` against `FileSystem::new`.
- The read column opens the volume, looks up `big.bin` and reads it to the end through a
  4,096-byte buffer, summing the byte counts.
- The list column opens the volume and the directory, then walks all 130 entries (`.` and `..`
  included). Each entry adds 1, its size and its long name's length to a total.
- Both sides read 1,048,576 bytes, reach the same list total (3,717) and count the same 129,046
  clusters, which the binary checks before timing.
- The loop starts at 64 repetitions and doubles until one pass takes 50 ms or more. It then runs
  seven passes and reports the lowest, divided by the repetitions. Inputs and results pass through
  `black_box`.

Three runs pinned to one core, in nanoseconds, this crate first:

| workload | run 1 | run 2 | run 3 |
|---|---|---|---|
| open the volume | 60 / 170 | 62 / 153 | 61 / 154 |
| open and read a 1 MiB file | 76,123 / 80,516 | 74,300 / 81,735 | 73,648 / 83,489 |
| open and list a 128-file directory | 18,472 / 64,363 | 18,447 / 65,022 | 18,703 / 64,027 |

Seven unpinned runs on the shared host put the read at 76,269 to 79,744 against 82,468 to 89,823,
and the listing at 18,684 to 29,551 against 64,246 to 93,890; both move with the host's load.

## The create cost

Finding P2-7 will not be fixed. Each create reads the whole directory once: one pass refuses a
clashing name, numbers the alias and finds the free slots. Remembering the first free run would
save no reads, since a directory that fills from the front has it at the end marker. In a release
build on a Linux x86_64 host, the 1,000th, 2,000th and 4,000th 8.3 creates in the root of a 128 MiB
FAT32 volume of one-sector clusters read 65, 127 and 253 sectors. The crate README's `BUGS` section states
the cost.

## What was not run

- Kani, mutation testing and the fuzz targets were not run; the harness count comes from source.
- No comparator's tests ran; the lane built only `fatfs` 0.3.6, for the benchmark and the probe.
- The benchmark covers reading and listing only, not writing, formatting or a real card.
- No image went through `fsck.fat`.
