# The API Guidelines checklist

An appendix to [the milestone](../1152-interfaces-note-release-review.md), giving a verdict on each
of the 54 items of the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) for
`partsfoundry/interfaces_note` at `088baba2`. A finding named in a row is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `DeclaredInterface`, `decode_interfaces`, `MAXIMUM_INTERFACES` |
| C-CONV | not applicable | no `as_`, `to_` or `into_` conversion |
| C-GETTER | met | `len`, `is_empty` and `version_of`, with no `get_` prefix |
| C-ITER | not met | `iter` exists and `IntoIterator` does not (P1-6) |
| C-ITER-TY | not met | `iter` returns an opaque type, not an `Iter` (P1-6) |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | met | `NoVersion`, `UnknownVersion`, `WrongLength` |
| C-COMMON-TRAITS | not met | no `Hash` on the value types, no `Ord` on `DeclaredInterface`, nothing on `InterfacesNote` (P1-5) |
| C-CONV-TRAITS | not applicable | no value converts to another |
| C-COLLECT | not applicable | `Interfaces` is a view over bytes and cannot be collected into |
| C-SERDE | not applicable | the crate is its own wire format |
| C-SEND-SYNC | met | every type holds integers, an array or a shared slice |
| C-GOOD-ERR | not met | neither `Error` nor `Refusal` implements `Display` or `core::error::Error` (P1-1) |
| C-NUM-FMT | not applicable | no numeric type of its own |
| C-RW-VALUE | not applicable | no reader or writer |
| C-EVOCATIVE | met | `carry_interfaces!` takes an ordinary slice expression |
| C-MACRO-ATTR | met | `#[cfg(...)]` applies to the macro call as to any item |
| C-ANYWHERE | met | the macro works wherever an item may stand; what a second call does is P0-3 |
| C-MACRO-VIS | not applicable | the static it places is private by design |
| C-MACRO-TY | not applicable | the macro takes no type |
| C-CRATE-DOC | not met | the crate page has no example (P1-4) |
| C-EXAMPLE | not met | six public items have none (P1-4) |
| C-QUESTION-MARK | not met | the examples use `unwrap` (P1-4) |
| C-FAILURE | not met | no `# Errors` or `# Panics` heading (P1-4) |
| C-LINK | met | items link to each other |
| C-METADATA | met | every key the guideline lists is present; what the package carries is P2-6 |
| C-RELNOTES | met | `CHANGELOG.md`, with one line before the first release |
| C-HIDDEN | met | nothing is `doc(hidden)` |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | not applicable | no conversion |
| C-METHOD | met | `version_of` and `check_served` are methods of `Interfaces` |
| C-NO-OUT | met | the encoder returns its array |
| C-OVERLOAD | not applicable | no operator |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | met | `InterfacesNote::of`, and `decode_interfaces` as the one way to an `Interfaces` |
| C-INTERMEDIATE | met | `version_of` exposes the value that `check_served` compares |
| C-CALLER-CONTROL | met | the decoder borrows, and the caller owns every byte |
| C-GENERIC | not applicable | the inputs are slices of one concrete type |
| C-OBJECT | not applicable | no trait |
| C-NEWTYPE | met | an id is a `u64` and a version a `u32`, so two constants in the wrong order do not compile |
| C-CUSTOM-TYPE | met | `DeclaredInterface` names its two fields, and no argument is a `bool` |
| C-BITFLAG | not applicable | no flag set |
| C-BUILDER | not applicable | no value complex enough |
| C-VALIDATE | met | the decoder checks every field, and the encoder refuses a list the decoder would |
| C-DTOR-FAIL | not applicable | no `Drop` |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | not met | `InterfacesNote` has no `Debug` (P1-5) |
| C-DEBUG-NONEMPTY | met | each derived `Debug` names its type |
| C-SEALED | not applicable | no trait |
| C-STRUCT-PRIVATE | not met | `InterfacesNote`'s field is public (P0-2), and `Refusal` is exhaustive (P0-4) |
| C-NEWTYPE-HIDE | met | `Interfaces` hides its slice |
| C-STRUCT-BOUNDS | met | no bound on a declaration |
| C-STABLE | met | no dependencies |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 24 met, 10 not met, 20 not applicable.
