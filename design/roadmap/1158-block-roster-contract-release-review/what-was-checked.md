# What the review read and ran

An appendix to [the milestone](../1158-block-roster-contract-release-review.md).

## The crate

`partsfoundry/block_roster_contract` at `f0c199acc9cf2ca9e01c9350d3124aecf7994654`, version
0.1.0-pre.3, a fresh clone of `main`. Its newest tag is `v0.1.0-pre.3`. The census of milestone
1129 (the combine review) counted the same commit. The lane read in full: `Cargo.toml`,
`README.md`, `CHANGELOG.md`, `src/lib.rs` (820 lines, its tests and its five Kani harnesses
included), `docs/stranger-test.md`, both fuzz targets, `fuzz/Cargo.toml`,
`.github/mutants-exempts`, `.github/accepted-words` and the `ci.yml` and `fuzz.yml` callers.

## The commands

Each command below ran in the clone on a Linux x86_64 host, with rustc 1.100.0 and a target
directory in the lane's scratch area. `git status --short` showed the clone clean afterward.

- `cargo build` passes.
- `cargo test` passes: 16 unit tests and 2 doctests, one of them the README's example.
- `cargo +1.88 test`, the minimum Rust version, passes with the same counts.
- `RUSTDOCFLAGS="-D warnings" cargo doc --no-deps` passes with no warning.
- `cargo clippy --all-targets` passes with no warning.
- The bare-target builds pass: `cargo build --lib --target <target>` for each of
  `x86_64-unknown-none`, `aarch64-unknown-none-softfloat` and `riscv64imac-unknown-none-elf`.
- `cargo package --list --allow-dirty` lists 14 files: the manifest twice, the lock, the README,
  the changelog, two licenses, `src/lib.rs`, five falsification patches and
  `.cargo_vcs_info.json`. No workflow or hook ships.
- `grep -c 'kani::proof' src/lib.rs` prints 5, and `falsifications/` holds 5 patches, as the
  README says.
- `grep -n '# Errors\|# Panics\|# Examples' src/lib.rs` prints one line, the `# Examples` of
  `write` (P1-3).
- The crate declares no features, so there is one feature combination.

## The probe

A scratch program that depends on the clone by path printed:

- `write` accepts two equal devices and a device with transport 99 and ordinal `u32::MAX`, and
  `read` returns all three. The README says a reader may trust neither number.
- `{:?}` of that roster is
  `Roster { entries: [[0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0], [255, 255, 255, 255, 99, 0, 0, 0]] }`,
  and `{:?}` of its first device is `Device { transport: 1, ordinal: 0 }` (P1-2).
- `roster.count_by_transport(device.ordinal)` compiles and returns 0 (P0-2).
- A page whose magic bytes are `blkrosv2` returns `NotARoster`, and so does a page of `0x55`
  (P0-5).
- `write(&mut [0u8; 8], &[])` and `write(&mut [0u8; 16], &devices)` both return
  `Err(TooManyDevices)`, with one `Display` text for both (P0-4).
- `entry_capacity(4096)` is 510. `Roster` is 16 bytes, `Device` 8 and `ReadError` 1.

Five more functions sat behind one feature each, and each failed to compile as P1-1 and P1-2
say:

- `roster.devices().rev()`: the opaque type is not a `DoubleEndedIterator`.
- A function from `&'a [u8]` to `impl Iterator<Item = Device> + 'a` that returns
  `Roster::read(page).unwrap().devices()`: error E0515, a value that refers to a temporary.
- `for device in roster` with `roster: &Roster`: `&Roster` is not an iterator.
- `a == b` on two rosters: no `PartialEq`.
- `Device::default()`: no `Default`. The block asks for none, since no transport is a natural
  default.

## The later items

- P2-1. `Roster::read` is the one way in. `core` spells a checked conversion from bytes as
  `TryFrom` (`<[u8; 4]>::try_from(slice)`), and `zerocopy` 0.8.66 spells it `ref_from_bytes`.
- P2-2. `transport_name`, `entry_capacity`, `len` and `is_empty` are `const fn`. `read`, `get`,
  `devices`, `count_by_transport` and `write` are not. `write` loops with an iterator, which a
  `const fn` cannot. The lane did not try the change, so whether each body compiles as `const` at
  Rust 1.88 is inferred.
