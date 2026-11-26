# What the review read and ran

An appendix to [the milestone](../1149-non-volatile-memory-express-release-review.md).

## The crate

`partsfoundry/non_volatile_memory_express` at `60b34280ecbba250ea4272984c5bcb3afe908e57`, version
0.1.0-pre.4, edition 2024, `rust-version` 1.85, no dependencies and no features. Read:
`Cargo.toml`, `README.md`, `CHANGELOG.md`, `examples/software_controller.rs`, and every module
under `src/` for its public items (`lib`, `capabilities`, `command`, `command_identifier_set`,
`completion`, `configuration`, `doorbell`, `identify`, `namespace`, `physical_region_page`,
`queues` and `registers`). The review listed `src/verification.rs`, `examples/qemu_driver.rs`,
`falsifications/`, `fuzz/` and `docs/` without reading them.

## The commands

Every command ran in a copy of the clone with its target directory elsewhere, so the clone stayed
clean. The host is Linux x86_64 with rustc 1.100.0.

- `cargo build` passes.
- `cargo test`: 57 unit tests, the example's 1 test, 13 doctests and 1 `compile_fail` doctest
  pass.
- `cargo +1.85 test`, the declared minimum: the same counts pass.
- `cargo doc --no-deps`, and again with `RUSTDOCFLAGS="-D warnings"`: both pass.
- `cargo clippy --all-targets` passes with no warning.
- The bare-target builds pass for `x86_64-unknown-none`, `riscv64imac-unknown-none-elf` and
  `aarch64-unknown-none-softfloat`.
- `cargo run --example software_controller` prints twelve reported heads and one refusal.
- `cargo build --example qemu_driver` passes; the example was not run.
- `cargo package --list --allow-dirty` lists 41 files: the source, the two examples, the eighteen
  falsification patches, the README, the changelog and the licenses. `docs/` is not among them
  (P2-7).
- `grep -rn '# Errors' src`, `grep -rn must_use src` and `grep -rn 'forbid\|deny(' src` each print
  nothing (P1-2, P1-3, P1-4). `grep -rn '# Panics' src` finds seven headings.
- The crate has no features, so there is no feature combination to build.

A probe crate, depending on the copy by path, printed the following.

- `doorbell(u16::MAX, Doorbell::CompletionHead, 15)` is `0x3fffe1000`, and a stride exponent of
  16 gives the offsets of 0 (P0-6).
- A `SubmissionQueue` assigned to a second binding and pushed there leaves the first one's tail
  at 0, and `size_of::<CommandIdentifierSet<1024>>()` is 8,192 (P0-3).
- `physical_region_page_pair(0x4000_0800, 4096, 16384)` returns one pointer and a zero second
  entry (P0-1).
- `physical_region_page_pair(0, (1 << 63) + 1, 1 << 63)` panics with an overflowing multiply in a
  debug build and returns `None` in a release build (P0-1).
- `Command::read` with a count of zero panics (P1-2).

## The comparators read

The review downloaded each comparator's `.crate` at the version the prior-art table gives, into
a directory of its own. It measured through the crates.io API on 2026-11-26 (UTC) as
`release-review-lane`. Searches by the keyword `nvme` and by name found the rows of the table
and no other driver. crates.io has no crate named `nvme-rs`, `nvme-core`, `nvme-types`,
`nvme-spec`, `nvme-device`, `nvmed`, `embedded-nvme`, `simple-nvme` or `nvme-oxide`.

- `nvme-driver` 0.8.2: `Nvme`, `Config`, `Namespace` and `NvmeBlockDriver` are the public surface
  (`src/lib.rs`), over `dma-api`, `mmio-api`, `mbarrier`, `rdif-block`, `tock-registers` and
  `log`. `NvmeReg` (`src/registers.rs`) is a `register_structs!` block; `begin_enable` checks the
  page size against the capabilities once, and `write_sq_y_tail_doolbell` computes the doorbell
  pointer and writes it. `CompleteQueue::complete` (`src/queue.rs`) issues `rmb`, reads the whole
  entry and then tests the phase; `NvmeCompletion::sq_head` is declared and never read; its
  `result` is a `u64`. `Identify::parse` implementations (`src/command.rs`) cast the byte slice to
  `*const u32` and to a `#[repr(C)]` struct inside `unsafe`. `Error` (`src/err.rs`) has `Display`
  and `core::error::Error` and an `Unknown(&'static str)` variant with 21 call sites. The I/O queue
  (`src/block/io_queue.rs`) keeps a free list of command identifiers and one list page per
  command.
