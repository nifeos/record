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
under milestone 1129 (the combine review), whose [block](1129-crate-interfaces-best-in-class.md)
sets its form. It compares the public interface with the xHCI crates a stranger would choose
instead, and with the Linux, U-Boot and OpenBSD drivers. The baseline is milestone 1060 (the
outside review), [its block](1060-extensible-host-controller-interface-outside-review.md), whose
findings have all landed, and the cleared package
[`notes/crate-reviews/extensible-host-controller-interface.md`](../../notes/crate-reviews/extensible-host-controller-interface.md).
This review reopens neither: the names 1060 ratified stand, and a finding that touches one
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
- P0-8, the crate refuses with `bool`, `Option` and panics: Waiting on the errors decision of
  milestone 1129.
- P1-1, the documentation speaks of one driver and a kernel: Open.
- P1-2, `Capabilities` reads neither the 64-bit addressing bit nor the segment table bound: Open.
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

A stranger driving an xHCI controller with no operating system meets an interface that names
every value it returns. No future event type or capability bit breaks it, and it carries nothing
of the one driver it grew beside.

## What the review read and ran

[The appendix](1146-extensible-host-controller-interface-release-review/what-was-checked.md) lists
every source and command, and [the guidelines table](1146-extensible-host-controller-interface-release-review/api-guidelines.md)
marks all 54 items.

## Prior art

From the crates.io API on 2026-11-26 (UTC). A stranger brings the problem of driving an xHCI
controller with no operating system under it, so the ranked crates are the no_std xHCI crates.
The register crates are how such a driver reaches its registers, and the std crates run above an
operating system's own driver; both stand in the table as neighbors.

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

The demand appendix of milestone 1129 gave `xhci` 37,572 in 90 days, read earlier the same day.
One crate over 10,000 is enough by 1129's rule. The review read the three systems as well, for
what no Rust crate shows: the port write trap, the 64-bit addressing bit, and the events a driver
ignores.

### What `extensible_host_controller_interface` does better

- Than `xhci`: no dependency and no `unsafe`, where `xhci` 0.9.2 takes five dependencies and has
  30 lines with `unsafe`, among them `Registers::new`. `ProducerRing` places the link, flips the
  cycle and refuses when full; `xhci` stops at the layouts and leaves the ring to the caller.
  Kani proves 13 properties, each with a falsification patch.
- Than `crab-usb`: it runs anywhere a `u64` does, where `crab-usb` 0.12.1 needs 18 dependencies
  and has 234 lines with `unsafe`. Its transfer ring (`src/backend/kmod/xhci/ring.rs`) advances
  with no full check, so a caller can overwrite a TRB the controller has not reached.
- Than both: `port::write_value` keeps the bits Linux's `xhci_port_state_to_neutral` keeps
  (`XHCI_PORT_RO | XHCI_PORT_RWS`, 0x4e00ffe9, in `xhci-hub.c`), so a port write never
  acknowledges a change by accident. The README states the barrier order on both sides of a ring.
- Than the three systems: it is the arithmetic alone, testable on a host, where each system folds
  it into a driver with its own memory and locking.

## The items

Effort is S (half a day), M (a day or two) or L (longer). One-way means a caller outside the
repository acts on it after 0.1.0. Each P0 is one-way and lands in 0.1.0 or never. Each P1 is
two-way and lands before the release; a P2 may follow it.

### P0: the 0.1.0 interface

#### P0-1. `Event` is exhaustive and its completion codes are bare bytes

Verified in source (`src/event.rs`, `src/completion.rs`).
`Event` has four variants and no `#[non_exhaustive]`, so the variant P2-2 wants breaks every
caller's `match`. `Transfer` and `Command` carry `code: u8`, and `completion` is 36 `u8` constants
and a `name` function, so the compiler cannot tell a completion code from a slot number. `xhci`
returns `Result<CompletionCode, u8>`, with `CompletionCode` an enum.
Change: `#[non_exhaustive]` on `Event`; the code becomes `CompletionCode(u8)`, with the ratified
names as associated constants and `name()` as a method. Door: one-way (D1 and D2). Effort: S.

#### P0-2. `Capabilities` is exhaustive

