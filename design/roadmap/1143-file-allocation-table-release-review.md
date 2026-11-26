---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1061, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1143. `file_allocation_table`: the release review's findings

*(The number and the slug are provisional.)*

The release review of `partsfoundry/file_allocation_table` at commit `77d47998`, version
0.1.0-pre.3, under [milestone 1129 (the combine review)](1129-crate-interfaces-best-in-class.md),
whose block sets its form. The lane read the crate as a firmware author choosing a FAT library
would, weighing it against `fatfs` and `embedded-sdmmc`. The baseline is milestone 1061 (the
outside review's findings), [its block](1061-file-allocation-table-outside-review.md) and the
cleared package
[`notes/crate-reviews/file-allocation-table.md`](../../notes/crate-reviews/file-allocation-table.md)
with [its interface listing](../../notes/crate-reviews/file-allocation-table-public-api.md).
1061's open item, the first-publish token, stays its own. Three settled choices stay closed: the
`embedded-io-07` feature, optional and off by default (ruled 2026-11-12 UTC); the crate stays
standalone; and the names of 1061's P1-5 to P1-9, ratified as built (2026-11-16 UTC). Those names
were ratified after every naming rule now in force, so the release-review rule reopens none.

Reuse: the crate's tests and its `lamfat` comparison tests, and a scratch benchmark crate that
[the appendix](1143-file-allocation-table-release-review/what-was-checked.md) describes. No new
tool.

## Finding status

- P0-1, entries return their attribute byte as a bare `u8`: Open.
- P0-2, cluster numbers are bare `u32`: Open.
- P0-3, the two image builders disagree on sector widths and refuse with a bare `bool`: Open.
- P0-4, `WritableVolume` dereferences to `Volume`: Open.
- P1-1, the crate page has no example: Open.
- P1-2, the README misstates the size of a `Volume`: Open.
- P1-3, fallible functions carry no `# Errors` section: Open.
- P2-1, the manifest has no `documentation` key: Open.
- P2-2, block-device adapters: Waiting on the feature-name decision of milestone 1129.
- P2-3, `BufRead` and an async reader: Waiting on the byte sinks and sources decision of milestone 1129.
- P2-4, a sector buffer sized to the device: Open.
- P2-5, `LayoutError` has no `Hash`: Open.
- P2-6, `Attributes` has no operators: Open.
- P2-7, creating entries in a large directory is quadratic: Open.

## Open decisions

The one-way doors D1 to D6 below.

## Goal

A stranger writing firmware that reads and writes an SD card or a disk image picks this crate over
`fatfs` and `embedded-sdmmc`. It builds with no allocator and no std on stable Rust. It refuses a malformed image with a typed error and takes a device through one small trait. Its types keep
a cluster number, a sector index and an attribute set apart.

## What the review read and ran

The sources, the commands, the comparators and the benchmark method are in
[the appendix](1143-file-allocation-table-release-review/what-was-checked.md), and the 54 API
Guidelines items in
[the guidelines table](1143-file-allocation-table-release-review/api-guidelines.md).

## Prior art

The figures come from the crates.io API, read on 2026-11-26 (UTC). The task a stranger brings is
reading and writing a FAT12, FAT16 or FAT32 volume on a device with no operating system, or in a
host tool that builds an image. The review read `fatfs` at 0.3.6, its published version; its git
main line is an unpublished 0.4 with its own I/O traits, which `lamfat` 0.4.3 republishes, so the
review read that too.

| crate | role | version read | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `fatfs` | ranked 1: read and write, over `std::io` | 0.3.6 | 1,978,715 | 543,223 | 60 | 2023-01-17 |
| `embedded-sdmmc` | ranked 2: an SD card over SPI with a FAT volume manager | 0.10.0 | 412,688 | 62,481 | 40 | 2026-08-10 |
| `lamfat` | ranked 3: a republish of `fatfs`'s main line | 0.4.3 | 36,281 | 28,025 | 0 | 2026-10-15 |
| `starry-fatfs` | measured, not ranked: another `fatfs` fork | 0.4.1-preview.2 | 48,458 | 12,931 | 3 | 2026-02-06 |
| `hadris-fat` | measured, not ranked: FAT with an exFAT preview | 2.5.0 | 12,298 | 5,539 | 8 | 2026-11-22 |
| `fat-core` | neighbor: a forensic reader | 0.2.0 | 8,446 | 6,230 | 2 | |
| `rust-fs-core` | neighbor: not FAT | 0.5.1 | 71,112 | 71,112 | 15 | |
| `embedded-io` | integration: `Read`, `Write`, `Seek` | 0.7.1 | 203,586,087 | 93,397,838 | 352 | 2025-10-01 |
| `embedded-io-async` | integration: the async traits | 0.7.0 | 9,393,156 | 3,930,371 | 323 | 2025-09-30 |
| `embedded-storage` | integration: byte-addressed storage | 0.3.2 | 10,347,110 | 1,749,590 | 89 | 2026-09-20 |
| `block-device-driver` | integration: an async block trait | 0.2.0 | 1,549,551 | 713,321 | 8 | 2024-03-30 |
| `embedded-sdmmc-types` | integration: the `BlockDevice` trait | 0.1.0 | 22,681 | 21,186 | 2 | 2026-08-10 |

`hadris-fat`'s newest version is 3.0.0-rc.4; the row reads its newest stable one.

### What `file_allocation_table` does better

- Than `fatfs` 0.3.6: it builds with no std on stable Rust. `fatfs` 0.3.6 without its default
  features needs the `core_io` crate. A build for `x86_64-unknown-none` fails without it, since
  the compiler cannot find the crate, and with it, since the `core_io` build script fails. Its errors are
  typed enums a caller matches, where `fatfs` returns `io::Error` built from string messages
  (`Error::new(ErrorKind::Other, "...")`). It lists a 128-file directory in about a third of the
  time `fatfs` takes, as Measured performance shows below.
- Than `embedded-sdmmc` 0.10.0: it is a file system alone, over any sector size of 512 to
  4,096 bytes. `embedded-sdmmc` binds its FAT code to its own 512-byte `Block` and takes
  `embedded-hal`, `heapless`, `thiserror`, `bitbybit`, `arbitrary-int` and `log` with it. Its errors
  are `#[non_exhaustive]` and carry no strings, where `embedded-sdmmc`'s `Error<E>` is exhaustive and
  carries `FormatError(&'static str)`. It hands out owned values and borrows. `embedded-sdmmc`'s `VolumeManager` instead holds a
  `RefCell` and fixed tables of open handles, which a caller sizes by the const generics
  `MAX_DIRS` and `MAX_FILES`.
- Than `lamfat` 0.4.3: no default feature turns on std, allocation or logging, where `lamfat`'s
  defaults are `std`, `alloc`, `lfn`, `unicode` and `log_level_trace`.
- Than `hadris-fat` 2.5.0: one crate with no required dependency, where `hadris-fat` takes five
  sibling crates (`hadris-common`, `hadris-fixed`, `hadris-io`, `hadris-macros`, `hadris-path`).
- Than all four: `#![forbid(unsafe_code)]`, 35 Kani harnesses, a format planner that writes no
  byte itself (`FormatPlan::fill_sector`), and a volume builder for host tools (`VolumeLayout`).

## The items

Sizes: S takes half a day, M a day or two, L longer. A P0 item changes a public signature that
callers will build on after 0.1.0, so it ships in that release or never.

### P0: the 0.1.0 interface

#### P0-1. Entries return their attribute byte as a bare `u8`

Verified in source.
`ShortEntry::attributes()` (`src/directory.rs`) and `NamedEntry::attributes()`
(`src/named_entry.rs`) return the stored byte as `u8`, beside the typed `user_attributes() ->
Attributes`, `is_directory()` and `is_volume_label()`. A caller who reaches for `attributes()`
tests bits by number, and the meaning of each bit becomes part of the interface. `fatfs` 0.3.6
returns `FileAttributes`, a bit set; `embedded-sdmmc` 0.10.0 wraps the byte in `Attributes` with
`is_directory`, `is_volume` and `is_lfn`.
Change: make both `attributes()` methods crate-private, leaving the typed getters as the public
view. Door: one-way (D1). Effort: S.

#### P0-2. Cluster numbers are bare `u32`

Verified in source.
`Volume::chain(first_cluster: u32)` and `Volume::table_entry(cluster: u32)` (`src/reader.rs`),
`NamedEntry::first_cluster()` and `ShortEntry::first_cluster()`, the `Chain` iterator's
`Result<u32, _>`, `TableEntry::Next(u32)`, `ChainError::NotADataCluster(u32)` and
`ChainError::Broken { cluster: u32, .. }`, and
`FileSystemInformation::next_free_cluster() -> Option<u32>` all carry a cluster as `u32`. The same
`u32` type carries sector counts and byte sizes, so nothing stops a size passing as a cluster. The
crate already has `DirectoryCluster(u32)` for directories (1061's P1-8), and `embedded-sdmmc`
0.10.0 exports `ClusterId`, which its `DirEntry::cluster` field carries.
Change: a cluster newtype (name provisional, for the naming authority) in every place above, with
`DirectoryCluster` convertible to it. Door: one-way (D2). Effort: M.

#### P0-3. The two image builders disagree on sector widths and refuse with a bare `bool`

Verified in source.
`FormatOptions::new(sector_size, total_sectors: u32)`, `with_hidden_sectors(u32)`,
`FormatPlan::metadata_sectors() -> u32` and `FormatPlan::fill_sector(index: u32, out) -> bool`
(`src/format.rs`) take `u32`, while `VolumeLayoutOptions::new(total_sectors: u64)`,
`with_hidden_sectors(u64)`, `VolumeLayout::metadata_sectors() -> u64` and
`VolumeLayout::fill_sector(index: u64, out) -> bool` (`src/volume.rs`) take `u64`, as
`SectorDevice::read_sector` does. A caller moving from one builder to the other casts. Both
`fill_sector` methods return `false` for two different refusals, an index past the metadata and a
buffer of the wrong length, which the caller cannot tell apart.
Change: `u64` for every caller-facing sector index and count, the on-disk 32-bit limit refused at
construction as `VolumeLayoutOptions` already does, and `fill_sector` returning a `Result` whose
error names the refusal. Door: one-way (D3). Effort: S.

#### P0-4. `WritableVolume` dereferences to `Volume`

Verified in source.
`impl Deref for WritableVolume<D, C>` and `impl DerefMut` (`src/writable_volume.rs`) expose every
`Volume` method on the writable one. The API Guidelines keep `Deref` for smart pointers
(C-DEREF); here it makes `Volume`'s method set part of `WritableVolume`'s, so a method later added
to `Volume` under a name `WritableVolume` also uses changes which one a caller's code calls.
`into_volume` already gives the volume back by value.
Change: `as_volume` and `as_volume_mut` accessors (names provisional) in place of the two impls.
Door: one-way (D4). Effort: S.

### P1: before the first release

#### P1-1. The crate page has no example

Verified in source (C-CRATE-DOC, C-EXAMPLE, C-QUESTION-MARK).
The crate documentation in `src/lib.rs` is 85 lines with `# Features` and `# BUGS` and no code.
The README's examples compile as doctests through `#[cfg(doctest)] struct ReadmeExample`, so they
run in the tests but do not appear on the crate's documentation page. Of the item examples,
`SectorDevice` has one; most of the rest end in `.unwrap()` (13 lines) rather than `?` (5 lines).
Change: the README's read example on the crate page, an example on `Volume::open`,
`WritableVolume::create_file`, `FormatPlan` and `VolumeLayout`, and `?` throughout. Door: two-way.
Effort: S.

#### P1-2. The README misstates the size of a `Volume`

Verified by building.
The README's Footprint section gives a `Volume` as 4,192 bytes plus the device.
`size_of::<Volume<D>>()` for a zero-sized device prints 4,216 on a 64-bit host. The `Directory`,
`FileReader` and `NamedEntry` figures (4,152, 4,152 and 576) match. Change: 4,216, and a test that
pins each figure the README states. Door: two-way. Effort: S.

#### P1-3. Fallible functions carry no `# Errors` section

Verified in source (C-FAILURE).
No item has an `# Errors` heading; each fallible function states its refusals in prose
("Refuses ...") within its first paragraph, and some name no variant. Change: an `# Errors`
section on each public function that returns `Result`, naming its variants. Door: two-way.
Effort: M.

### P2: may follow

#### P2-1. The manifest has no `documentation` key

Verified in `Cargo.toml` (C-METADATA).
It has `repository` and `readme` but no `documentation` or `homepage`. Change: add
`documentation`. Door: two-way. Effort: S.

#### P2-2. Block-device adapters

Verified in the comparators' source.
The crate implements `SectorDevice` for no outside trait. `embedded-sdmmc-types` 0.1.0's
`BlockDevice` reads `&mut [Block]` at a `BlockIdx(u32)` through `&self`; `block-device-driver`
0.2.0's is async over `BlockDevice<const SIZE: usize>` with aligned buffers; `embedded-storage`
0.3.2's `ReadStorage` and `Storage` take `u32` byte offsets. A caller with an SD card driver
written to one of them writes the adapter. Change: optional adapters for `embedded-sdmmc-types`
and `embedded-storage`, under the names the feature-name decision picks. Door: two-way (an
addition). Effort: S each.

#### P2-3. `BufRead` and an async reader

Verified in source.
The `embedded-io-07` feature implements `Read`, `Write` and `Seek` for the file reader and writer
(`src/embedded_io_07.rs`), and `flush` returns `Ok`. It implements no `BufRead`, though the reader
already holds a sector buffer, and nothing for `embedded-io-async` 0.7.0. Change: `BufRead` on the
reader, and the async traits when the byte sinks and sources decision rules on them. Door: two-way
(an addition). Effort: M.

#### P2-4. A sector buffer sized to the device

Verified by building.
`Volume`, `Directory` and `FileReader` each hold a 4,096-byte buffer, the largest sector size, so
a 512-byte card spends 3.5 KiB per value it does not use; `embedded-sdmmc` holds one 512-byte
`Block` in its cache. Change: a const generic for the buffer size with 4,096 as its default.
Door: two-way, since a defaulted parameter breaks no caller. Effort: M.

#### P2-5. `LayoutError` has no `Hash`

Verified in source (C-COMMON-TRAITS).
The other fourteen public error types derive `Hash`; `LayoutError` (`src/volume.rs`) derives
`Debug`, `Clone`, `Copy`, `PartialEq` and `Eq` only. Change: derive it. Door: two-way. Effort: S.

#### P2-6. `Attributes` has no operators

Verified in source.
`Attributes` combines through `union`, `difference` and `contains`; it implements no `BitOr`,
`BitAnd` or `Not`, where `fatfs`'s `FileAttributes` (from `bitflags`) has them. Change: the
operators beside the methods. Door: two-way (an addition). Effort: S.

#### P2-7. Creating entries in a large directory is quadratic

Verified in source (the README's `BUGS`).
Each new entry scans the directory for a free run of slots and for a clashing name, so filling a
directory of n entries costs on the order of n squared sector reads, as it does in `fatfs`. The
README gives the figures. Change: a scan that remembers the first free run between calls on one
`WritableVolume`. Door: two-way. Effort: M.

### Measured performance

On a Linux x86_64 host (Intel Xeon Platinum 8160 at 2.10 GHz, 80 threads), rustc 1.100.0, release
profile, against `fatfs` 0.3.6 on the same 64 MiB FAT32 image in memory. Each figure is
nanoseconds per operation, the lowest of seven passes; each workload includes opening the volume.
The appendix gives the method and two further runs, which agree within 15 percent on reading and
on opening.

| workload | `file_allocation_table` | `fatfs` 0.3.6 |
|---|---|---|
| open the volume | 60 | 154 |
| open and read a 1 MiB file | 77,593 | 83,817 |
| open and list a 128-file directory | 27,110 | 72,452 |

Reading a large file is within 10 percent of `fatfs`, since both copy whole sectors and the device
copy dominates; listing is about 2.7 times faster across the three runs (2.4 to 3.5).

## One-way doors

- D1, the raw attribute byte (P0-1). Recommended: crate-private, the stricter choice; a typed or
  raw getter can be added later without breaking a caller.
- D2, the cluster type (P0-2). Recommended: a newtype, matching `DirectoryCluster` and
  `embedded-sdmmc`'s `ClusterId`; its name goes to the naming authority.
- D3, sector widths and the `fill_sector` refusal (P0-3). Recommended: `u64` throughout and a
  `Result`, matching `SectorDevice` and `VolumeLayout`.
- D4, `Deref` on `WritableVolume` (P0-4). Recommended: explicit accessors, the stricter choice;
  adding `Deref` later breaks no caller, removing it does.
- D5, the feature's name. `embedded-io-07`, ruled 2026-11-12 (UTC), names the major version, so a
  later `embedded-io` 0.8 can sit beside it as `embedded-io-08`. `embedded-sdmmc` takes
  `embedded-io` 0.7 as a required dependency, and `fatfs` and `lamfat` define their own traits.
  Recommended: keep the name and have the feature-name decision of milestone 1129 adopt the
  version suffix for every crate that adapts a pre-1.0 trait crate.
- D6, the device trait. `SectorDevice` reads one sector at a `u64` index through `&mut self` and
  reports a sector size of 512 to 4,096 bytes; `WritableSectorDevice` adds one write. The
  comparators' traits take `&self` (`embedded-sdmmc-types`), a `u32` index
  (`embedded-sdmmc-types`, `block-device-driver`) or byte offsets (`embedded-storage`), and fix
  the block at 512 bytes or a const. Recommended: keep it. `&mut self` needs no cell, and `u64` covers every FAT32 volume's sectors
  past a partition offset. Adapters (P2-2) reach the other traits, and the byte sinks and sources
  decision of milestone 1129 may adopt this one as the sector form.

## Evidence for the shared decisions

- Errors. The crate's fifteen public error types each implement `Display` and
  `core::error::Error` (`src/error_display.rs`), are `#[non_exhaustive]`, name their fields
  (`ChainError::Broken { cluster, entry }`), and are generic over the device's error, which they
  hand back unchanged (`ChainError::Device(E)`). `fatfs` 0.3.6 uses `io::Error` with string
  messages; `lamfat` 0.4.3 has a `#[non_exhaustive]` `Error<T>`; `embedded-sdmmc` 0.10.0 has an
  exhaustive `Error<E>` from `thiserror` with `&'static str` payloads. The evidence points to this
  crate's shape. Its enums are non-exhaustive, name their fields and wrap the lower layer's error.
- Direct memory access regions: not applicable; the crate moves bytes through the caller's
  buffers only.
- Doorbells and tails: not applicable.
- Register access: not applicable.
- Byte sinks and sources. The crate's source is `SectorDevice`, a whole sector by `u64` index
  (D6), and its sink `WritableSectorDevice`; above the file system it offers `embedded-io` 0.7
  `Read`, `Write` and `Seek` behind a feature, mapping each error to the nearest `ErrorKind`.
  `embedded-sdmmc` offers the same `embedded-io` traits on its `File`; `fatfs` 0.3.6 uses `std::io`
  or `core_io`, and `lamfat` its own `Read`, `Write` and `Seek`. The evidence points to
  `embedded-io` as the byte layer and a sector trait of the caller's sector size beneath it.
- Feature names. One feature, `embedded-io-07` (D5). The evidence points to naming an adapter
  feature after the crate and its major version.
- Simulators: not applicable. The crate exports no test double. Its `SectorDevice` example is a
  device over a byte slice, which serves a caller's tests.
- Contract layout: not applicable; the crate is a library over an on-disk format it does not
  define.

## Follow-on

- **Outstanding.** The shared decisions of milestone 1129 take D5 and P2-2 for feature names, and
  D6 and P2-3 for byte sinks and sources.

## Done when

The block is built when `script/review-status` reports BUILT: each P0 and P1 item reads Done or
Will not fix with its ruling, and D1 to D6 carry the architect's rulings.

## BUGS

- The benchmark reads from memory. It measures the file system's work and a copy per sector, not
  a card's latency.
- `starry-fatfs` 0.4.1-preview.2 was measured, not read.
- `hadris-fat` was read at 2.5.0 for its features and dependencies only, and not built.

## Index row

The release review of `file_allocation_table` against `fatfs`, `embedded-sdmmc`, `lamfat` and
`hadris-fat`: four one-way type changes before 0.1.0, three documentation fixes before the
release, and six doors to rule. It lists a directory about 2.7 times faster than `fatfs`.
