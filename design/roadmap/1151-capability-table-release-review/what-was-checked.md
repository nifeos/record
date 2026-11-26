# What the review read and ran

An appendix to [the milestone](../1151-capability-table-release-review.md).

## The crate

`partsfoundry/capability_table` at `a0e8b159e550943828d4ddb61137e53a2c2cd631`, version 0.1.0,
edition 2024, `rust-version` 1.85, no dependencies, one feature (`peak`) and `publish = false`.
Read: `Cargo.toml`, `README.md`, `CHANGELOG.md` and all of `src/lib.rs` above the proofs, which is
every public item. The review read `src/tests.rs` and the twelve Kani harnesses for their names
only, and listed `falsifications/` and `docs/` without reading them.

## The commands

A Linux x86_64 host with rustc 1.100.0 ran each one in a copy of the clone, building outside it.

- `cargo build` and `cargo build --features peak` pass.
- `cargo test`: 28 unit tests and 2 doctests pass. The crate's development dependency on itself
  turns `peak` on for every test run, so `cargo test --no-default-features` runs the same 28 and 2.
- `cargo +1.85 test`, the declared minimum: the same 28 and 2 pass, and
  `cargo +1.85 build --lib --target x86_64-unknown-none` passes.
- `cargo doc --no-deps`, and again with `RUSTDOCFLAGS="-D warnings"` and `--features peak`: both
  pass.
- `cargo clippy --all-targets` passes with no warning. With `-W clippy::pedantic` it reports seven
  functions with no `# Errors` section and eleven that could carry `#[must_use]` (P1-4).
- `cargo build --lib --target x86_64-unknown-none`, `riscv64imac-unknown-none-elf` and
  `aarch64-unknown-none-softfloat`, each with and without `--features peak`: all six pass.
- `cargo package --list --allow-dirty` lists 50 files, among them `.github/`, `.githooks/`,
  `.cargo/mutants.toml`, `deny.toml`, `_typos.toml`, `CODEOWNERS` and `falsifications/` (P1-2).
- `cargo package --allow-dirty`, with `publish = false` removed in the copy, fails: `no matching
  package named capability_table found`, required by the crate itself (P1-1). With the `version`
  key also removed from the development dependency, it verifies, and `cargo test` passes as above.
- `grep -n '# Errors' src/lib.rs` and a search for `forbid` and `must_use` print nothing.
- The feature combinations are two, with and without `peak`, and both build on every target above.

## The comparators read

The review took each `.crate` at the prior-art table's version, unpacked it apart and read it.
The download figures are the crates.io API's on 2026-11-26 (UTC). Searches there for a capability
table, a handle table, `cspace`, `cnode`, `zircon`, `sel4` and the keywords `capability` and
`capabilities` find no other library that holds such a table.

- `ruvix-cap` 0.1.0: `CapabilityTable<const N: usize = 1024>` (`src/table.rs`) holds an array of
  `CapTableEntry`, each with public fields for the capability, a generation, a validity flag, an
  owner, a depth and a parent. It has `allocate_root`, `allocate_derived`, `lookup` returning
  `&CapTableEntry`, `lookup_mut`, `deallocate`, `capacity`, `len`, `is_empty`, `is_full` and an
  `iter` that returns `impl Iterator`. It finds a free slot by a scan from a hint. A stale
  generation answers `StaleHandle`. `CapError` (`src/error.rs`) derives `Debug`, `Clone`, `Copy`,
  `PartialEq` and `Eq`, has twelve variants and `as_str`, and implements neither `Display` nor
  `core::error::Error`. `DerivationTree::revoke` (`src/derivation.rs`) returns the count revoked.
  `src/lib.rs` carries `#![forbid(unsafe_code)]`. Features: `alloc`, `std`, `audit-log` and
  `metrics`.
- `ruvix-types` 0.1.0: `CapRights(u32)` (`src/capability.rs`) with seven rights, `from_bits` that
  keeps every bit, `bits`, `contains`, `union`, `intersection`, `difference`, `is_subset_of`,
  `Default`, `Hash` and the `|` and `&` operators. `Capability` has five public fields and a
  `new`, and `derive` returns `Option<Self>`, refusing without `GRANT` or on a wider request.
  `CapHandle` wraps an index and a generation.
