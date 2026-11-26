# `domain_name_system` against the Rust API Guidelines checklist

An appendix to [the release review](../1136-domain-name-system-release-review.md). It marks the 54
items against `partsfoundry/domain_name_system` at `513558c`, and a "not met" points at its finding.

| code | mark | note |
|---|---|---|
| C-CASE | met | conventional case; acronyms follow the crate's ratified spellings |
| C-CONV | met | `Name::as_bytes` borrows |
| C-GETTER | met | `Query::id`, `Query::name`, `Answer::ttl_seconds`, with no `get_` prefix |
| C-ITER | not applicable | `Reader` is a cursor counted by the header, not a collection |
| C-ITER-TY | not applicable | no iterator |
| C-FEATURE | not applicable | no Cargo feature |
| C-WORD-ORDER | met | the ratified names pass every rule in force |
| C-COMMON-TRAITS | not met | item 5: no `Debug` on `Reader` or `TcpReply`, no `PartialEq` or `Eq` on `Question`, `Record` or `Query`; item 7: no `Hash` on `Name` |
| C-CONV-TRAITS | met | `FromStr` and `Display` on `Name` |
| C-COLLECT | not applicable | no collection |
| C-SERDE | not applicable | wire bytes are the serialized form |
| C-SEND-SYNC | met | every type is plain data or a borrow, so both hold |
| C-GOOD-ERR | not met | item 2: no `Display` or `core::error::Error` |
| C-NUM-FMT | not applicable | no number-like type |
| C-RW-VALUE | not applicable | no `Read` or `Write`; buffers are slices |
| C-EVOCATIVE | not applicable | no macro |
| C-MACRO-ATTR | not applicable | no macro |
| C-ANYWHERE | not applicable | no macro |
| C-MACRO-VIS | not applicable | no macro |
| C-MACRO-TY | not applicable | no macro |
| C-CRATE-DOC | not met | item 3: thorough prose and a BUGS list, but no code example |
| C-EXAMPLE | not met | item 6: twenty-two functions have none |
| C-QUESTION-MARK | not met | item 3: the README's example unwraps |
| C-FAILURE | met | each `Error` and `Reject` variant states when it occurs; nothing panics |
| C-LINK | met | intra-doc links throughout |
| C-METADATA | not met | item 8: no `documentation` field |
| C-RELNOTES | met | `CHANGELOG.md` |
| C-HIDDEN | met | nothing hidden |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | met | `Name::from_dotted` lives on `Name` |
| C-METHOD | met | operations are methods on the type they act on, except `decode_name` over a whole message |
| C-NO-OUT | met | writers fill a caller's buffer and return the length, the shape a `no_std` crate needs |
| C-OVERLOAD | not applicable | no overloaded name |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | met | `Query::new`, `Query::for_name`, `Reader::new`, `TcpReply::new` |
| C-INTERMEDIATE | met | `Header`, `Reader` and `decode_name` expose the steps `accept` takes |
| C-CALLER-CONTROL | met | every buffer belongs to the caller |
| C-GENERIC | met | slices in, slices out; nothing a generic would widen |
| C-OBJECT | not applicable | no trait |
| C-NEWTYPE | met | `Name` wraps its bytes and its length |
| C-CUSTOM-TYPE | met | no `bool` argument |
| C-BITFLAG | not met | door 4: `FLAG_` constants over a bare `u16`, not a flags type |
| C-BUILDER | not applicable | no construction with options |
| C-VALIDATE | met | every parser is total and refuses with a variant |
| C-DTOR-FAIL | not applicable | no custom `Drop` |
| C-DTOR-BLOCK | not applicable | no custom `Drop` |
| C-DEBUG | not met | item 5 |
| C-DEBUG-NONEMPTY | met | the root name prints `.` |
| C-SEALED | not applicable | no trait |
| C-STRUCT-PRIVATE | met | public fields on `Header`, `Question` and `Record`; door 3 |
| C-NEWTYPE-HIDE | met | `Answer` and `Name` keep their storage private |
| C-STRUCT-BOUNDS | met | no bound on any struct definition |
| C-STABLE | met | no dependency |
| C-PERMISSIVE | met | `MIT OR Apache-2.0` |
