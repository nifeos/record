# The API Guidelines checklist

An appendix to [the milestone](../1159-byte-sink-contract-release-review.md), giving a verdict on
each of the 54 items of the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) for
`partsfoundry/byte_sink_contract` at `8a477c6a`. A finding named in a row is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `MessageWords`, `end_of_stream`, `MAXIMUM_INLINE_BYTES` |
| C-CONV | not applicable | no `as_`, `to_` or `into_` conversion |
| C-GETTER | met | `len`, `kind` and `severity`, with no `get_` prefix |
| C-ITER | not applicable | no collection; P1-6 would add an iterator |
| C-ITER-TY | not applicable | no iterator type |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | met | `OPERATION_BYTES` and `OPERATION_END_OF_STREAM`; `KIND_SHIFT` and `SEVERITY_SHIFT` |
| C-COMMON-TRAITS | not met | no `Hash` on the three types (P1-5) |
| C-CONV-TRAITS | not met | no `From` between `MessageWords` and `[u64; 3]` (P2-3) |
| C-COLLECT | not applicable | no collection |
| C-SERDE | not applicable | the crate is its own wire format |
| C-SEND-SYNC | met | every type holds integers alone |
| C-GOOD-ERR | not met | `Message::Malformed` and `Sent` are not error types (P0-3, P0-4) |
| C-NUM-FMT | not applicable | no numeric type of its own |
| C-RW-VALUE | not applicable | no reader or writer |
| C-EVOCATIVE | not applicable | no macro |
| C-MACRO-ATTR | not applicable | no macro |
| C-ANYWHERE | not applicable | no macro |
| C-MACRO-VIS | not applicable | no macro |
| C-MACRO-TY | not applicable | no macro |
| C-CRATE-DOC | not met | the crate page has a table and its reasons, and no example (P1-4) |
| C-EXAMPLE | not met | nine of eleven public functions have none (P1-4) |
| C-QUESTION-MARK | not applicable | no function returns a `Result`; the examples end a wrong arm with `unreachable!` |
| C-FAILURE | met | no public function panics, and `Message::Malformed` lists what `unpack` refuses |
| C-LINK | met | items link to each other |
| C-METADATA | met | every key the guideline requires is present; what the package carries is P2-4 |
| C-RELNOTES | met | `CHANGELOG.md`, with one line before the first release |
| C-HIDDEN | met | nothing is `doc(hidden)` |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | not applicable | no conversion |
| C-METHOD | not met | five functions with a clear receiver are free functions (P0-6) |
| C-NO-OUT | not met | `unpack` writes through `out`; the measurement favors it (P2-6) |
| C-OVERLOAD | not applicable | no operator |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | met | `MessageWords::new` |
| C-INTERMEDIATE | met | `pack` returns the count it took beside the words |
| C-CALLER-CONTROL | met | `pack` borrows, and the caller owns the buffer `unpack` fills |
| C-GENERIC | not applicable | the one input is a byte slice |
| C-OBJECT | not applicable | no trait |
| C-NEWTYPE | not met | a first word is a bare `u64` and a level a bare `u8` (P0-6, P0-2) |
| C-CUSTOM-TYPE | not met | a level is a `u8` and an opcode a `u8` constant (P0-2, P0-8) |
| C-BITFLAG | not applicable | no flag set |
| C-BUILDER | not applicable | no value complex enough |
| C-VALIDATE | not met | `unpack` accepts three things the documentation rules out, and `with_severity` clamps in silence (P0-1, P0-2) |
| C-DTOR-FAIL | not applicable | no `Drop` |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | met | all three types derive `Debug` |
| C-DEBUG-NONEMPTY | met | each derived `Debug` names its type |
| C-SEALED | not applicable | no trait |
| C-STRUCT-PRIVATE | not met | `Message` and `Sent` are exhaustive (P0-3, P0-4); the public fields of `MessageWords` hold no invariant (P0-7) |
| C-NEWTYPE-HIDE | not applicable | no wrapper type |
| C-STRUCT-BOUNDS | not applicable | no generic type |
| C-STABLE | met | no dependencies |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 16 met, 11 not met, 27 not applicable.
