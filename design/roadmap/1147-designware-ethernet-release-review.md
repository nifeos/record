---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1074, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1147. `designware_ethernet`: the release review's findings

The release review of `partsfoundry/designware_ethernet` at commit `565b331f`, under
milestone 1129 (the combine review), whose [block](1129-crate-interfaces-best-in-class.md) sets its form. It
compares the public interface with the Rust drivers for the same Synopsys controller and with three
drivers outside Rust. The baseline is milestone 1074 (what an outside maintainer would fix),
[its block](1074-designware-ethernet-outside-review.md), whose items have all landed but the board
run, and the cleared package
[`notes/crate-reviews/designware-ethernet.md`](../../notes/crate-reviews/designware-ethernet.md).
This review reopens neither, and no name the package ratified falls under a later naming rule.

Reuse: the prior-art table weighs each DesignWare driver a caller could take instead; the evidence
section feeds milestone 1129's shared decisions.

## Finding status

The status words are those `script/review-status` reads.

- P0-1, six public structs with public fields and no `#[non_exhaustive]`: Open.
- P0-2, the bring-up serves one physical layer device: Open.
- P0-3, four error types with no `Display` and no `core::error::Error`: Waiting on the errors
  decision of milestone 1129.
- P0-4, the bring-up answers a bare tuple and takes an unchecked station address: Open.
- P0-5, the packed settings word is a public format: Open.
- P0-6, safe functions take the physical address the device uses: Open.
- P0-7, an inconclusive coherence probe passes the bring-up: Open.
- P1-1, the README says the crate has run on a board, and the crate page says it has not: Open.
- P1-2, a short receive buffer loses a good frame as a dropped one: Open.
- P1-3, one failure section, few examples, four links to private items, and a README that is not
  the crate page: Open.
- P1-4, the probe deadline subtracts two clock readings unchecked: Open.
- P2-1, the manifest has no `documentation` key and no `include` list: Open.
- P2-2, `smoltcp` and `embassy-net-driver` adapters and a borrowed frame: Waiting on the
  feature-names decision of milestone 1129.
- P2-3, ring sizes the caller chooses: Open.
- P2-4, the driver always programs one MDIO clock range: Open.
- P2-5, the simulator ships to callers: Waiting on the simulators decision of milestone 1129.

## Open decisions

The one-way doors below, D1 to D7, each for the architect.

## Goal

A stranger driving a DesignWare Ethernet QoS controller with no operating system meets an
interface that can grow without a break and takes the board's physical layer device. Its errors say
why, and it plugs into the network stacks Rust already uses.

## What the review read and ran

Every source and command is in [the appendix](1147-designware-ethernet-release-review/what-was-checked.md),
and [the guidelines table](1147-designware-ethernet-release-review/api-guidelines.md) marks all 54 items.

## Prior art

