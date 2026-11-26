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

- P0-1, the data plane's counters are public fields: Open.
- P0-2, the device table is a slice of bare pairs: Open.
- P0-3, the register trait takes `u64` offsets: Waiting on the register-access decision of
  milestone 1129.
- P0-4, the data plane borrows its region and tails on every call: Waiting on the DMA-region
  decision of milestone 1129.
- P1-1, the package ships the repository's scaffolding: Open.
- P1-2, no item carries an example: Open.
- P1-3, no fallible function has an `# Errors` section: Open.
- P2-1, a `smoltcp` device adapter: Waiting on the feature-name decision of milestone 1129.
- P2-2, a data path without the copy: Open.
- P2-3, a link-state query: Open.
- P2-4, `DataPlane::new` panics where it could refuse: Open.
- P2-5, the manifest has no `documentation` key: Open.

## Open decisions

The one-way doors D1 to D6 below.

## Goal

A stranger with an 82574L under QEMU or an I219 on a desktop board picks this crate over porting
FreeBSD's or Linux's driver and over the Rust drivers for other Intel parts. It brings the device up
without an operating system, its data plane plugs into `smoltcp` with little glue, and its traits
match the other ring drivers' once the shared decisions rule.

## What the review read and ran

The sources, the commands, the benchmark and the systems outside Rust are in
[the appendix](1145-e1000e-release-review/what-was-checked.md), and the 54 API Guidelines items in
[the guidelines table](1145-e1000e-release-review/api-guidelines.md).

## Prior art

Measured from the crates.io API on 2026-11-26 (UTC). A stranger brings this crate the problem of
sending and receiving Ethernet frames on an Intel 8257x or I219 controller, with no operating
system. No Rust crate for this family draws 10,000 downloads in 90 days; the leading Intel driver,
`ixgbe-driver`, serves the 10 Gb/s 82599 instead. So the review also reads Linux's `e1000e`
driver, which drives the same parts.

| crate or system | role | version read | total | 90 days | reverse dependencies | updated |
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

- Than `ixgbe-driver`: its traits are safe, and the caller owns the memory. `ixgbe-driver`'s
  `IxgbeHal` is an `unsafe trait` whose `dma_alloc` and `mmio_phys_to_virt` hand the driver raw
  pointers it then reads with `read_volatile`; this crate makes no volatile access and has no
  `unsafe` at all. Its four error types implement `Display` and `core::error::Error` and are
  `#[non_exhaustive]`; `IxgbeError` derives only `Debug`. It has no dependencies, where
  `ixgbe-driver` takes five, `smoltcp` 0.12 among them.
