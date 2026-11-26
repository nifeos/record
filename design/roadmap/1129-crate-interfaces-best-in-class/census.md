# The census of shared shapes

An appendix to [the milestone](../1129-crate-interfaces-best-in-class.md). It is step 1 of
[the order](../1129-crate-interfaces-best-in-class.md#the-order): each shape in
[the shared-shapes table](../1129-crate-interfaces-best-in-class.md#across-crates-what-they-share),
counted in each of the 29 crates, at a named commit of each crate's `main`.

Measured on 2026-11-26 (UTC), after `git fetch origin` in each crate's checkout. The commit is
`origin/main` at that fetch, and every command below reads that commit and no working tree, so a
reader gets the same numbers from the same commit. A crate that has changed since is a different
count. The counts are of the crate's library sources: `src/` of the repository, or
`file_system_contract/src/` for `file_system_contract`, whose repository also holds the unpublished
`file_system_fixture`. Files named `tests.rs` and anything under a `tests/` directory are left out. A
`mod tests` inside a source file is not, and where that could change a count the check is named
under the shape.

## How to repeat a count

Each crate's repository is `<repo>`, and its commit is in the table below. Define this once:

```sh
census() {  # census <repo> <ERE> <commit>: lines of the library sources that match
  src=src; [ "$1" = file_system_contract ] && src=file_system_contract/src
  git -C "$1" grep -hE "$2" "$3" -- "$src" ':(exclude,glob)**/tests.rs' ':(exclude,glob)**/tests/**' | wc -l
}
```

A count in a table below is `census <repo> '<ERE>' <commit>`, with the pattern the shape names
and the crate's own repository and commit. For example, `byte_glob`'s count of E3 is
`census byte_glob '^\s*impl(<.*>)? +(core::error::|std::error::)?Error +for ' a095cd860a`. A
column marked (read) is not a command: a grep could not decide it, and the paragraph under the
table says what was read and where.

| crate | commit | crate | commit |
|---|---|---|---|
| `address_space_layout` | `9568826fc8` | `block_roster_contract` | `f0c199acc9` |
| `boot_ladder` | `019d76c8e5` | `byte_glob` | `a095cd860a` |
| `byte_sink_contract` | `8a477c6a31` | `capability_table` | `a0e8b159e5` |
| `clock_contract` | `92079a486b` | `counter_frequency_contract` | `4decec9d5e` |
| `designware_ethernet` | `565b331f07` | `designware_mobile_storage` | `ac950346f3` |
| `device_tree_blob` | `9ed5c2a970` | `domain_name_system` | `513558c4ae` |
| `e1000e` | `6f6d3f1cc2` | `entropy_contract` | `5150f14f78` |
| `environment_contract` | `62ea88d90a` | `extensible_host_controller_interface` | `a10790e155` |
| `file_allocation_table` | `77d4799870` | `file_system_contract` | `0551506169` |
| `generational_table` | `b5243332a6` | `grant_contract` | `f84cd7e6ff` |
| `grant_plan` | `69aedfbc9a` | `interfaces_note` | `088baba279` |
| `intrusive_queue` | `7368a9e32e` | `jh7110_entropy` | `eac91efd03` |
| `line_editor` | `2c625ef614` | `non_volatile_memory_express` | `60b34280ec` |
| `program_argument_contract` | `b097970b86` | `terminal_contract` | `591aed99de` |
| `universal_serial_bus` | `4612f6b5e5` |  |  |
## Errors

The question is whether each error type is one a caller can match, implements `core::fmt::Display`
and `core::error::Error`, and how the crate reports failure where it has no error type.

```sh
# E1, error-named public types
census <repo> '^\s*pub (enum|struct) \w*(Error|Refus|Fault|Failure)' <commit>
# E2, Display implementations (any type)
census <repo> '^\s*impl(<.*>)? +(core::fmt::|fmt::)?Display +for ' <commit>
# E3, Error implementations
census <repo> '^\s*impl(<.*>)? +(core::error::|std::error::)?Error +for ' <commit>
# E5, public functions whose one-line signature returns an Option
census <repo> '^\s*pub (const )?(unsafe )?fn .*-> Option<' <commit>
```

E4 is read: the public types that appear as the `E` of a `Result<_, E>` in a public signature
(found with `git -C <repo> grep -nE 'Result<|Err\(' <commit> -- src` and then read), and how many of
them implement `core::error::Error`, written "implementing of types". E1 misses four error types
whose names do not say so: `address_space_layout::ImagePlacement`,
`block_roster_contract::TooManyDevices`, and `entropy_contract::OperationOutOfRange` and
`StepOutOfRange`, which is why E4 is read. `designware_mobile_storage::Fault` is a knob of the
simulator, not an error, and is not counted. E5 counts one-line signatures only, so a signature split
over several lines is missed, and it counts absence as well as failure. Nothing in E1 to E3 sits
below a `mod tests`: each hit was compared with the line of its file's first `mod tests`.

| crate | E1 | E2 | E3 | E4 (read) | E5 |
|---|---|---|---|---|---|
| `address_space_layout` | 0 | 1 | 0 | 0 of 1 | 0 |
| `block_roster_contract` | 1 | 2 | 2 | 2 of 2 | 2 |
| `boot_ladder` | 0 | 4 | 0 | 0 of 0 | 5 |
| `byte_glob` | 0 | 0 | 0 | 0 of 0 | 0 |
| `byte_sink_contract` | 0 | 0 | 0 | 0 of 0 | 1 |
| `capability_table` | 1 | 1 | 1 | 1 of 1 | 1 |
| `clock_contract` | 0 | 0 | 0 | 0 of 0 | 0 |
| `counter_frequency_contract` | 0 | 0 | 0 | 0 of 0 | 1 |
| `designware_ethernet` | 4 | 0 | 0 | 0 of 4 | 3 |
| `designware_mobile_storage` | 5 | 4 | 4 | 4 of 4 | 1 |
| `device_tree_blob` | 1 | 1 | 1 | 1 of 1 | 0 |
| `domain_name_system` | 1 | 1 | 0 | 0 of 1 | 1 |
| `e1000e` | 4 | 4 | 4 | 4 of 4 | 1 |
| `entropy_contract` | 1 | 2 | 2 | 2 of 3 | 1 |
| `environment_contract` | 1 | 1 | 1 | 1 of 1 | 6 |
| `extensible_host_controller_interface` | 0 | 0 | 0 | 0 of 0 | 2 |
| `file_allocation_table` | 15 | 15 | 15 | 15 of 15 | 19 |
| `file_system_contract` | 0 | 0 | 0 | 0 of 0 | 12 |
| `generational_table` | 0 | 0 | 0 | 0 of 0 | 5 |
| `grant_contract` | 0 | 0 | 0 | 0 of 0 | 6 |
| `grant_plan` | 3 | 0 | 0 | 0 of 3 | 14 |
| `interfaces_note` | 2 | 0 | 0 | 0 of 2 | 1 |
| `intrusive_queue` | 0 | 0 | 0 | 0 of 0 | 2 |
| `jh7110_entropy` | 0 | 0 | 0 | 0 of 0 | 2 |
| `line_editor` | 1 | 0 | 0 | 0 of 1 | 7 |
| `non_volatile_memory_express` | 2 | 2 | 2 | 2 of 2 | 9 |
| `program_argument_contract` | 1 | 0 | 0 | 0 of 1 | 0 |
| `terminal_contract` | 0 | 0 | 0 | 0 of 0 | 1 |
| `universal_serial_bus` | 1 | 0 | 0 | 0 of 1 | 3 |

Two more facts from the reading. `file_system_contract` has no error type: its fallible functions
return a raw `i32` error number (`Result<usize, i32>` in `extended_attribute.rs`). Twelve crates
have no error type at all (E4 is 0 of 0): `boot_ladder`, `byte_glob`, `byte_sink_contract`,
`clock_contract`, `counter_frequency_contract`, `extensible_host_controller_interface`,
`file_system_contract`, `generational_table`, `grant_contract`, `intrusive_queue`, `jh7110_entropy`
and `terminal_contract`. They return values, options, booleans or nothing that can fail.

## DMA regions, doorbells and tails, register access

```sh
# D1, a public DMA-region trait
census <repo> '^\s*pub (unsafe )?trait \w*DirectMemoryAccessRegion\b' <commit>
# T1, a public Tails trait
census <repo> '^\s*pub (unsafe )?trait \w*Tails\b' <commit>
# H1, a public trait named Hardware
census <repo> '^\s*pub (unsafe )?trait Hardware\b' <commit>
# R1, a trait that declares a register read by offset
census <repo> '^\s*fn read\(&mut self, offset: u(32|64)\) -> u32;' <commit>
# B1, a public function that computes a doorbell
census <repo> '^\s*pub (const )?fn \w*doorbell\w*' <commit>
# V1, a volatile access outside a comment
census <repo> '^[^/]*(read|write)_volatile' <commit>
```

| crate | D1 | T1 | H1 | R1 | B1 | V1 |
|---|---|---|---|---|---|---|
| `address_space_layout` | 0 | 0 | 0 | 0 | 0 | 0 |
| `block_roster_contract` | 0 | 0 | 0 | 0 | 0 | 0 |
| `boot_ladder` | 0 | 0 | 0 | 0 | 0 | 0 |
| `byte_glob` | 0 | 0 | 0 | 0 | 0 | 0 |
| `byte_sink_contract` | 0 | 0 | 0 | 0 | 0 | 0 |
| `capability_table` | 0 | 0 | 0 | 0 | 0 | 0 |
| `clock_contract` | 0 | 0 | 0 | 0 | 0 | 0 |
| `counter_frequency_contract` | 0 | 0 | 0 | 0 | 0 | 0 |
| `designware_ethernet` | 1 | 1 | 1 | 1 | 0 | 0 |
| `designware_mobile_storage` | 1 | 0 | 0 | 1 | 0 | 0 |
| `device_tree_blob` | 0 | 0 | 0 | 0 | 0 | 0 |
| `domain_name_system` | 0 | 0 | 0 | 0 | 0 | 0 |
| `e1000e` | 1 | 1 | 1 | 1 | 0 | 0 |
| `entropy_contract` | 0 | 0 | 0 | 0 | 0 | 0 |
| `environment_contract` | 0 | 0 | 0 | 0 | 0 | 0 |
| `extensible_host_controller_interface` | 0 | 0 | 0 | 0 | 1 | 0 |
| `file_allocation_table` | 0 | 0 | 0 | 0 | 0 | 0 |
| `file_system_contract` | 0 | 0 | 0 | 0 | 0 | 0 |
| `generational_table` | 0 | 0 | 0 | 0 | 0 | 0 |
| `grant_contract` | 0 | 0 | 0 | 0 | 0 | 0 |
| `grant_plan` | 0 | 0 | 0 | 0 | 0 | 0 |
| `interfaces_note` | 0 | 0 | 0 | 0 | 0 | 0 |
| `intrusive_queue` | 0 | 0 | 0 | 0 | 0 | 0 |
| `jh7110_entropy` | 0 | 0 | 0 | 0 | 0 | 0 |
| `line_editor` | 0 | 0 | 0 | 0 | 0 | 0 |
| `non_volatile_memory_express` | 0 | 0 | 0 | 0 | 2 | 0 |
| `program_argument_contract` | 0 | 0 | 0 | 0 | 0 | 0 |
| `terminal_contract` | 0 | 0 | 0 | 0 | 0 | 0 |
| `universal_serial_bus` | 0 | 0 | 0 | 0 | 0 | 0 |

What the traits are, read from the source at the commits above. The three D1 traits differ as the
milestone says: `designware_ethernet` and `e1000e` take `u64` offsets and carry no barrier, and
`designware_mobile_storage` takes `u32` offsets and a `barrier` method (it also carries the bus
address and the length). The two T1 traits (`designware_ethernet::Tails` and `e1000e::Tails`) each
set the receive tail and the transmit tail, with a `barrier`. The R1 traits are
`designware_ethernet::Hardware` (`u32` offsets), `e1000e::Hardware` (`u64` offsets, with a flash
status read, the PCI vendor identifier and a note hook) and
`designware_mobile_storage::RegisterWindowAndClock` (`u32` offsets and a clock), so H1 misses one
register-access trait that R1 finds. `non_volatile_memory_express` and
`extensible_host_controller_interface` have no such trait: they compute the doorbell offset (B1)
and leave the access to the caller, as does `jh7110_entropy`, whose manifest says so. V1 is zero
everywhere: the four hits of a looser grep are doc comments. No crate depends on `tock-registers`
or `safe-mmio`: `git -C <repo> show <commit>:Cargo.toml | grep -cE '^(tock-registers|safe-mmio) *='`
prints 0 for each.

## Byte sinks and sources

```sh
# S1, a public trait named for a byte sink, source, reader, writer, device or stream
census <repo> '^\s*pub (unsafe )?trait \w*(Sink|Source|Reader|Writer|Device|Stream)\w*' <commit>
# S2, an embedded-io dependency in the manifest
git -C <repo> show <commit>:Cargo.toml | grep -cE '^embedded-io *='
# S3, any mention of fmt::Write
census <repo> '\bfmt::Write\b' <commit>
```

| crate | S1 | S2 | S3 | S3 in library code (read) |
|---|---|---|---|---|
| `address_space_layout` | 0 | 0 | 0 | 0 |
| `block_roster_contract` | 0 | 0 | 1 | 0 |
| `boot_ladder` | 0 | 0 | 0 | 0 |
| `byte_glob` | 0 | 0 | 0 | 0 |
| `byte_sink_contract` | 0 | 0 | 0 | 0 |
| `capability_table` | 0 | 0 | 0 | 0 |
| `clock_contract` | 0 | 0 | 0 | 0 |
| `counter_frequency_contract` | 0 | 0 | 0 | 0 |
| `designware_ethernet` | 0 | 0 | 0 | 0 |
| `designware_mobile_storage` | 0 | 0 | 0 | 0 |
| `device_tree_blob` | 0 | 0 | 0 | 0 |
| `domain_name_system` | 0 | 0 | 0 | 0 |
| `e1000e` | 0 | 0 | 0 | 0 |
| `entropy_contract` | 0 | 0 | 0 | 0 |
| `environment_contract` | 0 | 0 | 0 | 0 |
| `extensible_host_controller_interface` | 0 | 0 | 0 | 0 |
| `file_allocation_table` | 2 | 1 | 0 | 0 |
| `file_system_contract` | 0 | 0 | 0 | 0 |
| `generational_table` | 0 | 0 | 0 | 0 |
| `grant_contract` | 0 | 0 | 0 | 0 |
| `grant_plan` | 0 | 0 | 2 | 0 |
| `interfaces_note` | 0 | 0 | 0 | 0 |
| `intrusive_queue` | 0 | 0 | 0 | 0 |
| `jh7110_entropy` | 0 | 0 | 0 | 0 |
| `line_editor` | 1 | 0 | 0 | 0 |
| `non_volatile_memory_express` | 0 | 0 | 0 | 0 |
| `program_argument_contract` | 0 | 0 | 0 | 0 |
| `terminal_contract` | 0 | 0 | 0 | 0 |
| `universal_serial_bus` | 0 | 0 | 0 | 0 |

S1 finds `line_editor::Sink` and `file_allocation_table`'s `SectorDevice` and `WritableSectorDevice`
(two traits, one crate). `file_allocation_table` is the one crate with S2, behind the feature
`embedded-io-07`, which is off by default. S3 is read: the one hit in `block_roster_contract` and
the two in `grant_plan` are all below the first `mod tests` of their files, so no crate implements
or accepts `core::fmt::Write` in library code. `byte_sink_contract` holds the layout of a byte
channel and declares no trait, so S1 does not count it.

## Feature names

```sh
# F1, the feature names in the manifest (file_system_contract/Cargo.toml for file_system_contract)
git -C <repo> show <commit>:Cargo.toml | sed -n '/^\[features\]/,/^\[/p'
```

| crate | F1 |
|---|---|
| `address_space_layout` | none |
| `block_roster_contract` | none |
| `boot_ladder` | none |
| `byte_glob` | none |
| `byte_sink_contract` | none |
| `capability_table` | `peak` |
| `clock_contract` | none |
| `counter_frequency_contract` | none |
| `designware_ethernet` | none |
| `designware_mobile_storage` | `simulator` |
| `device_tree_blob` | none |
| `domain_name_system` | none |
| `e1000e` | none |
| `entropy_contract` | none |
| `environment_contract` | none |
| `extensible_host_controller_interface` | none |
| `file_allocation_table` | `default`, `embedded-io-07` |
| `file_system_contract` | none |
| `generational_table` | none |
| `grant_contract` | none |
| `grant_plan` | none |
| `interfaces_note` | none |
| `intrusive_queue` | none |
| `jh7110_entropy` | none |
| `line_editor` | none |
| `non_volatile_memory_express` | none |
| `program_argument_contract` | none |
| `terminal_contract` | none |
| `universal_serial_bus` | none |

Three crates declare features and 26 declare none. `capability_table` has `peak`,
`designware_mobile_storage` has `simulator`, and `file_allocation_table` has the empty `default` and
`embedded-io-07`. Every `feature = "..."` in the sources names one of those
(`git -C <repo> grep -ohE 'feature *= *"[^"]+"' <commit> -- src`), and no crate has a `std` or
`alloc` feature.

## Contract crates

```sh
# C1, an interface identity
census <repo> '^\s*pub const INTERFACE_ID\b' <commit>
# C2, a version
census <repo> '^\s*pub const (\w+_)?VERSION\b' <commit>
# C3, a magic
census <repo> '^\s*pub const MAGIC\b' <commit>
```

| crate | C1 | C2 | C3 |
|---|---|---|---|
| `address_space_layout` | 1 | 1 | 0 |
| `block_roster_contract` | 1 | 1 | 1 |
| `boot_ladder` | 0 | 0 | 0 |
| `byte_glob` | 0 | 0 | 0 |
| `byte_sink_contract` | 1 | 1 | 0 |
| `capability_table` | 0 | 0 | 0 |
| `clock_contract` | 1 | 1 | 1 |
| `counter_frequency_contract` | 1 | 1 | 1 |
| `designware_ethernet` | 0 | 0 | 0 |
| `designware_mobile_storage` | 0 | 0 | 0 |
| `device_tree_blob` | 0 | 0 | 0 |
| `domain_name_system` | 0 | 0 | 0 |
| `e1000e` | 0 | 0 | 0 |
| `entropy_contract` | 1 | 1 | 0 |
| `environment_contract` | 1 | 1 | 1 |
| `extensible_host_controller_interface` | 0 | 0 | 0 |
| `file_allocation_table` | 0 | 0 | 0 |
| `file_system_contract` | 2 | 2 | 0 |
| `generational_table` | 0 | 0 | 0 |
| `grant_contract` | 1 | 1 | 0 |
| `grant_plan` | 0 | 0 | 0 |
| `interfaces_note` | 1 | 1 | 0 |
| `intrusive_queue` | 0 | 0 | 0 |
| `jh7110_entropy` | 0 | 0 | 0 |
| `line_editor` | 0 | 0 | 1 |
| `non_volatile_memory_express` | 0 | 0 | 0 |
| `program_argument_contract` | 1 | 1 | 1 |
| `terminal_contract` | 1 | 1 | 0 |
| `universal_serial_bus` | 0 | 0 | 0 |

A contract crate here is one that exports `INTERFACE_ID` (C1): twelve crates. `file_system_contract`
exports two, one for the block protocol (14) and one for the file-service protocol (15), each with
its own `VERSION`. The identities are `address_space_layout` 2, `block_roster_contract` 5,
`byte_sink_contract` 6, `clock_contract` 8, `counter_frequency_contract` 9, `entropy_contract` 12,
`environment_contract` 13, `grant_contract` 17, `program_argument_contract` 18, `interfaces_note`
21 and `terminal_contract` 25. Five of the twelve also export a `MAGIC` (`block_roster_contract` and
`clock_contract` as a `u64`; `counter_frequency_contract`, `environment_contract` and
`program_argument_contract` as `[u8; 8]`), and seven do not. `line_editor` exports a `MAGIC` (a
`u32`, in its hand-off page) and no identity, so C3 is 6 while the crates with both are 5. Every
`VERSION` is a `u32` with the value 1, except `program_argument_contract`, which is 2.
`interfaces_note` exports its version as `INTERFACES_VERSION`, which the `(\w+_)?` prefix in the
pattern for C2 reads.

The entry points are read from the public functions whose names carry a decode, encode, build or
request verb
(`git -C <repo> grep -hoE '^\s*pub (const )?fn \w*(decode|parse|unpack|encode|build|pack|request|read|write|new|check|valid)\w*' <commit> -- src`).
They do not share a spelling.

| crate | entry points |
|---|---|
| `address_space_layout` | `check_image` |
| `block_roster_contract` | `read`, `write` |
| `byte_sink_contract` | `pack`, `unpack` |
| `clock_contract` | `read`, `request` |
| `counter_frequency_contract` | `build_page` |
| `entropy_contract` | `request`, `requested_bytes`, `request_is_well_formed`, `readiness` |
| `environment_contract` | `build` |
| `file_system_contract` | `encode`, `decode`, `request`, `pack_name`, `unpack_name`, `write_page` and others |
| `grant_contract` | `new`, `try_new` |
| `interfaces_note` | `encode_interfaces`, `decode_interfaces`, `check_served` |
| `program_argument_contract` | `parse` |
| `terminal_contract` | `decode` |

Six of the twelve have error types: `address_space_layout` (`ImagePlacement`), `block_roster_contract`
(two), `entropy_contract` (three), `environment_contract` (`Refused`), `interfaces_note` (`Error` and
`Refusal`) and `program_argument_contract` (`PushRefused`). The other six have none.

## Simulators

```sh
# M1, files of the repository (not of fuzz/) whose path names a simulator or a fake
git -C <repo> ls-tree -r --name-only <commit> | grep -v '^fuzz/' | grep -ciE 'simulat|fake'
```

| crate | M1 |
|---|---|
| `address_space_layout` | 0 |
| `block_roster_contract` | 0 |
| `boot_ladder` | 0 |
| `byte_glob` | 0 |
| `byte_sink_contract` | 0 |
| `capability_table` | 0 |
| `clock_contract` | 0 |
| `counter_frequency_contract` | 0 |
| `designware_ethernet` | 1 |
| `designware_mobile_storage` | 4 |
| `device_tree_blob` | 0 |
| `domain_name_system` | 0 |
| `e1000e` | 1 |
| `entropy_contract` | 0 |
| `environment_contract` | 0 |
| `extensible_host_controller_interface` | 1 |
| `file_allocation_table` | 0 |
| `file_system_contract` | 0 |
| `generational_table` | 0 |
| `grant_contract` | 0 |
| `grant_plan` | 0 |
| `interfaces_note` | 0 |
| `intrusive_queue` | 0 |
| `jh7110_entropy` | 0 |
| `line_editor` | 0 |
| `non_volatile_memory_express` | 0 |
| `program_argument_contract` | 0 |
| `terminal_contract` | 0 |
| `universal_serial_bus` | 0 |

M1 is a count of files, and what each is was read. `designware_mobile_storage` is the one crate
that exports a simulator: `exported_simulator.rs` re-exports `SimulatedHostController` and
`SimulatedDirectMemoryAccessRegion` behind the feature `simulator`, and `tests/simulator.rs` runs
only with it. `designware_ethernet` (`src/simulator.rs`) and `e1000e`
(`src/platform_controller_hub/simulator.rs`) each keep one behind `#[cfg(test)]`, so a caller cannot
use it. `extensible_host_controller_interface` has `examples/fake_controller.rs`, an example and not
a library item. `non_volatile_memory_express`, `universal_serial_bus` and `jh7110_entropy` have no
simulator or fake.

## The totals

Crates that have each shape, out of the 29, with the column that counts it.

| shape | measure | crates | of 29 |
|---|---|---|---|
| Errors | has an error type (E4) | 17 | 29 |
| Errors | implements `core::error::Error` on every error type (E4) | 8 | 29 |
| Errors | implements it on some error types, not all (E4) | 1 | 29 |
| Errors | has error types and implements it on none (E4) | 8 | 29 |
| Errors | has any `Error` implementation (E3) | 9 | 29 |
| Errors | has no error type (E4) | 12 | 29 |
| DMA regions | declares a DMA-region trait (D1) | 3 | 29 |
| Doorbells and tails | declares a `Tails` trait (T1) | 2 | 29 |
| Doorbells and tails | computes a doorbell offset as a function (B1) | 2 | 29 |
| Register access | declares a register read and write by offset (R1) | 3 | 29 |
| Register access | declares a trait named `Hardware` (H1) | 2 | 29 |
| Register access | uses a volatile access in library code (V1) | 0 | 29 |
| Byte sinks and sources | declares a byte sink, source or device trait (S1) | 2 | 29 |
| Byte sinks and sources | depends on `embedded-io` (S2) | 1 | 29 |
| Byte sinks and sources | implements or accepts `core::fmt::Write` in library code (S3, read) | 0 | 29 |
| Feature names | declares a feature (F1) | 3 | 29 |
| Contract crates | exports an interface identity (C1) | 12 | 29 |
| Contract crates | exports an identity and a magic (C1 and C3) | 5 | 29 |
| Simulators | exports a simulator behind a feature (M1, read) | 1 | 29 |
| Simulators | has a simulator or a fake of any kind (M1) | 4 | 29 |

## Outside the 29

`partsfoundry/jh7110_clock_and_reset` exists in the organization and is empty at the time of the
count (`gh repo view partsfoundry/jh7110_clock_and_reset --json isEmpty`), so it has no commit to
count and is not one of the 29. `file_system_fixture` is in `file_system_contract`'s repository and
the milestone leaves it out, as it leaves out `rsext4`.
