# What the review read and ran

An appendix to [the milestone](../1142-designware-mobile-storage-release-review.md).

## The crate

`partsfoundry/designware_mobile_storage` at `ac950346f360fa260ef23e3601738376f9ea66f1`,
version 0.1.0-pre.3. Read: `Cargo.toml`, `README.md`, `CHANGELOG.md` and every module under
`src/` (`host_controller`, `sd`, `card`, `command`, `internal_direct_memory_access`,
`registers`, `exported_simulator` and `proofs`), with the simulator read for its types only.

## The commands

- `cargo build --lib --target riscv64imac-unknown-none-elf` passes.
- `cargo build --lib --target riscv64imac-unknown-none-elf --features simulator` fails with 320
  errors (missing `derive`, `assert` and `vec`), since the feature turns off `no_std` and the
  bare target has no std (P1-1).
- `grep -c 'kani::proof' src/proofs.rs` prints 22 (P1-2).

## The comparators read

Each `.crate` from crates.io at the version in the prior-art table, unpacked and read.

- `embedded-sdmmc` 0.10.0: an SD card in SPI mode over `embedded-hal`, with a FAT volume manager
  above it and `BlockDevice` from `embedded-sdmmc-types`.
- `embedded-sdmmc-types` 0.1.0: `BlockDevice` with `read(&self, &mut [Block], BlockIdx)`,
  `write(&self, &[Block], BlockIdx)` and `num_blocks`, its error type bound by
  `core::error::Error`. The methods take `&self`, so an adapter over `&mut HostController` needs a
  cell.
- `block-device-driver` 0.2.0: an async `BlockDevice<const SIZE: usize>` with an alignment type.
- `sdmmc-protocol` 0.5.4 and `dwmmc-host` 0.4.2: the card protocol over the `sdmmc_host::SdMmcHost`
  trait, and the controller behind it. `dwmmc-host` opens with `pub unsafe fn new(base:
  NonNull<u8>)`, states that block I/O uses the internal engine only and completes through
  acknowledged interrupts, takes its region from `dma-api`, and supports UHS-I and HS200 clocking,
  which this crate does not.
- `simple-sdmmc` 0.1.1: the same controller. `read_block`, `write_block`, `read_blocks` and
  `write_blocks` `unwrap` the command's result; `read_blocks_dma` and `write_blocks_dma` divide
  the length by the block size and cast `buf.as_ptr()` to `u32`, under a comment that the virtual
  address must equal the physical.
- `sdio-host` 0.9.0 and `sdio` 0.5.3: card register types, for the neighbor role.
- `sdmmc` 0.1.0: measured, not read.

## The systems outside Rust

- Linux v6.12, `drivers/mmc/host/dw_mmc.c`: `dma_map_sg` maps the request's own pages for the
  engine, `dw_mci_ops` fills `mmc_host_ops` between the card core and the controller, and
  `dma_64bit_address` selects the 64-bit descriptor format.
- U-Boot v2025.10, `drivers/mmc/dw_mmc.c`: `bounce_buffer_start` around each engine transfer, both
  descriptor formats, and `dm_mmc_ops` between the card layer and the controller.

Both are GPL; the review read them for their interface shape only.

## What was not run

- No benchmark: the throughput question (P2-2) needs a board, and the simulator models no bus
  timing.
- Kani was not run; the harness count is from source.
- The review built and ran no comparator.
