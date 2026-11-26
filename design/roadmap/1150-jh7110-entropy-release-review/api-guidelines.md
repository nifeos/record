# The API Guidelines checklist

An appendix to [the milestone](../1150-jh7110-entropy-release-review.md), giving a verdict on each
of the 54 items of the [Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html)
for `partsfoundry/jh7110_entropy` at `eac91efd`. A finding named in a row is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `GenerationOutcome`, `generation_outcome`, `STATUS_SEEDED` |
| C-CONV | met | `output_bytes` and `take_into` are the only conversions, and neither claims an `as_`, `to_` or `into_` cost it does not have |
| C-GETTER | met | `Pool::remaining_bytes`, with no `get_` prefix |
| C-ITER | not applicable | no collection is iterated |
| C-ITER-TY | not applicable | no iterator type |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | met | `WrongOutputWidth`, `NotReady`, `TakenBytes` |
| C-COMMON-TRAITS | not met | `GenerationOutcome` is `Clone` and `Copy` with the bytes inside (P0-1), and `Pool` is `PartialEq` and `Eq` over bytes still to be served (P0-5) |
| C-CONV-TRAITS | not applicable | no value type converts to another |
| C-COLLECT | not applicable | no collection |
| C-SERDE | not applicable | register words and random bytes have no serialized form here |
| C-SEND-SYNC | met | every public type is `Send` and `Sync`; none holds a pointer |
| C-GOOD-ERR | not met | no error type; `Pool` reports a dry generator as `None`, `false` or a short count (P0-6) |
| C-NUM-FMT | not applicable | no numeric type of its own |
| C-RW-VALUE | not applicable | no reader or writer; the generator is a closure taken by `&mut` |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | met | the crate page names its sources, both device trees and a decode example that runs as a doctest |
| C-EXAMPLE | not met | `interrupt_line`, `output_bytes` and `Pool::refill` have none, and no example performs the register sequence (P1-2) |
| C-QUESTION-MARK | not applicable | no public function returns a `Result`, so no example has an error to propagate |
| C-FAILURE | met | no public function returns a `Result` or panics; `take` documents its clamp and `take_into` its short count |
| C-LINK | met | items link to each other and to the constants they test |
| C-METADATA | met | description, license, repository, documentation, keywords, categories and an `include` list |
| C-RELNOTES | met | `CHANGELOG.md` gives each version's changes and marks the breaking ones |
| C-HIDDEN | met | nothing is `doc(hidden)`, and the proofs are private |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | not applicable | no conversion between types |
| C-METHOD | met | the pool's operations are methods; the decode is a free function of three register reads |
| C-NO-OUT | met | `take_into` fills a caller's slice, as `Read::read` does, and returns the count |
| C-OVERLOAD | not applicable | no operator |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | met | `Pool::new`, with `Default` beside it |
| C-INTERMEDIATE | met | `generation_outcome` and `output_bytes` expose the two steps of an answer |
| C-CALLER-CONTROL | met | the caller owns the register access, the generator, the output slice, the lock and every bound |
| C-GENERIC | met | the generator is `impl FnMut() -> Option<[u8; 32]>` |
| C-OBJECT | not applicable | no trait |
| C-NEWTYPE | not met | `STAT` and `ISTAT` reach `generation_outcome` as two bare `u32`s (P0-3) |
| C-CUSTOM-TYPE | met | `GenerationOutcome` and `TakenBytes` where a `bool` or a pair would be ambiguous; `refill` returns a `bool` that P0-6 replaces |
| C-BITFLAG | met | the flags are `u32` constants of the register's width, combined with `\|` |
| C-BUILDER | not applicable | no type with many optional parts |
| C-VALIDATE | met | the decode checks lockup, work in flight, the seed and the width before it serves bytes, and `take` clamps its count |
| C-DTOR-FAIL | met | `Pool`'s `Drop` zeroes an array and cannot fail |
| C-DTOR-BLOCK | met | `Pool`'s `Drop` does not block |
| C-DEBUG | met | every public type implements `Debug` |
| C-DEBUG-NONEMPTY | met | each output names its type; `GenerationOutcome`'s prints the ready bytes, which P0-1 removes |
| C-SEALED | not applicable | no trait |
| C-STRUCT-PRIVATE | not met | `Discovered` and `TakenBytes` have public fields; `Discovered` cannot grow (P0-4), and `TakenBytes` is a plain pair by design |
| C-NEWTYPE-HIDE | met | `Pool`'s buffer and cursor are private |
| C-STRUCT-BOUNDS | not applicable | no generic struct |
| C-STABLE | met | no dependencies |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 27 met, 5 not met, 22 not applicable.
