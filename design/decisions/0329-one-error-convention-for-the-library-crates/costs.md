# One error convention: what option A costs, crate by crate

The measured cost behind [option A of the error convention](../0329-one-error-convention-for-the-library-crates.md),
read from each crate's `origin/main` on 2026-11-26 (UTC). The main page is complete without it. A
script made the counts, and a reading of the source settled what the script could not.

## Types and variants changed

"name" turns a positional variant into named fields, "mark" adds `#[non_exhaustive]`, "traits" adds
`Display` and `core::error::Error`, and "rename" follows rule 10.

| crate | what changes | types | variants | renames |
|---|---|---|---|---|
| `address_space_layout` | `Error`; mark the enum and its two struct variants | 1 | 2 | 1 |
| `block_roster_contract` | mark `TooManyDevices` | 1 | 0 | 1 |
| `capability_table` | mark the enum | 1 | 0 | 0 |
| `designware_ethernet` | traits on four; one `source`; name 1; mark 4 variants | 4 | 5 | 0 |
| `designware_mobile_storage` | name 20; stop rendering 7 wrappers (2 among the 20); two `source` | 4 | 25 | 2 |
| `device_tree_blob` | name 4; `offset` on 5 (`BadToken` in both) | 1 | 8 | 0 |
| `domain_name_system` | mark `Reject`; name `ServerError`; `offset` on 8 | 2 | 9 | 1 |
| `e1000e` | stop rendering in two wrapping variants | 1 | 2 | 0 |
| `entropy_contract` | traits on `Refusal`; mark two unit structs and `ShortReply` | 3 | 1 | 3 |
| `environment_contract` | mark the enum | 1 | 0 | 1 |
| `file_allocation_table` | name 3; mark 5 variants | 4 | 8 | 0 |
| `grant_plan` | traits and mark on five; name `NoSuchCapability`; mark `MemoryGrantOutOfRange` | 5 | 2 | 5 |
| `interfaces_note` | traits and mark on both; name `BadField` | 2 | 1 | 1 |
| `line_editor` | traits and mark; name `Layout` | 1 | 1 | 1 |
| `program_argument_contract` | traits and mark on both | 2 | 0 | 2 |
| `universal_serial_bus` | traits and mark; mark 3 variants; `at` becomes `offset` | 1 | 3 | 1 |

In all, 34 of the 51 types change in 16 crates and 67 variants change shape. `device_tree_blob` and
the `Error` of `domain_name_system` count `offset` on each variant that refuses a part of a
variable-length walk. `domain_name_system` gave `Error` and `Reject` their traits and a `source` at
`8f6dd771da`, so its row asks for the shape only.

The 19 renames are the types whose names do not end in `Error`: `ImagePlacement`,
`TooManyDevices`, `Fault`, `Refusal` (six crates), `Reject`, `OperationOutOfRange`,
`StepOutOfRange`, `Refused`, `PathRefusal`, `BindRefusal`, `NameSetFull`, `NoJobNamed`,
`PushRefused` and `WrongPageLength`. Each new name stays provisional until its crate's review
ratifies it.

## New types under rule 1

Rule 1 reaches eight crates where a refusal has more than one cause and answers with `Option`,
`bool` or a raw integer.

| crate | commit | today | new types |
|---|---|---|---|
| `generational_table` | `b5243332a6` | `insert` drops the value when full (block 1135) | 1 |
| `extensible_host_controller_interface` | `a10790e155` | `complete` answers `false` for two causes; `find_extended` answers `None` for four | 2 |
| `file_system_contract` | `0551506169` | `extended_attribute::set` and `remove` return `Result<usize, i32>` | 1 |
| `boot_ladder` | `019d76c8e5` | `in_line` and `parse` answer `None` for no verdict and a damaged one (block 1154) | 1 |
| `grant_contract` | `f84cd7e6ff` | `ShortOptions::try_new` answers `None` for three broken rules | 1 |
| `jh7110_entropy` | `eac91efd03` | `Pool::refill` answers `false` for every generator failure (block 1150) | 1 |
| `file_allocation_table` | `b55594420e` | both `fill_sector` builders answer `false` (block 1143) | 1 |
| `non_volatile_memory_express` | `60b34280ec` | twelve functions answer `None`, some for three causes (block 1149) | 3 |

That makes 11 new types in 8 crates. The `non_volatile_memory_express` count takes block 1149's
three families: the Identify parses, the `Namespace` functions and the pointer builders.

Seven crates need nothing from rule 1. `byte_glob`, `byte_sink_contract`, `clock_contract`,
`counter_frequency_contract`, `intrusive_queue` and `terminal_contract` answer with predicates or
with an `Option` that has one cause. `jh7110_clock_and_reset` (`2c614b2f6c`), which the census of
milestone 1129 (the combine review) left out, has no error type of its own. Its fallible functions
pass the device tree provider's `E` through, and its index lookups answer `None` for an index out of
range, which is an ordinary absence. Its review applies rules 2 to 10 if it ever adds a type.

## Tests that build a marked variant

Rule 4 has a cost inside each crate. Code outside a crate cannot build its `#[non_exhaustive]`
variants, and the files under `tests/` sit outside it. A script counted the expressions there that
build a variant rule 4 or rule 6 would mark:

| crate | constructions | where |
|---|---|---|
| `device_tree_blob` | 72 | `tests/hostile.rs`, `tests/strings_block.rs` |
| `domain_name_system` | 28 | `tests/replies.rs` |
| `file_allocation_table` | 11 | `tests/the_errors_display.rs` |

The other crates build none. Each of the 111 becomes a `matches!` with `{ .. }`, and a test of a
marked variant's message moves into the crate's own unit tests, where the crate can still build
the variant. The count is a pattern match over source lines, so it may be off by a few.

## Rule 8 traced

Fifteen enums in ten crates have more than one public entry point. I traced two:

- `universal_serial_bus::Refusal` has three. `DeviceDescriptor::parse` and
  `ConfigurationHeader::parse` return only `Truncated` and `NotThatDescriptor`, and
  `find_boot_keyboard` returns those through the header and four more. The groups share a variant,
  so rule 8 keeps one enum, as block 1148's D4 recommends.
- `grant_plan::Refusal` has eight, in five modules. The modules' variant sets chain together:
  `UnclosedQuote` joins the line, parsing and word modules, and `planning` shares a variant with
  each of the others. Rule 8 keeps one enum.

The stricter test, split whenever an entry point cannot return a variant, splits both. It turns
`universal_serial_bus::Refusal` into two types, against block 1148's D4 and the single enums it
cites in `nusb` and `crab-usb`. A module-level reading of `grant_plan::Refusal` turns it into
about five, and the shell that names its variants 14 times changes with it. I did not trace the other 13.
