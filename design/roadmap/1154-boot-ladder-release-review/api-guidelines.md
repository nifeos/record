# The API Guidelines checklist

An appendix to [the milestone](../1154-boot-ladder-release-review.md), giving a verdict on each of
the 54 items of the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) for
`partsfoundry/boot_ladder` at `019d76c8`. A finding named in a row is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `ParsedVerdict`, `find_in`, `SELF_TEST_CHECKS` |
| C-CONV | met | `to_words` and `from_words`, `to_packed` and `from_packed`, as std's `to_bits` and `from_bits` |
| C-GETTER | met | `absent_count`, `failed_count`, `parts`; no `get_` prefix |
| C-ITER | not applicable | no collection type |
| C-ITER-TY | not applicable | the name lists return `impl Iterator`, with no named iterator type |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | met | `absent_names` and `failed_names`, `absent_count` and `failed_count` |
| C-COMMON-TRAITS | not met | no `Hash` on the five value types, and nothing on `Verdict`, `CheckLine` and `SubjectLine` (P1-3) |
| C-CONV-TRAITS | not applicable | no value type converts to another through `From` |
| C-COLLECT | not applicable | no collection |
| C-SERDE | not applicable | the printed line is the serialized form |
| C-SEND-SYNC | met | every type is `Send` and `Sync` but `CheckLine`, whose `fmt::Arguments` field is neither by its nature |
| C-GOOD-ERR | not applicable | no error type; P0-3 adds one under the errors decision |
| C-NUM-FMT | not applicable | no numeric type of its own |
| C-RW-VALUE | not applicable | no reader or writer |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | not met | the crate page explains the matching rule and carries no example (P1-2) |
| C-EXAMPLE | not met | no public item has an example; the README's two run as doctests and render nowhere (P1-2) |
| C-QUESTION-MARK | not met | the README's example uses `unwrap` (P1-2) |
| C-FAILURE | not met | `check` has `# Panics`; `Tally::record` panics in a debug build on an index of 64 or more and says nothing (P0-1) |
| C-LINK | met | items link to each other throughout |
| C-METADATA | not met | no `documentation` key (P2-5) |
| C-RELNOTES | met | `CHANGELOG.md`, with the first version under Unreleased |
| C-HIDDEN | met | nothing is `doc(hidden)`; the README carrier is private and exists under `cfg(doctest)` only |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | met | `from_words` and `from_packed` sit on `Tally`, the more specific side |
| C-METHOD | not met | `subject_thread(heads, line)` is a free function with a receiver (P0-6) |
| C-NO-OUT | met | every function returns its result |
| C-OVERLOAD | not applicable | no operator |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | not met | `Heads::new` and `Tally::new` are met; `ParsedVerdict::in_line` is a constructor named for neither a conversion nor a search (P0-6) |
| C-INTERMEDIATE | met | `find_in` returns the whole range, and the verdict gives counts and both name lists |
| C-CALLER-CONTROL | met | everything borrows the caller's text, and nothing allocates |
| C-GENERIC | met | printing is through `Display`, so any formatter takes it; the byte-slice readers are P1-5 |
| C-OBJECT | not applicable | no traits |
| C-NEWTYPE | not met | a check is a bare `usize` (P0-1) |
| C-CUSTOM-TYPE | met | `Outcome` rather than a pair of `bool`s |
| C-BITFLAG | not applicable | the three masks are private |
| C-BUILDER | not applicable | nothing has enough parts to need one |
| C-VALIDATE | not met | `record` takes an index off the list (P0-1), `parse` takes counts that disagree (P0-2), `Heads::new` takes an empty name (P0-7) |
| C-DTOR-FAIL | not applicable | no `Drop` |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | not met | `Verdict`, `CheckLine` and `SubjectLine` (P1-3) |
| C-DEBUG-NONEMPTY | met | every derived `Debug` names its type and fields |
| C-SEALED | not applicable | no traits |
| C-STRUCT-PRIVATE | not met | `CheckLine` and `SubjectLine` are all public fields (P0-4), and `ParsedVerdict` has two (P0-5) |
| C-NEWTYPE-HIDE | met | the name lists hide their adapters behind `impl Iterator` |
| C-STRUCT-BOUNDS | not applicable | no type parameter |
| C-STABLE | met | no dependencies |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 18 met, 12 not met, 24 not applicable.
