# What the review read and ran

An appendix to [the milestone](../1146-extensible-host-controller-interface-release-review.md).

## The crate

`partsfoundry/extensible_host_controller_interface` at
`a10790e1557aa761b889663f68c8a3541d0c5402`, version 0.1.0-pre.4 with `publish = false`, edition
2024, `rust-version` 1.85, no dependencies and no features. Read in full: `src/lib.rs`,
`src/ring.rs`, `src/transfer_request_block.rs`, `src/transfer_request_block_type.rs`,
`src/event.rs`, `src/completion.rs`, `src/registers.rs`, `src/extended_capabilities.rs`,
`src/context.rs`, `src/port.rs`, `src/direct_memory_access.rs`, `examples/fake_controller.rs`,
`Cargo.toml`, `README.md`, `CHANGELOG.md` and `docs/stranger-test-run-2026-11-11.md`; `src/tests.rs`
and `src/verification.rs` read for what they cover. The 13 Kani harnesses, the 13 falsification
patches and the three fuzz targets were listed, not run.

## The commands

On a read-only export of `main` at that commit:

- `cargo build`, `cargo test` (45 unit tests and 3 documentation tests, all passed),
  `cargo doc --no-deps` and `cargo clippy --all-targets -- -D warnings`: clean.
- `cargo build --target <t>` for `x86_64-unknown-none`, `aarch64-unknown-none-softfloat` and
  `riscv64imac-unknown-none-elf`: clean.
- `cargo +1.85 build`: clean.
- The benchmark of the block's measured-performance section: a bench crate outside the
  repository that depends on this crate and on `xhci` 0.9.2 by path, built with
  `cargo build --release` and run once, each operation timed over 10,000,000 iterations, best of
  seven.

## The measurements

`GET /api/v1/crates/<name>` and `GET /api/v1/crates/<name>/reverse_dependencies` on crates.io,
2026-11-26 (UTC), with a generic User-Agent, for every crate in the prior-art table, and
`GET /api/v1/crates?q=xhci` to find the ranked crates. The 90-day figure is the API's
`recent_downloads`.

## The comparators read

Each `.crate` from crates.io at the version in the prior-art table, unpacked and read.

- `xhci` 0.9.2: `Registers::new` as an `unsafe fn` over an `accessor::Mapper`; each TRB a private
  `[u32; 4]` behind `into_raw` and `TryFrom<[u32; 4]>`; `completion_code() -> Result<CompletionCode,
  u8>`; eight event types in `event::Allowed`, among them `HostController`; `transfer::Direction`;
  `addressing_capability` on `HCCPARAMS1`; `trb_transfer_length` over bits 0 to 16. No
  `#[non_exhaustive]` anywhere. Run in the benchmark.
- `crab-usb` 0.12.1: a host stack over `xhci` 0.9, `dma-api` and `tock-registers`, with errors
  through `thiserror` and `anyhow`; `ConvertXhciError` maps completion codes to `TransferError`;
  `TrbRing::enque_trb` and `next_index` in `src/backend/kmod/xhci/ring.rs` advance with no full
  check. Read, not built.
- `usb-host` 0.1.3: the crates.io record only; it is host driver traits with no controller.

## The systems read

Fetched as raw files at the named tag or commit and read, not run.

- Linux v6.17, `drivers/usb/host/`: `xhci.h` (`COMP_*` codes, `TRB_LEN`, `TRB_MAX_BUFF_SIZE`,
  `TRB_HC_EVENT`), `xhci-caps.h` (`HCC_64BIT_ADDR`), `xhci.c` (the DMA mask from that bit),
  `xhci-ring.c` (`xhci_handle_event_trb`, `xhci_num_trbs_free`, `prepare_ring`) and `xhci-hub.c`
  (`xhci_port_state_to_neutral`, `XHCI_PORT_RO`, `XHCI_PORT_RWS`).
- U-Boot v2025.10, `drivers/usb/host/xhci-ring.c` and `xhci.c`: the 64 KiB split of a buffer
  across TRBs.
- OpenBSD `sys/dev/usb/xhci.c` at its last change, `cd5896cffe` (2025-03-01), and `xhcireg.h`:
  `XHCI_HCC_AC64`, `XHCI_TRB_LEN`, `XHCI_TRB_MAXSIZE`, the event loop and its Host Controller
  Event `TODO`, and the `free_trbs` count.

## Not run

- Kani, the falsification patches, the fuzz targets and the mutation run: 1060 recorded them, and
  this review changes nothing they cover.
- `crab-usb` was not built.
- No run against a controller, in silicon or in QEMU.
