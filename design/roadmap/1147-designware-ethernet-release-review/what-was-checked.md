# What the review read and ran

An appendix to [the milestone](../1147-designware-ethernet-release-review.md), at
`partsfoundry/designware_ethernet` commit `565b331f07394c256b6d186b74c94b94598aca29`.

## The crate

Every file under `src/`, the README, the CHANGELOG, `Cargo.toml`, `docs/stranger-test.md` and the
six patches under `falsifications/`. The public surface is eight modules: `bring_up`,
`cache_coherence`, `link`, `management_data_io`, `motorcomm_physical_layer_device`,
`network_interface_controller`, `registers` (four public constants) and `layout`, with
`Hardware`, `DirectMemoryAccessRegion`, `Tails` and `DataPlane` at the root. The crate contains
no `unsafe`, declares no features and has no dependencies.

## The measurements

Run in a clean export of the commit above, on an x86_64 Linux host:

- `cargo build` and `cargo clippy --all-targets`: clean.
- `cargo test`: 98 tests and one doctest pass.
- `cargo build --target riscv64imac-unknown-none-elf` and
  `cargo build --target aarch64-unknown-none-softfloat`: clean.
- `cargo kani` (Kani 0.68.0): six of six harnesses verified, each in about 0.15 s.
- `cargo package --list`: the list P2-1 names.
- `cargo doc --no-deps`: clean. `RUSTDOCFLAGS="-D warnings" cargo doc --no-deps`: four errors, the
  links to private items of P1-4.
- The benchmark: a bench crate outside the repository depending on the export by path, run with
  `cargo run --release`. It made four runs of 2,000,000 frames at 60 and 1514 bytes, over ordinary
  memory implementing `DirectMemoryAccessRegion`, with a simulated device completing each
  descriptor. A bare `copy_from_slice` loop beside it measured 2.6 to 3.4 ns at 60 bytes and 20 to
  24 ns at 1514 bytes. At 1514 bytes receive measured below it, so the loop is no reliable floor,
  and the block does not subtract it.
- crates.io downloads: the crates.io API on 2026-11-26 (UTC), each crate's `downloads`,
  `recent_downloads` (90 days) and reverse-dependency count. Searches for `dwmac`, `stmmac`,
  `designware`, `eqos`, `gmac`, `synopsys ethernet`, `yt8531` and `motorcomm` found no other
  driver for this controller.

## The comparators read

Each from its published crate at the version in the block's table:

- `stm32-eth` 0.8.2: the ring and packet types, the `smoltcp-phy` feature, the `Miim`
  implementation, the error types and every `unsafe` use.
- `embassy-stm32` 0.6.0: `eth/mod.rs`, `eth/v2/` (descriptors, receive and transmit) and
  `eth/generic_phy.rs`.
- `esp-emac` 0.5.0: the `Emac` type, its configuration, `EmacError` and the `embassy_net` module.
- `dwmac-my` 0.2.0: the `DwmacHal` trait, the driver and its physical layer device registers.
- `esp-p4-eth` 0.1.0: the `embassy-net-driver` implementation.
- `smoltcp` 0.14.0: `phy::Device`, `RxToken`, `TxToken` and `wire::EthernetAddress`.
- `embassy-net-driver` 0.2.0: `Driver` and `HardwareAddress`.
- `ieee802_3_miim` 0.10.0 and `mdio` 0.1.2: the MDIO traits.

## The systems outside Rust

- Linux v6.12: `drivers/net/ethernet/stmicro/stmmac/` (`stmmac_main.c`, `dwmac4_descs.c`, `dwmac4_lib.c`,
  `common.h`) and `drivers/net/phy/motorcomm.c`.
- U-Boot v2025.10: `drivers/net/dwc_eth_qos.c`.
- OpenBSD at `59ec3ab4d107`: `sys/dev/ic/dwqe.c`.

## Not run

- The comparative benchmark against `stm32-eth`, which builds only for an STM32 target with a chip
  feature and drives the 3.x descriptors.
- Any run on a board; that is the open item of milestone 1074 (what an outside maintainer would fix).
- Mutation testing, which the crate repository runs in its merge queue.