- P2-3. `read` checks the capacity word twice and keeps the counted entries alone. A program that
  reports how full the page is reads bytes 12 to 16 itself.
- P2-4. `read` converts both header words with `as usize`. Where `usize` is 16 bits, a count of
  65,537 becomes 1 and the page reads as one device. The crate's CI builds three 64-bit targets,
  and the lane built no 16-bit one.
- P2-5. `CHANGELOG.md` opens "Dates are UTC" and its three headings are bare version numbers.
  `docs/stranger-test.md` records a run that counted three proofs and ten unit tests; the file
  stays out of the package.

## The search for a comparator

On 2026-11-26 (UTC), `https://crates.io/api/v1/crates?q=<words>&sort=recent-downloads&per_page=8`
for each of: "block device list", "block devices", "lsblk", "device roster", "boot info", "nvme",
"disk enumeration", "shared page", "device inventory" and "sysfs block". No result publishes a
page layout that lists drives. The results that list drives on a hosted system became the ranked
crates. The lane also measured these at 22:53 (UTC) and set them aside:

| crate | version | total | 90 days | reverse dependencies | why set aside |
|---|---|---|---|---|---|
| `lsblk` | 0.6.1 | 22,533 | 3,677 | 1 | below the three ranked crates |
| `sysinfo` | 0.40.4 | 257,767,773 | 66,525,056 | 2,346 | lists mounted file systems among much else |
| `uefi` | 0.41.0 | 3,025,847 | 726,559 | 31 | a handle is the access path, which this crate refuses by design |
| `bootloader_api` | 0.11.17 | 246,204 | 114,110 | 7 | a boot page with no device list |
| `multiboot2-common` | 0.7.0 | 772,796 | 240,458 | not measured | read with `multiboot2`, which depends on it |

Only `block-utils` passes 10,000 downloads in 90 days among the crates that answer the same
question, and it has no wire form. The lane therefore read two systems outside Rust as well.

## The comparators read

The lane downloaded each `.crate` file from `static.crates.io` at the version the block's table
gives and unpacked each in its own directory.

- `block-utils` 0.11.1, `src/lib.rs` and `Cargo.toml`. `get_block_devices` returns
  `BlockResult<Vec<PathBuf>>` and `get_block_devices_iter` an opaque iterator of `PathBuf`, both
  from a udev scan. `Device` has nine public fields, among them `capacity`, `serial_number` and a
  `MediaType` enum with an `NVME` case. `BlockUtilsError` derives `thiserror::Error` with a
  `String` variant and five wrapped errors, and it is exhaustive. Nine dependencies and `udev` on
  Linux. It needs `std`.
- `rs-drivelist` 0.9.4, `src/lib.rs` and `src/device.rs`. `drive_list` returns
  `anyhow::Result<Vec<DeviceDescriptor>>`. The descriptor has 22 public fields in camel case,
  among them `busType: Option<String>`, `size` and seven booleans.
- `blockdev` 0.6.2, `src/lib.rs`. `get_devices` returns `Result<BlockDevices, BlockDevError>`.
  `BlockDevices` has `len`, `is_empty`, `iter` (a `std::slice::Iter`) and `IntoIterator` by value
  and by reference. `BlockDevError` is `#[non_exhaustive]` with named fields `path` and `source`,
  `Display` and `Error` written by hand. `DeviceType` is an exhaustive enum with `Other`,
  `as_str`, `Display` and `FromStr`. `get_devices` has `# Errors` and `# Examples` sections, and
  the example uses `?`. Its one feature is `serde`.
