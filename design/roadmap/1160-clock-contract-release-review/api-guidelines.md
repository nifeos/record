# The API Guidelines checklist

An appendix to [the milestone](../1160-clock-contract-release-review.md), giving a verdict on each
of the 54 items of the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) for
`partsfoundry/clock_contract` at `08ceb003`. A finding named in a row is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `ClockPage`, `wall_nanoseconds`, `NOT_BEFORE_NANOSECONDS` |
| C-CONV | not applicable | no conversion method |
| C-GETTER | met | no `get_` prefix; `Reading` exposes fields |
| C-ITER | not applicable | no collection |
| C-ITER-TY | not applicable | no iterator type |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | met | every time ends `_NANOSECONDS`; the refusals open `REFUSED_` |
| C-COMMON-TRAITS | not met | `Reading` has no `Hash` and no `Default` (P1-7); a state and a status have no `Display` (P2-1) |
| C-CONV-TRAITS | not met | no `From` or `TryFrom` between a word and a state, a status or an operation (P0-2); none with `core::time::Duration` (P2-2) |
| C-COLLECT | not applicable | no collection |
| C-SERDE | not applicable | the page and the two message words are the serialized form |
| C-SEND-SYNC | met | `ClockPage` is `Send` and `Sync` by two `unsafe impl` with their reasons; `Reading` is plain data |
| C-GOOD-ERR | not met | a refusal is a `u64` status word with no `Display` and no `core::error::Error` (P1-1) |
| C-NUM-FMT | not applicable | no numeric type of its own |
| C-RW-VALUE | not applicable | no reader or writer in the `std::io` sense |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | not met | the crate page states the identity and the three authorities, and has no example (P1-5) |
| C-EXAMPLE | not met | two of 11 public functions carry one; `ClockPage` and `propose` have none (P1-5) |
| C-QUESTION-MARK | met | no example unwraps; nothing in the crate returns `Result` |
| C-FAILURE | met | `ClockPage::new` has `# Safety`; no function panics in a release build or returns an error. The debug assertion of `propose::request` is in its text, without a `# Panics` heading |
| C-LINK | met | items link to each other; the Linux and FreeBSD file names are plain text |
| C-METADATA | not met | no `documentation` key (P2-3) |
| C-RELNOTES | met | `CHANGELOG.md`, with the first version unreleased |
| C-HIDDEN | met | nothing is `doc(hidden)`; the word indices are private, which P1-3 raises as a gap in the contract |
| C-SMART-PTR | not applicable | `ClockPage` is a handle with methods and no `Deref` |
| C-CONV-SPECIFIC | not applicable | no conversion |
| C-METHOD | not met | `state::is_known(state)` and `policy::decide(current_state, ...)` have a clear receiver and are free functions over `u64` (P0-2) |
| C-NO-OUT | met | every function returns its result |
| C-OVERLOAD | not applicable | no operator |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | met | `ClockPage::new` |
| C-INTERMEDIATE | met | `publish` returns the generation it made, and `Reading` carries the generation it read |
| C-CALLER-CONTROL | met | the caller maps the frame and passes its address; the crate allocates and copies nothing |
| C-GENERIC | not applicable | no parameter a generic would widen |
| C-OBJECT | not applicable | no trait |
| C-NEWTYPE | not met | six kinds of word are `u64` (P0-2, door D2) |
| C-CUSTOM-TYPE | not met | `decide(u64, u64, u64) -> u64` and `publish(u64, u64)` take arguments a caller can swap (P0-2) |
| C-BITFLAG | not applicable | no flag set |
| C-BUILDER | not applicable | no value with many parts |
| C-VALIDATE | not met | `publish` stores any state word; `propose::request` checks its argument in a debug build alone; `publish` is callable on a read-only mapping (P0-1, P0-2) |
| C-DTOR-FAIL | not applicable | no `Drop` |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | met | `ClockPage` and `Reading` derive `Debug` |
| C-DEBUG-NONEMPTY | met | `Reading { state: 0, offset_nanoseconds: 0, generation: 0 }`, and `ClockPage { base: 0x... }` |
| C-SEALED | not applicable | no trait |
| C-STRUCT-PRIVATE | not met | `Reading` has three public fields and no `#[non_exhaustive]` (P0-3); `ClockPage`'s field is private |
| C-NEWTYPE-HIDE | not applicable | no newtype |
| C-STRUCT-BOUNDS | not applicable | no generic type |
| C-STABLE | met | no dependency outside `cfg(loom)` |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 17 met, 11 not met, 26 not applicable.