From the crates.io API on 2026-11-26 (UTC). A stranger brings the problem of driving a Synopsys
DesignWare Ethernet MAC (Linux's `stmmac`) with no operating system, so the ranked crates are the
standalone drivers for that family. The integrations are the network stacks' device traits, the
MDIO traits and the register-access crates.

| crate | role | version read | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `stm32-eth` | ranked 1: the 3.x MAC of STM32 parts | 0.8.2 | 46,932 | 21,781 | 0 | 2026-02-16 |
| `esp-emac` | ranked 2: the ESP32 MAC, a Synopsys GMAC | 0.5.0 | 243 | 135 | 0 | 2026-06-09 |
| `dwmac-my` | ranked 3: the same 5.20 controller and the same board | 0.2.0 | 37 | 8 | 0 | 2026-02-12 |
| `embassy-stm32` | neighbor: a whole HAL whose `eth::v2` drives the same 4.x descriptors | 0.6.0 | 864,941 | 201,745 | 47 | 2026-03-20 |
| `esp-p4-eth` | neighbor: the ESP32-P4 MAC, async only | 0.1.0 | 43 | 17 | 0 | 2026-05-02 |
| `smoltcp` | integration: `phy::Device` | 0.14.0 | 11,087,347 | 3,453,932 | 133 | 2026-08-17 |
| `embassy-net-driver` | integration: `Driver` | 0.2.0 | 2,673,211 | 977,529 | 18 | 2023-10-18 |
| `embassy-net-driver-channel` | integration: a channel-backed `Driver` | 0.4.0 | 1,506,480 | 356,756 | 19 | 2026-03-20 |
| `ieee802_3_miim` | integration: an MDIO trait and physical layer devices | 0.10.0 | 79,117 | 30,208 | 2 | 2026-08-25 |
| `mdio` | integration: an MDIO trait | 0.1.2 | 31,842 | 1,581 | 2 | 2022-10-01 |
| `tock-registers` | integration: register access | 0.12.0 | 2,363,430 | 619,429 | 75 | 2026-11-04 |
| `safe-mmio` | integration: register access | 0.4.0 | 647,707 | 214,105 | 13 | 2026-11-12 |
| `embedded-hal` | integration: `delay::DelayNs` | 1.0.0 | 41,112,022 | 10,120,693 | 1852 | 2024-01-09 |

`stm32-eth` passes 10,000 downloads in 90 days, but drives the older 3.x descriptors, so the
review also read Linux `stmmac` at v6.12, U-Boot `dwc_eth_qos.c` at v2025.10, and OpenBSD `dwqe.c`
at `59ec3ab4d107`.

### What `designware_ethernet` does better

- Than `stm32-eth`: no `unsafe` and no volatile access. Every register and DMA access goes through
  a trait the caller implements, so the whole driver runs against a host simulator, and six Kani
  harnesses prove its descriptor and offset bounds. `stm32-eth` has 74 uses of `unsafe` and builds
  only with one chip feature selected.
- Than `embassy-stm32`'s `eth::v2`, on the same descriptor format: `receive_verdict` checks the
  length against the buffer, the caller's room and the 1514-byte frame bound before any copy (a
  Kani proof), and one `receive` call consumes at most one ring of descriptors.
- Than `dwmac-my`, on the same board and controller: no allocator, and MDIO errors that name the address, where `dwmac-my` returns
  `&'static str`.
- Than every Rust comparator: the cache-coherence probe measures whether each side sees the other's
  writes, and the bring-up refuses on a measured incoherence; no Rust crate asks.
- Than `ieee802_3_miim`: `ManagementDataIo::read` returns `Result<u16, Error>`, so a caller learns
  of a stuck bus; `Miim::read_raw` returns a bare `u16`.

## The items

Effort is S (half a day), M (a day or two) or L (longer). A one-way door is one that strangers
build on from 0.1.0 onward; every P0 is such a door. P1 findings are two-way and come before the
release.

### P0: the 0.1.0 interface

#### P0-1. Six public structs with public fields and no `#[non_exhaustive]`

Verified in source.
`bring_up::Inputs`, `link::Link`, `network_interface_controller::BusConfiguration`,
`motorcomm_physical_layer_device::Settings` and `management_data_io::Bus` (a public tuple field)
take a struct literal, and a caller may write `DataPlane`'s `pub dropped: u32`. A later field (an
MDIO clock range, a coherence policy, a second queue) breaks every caller that names one. `Identity`, `Account`, `Observation` and `Applied` are already
`#[non_exhaustive]`. `esp-emac` 0.5.0 builds `EmacConfig` with methods, and `stm32-eth` 0.8.2 keeps
its ring state private.
Change: `#[non_exhaustive]` on the five, each with a `const fn new` or a `Default` and setters, and
`dropped` behind a getter. Door: one-way (D1). Effort: S.

#### P0-2. The bring-up serves one physical layer device

Verified in source (`src/bring_up.rs`).
`Inputs::physical_layer_device` is a Motorcomm `Settings`, and `bring_up` refuses any device whose
identifier is not the `YT8531`'s (`Error::UnknownPhysicalLayerDevice`). A stranger whose board
carries a Realtek or Microchip device rewrites the bring-up. Linux (`phylink`), U-Boot (`phy_connect`) and OpenBSD (`mii(4)`) all
attach the physical layer device apart from the MAC, and `stm32-eth` implements
`ieee802_3_miim::Miim` and leaves the device to the caller.
Change: name the bring-up after the `YT8531`, and defer a physical layer device trait, since a
published trait is itself a one-way commitment. Once D1 makes `Inputs` non-exhaustive, a generic
bring-up can come later as an addition. Names provisional. Door: one-way (D2). Effort: S.

