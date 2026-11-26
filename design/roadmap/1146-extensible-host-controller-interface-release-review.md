---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1146. `extensible_host_controller_interface`: the release review's findings

The release review of `partsfoundry/extensible_host_controller_interface` at commit `a10790e1`,
made under milestone 1129 (the combine review), whose
[block](1129-crate-interfaces-best-in-class.md) sets its form. It compares the crate's public
interface with the xHCI crates a stranger would choose instead, and with the xHCI drivers of
Linux, U-Boot and OpenBSD, and lists what changes before the 0.1.0 interface. The baseline is
milestone 1060 (the outside review), [its block](1060-extensible-host-controller-interface-outside-review.md),
whose findings have all landed, and the cleared package
[`notes/crate-reviews/extensible-host-controller-interface.md`](../../notes/crate-reviews/extensible-host-controller-interface.md).
Neither is reopened here: the names 1060 ratified stand, and a finding below that touches one
proposes a type around it, not a new spelling.

Reuse: the prior-art table weighs each xHCI crate a caller could take instead.

## Finding status

The status words are those `script/review-status` reads.

- P0-1, `Event` is exhaustive and its completion codes are bare bytes: Open.
- P0-2, `Capabilities` is exhaustive: Open.
- P0-3, one driver's memory layout is public: Open.
- P0-4, two builders take the data direction as a `bool`: Open.
- P0-5, slots, ports, endpoints and speeds are all bare `u8`: Open.
- P0-6, `doorbell` is the one register offset with no bound: Open.
- P0-7, `TransferRequestBlock` exposes its dwords as a public field: Open.
- P0-8, refusals are spelled `bool`, `Option` and panics: Waiting on the errors decision of
  milestone 1129.
- P1-1, the documentation speaks of one driver and a kernel: Open.
- P1-2, the 64-bit addressing bit and the segment table bound are not decoded: Open.
- P1-3, no `Hash` and no `#[must_use]`: Open.
- P1-4, most entry points have no example: Open.
- P2-1, a TRB carries at most 65,535 bytes: Open.
- P2-2, the Host Controller Event decodes as `Other`: Open.
- P2-3, ring constructors with no fallible form: Open.
- P2-4, the doorbell's value has no builder: Waiting on the doorbells decision of milestone 1129.
- P2-5, no little-endian byte form of a TRB: Open.
- P2-6, the fake controller is an example, not an export: Waiting on the simulators decision of
  milestone 1129.
- P2-7, the manifest has no `documentation` key: Open.

## Open decisions

The one-way doors below, D1 to D10, each for the architect.

## Goal

A stranger writing an xHCI driver on a target without an operating system meets an interface that
names every value it hands back, that a future event type or capability bit cannot break, and
that carries no layout or wording from the one driver it was written beside.

## What the review read and ran

The sources read, the commands run and the 54 API Guidelines items are in
[the appendix](1146-extensible-host-controller-interface-release-review/what-was-checked.md) and
[the guidelines table](1146-extensible-host-controller-interface-release-review/api-guidelines.md).

## Prior art

Measured from the crates.io API on 2026-11-26 (UTC). The problem a stranger brings to this crate is
driving an xHCI controller with no operating system under it, so the ranked crates are the no_std
xHCI crates. The register crates are how such a driver reaches its registers, and the std USB
crates run above an operating system's own xHCI driver; both stand in the table as neighbors.

