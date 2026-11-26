# The API Guidelines checklist

An appendix to [the milestone](../1163-environment-contract-release-review.md), giving a verdict
on each of the 54 items of the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) for
`partsfoundry/environment_contract` at `62ea88d9`. A finding named in a row is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `PageBuilder`, `time_zone`, `PAGE_CONTENT_BYTES` |
| C-CONV | not applicable | no conversion method |
| C-GETTER | met | `time_zone`, `locale` and `terminal_type`, with no `get_` prefix |
| C-ITER | not applicable | the lists are slices; the crate has no collection type |
| C-ITER-TY | not applicable | no iterator type |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | met | `UnknownTimeZone`, `UnknownLocale`; every cap is `MAXIMUM_*_BYTES` |
| C-COMMON-TRAITS | not met | three types have no `Hash`, and `ConfigurationPage` has no `PartialEq` (P1-5) |
| C-CONV-TRAITS | not met | no `TryFrom<&[u8]>` for `ConfigurationView` (P1-6) |
| C-COLLECT | not applicable | no collection |
| C-SERDE | not applicable | the page is the serialized form, and the crate defines it |
| C-SEND-SYNC | met | `ConfigurationPage` is `Send` and `Sync` by an `unsafe impl` with its reason; the rest are plain data |
| C-GOOD-ERR | met | `Refused` has `Debug`, `Display` and `core::error::Error`; P0-5 is about what it carries |
| C-NUM-FMT | not applicable | no numeric type of its own |
| C-RW-VALUE | not applicable | no reader or writer |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | not met | the crate page states the purpose and has no example and no layout (P1-3, P1-4) |
| C-EXAMPLE | not met | the three types have one; no method, function or constant has (P1-3) |
| C-QUESTION-MARK | not met | all four examples call `unwrap` (P1-3) |
| C-FAILURE | not met | `# Safety` is present on `ConfigurationPage::new`; no setter has `# Errors` (P1-3) |
| C-LINK | met | items link to each other and to the lists |
| C-METADATA | met | every key is present, `documentation` included |
| C-RELNOTES | met | `CHANGELOG.md`, with the first version unreleased |
| C-HIDDEN | met | nothing is `doc(hidden)`; the proofs are behind `cfg(kani)` |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | not applicable | no conversion |
| C-METHOD | met | every function with a receiver is a method |
| C-NO-OUT | met | `build` returns the page (P2-6 adds a second entry and removes none) |
| C-OVERLOAD | not applicable | no operator |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | met | `PageBuilder::new`, `ConfigurationView::new`, `ConfigurationPage::new` |
| C-INTERMEDIATE | not met | the reader discards why it answered `None` (P0-4), and `is_known_*` discards the member it found (P2-2) |
| C-CALLER-CONTROL | met | nothing allocates; the one copy is the 107-byte page (P2-6) |
| C-GENERIC | not applicable | the setters take `&str`, and no wider bound would serve a caller |
| C-OBJECT | not applicable | no trait |
| C-NEWTYPE | not met | an address is a `u64` (P0-2), and a checked value is a `&str` (P2-2, door D10) |
| C-CUSTOM-TYPE | met | the refusal is an enum, and no function takes a `bool` or an `Option` |
| C-BITFLAG | not applicable | no flag set |
| C-BUILDER | met | `PageBuilder`, with setters that return `Self` |
| C-VALIDATE | met | the setters check each value, and the reader checks the magic, each length and each member |
| C-DTOR-FAIL | not applicable | no `Drop` |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | met | every public type derives `Debug` |
| C-DEBUG-NONEMPTY | met | no output is empty; `ConfigurationView`'s is 107 numbers (P1-2) |
| C-SEALED | not applicable | no trait |
| C-STRUCT-PRIVATE | met | every field is private |
| C-NEWTYPE-HIDE | not applicable | no newtype |
| C-STRUCT-BOUNDS | not applicable | no trait bound on a type; the lifetime of `PageBuilder` is P0-1 |
| C-STABLE | met | no dependencies |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 21 met, 8 not met, 25 not applicable.