Verified in source (`src/registers.rs`).
`Capabilities` and `SupportedProtocol` have public fields and no `#[non_exhaustive]`, so a caller
may build one with a struct literal, and the fields P1-2 adds break that caller.
Change: `#[non_exhaustive]` on both. Door: one-way (D3). Effort: S.

#### P0-3. One driver's memory layout is public

Verified in source (`src/direct_memory_access.rs`).
The module fixes a page for each structure of a single-slot boot-keyboard driver, and its head
says nothing else in the crate reads it. Its fifteen constants would be 0.1.0 interface that no
other driver uses and the crate can never change. Neither comparator ships a layout.
Change: move the module into `examples/`. Door: one-way (D4). Effort: S.

#### P0-4. Two builders take the data direction as a `bool`

Verified in source (`src/transfer_request_block.rs`).
`data(buffer, len, inbound: bool)` and `status(data_was_inbound: bool)` take a flag
(C-CUSTOM-TYPE), so the example reads `data(..., 18, true)` and `status(true)`. Beside them,
`setup` takes `TransferType`, an enum since 1060's P1-12. `xhci` has a `Direction` enum.
Change: a `Direction` enum with `In` and `Out`, names provisional. Door: one-way (D5). Effort: S.

#### P0-5. Slots, ports, endpoints and speeds are all bare `u8`

Verified in source (`src/transfer_request_block.rs`, `src/context.rs`, `src/port.rs`).
`reset_endpoint(slot: u8, device_context_index: u8)` and `set_dequeue` take two `u8` side by side,
which a caller can swap unnoticed; `context::slot(speed, port, entries)` takes three. The ranges
differ: a slot is 1 to 255, a device context index 1 to 31, a port 1 to `maximum_ports`, a speed
id 1 to 15 (C-NEWTYPE). `xhci` keeps them as `u8` too.
Change: `SlotId`, `DeviceContextIndex`, `PortNumber` and `PortSpeed` newtypes over `u8`, each with
a `new` that refuses reserved values and a `get`. `PortSpeed` stays open, since a Supported
Protocol capability may define its own ids; the `port::speed` constants become its associated
constants. Names provisional. Door: one-way (D6). Effort: M.

#### P0-6. `doorbell` is the one register offset with no bound