#### P0-3. Four error types with no `Display` and no `core::error::Error`

Verified in source.
`bring_up::Error`, `network_interface_controller::Error`, `management_data_io::Error` and
`TransmitError` are `#[non_exhaustive]` and none implements `Display` or `core::error::Error`;
`bring_up::Error` wraps two others without a `source`. `stm32-eth`'s and `esp-emac`'s errors have no
`Display` either.
Change: `Display` and `core::error::Error` on all four, with `source` returning the wrapped error,
in the shape the shared errors decision picks. Door: one-way (D3). Effort: S.

#### P0-4. The bring-up answers a bare tuple and takes an unchecked station address

Verified in source (`src/bring_up.rs`, `src/network_interface_controller.rs`).
`bring_up` returns `Result<([u8; 6], Option<Link>), Error>`, so a caller reads `.0` and `.1`.
Station addresses are bare `[u8; 6]`. `station_mac_address(high, low)` refuses an all-zero,
all-ones or multicast address from the registers, but the bring-up programs the one in
`Inputs::station_mac_address` unchecked. `smoltcp` 0.14.0 has
`EthernetAddress` with `is_unicast`, and `embassy-net-driver` 0.2.0 has `HardwareAddress`.
Change: a named result struct, and a station address newtype whose constructor refuses what
`station_mac_address` refuses, with `From` into `[u8; 6]` and `smoltcp`'s type behind P2-2's
feature. `Account` stays an out-parameter, since it records how far a failed bring-up got. Names
provisional. Door: one-way (D4). Effort: S.

#### P0-5. The packed settings word is a public format

Verified in source (`src/motorcomm_physical_layer_device.rs`).
`Settings::to_word` and `Settings::from_word` pack the delays, inversions, source and drive
strengths into a `u64` "for a process that hands them to another", with a documented layout and
no version field. A caller that stores or sends the word fixes that layout. No comparator
publishes one.
Change: make both crate-private for 0.1.0, or, if a caller needs them, add a version field in the
top bits before 0.1.0 and freeze the layout. Door: one-way (D5). Effort: S.

#### P0-6. Safe functions take the physical address the device uses

Verified in source (`src/data_plane.rs`, `src/bring_up.rs`, `src/network_interface_controller.rs`).
`DataPlane::new(u64)`, `network_interface_controller::configure` (its `region_physical_address`)
and the public field `Inputs::region_physical_address` are all safe. That number becomes the
buffer addresses in the descriptors: `start`, `receive` and `transmit` add a buffer offset to it.
Safe code can thus aim the device's memory access anywhere, which leaves the interface's
soundness open.
Change: either the constructors that take an address become `unsafe fn` with a `# Safety`
section, or the region becomes an `unsafe trait` that supplies its own physical address. Door:
one-way (D6). Effort: M.

#### P0-7. An inconclusive coherence probe passes the bring-up

Verified in source (`src/bring_up.rs`, `bring_up`).
`bring_up` refuses every verdict but `Verdict::Coherent` and `Verdict::Inconclusive`. An
inconclusive probe means the loopback frame never completed and the probe measured nothing, yet
the bring-up runs the rings as if the platform were coherent. U-Boot never assumes: each platform
names its cache operations. Change: refuse on `Inconclusive` by default, with the account holding
the observation, and, once P0-1 lands, a field of `Inputs` that accepts it. Door: one-way (D7), since refusing after
0.1.0 breaks boards that pass today. Effort: S.

### P1: before the first release

#### P1-1. The README says the crate has run on a board, and the crate page says it has not

Verified in source.
The README claims a run on a StarFive VisionFive 2; the crate page's BUGS says no test has touched
the device. Change: the README says what the crate page says until the board run lands.
Door: two-way. Effort: S.

#### P1-2. A short receive buffer loses a good frame as a dropped one

