# The API Guidelines checklist

An appendix to [the milestone](../1165-terminal-contract-release-review.md), giving a verdict on
each of the 54 items of the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) for
`partsfoundry/terminal_contract` at `591aed99`. A finding named in a row is the block's. The crate
declares no type, no trait and no macro, which is why so many rows do not apply.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `OPERATION_WRITE`, `is_retry`, `admits` |
| C-CONV | not applicable | no conversion method |
| C-GETTER | met | `operation` and `len` read a field with no `get_` prefix |
| C-ITER | not applicable | no collection |
| C-ITER-TY | not applicable | no iterator type |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | not met | `OPERATION_INTRCOUNT` beside `OPERATION_SUSPEND_COUNT`, and `OPERATION_READLINE` beside `OPERATION_READ_LINE_BYTES`; the badges end `_BADGE` while the flags open `FLAG_` (P0-6) |
| C-COMMON-TRAITS | not applicable | no type |
| C-CONV-TRAITS | not applicable | no type; P0-1 adds the types and their conversions |
| C-COLLECT | not applicable | no collection |
| C-SERDE | not applicable | the words are the serialized form |
| C-SEND-SYNC | not applicable | no type |
| C-GOOD-ERR | not met | `decode` answers `None` with no cause, and a refusal is a `u64` with no `Display` and no `core::error::Error` (P1-1) |
| C-NUM-FMT | not applicable | no numeric type of its own |
| C-RW-VALUE | not applicable | no reader or writer in the `std::io` sense |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | not met | the crate page describes the call and the two pages, and has no example (P1-4) |
| C-EXAMPLE | not met | one of six functions carries one (P1-4) |
| C-QUESTION-MARK | met | the one example asserts and unwraps nothing |
| C-FAILURE | not met | `req` drops the bits of an operation past 255 and of a length past 32 bits, and its text says neither (P0-1) |
| C-LINK | met | items link to each other |
| C-METADATA | not met | no `documentation` key (P2-4) |
| C-RELNOTES | met | `CHANGELOG.md`, with the first version unreleased; P2-6 raises its dates |
| C-HIDDEN | met | nothing is `doc(hidden)`, and the one private item is the reserved-bits mask |
| C-SMART-PTR | not applicable | no type |
| C-CONV-SPECIFIC | not applicable | no conversion |
| C-METHOD | not met | all six functions are free functions over `u64` with a clear receiver (P0-1) |
| C-NO-OUT | met | every function returns its result |
| C-OVERLOAD | not applicable | no operator |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | not applicable | no type |
| C-INTERMEDIATE | met | `decode` returns the operation and the count together |
| C-CALLER-CONTROL | met | the crate allocates and copies nothing |
| C-GENERIC | not applicable | no parameter a generic would widen |
| C-OBJECT | not applicable | no trait |
| C-NEWTYPE | not met | seven kinds of word are `u64` (P0-1, door D1) |
| C-CUSTOM-TYPE | not met | `admits(u64, u64)` and `is_retry(u64, u64)` take arguments a caller can swap, and `decode` answers a pair (P0-1, P0-2) |
| C-BITFLAG | not met | three reply flags and two start bits are loose `u64` constants (P0-1) |
| C-BUILDER | not applicable | no value with many parts |
| C-VALIDATE | not met | `req` masks its arguments (P0-1), and `decode` passes any count for any operation (P0-5) |
| C-DTOR-FAIL | not applicable | no `Drop` |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | not applicable | no type |
| C-DEBUG-NONEMPTY | not applicable | no type |
| C-SEALED | not applicable | no trait |
| C-STRUCT-PRIVATE | not applicable | no struct |
| C-NEWTYPE-HIDE | not applicable | no newtype |
| C-STRUCT-BOUNDS | not applicable | no generic type |
| C-STABLE | met | no dependency |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 11 met, 11 not met, 32 not applicable.