| crate or system | role | version read | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `xhci` | ranked 1 | 0.9.2 | 124,800 | 36,973 | 2 | 2023-07-19 |
| `crab-usb` | ranked 2: a whole host stack on `xhci` | 0.12.1 | 35,428 | 19,601 | 2 | 2026-09-11 |
| `usb-host` | ranked 3: host driver traits, no controller | 0.1.3 | 8,009 | 87 | 2 | 2022-10-12 |
| `tock-registers` | integration: typed register access | 0.12.0 | 2,363,430 | 619,429 | 75 | 2026-11-04 |
| `safe-mmio` | integration: typed register access | 0.4.0 | 647,707 | 214,105 | 13 | 2026-11-12 |
| `volatile-register` | integration: volatile cells | 0.2.2 | 13,020,405 | 2,221,996 | 28 | 2023-10-20 |
| `nusb` | neighbor: std, above the operating system's driver | 0.2.9 | 2,420,609 | 1,142,486 | 182 | 2026-10-24 |
| `rusb` | neighbor: std, libusb bindings | 0.9.4 | 10,538,976 | 2,063,423 | 170 | 2024-04-27 |
| Linux `drivers/usb/host/xhci*` | system | v6.17 | | | | |
| U-Boot `drivers/usb/host/xhci*` | system | v2025.10 | | | | |
| OpenBSD `sys/dev/usb/xhci.c` | system | `cd5896cffe` | | | | 2025-03-01 |

The demand appendix of milestone 1129 gave `xhci` 37,572 in 90 days; the API gives 36,973 today,
since the window moved. `xhci` passes 10,000 downloads in 90 days, which by 1129's rule is enough
on its own, and the review read the three systems as well, for the behavior no Rust comparator
shows (the port write trap, the 64-bit addressing bit, the events a driver ignores).

### What `extensible_host_controller_interface` does better

- Than `xhci`: it has no dependency and no `unsafe`, where `xhci` 0.9.2 takes five dependencies
  (`accessor`, `bit_field`, `num-derive`, `num-traits`, `paste`) and 30 lines with `unsafe`,
  among them `Registers::new`. It carries the ring discipline itself: `ProducerRing` places the
  link and flips the cycle, and `try_enqueue` refuses when the ring is full. `xhci` stops at the
  TRB and register layouts and leaves the ring to the caller. It proves 13 properties with Kani and
  ships a falsification patch for each.
- Than `crab-usb`: it runs anywhere a `u64` does. `crab-usb` 0.12.1 needs 18 dependencies,
  among them `anyhow`, `futures`, `crossbeam` and `dma-api`, and 234 lines with `unsafe`. Its ring
  (`src/backend/kmod/xhci/ring.rs`, `enque_trb`) advances with no full check, so a caller can
  overwrite a TRB the controller has not reached; this crate's `try_enqueue` refuses.
- Than both: `port::write_value` keeps the same bits Linux's `xhci_port_state_to_neutral` keeps
  (read from `xhci-hub.c` at v6.17: `XHCI_PORT_RO | XHCI_PORT_RWS`, 0x4e00ffe9), so a port write
  never acknowledges a change nobody asked to. `xhci` exposes each `PORTSC` bit and leaves the trap
  to the caller. The README states the barrier order on both sides of a ring, which neither crate
  does.
- Than the three systems: it is the arithmetic alone, testable on a host, where Linux, U-Boot
  and OpenBSD each fold it into a driver with its own memory and locking.

## The items

Effort is S (half a day), M (a day or two) or L (longer). A door is one-way when someone outside
the repository acts on it once 0.1.0 is out. A P0 finding is one-way, so it lands in the 0.1.0
interface or not at all; a P1 finding is two-way and lands before the release.

### P0: the 0.1.0 interface

#### P0-1. `Event` is exhaustive and its completion codes are bare bytes

