# The API Guidelines checklist

An appendix to [the milestone](../1145-e1000e-release-review.md), giving a verdict on each of the
54 items of the [Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html)
for `partsfoundry/e1000e` at `6f6d3f1c`. A finding named in a row is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `DataPlane`, `receive_verdict`, `RECEIVE_ENTRIES` |
| C-CONV | not applicable | no `as_`, `to_` or `into_` conversion is public |
| C-GETTER | met | `receive_cursor` and `Hardware::pci_vendor_id`, with no `get_` prefix |
| C-ITER | not applicable | no collection is iterated |
| C-ITER-TY | not applicable | no iterator type |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | met | `TransmitError`, `BadLength`, `ResetTimeout` |
| C-COMMON-TRAITS | met | the value types derive `Debug`, `Clone`, `Copy`, `PartialEq` and `Eq`; `DataPlane` and `SoftwareFlag`, which hold state or a claim, derive `Debug` only |
| C-CONV-TRAITS | not applicable | no value type converts to another |
| C-COLLECT | not applicable | no collection |
| C-SERDE | not applicable | register words and descriptors have no serialized form here |
| C-SEND-SYNC | met | no type holds a pointer, so every type is `Send` and `Sync` |
| C-GOOD-ERR | met | `Display`, `core::error::Error` and `#[non_exhaustive]` on all four error types; `sequence::Error` chains its inner error through `source` |
| C-NUM-FMT | not applicable | no numeric type of its own |
| C-RW-VALUE | not applicable | no reader or writer |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | met | the README is the crate page, with an example that runs as a doctest |
| C-EXAMPLE | not met | only the crate page and `receive_verdict` have one (P1-2) |
| C-QUESTION-MARK | not met | `examples/host_ring.rs` ends each fallible call with `expect` (P1-2) |
| C-FAILURE | not met | no `# Errors` section on any of the thirteen fallible public functions (P1-3) |
| C-LINK | met | items link to each other and to the registers they touch |
| C-METADATA | not met | no `documentation` key (P2-5) |
| C-RELNOTES | met | `CHANGELOG.md` gives each pre-release's changes |
| C-HIDDEN | met | the simulator is private; nothing is `doc(hidden)` |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | not applicable | no conversion |
| C-METHOD | met | the ring operations are methods on `DataPlane` |
| C-NO-OUT | met | `receive` fills the caller's buffer and returns the length |
| C-OVERLOAD | not applicable | no operator |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | met | `DataPlane::new` and `SoftwareFlag::acquire` |
| C-INTERMEDIATE | met | `receive_verdict`, `plan_paged_access` and `receive_cursor` expose the steps the loops take |
| C-CALLER-CONTROL | met | the caller supplies the region, the tails, the register access and every buffer |
| C-GENERIC | met | every function is generic over the traits it uses |
| C-OBJECT | met | `Hardware`, `DirectMemoryAccessRegion`, `Tails` and `FlushSupport` are object safe |
| C-NEWTYPE | met | `SoftwareFlag` proves the flag is held; register words stay the datasheet's integers |
| C-CUSTOM-TYPE | met | `ReceiveVerdict`, `EmptiedRings` and `AccessPath` where a `bool` or an integer would be ambiguous |
| C-BITFLAG | met | the flags are constants of the register's width, combined with `\|` |
| C-BUILDER | not applicable | no type with many optional parts |
| C-VALIDATE | met | frame lengths, PHY pages, flash offsets and the region's base are checked before use |
| C-DTOR-FAIL | not applicable | no `Drop`; `SoftwareFlag::release` takes the flag by value |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | met | every public type implements `Debug` |
| C-DEBUG-NONEMPTY | met | the derived output names each type |
| C-SEALED | not applicable | every trait is for callers to implement |
| C-STRUCT-PRIVATE | not met | `DataPlane`'s two counters are public fields (P0-1) |
| C-NEWTYPE-HIDE | met | `DataPlane`'s cursors and base are private |
| C-STRUCT-BOUNDS | not applicable | no generic struct |
| C-STABLE | met | no dependencies |
| C-PERMISSIVE | met | (MIT OR Apache-2.0) AND BSD-3-Clause AND BSD-2-Clause |

Totals: 26 met, 5 not met, 23 not applicable.
