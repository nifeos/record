# The API Guidelines checklist

An appendix to [the milestone](../1146-extensible-host-controller-interface-release-review.md).
Each of the 54 items of the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html), read
against `partsfoundry/extensible_host_controller_interface` at `a10790e1`. A finding named in a row
is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | types in UpperCamelCase, functions in snake_case, constants in SCREAMING_SNAKE_CASE |
| C-CONV | not applicable | no `as_`, `to_` or `into_` conversion |
| C-GETTER | met | `kind`, `is_cycle`, `capacity` and `index` carry no `get_` |
| C-ITER | not applicable | no collection is iterated |
| C-ITER-TY | not applicable | no iterator type |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | met | the limits open `MINIMUM_` and `MAXIMUM_`, the waits end `_MILLISECONDS` |
| C-COMMON-TRAITS | not met | no public type derives `Hash` (P1-3) |
| C-CONV-TRAITS | not applicable | no value type converts to another |
| C-COLLECT | not applicable | no collection |
| C-SERDE | not applicable | the values are hardware layouts, not data to serialize |
| C-SEND-SYNC | met | every type is plain data and is `Send` and `Sync` |
| C-GOOD-ERR | not met | no error type; refusals are `bool`, `Option` and panics (P0-8) |
| C-NUM-FMT | not applicable | no numeric type of its own |
| C-RW-VALUE | not applicable | no reader or writer is taken |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | met | the crate page states what is computed, what the caller does, and an example |
| C-EXAMPLE | not met | examples on the crate page and `ProducerRing` only (P1-4) |
| C-QUESTION-MARK | not applicable | no example calls anything fallible through `Result` |
| C-FAILURE | met | both panicking constructors carry a `# Panics` section; nothing returns `Result` |
| C-LINK | met | items link to each other and cite the specification's sections |
| C-METADATA | not met | no `documentation` key (P2-7) |
| C-RELNOTES | met | `CHANGELOG.md` has one section per pre-release |
| C-HIDDEN | met | the overlap assertions and ring internals are `pub(crate)`; nothing is `doc(hidden)` |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | not applicable | no conversion |
| C-METHOD | met | ring and capability operations are methods; the field builders are free functions in their modules |
| C-NO-OUT | met | every function returns its result |
| C-OVERLOAD | not applicable | no operator |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | met | `new` on both rings and on `PortDebounce`, `decode` on the decoded types |
| C-INTERMEDIATE | met | `entry_physical_address`, `dequeue_pointer` and `segment_table_entry` expose what the caller writes |
| C-CALLER-CONTROL | met | the caller owns all memory and every register access |
| C-GENERIC | not applicable | no parameter a generic would widen |
| C-OBJECT | met | `find_extended` takes `&mut dyn FnMut`, which any closure fits |
| C-NEWTYPE | not met | slot, port, device context index and speed are bare `u8` (P0-5) |
| C-CUSTOM-TYPE | not met | `data` and `status` take the direction as `bool` (P0-4); completion codes are `u8` (P0-1) |
| C-BITFLAG | met | the port and command bits are `u32` constants combined with `\|`, the register's own type |
| C-BUILDER | not applicable | every builder is one call with its fields as arguments |
| C-VALIDATE | not met | `doorbell` takes any slot (P0-6); `enqueue` places past capacity (P0-9); the TRB builders do not check the 64 KiB rule, by design and stated |
| C-DTOR-FAIL | not applicable | no `Drop` |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | met | every public type derives `Debug` |
| C-DEBUG-NONEMPTY | met | every derived `Debug` prints its fields |
| C-SEALED | not applicable | no trait |
| C-STRUCT-PRIVATE | not met | `TransferRequestBlock`'s field is public (P0-7); `Capabilities` is exhaustive (P0-2) |
| C-NEWTYPE-HIDE | not met | `TransferRequestBlock` exposes its inner array (P0-7) |
| C-STRUCT-BOUNDS | met | no struct declares a bound |
| C-STABLE | met | no dependencies |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 21 met, 9 not met, 24 not applicable.