Verified in source (`src/event.rs`, `src/completion.rs`).
`Event` has four variants and no `#[non_exhaustive]`, so the variant P2-2 wants (or any of the
other event types xHCI 1.2 section 6.4.2 defines) breaks every caller's `match` on the day it lands.
`Event::Transfer` and `Event::Command` carry `code: u8`, and `completion` is a module of 36 `u8`
constants and a `name` function, so a caller compares against integers and the compiler cannot
tell a completion code from a slot number. `xhci` 0.9.2 returns `Result<CompletionCode, u8>`
from `completion_code()`, with `CompletionCode` an enum.
Change: `#[non_exhaustive]` on `Event`. The code becomes a type: `CompletionCode(u8)` with the
existing names as associated constants, `name()` as a method, and `is_success()` for Success and
the vendor information codes 224 to 255, as `completion::name` documents them. The
constant names stand as ratified. Door: one-way (D1 for the attribute, D2 for the code's type).
Effort: S.

#### P0-2. `Capabilities` is exhaustive

Verified in source (`src/registers.rs`).
`Capabilities` has ten public fields and no `#[non_exhaustive]`, so a caller may build one with a
struct literal, and the field P1-2 adds breaks that caller. Reading the fields stays as it is.
Change: `#[non_exhaustive]` on `Capabilities` and on `SupportedProtocol`, which has the same
shape. Door: one-way (D3). Effort: S.

#### P0-3. One driver's memory layout is public

Verified in source (`src/direct_memory_access.rs`).
The module fixes the page of every structure for a single-slot boot-keyboard driver, and its own
head says nothing else in the crate reads it. 1060's P2-8 documented that; it is still a public
module, so its fifteen constants are 0.1.0 interface that a stranger's driver will never use and
that the crate can never change. Neither comparator ships a layout.
Change: the module moves into `examples/` (or to the driver that uses it). Door: one-way (D4).
Effort: S.

#### P0-4. Two builders take the data direction as a `bool`

Verified in source (`src/transfer_request_block.rs`).
`TransferRequestBlock::data(buffer, len, inbound: bool)` and `status(data_was_inbound: bool)`
take the direction as a flag (C-CUSTOM-TYPE), and the example calls them as `data(..., 18, true)`
and `status(true)`. `setup` beside them already takes `TransferType`, which 1060's P1-12 made an
enum for this reason. `xhci` 0.9.2 has a `Direction` enum.
Change: a `Direction` enum with `In` and `Out`, taken by both. The names follow design/naming.md
and are provisional until ratified. Door: one-way (D5). Effort: S.

#### P0-5. Slots, ports, endpoints and speeds are all bare `u8`

Verified in source (`src/transfer_request_block.rs`, `src/context.rs`, `src/registers.rs`,
`src/port.rs`).
`reset_endpoint(slot: u8, device_context_index: u8)` and `set_dequeue` take two `u8` side by side,
which a caller can swap with no error. `context::slot(speed: u8, port: u8, entries: u8)` takes
three. `port::speed_of` returns a `u8` that `default_control_packet`, `is_superspeed` and
`interrupt_interval` take, beside port and slot numbers of the same type (C-NEWTYPE). The values
have different ranges: a slot is 1 to 255, a device context index 1 to 31, a port 1 to
`maximum_ports`, a speed id 1 to 15. `xhci` 0.9.2 keeps them as `u8` too.
Change: `SlotId`, `DeviceContextIndex`, `PortNumber` and `PortSpeed` newtypes over `u8`, each with
`new` that refuses the reserved values and `get`. `PortSpeed` stays open (a newtype, not an
enum), since a Supported Protocol capability may define its own ids; the `port::speed` constants
become its associated constants. The names are provisional. Door: one-way (D6). Effort: M.

#### P0-6. `doorbell` is the one register offset with no bound

Verified in source (`src/registers.rs`).
`Capabilities::port_status_and_control` and `interrupter_register` return `None` past the
controller's count (1060's P1-11), and `doorbell(slot: u8)` returns a `u64` for any slot, though
the array holds `maximum_slots + 1` doorbells (xHCI 1.2 section 5.6). A caller who rings slot
`maximum_slots + 1` writes past the array.
Change: `doorbell` returns `Option<u64>`, `None` past `maximum_slots`. Door: one-way (D7).
Effort: S.

#### P0-7. `TransferRequestBlock` exposes its dwords as a public field

Verified in source (`src/transfer_request_block.rs`, `examples/fake_controller.rs`).
`pub struct TransferRequestBlock(pub [u32; 4])` lets any caller write any bits, so the cycle and
type the builders set can be changed behind them, and the example reads `t.0[3] & 1 << 5` for the
Interrupt On Completion bit. A field cannot be made private after 0.1.0 (C-STRUCT-PRIVATE).
`xhci` 0.9.2 keeps its TRB arrays private behind `into_raw` and `try_from`.
Change: the field becomes private, with `from_dwords([u32; 4])` and `dwords() -> [u32; 4]` for
the memory write and the read back, and `interrupt_on_completion()` for the bit the example reads.
Door: one-way (D8). Effort: S.

