# The API Guidelines checklist

An appendix to [the milestone](../1162-entropy-contract-release-review.md), giving a verdict on
each of the 54 items of the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) for
`partsfoundry/entropy_contract` at `5150f14f`. A finding named in a row is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `Refusal`, `fill_with`, `MAXIMUM_BYTES` |
| C-CONV | not applicable | no conversion method |
| C-GETTER | met | `operation` and `requested_bytes`, with no `get_` prefix; `GET` is the opcode's own name |
| C-ITER | not applicable | no collection type |
| C-ITER-TY | not applicable | no iterator type |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | met | `OperationOutOfRange` and `StepOutOfRange`; every step opens `STEP_` |
| C-COMMON-TRAITS | not met | the three refusal types have no `Hash` (P1-5) |
| C-CONV-TRAITS | not applicable | no type that converts to or from another |
| C-COLLECT | not applicable | no collection |
| C-SERDE | not applicable | the wire form is two words, built and read by the crate's own functions |
| C-SEND-SYNC | met | every type is plain data |
| C-GOOD-ERR | not met | `Refusal` has no `Display` and no `core::error::Error` (P1-2) |
| C-NUM-FMT | not applicable | no numeric type of its own |
| C-RW-VALUE | not applicable | no reader or writer |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | met | the crate page states the exchange, a service example and its `BUGS` |
| C-EXAMPLE | met | every public function has an example; the constants and the refusal types appear in them |
| C-QUESTION-MARK | not met | eight lines of the item examples call `unwrap` or `expect` (P1-4) |
| C-FAILURE | not met | `fill_with` has no `# Errors` section (P1-4) |
| C-LINK | met | items link to each other; the note of interfaces the README names is not a link (P1-1) |
| C-METADATA | met | description, license, repository, documentation, keywords and categories |
| C-RELNOTES | met | `CHANGELOG.md`, with a section for 0.1.0-pre.1 |
| C-HIDDEN | met | nothing is `doc(hidden)`; the proofs are behind `cfg(kani)` |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | not applicable | no conversion |
| C-METHOD | not applicable | the crate has no type that could own the functions (P2-5, door D10) |
| C-NO-OUT | met | `copy_delivered_bytes` and `fill_with` fill a caller's buffer, as `Read::read` does, and return the result |
| C-OVERLOAD | not applicable | no operator |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | not applicable | no type with a constructor |
| C-INTERMEDIATE | not met | `ShortReply` carries both counts; `NoService` drops the word it read (P0-3) |
| C-CALLER-CONTROL | met | the caller owns every buffer, and `reply` borrows its bytes |
| C-GENERIC | met | `readiness` takes any `IntoIterator` of `u8` and `fill_with` any `FnMut`; a slice needs `copied` (P2-2) |
| C-OBJECT | not applicable | no trait |
| C-NEWTYPE | not met | a one-byte opcode and step are `u64` (P0-1), and every word is a bare `u64` (P2-5, door D10) |
| C-CUSTOM-TYPE | met | no `bool` or `Option` argument; `Refusal` names its fields |
| C-BITFLAG | not applicable | no flag set |
| C-BUILDER | not applicable | no value with many parts |
| C-VALIDATE | not met | a run-time check stands where a `u8` would do (P0-1), and a zero count passes (P0-5) |
| C-DTOR-FAIL | not applicable | no `Drop` |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | met | the three types derive `Debug` |
| C-DEBUG-NONEMPTY | met | the derived output names the type, the variant and its fields |
| C-SEALED | not applicable | no trait |
| C-STRUCT-PRIVATE | not met | a caller can build both unit refusals, and neither can gain a field (P0-2) |
| C-NEWTYPE-HIDE | not applicable | no newtype |
| C-STRUCT-BOUNDS | not applicable | no generic type |
| C-STABLE | met | no dependencies |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 18 met, 8 not met, 28 not applicable.
