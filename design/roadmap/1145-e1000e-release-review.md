---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1057, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1145. `e1000e`: the release review's findings

*(The number and the slug are provisional.)*

The release review of `partsfoundry/e1000e` at commit `6f6d3f1c`, version 0.1.0-pre.4, under
milestone 1129 (the combine review), whose [block](1129-crate-interfaces-best-in-class.md) sets its
form. The baseline is milestone 1057 (the outside review's findings),
[its block](1057-e1000e-outside-review.md) and the cleared package
[`notes/crate-reviews/e1000e.md`](../../notes/crate-reviews/e1000e.md). 1057's open items stay its
own, and nothing here repeats them: the first release still waits for its cabled I219 run (P1-7),
and its rulings on the ring size (P2-6) and on the private test doubles (P2-7) stand. The names
1057 ratified stand, `empty_descriptor_rings` among them; the recheck against the naming rules made
after the clearance finds none that a later rule reopens.

Reuse: the prior-art table weighs each Intel driver a caller could take.

## Finding status

- P0-1, the data plane's counters are public fields: Done, partsfoundry/e1000e#42.
- P0-2, the device table is a slice of bare pairs: Done, partsfoundry/e1000e#42.
- P0-3, the register trait takes `u64` offsets: Waiting on the register-access decision of
  milestone 1129.
- P0-4, nothing ties the bus address to the region: Waiting on the DMA-region decision of
  milestone 1129.
- P1-1, the package ships the repository's scaffolding: Done, partsfoundry/e1000e#42.
- P1-2, no item carries an example: Done, partsfoundry/e1000e#42.
- P1-3, no fallible function has an `# Errors` section: Done, partsfoundry/e1000e#42.
- P2-1, a `smoltcp` device adapter: Waiting on the feature-name decision of milestone 1129.
- P2-2, a data path without the copy: Waiting on the DMA regions decision of milestone 1129.
- P2-3, a link-state query: Done, partsfoundry/e1000e#42.
- P2-4, `DataPlane::new` panics where it could refuse: Done, partsfoundry/e1000e#42.
- P2-5, the manifest has no `documentation` key: Done, partsfoundry/e1000e#42.
- P2-6, no attribute states that the crate has no `unsafe`: Done, partsfoundry/e1000e#42.

## Open decisions

The one-way doors D1 to D6 below.

## Goal

A stranger with an 82574L under QEMU or an I219 on a desktop board picks this crate over porting
FreeBSD's or Linux's driver and over the Rust drivers for other Intel parts. It brings the device up
without an operating system, its data plane plugs into `smoltcp` with little glue, and its traits
match the other ring drivers' once the shared decisions rule.

## What the review read and ran

See [the appendix](1145-e1000e-release-review/what-was-checked.md) and
[the guidelines table](1145-e1000e-release-review/api-guidelines.md).

## Prior art

Measured from the crates.io API on 2026-11-26 (UTC). A stranger brings this crate the problem of
sending and receiving Ethernet frames on an Intel 8257x or I219 controller, with no operating
system. No Rust crate for this family draws 10,000 downloads in 90 days; the leading Intel driver,
`ixgbe-driver`, serves the 10 Gb/s 82599 instead. So the review also reads Linux's `e1000e`
driver, which drives the same parts.

| crate or system | role | version read | total | 90 days | reverse dependencies | version read released |
|---|---|---|---|---|---|---|
| `ixgbe-driver` | ranked 1: another Intel family, the 82599 | 0.1.1 | 87,036 | 49,984 | 2 | 2026-02-26 |
| `eth-intel` | ranked 2: an Intel e1000 driver | 0.2.4 | 11,183 | 841 | 1 | 2026-09-11 |
| `e1000-driver` | ranked 3: the 8254x e1000 | 0.1.0 | 1,885 | 92 | 0 | 2023-02-24 |
| `eth-igb` | measured and read, not ranked: the Intel igb family | 0.1.1 | 831 | 7 | 0 | 2025-07-18 |
| `virtio-drivers` | neighbor: the virtio network device | 0.13.0 | 445,515 | 101,631 | 91 | 2026-03-03 |
| `axdriver_net` | neighbor: a network driver trait over `ixgbe-driver` | 0.2.0 | 19,634 | 1,708 | 2 | 2026-04-03 |
| `smoltcp` | integration: the `phy::Device` trait | 0.14.0 | 11,087,347 | 3,453,932 | 133 | 2026-08-17 |
| `embassy-net-driver` | integration: the `Driver` trait | 0.2.0 | 2,673,211 | 977,529 | 18 | 2023-10-18 |
| Linux `drivers/net/ethernet/intel/e1000e` | outside Rust | v6.12 | | | | |

crates.io has no crate named `e1000e`, `e1000`, `igb`, `intel-e1000`, `e1000e-driver` or
`igb-driver`, and searches for 82574, I219 and e1000e find no other driver.

### What `e1000e` does better

- Than `ixgbe-driver`: its four error types implement `Display` and `core::error::Error` and are
  `#[non_exhaustive]`; `IxgbeError` derives only `Debug`. It has no dependencies, where
  `ixgbe-driver` takes five, `smoltcp` 0.12 among them.
- Than `eth-intel` and `eth-igb`: no `dma-api`, `mmio-api` or `tock-registers` domain to set up
  first, and errors that say which step failed, not free text.
- Than `e1000-driver`: it targets the 82574L and the I219, the parts on current boards and in
  QEMU's `e1000e` model, where `e1000-driver` drives the older 8254x.
- Than Linux v6.12: the same bring-up order with no operating system, no allocator and no
  locking layer, and with Kani proofs over every status word a device can write.

## The items

Effort is S (half a day), M (a day or two) or L (longer). A P0 changes a public item that callers
will build on from 0.1.0 onward, so it lands before that version or stays as it is.

### P0: the 0.1.0 interface

#### P0-1. The data plane's counters are public fields

Verified in source.
`DataPlane::dropped` and `DataPlane::dropped_for_lack_of_room` are `pub u32` fields, so a caller
can write them as well as read them, and moving them behind a method later breaks every caller
that names the field. The struct's other fields are private. `ixgbe-driver` keeps its device's
state in private fields of `IxgbeDevice`. `dropped_for_lack_of_room` is a provisional name.
Change: private fields, read through `dropped()` and `dropped_for_lack_of_room()`. Door: one-way
(D1). Effort: S.

#### P0-2. The device table is a slice of bare pairs

Verified in source.
`DEVICE_IDS: &[(u16, &str)]` makes the pair and its strings, such as `"I219-LM (SPT)"`, part of
the interface. Adding a field, such as the device family a caller must branch on, breaks every
caller that destructures a pair. `is_supported_device` and `model_name` already answer the two
questions a probe asks. Linux's `e1000_pci_tbl` carries a board type beside each identifier, which
is the field this table would grow.
Change: `DEVICE_IDS` stays inside the crate, and the two functions stay the interface. Door:
one-way (D2). Effort: S.

#### P0-3. The register trait takes `u64` offsets

Verified in source.
`Hardware::read(&mut self, offset: u64) -> u32` and `write`, and the register constants in
`registers` and `platform_controller_hub::registers`, and the configuration-space offset
`flush::PCI_CONFIGURATION_DESCRIPTOR_RING_STATUS_REGISTER`, are `u64`, though every offset the crate names is below `0x1_0000`, and the PHY
registers of `physical_layer_device::registers` are `u32`. `designware_ethernet::Hardware` takes
`u32` offsets, as do `ixgbe-driver`'s `get_reg32(reg: u32)` and Linux's `__er32`, an offset added
to `hw_addr`. The width is in every implementation a caller writes.
Change: the width the register-access decision of milestone 1129 picks, for `Hardware` and the
offset constants together. Door: one-way (D3). Effort: S.

#### P0-4. Nothing ties the bus address to the region

Verified in source.
`DataPlane::new(data_plane_physical_address: u64)` is a safe function, and `start`, `receive` and
`transmit` write that address plus an offset into each descriptor (`src/data_plane.rs`, lines 140
to 146, 200 and 233), where the device reads it and then reads or writes the buffer there. Nothing
ties the address to the `DirectMemoryAccessRegion` passed on each call, keeps that memory mapped
and unshared while the device holds descriptors, or says what holds after a drop of the
`DataPlane`. `flush::empty_descriptor_rings(.., transmit_ring: u64)` hands the device an address the
same way. So the soundness of the device's accesses rests on a promise that no `unsafe` asks the
caller to make. `ixgbe-driver`'s `IxgbeHal` and `virtio-drivers`' `Hal` are `unsafe trait`s, which
puts the contract on the implementer, and Linux's `struct e1000_ring` holds `desc` and `dma`
together. `designware_ethernet` takes its address the same way (block 1147).
Change: a contract the caller accepts with `unsafe`, in the form the DMA-region decision of
milestone 1129 picks. Door: one-way (D4), since a safe function can become unsafe only by breaking
every caller, and the reverse breaks none. Effort: M.

### P1: before the first release

#### P1-1. The package ships the repository's scaffolding

Verified by building.
`cargo package --list --allow-dirty` lists 73 files, among them `.github/`, `.githooks/`,
`.cargo/mutants.toml`, `deny.toml`, `CODEOWNERS` and the ten `falsifications/` patches. Change: an `include` list of `src/`, `examples/`, `docs/`, the README, the changelog
and the licenses. Door: two-way. Effort: S.

#### P1-2. No item carries an example

Verified in source (C-EXAMPLE, C-QUESTION-MARK).
The README, which is the crate page, shows `is_supported_device`, `model_name` and
`receive_verdict`, and `receive_verdict` has one more. `DataPlane`, the traits,
`initialize_hardware`, `setup_copper_link` and `empty_descriptor_rings` have none, so the bring-up
order appears only in `docs/bring-up.md`. `examples/host_ring.rs` drives the rings and ends each
fallible call with `expect`. Change: an example on `DataPlane` drawn from `host_ring.rs`, a
`no_run` example of the bring-up order on `initialize_hardware`, and `?` in `host_ring.rs`.
Door: two-way. Effort: S.

#### P1-3. No fallible function has an `# Errors` section

Verified in source (C-FAILURE).
Thirteen public functions return a `Result`, among them `DataPlane::transmit`,
`sequence::initialize_hardware`, `global_reset`, `setup_copper_link`,
`physical_layer_device::read`, `write`, `update`, `SoftwareFlag::acquire` and
`plan_paged_access`; `grep '# Errors'` finds no heading anywhere in `src/`. The variants' own
documentation says what each means, but not which function returns which. Change: an `# Errors`
section on each. Door: two-way. Effort: S.

### P2: may follow

#### P2-1. A `smoltcp` device adapter

Verified in the comparators' source.
`smoltcp` 0.14.0's `phy::Device` and `embassy-net-driver` 0.2.0's `Driver` hand out tokens that
lend the stack a buffer, and wrapping `DataPlane` in either takes a page of glue every caller
writes again. Change: an optional adapter under the
name the feature-name decision of milestone 1129 picks. Door: two-way (an addition). Effort: S.

#### P2-2. A data path without the copy

Verified in source; measured below.
`receive` copies the frame from the region into the caller's `out`, and `transmit` copies `frame`
into the region, since `DirectMemoryAccessRegion` lends no slice. Linux v6.12 copies too, but only
a frame shorter than `copybreak`; a longer one goes up in the buffer the device wrote.
`virtio-drivers`' `VirtIONetRaw` shares the caller's buffer with the device through `Hal::share`.
The copy of a full frame costs near 30 ns on the host, against 12.3 µs on a 1 Gb/s wire. Change: a token path, beside these methods, that lends the slot to the
stack. Door: two-way. Effort: M.

#### P2-3. A link-state query

Verified in source.
`DEVICE_STATUS_LINK_UP` is public, but no function reads it; a caller reads the status register
through `Hardware` itself. `embassy-net-driver`'s `Driver::link_state` and `ixgbe-driver`'s
`NicDevice::get_link_speed` make it part of the driver. Change: `is_link_up(hardware: &mut impl
Hardware) -> bool`. Door: two-way (an addition). Effort: S.

#### P2-4. `DataPlane::new` panics where it could refuse

Verified in source.
`new` asserts that the region fits below the top of the physical address space, a case only the
caller's mapping can rule out. Change: a `try_new` returning `Option<DataPlane>`, beside `new`. Door:
two-way (an addition). Effort: S.

#### P2-5. The manifest has no `documentation` key

Verified in `Cargo.toml` (C-METADATA).
Change: add it. Door: two-way. Effort: S.

#### P2-6. No attribute states that the crate has no `unsafe`

Verified in source.
The crate has no `unsafe`, and `src/lib.rs` does not say so. Change: `#![forbid(unsafe_code)]`,
or `#![deny(unsafe_code)]` with an `#[allow]` on each declaration if D4 makes one `unsafe`, since
the lint also fires on an `unsafe fn` or `unsafe trait` declaration (checked with `rustc`). Door:
two-way. Effort: S.

### Measured performance

The data plane's cost per frame, on a Linux x86_64 host, against a region over a `Vec<u8>` and
tails that store two integers, both written in the scratch crate the appendix describes. The
barrier is a compiler fence, as `Tails` documents for x86_64. Each figure is the lowest of seven
passes divided by the repeats; the range is over three runs of the program.

| frame | transmit and completion | device write and receive | device write alone |
|---|---|---|---|
| 60 bytes | 9.3 to 9.4 ns | 14.6 to 15.4 ns | 4.2 to 4.5 ns |
| 1514 bytes | 31.0 to 32.2 ns | 58.7 to 66.8 ns | 22.5 to 23.1 ns |

The first column is `transmit` and the fake's completion, the second the fake's copy into a slot
and `receive`, and the third the fake's part of the second alone; the appendix has the detail.


Inferred: the data plane's own share of a receive is about 10 ns at 60 bytes and 36 to 44 ns at
1514, so the copy of the larger frame costs about 30 ns here. No comparator ran: `virtio-drivers` keeps its fake behind `#[cfg(test)]`, and `ixgbe-driver` needs a mapped device, so neither runs like for like without hardware.

## One-way doors

- D1, the counters (P0-1). Recommended: private fields and two read methods before 0.1.0, the
  stricter choice; a setter can come later, and a public field cannot go back.
- D2, the device table (P0-2). Recommended: keep `DEVICE_IDS` inside the crate and
  `is_supported_device` and `model_name` as the interface, the stricter choice; a typed,
  `#[non_exhaustive]` table can follow later.
- D3, the register offset width (P0-3). Recommended: `u32`, matching `designware_ethernet::Hardware`
  and every comparator, for the configuration-space constant as well. The DMA region keeps `u64`,
  since a region can be large. Decided once for every ring driver by the
  register-access decision.
- D4, the bus address contract (P0-4). Option A: `DataPlane::new` and `empty_descriptor_rings`
  become `unsafe fn`s. Each `# Safety` section requires that the address is the bus address of the
  region passed on every call, and that the memory stays mapped and unshared until the caller stops
  the device. Option B: an `unsafe trait` region that reports its own bus address, as
  `ixgbe-driver` and `virtio-drivers` do. Recommended: A for 0.1.0, which keeps the per-call
  borrow that lets a caller hold the region and the registers in its own fields; either is the
  stricter choice over today's safe function, and a later decision may lift it. Decided once for
  this crate and `designware_ethernet`.
- D5, the tails trait. `Tails` sets the two tails and carries the barrier, and lets a caller hold a receive tail write back to a newer value, as `designware_ethernet`'s `Tails` sets its two and carries
  its barrier. `non_volatile_memory_express` and `extensible_host_controller_interface` compute a
  doorbell offset and declare no trait, and Linux writes `rx_ring->tail` with `writel` once per 16
  buffers (`E1000_RX_BUFFER_WRITE`). `FlushSupport`, the third trait of the ring path, reads the configuration-space status word
  and writes one transmit descriptor with its own ordering, because the flush runs before any
  `DataPlane` exists. Recommended: keep both traits as they stand, and have the doorbells-and-tails
  decision of milestone 1129 adopt `Tails` for the two ring drivers and name `FlushSupport` as
  this crate's own.
- D6, the simulator, behind `#[cfg(test)]` as 1057's P2-7 ruled provisionally. Recommended: keep
  it private for 0.1.0, the stricter choice, since exporting it later is an addition.

## Evidence for the shared decisions

- **Errors.** The crate: four error enums (`TransmitError`, `physical_layer_device::Error`,
  `non_volatile_memory::Error`, `sequence::Error`), each with `Display`, `core::error::Error` and
  `#[non_exhaustive]`, unit variants except `sequence::Error`'s two wrapping variants, whose
  `source` returns the inner error. The comparators: `IxgbeError` derives only `Debug` and is
  exhaustive; `virtio-drivers`, `eth-intel` and `eth-igb` derive `thiserror::Error`, the last two
  with free-text variants.
  Points toward an enum per module with `Display`, `core::error::Error` and `#[non_exhaustive]`,
  and the inner error chained through `source`; this crate already conforms.
- **DMA regions.** The crate: `DirectMemoryAccessRegion` with `u64` offsets, four methods, no
  barrier, implemented by the caller over memory it owns. The comparators: `ixgbe-driver`'s
  `IxgbeHal` (`src/hal.rs`) and `virtio-drivers`' `Hal` (`src/hal.rs`) are `unsafe trait`s that
  allocate the memory and return `NonNull<u8>`, which the driver then reads directly;
  `designware_ethernet` has the same trait shape as this crate, `designware_mobile_storage` takes
  `u32` offsets and a barrier. Both comparators put the contract for the memory on an `unsafe trait`,
  where this crate and `designware_ethernet` take a bare address in a safe function (P0-4). Points
  toward `u64` offsets, the barrier elsewhere and a contract the caller accepts with `unsafe` (D4).
- **Doorbells and tails.** The crate: `Tails` with two setters and the barrier, the receive tail
  allowed to lag. The comparators: `ixgbe-driver` writes its tail registers itself, Linux
  v6.12 batches the receive tail, and `virtio-drivers` notifies through its `Transport`. `FlushSupport` is a
  third trait beside `Tails` and the region, with its own descriptor write. Points toward keeping
  `Tails` for the two ring drivers, with the held-back receive tail as a documented permission (D5).
- **Register access.** The crate: `Hardware` with `u64` offsets, a 16-bit flash status read, a
  microsecond delay, the PCI vendor identifier and a `note` hook for bring-up observations. The
  comparators: `ixgbe-driver` (`get_reg32`, `u32`), `eth-intel` (`Regs::read(offset: usize)`),
  `eth-igb` (`tock-registers`), Linux (`er32` and `ew32`). Points toward a `u32` offset (D3), configuration-space offsets included, and a register trait of
  the caller's, with typed fields left above it; the delay and the `note` hook are this crate's own.
- **Byte sinks and sources.** Not applicable: the crate moves whole frames, not a byte stream.
- **Feature names.** The crate declares no features. The one candidate is the `smoltcp` adapter
  (P2-1), whose name waits on the decision. `virtio-drivers` names its optional dependency
  `embedded-io` and `ixgbe-driver` its interrupt support `irq`. Points toward a feature named for
  the dependency it brings in.
- **Simulators.** A private simulator and a public fake in `examples/host_ring.rs`;
  `virtio-drivers` keeps `FakeTransport` behind `#[cfg(test)]`, and no Intel comparator has a test
  double. Points toward a private simulator and a public example (D6).
- **Contract layout.** Not applicable: the crate exports no interface identity, magic or wire
  contract.

## Follow-on

- **Outstanding.** The shared decisions of milestone 1129 take D3 for register access, D4 for
  regions, D5 for doorbells and tails, D6 for simulators and P2-1 for feature names.


## Done when

The `e1000e` review is done once its P0 and P1 items read Done or Will not fix, D1 to D6 have rulings, and `script/review-status` lists BUILT.

## BUGS

- The benchmark ran against the crate's own kind of fake, not a device, and no comparator ran.
- The Linux reading is of four files of `drivers/net/ethernet/intel/e1000e` at v6.12; FreeBSD's
  `sys/dev/e1000` was not read beyond the names the crate cites.

## Index row

The release review of `e1000e` against six crates and Linux. Four one-way interface changes come before 0.1.0 and three
smaller fixes before the release; the data plane measures 9 to 67 ns a frame; six doors wait.