#### P0-8. Refusals are spelled `bool`, `Option` and panics

Verified in source (`src/ring.rs`, `src/registers.rs`).
The crate has no error type. `ProducerRing::complete` answers `false` for an address that is not
outstanding, and the caller cannot tell a stale event from a foreign one. `find_extended` answers
`None` for four different endings: the id is absent, the list ends, the walk leaves `limit`, and
64 hops pass; the last two mean a broken controller, which a driver reports and does not treat as
an absent capability. `ProducerRing::new` and `EventRing::new` panic on a size out of range.
`xhci` 0.9.2 returns the raw dwords as its error from every `try_from`.
Change: `find_extended` returns `Result<Option<u64>, ExtendedCapabilityWalkError>` (the error
for a broken list, `None` for an absent id), and `complete` a `Result` whose error says stale or
foreign, each error `#[non_exhaustive]` with `Display` and `core::error::Error`, in the shape the
shared errors decision picks. Door: one-way (D9). Effort: S.

### P1: before the first release

#### P1-1. The documentation speaks of one driver and a kernel

Verified in source.
`Event::Other` is "any other event type, which this driver does not act on"; `Capabilities::decode`
speaks of "a value this driver cannot use"; the crate page says "a kernel finds and confines the
register file" and that a user-space driver drives it; `src/tests.rs` repeats "this driver". The crate is not a driver, and a
stranger reads each as a reference to a program they do not have.
Change: describe each in terms of the caller. Door: two-way. Effort: S.

#### P1-2. The 64-bit addressing bit and the segment table bound are not decoded

Verified in source and in the systems' sources.
`Capabilities::decode` reads `HCCPARAMS1` for the context size and the extended list, and not bit
0 (`AC64`), which says whether the controller can reach memory above 4 GiB. Linux sets the DMA
mask from it (`HCC_64BIT_ADDR`, `xhci.c` at v6.17, line 5478), OpenBSD sets `BUS_DMA_64BIT` from
it (`XHCI_HCC_AC64`, `xhci.c` line 332), and `xhci` 0.9.2 has `addressing_capability`. A caller
who places rings above 4 GiB on a 32-bit controller gets silent truncation. `HCSPARAMS2`'s
`ERST Max` (bits 7:4), the bound on event ring segments, is not read either.
Change, after D3: `addresses_64_bit: bool` and `maximum_event_ring_segment_table_entries` fields,
and a sentence on `ProducerRing::new` and `EventRing::new` saying the base must be below 4 GiB
when the first is false. The names are provisional. Door: two-way once P0-2 lands. Effort: S.

#### P1-3. No `Hash` and no `#[must_use]`

Verified in source.
Every public type derives `Debug, Clone, Copy, PartialEq, Eq` and none derives `Hash`
(C-COMMON-TRAITS), so a caller cannot key a map by `Event` or `EndpointType`. Nothing is
`#[must_use]`: a caller who drops `try_enqueue`'s placement loses the TRB and, on the last entry
of a lap, the link the ring needs, and the compiler says nothing.
Change: `Hash` on every public type, and `#[must_use]` on `TransferRequestBlockPlacement`, the
TRB builders and `complete`. Door: two-way (a warning, not an error). Effort: S.

#### P1-4. Most entry points have no example

Verified in source (C-EXAMPLE).
Doc examples sit on the crate page and on `ProducerRing`, and nowhere else. `EventRing`,
`Event::decode`, `Capabilities::decode`, `find_extended`, `SupportedProtocol::decode`,
`PortDebounce` and the context builders have none, and those are where a stranger starts.
Change: a short example on each, built from the values the tests already use. Door: two-way.
Effort: S.

### P2: may follow

#### P2-1. A TRB carries at most 65,535 bytes