Verified in source (`src/descriptor.rs`, `src/data_plane.rs`).
`receive_verdict` drops a frame longer than `out.len()`, and `receive` reposts its slot and counts
it in `dropped` with the malformed frames. The caller cannot tell a short buffer from a bad frame.
`stm32-eth` lends the packet in place instead.
Change: document that `out` must hold `MAXIMUM_FRAME_BYTES`, and count short-buffer drops apart
from malformed ones. Door: two-way. Effort: S.

#### P1-3. One failure section, few examples, four links to private items, and a README that is not the crate page

Verified by `cargo doc` and in source.
Of the thirteen public functions that return a `Result`, only `bring_up` has an `# Errors`
heading. The source holds four code blocks, none on `configure`, `start`, `stop` or the Motorcomm
sequences. `RUSTDOCFLAGS="-D warnings" cargo doc --no-deps` fails on four dead links to
crate-private items. The README compiles as a doctest but is not the crate page.
Change: an `# Errors` heading on each fallible function, examples on `bring_up`, `configure` and
`DataPlane`, the four links as plain text, and `#![doc = include_str!("../README.md")]`. Door:
two-way. Effort: M.

#### P1-4. The probe deadline subtracts two clock readings unchecked

Verified in source (`src/bring_up.rs`, the loop after `cache_coherence::prepare`).
`port.now_microseconds() - started` panics in a debug build if the caller's clock reads lower the
second time, and wraps in a release build, which ends the wait at once and yields an inconclusive
probe that P0-7 then accepts. Change: `saturating_sub`. Door: two-way. Effort: S.

### P2: may follow

#### P2-1. The manifest has no `documentation` key and no `include` list

Verified by `cargo package --list`.
The package carries `falsifications/`, `docs/stranger-test.md`, `_typos.toml`, `deny.toml` and
`CODEOWNERS`. Change: a `documentation` key and an `include` list of `src/`, the licenses, the
README and the CHANGELOG. Door: two-way. Effort: S.

#### P2-2. `smoltcp` and `embassy-net-driver` adapters and a borrowed frame

Verified in the comparators' source.
`stm32-eth` implements `smoltcp::phy::Device` behind `smoltcp-phy`, and `esp-p4-eth` implements
`embassy-net-driver`. This crate implements neither, and its data plane copies each frame in and
out, so an adapter over it copies twice. Change: a closure-taking
receive and transmit over the ring buffers, and the two adapters behind features named by the
shared decision. Door: two-way (additions). Effort: M.

#### P2-3. Ring sizes the caller chooses

Verified in source and inferred for the rate.
Both rings hold 16 entries, fixed. At 1 Gbit/s a ring of 16 minimum-size frames fills in about
11 microseconds. Linux defaults to 512; `embassy-stm32` and `esp-emac` take const parameters.
Change: defaulted const parameters on `DataPlane` and the layout, which adds them without a break.
Door: two-way. Effort: M.

#### P2-4. The driver always programs one MDIO clock range

Verified in source (`src/management_data_io.rs`) and inferred for the boards.
The driver always programs the largest divider, which keeps MDC under 2.5 MHz for a CSR clock up
to 810 MHz and no faster. Linux (`stmmac_clk_csr_set`)
and OpenBSD pick the range from the clock's rate. Change: an optional range in `BusConfiguration`
once P0-1 lands, the largest divider by default. Door: two-way. Effort: S.

#### P2-5. The simulator ships to callers

Verified in source.
`simulator` (799 lines) is `#[cfg(test)]`, so a caller testing its own integration writes its own
controller. Change: per the shared simulators decision. Door: two-way. Effort: S.

### Measured performance

On an x86_64 Linux host, release build, four runs of 2,000,000 frames, with a bench crate outside
the repository. The region is ordinary memory, the tails discard their writes, the barrier is a
`SeqCst` fence, and a stand-in device completes each descriptor. Per frame: transmit 16 to 24 ns at
60 bytes and 41 to 49 ns at 1514 bytes; receive 17 to 21 ns at either size, each with encode or
verdict, copy, ring step and tail write. On a board, uncached or coherent memory dominates both.

`stm32-eth` builds only for an STM32 target, so it did not run beside it.

