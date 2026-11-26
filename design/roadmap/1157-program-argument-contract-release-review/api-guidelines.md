# The API Guidelines checklist

An appendix to [the milestone](../1157-program-argument-contract-release-review.md), giving a
verdict on each of the 54 items of the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) for
`partsfoundry/program_argument_contract` at `b097970b`. A finding named in a row is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `ArgumentPage`, `record_bytes`, `MAXIMUM_RECORDS_BYTES` |
| C-CONV | not applicable | no `as_`, `to_` or `into_` conversion |
| C-GETTER | met | `len`, `is_empty` and `remaining_bytes`, with no `get_` prefix |
| C-ITER | not met | `iter` exists and `IntoIterator` does not (P2-1) |
| C-ITER-TY | met | `iter` returns the named `Iter` |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | not met | `PushRefused` names the operation and `WrongPageLength` the cause (P0-2) |
| C-COMMON-TRAITS | not met | no `PartialEq`, `Eq`, `Hash` or `Default` on `ArgumentPage`, no `Hash` on the refusals (P1-3) |
| C-CONV-TRAITS | not applicable | no value converts to another |
| C-COLLECT | not applicable | `ArgumentPage` is a view over bytes, and a push can fail |
| C-SERDE | not applicable | the crate is its own wire format |
| C-SEND-SYNC | met | the types hold slices and integers only |
| C-GOOD-ERR | not met | neither refusal implements `Display` or `core::error::Error` (P1-2) |
| C-NUM-FMT | not applicable | no numeric type of its own |
| C-RW-VALUE | not applicable | no reader or writer trait is taken |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | not met | the crate page explains the layout and shows no code (P1-4) |
| C-EXAMPLE | not met | `PageBuilder` alone has an example (P1-4) |
| C-QUESTION-MARK | not met | the examples call `unwrap` (P1-4) |
| C-FAILURE | met | `# Errors` on `new` and `push`, `# Safety` on `from_virtual_address` |
| C-LINK | met | items link to each other and to the constants |
| C-METADATA | not met | no `documentation` key (P2-4) |
| C-RELNOTES | met | `CHANGELOG.md` records the one removal before the first release |
| C-HIDDEN | met | `check`, `split_record` and the prefix width are private; nothing is `doc(hidden)` |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | not applicable | no conversion |
| C-METHOD | met | every operation is a method of the builder or the page; `record_bytes` has no receiver to take |
| C-NO-OUT | met | the builder borrows the caller's frame for its whole life, and `finish` returns the count |
| C-OVERLOAD | not applicable | no operator |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | met | `PageBuilder::new`, `ArgumentPage::parse` and `ArgumentPage::from_virtual_address` |
| C-INTERMEDIATE | met | `remaining_bytes` and the count from `finish` |
| C-CALLER-CONTROL | met | the caller owns the page, and every argument is borrowed |
| C-GENERIC | met | `push` and `parse` take plain byte slices |
| C-OBJECT | not applicable | no trait |
| C-NEWTYPE | not met | a virtual address is a bare `u64` (P0-5) |
| C-CUSTOM-TYPE | met | no `bool` or `Option` argument |
| C-BITFLAG | not applicable | no flag set |
| C-BUILDER | met | `PageBuilder` |
| C-VALIDATE | not met | `finish` writes a line after a refused `push` (P0-1), and `new` checks at run time a length the type can state (P0-4) |
| C-DTOR-FAIL | not applicable | no `Drop` |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | met | all five public types implement `Debug` |
| C-DEBUG-NONEMPTY | met | `EMPTY` prints its type name and both fields |
| C-SEALED | not applicable | no trait |
| C-STRUCT-PRIVATE | met | every field is private |
| C-NEWTYPE-HIDE | met | `Iter` hides how the walk is kept |
| C-STRUCT-BOUNDS | met | no bound on a declaration |
| C-STABLE | met | no dependencies |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 23 met, 10 not met, 21 not applicable.
