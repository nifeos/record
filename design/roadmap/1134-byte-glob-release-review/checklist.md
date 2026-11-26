# `byte_glob` against the Rust API Guidelines checklist

An appendix to [the release review](../1134-byte-glob-release-review.md). Each of the 54 items of
the checklist is marked met, not met, or not applicable, against `partsfoundry/byte_glob` at
`a095cd8`. A "not met" names the finding that answers it.

| code | mark | note |
|---|---|---|
| C-CASE | met | snake case for the functions, camel case for the two types |
| C-CONV | not applicable | no `as_`, `to_` or `into_` conversion |
| C-GETTER | met | `Outcome`'s two fields are public data, so no getter is owed |
| C-ITER | not applicable | no collection |
| C-ITER-TY | not applicable | no iterator |
| C-FEATURE | not applicable | no Cargo feature |
| C-WORD-ORDER | met | the seven names were ratified and pass every later rule |
| C-COMMON-TRAITS | not met | item 1: no `Hash` on either type, no `Default` on `LeadingDot` |
| C-CONV-TRAITS | not applicable | no conversion between types |
| C-COLLECT | not applicable | no collection |
| C-SERDE | not applicable | a two-valued policy and a result hold nothing worth storing |
| C-SEND-SYNC | met | both types are plain `Copy` data, so `Send` and `Sync` hold automatically |
| C-GOOD-ERR | not applicable | no error type: every pair of byte strings has an answer |
| C-NUM-FMT | not applicable | no number-like type |
| C-RW-VALUE | not applicable | no reader or writer |
| C-EVOCATIVE | not applicable | no macro |
| C-MACRO-ATTR | not applicable | no macro |
| C-ANYWHERE | not applicable | no macro |
| C-MACRO-VIS | not applicable | no macro |
| C-MACRO-TY | not applicable | no macro |
| C-CRATE-DOC | not met | item 2: thorough prose, but no code example and a fragment for a summary |
| C-EXAMPLE | not met | item 2: `has_magic` and `step_bound` have none |
| C-QUESTION-MARK | not applicable | no example calls a fallible function |
| C-FAILURE | met | each function states that it is total and never panics |
| C-LINK | met | intra-doc links throughout |
| C-METADATA | not met | item 6: no `documentation` field |
| C-RELNOTES | met | `CHANGELOG.md`, one line per change |
| C-HIDDEN | met | nothing hidden; no implementation detail in the public pages |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | not applicable | no conversion |
| C-METHOD | not applicable | free functions over two slices; no receiver is clearer |
| C-NO-OUT | met | `match_steps` returns `Outcome` rather than filling an out-parameter |
| C-OVERLOAD | not applicable | no overloaded name |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | not applicable | the crate builds `Outcome`; a caller never constructs one |
| C-INTERMEDIATE | met | `match_steps` exposes the step count that `matches_with` computes |
| C-CALLER-CONTROL | met | borrows both inputs; the caller owns every byte |
| C-GENERIC | met | concrete `&[u8]` on purpose; see one-way door 2 |
| C-OBJECT | not applicable | no trait |
| C-NEWTYPE | met | `LeadingDot` stands for a flag bit |
| C-CUSTOM-TYPE | met | `LeadingDot` rather than a `bool` argument |
| C-BITFLAG | not applicable | one option, so no flag set |
| C-BUILDER | not applicable | no construction with options |
| C-VALIDATE | met | no input is invalid: a malformed pattern means itself |
| C-DTOR-FAIL | not applicable | no destructor |
| C-DTOR-BLOCK | not applicable | no destructor |
| C-DEBUG | met | both types derive `Debug` |
| C-DEBUG-NONEMPTY | met | derived output always names the variant or the fields |
| C-SEALED | not applicable | no trait |
| C-STRUCT-PRIVATE | met | `Outcome`'s fields are public but `#[non_exhaustive]` keeps it extendable |
| C-NEWTYPE-HIDE | not applicable | no wrapped implementation type |
| C-STRUCT-BOUNDS | not applicable | no generic type |
| C-STABLE | met | no dependency at all |
| C-PERMISSIVE | met | `MIT OR Apache-2.0` |