- `tunnr-nvme` 0.1.1: a `std` driver over VFIO with `libc` as its one dependency. `Bar`
  (`src/bar.rs`) has `read32`, `write32`, `read64` and `write64` at a `usize` offset; `Mapper`
  (`src/memory.rs`) has `map` and `unmap`. `spec.rs` has the register offsets as `usize`
  constants, `sq_doorbell` and `cq_doorbell` taking a stride in bytes, a `Status` struct, the
  Identify parses and `prp_pages`, which returns `(u64, Vec<u64>)`. `cmd.rs` has `NvmeCommand`, a
  `#[repr(C, packed)]` struct with public fields, and over a dozen builders, among them
  `set_num_queues`, `write_zeroes`, `io_write_fua` and the two queue deletions. `QueuePair`
  (`src/queues.rs`) reads dword 3, tests the phase, fences and then reads the entry, and records
  `sq_head % depth`. `fake.rs`, under the `fake` feature, exports `FakeNvme` and `FakeMapper`.
  `Error` (`src/lib.rs`) has five `String` variants.
- `nvme` 0.0.0: the API reports six versions, 0.1.0 to 0.2.2, all yanked, so no source was read.
- `nvme-cli-sys` 1.0.0: generated bindings (`src/bindings.rs`) to Linux's ioctl structures, with
  no driver logic; a neighbor.
- `libnvme` 0.9.0: bindings to a Linux C library, host only; measured, and its source listed but
  not read.
- `vroom` 0.1.0 on crates.io describes itself as Vim macros from the shell. The measurement that
  set the order took it for the NVMe driver of that name; it is not.

## The systems outside Rust

- Linux v6.12, `drivers/nvme/host/pci.c`, `drivers/nvme/host/core.c` and `include/linux/nvme.h`,
  fetched from the tagged tree. `nvme_cqe_pending` reads the status word alone and tests the
  phase, and `nvme_poll_cq` issues `dma_rmb` before `nvme_handle_cqe` reads the rest.
  `nvme_handle_cqe` looks the command identifier up in the tag set and warns on an unknown one; it
  passes `sq_head` to a trace point and nowhere else. `nvme_write_sq_db` writes
  `dbs[qid * 2 * db_stride]` and skips writes while a batch is open. `struct nvme_completion`
  holds a 64-bit result union, and every multi-byte field is a `__le` type.
  `NVME_PCI_MAX_QUEUE_SIZE` is 4095 and `io_queue_depth` defaults to 1024. `nvme_set_queue_count`
  runs before the driver creates an I/O queue. GPL; read for its interface shape only.

## The benchmark

A scratch crate depending on the crate's copy by path and on `tunnr-nvme = "=0.1.1"`, built with
`cargo build --release` and run three times. Each row starts at 64 repeats and doubles until a
pass lasts 50 ms, then runs seven passes and reports the lowest divided by the repeats, with
`black_box` on every input and result.

- Pointers for 4 KiB: `physical_region_page_pair(0x4000_0800, 4096, 4096)` against
  `spec::prp_pages` with the same arguments followed by `spec::prp_fields`.
- Pointers and list for 128 KiB: `physical_region_page_list(0x4000_0800, 131072, 4096, list,
  0x9000)` into a `[u64; 512]`, against `spec::prp_pages` followed by the copy of each entry into
  a byte page with `to_le_bytes`, as `QueuePair::push` does, and `spec::prp_fields`.
- One Read command: `Command::read` against `cmd::NvmeCommand::io_read`, same fields.
- One whole round, the crate alone: `CommandIdentifierSet::<1>::acquire`,
  `Namespace::transfer_command`, `SubmissionQueue::push` on a 64-entry ring, a copy of the command
  into a `Vec` of slots, then a completion built for that command and passed through
  `is_phase_tag_set`, `from_dwords`, `is_owned`, `release`, `record_head` and `pop`.

## What was not run

- No whole-round comparator ran: `tunnr-nvme`'s `QueuePair` methods are private and reach memory
  through its `Mapper`, and `nvme-driver` needs a mapped register block and its DMA domain.
- No device and no QEMU run: the benchmark measures arithmetic against host memory.
- Kani, mutation testing and the fuzz targets were not run.
- SPDK and the Redox driver were not read.
