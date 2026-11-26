# The API Guidelines checklist

An appendix to [the milestone](../1161-counter-frequency-contract-release-review.md), giving a
verdict on each of the 54 items of the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) for
`partsfoundry/counter_frequency_contract` at `4decec9d`. A finding named in a row is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `CounterFrequencyPage`, `build_page`, `PAGE_CONTENT_BYTES` |
| C-CONV | not applicable | no conversion method |
| C-GETTER | met | `hertz`, with no `get_` prefix |
| C-ITER | not applicable | no collection |
| C-ITER-TY | not applicable | no iterator type |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | met | `MINIMUM_PLAUSIBLE_HERTZ` and `MAXIMUM_PLAUSIBLE_HERTZ`; every size ends `_BYTES` |
| C-COMMON-TRAITS | not met | `CounterFrequencyPage` has `Debug`, `Clone` and `Copy`, and no `PartialEq`, `Eq` or `Hash` (P1-4) |
| C-CONV-TRAITS | not applicable | no value type of its own to convert; the safe decoder of P0-1 is a function |
| C-COLLECT | not applicable | no collection |
| C-SERDE | not applicable | the wire form is the crate's own sixteen bytes |
| C-SEND-SYNC | met | `Send` and `Sync` by `unsafe impl`, each with its argument |
| C-GOOD-ERR | not applicable | no error type; P0-5 waits on the errors decision |
| C-NUM-FMT | not applicable | no numeric type of its own |
| C-RW-VALUE | not applicable | no reader or writer |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | not met | the crate page has the identity and a BUGS section, and no example (P1-2) |
| C-EXAMPLE | not met | `is_plausible`, `build_page` and `hertz` have one; `new` has none (P1-2) |
| C-QUESTION-MARK | met | no example unwraps; each asserts on the `Option` |
| C-FAILURE | met | `new` has a `# Safety` section; no function panics or returns an error |
| C-LINK | met | items link to each other; three names of things outside the crate are not links (P1-1) |
| C-METADATA | not met | no `documentation` key (P2-3) |
| C-RELNOTES | met | `CHANGELOG.md`, one entry for each pre-release |
| C-HIDDEN | met | nothing is `doc(hidden)`; the proofs are behind `cfg(kani)` |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | not applicable | no conversion |
| C-METHOD | met | `hertz` is a method; `is_plausible` and `build_page` take a number and have no receiver |
| C-NO-OUT | met | `build_page` returns its array |
| C-OVERLOAD | not applicable | no operator |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | met | `CounterFrequencyPage::new` |
| C-INTERMEDIATE | not applicable | no intermediate result to expose |
| C-CALLER-CONTROL | met | `build_page` returns the bytes and the caller places them |
| C-GENERIC | not applicable | no parameter a generic would widen |
| C-OBJECT | not applicable | no trait |
| C-NEWTYPE | not met | the address is a bare `u64` cast to a pointer (P0-1), and the rate a bare `u64` that may be zero (P0-2) |
| C-CUSTOM-TYPE | met | `Option<u64>`, and no `bool` argument |
| C-BITFLAG | not applicable | no flag set |
| C-BUILDER | not applicable | no value with many parts |
| C-VALIDATE | not met | `build_page` writes a rate outside the band and `hertz` returns it (P0-2) |
| C-DTOR-FAIL | not applicable | no `Drop` |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | met | the one type derives `Debug` |
| C-DEBUG-NONEMPTY | met | the output names the type and its address, not the rate (P1-4) |
| C-SEALED | not applicable | no trait |
| C-STRUCT-PRIVATE | met | `base` is private |
| C-NEWTYPE-HIDE | not applicable | no newtype |
| C-STRUCT-BOUNDS | not applicable | no generic type |
| C-STABLE | met | no dependencies |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 19 met, 6 not met, 29 not applicable.
