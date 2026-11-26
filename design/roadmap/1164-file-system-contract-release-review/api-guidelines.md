# The API Guidelines checklist

An appendix to [the milestone](../1164-file-system-contract-release-review.md), giving a verdict
on each of the 54 items of the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) for
`partsfoundry/file_system_contract` at `05515061`. A finding named in a row is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `Rights`, `request_handle`, `MAXIMUM_TRANSFER_BYTES` |
| C-CONV | not applicable | no conversion method |
| C-GETTER | met | `Rights::bits` and the field readers carry no `get_` prefix; `store::get` is a lookup, as the standard library's `get` is |
| C-ITER | met | the four walkers are functions named `iter`; the crate has no collection type |
| C-ITER-TY | not met | `iter` returns `Entries`, `Names` and `Records`, and no type is named `Iter`; door D8 rules the names |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | met | every limit opens `MAXIMUM_` and every size ends `_BYTES` |
| C-COMMON-TRAITS | not met | `Rights` has no `Hash`, `Verb` no `PartialEq`, and the four iterators derive nothing (P1-5) |
| C-CONV-TRAITS | not met | no `From` or `TryFrom` between a word and an operation, a handle or a rights mask (P0-1), and none between bytes and a record (P0-9) |
| C-COLLECT | not applicable | no collection |
| C-SERDE | not applicable | the words and the records are the serialized form |
| C-SEND-SYNC | met | every type is plain data or a borrowed slice |
| C-GOOD-ERR | not met | an error is an `i32` with no `Display` and no `core::error::Error` (P0-5) |
| C-NUM-FMT | not applicable | no numeric type of its own |
| C-RW-VALUE | not applicable | no reader or writer in the `std::io` sense |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | not met | the crate page states the call and the reply word, and shows no example; the README's example runs as a hidden doctest (P1-2) |
| C-EXAMPLE | not met | six `# Examples` sections for 66 public functions (P1-2) |
| C-QUESTION-MARK | not met | the examples of `grant::specification` and `grant::write_page` call `unwrap` (P1-2) |
| C-FAILURE | not met | five `# Panics` sections; `block::request` and `extended_attribute::reply` state their panic under no heading, and `store::set` and `store::remove` have no `# Errors` (P1-2) |
| C-LINK | met | items link to each other |
| C-METADATA | not met | `documentation` points at the repository (P2-4) |
| C-RELNOTES | met | `CHANGELOG.md`, with the first version unreleased; P2-5 raises its dates |
| C-HIDDEN | met | the README doctest holder and the proofs are private |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | not applicable | no conversion |
| C-METHOD | not met | `request_handle(w0)`, `grant::is_writable(w)` and `nameset::contains(buf, name)` have a clear receiver and are free functions (P0-1, P0-9) |
| C-NO-OUT | not met | `grant::unpack_name` fills a buffer and returns a clamped length (P2-2); the encoders write into a caller's buffer, which the guideline allows |
| C-OVERLOAD | not applicable | no operator; `Rights` has none on purpose |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | met | `Rights::root` |
| C-INTERMEDIATE | met | each encoder returns the bytes it used, and `store::get` returns the kind with the value |
| C-CALLER-CONTROL | met | every walk borrows, every encoder fills a caller's buffer, and nothing allocates |
| C-GENERIC | not applicable | no parameter a generic would widen |
| C-OBJECT | not applicable | no trait |
| C-NEWTYPE | not met | `Rights` is the one newtype; an operation, a handle, a mask and a badge are `u64` (P0-1, door D1) |
| C-CUSTOM-TYPE | not met | `is_directory: bool` arguments, and `volume_statistics::decode` answers three `u64` (P0-9) |
| C-BITFLAG | not met | two sets of rights and two flag bytes are loose constants (P0-1) |
| C-BUILDER | not applicable | no value with many parts |
| C-VALIDATE | not met | the packers take any operation (P0-2), and the decoders refuse one field (P0-3) |
| C-DTOR-FAIL | not applicable | no `Drop` |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | not met | the four iterator types have no `Debug` (P1-5) |
| C-DEBUG-NONEMPTY | met | `Rights(49)`; P1-5 asks for the names |
| C-SEALED | not applicable | no trait |
| C-STRUCT-PRIVATE | not met | `Verb` has seven public fields (P0-4); the field of `Rights` is private |
| C-NEWTYPE-HIDE | not met | `nameset::iter` returns `core::iter::Take<Names>` (P0-9) |
| C-STRUCT-BOUNDS | not applicable | no generic type |
| C-STABLE | met | no dependency |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 14 met, 18 not met, 22 not applicable.
