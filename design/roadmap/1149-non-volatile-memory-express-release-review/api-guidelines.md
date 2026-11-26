# The API Guidelines checklist

An appendix to [the milestone](../1149-non-volatile-memory-express-release-review.md), giving a
verdict on each of the 54 items of the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) for
`partsfoundry/non_volatile_memory_express` at `60b34280`. A finding named in a row is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `SubmissionQueue`, `physical_region_page_pair`, `ADMIN_IDENTIFY` |
| C-CONV | met | `Completion::from_dwords` and `Namespace::from_identify` construct; no `as_`, `to_` or `into_` conversion is public (P0-2 adds `as_dwords`) |
| C-GETTER | met | `tail`, `head`, `capacity_bytes`, `unit_bytes`, with no `get_` prefix |
| C-ITER | not applicable | no collection is iterated |
| C-ITER-TY | not applicable | no iterator type |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | met | `ImpossibleHeadError`, `NotInFlightError`, `IdentifyNamespace`, `IdentifyController` |
| C-COMMON-TRAITS | not met | every public type derives `Debug`, `Clone`, `Copy`, `PartialEq` and `Eq`; none derives `Hash` (P1-3), and the three cursor types should not be `Copy` (P0-3) |
| C-CONV-TRAITS | not met | `Capabilities` wraps a `u64` and has no `From<u64>` (P1-3) |
| C-COLLECT | not applicable | no collection a caller fills from an iterator |
| C-SERDE | not applicable | the layouts are the specification's wire formats, built and decoded by the crate |
| C-SEND-SYNC | met | every public type is plain data, so `Send` and `Sync` |
| C-GOOD-ERR | not met | the two error types have `Display`, `core::error::Error` and `#[non_exhaustive]`; twelve functions refuse with a bare `Option` that gives no reason (P0-5) |
| C-NUM-FMT | not applicable | no numeric type of its own |
| C-RW-VALUE | not applicable | no reader or writer |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | met | the README is the crate page, with a worked command and completion that run as a doctest |
| C-EXAMPLE | not met | `Capabilities`, the six `Command` builders, the `Completion` readers and `parse_identify_namespace` have none (P1-5) |
| C-QUESTION-MARK | not met | the README example and `examples/software_controller.rs` end fallible calls with `expect` (P1-5) |
| C-FAILURE | not met | no `# Errors` section anywhere, and `Command::read` and `write` panic without a `# Panics` heading (P1-2) |
| C-LINK | met | items link to each other and to the functions that consume their values |
| C-METADATA | not met | no `documentation` key (P2-7) |
| C-RELNOTES | met | `CHANGELOG.md` gives each pre-release's changes |
| C-HIDDEN | met | `verification` is private and behind `cfg(kani)`; nothing is `doc(hidden)` |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | met | `Namespace::from_identify` lives on `Namespace`, the more specific type |
| C-METHOD | not met | `doorbell` is a free function whose third argument is a field of `Capabilities` (P0-6); the parses and pointer builders are free functions with no clear receiver |
| C-NO-OUT | met | `physical_region_page_list` fills the caller's list page, a buffer the device reads, and returns the pair |
| C-OVERLOAD | not applicable | no operator |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | met | `SubmissionQueue::new`, `CompletionQueue::new`, `CommandIdentifierSet::new`, `Namespace::new` |
| C-INTERMEDIATE | met | `Completion::is_phase_tag_set`, `physical_region_page_pair` and `blocks_per_transfer` expose the steps `transfer_command` takes |
| C-CALLER-CONTROL | met | the caller owns every buffer, every register access and every wait; the crate copies nothing |
| C-GENERIC | not applicable | no function takes a trait; `CommandIdentifierSet` is generic over its size alone |
| C-OBJECT | not applicable | the crate declares no trait |
| C-NEWTYPE | not met | queue, command and namespace identifiers, page sizes and bus addresses are bare integers (P0-1, P0-4) |
| C-CUSTOM-TYPE | met | `Direction` and `Doorbell` where a `bool` would be ambiguous; `maximum_data_transfer_bytes` uses `u64::MAX` for no limit, which its doc states |
| C-BITFLAG | met | the four status bits are `u32` constants combined with `&` |
| C-BUILDER | not applicable | no type with many optional parts |
| C-VALIDATE | not met | heads, identifiers, block numbers and Identify answers are checked; the page size is checked three ways in three places, and a public field lets a caller bypass the command builders (P0-1, P0-2) |
| C-DTOR-FAIL | not applicable | no `Drop` |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | met | every public type derives `Debug` |
| C-DEBUG-NONEMPTY | met | the derived output names each type and field |
| C-SEALED | not applicable | the crate declares no trait |
| C-STRUCT-PRIVATE | not met | `Command(pub [u32; 16])` and `Capabilities(pub u64)` (P0-2); the public fields of `Completion`, the two Identify structs and the two errors are read-only by `#[non_exhaustive]` |
| C-NEWTYPE-HIDE | met | the rings and `Namespace` keep their fields private |
| C-STRUCT-BOUNDS | met | `CommandIdentifierSet<const WORDS: usize>` carries no trait bound, and checks its size in a `const` block |
| C-STABLE | met | no dependencies |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 22 met, 11 not met, 21 not applicable.