- Than `eth-intel` and `eth-igb`: no `dma-api`, `mmio-api` or `tock-registers` domain to set up
  first, and errors that say which step failed, where `eth-intel`'s `Other(&'static str)` and
  `eth-igb`'s `Unknown(&'static str)` carry free text.
- Than `e1000-driver`: it targets the 82574L and the I219, the parts on current boards and in
  QEMU's `e1000e` model, where `e1000-driver` drives the older 8254x, holds its registers as a
  `&'static mut [Volatile<u32>]` and allocates through its own `KernelFunc` trait.
- Than Linux v6.12: the same bring-up order (reset, the PHY workarounds, the flush of
  `em_flush_desc_rings` from FreeBSD) with no operating system, no allocator and no locking layer,
  and with Kani proofs over every status word a device can write.

## The items

Effort is S (half a day), M (a day or two) or L (longer). A P0 changes a public item that callers
will build on from 0.1.0 onward, so it lands before that version or stays as it is.

### P0: the 0.1.0 interface

#### P0-1. The data plane's counters are public fields

Verified in source.
`DataPlane::dropped` and `DataPlane::dropped_for_lack_of_room` are `pub u32` fields, so a caller
can write them as well as read them, and moving them behind a method later breaks every caller
that names the field. The struct's other fields are private. `ixgbe-driver` keeps its device's
state in private fields of `IxgbeDevice` and offers `reset_stats` as a method, and Linux keeps its
counters in the adapter. `dropped_for_lack_of_room` is a provisional name.
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
`registers` and `platform_controller_hub::registers`, are `u64`, though every offset the crate names is below `0x1_0000`, and the PHY
registers of `physical_layer_device::registers` are `u32`. `designware_ethernet::Hardware` takes
`u32` offsets, as do `ixgbe-driver`'s `get_reg32(reg: u32)` and Linux's `__er32`, an offset added
to `hw_addr`. The width is in every implementation a caller writes.
Change: the width the register-access decision of milestone 1129 picks, for `Hardware` and the
offset constants together. Door: one-way (D3). Effort: S.

#### P0-4. The data plane borrows its region and tails on every call

Verified in source.
`DataPlane::start`, `receive`, `transmit` and `can_transmit` each take `&mut impl
DirectMemoryAccessRegion` and `&mut impl Tails`, so a caller can hand one data plane a different region on a later call and the cursors then describe memory they did not fill. `ixgbe-driver`'s
`IxgbeDevice` and `virtio-drivers`' `VirtIONetRaw` own their queues and their transport, and
Linux's `struct e1000_ring` holds the ring's memory (`desc`, `dma`) and its `tail` together. The
borrow lets a caller keep the region and the registers in fields of its own and split the borrows.
Change: none before 0.1.0 unless the DMA-region decision of milestone 1129 picks ownership; an owning wrapper can come beside these methods later. Door: one-way (D4). Effort: M if it changes.

### P1: before the first release

#### P1-1. The package ships the repository's scaffolding

Verified by building.
`cargo package --list --allow-dirty` lists 73 files: beside `src/`, the README, the changelog and
the four licenses, it ships `.github/` (nine workflows, the issue templates, the accepted words),
`.githooks/commit-msg`, `.cargo/mutants.toml`, `deny.toml`, `_typos.toml`, `CODEOWNERS`, the ten
`falsifications/` patches and the three `docs/` files. A caller downloads the repository's CI with
the driver. Change: an `include` list of `src/`, `examples/`, `docs/`, the README, the changelog
and the licenses. Door: two-way. Effort: S.

#### P1-2. No item carries an example

Verified in source (C-EXAMPLE, C-QUESTION-MARK).
The README, which is the crate page, shows `is_supported_device`, `model_name` and
`receive_verdict`, and `receive_verdict` has one more. `DataPlane`, the two traits,
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
`smoltcp` 0.14.0's `phy::Device` hands out an `RxToken` and a `TxToken` whose `consume` gives the
stack a buffer; `embassy-net-driver` 0.2.0's `Driver` has the same shape. Wrapping `DataPlane` in
either takes a page of glue that every caller writes again. Change: an optional adapter under the
name the feature-name decision of milestone 1129 picks. Door: two-way (an addition). Effort: S.

#### P2-2. A data path without the copy

Verified in source; measured below.
`receive` copies the frame from the region into the caller's `out`, and `transmit` copies `frame`
into the region, since `DirectMemoryAccessRegion` lends no slice. Linux v6.12 copies too, but only
a frame shorter than `copybreak`; a longer one goes up in the buffer the device wrote.
`virtio-drivers`' `VirtIONetRaw` shares the caller's buffer with the device through `Hal::share`.
The measurement below puts the copy of a full frame near 30 ns on the host, against 12.3 µs for the
frame on a 1 Gb/s wire. Change: a token path, beside these methods, that lends the slot to the
stack. Door: two-way. Effort: M.

#### P2-3. A link-state query

Verified in source.
`DEVICE_STATUS_LINK_UP` is public, but no function reads it; a caller reads the status register
through `Hardware` itself. `embassy-net-driver`'s `Driver::link_state` and `ixgbe-driver`'s
`NicDevice::get_link_speed` make it part of the driver. Change: `is_link_up(hardware: &mut impl
Hardware) -> bool`. Door: two-way (an addition). Effort: S.

#### P2-4. `DataPlane::new` panics where it could refuse

Verified in source.
`new` asserts that the region fits below the top of the physical address space and documents the
panic. The address comes from the caller's mapping, so a caller that cannot rule the case out
cannot test for it first. Change: a `try_new` returning `Option<DataPlane>`, beside `new`. Door:
two-way (an addition). Effort: S.

#### P2-5. The manifest has no `documentation` key

Verified in `Cargo.toml` (C-METADATA).
Change: add it. Door: two-way. Effort: S.

### Measured performance

The data plane's cost per frame, on a Linux x86_64 host, against a region over a `Vec<u8>` and
tails that store two integers, both written in the scratch crate the appendix describes. The
barrier is a compiler fence, as `Tails` documents for x86_64. Each figure is the lowest of seven
passes divided by the repeats; the range is over three runs of the program.

| frame | transmit and completion | device write and receive | device write alone |
|---|---|---|---|
| 60 bytes | 9.3 to 9.4 ns | 14.6 to 15.4 ns | 4.2 to 4.5 ns |
| 1514 bytes | 31.0 to 32.2 ns | 58.7 to 66.8 ns | 22.5 to 23.1 ns |

- Transmit and completion: `DataPlane::transmit` (the reclaim, the copy into the region, two
  descriptor words, the barrier, the tail) and the fake device's completion, one read and one
  write of the status word.
- Device write and receive: the fake device's copy of the frame into the slot and its status word,
  then `DataPlane::receive` (the status read, the barrier, the copy out, the repost, the barrier,
  the tail).
- Device write alone: the fake device's part of the second column, timed by itself, to subtract.

Inferred: the data plane's own share of a receive is about 10 ns at 60 bytes and 36 to 44 ns at
1514, so the copy of the larger frame costs about 30 ns here. No comparator ran: `virtio-drivers` keeps its fake behind `#[cfg(test)]`, and `ixgbe-driver` needs a mapped device, so neither runs like for like without hardware.

## One-way doors

- D1, the counters (P0-1). Recommended: private fields and two read methods before 0.1.0, the
  stricter choice; a setter can come later, and a public field cannot go back.
- D2, the device table (P0-2). Recommended: keep `DEVICE_IDS` inside the crate and
  `is_supported_device` and `model_name` as the interface, the stricter choice; a typed,
  `#[non_exhaustive]` table can follow later.
- D3, the register offset width (P0-3). Recommended: `u32`, matching `designware_ethernet::Hardware`
  and every comparator, and covering every offset the crate names with room to spare; the DMA region
  keeps `u64`, since a region can be large. Decided once for every ring driver by the
  register-access decision.
- D4, who holds the region and the tails (P0-4). Recommended: keep the per-call borrow for 0.1.0;
  an owning wrapper can come later beside it, and taking the borrow form away later cannot.
- D5, the tails trait. `Tails` sets the two tails and carries the barrier, and lets a caller hold a receive tail write back to a newer value, as `designware_ethernet`'s `Tails` sets its two and carries
  its barrier. `non_volatile_memory_express` and `extensible_host_controller_interface` compute a
  doorbell offset and declare no trait, and Linux writes `rx_ring->tail` with `writel` once per 16
  buffers (`E1000_RX_BUFFER_WRITE`). Recommended: keep the trait as it stands, and have the
  doorbells-and-tails decision of milestone 1129 adopt this shape for the two ring drivers.
- D6, the simulator. `src/platform_controller_hub/simulator.rs` stays behind `#[cfg(test)]`, as
  1057's P2-7 ruled provisionally, and `examples/host_ring.rs` is the fake a caller sees.
  `virtio-drivers` keeps its `FakeTransport` the same way; `designware_mobile_storage` exports
  its simulator behind a `simulator` feature. Recommended: keep it private for 0.1.0, the stricter
  choice, since exporting it later is an addition; the simulators decision of milestone 1129 may
  export it.

## Evidence for the shared decisions

- **Errors.** The crate: four error enums (`TransmitError`, `physical_layer_device::Error`,
  `non_volatile_memory::Error`, `sequence::Error`), each with `Display`, `core::error::Error` and
  `#[non_exhaustive]`, unit variants except `sequence::Error`'s two wrapping variants, whose
  `source` returns the inner error. The comparators: `IxgbeError` (`src/lib.rs`) derives only
  `Debug` and is exhaustive; `virtio-drivers`' `Error` (`src/lib.rs`) and `eth-intel`'s and
  `eth-igb`'s (`src/err.rs`) derive `thiserror::Error`, the last two with free-text variants.
  Points toward an enum per module with `Display`, `core::error::Error` and `#[non_exhaustive]`,
  and the inner error chained through `source`; this crate already conforms.
- **DMA regions.** The crate: `DirectMemoryAccessRegion` with `u64` offsets, four methods, no
  barrier, implemented by the caller over memory it owns. The comparators: `ixgbe-driver`'s
  `IxgbeHal` (`src/hal.rs`) and `virtio-drivers`' `Hal` (`src/hal.rs`) are `unsafe trait`s that
  allocate the memory and return `NonNull<u8>`, which the driver then reads directly;
  `designware_ethernet` has the same trait shape as this crate, `designware_mobile_storage` takes
  `u32` offsets and a barrier. Points toward the safe, caller-owned trait with `u64` offsets and
  the barrier elsewhere, two crates to one (D4).
- **Doorbells and tails.** The crate: `Tails` with two setters and the barrier, the receive tail
  allowed to lag. The comparators: `ixgbe-driver` writes its tail registers itself
  (`src/ixgbe.rs`, `set_reg32`), Linux v6.12 batches the receive tail (`netdev.c`,
  `e1000_alloc_rx_buffers`), `virtio-drivers` notifies through its `Transport`. Points toward
  keeping `Tails` for the two ring drivers, with the held-back receive tail as a documented
  permission (D5).
- **Register access.** The crate: `Hardware` with `u64` offsets, a 16-bit flash status read, a
  microsecond delay, the PCI vendor identifier and a `note` hook for bring-up observations. The
  comparators: `ixgbe-driver` (`get_reg32`, `u32`), `eth-intel` (`src/e1000/registers.rs`,
  `Regs::read(offset: usize)` over a `NonNull<u8>`), `eth-igb` (`tock-registers`), Linux (`er32`
  and `ew32`, `hw.h`'s operation tables). Points toward a `u32` offset (D3) and a register trait of
  the caller's, with typed fields left above it; the delay and the `note` hook are this crate's own.
- **Byte sinks and sources.** Not applicable: the crate moves whole frames, not a byte stream.
- **Feature names.** The crate declares no features. The one candidate is the `smoltcp` adapter
  (P2-1), whose name waits on the decision. `virtio-drivers` names its optional dependency
  `embedded-io` and `ixgbe-driver` its interrupt support `irq`. Points toward a feature named for
  the dependency it brings in.
- **Simulators.** The crate: a simulator behind `#[cfg(test)]` and a fake region and tails in
  `examples/host_ring.rs`. The comparators: `virtio-drivers` keeps `FakeTransport` behind
  `#[cfg(test)]` (`src/transport/mod.rs`); no Intel comparator has a test double. Points toward a
  private simulator and a public example for the ring drivers (D6).
- **Contract layout.** Not applicable: the crate exports no interface identity, magic or wire
  contract.

## Follow-on

- **Outstanding.** The shared decisions of milestone 1129 take D3 for register access, D4 for
  regions, D5 for doorbells and tails, D6 for simulators and P2-1 for feature names.


## Done when

Every P0 and P1 finding reads Done, or Will not fix with its ruling, the architect has ruled D1
to D6, and `script/review-status` shows the block BUILT.

## BUGS

- The benchmark ran against the crate's own kind of fake, not a device, and no comparator ran.
- The Linux reading is of four files of `drivers/net/ethernet/intel/e1000e` at v6.12; FreeBSD's
  `sys/dev/e1000` was not read beyond the names the crate cites.

## Index row

The release review of `e1000e` against `ixgbe-driver`, `eth-intel`, `e1000-driver`, `eth-igb`,
`virtio-drivers`, `smoltcp` and Linux. Four one-way interface changes come before 0.1.0 and three
smaller fixes before the release; the data plane measures 9 to 67 ns a frame; six doors wait.