- `multiboot2` 0.28.0, `src/lib.rs`, `src/boot_information.rs`, `src/memory_map.rs` and
  `src/bootdev.rs`; and `multiboot2-common` 0.7.0, `src/lib.rs` and `src/raw.rs`.
  `pub const MAGIC: u32` is the value a boot loader leaves in a register, not a field of the
  table. `BootInformation::load` is an `unsafe fn` from a raw pointer that returns
  `Result<Self, LoadError>`. `LoadError` has `Memory(MemoryError)` and `NoEndTag` and derives
  `Copy`, `Eq`, `Ord`, `Hash` and `thiserror::Error`. `MemoryError` has six causes, among them
  `ShorterThanHeader` and `SizeInsufficient(usize, usize)`. `MemoryArea` has private fields, `new`
  and four `const` getters, and derives `Eq`, `Ord` and `Hash`. `MemoryAreaTypeRaw(u32)` is the
  wire number, and `MemoryAreaType` an enum with a `Custom(u32)` case. The memory map tag carries
  `entry_size` and `entry_version`, and `memory_areas` asserts that the size matches.
  `EFIMemoryAreaIter<'a>` is a named, `Clone`, exact-size iterator. The features are `alloc` and
  `builder`.
- `zerocopy` 0.8.66, `src/lib.rs` and `src/error.rs`: `FromBytes::ref_from_prefix` and
  `ref_from_prefix_with_elems`, and `SizeError`, `AlignmentError` and `CastError`, each with
  `into_src`. The benchmark uses them.

## The systems outside Rust

- seL4 13.0.0, `libsel4/include/sel4/bootinfo_types.h`. `seL4_BootInfo` is the page the kernel
  writes once for the first program. It has no magic and no version. Its `untypedList` is an array
  of two-word `seL4_UntypedDesc` entries with an `isDevice` byte, sized by a build setting, and
  the count is `untyped.end - untyped.start`, two slot numbers elsewhere in the page. Further
  chunks follow the page, each behind a `seL4_BootInfoHeader` of an `id` and a `len`.
- Linux v6.12, `drivers/nvme/host/core.c`, `nvme_scan_ns_list`. The reader asks for a page of
  `NVME_IDENTIFY_DATA_SIZE` bytes, reads it as little-endian `u32` namespace numbers and stops at
  the first zero, so the list has no count and no magic. The file is GPL; the lane read it for the shape of
  the list only.

## The benchmark

A scratch crate depends on the clone by path and on `zerocopy` at `=0.8.66` with its `derive`
feature. It was built with `cargo build --release`, rustc 1.100.0, on a Linux x86_64 host (an
Intel Xeon Platinum 8160 at 2.10 GHz, 80 threads).

The comparator declares `Header { magic: U64, count: U32, capacity: U32 }` and
`Entry { ordinal: U32, transport: U32 }` with `zerocopy`'s little-endian types. It takes the
header with `ref_from_prefix`, makes the five checks `Roster::read` makes, and takes the counted
entries with `<[Entry]>::ref_from_prefix_with_elems`. Both sides read a 4096-byte page that
`write` filled with 3 or 510 devices, and the program asserts that both sums agree before it
times them.

Each row runs a closure in a loop that starts at 64 repeats and doubles until one pass lasts
50 ms. Seven passes follow at that count, and the figure is the lowest pass divided by the count.
`std::hint::black_box` wraps every input and every result. The read rows include the header
checks. The sum rows add the transport and the ordinal of every device. The count rows count the
devices of transport 1. The `write` row includes the header and every entry.

Two runs of the same binary, in nanoseconds per call:

| operation | 3 devices, run 1 | run 2 | 510 devices, run 1 | run 2 |
|---|---|---|---|---|
| `Roster::read` | 3.79 | 3.76 | 3.81 | 6.51 |
| `zerocopy`, the same checks | 3.84 | 3.64 | 3.72 | 3.86 |
| `Roster::read`, then sum every device | 6.17 | 5.90 | 189.21 | 192.04 |
| `zerocopy`, the same sum | 5.96 | 5.60 | 196.43 | 188.68 |
| `Roster::read`, then `count_by_transport` | 8.95 | 8.66 | 126.63 | 125.34 |
| `zerocopy`, the same count | 5.76 | 5.62 | 129.50 | 120.24 |
| `write` | 7.99 | 17.98 | 171.24 | 122.13 |

The block's table is run 1. The host ran other work, so a row moves between runs by more than
the two sides differ. One difference repeats: at 3 devices `count_by_transport` takes about 3 ns
longer than the hand-written count.

## What the lane did not run

- Kani and the falsification replay; the harness and patch counts are from the source.
- The fuzz targets and mutation testing.
- A build for a 16-bit target (P2-4) or at Rust 1.88 for a bare target.
- The tests of any comparator.
