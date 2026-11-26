# The census of shared shapes

An appendix to [the milestone](../1129-crate-interfaces-best-in-class.md). It is step 1 of
[the order](../1129-crate-interfaces-best-in-class.md#the-order): each shape in
[the shared-shapes table](../1129-crate-interfaces-best-in-class.md#across-crates-what-they-share),
counted in each of the 29 crates at a named commit of its `main`.

Counted on 2026-11-26 (UTC), after `git fetch origin` in each crate's checkout. The commit is
`origin/main` at that fetch. Every command reads that commit and no working tree, so the same commit
gives the same number, and a crate that has changed since gives another. The counts cover the
crate's library sources: `src/`, or `file_system_contract/src/` for `file_system_contract`, whose
repository also holds the unpublished `file_system_fixture`. Files named `tests.rs` and anything
under a `tests/` directory stay out. A `mod tests` inside a source file stays in, and the section of
each shape says where that could change a count.

## How to repeat a count

`<repo>` is a crate's repository and `<commit>` its commit from the table. Define this once:

```sh
census() {  # census <repo> <ERE> <commit>: lines of the library sources that match
  src=src; [ "$1" = file_system_contract ] && src=file_system_contract/src
  git -C "$1" grep -hE "$2" "$3" -- "$src" ':(exclude,glob)**/tests.rs' ':(exclude,glob)**/tests/**' | wc -l
}
```

A cell is `census <repo> '<ERE>' <commit>` with the pattern its column names below. For example,
`byte_glob`'s E3 is
`census byte_glob '^\s*impl(<.*>)? +(core::error::|std::error::)?Error +for ' a095cd860a`. Two
columns are not that command and carry their own: S2 and F1 read the manifest, and M1 lists files. E4
is a reading, because no grep decides it.

| crate | commit | E1 | E2 | E3 | E4 | E5 | D1 | T1 | H1 | R1 | B1 | V1 | S1 | S2 | S3 | F1 | C1 | C2 | C3 | M1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `address_space_layout` | `9568826fc8` | 0 | 1 | 0 | 0/1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 |
| `block_roster_contract` | `f0c199acc9` | 1 | 2 | 2 | 2/2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 1 | 1 | 0 |
| `boot_ladder` | `019d76c8e5` | 0 | 4 | 0 | 0/0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `byte_glob` | `a095cd860a` | 0 | 0 | 0 | 0/0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `byte_sink_contract` | `8a477c6a31` | 0 | 0 | 0 | 0/0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 |
| `capability_table` | `a0e8b159e5` | 1 | 1 | 1 | 1/1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| `clock_contract` | `92079a486b` | 0 | 0 | 0 | 0/0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0 |
| `counter_frequency_contract` | `4decec9d5e` | 0 | 0 | 0 | 0/0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0 |
| `designware_ethernet` | `565b331f07` | 4 | 0 | 0 | 0/4 | 3 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `designware_mobile_storage` | `ac950346f3` | 5 | 4 | 4 | 4/4 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 4 |
| `device_tree_blob` | `9ed5c2a970` | 1 | 1 | 1 | 1/1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `domain_name_system` | `513558c4ae` | 1 | 1 | 0 | 0/1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `e1000e` | `6f6d3f1cc2` | 4 | 4 | 4 | 4/4 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `entropy_contract` | `5150f14f78` | 1 | 2 | 2 | 2/3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 |
| `environment_contract` | `62ea88d90a` | 1 | 1 | 1 | 1/1 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0 |
| `extensible_host_controller_interface` | `a10790e155` | 0 | 0 | 0 | 0/0 | 2 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `file_allocation_table` | `77d4799870` | 15 | 15 | 15 | 15/15 | 19 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 2 | 0 | 0 | 0 | 0 |
| `file_system_contract` | `0551506169` | 0 | 0 | 0 | 0/0 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 2 | 0 | 0 |
| `generational_table` | `b5243332a6` | 0 | 0 | 0 | 0/0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `grant_contract` | `f84cd7e6ff` | 0 | 0 | 0 | 0/0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 |
| `grant_plan` | `69aedfbc9a` | 3 | 0 | 0 | 0/3 | 14 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 |
| `interfaces_note` | `088baba279` | 2 | 0 | 0 | 0/2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 |
| `intrusive_queue` | `7368a9e32e` | 0 | 0 | 0 | 0/0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `jh7110_entropy` | `eac91efd03` | 0 | 0 | 0 | 0/0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `line_editor` | `2c625ef614` | 1 | 0 | 0 | 0/1 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| `non_volatile_memory_express` | `60b34280ec` | 2 | 2 | 2 | 2/2 | 9 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `program_argument_contract` | `b097970b86` | 1 | 0 | 0 | 0/1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0 |
| `terminal_contract` | `591aed99de` | 0 | 0 | 0 | 0/0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 |
| `universal_serial_bus` | `4612f6b5e5` | 1 | 0 | 0 | 0/1 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Errors (E1 to E5)

The question is whether each error type is one a caller can match, implements `core::fmt::Display`
and `core::error::Error`, and how the crate reports failure without an error type.

```sh
# E1, error-named public types
census <repo> '^\s*pub (enum|struct) \w*(Error|Refus|Fault|Failure)' <commit>
# E2, Display implementations of any type
census <repo> '^\s*impl(<.*>)? +(core::fmt::|fmt::)?Display +for ' <commit>
# E3, Error implementations
census <repo> '^\s*impl(<.*>)? +(core::error::|std::error::)?Error +for ' <commit>
# E5, public functions whose one-line signature returns an Option
census <repo> '^\s*pub (const )?(unsafe )?fn .*-> Option<' <commit>
```

E4 reads the public types that appear as the `E` of a `Result<_, E>` in a public signature, found
with `git -C <repo> grep -nE 'Result<|Err\(' <commit> -- src`. It reads "implementing/types": 8/8
means all eight error types implement `core::error::Error`. E1 misses four error types whose names
do not say so (`address_space_layout::ImagePlacement`, `block_roster_contract::TooManyDevices`,
`entropy_contract::OperationOutOfRange` and `StepOutOfRange`), which is why E4 is a reading.
`designware_mobile_storage::Fault` is a simulator knob and does not count. E5 misses a signature
split over several lines, and it counts an absent value as well as a failure. No E1, E2 or E3 hit
sits below its file's first `mod tests`.

Twelve crates have no error type (E4 is 0/0): `boot_ladder`, `byte_glob`, `byte_sink_contract`,
`clock_contract`, `counter_frequency_contract`, `extensible_host_controller_interface`,
`file_system_contract`, `generational_table`, `grant_contract`, `intrusive_queue`, `jh7110_entropy`
and `terminal_contract`. Of them, only `file_system_contract` has a fallible function: it returns a
raw `i32` error number (`Result<usize, i32>` in `extended_attribute.rs`).

## DMA regions, doorbells and tails, register access (D1 to V1)

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

The reading of the traits, at the commits above. The three D1 traits differ as the milestone says.
`designware_ethernet` and `e1000e` take `u64` offsets and carry no barrier. `designware_mobile_storage`
takes `u32` offsets, a `barrier` method, the bus address and the length. The two T1 traits each set
the receive tail and the transmit tail, with a `barrier`. The R1 traits are
`designware_ethernet::Hardware` (`u32` offsets), `e1000e::Hardware` (`u64` offsets, a flash status
read, the PCI vendor identifier and a note hook) and
`designware_mobile_storage::RegisterWindowAndClock` (`u32` offsets and a clock). H1 therefore misses
one register trait that R1 finds. `non_volatile_memory_express` and
`extensible_host_controller_interface` declare no such trait. They compute the doorbell offset (B1)
and leave the access to the caller, as does `jh7110_entropy`. V1 is zero everywhere: a looser grep
finds four hits, all doc comments. No manifest names `tock-registers` or `safe-mmio`:
`git -C <repo> show <commit>:Cargo.toml | grep -cE '^(tock-registers|safe-mmio) *='` prints 0.

## Byte sinks and sources (S1 to S3)

```sh
# S1, a public trait named for a byte sink, source, reader, writer, device or stream
census <repo> '^\s*pub (unsafe )?trait \w*(Sink|Source|Reader|Writer|Device|Stream)\w*' <commit>
# S2, an embedded-io dependency in the manifest
git -C <repo> show <commit>:Cargo.toml | grep -cE '^embedded-io *='
# S3, any mention of fmt::Write
census <repo> '\bfmt::Write\b' <commit>
```

S1 finds `line_editor::Sink` and the two traits of `file_allocation_table`, `SectorDevice` and
`WritableSectorDevice`. That crate alone has S2, behind the feature `embedded-io-07`, off by default.
The reading of S3: the hit in `block_roster_contract` and the two in `grant_plan` all sit below
their file's first `mod tests`, so no crate implements or accepts `core::fmt::Write` in library
code. `byte_sink_contract` holds the layout of a byte channel and declares no trait, so S1 does not
count it.

## Feature names (F1)

```sh
# F1, the entries of the manifest's [features] table (file_system_contract/Cargo.toml for that crate)
git -C <repo> show <commit>:Cargo.toml | sed -n '/^\[features\]/,/^\[/p'
```

F1 counts entries. Three crates declare features and 26 declare none: `capability_table` has `peak`,
`designware_mobile_storage` has `simulator`, and `file_allocation_table` has the empty `default` and
`embedded-io-07`. Every `feature = "..."` in the sources names one of those
(`git -C <repo> grep -ohE 'feature *= *"[^"]+"' <commit> -- src`), and no crate has a `std` or
`alloc` feature.

## Contract crates (C1 to C3)

```sh
# C1, an interface identity
census <repo> '^\s*pub const INTERFACE_ID\b' <commit>
# C2, a version (INTERFACES_VERSION in interfaces_note matches the prefix)
census <repo> '^\s*pub const (\w+_)?VERSION\b' <commit>
# C3, a magic
census <repo> '^\s*pub const MAGIC\b' <commit>
```

A contract crate here exports `INTERFACE_ID`: twelve crates. `file_system_contract` exports two, one
for the block protocol (14) and one for the file-service protocol (15), each with its own `VERSION`.
The identities are `address_space_layout` 2, `block_roster_contract` 5, `byte_sink_contract` 6,
`clock_contract` 8, `counter_frequency_contract` 9, `entropy_contract` 12, `environment_contract`
13, `grant_contract` 17, `program_argument_contract` 18, `interfaces_note` 21 and `terminal_contract`
25. Five of the twelve also export a `MAGIC`: a `u64` in `block_roster_contract` and
`clock_contract`, a `[u8; 8]` in `counter_frequency_contract`, `environment_contract` and
`program_argument_contract`. Seven export none. `line_editor` exports a `u32` `MAGIC` for its
hand-off page and no identity, which makes C3 six crates and C1 with C3 five. Every `VERSION` is a
`u32` of 1 except `program_argument_contract`, which is 2.

The entry points come from
`git -C <repo> grep -hoE '^\s*pub (const )?fn \w*(decode|parse|unpack|encode|build|pack|request|read|write|new|check|valid)\w*' <commit> -- src`
and share no spelling:

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

Six of the twelve have error types: `address_space_layout` (`ImagePlacement`),
`block_roster_contract` (two), `entropy_contract` (three), `environment_contract` (`Refused`),
`interfaces_note` (`Error` and `Refusal`) and `program_argument_contract` (`PushRefused`).

## Simulators (M1)

```sh
# M1, files outside fuzz/ whose path names a simulator or a fake
git -C <repo> ls-tree -r --name-only <commit> | grep -v '^fuzz/' | grep -ciE 'simulat|fake'
```

M1 counts files, and the reading says what each is. `designware_mobile_storage` is the one crate
that exports a simulator: `exported_simulator.rs` re-exports `SimulatedHostController` and
`SimulatedDirectMemoryAccessRegion` behind the feature `simulator`, and `tests/simulator.rs` runs
only with it. `designware_ethernet` (`src/simulator.rs`) and `e1000e`
(`src/platform_controller_hub/simulator.rs`) keep theirs behind `#[cfg(test)]`, out of a caller's
reach. `extensible_host_controller_interface` has `examples/fake_controller.rs`, an example and not
a library item. `non_volatile_memory_express`, `universal_serial_bus` and `jh7110_entropy` have no
simulator or fake.

## The totals

Crates having each shape, out of the 29, with the column that counts it.

| shape | measure | crates |
|---|---|---|
| Errors | has an error type (E4) | 17 |
| Errors | implements `core::error::Error` on every error type (E4) | 8 |
| Errors | implements it on some error types, not all (E4) | 1 |
| Errors | has error types and implements it on none (E4) | 8 |
| Errors | has any `Error` implementation (E3) | 9 |
| Errors | has no error type (E4) | 12 |
| DMA regions | declares a DMA-region trait (D1) | 3 |
| Doorbells and tails | declares a `Tails` trait (T1) | 2 |
| Doorbells and tails | computes a doorbell offset with a function (B1) | 2 |
| Register access | declares a register read and write by offset (R1) | 3 |
| Register access | declares a trait named `Hardware` (H1) | 2 |
| Register access | makes a volatile access in library code (V1) | 0 |
| Byte sinks and sources | declares a byte sink, source or device trait (S1) | 2 |
| Byte sinks and sources | depends on `embedded-io` (S2) | 1 |
| Byte sinks and sources | implements or accepts `core::fmt::Write` in library code (S3, read) | 0 |
| Feature names | declares a feature (F1) | 3 |
| Contract crates | exports an interface identity (C1) | 12 |
| Contract crates | exports an identity and a magic (C1 and C3) | 5 |
| Simulators | exports a simulator behind a feature (M1, read) | 1 |
| Simulators | has a simulator or a fake of any kind (M1) | 4 |

## Outside the 29

`partsfoundry/jh7110_clock_and_reset` exists in the organization and is empty
(`gh repo view partsfoundry/jh7110_clock_and_reset --json isEmpty`), so it has no commit to count
and is not one of the 29. The milestone leaves out `rsext4` and `file_system_fixture`.
