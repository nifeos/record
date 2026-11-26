# The API Guidelines checklist

An appendix to [the milestone](../1144-device-tree-blob-release-review.md), giving a verdict on
each of the 54 items of the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) for
`partsfoundry/device_tree_blob` at `9ed5c2a9`. A finding named in a row is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `DeviceTreeBlob`, `node_property`, `MAXIMUM_TOTAL_SIZE_BYTES` |
| C-CONV | not applicable | no `as_`, `to_` or `into_` conversion |
| C-GETTER | met | `total_size` and `boot_arguments`, no `get_` prefix |
| C-ITER | not applicable | the crate holds no collection; the missing traversal is P1-1 |
| C-ITER-TY | not applicable | no iterator |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | met | the error variants read alike: `BadMagic`, `BadToken`, `TooDeep`, `TooLarge` |
| C-COMMON-TRAITS | not met | `DeviceTreeBlob` is not `Clone` or `Copy`; `Region` lacks `Hash`, `Default` and `Ord` (P1-2) |
| C-CONV-TRAITS | not applicable | no conversion between the crate's types |
| C-COLLECT | not applicable | no collection |
| C-SERDE | not applicable | no type a caller would serialize |
| C-SEND-SYNC | met | every public type holds slices and integers, so is `Send` and `Sync` |
| C-GOOD-ERR | met | `Error` implements `Display` and `core::error::Error` and is `#[non_exhaustive]`; its location is P0-3 |
| C-NUM-FMT | not applicable | no number type |
| C-RW-VALUE | not applicable | no reader or writer is taken |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | not met | the crate page describes the format but holds no example (P1-3) |
| C-EXAMPLE | not met | four of seventeen public functions have an example (P1-3) |
| C-QUESTION-MARK | met | the examples use `?` with `Ok::<(), device_tree_blob::Error>(())` |
| C-FAILURE | not met | no `# Errors` section (P1-3); the `# Safety` section of `from_pointer` is incomplete (P1-4) |
| C-LINK | met | the documentation links `Error`, `Region` and the limits |
| C-METADATA | met | description, license, repository, documentation, readme, keywords and categories |
| C-RELNOTES | met | `CHANGELOG.md` |
| C-HIDDEN | met | no `#[doc(hidden)]`; the walker and its tokens are private |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | not applicable | no conversion |
| C-METHOD | met | every lookup is a method on `DeviceTreeBlob` |
| C-NO-OUT | met | the `out` slices are caller buffers, the no-allocator form, and the count is returned |
| C-OVERLOAD | not applicable | no overloaded operator |
| C-DEREF | met | no `Deref` |
| C-CTOR | met | `from_bytes` and `from_pointer` |
| C-INTERMEDIATE | met | values come back as slices of the blob, not copies |
| C-CALLER-CONTROL | met | the caller supplies every output buffer |
| C-GENERIC | not applicable | the parameters are byte slices and a `u32` |
| C-OBJECT | not applicable | no traits |
| C-NEWTYPE | met | `Region` carries an address and a size; the pointer handle is a `u32`, as in every comparator |
| C-CUSTOM-TYPE | met | no `bool` or `Option` parameter |
| C-BITFLAG | not applicable | no flags |
| C-BUILDER | not applicable | no complex value to build |
| C-VALIDATE | not met | `from_bytes` checks the header only, so a lookup can meet the fault (P0-1) |
| C-DTOR-FAIL | not applicable | no destructor |
| C-DTOR-BLOCK | not applicable | no destructor |
| C-DEBUG | met | every public type has `Debug`; its output is P2-1 |
| C-DEBUG-NONEMPTY | met | the derived output is never empty |
| C-SEALED | not applicable | no traits |
| C-STRUCT-PRIVATE | not met | `DeviceTreeBlob` keeps its fields private; `Region` has two public fields and is not `#[non_exhaustive]` (P0-4) |
| C-NEWTYPE-HIDE | not applicable | no wrapped implementation type |
| C-STRUCT-BOUNDS | met | no bounds on the declarations |
| C-STABLE | met | no dependencies |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 23 met, 6 not met, 25 not applicable.
