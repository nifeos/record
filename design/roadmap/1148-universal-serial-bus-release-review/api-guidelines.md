# The API Guidelines checklist

An appendix to [the milestone](../1148-universal-serial-bus-release-review.md), giving a verdict
on each of the 54 items of the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) for
`partsfoundry/universal_serial_bus` at `4612f6b5`. A finding named in a row is the block's.

| code | verdict | why |
|---|---|---|
| C-CASE | met | `BootReport`, `find_boot_keyboard`, `REPORT_BYTES` |
| C-CONV | not met | `to_u64` takes `&self` on a `Copy` type, the standard 1147 applies to `Settings::to_word` |
| C-GETTER | met | no `get_` getter; `get_descriptor` names the USB request |
| C-ITER | not applicable | no collection is iterated |
| C-ITER-TY | not applicable | no iterator type |
| C-FEATURE | not applicable | no features |
| C-WORD-ORDER | met | `NoBootKeyboard`, `PacketTooSmall`, `NotThatDescriptor` |
| C-COMMON-TRAITS | not met | every public type derives `Debug`, `Clone`, `Copy`, `PartialEq` and `Eq` but not `Hash`, as in 1146 |
| C-CONV-TRAITS | not met | no `From` between `SetupPacket` and its eight bytes (P2-2) |
| C-COLLECT | not applicable | no collection |
| C-SERDE | not applicable | descriptors and reports have their wire form already |
| C-SEND-SYNC | met | the types hold only integers, so they are `Send` and `Sync` |
| C-GOOD-ERR | not met | `Refusal` has no `Display` and no `core::error::Error` (P1-1) |
| C-NUM-FMT | not applicable | no numeric type of its own |
| C-RW-VALUE | not applicable | no reader or writer |
| C-EVOCATIVE | not applicable | no macros |
| C-MACRO-ATTR | not applicable | no macros |
| C-ANYWHERE | not applicable | no macros |
| C-MACRO-VIS | not applicable | no macros |
| C-MACRO-TY | not applicable | no macros |
| C-CRATE-DOC | not met | the crate page has no example, and the README's is not compiled (P1-3) |
| C-EXAMPLE | not met | only `find_boot_keyboard` and `changes` have one (P1-3) |
| C-QUESTION-MARK | not met | both doctests `unwrap` (P1-3) |
| C-FAILURE | not met | no `# Errors` section on any fallible function (P1-2) |
| C-LINK | met | items link to each other and to the constants they read |
| C-METADATA | not met | no `include` (P1-4) and no `documentation` key (P2-4) |
| C-RELNOTES | met | `CHANGELOG.md` with an Unreleased section |
| C-HIDDEN | met | the verification module is private; nothing is `doc(hidden)` |
| C-SMART-PTR | not applicable | no smart pointer |
| C-CONV-SPECIFIC | met | `to_u64` and `is_device_to_host` are methods on `SetupPacket` |
| C-METHOD | met | each parse is an associated function of the type it returns |
| C-NO-OUT | met | every function returns its result; `changes` reports through a closure, not an out parameter |
| C-OVERLOAD | not applicable | no operator |
| C-DEREF | not applicable | no `Deref` |
| C-CTOR | met | `SetupPacket::get_descriptor`, `set_configuration`, `set_boot_protocol`, `set_idle_forever` and each `parse` |
| C-INTERMEDIATE | not met | the walk exposes only its answer, not the descriptors it passed (P2-1) |
| C-CALLER-CONTROL | met | the caller owns every buffer and every transfer |
| C-GENERIC | not met | `changes` takes `&mut dyn FnMut` rather than a generic or an iterator (P0-3) |
| C-OBJECT | not applicable | no traits |
| C-NEWTYPE | not met | `u8` stays where every value is valid (D5), but `request_type` has reserved values (P0-4) |
| C-CUSTOM-TYPE | not met | the `bool` argument of the `changes` callback (P0-3) |
| C-BITFLAG | met | the modifier byte stays the report's own byte, and `changes` turns it into usages |
| C-BUILDER | not applicable | no type with many optional parts |
| C-VALIDATE | met | every length is checked before it is read through, and proven with Kani |
| C-DTOR-FAIL | not applicable | no `Drop` |
| C-DTOR-BLOCK | not applicable | no `Drop` |
| C-DEBUG | met | every public type derives `Debug` |
| C-DEBUG-NONEMPTY | met | the derived output names each type |
| C-SEALED | not applicable | no traits |
| C-STRUCT-PRIVATE | not met | `DeviceDescriptor`, `ConfigurationHeader`, `BootKeyboard` and `BootReport` (P0-2) |
| C-NEWTYPE-HIDE | not applicable | no wrapper type |
| C-STRUCT-BOUNDS | not applicable | no generic types |
| C-STABLE | met | no dependencies |
| C-PERMISSIVE | met | MIT OR Apache-2.0 |

Totals: 18 met, 14 not met, 22 not applicable.
