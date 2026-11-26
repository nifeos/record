# What the review read and ran

An appendix to [the milestone](../1144-device-tree-blob-release-review.md).

## The crate

`partsfoundry/device_tree_blob` at `9ed5c2a970f2c4d81ee75d49cb0e94c1df4ad985`, version 0.1.0,
the head of its `main`. Read: `Cargo.toml`, `README.md`, `CHANGELOG.md`, all of `src/lib.rs`
(1,429 lines, with the nine Kani harnesses read for what they prove) and the three test files,
`tests/hostile.rs`, `tests/qemu_aarch64_virt.rs` and `tests/qemu_riscv64_virt.rs`. The review
left the clone as it found it; every build wrote to a target directory outside it.

## The commands

- `cargo build` passes.
- `cargo test` passes: 1 unit test, 46 in `hostile.rs`, 17 in `qemu_aarch64_virt.rs`, 10 in
  `qemu_riscv64_virt.rs` and 4 doctests.
- `cargo +1.88 test`, the declared minimum Rust version, passes the same tests.
- `RUSTDOCFLAGS="-D warnings" cargo doc --no-deps` passes.
- `cargo clippy --all-targets -- -D warnings` passes.
- `cargo build --lib --target` with `x86_64-unknown-none`, `aarch64-unknown-none-softfloat` and
  `riscv64imac-unknown-none-elf` passes on each.
- The crate declares no features, so there is no combination to build.
- `cargo package --list --allow-dirty` lists the repository's hooks, workflows, templates,
  `_typos.toml`, `deny.toml`, `rustfmt.toml`, `falsifications/` and `docs/stranger-test.md`
  beside the sources and fixtures, and leaves out `fuzz/` (P2-2).
- A scratch binary took `tests/fixtures/qemu-riscv64-virt.dtb` and replaced the final `FDT_END`
  token of its structure block with the value 10. On that blob, `from_bytes`
  returned the tree, `node_property(b"serial@10000000", b"compatible")` returned the 9-byte value,
  `boot_arguments` returned `Ok(None)` and `memory_regions` returned `Err(BadToken(10))` (P0-1).
  `fdt` 0.1.5's `Fdt::new` accepted the same blob.

## The benchmark

A scratch crate depending on the crate by path and on `fdt = "=0.1.5"` and
`fdt-rs = { version = "=0.4.5", default-features = false }`, built with `cargo build --release`
and run on a Linux x86_64 host, Intel Xeon Platinum 8160 at 2.10 GHz, 80 threads, rustc 1.100.0.

- Inputs: the crate's fixtures `qemu-riscv64-virt.dtb` (5,235 bytes, 34 nodes) and
  `qemu-aarch64-virt.dtb` (7,566 bytes, 57 nodes), copied into a `u32`-aligned buffer because
  `fdt-rs` requires one. All three crates read the same slice, and the program first checked
  that all three return the same `compatible` value and that `fdt` and `fdt-rs` count the same
  nodes.
- Parse: `DeviceTreeBlob::from_bytes`, `fdt::Fdt::new` and `fdt_rs::base::DevTree::new`, each
  returning whether it succeeded.
- Walk all nodes: `fdt`'s `all_nodes().count()` and `fdt-rs`'s `nodes().count()` over a parsed
  tree. The crate has no public walk, so its column is `node_property(b"no-such-node", b"x")`,
  which visits every token and returns `Ok(None)`.
- Node by name and read `compatible`: the node is `/soc/serial@10000000` on riscv64 and
  `/pl011@9000000` on aarch64. The crate calls `node_property` with the last path component;
  `fdt` calls `find_node` with the whole path, then `property("compatible")`; `fdt-rs` has no
  path lookup, so it scans `nodes()` for the last component's name and then the node's `props()`.
- The loop: start at 64 calls per pass and double until one pass lasts at least 50 ms, then run
  seven passes at that count and report the lowest pass divided by the count. Each input and each
  result passes through `std::hint::black_box`.

## The comparators read

