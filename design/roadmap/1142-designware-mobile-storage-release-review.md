---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1142. `designware_mobile_storage`: the release review's findings

The release review of `partsfoundry/designware_mobile_storage` at commit `ac950346`, version
0.1.0-pre.3, under milestone 1129 (the combine review), whose
[block](1129-crate-interfaces-best-in-class.md) sets its form. The baseline is
milestone 1050 (the outside review's findings),
[its block](1050-designware-mobile-storage-outside-review.md) and the cleared package
[`notes/crate-reviews/designware-mobile-storage.md`](../../notes/crate-reviews/designware-mobile-storage.md).
1050's open items wait on a board run and stay its own; nothing here repeats them. Its decision 4,
the crate keeping its own direct memory access trait, stands as door D7 below.

Reuse: the prior-art table weighs each SD driver a caller could take instead.

## Finding status

- P0-1, five public structs are exhaustive: Done, `partsfoundry/designware_mobile_storage#43`.
- P0-2, the error variants are positional: Waiting on the errors decision of milestone 1129.
- P0-3, block buffers carry no block type: Done, `partsfoundry/designware_mobile_storage#43`.
- P0-4, the bus width is a bare `u8`: Done, `partsfoundry/designware_mobile_storage#43`.
- P0-5, `command::Response` is exhaustive: Done, `partsfoundry/designware_mobile_storage#43`.
- P0-6, the region trait is safe to implement: Open.
- P1-1, the `simulator` feature turns the whole crate into a std crate: Done,
  `partsfoundry/designware_mobile_storage#43`.
- P1-2, the README miscounts the harnesses: Done, `partsfoundry/designware_mobile_storage#43`.
- P1-3, a stale comment in the manifest: Done, `partsfoundry/designware_mobile_storage#43`.
- P1-4, two public types have no `Debug`: Done, `partsfoundry/designware_mobile_storage#43`.
- P1-5, only the crate page has an example: Done, `partsfoundry/designware_mobile_storage#43`.
- P2-1, a `BlockDevice` adapter: Waiting on the feature-name decision of milestone 1129.
- P2-2, a data path without the copy: Open.
- P2-3, 64-bit descriptors: Open.
- P2-4, `new` drops the register window when it refuses: Done,
  `partsfoundry/designware_mobile_storage#43`.
- P2-5, the card protocol over a host trait: Open.
- P2-6, the manifest has no `documentation` key: Done, `partsfoundry/designware_mobile_storage#43`.
- P2-7, the bounds on the struct declarations: Done, `partsfoundry/designware_mobile_storage#43`.

## Open decisions

The one-way doors D1 to D9 below.

## Goal

A stranger with a board built on the DesignWare controller picks this crate over the Rust
drivers for it and over porting U-Boot's. Its types refuse the wrong buffer and the wrong bus
width, its errors name their fields, and it plugs into the block traits the ecosystem already uses.

## What the review read and ran

The sources, the commands and the systems outside Rust are in
[the appendix](1142-designware-mobile-storage-release-review/what-was-checked.md), and the 54
API Guidelines items in [the guidelines table](1142-designware-mobile-storage-release-review/api-guidelines.md).

## Prior art

Measured from the crates.io API on 2026-11-26 (UTC). A stranger brings this crate the problem of
bringing up an SD card or eMMC and moving blocks, with no operating system. The two crates for
this controller draw under 10,000 downloads in 90 days, so the review also reads Linux and U-Boot, which
drive it on the same boards.

| crate or system | role | version read | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `embedded-sdmmc` | ranked 1: an SD card over SPI, with FAT | 0.10.0 | 412,688 | 62,481 | 40 | 2026-08-10 |
| `sdmmc-protocol` | ranked 2: card protocol over host traits | 0.5.4 | 2,525 | 861 | 7 | 2026-09-18 |
| `dwmmc-host` | the same controller, `sdmmc-protocol`'s backend | 0.4.2 | 1,933 | 568 | 2 | 2026-09-09 |
| `simple-sdmmc` | ranked 3: the same controller | 0.1.1 | 13,807 | 713 | 1 | 2026-05-09 |
| `sdmmc` | measured, not read: an ARM64 SD driver | 0.1.0 | 11,317 | 592 | 2 | 2026-01-28 |
| `sdio-host` | neighbor: card register types only | 0.9.0 | 1,744,625 | 641,939 | 3 | 2022-07-27 |
| `sdio` | neighbor: the successor of `sdio-host` | 0.5.3 | 158,958 | 143,003 | 2 | 2026-10-19 |
| `embedded-sdmmc-types` | integration: the `BlockDevice` trait | 0.1.0 | 22,681 | 21,186 | 2 | 2026-08-10 |
| `block-device-driver` | integration: an async block trait | 0.2.0 | 1,549,551 | 713,321 | 8 | 2024-03-30 |
| `embedded-storage` | integration: storage traits | 0.3.2 | 10,347,110 | 1,749,590 | 89 | 2026-09-20 |
| `embedded-hal` | integration: delays and pins | 1.0.0 | 41,112,022 | 10,120,693 | 1852 | 2024-01-09 |
| `tock-registers` | integration: typed registers | 0.12.0 | 2,363,430 | 619,429 | 75 | 2026-11-04 |
| `safe-mmio` | integration: memory-mapped access | 0.4.0 | 647,707 | 214,105 | 13 | 2026-11-12 |
| Linux `drivers/mmc/host/dw_mmc.c` | outside Rust | v6.12 | | | | |
| U-Boot `drivers/mmc/dw_mmc.c` | outside Rust | v2025.10 | | | | |

### What `designware_mobile_storage` does better

- Than `embedded-sdmmc`: it drives the card through the SD host controller on a four- or
  eight-bit bus with the controller's own direct memory access engine; `embedded-sdmmc` speaks the
  card's SPI mode, one bit wide. The file system is a separate crate here, not bundled.
- Than `sdmmc-protocol` with `dwmmc-host`: it has no dependencies, where `dwmmc-host` 0.4.2
  takes eight (among them `dma-api`, `mmio-api`, `embedded-hal`, `log` and `volatile`). It keeps a
  polled FIFO path beside the descriptor path, where `dwmmc-host` needs an interrupt and the
  engine. It exports a simulator for a caller's tests and
  proves 22 properties with Kani.
- Than `simple-sdmmc`: every transfer returns an error, where `simple-sdmmc` 0.1.1's
  `read_block` and `write_blocks` `unwrap` the controller's result and panic. It refuses a buffer that
  is not a whole number of blocks, where `simple-sdmmc` divides and drops the remainder. It checks
  a region before the engine sees it, where `simple-sdmmc`'s `read_blocks_dma` casts the
  buffer's virtual address to `u32` and documents the identity mapping it assumes.
- Than Linux and U-Boot: it needs no operating system's mapping layer, no device model and
  no allocator, and Kani proves its card bring-up, where theirs rests on tests.

## The items

Effort is S (half a day), M (a day or two) or L (longer). One-way means a caller outside the
repository acts on it once 0.1.0 is out, so each P0 lands in 0.1.0 or not at all.

### P0: the 0.1.0 interface

#### P0-1. Five public structs are exhaustive

Verified in source (`src/sd.rs`, `src/host_controller.rs`, `src/card.rs`, `src/command.rs`).
`sd::Card` (ten public fields), `host_controller::Identity` (ten), `card::CardIdentification`,
`command::Command` and `command::Data` have every field public and no `#[non_exhaustive]`. A caller
can build a `Card` that no card answered, and adding a field later, such as a card's speed class,
breaks every caller that builds or destructures one. `Deadlines` already has the attribute;
`simple-sdmmc` keeps its `SdMmc` fields private.
`command::Data` has no public constructor, only its three public fields, so the attribute alone
would leave a caller no way to build one and make `Command::with_data` unusable.
Change: `Card` and `Identity`, which are the hardware's answers and which a caller hands back to
`read_blocks`, get private fields with getters, so a caller can read one and never forge one.
`Data` gains a constructor, such as `Data::new(block_bytes, blocks, write)` (name provisional),
and becomes `#[non_exhaustive]`. `CardIdentification` and `Command` become `#[non_exhaustive]`
with their fields still readable, and `Command::new` and `Command::with_data` remain the way to
build a command. Door: one-way (D1). Effort: S.

#### P0-2. The error variants are positional

Verified in source.
`host_controller::Error` has twelve variants such as `CommandTimeout(u8, u32)` and
`DataTimeout(u8, u32, u32)`; `sd::InitializationError` and `BlockTransferError::Status(u32)` do the
same. A caller matching on one must read the documentation to learn which number is the command
and which the status. All four error types implement `Display` and `core::error::Error` and are
`#[non_exhaustive]`, which is better than every Rust comparator.
Change: named fields, `CommandTimeout { command: u8, status: u32 }`, in the shape the errors
decision of milestone 1129 picks. Door: one-way (D2). Effort: M.

#### P0-3. Block buffers carry no block type

Verified in source.
`sd::read_blocks` and `sd::write_blocks` take `&mut [u8]` and `&[u8]` and refuse at run time a
length that is not a multiple of `BLOCK_BYTES` (`BlockTransferError::Length`). The
`BlockDevice` trait of `embedded-sdmmc-types` 0.1.0 takes `&mut [Block]`, and this crate's own
simulator hands out `&[[u8; BLOCK_BYTES]]`.
Change: `&mut [[u8; BLOCK_BYTES]]` and `&[[u8; BLOCK_BYTES]]`, and the `Length` variant goes; a
caller with bytes uses `as_chunks`. Door: one-way (D3). Effort: S.

#### P0-4. The bus width is a bare `u8`

Verified in source.
`sd::identify(host, maximum_bus_width: u8)` accepts 8 as a maximum, and its documentation names
8 for an eMMC slot, but the driver never sets an eight-bit bus. `configure_sd` sets four bits
for any maximum of four or more and one bit otherwise (`src/sd.rs`, lines 393 to 400), and the
eMMC path ignores the argument. `Card::bus_width` is a `u8` too. Linux and U-Boot carry the device tree's
`bus-width` as an integer, but neither is a type a caller can misuse at compile time.
Change: a `BusWidth` enum, `#[non_exhaustive]`, in both places, whose documentation says which
widths the driver sets today. Door: one-way (D4). Effort: S.

#### P0-5. `command::Response` is exhaustive

Verified in source (`src/command.rs`, line 100).
`Response` lists the response kinds this driver sends (`None`, `R1`, `R1b`, `R2`, `R3`, `R6` and
`R7`) with no `#[non_exhaustive]`. A caller that matches on it breaks when a later release adds
one, such as an SDIO card's R4 or R5.
Change: `#[non_exhaustive]`. Door: one-way (D8). Effort: S.

#### P0-6. The region trait is safe to implement

Verified in source (`src/internal_direct_memory_access.rs`).
`DirectMemoryAccessRegion` is a safe trait, and its `direct_memory_access_bus_address` tells the
controller where to read and write memory. The driver trusts that address, so the soundness of
every transfer rests on code a caller writes without an `unsafe` block. `dwmmc-host` 0.4.2 puts
the same promise on its constructor, `unsafe fn new(base: NonNull<u8>)`, and this crate's
constructor is safe. The question is where the soundness promise sits.
Change: `pub unsafe trait DirectMemoryAccessRegion`, with a `# Safety` section that states the
promise the trait's documentation already lists. Door: one-way (D9). Effort: S.

### P1: before the first release

#### P1-1. The `simulator` feature turns the whole crate into a std crate

Verified in source; the second hazard inferred from Cargo's feature unification.
`#![cfg_attr(not(any(test, feature = "simulator")), no_std)]` makes every module, the driver's
included, compile against std when the feature is on. The simulator needs std, so the feature
cannot build for a bare target whatever the fix; the hazards lie elsewhere. With the feature on,
a stray use of std in a driver module compiles, and nothing notices until a build without it.
Cargo also unifies features across a build, so one workspace member that turns `simulator` on
turns std on for every member that builds this crate in the same run.
Change: `#![no_std]` always, `extern crate std` under the feature, and the feature documented as
needing std. The feature's name is door D5. Door: two-way. Effort: S.

#### P1-2. The README miscounts the harnesses

Verified in source.
The README says "twenty-two in all" at line 84, then "runs all twenty-four harnesses" at line
194, and quotes a run line of 24 at line 221; `src/proofs.rs` holds 22 `#[kani::proof]` harnesses. Change: 22 throughout. Door: two-way.
Effort: S.

#### P1-3. A stale comment in the manifest

Verified in source.
`Cargo.toml`'s description comment names "the MBR rule for where a write test may land"; the
crate holds no partition code, which 1050 moved out. Change: drop the clause. Door: two-way.
Effort: S.

#### P1-4. Two public types have no `Debug`

Verified in source (C-DEBUG).
`HostController` and `InternalDirectMemoryAccess`; the simulators have one. Change: a `Debug`
that prints the controller's identity and state, not the window. Door: two-way. Effort: S.

#### P1-5. Only the crate page has an example

Verified in source (C-EXAMPLE).
The README, which is the crate page, reads one block through `identify` and `read_blocks`, and
`SimulatedHostController` has an example. No item in `host_controller`, `sd`,
`internal_direct_memory_access`, `card` or `command` has one, so the engine path
(`DirectMemoryAccessRegion`, `InternalDirectMemoryAccess::new`,
`with_internal_direct_memory_access`) appears in no example. Change: an example on each module and on
the engine path, run against the simulator. Door: two-way. Effort: S.

### P2: may follow

#### P2-1. A `BlockDevice` adapter

Verified in the comparators' source.
The crate implements neither `embedded-sdmmc-types`'s `BlockDevice` nor `block-device-driver`'s, so a
file system written against them cannot take this driver directly. Change: an optional adapter
under the name the feature-name decision picks. Door: two-way (an addition). Effort: S.

#### P2-2. A data path without the copy

Verified in source; not measured.
With the engine, `read_data` copies each block out of the region's pages into the caller's buffer
(`read_bytes`), and `write_data` copies in. Linux v6.12 maps the request's own pages
(`dma_map_sg`); U-Boot v2025.10 passes the buffer to `bounce_buffer_start`, which copies only a
buffer the engine cannot take as it is. Change: a path that takes a
caller's region as the transfer buffer, beside this one. Door: two-way. Effort: M.

#### P2-3. 64-bit descriptors

Verified in source.
`InternalDirectMemoryAccess::new` refuses a controller built with 64-bit addressing
(`Refusal::Addressing64`) and any region above 4 GiB. Linux and U-Boot drive both descriptor
formats. Change: the 64-bit format when a board needs it. Door: two-way. Effort: M.

#### P2-4. `new` drops the register window when it refuses

Verified in source.
`HostController::new` takes `R` by value and drops it on `Error::QueueWidth`, so a caller whose
window was costly to make cannot try again. Change: a constructor whose error carries the window
back, beside `new`. Door: two-way (an addition). Effort: S.

#### P2-5. The card protocol over a host trait

Verified in source.
`sd::identify`, `read_blocks` and `write_blocks` take `&mut HostController<R, D>`, so the card
protocol serves this controller alone. `sdmmc-protocol`, Linux (`mmc_host_ops`) and U-Boot
(`dm_mmc_ops`) put a host trait between the card protocol and the controller. Change: a trait
when a second controller wants the protocol, which is the point at which the protocol would also
become its own crate. Door: two-way. Effort: L.

#### P2-6. The manifest has no `documentation` key

Verified in `Cargo.toml` (C-METADATA).
Change: add it. Door: two-way. Effort: S.

#### P2-7. The bounds on the struct declarations

Verified in source (C-STRUCT-BOUNDS).
`HostController<R: RegisterWindowAndClock, D: DirectMemoryAccessRegion>` and
`InternalDirectMemoryAccess<D: DirectMemoryAccessRegion>` bound their parameters where the fields
need none. Change: move the bounds to the `impl` blocks. Door: two-way, since removing a bound
breaks no caller. Effort: S.

### Measured performance

Not run. The interface shapes throughput through the copy of P2-2, but measuring it needs a board,
and the leading same-controller comparator needs a platform's `dma-api` domain to run at all. The
simulator models no bus timing, so a run on it would measure the simulator.

## One-way doors

- D1, exhaustive structs (P0-1). Recommended: private fields with getters on `Card` and
  `Identity`, the stricter choice, so no caller can forge a hardware answer; `#[non_exhaustive]`
  on `CardIdentification`, `Command` and `Data`, with a constructor for `Data`. Opening a field
  or dropping the attribute later breaks no caller.
- D2, error fields (P0-2). Recommended: named fields, decided once for every crate by the
  errors decision.
- D3, block buffer type (P0-3). Recommended: arrays of `BLOCK_BYTES`, matching
  `embedded-sdmmc-types`.
- D4, bus width type (P0-4). Recommended: the enum.
- D5, the feature's name. `simulator`, the one exported test double among the drivers.
  Recommended: keep the name and have the simulators decision of milestone 1129 adopt it for every
  driver that ships one.
- D6, the register trait. `RegisterWindowAndClock` joins a read and write by offset with a
  microsecond clock. `tock-registers` and `safe-mmio` type each register's fields over a pointer,
  and `embedded-hal`'s `DelayNs` waits rather than reads a clock. Recommended: keep the one trait;
  a caller implements three methods, and the register-access decision of milestone 1129 may layer
  typed fields above it without changing it.
- D7, the region trait. 1050's decision 4, provisional A, keeps this crate's
  `DirectMemoryAccessRegion`. Recommended: keep it until the shared region decision rules, since
  its `u32` offsets and its barrier differ from the other two drivers'.
- D8, the response kinds (P0-5). Recommended: `#[non_exhaustive]` on `Response`.
- D9, whether the region trait is `unsafe` (P0-6). Recommended: `unsafe trait`. The trait's
  bus address decides where the controller writes, so its implementer makes a promise the
  compiler cannot check, and an `unsafe impl` is where Rust asks for one. Making it safe later is
  a relaxation; making it unsafe after 0.1.0 breaks every implementer.

## Follow-on

- **Outstanding.** The shared decisions of milestone 1129 take D2 for errors, D5 and P2-1 for feature names and simulators, D6 for
  register access, D7 and D9 for regions.

## Done when

Every P0 and P1 finding reads Done, or Will not fix with its ruling, the architect has ruled D1
to D9, and `script/review-status` shows the block BUILT.

## BUGS

- The review ran no comparator, and measured `sdmmc` 0.1.0 without reading it.
- The Linux and U-Boot readings are of one file each, at the versions in the table.

## Index row

The release review of `designware_mobile_storage` against `embedded-sdmmc`, `sdmmc-protocol` with
`dwmmc-host`, `simple-sdmmc`, Linux and U-Boot: six one-way type changes before 0.1.0, a feature
that turns off no_std, four smaller fixes before the release and nine doors to rule.