Verified in source (`src/registers.rs`).
`port_status_and_control` and `interrupter_register` return `None` past the controller's count
(1060's P1-11). `doorbell(slot: u8)` returns an offset for any slot, though the array holds
`maximum_slots + 1` doorbells (xHCI 1.2 section 5.6), so a caller can write past it.
Change: `doorbell` returns `Option<u64>`. Door: one-way (D7). Effort: S.

#### P0-7. `TransferRequestBlock` exposes its dwords as a public field

Verified in source (`src/transfer_request_block.rs`, `examples/fake_controller.rs`).
`pub struct TransferRequestBlock(pub [u32; 4])` lets a caller rewrite the cycle and type behind
the builders, and the example reads `t.0[3] & 1 << 5` for Interrupt On Completion. No release
after 0.1.0 can take a public field back (C-STRUCT-PRIVATE). `xhci` keeps its arrays private
behind `into_raw` and `try_from`.
Change: a private field, with `from_dwords`, `dwords` and `interrupt_on_completion`. Door: one-way
(D8). Effort: S.

#### P0-8. The crate refuses with `bool`, `Option` and panics

Verified in source (`src/ring.rs`, `src/registers.rs`).
There is no error type. `ProducerRing::complete` answers `false` for an address it does not hold,
whether stale or foreign. `find_extended` answers `None` for four endings: the id is absent, the
list ends, the walk leaves `limit`, or 64 hops pass. The last two mean a broken controller, which
a driver reports rather than reading as an absent capability. The two ring constructors panic on
a size out of range. `xhci` returns the raw dwords as the error of every `try_from`.
Change: `find_extended` returns `Result<Option<u64>, _>` and `complete` a `Result` that says stale
or foreign, each error `#[non_exhaustive]` with `Display` and `core::error::Error`, in the shape
the shared errors decision picks. Door: one-way (D9). Effort: S.

### P1: before the first release

#### P1-1. The documentation speaks of one driver and a kernel

Verified in source.
`Event::Other` is an event type "which this driver does not act on", `Capabilities::decode`
refuses "a value this driver cannot use", and the crate page says a kernel confines the register
file and a user-space driver drives it. The crate is not a driver, and a stranger has neither.
Change: describe each in terms of the caller. Door: two-way. Effort: S.

#### P1-2. `Capabilities` reads neither the 64-bit addressing bit nor the segment table bound

Verified in source and in the systems' sources.
`decode` reads the context size from `HCCPARAMS1` but not bit 0 (`AC64`), which says whether the
controller reaches memory above 4 GiB. Linux sets its DMA mask from it (`HCC_64BIT_ADDR` in
`xhci.c`), OpenBSD sets `BUS_DMA_64BIT` from `XHCI_HCC_AC64`, and `xhci` has
`addressing_capability`. A ring above 4 GiB on a 32-bit controller truncates silently.
`HCSPARAMS2`'s `ERST Max`, the bound on event ring segments, goes unread too.
Change, after D3: two fields for them, names provisional, and a sentence on both ring
constructors. Door: two-way once P0-2 lands. Effort: S.

#### P1-3. No `Hash` and no `#[must_use]`

Verified in source.
Every public type derives `Debug, Clone, Copy, PartialEq, Eq` and none `Hash` (C-COMMON-TRAITS).
Nothing is `#[must_use]`, so a caller who drops `try_enqueue`'s placement loses the TRB, and on
the last entry of a lap the link, with no warning.
Change: `Hash` on every public type; `#[must_use]` on the placement, the builders and `complete`.
Door: two-way. Effort: S.

#### P1-4. Most entry points have no example

Verified in source (C-EXAMPLE).
Only the crate page and `ProducerRing` carry examples. `EventRing`, `Event::decode`,
`Capabilities::decode`, `find_extended`, `PortDebounce` and the context builders have none, and
a stranger starts there. Change: a short example on each. Door: two-way. Effort: S.

### P2: may follow

#### P2-1. A TRB carries at most 65,535 bytes

Verified in source and in the systems' sources.
`data`, `normal` and `fits_one_transfer_request_block` take `len: u16`. The Transfer Length field
is 17 bits (`TRB_LEN`, 0x1ffff, in Linux's `xhci.h` and OpenBSD's `xhcireg.h`), and Linux and
U-Boot fill a TRB with up to 65,536 bytes (`TRB_MAX_BUFF_SIZE`). The crate builds no bulk
transfer, where this would cost; a boot report is 8 bytes.
Change: none before 0.1.0; a later bulk builder takes a `u32`. Door: one-way (D10). Effort: S.

#### P2-2. The Host Controller Event decodes as `Other`

Verified in source and in the systems' sources.
Type 37 carries Event Ring Full, and `Event::decode` drops its code. Linux
(`xhci_handle_event_trb`) and OpenBSD (`XHCI_EVT_HOST_CTRL`, a `TODO`) ignore it too; `xhci`
decodes it. Change, after D1: `Event::HostController { code }`. Door: two-way. Effort: S.

#### P2-3. Ring constructors with no fallible form

Verified in source.
A ring size from configuration has no way to ask. Change: `try_new` beside each `new`. Door:
two-way. Effort: S.

#### P2-4. The doorbell's value has no builder

Verified in source.
The caller composes the target and stream id by hand. Change: what the doorbells decision picks.
Door: two-way. Effort: S.

#### P2-5. No little-endian byte form of a TRB

Verified in source.
The type documents "four little-endian dwords" but holds host-order `u32`, so a big-endian caller
swaps each dword unaided. Change: `to_le_bytes` and `from_le_bytes`. Door: two-way. Effort: S.

#### P2-6. The fake controller is an example, not an export

Verified in source.
`examples/fake_controller.rs` and `src/tests.rs` each hold a consumer that follows links, flips
its cycle and writes events; a stranger's tests can use neither. Change: export one under the
simulators decision's feature name. Door: two-way. Effort: M.

#### P2-7. The manifest has no `documentation` key

Verified in `Cargo.toml` (C-METADATA). Change: add it. Door: two-way. Effort: S.

### Measured performance

On this Linux host (Intel Xeon Platinum 8160, rustc 1.100.0, release profile), 10,000,000
iterations, best of seven, against `xhci` 0.9.2. The bench crate stays in scratch space.

| operation | this crate | `xhci` 0.9.2 |
|---|---|---|
| decode one event TRB, read its pointer and code | 1.57 ns | 9.31 ns (`event::Allowed::try_from`, `completion_code`) |
| build one Normal TRB | 0.60 ns | 7.53 ns (`Normal::new` and four setters) |
| `try_enqueue` and `complete`, 256-entry ring | 24.94 ns | no ring to compare |

The ring pair spends its time in three `%` divisions by a runtime size, less than one uncached
doorbell write, so the review proposes no change.

## One-way doors

Each for the architect, one at a time.

- D1, `Event` exhaustive (P0-1). Recommended: `#[non_exhaustive]`, the stricter choice; a later
  release can drop it without breaking a caller.
- D2, the completion code's type (P0-1). Recommended: the newtype `CompletionCode(u8)`. An enum
  needs an escape variant for the vendor ranges anyway, and the newtype keeps every byte.
- D3, `Capabilities` and `SupportedProtocol` exhaustive (P0-2). Recommended: `#[non_exhaustive]`.
- D4, `direct_memory_access` (P0-3). Recommended: out of the interface; a later release can add a
  module back, never remove one.
- D5, the data direction (P0-4). Recommended: the enum, as `TransferType` already is.
- D6, newtypes for slot, device context index, port and speed (P0-5). Recommended: all four,
  `PortSpeed` open. A newtype can gain conversions later; a bare `u8` cannot gain a range.
- D7, the doorbell bound (P0-6). Recommended: `Option<u64>`, matching its siblings.
- D8, the TRB's field (P0-7). Recommended: private, with the three accessors.
- D9, the refusals (P0-8). Recommended: the two error types, in the errors decision's shape.
- D10, the TRB length (P2-1). Recommended: keep `u16` on the builders that exist; a bulk builder
  takes its own wider length.

## Evidence for the shared decisions

What this crate shows each shared question of milestone 1129.

- Errors: none. It refuses with `bool` (`complete`), `Option` (`find_extended` and three offset
  functions) and panics (the ring constructors), and hands controller codes back as `u8`.
- Byte sinks and sources: not applicable; the crate moves no byte stream.
- Feature names: none declared, and none needed until P2-6.
- Simulators: two fakes, neither exported (P2-6).
- Register access: no trait. `Capabilities` returns byte offsets as `u64` and takes register values
  as `u32`; the caller does every volatile access. The one callback is `find_extended`'s
  `&mut dyn FnMut(u64) -> u32`. `xhci` reads through an `accessor` `Mapper` behind an `unsafe fn
  new`, and `crab-usb` through `tock-registers`. A pure arithmetic crate keeps this shape under any
  shared trait, which belongs in the driver above it.
- Memory regions and DMA regions: no trait. Physical addresses are bare `u64`, and the one layout
  is P0-3's. Any region decision must let a region say whether it lies below 4 GiB, for P1-2.
- Doorbells and tails: `doorbell(slot)` computes the offset, with no bound (P0-6) and no value
  builder (P2-4); `ProducerRing` keeps the ring index. A decision that names an offset function and
  a value builder fits this crate, which touches no register.

## Follow-on

- **Outstanding.** D9, P2-4 and P2-6 wait on the errors, doorbells and simulators decisions of
  milestone 1129.
- **Outstanding.** The hardware checks 1060 lists remain unrun on silicon.

## Done when

Every P0 and P1 reads Done, or Will not fix with its ruling; D1 to D10 have rulings; and
`script/review-status` shows the block BUILT.

## BUGS

- The review ran `xhci` 0.9.2 in the benchmark only, read `crab-usb` 0.12.1 without building it,
  and read the three systems without running them.
- The benchmark loops with warm caches; a driver's cost is register and memory traffic, which no
  host run measures.

## Index row

The release review of `extensible_host_controller_interface` against `xhci`, `crab-usb` and the
Linux, U-Boot and OpenBSD drivers: eight one-way changes before 0.1.0 and ten doors to rule.
