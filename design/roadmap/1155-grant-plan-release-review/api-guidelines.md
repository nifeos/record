# The API Guidelines checklist

An appendix to [the milestone](../1155-grant-plan-release-review.md), giving a verdict on each of
the 54 items of the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) for
`partsfoundry/grant_plan` at `69aedfbc`. A finding named in a row is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `ParsedInvocation`, `plan_against`, `MAXIMUM_STAGES` |
| C-CONV | met | `Name::as_bytes` borrows at no cost; nothing is named `to_` or `into_` |
| C-GETTER | met | `depth`, `position`, `stages`, `names`; no `get_` prefix |
| C-ITER | not met | `NameSet::iter` and `Bindings::iter` exist; tokens, words and path components have no iterator (P0-5) |
| C-ITER-TY | not applicable | both `iter` methods return `impl Iterator`, with no named iterator type |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | met | `FileForbidden`, `InputForbidden`, `MemoryGrantForbidden`; `TooManyNames`, `TooManyStages` |
| C-COMMON-TRAITS | not met | no type has `Hash`; `Expander` and `TwoRoots` derive nothing; no refusal has `Display` (P0-3, P1-8) |
| C-CONV-TRAITS | not met | `Name` has no `TryFrom<&[u8]>` and no `AsRef<[u8]>` (P2-3) |
| C-COLLECT | not applicable | `NameSet` is bounded and refuses a ninth name, so it cannot be `FromIterator` |
| C-SERDE | not applicable | a plan travels in the layouts of the contract crates |
| C-SEND-SYNC | met | no pointer and no interior mutability, so every type is `Send` and `Sync` |
| C-GOOD-ERR | not met | five error types with neither `Display` nor `core::error::Error` (P0-3) |
| C-NUM-FMT | not applicable | no numeric type of its own |
| C-RW-VALUE | not applicable | no reader or writer |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | not met | the crate page names the entry points and carries no example (P1-5) |
| C-EXAMPLE | not met | five items have one; the planner, the expander and the path types have none (P1-5) |
| C-QUESTION-MARK | not met | the README's and the items' examples use `unwrap` (P1-5) |
| C-FAILURE | not met | no `# Errors` on 26 fallible functions, and no `# Panics` on `Expander::finish` or `DirectoryPath::component` (P0-1, P0-5, P1-5) |
| C-LINK | met | items link to each other throughout; one link names a private field (P1-4) |
| C-METADATA | not met | no `documentation` key (P2-5) |
| C-RELNOTES | met | `CHANGELOG.md`, with the first version under Unreleased |
| C-HIDDEN | met | nothing is `doc(hidden)`; six modules are private behind re-exports |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | met | `Expansion::designated` sits on `Expansion`, the more specific side |
| C-METHOD | not met | `navigation::path` and `word::read` build a `Path` and a `Word` as free functions (P0-8) |
| C-NO-OUT | not met | `ShellHoldings::steps_after_start` writes its position through `&mut`; its documentation records a measured stack cost as the reason, and the review raises no finding |
| C-OVERLOAD | not applicable | no operator |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | met | `Expander::new`, `Cursor::new`, `NameSet::empty`, `DirectoryPath::root`, `MountedTree::mounted_at` |
| C-INTERMEDIATE | met | a parse keeps the line, an `Endowment` keeps the manifest, a `Batch` says whether more follows |
| C-CALLER-CONTROL | met | every parse borrows the line; the caller supplies the listing, the holdings and each buffer |
| C-GENERIC | not met | `for_each_word` takes `&mut dyn FnMut` and `token_end` takes `&dyn Fn` where an iterator serves (P0-5) |
| C-OBJECT | not applicable | no traits |
| C-NEWTYPE | met | `Name`, `DirectoryPath` and `GrantSide` stand where a slice or a number would |
| C-CUSTOM-TYPE | not met | `kill_operands` returns `(bool, usize)`, and five signatures carry a bare `bool` (P2-3) |
| C-BITFLAG | met | `Endowment::short_options` is a mask numbered by the manifest, not an enum |
| C-BUILDER | not applicable | no value has enough optional parts; P0-2 adds setters to `ShellHoldings` and `Streams` |
| C-VALIDATE | not met | `plan_against` trusts public fields a caller can clear (P0-4); `finish` takes a batched expander (P0-1); `component` takes any index (P0-5) |
| C-DTOR-FAIL | not applicable | no `Drop` |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | not met | `Expander` and `TwoRoots` (P1-8) |
| C-DEBUG-NONEMPTY | met | the written `Debug` of `Name`, `NameSet` and `DirectoryPath` prints the name, the list and the path, and `/` at the root |
| C-SEALED | not applicable | no traits |
| C-STRUCT-PRIVATE | not met | seven structs are all public fields (P0-2), and three mix public with private (P0-4) |
| C-NEWTYPE-HIDE | met | both `iter` methods hide their adapters behind `impl Iterator` |
| C-STRUCT-BOUNDS | not applicable | no type parameter |
| C-STABLE | not met | `grant_contract` 0.1.0 and `program_argument_contract` 0.1.0 stand in public signatures, both unpublished (P1-7) |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 17 met, 17 not met, 20 not applicable.
