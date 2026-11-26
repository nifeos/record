# The API Guidelines checklist

An appendix to [the milestone](../1153-address-space-layout-release-review.md), giving a verdict
on each of the 54 items of the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) for
`partsfoundry/address_space_layout` at `9568826f`. A finding named in a row is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `Band`, `check_image`, `PAGE_BYTES` |
| C-CONV | not applicable | no conversion method |
| C-GETTER | met | `bytes`, with no `get_` prefix |
| C-ITER | not applicable | `BANDS` is a slice; the crate has no collection type |
| C-ITER-TY | not applicable | no iterator type |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | met | every address ends `_VIRTUAL_ADDRESS`; `TooLarge`, `OutsideBand` |
| C-COMMON-TRAITS | not met | `Band` and `ImagePlacement` have no `Hash` (P1-4) |
| C-CONV-TRAITS | not met | no `From` or `TryFrom` with `core::ops::Range<u64>` (P2-3) |
| C-COLLECT | not applicable | no collection |
| C-SERDE | not applicable | constants and a range; no serialized form |
| C-SEND-SYNC | met | every type is plain data |
| C-GOOD-ERR | not met | `ImagePlacement` has `Display` and no `core::error::Error` (P0-3) |
| C-NUM-FMT | not applicable | no numeric type of its own |
| C-RW-VALUE | not applicable | no reader or writer |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | not met | the crate page has the table and the reasons, and no example (P1-3) |
| C-EXAMPLE | not met | three items have one; `pair_page` and the `Band` methods have none (P1-3) |
| C-QUESTION-MARK | met | no example unwraps a success; `unwrap_err` shows the refusal |
| C-FAILURE | not met | no `# Panics` and no `# Errors` section (P1-3) |
| C-LINK | met | items link to each other; the names of other crates are not links (P1-1) |
| C-METADATA | not met | no `documentation` key (P2-5) |
| C-RELNOTES | met | `CHANGELOG.md`, with the first version unreleased |
| C-HIDDEN | met | nothing is `doc(hidden)`; the proofs are behind `cfg(kani)` |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | not applicable | no conversion |
| C-METHOD | not met | `window(band, start, bytes)` has a clear receiver and is a free function; its signature is ratified by milestone 1076 (what an outside maintainer would fix before it leaves), and the block does not reopen it |
| C-NO-OUT | met | every function returns its result |
| C-OVERLOAD | not applicable | no operator |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | met | `Band::new` |
| C-INTERMEDIATE | met | `ImagePlacement` carries the bounds it refused |
| C-CALLER-CONTROL | not applicable | nothing is copied or placed for the caller |
| C-GENERIC | not applicable | no parameter a generic would widen |
| C-OBJECT | not applicable | no trait |
| C-NEWTYPE | not met | a checked address is a bare `u64` (P2-7, door D10) |
| C-CUSTOM-TYPE | met | `window` takes a `Band`, not two more numbers |
| C-BITFLAG | not applicable | no flag set |
| C-BUILDER | not applicable | no value with many parts |
| C-VALIDATE | not met | a `Band` literal skips `Band::new` (P0-1); `check_image` takes bounds off a page (P0-4) |
| C-DTOR-FAIL | not applicable | no `Drop` |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | met | both types derive `Debug` |
| C-DEBUG-NONEMPTY | met | the derived output names the type and its fields, in decimal (P2-2) |
| C-SEALED | not applicable | no trait |
| C-STRUCT-PRIVATE | not met | `Band`'s fields are public beside a checked constructor (P0-1) |
| C-NEWTYPE-HIDE | not applicable | no newtype |
| C-STRUCT-BOUNDS | not applicable | no generic type |
| C-STABLE | met | no dependencies |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 16 met, 11 not met, 27 not applicable.
