# The API Guidelines checklist

An appendix to [the milestone](../1140-line-editor-release-review.md). Each of the 54 items of
the [Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html),
read against `partsfoundry/line_editor` at `2c625ef6`. A finding named in a row is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | types in UpperCamelCase, constants in SCREAMING_SNAKE_CASE |
| C-CONV | not applicable | no `as_`, `to_` or `into_` conversion |
| C-GETTER | met | `line` and `pending` carry no `get_` |
| C-ITER | not applicable | no collection is iterated |
| C-ITER-TY | not applicable | no iterator type |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | met | the three limits all open `MAXIMUM_` and end with their unit |
| C-COMMON-TRAITS | not met | `Event` has no `Hash`; the four state types derive nothing (P1-2) |
| C-CONV-TRAITS | not applicable | no value type converts |
| C-COLLECT | not applicable | `RawQueue` is filled from slices, not iterators |
| C-SERDE | not applicable | the handoff blob is the crate's own versioned format |
| C-SEND-SYNC | met | every type is plain data and is `Send` and `Sync` |
| C-GOOD-ERR | not met | `Refusal` has no `Display` or `Error`, and `restore` returns `Option` (P0-1) |
| C-NUM-FMT | not applicable | no numeric type of its own |
| C-RW-VALUE | met | every method borrows its sink as `&mut impl Sink`, so the caller keeps it |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | met | the crate page states the contract, the limits and an example |
| C-EXAMPLE | not met | five public items have no example (P1-4) |
| C-QUESTION-MARK | not applicable | no example calls anything fallible |
| C-FAILURE | not met | no `# Errors` heading on any fallible function (P1-4) |
| C-LINK | met | items link to each other in their documentation |
| C-METADATA | not met | no `documentation` key (P2-1) |
| C-RELNOTES | met | `CHANGELOG.md` has an Unreleased section |
| C-HIDDEN | met | `test_support` is private; nothing is `doc(hidden)` |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | not applicable | no conversion |
| C-METHOD | met | every operation on the editor is a method |
| C-NO-OUT | met | `pending` returns a tuple; `Reader::field` fills a caller buffer and returns its length |
| C-OVERLOAD | not applicable | no operator |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | met | `new` and `Default` on `LineEditor` and `RawQueue` |
| C-INTERMEDIATE | met | `pending` exposes the half-typed line and its cursor |
| C-CALLER-CONTROL | met | inputs arrive as `&[u8]` and sinks as `&mut`, so no method takes ownership it does not need |
| C-GENERIC | met | the sink is a generic parameter |
| C-OBJECT | not met | the implicit `Sized` bound refuses a `dyn Sink` (P1-3) |
| C-NEWTYPE | not applicable | no value a newtype would distinguish |
| C-CUSTOM-TYPE | met | `feed` returns an `Event`, not flags |
| C-BITFLAG | not applicable | no flag set |
| C-BUILDER | not applicable | construction takes no options |
| C-VALIDATE | met | `Reader::new` checks the magic and layout; a long line is refused with a bell |
| C-DTOR-FAIL | not applicable | no `Drop` |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | not met | four public types (P1-2) |
| C-DEBUG-NONEMPTY | met | `Event` and `Refusal` print their variant |
| C-SEALED | not applicable | `Sink` is for callers to implement |
| C-STRUCT-PRIVATE | met | every struct's fields are private |
| C-NEWTYPE-HIDE | met | no public field exposes an inner type |
| C-STRUCT-BOUNDS | met | no struct declares a bound |
| C-STABLE | met | no dependencies |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 23 met, 7 not met, 24 not applicable.
