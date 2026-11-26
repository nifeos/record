---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1085, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1144. `device_tree_blob`: the release review's findings

*(The number and the slug are provisional.)*

The release review of `partsfoundry/device_tree_blob` at commit `9ed5c2a9`, version 0.1.0, under
milestone 1129 (the combine review), whose [block](1129-crate-interfaces-best-in-class.md) sets
its form. The baseline is milestone 1085 (what an outside maintainer would fix before it leaves),
[its block](1085-device-tree-blob-outside-review.md) and the cleared package
[`notes/crate-reviews/device-tree-blob.md`](../../notes/crate-reviews/device-tree-blob.md).
Every finding of 1085 reads Done and nothing here repeats one. The ruling recorded there under
[Keep `device_tree_blob` and release it](1085-device-tree-blob-outside-review.md#keep-device_tree_blob-and-release-it)
keeps this crate over `dtoolkit`; this review reads `dtoolkit` as a comparator only.

The release-review rule reopens no name here. The architect ratified every name of the crate on
2026-11-19 or 2026-11-20 (UTC), and the one naming rule added since, on `right` and `permission`, touches
none of them.

Reuse: the prior-art table weighs each device tree reader a caller could take instead.

## Finding status

- P0-1, a blob's acceptance depends on the lookup: Open.
- P0-2, two rules for a short output slice: Open.
- P0-3, the errors carry no location: Waiting on the errors decision of milestone 1129.
- P0-4, `Region` has public fields and is not `#[non_exhaustive]`: Open.
- P0-5, the lookups match a name prefix: Open.
- P1-1, no general traversal: Open.
- P1-2, the common traits are missing: Open.
- P1-3, four of seventeen functions have an example: Open.
- P1-4, the `from_pointer` safety contract is incomplete: Open.
- P2-1, `Debug` prints the blob twice: Open.
- P2-2, the package ships the repository's tooling: Open.
- P2-3, every walk reads every property name: Open.

## Open decisions

The one-way doors D1 to D6 below.

## Goal

A stranger writing a boot loader or a kernel that receives a flattened device tree picks this
crate over `fdt`, `dtoolkit` and `fdt-rs`. It accepts a blob once and answers every lookup on it
the same way, it walks the tree as freely as the comparators do, and it never panics on what
firmware hands it.

## What the review read and ran

The sources, the commands, the benchmark method and libfdt are in
[the appendix](1144-device-tree-blob-release-review/what-was-checked.md), and the 54 API
Guidelines items in [the guidelines table](1144-device-tree-blob-release-review/api-guidelines.md).

## Prior art

Measured from the crates.io API on 2026-11-26 (UTC). A stranger brings this crate the problem of
reading the memory map, the boot arguments and a device's registers out of the blob firmware
hands over, with no allocator. Ranks 2 and 3 follow the leading reader by what a stranger
compares it with, not by downloads: `dtoolkit` is the alternative the baseline weighed, and
`fdt-rs` the other reader that needs no allocator.

| crate or system | role | version read | total | 90 days | reverse dependencies | version read released |
|---|---|---|---|---|---|---|
| `fdt` | ranked 1: a reader, no allocator | 0.1.5 | 1,710,541 | 468,200 | 7 | 2023-02-05 |
| `dtoolkit` | ranked 2: a reader, editor and writer | 0.5.0 | 11,389 | 7,525 | 3 | 2026-11-03 |
| `fdt-rs` | ranked 3: a reader, no allocator | 0.4.5 | 115,343 | 4,130 | 1 | 2024-02-25 |
| `device_tree` | measured and read: an owned tree, needs an allocator | 1.1.0 | 2,403,514 | 511,456 | 2 | 2016-06-28 |
| `dtb-walker` | measured and read: a callback walker | 0.2.0-alpha.3 | 168,871 | 104,023 | 0 | 2022-07-19 |
| `fdt-parser` | measured and read: a reader, needs an allocator | 0.5.1 | 191,083 | 34,583 | 10 | 2025-11-08 |
| `fdt-raw` | measured and read: a reader | 0.3.0 | 130,036 | 34,126 | 6 | 2026-03-09 |
| `flat_device_tree` | measured and read: a fork of `fdt` | 3.1.1 | 15,251 | 1,333 | 2 | 2024-06-07 |
| `vm-fdt` | neighbor: a writer only | 0.3.0 | 3,326,764 | 761,716 | 15 | 2023-11-15 |
| libfdt (dtc) `libfdt/fdt_ro.c` | outside Rust | v1.7.2 | | | | |

`device_tree` draws more downloads than `fdt` but builds a `Vec` and `String` tree and has had no
release since 2016, so it ranks below the readers a no-allocator caller can take.

### What `device_tree_blob` does better

- Than `fdt`, it refuses a malformed blob with an error. `fdt` 0.1.5 checks only the magic and
  `totalsize` in `Fdt::new`. Its source holds 49 `unwrap`, `expect` or `panic!` sites outside its
  tests and pretty-printing. `chosen()` and `root()` `expect` a node, and `str_at_offset` `expect`s UTF-8. Its `reg()`
  returns `None` for more than two cells. Its `MemoryRegion` holds a `*const u8` and a `usize`
  size, so a 64-bit region does not fit it on a 32-bit caller. This crate returns `u64` regions and
  refuses a wrapping one. Its `Error` implements `core::error::Error`, which `fdt`'s `FdtError` does not.
- Than `dtoolkit`: no dependencies, where `dtoolkit` 0.5.0 takes `zerocopy`, `zerocopy-derive` and
  `thiserror` even with no feature on. It reads a blob placed in a larger buffer, where
  `dtoolkit`'s `Fdt::new` refuses any `totalsize` that is not the slice's length.
- Than `fdt-rs`: a safe `from_bytes`, where `fdt-rs` 0.4.5 opens with `unsafe fn new(buf)` whose
  caller must guarantee alignment and length, and seven dependencies. `fdt-rs` keeps `std` on by
  default.
- Than all three: nine Kani harnesses and 46 hostile-blob tests, where none of the three
  carries a proof. `pointer_handle_property` honors `linux,phandle` beside `phandle`, where
  `fdt`'s `find_phandle` reads only `phandle`.

## The items

Effort is S (half a day), M (a day or two) or L (longer). A P0 change is one-way: once 0.1.0
reaches crates.io, callers outside the repository build on it, so it lands in 0.1.0 or never.

### P0: the 0.1.0 interface

#### P0-1. A blob's acceptance depends on the lookup

Verified by building.
`from_bytes` checks the header and the block offsets only; each lookup walks the structure block
from the start and stops at its answer. With the final `FDT_END` of the riscv64 fixture replaced by
an unknown token, `from_bytes` returns the tree, `node_property(b"serial@10000000",
b"compatible")` returns the value, and `memory_regions` on the same tree returns
`Err(BadToken(10))`. A caller cannot tell from `from_bytes` whether the blob is whole.
`dtoolkit`'s `Fdt::validate` walks the whole structure block, the names and the reservation block
before it returns a tree, and libfdt v1.7.2's `libfdt.h` declares `fdt_check_full` for a caller who asks.
Change: `from_bytes` and `from_pointer` walk the structure block once (tokens, nesting, depth and name terminators) and refuse a malformed blob, so a later lookup fails only on
a value's shape. The walk costs what the benchmark's walk column shows, a few microseconds on the
fixtures. Door: one-way (D1), since tightening what `from_bytes` accepts after 0.1.0 breaks a
caller whose blob it accepted. Effort: M.

#### P0-2. Two rules for a short output slice

Verified in source.
`memory_reservations`, `memory_regions`, `node_register_regions`,
`node_register_regions_compatible` and `reserved_memory_regions` refuse a full `out` with
`Error::TooManyRegions`. `node_properties` writes what fits and returns the number of matching
nodes, which may exceed `out.len()`. A caller who learns one rule misreads the other. The
comparators return iterators and need no rule.
Change: one rule for all six. Door: one-way (D2). Effort: S.

#### P0-3. The errors carry no location

Verified in source.
`Error`'s ten variants say what went wrong but not where: `Truncated`, `BadValue` and
`BadStructure` carry nothing, and `BadToken(u32)` carries the token, not its offset. `dtoolkit`'s
`FdtParseError` carries the byte offset beside its kind, and `fdt-parser`'s `BufferTooSmall`
carries `pos`. A firmware author reading the boot error cannot find the fault. Change: an offset
on each structural variant, in the shape the errors decision of milestone 1129 picks. Door:
one-way (D3). Effort: S.

#### P0-4. `Region` has public fields and is not `#[non_exhaustive]`

Verified in source.
`Region` (`src/lib.rs`, lines 15 to 22) has two public fields, `start` and `size_bytes`, and no
`#[non_exhaustive]`, so a caller builds one with a struct literal, as every `out` array does, and
a third field, such as the node a region came from, breaks each of them. `fdt`'s `MemoryRegion`
has public fields too; `dtoolkit` returns its register entries through methods.
Change: `#[non_exhaustive]`, with `Region::new` and the `Default` of P1-2 for building one. Door:
one-way (D5). Effort: S.

#### P0-5. The lookups match a name prefix

Verified in source.
`node_register_regions`, `node_property`, `node_property_inherited` and `node_properties` match the first node whose name starts with `prefix` (`starts_with`, at
`src/lib.rs` lines 445, 654, 701 and 822), so `b"cpu"` matches a `cpus` node and `b"memory"` a
`memory-controller@` node. `memory_regions` already matches the exact name or the name followed by
`@` (line 382), the specification's unit-address rule. A caller who relies on the prefix behavior
after 0.1.0 breaks if it narrows.
Change: the rule of D6, documented on each lookup. Door: one-way (D6). Effort: S.

### P1: before the first release


#### P1-1. No general traversal

Verified in source.
The public surface is thirteen fixed lookups and the private `Tokens` walker; there is no node
handle, no iteration over nodes, children or properties, and no lookup by path. A caller with a
question none of the lookups asks, such as every `status = "okay"` node or a node's
`interrupts`, writes a walker of its own. `fdt` has `all_nodes`, `find_node(path)`, `children`
and `properties`; `dtoolkit` has a `Node` trait with `children`, `properties`, `child` and
`Fdt::find_node`; `fdt-rs` has `nodes`, `props` and `compatible_nodes`; libfdt has
`fdt_path_offset`, `fdt_next_node` and `fdt_first_property_offset`, with an offset as the node
handle.
Change: a `Copy` node handle over the structure block (its offset and depth), `root`, `nodes`,
`find_node(path: &[u8])` with the specification's unit-address rule, and `children` and
`properties` on the handle, returning names and values as `&[u8]` as the lookups do. With P0-1 the
iterators need no `Result` per item. Door: two-way (an addition). Effort: M.

#### P1-2. The common traits are missing

Verified in source (C-COMMON-TRAITS).
`DeviceTreeBlob` derives only `Debug`, so a caller cannot copy the parsed tree into two
consumers; `fdt::Fdt` and `dtoolkit::fdt::Fdt` are `Clone` and `Copy`. `Region` lacks `Hash`,
`Default`, `PartialOrd` and `Ord`, so a caller cannot sort a memory map or keep regions in a set.
`Error` lacks `Hash`, which `dtoolkit`'s error types derive. Change: `Clone` and `Copy` on
`DeviceTreeBlob`; `Hash`, `Default`, `PartialOrd` and `Ord` on `Region`; `Hash` on `Error`. Door:
two-way. Effort: S.

#### P1-3. Four of seventeen functions have an example

Verified in source (C-CRATE-DOC, C-EXAMPLE, C-FAILURE).
The crate page has no example. `from_bytes`, `memory_regions`, `node_register_regions_compatible` and `node_properties` have one;
the other thirteen, `from_pointer` and `boot_arguments` among them, do not. No function has an
`# Errors` section, though each returns `Result`; `dtoolkit` gives both on each constructor and
lookup. `total_size`'s documentation speaks for one caller ("we are about to start handing
out"). Change: an example and an `# Errors` section on each, run against the fixtures, and
`total_size` described for any caller. Door: two-way. Effort: S.

#### P1-4. The `from_pointer` safety contract is incomplete

Verified in source.
The `# Safety` section of `from_pointer` (`src/lib.rs`, line 189) asks only that `pointer` point
at a blob that stays valid for `'a`. The function then builds a `&'a [u8]` of `totalsize` bytes,
so the contract must also require that those bytes are readable and that nothing modifies them
for `'a`. Change: say both. Door: two-way. Effort: S.

### P2: may follow


#### P2-1. `Debug` prints the blob twice

Verified in source (C-DEBUG).
The derived `Debug` prints the `bytes` and `structure` slices in full, every byte of a blob of up
to megabytes, and the structure prefix again. `dtoolkit`'s `Fdt` prints its length and address.
Change: a hand-written `Debug` with the total size and the block offsets. Door: two-way.
Effort: S.

#### P2-2. The package ships the repository's tooling

Verified by building.
`cargo package --list` includes `.githooks/`, `.github/`, `_typos.toml`, `deny.toml`,
`rustfmt.toml`, `falsifications/` and `docs/stranger-test.md`, since the manifest has no `include`.
Change: an `include` list of `src/`, `tests/`, the README, the changelog and the licenses. Door:
two-way. Effort: S.

#### P2-3. Every walk reads every property name

Inferred from source and the benchmark; the cause was not isolated.
`Tokens::step` resolves each property's name from the strings block as it passes, even for a
lookup that compares only node names. On the benchmark's walk and lookup, `fdt-rs` runs in about
half this crate's time. Change: a token that carries the name offset and resolves the name when a
lookup asks. Door: two-way. Effort: S.

### Measured performance

On a Linux x86_64 host, Intel Xeon Platinum 8160 at 2.10 GHz, rustc 1.100.0, release profile.
Nanoseconds per call, the lowest of seven passes; the method and the column contents are in
[the appendix](1144-device-tree-blob-release-review/what-was-checked.md#the-benchmark).

| input | operation | `device_tree_blob` | `fdt` 0.1.5 | `fdt-rs` 0.4.5 |
|---|---|---|---|---|
| riscv64 `virt`, 5,235 bytes, 34 nodes | parse | 6.0 | 6.9 | 2.7 |
| | walk all nodes | 3,150.4 (a lookup that misses) | 4,215.7 | 1,722.3 |
| | node by name, read `compatible` | 1,727.6 | 2,382.5 | 1,155.4 |
| aarch64 `virt`, 7,566 bytes, 57 nodes | parse | 5.9 | 7.1 | 2.7 |
| | walk all nodes | 5,484.7 (a lookup that misses) | 7,200.2 | 2,892.1 |
| | node by name, read `compatible` | 4,580.0 | 7,063.7 | 2,311.6 |

The crate has no public walk (P1-1), so its walk column is `node_property` with a name no node
has, which visits every token. Parse is a header check in all three. The crate is faster than
`fdt` on every row and slower than `fdt-rs` on every row; P2-3 is the likely cause.

## One-way doors

- D1, validate once (P0-1). Recommended: `from_bytes` and `from_pointer` walk the whole structure block, the stricter choice; loosening later breaks no
  caller. The lookups keep their `Result`, since `reg` and integer decoding still fail on a
  value's shape.
- D2, the short-slice rule (P0-2). Option A: all six refuse with `TooManyRegions`, whose ratified
  name and documentation already speak of the caller's output slice. Option B: all six write what
  fits and return the number found. Recommended: A, the stricter choice, since a caller who
  ignores a count truncates in silence.
- D3, error locations (P0-3). Recommended: an offset on each structural variant, decided once for
  every crate by the errors decision.
- D4, path lookups. `fdt`, `dtoolkit` and libfdt select by path, and `dtoolkit`'s `child`
  matches a unit address only when the caller gives one. Recommended: keep the lookups ratified at
  milestone 1085 under their names, and answer the path case with P1-1's `find_node`.
- D5, `Region`'s fields (P0-4). Option A: `#[non_exhaustive]` with `Region::new` and `Default`.
  Option B: two public fields frozen for good, since a span is a start and a size. Recommended: A,
  the stricter choice; dropping the attribute later breaks no caller.
- D6, the name rule of the lookups (P0-5). Option A: the exact name, or the name followed by `@`
  and a unit address, as `memory_regions` matches. Option B: keep the prefix rule as built and
  documented. Recommended: A, the stricter choice, since a prefix rule can come later as a new
  lookup and a narrowed rule breaks callers. The names ratified at milestone 1085 stay.

## Evidence for the shared decisions

- Errors: one `Error` enum, `#[non_exhaustive]`, with `Display` and `core::error::Error`, and no location (P0-3). `fdt`'s `FdtError` has three variants, no `core::error::Error` and no
  `#[non_exhaustive]`; `fdt-rs`'s `DevTreeError` is exhaustive with `Display` only; `dtoolkit`'s
  `FdtParseError` is a struct of a `#[non_exhaustive]` kind and an offset, through `thiserror`;
  libfdt returns negative codes. The evidence points to a non-exhaustive kind with an offset
  beside it.
- DMA regions: not applicable.
- Doorbells and tails: not applicable.
- Register access: not applicable.
- Byte sinks and sources: not applicable. The input is one borrowed `&[u8]` or a pointer, as in
  every comparator; nothing streams.
- Feature names: the crate declares none. `fdt` has `pretty-printing`; `dtoolkit` has `alloc`,
  `write`, `overlay`, `arrayvec07` and `heapless09`, naming an integration by its crate and major
  version; `fdt-rs` has `std`, on by default. The evidence points to `alloc` for an allocating
  addition and to the crate-and-version form for an integration.
- Simulators: not applicable. The crate drives no hardware; its tests read blobs dumped from QEMU.
- Contract layout: not applicable.

## Follow-on

- **Outstanding.** The errors decision of milestone 1129 takes D3. P1-1's handle and iterators
  follow D1, so that they need no per-item `Result`.

## Done when

Every P0 and P1 finding reads Done, or Will not fix with its ruling, the architect has ruled D1
to D6, and `script/review-status` shows the block BUILT.

## BUGS

- The benchmark inputs are the crate's two QEMU fixtures; the review measured no board's blob.
- The review read libfdt's `fdt_ro.c`, `fdt.c` and `libfdt.h` only, and ran no C.

## Index row

The release review of `device_tree_blob` against `fdt`, `dtoolkit`, `fdt-rs` and libfdt. Before
0.1.0: a `from_bytes` that accepts a blob some lookups then refuse, two rules for a short slice, errors without a location, an open `Region` and prefix matching.
Before the release: a general traversal. Six doors to rule.
