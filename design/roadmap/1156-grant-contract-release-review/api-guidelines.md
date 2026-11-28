# The API Guidelines checklist

An appendix to [the milestone](../1156-grant-contract-release-review.md), giving a verdict on each
of the 54 items of the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) for
`partsfoundry/grant_contract` at `f84cd7e6`. A finding or a door named in a row is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `ManifestAuthorities`, `narrow_by_verb`, `MAXIMUM_VERB_BYTES` |
| C-CONV | not applicable | no `as_`, `to_` or `into_` conversion |
| C-GETTER | met | `letters`, `bits`, `rights` and `diagnostics_slot`, with no `get_` prefix |
| C-ITER | not applicable | `ShortOptions::letters` hands out a slice, and no type is a collection |
| C-ITER-TY | not applicable | no iterator type |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | met | the five `...Declaration` types, and `WordGrant` with `VerbGrant` |
| C-COMMON-TRAITS | not met | no `Hash` on any type and no `Default` on the flag set (P1-4) |
| C-CONV-TRAITS | not met | no `TryFrom<&[u8]>` for `ShortOptions` and no `TryFrom<u16>` for the flag set (P1-4) |
| C-COLLECT | not applicable | no collection |
| C-SERDE | not applicable | the crate is a wire contract, and its byte form is a record another crate decodes |
| C-SEND-SYNC | met | a scratch crate compiles `Manifest`, `VerbGrant` and `ManifestAuthorities` as `Send`, `Sync` and `Unpin` |
| C-GOOD-ERR | not met | the checks return `bool` and `Option`, with no error type (P0-4) |
| C-NUM-FMT | not applicable | no numeric type of its own |
| C-RW-VALUE | not applicable | no reader or writer |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | not met | the crate page has no example; the README is included for doctests only (P1-5) |
| C-EXAMPLE | not met | one item has an example (P1-5) |
| C-QUESTION-MARK | not met | the item example calls `unwrap` (P1-5) |
| C-FAILURE | not met | `ShortOptions::new` panics and has no `# Panics` heading (P1-5) |
| C-LINK | met | items link to each other; the names that link nowhere are P1-1 |
| C-METADATA | not met | no `documentation` key (P2-5) |
| C-RELNOTES | met | `CHANGELOG.md`, with one line before the first release |
| C-HIDDEN | met | nothing is `doc(hidden)`, and the README holder exists under `cfg(doctest)` alone |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | not applicable | no conversion |
| C-METHOD | not met | `narrow_by_verb` is a free function with a clear receiver (P0-1) |
| C-NO-OUT | not met | `delegated_identity` fills an out-parameter and returns a length (P0-6); `verb_key` and `page_verb` use theirs as storage for the slice they return |
| C-OVERLOAD | not applicable | no operator; the missing `\|` and `&` are P1-4 |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | met | `ShortOptions::new` and `try_new` |
| C-INTERMEDIATE | met | `verb_key` exposes the key that `page_verb` builds |
| C-CALLER-CONTROL | met | every type is `Copy`, and the caller owns each buffer |
| C-GENERIC | not applicable | the inputs are slices of one concrete type |
| C-OBJECT | not applicable | no trait |
| C-NEWTYPE | not met | slots and rights are bare `u64` values (D10) |
| C-CUSTOM-TYPE | met | each declaration is an enum with named fields, and no function takes a `bool` |
| C-BITFLAG | met | `ManifestAuthorities` is a flag set, not an enum |
| C-BUILDER | not applicable | a manifest is written whole on purpose (D1) |
| C-VALIDATE | not met | `ShortOptions` validates; a verb table and a diagnostic slot do not (P0-1, P0-3) |
| C-DTOR-FAIL | not applicable | no `Drop` |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | met | every public type derives `Debug` |
| C-DEBUG-NONEMPTY | met | each derived `Debug` names its type |
| C-SEALED | not applicable | no trait |
| C-STRUCT-PRIVATE | not met | `Manifest` and `VerbGrant` have every field public; the first is deliberate (D1), the second is P0-1 |
| C-NEWTYPE-HIDE | met | `ShortOptions` and `ManifestAuthorities` keep their fields private |
| C-STRUCT-BOUNDS | not applicable | no generic type |
| C-STABLE | met | the one dependency appears in no public signature (P1-3) |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 17 met, 13 not met, 24 not applicable.