- `sel4` 0.0.12: `SlotRef` (`src/cspace.rs`) with `copy`, `mint`, `delete` and `revoke`, each a
  call into the kernel through `sel4-sys`. It holds no table of its own.
- `fuchsia-zircon` 0.3.3: `Rights` (`src/rights.rs`) is a `bitflags` type over `zx_rights_t`;
  `Handle::replace` and `HandleRef::duplicate` (`src/handle.rs`) take the new rights and call the
  kernel.
- `slotmap` 1.1.1: `SlotMap` (`src/basic.rs`) with `insert`, `get` returning `Option<&V>`,
  `remove` returning `Option<V>`, `retain`, `len` and `capacity`. Features: `std`, on by default,
  and `unstable`.
- `bitflags` 2.13.2: the `Flags` trait (`src/traits.rs`) with `from_bits` returning
  `Option<Self>`, `from_bits_truncate`, `from_bits_retain`, `bits`, `contains`, `union` and
  `intersection`. Features: `std`, `serde` and `example_generated`.
- `cap-std` 4.0.3: the review measured it and did not read it.

## The systems outside Rust

- seL4 13.0.0, fetched by tag: `src/object/cnode.c`, `include/object/structures.h`,
  `src/kernel/cspace.c` and `libsel4/mode_include/64/sel4/shared_types.bf`. A slot is a `cte_t`,
  a capability beside an `mdb_node_t` that links it into the derivation list. `cteInsert` asserts
  that the destination is empty and links the new slot after its source. `cteRevoke` deletes each
  following slot that `isMDBParentOf` accepts, with a preemption point between them. `lookupSlot`
  resolves an address through `resolveAddressBits`. `seL4_CapRights` has four bits: grant-reply,
  grant, read and write. GPL; read for its interface shape only.
- Zircon, the head of `releases/f20` at commit `639288a04e0b7f4b8dd6205c93350813979a9802`:
  `zircon/kernel/object/handle_table.cc`, `zircon/kernel/object/include/object/handle_table.h`,
  `zircon/kernel/object/include/object/handle.h` and `zircon/system/public/zircon/rights.h`.
  `HandleTable` keeps a locked list of handles and a count. A handle value is the handle's arena
  index shifted and mixed with a per-table random word, with its low bits fixed.
  `RemoveHandle` returns the `HandleOwner`. `Handle` holds a `RefPtr<Dispatcher>` and a `const`
  rights word. `rights.h` defines 25 rights and `ZX_RIGHT_SAME_RIGHTS` in a `uint32_t`.

## The benchmark

A scratch crate depending on the crate's copy by path, on `ruvix-cap` at `=0.1.0` and on `slotmap`
at `=1.1.1`, built with `cargo build --release` and run three times. Each table has room for 256
and holds 128 entries, inserted before the timed part. The entries are a `Capability<u64>` with
`READ` and `GRANT` here, a `ruvix-types` `Capability` with the same two rights placed by
`allocate_root`, and a `(u64, u32)` in a `SlotMap` made with `with_capacity(256)`. Each row starts
at 64 repeats and doubles until a pass lasts 50 ms, then runs seven passes and reports the lowest
divided by the operations, with `black_box` on each slot, key, value and result.

- Look up one of 128: `get`, `lookup` and `SlotMap::get` on each of the 128 in turn.
- Look up and derive: `CapabilityTable::derive(slot, READ)` here; `lookup` then
  `Capability::derive(READ, 0)` for `ruvix-cap`. `slotmap` has no such operation.
- Insert one, then delete it: `insert` then `delete`; `allocate_root` then `deallocate`; `insert`
  then `remove`. One pair counts as one operation.
- Insert 128 more, then delete them: 128 inserts into the half-full table and 128 deletions,
  divided by 256.
- Iterate: `iter` over the 128, summing a word of each entry, divided by 128.

`size_of` gives 4,136 bytes for `CapabilityTable<u64, 256>` and 14,352 for `ruvix-cap`'s
`CapabilityTable<256>`.

## What was not run

- The review read seL4 and Zircon and built neither.
- No benchmark of `delete_matching`, `insert_at` or `insert_at_or_above`, which no comparator
  matches like for like.
- No benchmark with the `peak` feature on, so the cost of its atomic write on growth is not
  measured.
- Kani, mutation testing and the falsification patches were not run.
- The host has no 32-bit target, so the review read the slot conversions and built none for one.
