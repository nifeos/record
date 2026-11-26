---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1059, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1158. `block_roster_contract`: the release review's findings

*(The number and the slug are provisional.)*

The release review of `partsfoundry/block_roster_contract` at commit `f0c199ac`, version
0.1.0-pre.3, under milestone 1129 (the combine review), whose
[block](1129-crate-interfaces-best-in-class.md) sets its form. The baseline is milestone 1059 (the
outside review's findings land before its first release),
[its block](1059-block-roster-contract-outside-review.md) and the cleared package
[`notes/crate-reviews/block-roster-contract.md`](../../notes/crate-reviews/block-roster-contract.md).
Every 1059 finding is closed. The page layout, the identity values, the crate's
name and the ratified names stay closed here, with one exception. The rule of
[design/naming.md](../naming.md) that spells `virtio` as `virtual_io` is newer than the
ratification of two transport constants, so the release-review rule reopens those two (P0-1).

Reuse: the crate's own tests, a scratch probe and a scratch benchmark. No new tool.

## Finding status

- P0-1, two transport constants spell `VIRTIO`: Open.
- P0-2, a transport is a bare `u32`: Open.
- P0-3, `Device` has public fields and no constructor: Open.
- P0-4, `TooManyDevices` is one unit struct for two causes: Waiting on the errors decision of milestone 1129.
- P0-5, a roster of another version reads as no roster at all: Open.
- P0-6, the identity constants and the entry points have no shared spelling: Waiting on the contract-layout decision of milestone 1129.
- P0-7, two refusal names carry no ruling: Open.
- P1-1, `devices()` returns a type nobody can name, bound to the `Roster` and not to the page: Open.
- P1-2, `Roster` and the two errors miss common traits, and `Roster` prints raw bytes: Open.
- P1-3, no `# Errors` section, and one example for nine public functions: Open.
- P1-4, the crate never names the system that gives `INTERFACE_ID` its meaning: Open.
- P2-1, no `TryFrom<&[u8]>` for `Roster`: Open.
- P2-2, `read`, `get` and `write` are not `const`: Open.
- P2-3, a reader cannot learn the capacity word: Open.
- P2-4, the count converts to `usize` with `as`: Open.
- P2-5, the changelog promises dates and carries none: Open.

## Open decisions

The one-way doors D1 to D8 below.

## Goal

A stranger who writes a kernel, a loader or a test hands a list of drives to another program in
one page and picks this crate for it. The compiler tells a transport from an ordinal. Each
refusal says what went wrong, and a second layout version can arrive without breaking a caller of
0.1.0.

## What the review read and ran

[The appendix](1158-block-roster-contract-release-review/what-was-checked.md) lists the files,
the commands with their results, the probe, each comparator and the benchmark's method.
[The guidelines table](1158-block-roster-contract-release-review/api-guidelines.md) marks the 54
API Guidelines items.

## Prior art

Measured from the crates.io API on 2026-11-26 at 22:53 (UTC). A stranger brings this crate one
problem: tell a program which drives the machine has, in a page somebody else wrote. The ranked
crates answer the first half on Linux, from the ambient `/sys`, and none has a wire form. The
neighbors and the two systems outside Rust have the page.

| crate or system | role | version read | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `block-utils` | ranked 1: lists block devices through udev | 0.11.1 | 1,091,200 | 32,524 | 2 | 2023-09-14 |
| `rs-drivelist` | ranked 2: a list of drive descriptors | 0.9.4 | 29,605 | 6,175 | 0 | 2024-08-04 |
| `blockdev` | ranked 3: walks `/sys/block` | 0.6.2 | 13,256 | 5,009 | 0 | 2026-09-05 |
| `multiboot2` | neighbor: a boot loader's tables, read by a kernel | 0.28.0 | 1,041,556 | 237,214 | 2 | 2026-09-04 |
| `zerocopy` | neighbor: what a stranger would read the page with instead | 0.8.66 | 1,210,090,471 | 360,879,323 | 938 | 2026-11-25 |
| seL4 `libsel4/include/sel4/bootinfo_types.h` | outside Rust: the page a kernel writes once for its first program | 13.0.0 | | | | |
| Linux `drivers/nvme/host/core.c`, `nvme_scan_ns_list` | outside Rust: a reader of the NVMe active namespace list | v6.12 | | | | |

`zerocopy` has a newer pre-release, and the review read its newest stable version. No
integration target applies: the crate moves no bytes and holds no device.

### What `block_roster_contract` does better

- Than `block-utils`, `rs-drivelist` and `blockdev`: no `std`, no allocation, no dependency and no
  ambient file system. `block-utils` has ten dependencies on Linux and returns `Vec<PathBuf>`.
  `rs-drivelist` returns `anyhow::Result`.
- Than `multiboot2`: the reader is safe on any bytes. `BootInformation::load` is an `unsafe fn`
  on a raw pointer, and `MemoryMapTag::memory_areas` asserts on an entry size the writer chose.
  Here `#![forbid(unsafe_code)]` and five Kani harnesses cover `read` and `write`.
- Than `zerocopy` used by hand: the five header checks come with the type, where a hand-written
  reader owes each one. The benchmark below shows the checks cost nothing.
- Than seL4's `seL4_BootInfo`: a magic and a count. A zeroed frame is no roster, where seL4's
  reader derives the length of `untypedList` from two slot numbers and trusts it.
- Than the NVMe list: a zero ends that list, so an unwritten page reads as empty.

The ranked crates beat it on what an entry says: a name, a size, a serial number, a model. The
crate's recorded reason is that listing a drive and holding it are separate authorities, so size
waits for the endpoint. An ordinal is a position in a scan, and the README says a reader may
trust no more.

## The items

Effort is S (half a day), M (a day or two) or L (longer). A one-way item binds every caller from
the first 0.1.0 tag. Each item names the symbol in `src/lib.rs` it reads.

### P0: the 0.1.0 interface

#### P0-1. Two transport constants spell `VIRTIO`

Verified in source: `TRANSPORT_VIRTIO_MEMORY_MAPPED_IO` and `TRANSPORT_VIRTIO_PCI`. The naming
rule spells the word `virtual_io` in every name the project authors, with no kept exception, and
a renamed public item carries `#[doc(alias = "virtio")]`. The clearance ratified both names
before that rule. The printed names (`virtio-mmio`, `virtio-pci`) are the specification's and
stay.
Change: `VIRTUAL_IO_MEMORY_MAPPED_IO` and `VIRTUAL_IO_PCI`, in the form P0-2 picks, with the
three aliases.
Door: one-way (D1). Effort: S.

#### P0-2. A transport is a bare `u32`

Verified in source and by building. `Device::transport` and the argument of
`count_by_transport` are `u32`, and so is the ordinal. The probe compiled
`roster.count_by_transport(device.ordinal)`. `multiboot2` wraps the same kind of number in
`MemoryAreaTypeRaw(u32)` beside an enum with a `Custom(u32)` case. `blockdev`'s `DeviceType` has
`as_str` and `Display`.
Change: `pub struct Transport(u32)` with `new`, `get`, `name` and `Display`, and the three kinds
as associated constants. An unknown number stays representable, as the page needs.
Door: one-way (D2). Effort: S in the crate, M across callers.

#### P0-3. `Device` has public fields and no constructor

Verified in source. Every writer builds `Device { transport, ordinal }`, so a field added by a
second layout version breaks each literal. The struct's documentation already warns that the
order of its fields is published behavior. `multiboot2`'s `MemoryArea` keeps its fields private
behind `new` and four `const` getters. seL4 and the ranked crates publish theirs.
Change: private fields, `pub const fn new(transport, ordinal)`, and `transport()` and
`ordinal()`. The derived order stays.
Door: one-way (D3), and the clearance ratified both field names. Effort: S, and one line at each
caller.

#### P0-4. `TooManyDevices` is one unit struct for two causes

Verified in source and by building: `write(&mut [0u8; 8], &[])` returns `Err(TooManyDevices)`
for no devices. The type is a unit struct that any caller can build, so it can gain neither a
cause nor a field. It carries neither the count nor the room. `multiboot2-common` 0.7.0 keeps
`MemoryError::ShorterThanHeader` apart from `SizeInsufficient(actual, expected)`.
`ReadError` is `#[non_exhaustive]` and carries no numbers either.
Change: a `#[non_exhaustive]` enum for `write` with a variant for each cause and named fields,
under the name and the rule on carried input that the errors decision picks.
Door: one-way (D4), and `TooManyDevices` is a ratified name. Effort: S.

#### P0-5. A roster of another version reads as no roster at all

Verified by building: a page that starts `blkrosv2` returns `ReadError::NotARoster`, the same
as a page of `0x55`. The magic carries the version digit and the page holds no other version
field, so `VERSION` is on the page only inside the magic. A reader of version 1 cannot report
that the writer is newer. `multiboot2`'s memory map tag carries `entry_version` apart from the
magic. A page that starts to return a different variant after 0.1.0 changes published behavior.
Change: a variant for a page whose first seven bytes are `blkrosv` and whose eighth is another
digit, its name provisional.
Door: one-way (D5). Effort: S.

#### P0-6. The identity constants and the entry points have no shared spelling

Verified in source. `MAGIC` is a `u64` built with `u64::from_le_bytes`, where three sibling
contract crates export `[u8; 8]`. `read` compares bytes and `write` converts back, so no caller
of this crate needs the integer. `VERSION` is a `u32` and `INTERFACE_ID` a `u64`. The reader is
the associated function `Roster::read`, and the writer is the free function `write`.
Change: whatever the contract-layout decision picks for each.
Door: one-way (D6). Effort: S.

#### P0-7. Two refusal names carry no ruling

Verified in the baseline block: `ReadError::CapacityBeyondPage` and
`ReadError::CountBeyondCapacity` are provisional. Both follow the ruled `CountBeyondPage`.
Change: ratify both as built.
Door: one-way (D7). Effort: S.

### P1: before the first release

#### P1-1. `devices()` returns a type nobody can name, bound to the `Roster` and not to the page

Verified by building. The signature is `fn devices(&self) -> impl ExactSizeIterator<Item = Device> + '_`.
Three probe functions failed to compile: `devices().rev()`, a `for` loop over `&roster`, and a
function that returns `Roster::read(page)?.devices()` for the page's lifetime. `Roster` is `Copy`
and borrows only the page. `blockdev` returns `std::slice::Iter` from `iter` and implements
`IntoIterator` twice. `multiboot2`'s `EFIMemoryAreaIter<'a>` has a name, `Clone` and
`ExactSizeIterator`.
Change: a named `Devices<'a>` that is `Clone`, double-ended, exact-size and fused;
`IntoIterator` for `Roster<'a>` and `&Roster<'a>`.
Door: two-way. Effort: S.

#### P1-2. `Roster` and the two errors miss common traits, and `Roster` prints raw bytes

Verified in source and by building. `Roster` has no `PartialEq`, `Eq` or `Hash`. `ReadError` and
`TooManyDevices` have no `Hash`. `{:?}` of a roster prints
`Roster { entries: [[0, 0, 0, 0, 1, 0, 0, 0]] }`. `multiboot2`'s `LoadError` derives `Hash` and
`Ord`.
Change: the derives, and a `Debug` that lists devices.
Door: two-way. Effort: S.

#### P1-3. No `# Errors` section, and one example for nine public functions

Verified in source. `write` has the one `# Examples` section. `Roster::read` and `write` describe
their refusals in prose under no heading. The crate page has the layout and no example. Both
examples call `unwrap`. `blockdev` gives `get_devices` an `# Errors` section and an example that
uses `?`.
Change: the sections, an example on the crate page and on `Roster::read`, and `?` in each.
Door: two-way. Effort: S.

#### P1-4. The crate never names the system that gives `INTERFACE_ID` its meaning

Verified in source and the README. The README calls the writer "one party" and leaves the rest to
"the system around this crate". The crate's doc comments say "the kernel" nine times. Nothing says whose
registry holds the number 5, so a stranger cannot tell whether the crate fits another system.
Change: one sentence that names the binary interface, and "the writer" for "the kernel".
Door: two-way, apart from D8. Effort: S.

### P2: may follow

Each is two-way and S. The appendix holds the evidence.

- P2-1: `TryFrom<&'a [u8]> for Roster<'a>` beside `read`, as `core` converts checked bytes.
  Verified in source.
- P2-2: `const fn` for `read`, `get` and `write`, so a build can check a page it embeds.
  Inferred.
- P2-3: `Roster::capacity`, the word `read` checks and then drops. Verified in source.
- P2-4: `usize::try_from` for the count and the capacity word in `read`; `as` truncates where
  `usize` is 16 bits. Inferred, since no such target was built.
- P2-5: a date on each changelog heading, as its first line promises. Verified in source.

### Measured performance

Measured in a release build with rustc 1.100.0 on a Linux x86_64 host, lowest of seven passes, on
a 4096-byte page. The comparator derives `zerocopy` 0.8.66 on a header and an entry struct and
makes the same five checks by hand.
[The appendix](1158-block-roster-contract-release-review/what-was-checked.md#the-benchmark) has
the method and a second run.

| operation | 3 devices | 510 devices |
|---|---|---|
| `Roster::read` | 3.8 ns | 3.8 ns |
| `zerocopy`, the same checks | 3.8 ns | 3.7 ns |
| `Roster::read`, then sum every device | 6.2 ns | 189 ns |
| `zerocopy`, the same sum | 6.0 ns | 196 ns |
| `Roster::read`, then `count_by_transport` | 9.0 ns | 127 ns |
| `zerocopy`, the same count | 5.8 ns | 130 ns |
| `write` | 8.0 ns | 171 ns |

The interface costs nothing a caller can measure. The two runs differ by more than the two
sides do.

## One-way doors

- D1, the spelling of `virtio` in two constants (P0-1). Recommended: `VIRTUAL_IO`, as the rule
  says, with aliases for `virtio`, `virtio-mmio` and `virtio-pci`.
- D2, the type of a transport (P0-2). Recommended: the newtype `Transport`, the stricter choice.
  A `From<Transport> for u32` can follow, and a bare `u32` cannot tighten after 0.1.0.
- D3, the fields of `Device` (P0-3). The clearance ratified public fields, and `multiboot2`'s
  `MemoryArea` is the evidence against. Recommended: private fields with `new` and two getters.
  Opening them later breaks no caller.
- D4, what `write` returns (P0-4). Recommended: a `#[non_exhaustive]` enum with one variant for a
  page shorter than the header and one for too many devices, named by the errors decision.
- D5, the refusal for another version (P0-5). Recommended: its own variant before 0.1.0, since
  the page has no other place to say it.
- D6, the identity and the entry points (P0-6). Recommended: the contract-layout decision rules
  them. This crate's evidence favors a `[u8; 8]` magic.
- D7, `CapacityBeyondPage` and `CountBeyondCapacity` (P0-7). Recommended: ratify as built.
- D8, whether the crate names its system (P1-4). Recommended: the answer that door D8 of
  [the `address_space_layout` review](1153-address-space-layout-release-review.md) gets, ruled
  once for the contract crates.

## Evidence for the shared decisions

- Errors. Two types. `ReadError` is a `#[non_exhaustive]` enum of five unit variants, one for
  each cause, and `TooManyDevices` is a unit struct for two causes (P0-4). Both implement
  `Display` and `core::error::Error`, and neither carries a number. `multiboot2` derives
  `thiserror::Error` on enums with positional fields and no `#[non_exhaustive]`. `blockdev` has a
  `#[non_exhaustive]` enum with named fields and a `source`. `zerocopy`'s `SizeError` hands the
  input back through `into_src`. The evidence points to one enum for each operation, both traits,
  `#[non_exhaustive]`, and named fields where a number explains the refusal.
- DMA regions, doorbells and tails, register access, simulators: not applicable.
- Byte sinks and sources. `read` borrows `&[u8]` and copies nothing, and `write` fills a
  `&mut [u8]` the caller owns. `multiboot2` and `zerocopy` do the same. The evidence points to
  plain slices for a fixed layout.
- Feature names. The crate declares none. `blockdev` names its one feature `serde`, after the
  dependency. `multiboot2` names `alloc` and `builder` for what they turn on.
- Contract layout. The crate root holds five constants. `MAGIC: u64` is the bytes `blkrosv1`
  read little-endian. The page carries `VERSION: u32 = 1` only as the magic's last digit, and it
  does not carry `INTERFACE_ID: u64 = 5`. `HEADER_BYTES` and `ENTRY_BYTES` size the layout. The
  crate has no request builder, since nobody asks for the page. The encoder is the free function
  `write(page, devices) -> Result<(), TooManyDevices>`, and the helper is `entry_capacity`. The
  decoder is `Roster::read(page) -> Result<Roster, ReadError>`, with five refusals in a fixed
  order: `TooShort`, `NotARoster`, `CountBeyondPage`, `CapacityBeyondPage` and
  `CountBeyondCapacity`. It checks the header and no entry. `multiboot2` exports `MAGIC` as an
  integer the machine hands over in a register, puts `load` on the type and builds through a
  `Builder`. seL4's page has no magic and no version. The evidence points to a byte-array magic,
  the decoder as an associated function with `TryFrom`, the encoder beside it, and a rule for
  what a reader reports on a version it does not know (D5).

## Follow-on

- **Outstanding.** The sixteen findings, open on the crate's `main` at `f0c199a`, read on
  2026-11-26 (UTC).
- **Outstanding.** The doors D1 to D8 have no ruling. The block of milestone 1129, read on
  2026-11-26 (UTC), records no ruling on errors or contract layout, which D4 and D6 wait on.

## Done when

`script/review-status` counts the block BUILT: no P0 or P1 line above reads Open or Waiting, and
the architect has ruled D1 to D8.

## BUGS

- No ranked comparator has a wire form, so the layout comparison rests on two neighbors and two
  systems outside Rust.
- The review read one seL4 header and one Linux function, and took the NVMe list's layout from
  that function and not from the specification.
- The benchmark host ran other work, and its two runs differ by more than a factor of two on one row.
- The review counted no caller of an item it recommends changing; the effort across callers is an
  estimate.
- Kani, the fuzz targets and mutation testing were not run.

## Index row

The release review of `block_roster_contract` against `block-utils`, `rs-drivelist` and
`blockdev`, the neighbors `multiboot2` and `zerocopy`, seL4's boot information page and the NVMe
namespace list. Seven findings touch the 0.1.0 interface. They are two constants that spell `VIRTIO`, a transport
that is a bare `u32`, public `Device` fields, one unit error for two causes, no refusal for another
version, identity and entry-point spellings, and two names without a ruling. Four
land before the release, five may follow, and eight doors wait for the architect.