Each `.crate` from crates.io at the version in the prior-art table, unpacked into its own empty
directory and read.

- `fdt` 0.1.5 (`src/lib.rs`, `src/node.rs`, `src/standard_nodes.rs`, `src/parsing.rs`):
  `Fdt::new` checks the magic and `totalsize` only. `FdtError` has `BadMagic`, `BadPtr` and
  `BufferTooSmall`, with `Display` and no `core::error::Error`. The walks are `all_nodes`,
  `find_node` with an alias fallback, `find_compatible`, `find_phandle` (reads only `phandle`),
  `children` and `properties`. `reg()` returns `None` above two cells. The source holds 49
  `unwrap`, `expect` or `panic!` sites outside `tests.rs`. One feature, `pretty-printing`.
  MPL-2.0.
- `dtoolkit` 0.5.0 (`src/lib.rs`, `src/error.rs`, `src/fdt.rs`, `src/fdt/node.rs`,
  `src/standard/*.rs`, `src/validate.rs`, `Cargo.toml`). `Fdt::new` and `Fdt::with_options` run
  `validate`, which walks the header, the reservation block and the structure block. It requires
  `totalsize` to equal the slice's length. `FdtOptions` has `strict_name_length` and `max_size`.
  `FdtParseError` carries an offset and a `#[non_exhaustive]` `FdtErrorKind`. A `Node` trait has
  `children`, `properties` and `child` (with the unit-address rule), beside `Fdt::find_node`.
  Every public constructor has `# Errors` and `# Examples`. Dependencies `zerocopy`, `zerocopy-derive`
  and `thiserror`; features `alloc`, `write`, `overlay`, `arrayvec07` and `heapless09`.
- `fdt-rs` 0.4.5 (`src/lib.rs`, `src/error.rs`, `src/base/tree.rs`, `src/base/iters.rs`,
  `src/base/node.rs`, `src/index/tree.rs`): `unsafe fn new` and `unsafe fn from_raw_pointer`
  whose callers guarantee alignment and length; `DevTreeError` exhaustive with `Display`;
  fallible iterators `nodes`, `props`, `compatible_nodes`; an optional index built into a
  caller's buffer. Seven dependencies; `std` on by default.
- `device_tree` 1.1.0 (`src/lib.rs`): an owned tree of `Vec` and `String`, `find(path)`.
- `dtb-walker` 0.2.0-alpha.3 (`src/lib.rs`, `src/walker.rs`): a callback walk, `walk(f)` with a
  `WalkOperation` return.
- `fdt-parser` 0.5.1 (`src/lib.rs`, `src/base/fdt.rs`, `src/base/node/mod.rs`,
  `src/cache/fdt.rs`): `extern crate alloc`, `all_nodes`, `find_nodes`, `get_node_by_path` in
  its cache; `FdtError` through `thiserror` with `BufferTooSmall { pos }`.
- `fdt-raw` 0.3.0 (`src/fdt.rs`): `all_nodes`, `find_by_path`.
- `flat_device_tree` 3.1.1 (`src/lib.rs`, `src/node.rs`): the `fdt` interface with
  `find_node`, `all_nodes` and `children`.
- `vm-fdt` 0.3.0: a writer, read for the neighbor role only.

## The systems outside Rust

- libfdt from dtc v1.7.2, `libfdt/fdt_ro.c`, `libfdt/fdt.c` and `libfdt/libfdt.h`.
  `fdt_path_offset`, `fdt_subnode_offset_namelen`, `fdt_next_node`,
  `fdt_first_property_offset` and `fdt_next_property_offset` use an offset as the node handle;
  `libfdt.h` declares `fdt_check_full`. libfdt is GPL-2.0-or-later or BSD-2-Clause; the review
  read it for its interface shape only.

## What was not run

- Kani and mutation testing were not run; the harness count is from source.
- The review ran no comparator's tests; the benchmark built and called `fdt` and `fdt-rs` only.
- The host has no `dtc` and exposes no device tree, so the review built no blob from source and
  measured no board's blob.