Verified in source and in the systems' sources.
`data`, `normal` and `fits_one_transfer_request_block` take `len: u16`. The TRB Transfer Length
field is 17 bits (`TRB_LEN` masks `0x1ffff` in Linux's `xhci.h` and OpenBSD's `xhcireg.h`), and
Linux and U-Boot fill a TRB with up to 64 KiB (`TRB_MAX_BUFF_SIZE`, 65,536). A 64 KiB aligned
buffer takes two TRBs here. The crate builds no bulk transfer, where this would cost; a boot
report is 8 bytes.
Change: none before 0.1.0. A bulk builder, when it comes, takes a `u32` length checked against
65,536. Door: one-way (D10). Effort: S.

#### P2-2. The Host Controller Event decodes as `Other`

Verified in source and in the systems' sources.
Type 37 carries the Event Ring Full Error, and `Event::decode` drops its code with every other
unknown type. Linux v6.17 (`xhci_handle_event_trb`, under a comment asking for more event types)
and OpenBSD (`XHCI_EVT_HOST_CTRL`, a `TODO`) ignore it too; `xhci` 0.9.2 decodes it.
Change, after D1: `Event::HostController { code }`. Door: two-way once P0-1 lands. Effort: S.

#### P2-3. Ring constructors with no fallible form

Verified in source.
`ProducerRing::new` and `EventRing::new` panic on a size out of range; every caller in the crate
passes a constant, but a size from configuration has no way to ask.
Change: `try_new` beside each, in the errors decision's shape. Door: two-way (an addition).
Effort: S.

#### P2-4. The doorbell's value has no builder

Verified in source.
`doorbell` gives the offset, and the caller composes the value (DB Target in bits 7:0, DB Stream
ID in bits 31:16) by hand; the example and the fake controller do not ring with a value at all.
Change: after the doorbells decision, a `doorbell_value(target, stream)` or the shape that
decision picks for every ring driver. Door: two-way (an addition). Effort: S.

#### P2-5. No little-endian byte form of a TRB

Verified in source.
`TransferRequestBlock` documents "four little-endian dwords" and holds host-order `u32`s, so a
caller on a big-endian target swaps each dword itself, and nothing says so.
Change: `to_le_bytes() -> [u8; 16]` and `from_le_bytes`, and a sentence on the type. Door:
two-way. Effort: S.

#### P2-6. The fake controller is an example, not an export

Verified in source.
`examples/fake_controller.rs` holds a consumer that follows links, flips its cycle and writes
transfer events; `src/tests.rs` holds a fuller one. A stranger testing a driver cannot depend on
either. Change: after the simulators decision, export one behind the feature name it picks.
Door: two-way (an addition). Effort: M.

#### P2-7. The manifest has no `documentation` key

Verified in `Cargo.toml` (C-METADATA).
Change: `documentation = "https://docs.rs/extensible_host_controller_interface"`. Door: two-way.
Effort: S.

### Measured performance

Run on this Linux host (Intel Xeon Platinum 8160, rustc 1.100.0, release profile), 10,000,000
iterations, best of seven, against `xhci` 0.9.2 from its `.crate`. The bench crate is in the
review's scratch space and is not committed.

| operation | this crate | `xhci` 0.9.2 |
|---|---|---|
| decode one event TRB and read its pointer and code | 1.57 ns | 9.31 ns (`event::Allowed::try_from` and `completion_code`) |
| build one Normal TRB | 0.60 ns | 7.53 ns (`Normal::new` and four setters) |
| `try_enqueue` and `complete`, 256-entry ring | 24.94 ns | no ring to compare |

The ring pair spends its time in three `%` divisions by a runtime size. One uncached doorbell
write costs more than that, so the review proposes no change.

## One-way doors

Each for the architect, one at a time.

- D1, `Event` exhaustive (P0-1). Recommended: `#[non_exhaustive]` before 0.1.0, the stricter
  choice; dropping the attribute later breaks no caller.
