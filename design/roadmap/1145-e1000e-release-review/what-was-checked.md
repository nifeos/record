# What the review read and ran

An appendix to [the milestone](../1145-e1000e-release-review.md).

## The crate

`partsfoundry/e1000e` at `6f6d3f1cc29f63d8beaa3e646ad60c21a19ca6e7`, version 0.1.0-pre.4,
edition 2024, `rust-version` 1.88, no dependencies and no features. Read: `Cargo.toml`,
`README.md`, `CHANGELOG.md`, `examples/host_ring.rs`, and every module under `src/` for its public
items (`lib`, `data_plane`, `descriptor`, `layout`, `registers`, `control_registers`,
`supported_devices`, and under `platform_controller_hub` the modules `hardware_access`,
`sequence`, `physical_layer_device`, `non_volatile_memory`, `flush`, `ultra_low_power`, `reset`
and `registers`). The review read the simulator, the tests and the three Kani proof modules for
their types only, and listed `docs/` and `fuzz/` without reading them.

## The commands

Each ran in a copy of the clone, with `CARGO_TARGET_DIR` outside it, on a Linux x86_64 host with
rustc 1.100.0.

- `cargo build` passes.
- `cargo test`: 80 unit tests and 2 doctests pass.
- `cargo +1.88 test`, the declared minimum: the same 80 and 2 pass.
- `cargo doc --no-deps`, and again with `RUSTDOCFLAGS="-D warnings"`: both pass.
- `cargo clippy --all-targets` passes with no warning.
- `cargo build --target x86_64-unknown-none`, `riscv64imac-unknown-none-elf` and
  `aarch64-unknown-none-softfloat`: all pass.
- `cargo run --example host_ring` prints `received 60 bytes` and `sent 42 bytes`.
- `cargo package --list --allow-dirty` lists 73 files, among them `.github/`, `.githooks/`,
  `.cargo/mutants.toml`, `deny.toml`, `_typos.toml`, `CODEOWNERS` and `falsifications/` (P1-1);
  `fuzz/` and `tests/qemu-smoke/` are separate packages and are not listed.
- `grep -rn '# Errors' src` prints nothing (P1-3).
- The crate has no features, so there is no feature combination to build.

## The comparators read

Each `.crate` from crates.io at the version in the prior-art table, unpacked into its own
directory and read. The measurement used the crates.io API with the User-Agent
`release-review-lane`, on 2026-11-26 (UTC).

- `ixgbe-driver` 0.1.1: `IxgbeHal` (`src/hal.rs`) is an `unsafe trait` with `dma_alloc`,
  `dma_dealloc`, `mmio_phys_to_virt` and a wait. `IxgbeDevice<H, const QS: usize>`
  (`src/ixgbe.rs`) owns its queues and reads its registers with `read_volatile` at
  `self.addr + reg` (`get_reg32(reg: u32)`). `NicDevice` (`src/lib.rs`) has `receive_packets`
  with a closure, `send(queue_id, IxgbeNetBuf)`, `get_mac_addr() -> [u8; 6]` and
  `get_link_speed`. `IxgbeError` derives only `Debug`. Five dependencies, `smoltcp` 0.12 among
  them.
- `eth-intel` 0.2.4: an e1000 driver over `dma-api` and `mmio-api`; `Regs::read(offset: usize)`
  over a `NonNull<u8>` (`src/e1000/registers.rs`); `Error` (`src/err.rs`) derives
  `thiserror::Error` and has an `Other(&'static str)` variant.
- `e1000-driver` 0.1.0: the 8254x, with registers as `&'static mut [Volatile<u32>]`, rings as
  borrowed slices, a `Vec` of buffers and a `KernelFunc` trait for coherent allocation
  (`src/e1000/e1000.rs`).
- `eth-igb` 0.1.1: the igb family over `dma-api`, `tock-registers` and `mbarrier`; `DError`
  (`src/err.rs`) with `Unknown(&'static str)`.
- `virtio-drivers` 0.13.0: `Hal` (`src/hal.rs`) is an `unsafe trait` with `dma_alloc`, `share`
  and `unshare`; `VirtIONetRaw` (`src/device/net/dev_raw.rs`) owns its transport and has
  `unsafe fn transmit_begin` and `receive_begin` over caller buffers; `FakeTransport` is
  `#[cfg(test)]` (`src/transport/mod.rs`); `Error` derives `thiserror::Error`; features `alloc`
  and `embedded-io`; depends on `safe-mmio`.
- `axdriver_net` 0.2.0: `NetDriverOps` (`src/lib.rs`) over `ixgbe-driver` and an `fxmac` driver,
  with its own `NetBuf` pool.
- `smoltcp` 0.14.0: `phy::Device` (`src/phy/mod.rs`) with `receive` and `transmit` returning
  tokens, and `RxToken::consume` and `TxToken::consume(len, f)` lending the frame to a closure.
- `embassy-net-driver` 0.2.0: `Driver` (`src/lib.rs`) with `receive`, `transmit`,
  `link_state`, `capabilities` and `hardware_address`, and the same token shape.

## The systems outside Rust

- Linux v6.12, `drivers/net/ethernet/intel/e1000e/` (`netdev.c`, `e1000.h`, `hw.h`, `regs.h`):
  `struct e1000_ring` holds the descriptor memory, its bus address and the `tail` register
  together. `e1000_alloc_rx_buffers` writes the receive tail once per `E1000_RX_BUFFER_WRITE` (16)
  buffers after a `wmb`. `e1000_clean_rx_irq` reads the status with a `dma_rmb` before the
  descriptor and copies frames shorter than `copybreak`. `er32` and `ew32` read and write an
  offset from `hw_addr`, and `hw.h` declares function tables for the MAC, the PHY and the NVM.
  GPL; read for its interface shape only.

## The benchmark

A scratch crate depending on the crate's copy by path, built with `cargo build --release` and run
three times. The region is a `Vec<u8>` of `layout::DIRECT_MEMORY_ACCESS_REGION_BYTES`; the tails
store two integers through `black_box`, and the barrier is `compiler_fence(SeqCst)`. Inputs: a
60-byte and a 1514-byte frame, `out` of 2048 bytes. Each column starts at 64 repeats and doubles
until a pass lasts 50 ms, then runs seven passes and reports the lowest divided by the repeats, with
`black_box` on the frame, `out` and each result.

- Transmit and completion: `DataPlane::transmit`, then the fake device's read and write of the
  status word that sets `DD`.
- Device write and receive: the fake device's copy of the frame into the slot at
  `receive_cursor` and its status word, then `DataPlane::receive`, asserted to return the length.
- Device write alone: the fake device's part of the second column, timed by itself.

## What was not run

- No comparator benchmark: `virtio-drivers`' `FakeTransport` is behind `#[cfg(test)]`, and
  `ixgbe-driver` needs a mapped BAR and a device that answers its bring-up.
- No device: the benchmark measures the data plane's own work against memory, not a bus.
- Kani, mutation testing and the fuzz targets were not run.
- FreeBSD's `sys/dev/e1000` was not read beyond the function names the crate cites.