## One-way doors

Each for the architect, one at a time.

- D1, structs that can grow (P0-1). Recommended: `#[non_exhaustive]` on `Inputs`, `Link`,
  `BusConfiguration`, `Settings` and `Bus`, with constructors, and `dropped` behind a getter. A
  non-exhaustive struct can open later; an exhaustive one cannot close.
- D2, the physical layer device (P0-2). Recommended: defer the trait and name the bring-up after
  the `YT8531`. With D1, a generic bring-up can follow as an addition; a trait published now
  cannot be withdrawn.
- D3, the error shape (P0-3). Recommended: `Display`, `core::error::Error` and `source`, in the
  shared errors decision's shape.
- D4, the bring-up's answer and the station address (P0-4). Recommended: a named result struct and
  a validated address newtype; a bare array can never gain the check.
- D5, the packed settings word (P0-5). Recommended: crate-private for 0.1.0. A published layout is
  a format, and none of the comparators publishes one.
- D6, the device's physical address (P0-6). Recommended: an `unsafe trait` region that supplies its
  own address, which holds the promise in one implementation and removes the public field;
  failing that, `unsafe fn` constructors. Safe later is compatible; the reverse breaks callers.
- D7, the inconclusive probe (P0-7). Recommended: refuse it by default, the stricter choice, with
  an `Inputs` field that accepts it once D1 lands.

## Evidence for the shared decisions

What this crate shows for each shape of milestone 1129, at `565b331f`.

- **Errors.** Four error enums, all `#[non_exhaustive]`, none with `Display` or
  `core::error::Error` (`src/bring_up.rs`, `src/network_interface_controller.rs`,
  `src/management_data_io.rs`, `src/data_plane.rs`). Variants name the input that failed, and
  `bring_up::Error` wraps the others as tuple variants: one enum per module.
- **DMA regions.** `DirectMemoryAccessRegion` (`src/data_plane.rs`) has `read_u64`, `write_u64`,
  `read_bytes` and `write_bytes` at `u64` offsets, takes `&self` to read, and has no barrier and no
  cache operation; `cache_coherence` measures coherence rather than supplying it. P0-6 asks
  whether the region should supply its own address.
- **Doorbells and tails.** `Tails` (`src/data_plane.rs`) holds `set_receive_tail`,
  `set_transmit_tail` and `barrier`, each tail the low 32 bits of a physical address, which works
  because `configure` refuses a region that straddles 4 GiB. The barrier sits with the tails
  because it orders descriptor writes before the doorbell.
- **Register access.** `Hardware` (`src/hardware.rs`) joins `read(u32) -> u32`, `write(u32, u32)`
  and `delay_microseconds(u64)` in one trait, with a volatile 32-bit access as its contract.
  `bring_up::Port` adds `now_microseconds` and the region.
- **Byte sinks and sources.** Not applicable: frames, not byte streams.
- **Feature names.** None. P2-2 would add the first two, after `stm32-eth`'s `smoltcp-phy`.
- **Simulators.** `src/simulator.rs`, 799 lines, `#[cfg(test)]`, models the controller, its
  descriptors and a physical layer device; P2-5.
- **Memory regions.** The caller provides the region; `layout` fixes its shape
  (`DIRECT_MEMORY_ACCESS_REGION_BYTES`, `receive_descriptor`, `transmit_descriptor`) and takes its
  physical address as a bare `u64` in `DataPlane::new` and `configure`. Only `configure` checks the
  address against the controller's width.

## Follow-on

- **Outstanding.** The board run of milestone 1074 settles P1-1.

## Done when

Each P0 and P1 finding reads Done or Will not fix with its ruling, the architect has answered D1 to
D7, and `script/review-status` reports BUILT.

## BUGS

- No comparator ran; the review took each one's behavior from its source.
- The benchmark ran over ordinary memory on a host, not over a device's DMA region.

## Index row

The release review of `designware_ethernet` against `stm32-eth`, `esp-emac`, `dwmac-my` and three
drivers outside Rust: seven one-way interface changes before 0.1.0, four two-way fixes before the
release, five that may follow, seven doors to rule.
