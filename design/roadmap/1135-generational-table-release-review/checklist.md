# `generational_table` against the Rust API Guidelines checklist

An appendix to [the release review](../1135-generational-table-release-review.md). All 54 items,
marked against `partsfoundry/generational_table` at `b524333`. Where an item is not met, the note
names the finding that answers it.

| code | mark | note |
|---|---|---|
| C-CASE | met | conventional case throughout |
| C-CONV | met | `to_bits` is a cheap `Copy` conversion, `from_bits` its inverse |
| C-GETTER | met | `len`, `slot_count`, `get`, `get_mut`; no `get_` prefix on a plain field |
| C-ITER | met | `iter`, `iter_mut`, `values`, `values_mut` |
| C-ITER-TY | not met | item 3: every iterator is `impl Iterator` |
| C-FEATURE | not applicable | no Cargo feature |
| C-WORD-ORDER | met | the nineteen ratified names follow the standard library's order |
| C-COMMON-TRAITS | met | `Table` has `Clone`, `Debug`, `Default`; `EntryName` has the eight that fit a key |
| C-CONV-TRAITS | not applicable | no conversion between two of the crate's types |
| C-COLLECT | not applicable | a fixed table cannot promise to take every item, so no `FromIterator` |
| C-SERDE | not applicable | left out on purpose, with no dependency; `to_bits` serves a caller that stores names |
| C-SEND-SYNC | met | automatic; `PhantomData<fn() -> T>` keeps `EntryName` `Send` and `Sync` for every `T` |
| C-GOOD-ERR | not applicable | no error type; item 1 returns the refused value, not an error |
| C-NUM-FMT | not applicable | `EntryName` is not a number to a caller |
| C-RW-VALUE | not applicable | no reader or writer |
| C-EVOCATIVE | not applicable | no macro |
| C-MACRO-ATTR | not applicable | no macro |
| C-ANYWHERE | not applicable | no macro |
| C-MACRO-VIS | not applicable | no macro |
| C-MACRO-TY | not applicable | no macro |
| C-CRATE-DOC | met | the crate page opens with an example and states the limits and the traits |
| C-EXAMPLE | not met | item 2: fourteen methods have none |
| C-QUESTION-MARK | not applicable | the examples unwrap an `Option` from a table they size |
| C-FAILURE | met | `new` documents its compile-time refusal; nothing else panics |
| C-LINK | met | intra-doc links throughout |
| C-METADATA | not met | item 8: no `documentation` field |
| C-RELNOTES | met | `CHANGELOG.md` |
| C-HIDDEN | met | the private `LiveEntries` debug helper does not appear |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | met | `from_bits` lives on `EntryName`, the type it builds |
| C-METHOD | met | every operation is a method on `Table` or `EntryName` |
| C-NO-OUT | met | results are returned, not written through a parameter |
| C-OVERLOAD | not applicable | no overloaded name |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | met | `Table::new`, a `const fn` |
| C-INTERMEDIATE | met | `iter_from_slot_index` exposes the slot a sweep resumes from |
| C-CALLER-CONTROL | met | `insert` takes the value by value, and `insert_with_name` takes a closure |
| C-GENERIC | met | generic over the entry type and the capacity |
| C-OBJECT | not applicable | no trait |
| C-NEWTYPE | met | `EntryName<T>` wraps the `u64` |
| C-CUSTOM-TYPE | met | no `bool` or bare integer argument |
| C-BITFLAG | not applicable | no flags |
| C-BUILDER | not applicable | one constructor without options |
| C-VALIDATE | met | a name from another table or a stale one resolves to `None` |
| C-DTOR-FAIL | not applicable | no custom `Drop` |
| C-DTOR-BLOCK | not applicable | no custom `Drop` |
| C-DEBUG | met | both types |
| C-DEBUG-NONEMPTY | met | an empty table prints its length and slot count |
| C-SEALED | not applicable | no trait |
| C-STRUCT-PRIVATE | met | every field is private |
| C-NEWTYPE-HIDE | met | the packed word is reached only through `to_bits` |
| C-STRUCT-BOUNDS | met | no bound on either struct definition |
| C-STABLE | met | no dependency |
| C-PERMISSIVE | met | `MIT OR Apache-2.0` |
