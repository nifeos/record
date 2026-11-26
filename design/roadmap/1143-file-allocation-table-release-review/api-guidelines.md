# The API Guidelines checklist

An appendix to [the release review of `file_allocation_table`](../1143-file-allocation-table-release-review.md).
It rules on all 54 items of the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) for
`partsfoundry/file_allocation_table` at `77d47998`. Each finding a row names lives in that block.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `WritableVolume`, `open_file_reader`, `SLOT_BYTES` |
| C-CONV | met | `into_device` and `into_volume` give the parts back by value |
| C-GETTER | met | `first_cluster`, `size_bytes`, `volume_label`, with no `get_` prefix |
| C-ITER | met | `named_entries`, `root_named_entries` and `chain` return iterators |
| C-ITER-TY | met | the iterators are the named types `NamedEntries`, `Directory` and `Chain` |
| C-FEATURE | met | `embedded-io-07`, with no `use-` or `with-` prefix |
| C-WORD-ORDER | met | `VolumeFull`, `DirectoryNotEmpty`, `ShorterThanItsSize` |
| C-COMMON-TRAITS | not met | value and error types derive `Debug`, `Clone`, `Copy`, `PartialEq` and `Eq`, and six lack `Hash` (P2-5) |
| C-CONV-TRAITS | met | `From<ChainError<E>>` for `OpenError<E>` and `WriteError<E>` |
| C-COLLECT | not applicable | no collection type |
| C-SERDE | not applicable | the on-disk bytes are the format; no other serialized form |
| C-SEND-SYNC | met | no cell or raw pointer, so the types are `Send` and `Sync` with their parameters |
| C-GOOD-ERR | met | fifteen error types, each with `Display`, `core::error::Error` and `#[non_exhaustive]` |
| C-NUM-FMT | not applicable | no numeric type of its own; `Attributes` prints through `Debug` |
| C-RW-VALUE | met | `SectorDevice` and `WritableSectorDevice` hold for `&mut D` |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | not met | the crate page in `src/lib.rs` has no example (P1-1) |
| C-EXAMPLE | not met | few items carry an example (P1-1) |
| C-QUESTION-MARK | not met | item examples mostly end in `.unwrap()` (P1-1) |
| C-FAILURE | not met | no `# Errors` section on any fallible function (P1-3) |
| C-LINK | met | items link each other, such as `SectorDevice::sector_size` |
| C-METADATA | not met | no `documentation` key (P2-1) |
| C-RELNOTES | met | `CHANGELOG.md` describes each change |
| C-HIDDEN | met | nothing is `doc(hidden)`; the README doctest holder exists only under `cfg(doctest)` |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | met | each error conversion sits on the wider error type |
| C-METHOD | met | volume operations are methods on `Volume` and `WritableVolume` |
| C-NO-OUT | met | only the sector fills write into a caller's buffer, which is the buffer case |
| C-OVERLOAD | not applicable | no operator is implemented (P2-6 would add some) |
| C-DEREF | not met | `WritableVolume` dereferences to `Volume` (P0-4) |
| C-CTOR | met | `Volume::open`, `WritableVolume::open`, `FormatOptions::new`, `VolumeLayoutOptions::new` |
| C-INTERMEDIATE | met | `boot_sector`, `table_entry` and `chain` expose the layers beneath a file |
| C-CALLER-CONTROL | met | the caller supplies the device, the clock and every buffer |
| C-GENERIC | met | generic over the device and the clock |
| C-OBJECT | met | `SectorDevice`, `WritableSectorDevice` and `Clock` are object safe |
| C-NEWTYPE | not met | cluster numbers are bare `u32` (P0-2) |
| C-CUSTOM-TYPE | not met | the raw attribute byte (P0-1) and the `bool` from `fill_sector` (P0-3) |
| C-BITFLAG | met | `Attributes` is a bit set, not an enum |
| C-BUILDER | met | `FormatOptions` and `VolumeLayoutOptions` build through `with_` methods |
| C-VALIDATE | met | the boot sector, each chain and each name are checked before use |
| C-DTOR-FAIL | not applicable | no `Drop`; each write updates the entry before it returns |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | met | every public type has `Debug` |
| C-DEBUG-NONEMPTY | met | the derived output names each type |
| C-SEALED | not applicable | both device traits and `Clock` are for callers to implement |
| C-STRUCT-PRIVATE | met | no public struct has a public field |
| C-NEWTYPE-HIDE | met | the volume's cache and cursors are private |
| C-STRUCT-BOUNDS | met | the struct declarations carry no bounds |
| C-STABLE | met | the only dependency, `embedded-io` 0.7, is optional and named by its version (D5) |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 32 met, 9 not met, 13 not applicable.
