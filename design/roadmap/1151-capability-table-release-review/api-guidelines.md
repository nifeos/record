# The API Guidelines checklist

An appendix to [the milestone](../1151-capability-table-release-review.md), giving a verdict on
each of the 54 items of the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) for
`partsfoundry/capability_table` at `a0e8b159`. A finding or a door named in a row is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `CapabilityTable`, `insert_at_or_above`, `MAXIMUM_SLOTS` |
| C-CONV | met | `bits` and `from_bits`, as `bitflags` spells them; P0-3 asks what `from_bits` means |
| C-GETTER | met | `capacity`, `used` and `size`, with no `get_` prefix; `get` is the lookup |
| C-ITER | met | `iter` |
| C-ITER-TY | not met | `iter` returns `impl Iterator`, so the type has no name (P2-2) |
| C-FEATURE | met | `peak` has no placeholder word; its name waits on the shared decision (P2-4) |
| C-WORD-ORDER | met | `NoSuchSlot`, `NoFreeSlot`, `SlotOccupied` |
| C-COMMON-TRAITS | not met | `Rights` lacks `Hash` and `Default`, `Capability` lacks `Hash`, and the table derives nothing (P1-6) |
| C-CONV-TRAITS | not applicable | `Rights` converts through the `const` functions `bits` and `from_bits`, which a trait cannot be |
| C-COLLECT | not applicable | a table of fixed size that places by slot is not built from an iterator |
| C-SERDE | not applicable | no dependencies; rights cross a boundary as `bits()` |
| C-SEND-SYNC | met | every public type is `Send` and `Sync` when the object is |
| C-GOOD-ERR | met | `Error` has `Display` and `core::error::Error`; P0-2 asks for `#[non_exhaustive]` |
| C-NUM-FMT | not met | `Rights` is a bit set with no `Binary` or `LowerHex` (P2-1) |
| C-RW-VALUE | not applicable | no reader or writer |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | met | the crate page says what the table is and shows the rights algebra |
| C-EXAMPLE | not met | two examples, both of `Rights`; none of the table or of `delegate` (P1-3) |
| C-QUESTION-MARK | not applicable | the two examples call nothing fallible; P1-3 asks that the new one use `?` |
| C-FAILURE | not met | no `# Errors` section on any of the seven fallible public functions (P1-4) |
| C-LINK | met | items link to each other and to the harness that proves each |
| C-METADATA | not met | no `documentation` key (P2-6) |
| C-RELNOTES | met | `CHANGELOG.md` gives the unreleased changes and their reasons |
| C-HIDDEN | met | the storage module, the free-slot set and the proofs are private; nothing is `doc(hidden)` |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | not applicable | no conversion between two of its types |
| C-METHOD | met | every table operation is a method; `highest_seen` is free because it belongs to no table |
| C-NO-OUT | met | `derive` and `get` return the capability, and `insert` returns the slot |
| C-OVERLOAD | not applicable | no operator; `union` and `intersect` are named so that a widening is visible at the call |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | met | `new` and `with_size` on the table; `Capability` has no constructor (P0-1) |
| C-INTERMEDIATE | met | `derive` hands back the narrowed copy for the caller to file, in this table or another |
| C-CALLER-CONTROL | met | the caller owns the storage, picks the size and the slot, and decides where a copy lands; P2-3 covers the `Copy` bound |
| C-GENERIC | met | generic over the object and the storage; `delete_matching` takes any `FnMut(&O) -> bool` |
| C-OBJECT | not applicable | no traits |
| C-NEWTYPE | met | `Rights` wraps its word; the slot number stays a `u64` on purpose (D7) |
| C-CUSTOM-TYPE | not met | `highest_seen` returns `(usize, usize)`, whose order is in the documentation alone (P2-4) |
| C-BITFLAG | met | `Rights` is a bit set with named constants, not an enum |
| C-BUILDER | not applicable | no type with many optional parts |
| C-VALIDATE | met | every slot number is checked, a size above the storage is refused, a storage above `MAXIMUM_SLOTS` fails to compile, and `from_bits` masks |
| C-DTOR-FAIL | not applicable | no `Drop` |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | not met | `CapabilityTable` has no `Debug` (P1-6) |
| C-DEBUG-NONEMPTY | met | `Rights::NONE` prints `Rights(0)` |
| C-SEALED | not applicable | no traits |
| C-STRUCT-PRIVATE | not met | `Capability` has two public fields (P0-1) |
| C-NEWTYPE-HIDE | met | `Rights` hides its `NonZeroU32` and its marker bit |
| C-STRUCT-BOUNDS | met | neither struct states a bound; the `impl` blocks do (P2-3) |
| C-STABLE | met | no dependencies |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 26 met, 9 not met, 19 not applicable.