- D2, the completion code's type (P0-1). Recommended: the newtype `CompletionCode(u8)` with the
  ratified names as associated constants. An enum needs an escape variant for the vendor ranges
  anyway, and the newtype keeps every byte the controller writes.
- D3, `Capabilities` and `SupportedProtocol` exhaustive (P0-2). Recommended: `#[non_exhaustive]`
  on both.
- D4, the `direct_memory_access` module (P0-3). Recommended: out of the public interface; a
  module can be added back, never taken away.
- D5, the data direction (P0-4). Recommended: the enum, as `TransferType` already is.
- D6, newtypes for slot, device context index, port and speed (P0-5). Recommended: all four,
  with `PortSpeed` open. A newtype can gain conversions later; a bare `u8` cannot gain a range.
- D7, the doorbell bound (P0-6). Recommended: `Option<u64>`, matching its two siblings.
- D8, the TRB's field (P0-7). Recommended: private, with the three accessors.
- D9, the refusals (P0-8). Recommended: the two error types, in the shape the errors decision of
  milestone 1129 picks for every crate.
- D10, the TRB length (P2-1). Recommended: keep `u16` for the builders that exist. A wider type
  serves only the bulk transfers the crate does not build, and the builder that does can take its
  own.

## Evidence for the shared decisions

What this crate shows each shared question of milestone 1129.

- Errors: none. Refusals are `bool` (`complete`), `Option` (`find_extended`,
  `port_status_and_control`, `interrupter_register`, `default_control_packet`) and panics (the
  two ring constructors), and the codes the controller hands back are `u8` constants. P0-8 and
  D9 wait on the decision; P0-1's code type is this crate's own.
- Byte sinks and sources: not applicable. The crate moves no byte stream.
- Feature names: none declared, and none needed until P2-6.
- Simulators: two fakes, neither exported. `examples/fake_controller.rs` consumes a transfer ring
  and writes events; `src/tests.rs` holds a fuller consumer that the host tests use. P2-6 waits on
  the decision.
- Register access: no trait. The crate returns byte offsets as `u64` from `Capabilities` and
  takes register values as `u32` arguments; the caller does every volatile access. The one
  callback is `find_extended`'s `read: &mut dyn FnMut(u64) -> u32`. `xhci` 0.9.2 instead takes a
  `Mapper` and reads through `accessor`, with an `unsafe fn new`. This is the shape a pure
  arithmetic crate can keep under any shared trait: a trait would sit in the driver above it.
- Memory regions and DMA regions: no trait. Physical addresses are bare `u64` (ring bases, TRB
  pointers, context pointers), and the one region layout is P0-3's module, which belongs to one
  driver. The crate needs the `AC64` bit of P1-2 from any region decision: the region must say
  whether it lies below 4 GiB.
- Doorbells and tails: `Capabilities::doorbell(slot)` computes the offset, with no bound (P0-6)
  and no value builder (P2-4). The ring index is `ProducerRing`'s own. Of the two ring drivers
  with `Tails` traits, neither shape fits a crate that touches no register; a doorbell decision
  that names an offset function and a value builder covers this crate and
  `non_volatile_memory_express` alike.

## Follow-on

- **Outstanding.** D9 is evidence for the errors decision, P2-4 for the doorbells decision and
  P2-6 for the simulators decision of milestone 1129.
- **Outstanding.** The hardware checks 1060 lists are still unrun on silicon; this review adds
  none.

## Done when

Every P0 and P1 finding reads Done, or Will not fix with its ruling, the architect has ruled D1
to D10, and `script/review-status` shows the block BUILT.

## BUGS

- The review ran `xhci` 0.9.2 in the benchmark only, read `crab-usb` 0.12.1 without building it,
  and read the three systems' sources without running them.
- The benchmark measures the arithmetic in a loop with warm caches; a driver's cost is its
  register and memory traffic, which no host run measures.

## Index row

The release review of `extensible_host_controller_interface` against `xhci`, `crab-usb` and the
Linux, U-Boot and OpenBSD drivers: eight one-way interface changes before 0.1.0, four two-way
fixes before the release, seven after it, ten doors to rule.
