# The API Guidelines checklist

An appendix to [the milestone](../1141-intrusive-queue-release-review.md): the 54 items of the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) against
`partsfoundry/intrusive_queue` at `7368a9e3`. A finding named in a row is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `Queue`, `Unqueued`, `push_back`, `extract_if` |
| C-CONV | met | `Unqueued::as_ptr` and `as_non_null` borrow and cost nothing |
| C-GETTER | met | `len` and `is_empty`, no `get_` |
| C-ITER | met | `iter` borrows the queue; nothing is yielded mutably, so there is no `iter_mut` |
| C-ITER-TY | met | `iter` returns `Iter` |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | met | the names follow `VecDeque` and `Vec::extract_if` |
| C-COMMON-TRAITS | not met | `Iter` has neither `Debug` nor `Clone` (P1-1) |
| C-CONV-TRAITS | not applicable | no value conversion |
| C-COLLECT | not met | no `Extend`, `FromIterator` or `IntoIterator for &Queue` (P2-1) |
| C-SERDE | not applicable | a queue of pointers has no serialized form |
| C-SEND-SYNC | not met | `Send` when `T: Send`, never `Sync` (P2-3) |
| C-GOOD-ERR | not applicable | no error type; `remove` answers `Option` |
| C-NUM-FMT | not applicable | no numeric type |
| C-RW-VALUE | not applicable | no reader or writer |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | met | the README is the crate page, with an example |
| C-EXAMPLE | met | every public item a caller starts from has one |
| C-QUESTION-MARK | not met | the examples unwrap (P2-4) |
| C-FAILURE | met | `# Safety` on `Node` and `Unqueued::new`; no public function returns an error |
| C-LINK | met | the items link to each other and to the rules they cite |
| C-METADATA | met | description, license, repository, documentation, keywords, categories |
| C-RELNOTES | met | `CHANGELOG.md` |
| C-HIDDEN | met | the test node is private under `cfg(any(test, kani))` |
| C-SMART-PTR | not applicable | `Unqueued` is a token, not a smart pointer, and has no `Deref` |
| C-CONV-SPECIFIC | not applicable | no conversion |
| C-METHOD | met | each operation is a method on `Queue` |
| C-NO-OUT | met | `extract_if` returns the extracted queue |
| C-OVERLOAD | not applicable | no operator |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | met | `Queue::new` is `const`, with `Default` |
| C-INTERMEDIATE | met | `pop_front` and `remove` hand back the token |
| C-CALLER-CONTROL | met | the caller owns every node and its storage |
| C-GENERIC | met | the queue is generic over its node |
| C-OBJECT | not applicable | `Node` is `Sized` by design; a queue of trait objects is not its job |
| C-NEWTYPE | met | `Unqueued` distinguishes a node that may be pushed from any pointer |
| C-CUSTOM-TYPE | met | `push_back` takes `Unqueued`, not a raw pointer |
| C-BITFLAG | not applicable | no flag set |
| C-BUILDER | not applicable | construction takes no options |
| C-VALIDATE | met | the token's contract is checked at the one `unsafe` call that mints it |
| C-DTOR-FAIL | not applicable | no `Drop` |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | not met | `Iter` (P1-1) |
| C-DEBUG-NONEMPTY | met | `Queue` prints its length and ends; `Unqueued` its pointer |
| C-SEALED | not applicable | `Node` is for callers to implement |
| C-STRUCT-PRIVATE | met | every field is private |
| C-NEWTYPE-HIDE | met | `Iter` hides how it walks |
| C-STRUCT-BOUNDS | not met | `Queue<T: Node>` and `Iter<'a, T: Node>` (P2-5) |
| C-STABLE | met | no dependencies |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 27 met, 6 not met, 21 not applicable.
