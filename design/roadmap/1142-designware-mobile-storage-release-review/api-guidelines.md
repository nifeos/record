# The API Guidelines checklist

An appendix to [the milestone](../1142-designware-mobile-storage-release-review.md), giving a
verdict on each of the 54 items of the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) for
`partsfoundry/designware_mobile_storage` at `ac950346`. A finding named in a row is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `HostController`, `read_blocks`, `BLOCK_BYTES` |
| C-CONV | met | `registers_mut` borrows and `into_registers` gives the window back |
| C-GETTER | met | no `get_` prefix |
| C-ITER | not applicable | no collection is iterated |
| C-ITER-TY | not applicable | no iterator type |
| C-FEATURE | met | `simulator`, with no `use-` or `with-` prefix |
| C-WORD-ORDER | met | `CommandTimeout`, `DataTimeout`, `ResponseTimeout` |
| C-COMMON-TRAITS | met | the value types derive `Debug`, `Clone`, `Copy`, `PartialEq` and `Eq` |
| C-CONV-TRAITS | not applicable | no value type converts to another |
| C-COLLECT | not applicable | no collection |
| C-SERDE | not applicable | register values and card registers have no serialized form here |
| C-SEND-SYNC | met | the types hold no raw pointer, so they are `Send` and `Sync` with their parameters |
| C-GOOD-ERR | met | `Display`, `core::error::Error` and `#[non_exhaustive]` on all four error types |
| C-NUM-FMT | not applicable | no numeric type of its own |
| C-RW-VALUE | not applicable | no reader or writer |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | met | the README is the crate page, with an example |
| C-EXAMPLE | not met | only the crate page and the simulator have one (P1-5) |
| C-QUESTION-MARK | met | the crate page's example uses `?` |
| C-FAILURE | met | `# Errors` on each fallible public function |
| C-LINK | met | items link to each other and to the registers they touch |
| C-METADATA | not met | no `documentation` key (P2-6) |
| C-RELNOTES | met | `CHANGELOG.md` marks each breaking change |
| C-HIDDEN | met | the simulator's internals are private; nothing is `doc(hidden)` |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | not applicable | no conversion |
| C-METHOD | met | controller operations are methods on `HostController` |
| C-NO-OUT | met | `read_data` fills the caller's buffer and returns the response |
| C-OVERLOAD | not applicable | no operator |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | met | `HostController::new`, `Command::new` and `InternalDirectMemoryAccess::new` |
| C-INTERMEDIATE | met | `send_command` returns the raw response words, and the window stays reachable |
| C-CALLER-CONTROL | met | the caller supplies the window, the clock, the region and every buffer |
| C-GENERIC | met | generic over the register window and the region |
| C-OBJECT | met | both traits are object safe |
| C-NEWTYPE | not met | the bus width is a bare `u8` (P0-4) |
| C-CUSTOM-TYPE | not met | the bus width argument (P0-4) and the untyped block buffers (P0-3) |
| C-BITFLAG | not applicable | no flag set is public |
| C-BUILDER | not applicable | `Deadlines` has a default and a setter |
| C-VALIDATE | met | the region, the queue width and each buffer length are checked before use |
| C-DTOR-FAIL | not applicable | no `Drop` |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | not met | `HostController` and `InternalDirectMemoryAccess` (P1-4) |
| C-DEBUG-NONEMPTY | met | the derived and written `Debug` output names each type |
| C-SEALED | not applicable | both traits are for callers to implement |
| C-STRUCT-PRIVATE | not met | five structs with public fields and no `#[non_exhaustive]`, among them the hardware answers `Card` and `Identity` (P0-1) |
| C-NEWTYPE-HIDE | met | the controller's state is private |
| C-STRUCT-BOUNDS | not met | `HostController` and `InternalDirectMemoryAccess` (P2-7) |
| C-STABLE | met | no dependencies |
| C-PERMISSIVE | met | (MIT OR Apache-2.0) AND ISC |

Totals: 26 met, 7 not met, 21 not applicable.
