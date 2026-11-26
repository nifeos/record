# The API Guidelines checklist

An appendix to [the milestone](../1158-block-roster-contract-release-review.md), giving a verdict
on each of the 54 items of the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) for
`partsfoundry/block_roster_contract` at `f0c199ac`. A finding named in a row is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `Roster`, `entry_capacity`, `HEADER_BYTES` |
| C-CONV | not applicable | no conversion method |
| C-GETTER | met | `len`, `get`, `transport_name`, with no `get_` prefix |
| C-ITER | not met | `devices` stands where the convention has `iter`; the name is ratified, and P1-1 adds `IntoIterator` beside it |
| C-ITER-TY | not met | the iterator is an opaque `impl ExactSizeIterator`, so no type is named for it (P1-1) |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | met | `CountBeyondPage`, `CapacityBeyondPage`, `CountBeyondCapacity`; every size ends `_BYTES` |
| C-COMMON-TRAITS | not met | `Roster` has no `PartialEq`, `Eq` or `Hash`; the two errors have no `Hash` (P1-2) |
| C-CONV-TRAITS | not met | no `TryFrom<&[u8]>` for `Roster` (P2-1) |
| C-COLLECT | not applicable | `Roster` borrows a page and cannot grow |
| C-SERDE | not applicable | the crate is its own wire form |
| C-SEND-SYNC | met | every type is plain data or a shared borrow |
| C-GOOD-ERR | not met | both errors have `Display` and `core::error::Error`; `TooManyDevices` names one cause for two (P0-4) |
| C-NUM-FMT | not applicable | no numeric type of its own |
| C-RW-VALUE | not applicable | no reader or writer type |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | not met | the crate page has the layout, the trust rules and the identity, and no example (P1-3) |
| C-EXAMPLE | not met | `write` has the one example among nine public functions (P1-3) |
| C-QUESTION-MARK | not met | both examples call `unwrap` (P1-3) |
| C-FAILURE | not met | `write` and `Roster::read` name their refusals in prose, under no `# Errors` heading (P1-3) |
| C-LINK | met | the items link to each other |
| C-METADATA | met | description, license, repository, documentation, readme, keywords and categories |
| C-RELNOTES | met | `CHANGELOG.md` has a line for each change; its headings carry no date (P2-5) |
| C-HIDDEN | met | the one hidden item is the README doctest holder, behind `cfg(doctest)` |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | not applicable | no conversion |
| C-METHOD | not met | `write(page, devices)` is a free function beside `Roster::read`; the contract-layout decision places both (P0-6) |
| C-NO-OUT | met | `write` fills the caller's page, which is the page's point, and returns its refusal |
| C-OVERLOAD | not applicable | no operator |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | not met | `Device` has no `new` (P0-3); `Roster::read` is a checked conversion and not a constructor |
| C-INTERMEDIATE | met | `read` returns the borrowed entries it checked, and nothing it computed is lost |
| C-CALLER-CONTROL | met | the caller owns the page on both sides, and `read` copies nothing |
| C-GENERIC | not applicable | a page is a byte slice, and no parameter would widen |
| C-OBJECT | not applicable | no trait |
| C-NEWTYPE | not met | a transport and an ordinal are both `u32` (P0-2) |
| C-CUSTOM-TYPE | not met | `count_by_transport(u32)` takes any number (P0-2) |
| C-BITFLAG | not applicable | no flag set |
| C-BUILDER | not applicable | a roster has a list and nothing else |
| C-VALIDATE | met | `read` checks the header before it lends an entry, and `write` checks room before it writes |
| C-DTOR-FAIL | not applicable | no `Drop` |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | met | every public type derives `Debug` |
| C-DEBUG-NONEMPTY | met | no output is empty; `Roster` prints its entries as raw bytes (P1-2) |
| C-SEALED | not applicable | no trait |
| C-STRUCT-PRIVATE | not met | `Device`'s fields are public (P0-3); `Roster`'s are private |
| C-NEWTYPE-HIDE | not applicable | no newtype; `devices` already hides its adapter chain, at the cost P1-1 names |
| C-STRUCT-BOUNDS | not applicable | no generic type |
| C-STABLE | met | no dependencies |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 16 met, 14 not met, 24 not applicable.
