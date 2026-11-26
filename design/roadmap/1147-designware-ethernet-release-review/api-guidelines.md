# The API Guidelines checklist

An appendix to [the milestone](../1147-designware-ethernet-release-review.md). Each of the 54 items
of the [Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html),
read against `partsfoundry/designware_ethernet` at `565b331f`. A finding named in a row is the
block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | types in UpperCamelCase, functions in snake_case, constants in SCREAMING_SNAKE_CASE |
| C-CONV | not met | `Settings::to_word` takes `&self` on a `Copy` type (P0-5) |
| C-GETTER | met | `receive_cursor`, `core_version` and `direct_memory_access_physical_address_bits` carry no `get_` |
| C-ITER | not applicable | no collection is iterated |
| C-ITER-TY | not applicable | no iterator type |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | met | `ResetTimeout`, `FlushTimeout` and `RegionOutOfReach` share one order; the limits end with their unit |
| C-COMMON-TRAITS | not met | no type derives `Hash`; `Link` and `BusConfiguration` have no `Default` (P0-1) |
| C-CONV-TRAITS | not met | no `From` or `TryFrom` for a station address (P0-4) |
| C-COLLECT | not applicable | no collection is built |
| C-SERDE | not applicable | no value is meant for a serializer; the packed word is the crate's own (P0-5) |
| C-SEND-SYNC | met | every type is plain data, and `Bus` is `Send` when its hardware is |
| C-GOOD-ERR | not met | four error types with no `Display` or `core::error::Error` (P0-3) |
| C-NUM-FMT | not applicable | no numeric type of its own |
| C-RW-VALUE | not applicable | no `Read` or `Write` parameter |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | not met | the crate page is shorter than the README, which is not included (P1-3) |
| C-EXAMPLE | not met | `bring_up`, `configure` and the Motorcomm sequences have no example (P1-3) |
| C-QUESTION-MARK | not met | the README example calls `unwrap` on `transmit` (P1-3) |
| C-FAILURE | not met | one `# Errors` heading among thirteen fallible public functions (P1-3) |
| C-LINK | met | items link to each other and to the OpenBSD and Linux sources they follow; four links point at private items (P1-3) |
| C-METADATA | not met | no `documentation` key (P2-1) |
| C-RELNOTES | met | `CHANGELOG.md` names each breaking change of 0.1.0-pre.1 |
| C-HIDDEN | met | `simulator` and the descriptor bits are crate-private; nothing is `doc(hidden)` |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | not met | `station_mac_address(high, low)` is a free function, not a constructor of an address type (P0-4) |
| C-METHOD | met | the ring operations are methods of `DataPlane`; the sequences take the caller's hardware as their first argument |
| C-NO-OUT | not met | `bring_up` writes `Account` through `&mut`, on purpose, so a failed bring-up still reports how far it got (P0-4 keeps it) |
| C-OVERLOAD | not applicable | no operator |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | not met | `Inputs`, `Link`, `BusConfiguration` and `Settings` are built by struct literal (P0-1) |
| C-INTERMEDIATE | met | `Identity`, `Account`, `Observation` and `Applied` expose what each step saw, and each sequence is public |
| C-CALLER-CONTROL | not met | the ring sizes are fixed, and each frame is copied in and out (P2-2, P2-3) |
| C-GENERIC | met | every sequence takes `impl Hardware`, `impl ManagementDataIo` or `impl Port` |
| C-OBJECT | met | `Hardware`, `ManagementDataIo`, `DirectMemoryAccessRegion` and `Tails` are object-safe; `Port`, with a generic method, serves generic code |
| C-NEWTYPE | not met | station addresses are `[u8; 6]` and physical addresses bare `u64` (P0-4) |
| C-CUSTOM-TYPE | not met | `start` and `mac_configuration` take `loopback: bool`; an enum may follow without a break only through a new function |
| C-BITFLAG | not applicable | the register bits are crate-private constants |
| C-BUILDER | not met | `BusConfiguration` has eight public fields and no builder or `Default` (P0-1) |
| C-VALIDATE | not met | `configure` checks the region's reach and `receive_verdict` every descriptor field, but a station address from `Inputs` is unchecked (P0-4) |
| C-DTOR-FAIL | not applicable | no `Drop` |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | not met | `management_data_io::Bus` has no `Debug`; adding one is compatible |
| C-DEBUG-NONEMPTY | met | every derived `Debug` prints its fields or variant |
| C-SEALED | not applicable | every trait is for callers to implement |
| C-STRUCT-PRIVATE | not met | five structs with public fields and `DataPlane::dropped` (P0-1) |
| C-NEWTYPE-HIDE | not met | `Bus` exposes the hardware it wraps as a public field (P0-1) |
| C-STRUCT-BOUNDS | not met | `Bus<'a, H: Hardware>` declares its bound on the struct; removing it later is compatible |
| C-STABLE | met | no dependencies |
| C-PERMISSIVE | met | `(MIT OR Apache-2.0) AND ISC AND BSD-2-Clause`, each permissive |

Totals: 14 met, 21 not met, 19 not applicable.
