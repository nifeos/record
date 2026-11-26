# What the review read and ran

An appendix to [the milestone](../1153-address-space-layout-release-review.md).

## The crate

`partsfoundry/address_space_layout` at `9568826fc8bdcc07a44b6e227042a5483753a5d1`, version 0.1.0,
no tag, a fresh clone of `main`. The census of milestone 1129 (the combine review) counted the
same commit. The lane read in full: `Cargo.toml`, `README.md`, `CHANGELOG.md`, `docs/stranger-test.md`,
`src/lib.rs` (643 lines, its tests included) and `.github/mutants-exempts`. It read
`src/verification.rs` for the harness list and the module documentation, and
`.github/workflows/ci.yml`.

## The commands

The lane ran these on a Linux x86_64 host with rustc 1.100.0 and `CARGO_TARGET_DIR` outside the
clone. `git status --short` showed the clone clean afterward.

- `cargo build` passes.
- `cargo test` passes: 10 unit tests and 3 doctests.
- `RUSTDOCFLAGS="-D warnings" cargo doc --no-deps` passes with no warning.
- `cargo clippy --all-targets` passes with no warning.
- `cargo build --lib --target <target>` passes for `riscv64imac-unknown-none-elf`,
  `aarch64-unknown-none-softfloat` and `x86_64-unknown-none`.
- `cargo package --list --allow-dirty` lists 49 files, 20 of them under `.github/`, `.githooks/`
  or named `.gitignore` (P2-5).
- `grep -c 'kani::proof' src/verification.rs` prints 11, and `falsifications/` holds 11 patches,
  as the README says.
- `grep -n '# Panics\|# Errors' src/lib.rs` prints nothing, and `# Examples` appears at lines 96,
  231 and 334 (P1-3).
- The crate declares no features, so there is one feature combination.

A scratch program that depends on the crate by path and on `memory_addr` at `=0.4.1` printed:

- `check_image(IMAGE.start + 1, IMAGE.start + 2)` is `Ok(())` (P0-4).
- `{:?}` of `IMAGE` is `Band { start: 1610612736, end: 2130706432 }`, and `{:?}` of
  `memory_addr::va_range!(0x6000_0000usize..0x7f00_0000usize)` is `VA:0x60000000..VA:0x7f000000`
  (P2-2).
- `Band { start: 0x2000, end: 0x1000 }` compiles, `contains(0x1800)` on it is false, and `bytes()`
  panics with "attempt to subtract with overflow" in a debug build (P0-1).
- `service_window(SERVICE_WINDOWS.end - PAGE_BYTES)` returns `0x5ffff000` (P0-2).
- `check_image(IMAGE.start, IMAGE.start)` refuses an empty image as `OutsideBand`.

## The search for a comparator

On 2026-11-26 (UTC), `https://crates.io/api/v1/crates?q=<words>&sort=recent-downloads&per_page=8`
for each of: "address space layout", "memory layout", "memory map", "virtual address", "address
range", "memory region", "memory-addr" and "linker script memory". No result publishes one
system's process layout. The results that hold an address or a range type became the neighbors.
The lane measured `static_assertions` 1.1.0, `const_panic` 0.2.17 and `rangemap` 1.9.0 and set
them aside. The first two build compile-time assertions of any kind, and the third maps ranges to
values.

## The neighbors read

The lane downloaded the four neighbors' `.crate` files from `static.crates.io`, at the versions
the block's table gives, and unpacked each apart from the others.

- `memory_addr` 0.4.1, `src/range.rs`, `src/addr.rs` and `src/lib.rs`. `AddrRange<A>` has public
  `start` and `end`. Its `new` is not `const` and panics when `start > end`, `try_new` returns
  `Option`, and `new_unchecked` is a `const unsafe fn`. Its methods are `is_empty`, `size`,
  `contains`, `contains_range`, `contained_in` and `overlaps`. It has `TryFrom<Range<T>>` with
  `Error = ()`, `Default`, and `Debug`, `LowerHex` and `UpperHex` written by hand. An empty range
  is valid. No dependencies, `no_std`.
- `x86_64` 0.15.5, `src/addr.rs` and `src/structures/paging/page.rs`: `VirtAddr(u64)` with a
  private field, `const fn new` with a `## Panics` section and `const fn try_new` returning
  `Result<VirtAddr, VirtAddrNotValid>`; `VirtAddrNotValid(pub u64)` implements `Debug` and neither
  `Display` nor `Error`. `PageRange` has public `start` and `end`, derives `Clone`, `Copy`,
  `PartialEq`, `Eq` and `Hash`, has `is_empty`, `len` (pages) and `size` (bytes), and is an
  `Iterator`. Its manifest's features give the feature-name evidence.
- `vm-memory` 0.18.0, `src/region.rs`: the `GuestMemoryRegion` trait (`len`, `start_addr`,
  `last_addr`, `check_address`, `address_in_range`) and `GuestRegionCollection`, whose constructor
  returns `GuestRegionCollectionError::MemoryRegionOverlap` or `UnsortedMemoryRegions`; the error
  derives `thiserror::Error`. It needs `std` and allocates.
- `memory_addresses` 0.4.0: the lane measured and unpacked it and did not read it.

## The systems outside Rust

- FreeBSD release/14.3.0, `sys/amd64/include/vmparam.h`: `VM_MAXUSER_ADDRESS`, `SHAREDPAGE` (one
  page below it) and `USRSTACK` (equal to `SHAREDPAGE`), each as a macro with a variant for each
  paging depth.
- Linux v6.12, `Documentation/arch/x86/x86_64/mm.rst` (the table of the whole address space, with
  user space as one row "different per mm"), `arch/x86/include/asm/page_64.h` and
  `arch/x86/include/asm/processor.h` (`TASK_UNMAPPED_BASE` as a third of the task size).
- seL4 13.0.0, `libsel4/sel4_arch_include/x86_64/sel4/sel4_arch/constants.h`: `seL4_UserTop`
  (`0x00007ffffffff000`) and `seL4_PageBits`, and nothing below the top.

The Linux files are GPL; the review read them for the shape of what they publish only.

## The benchmark

None, and none is owed: every checked placement is a `const fn` bound in a `const`, and
`check_image` is three comparisons run once for each image.

## What the lane did not run

- Kani and the falsification replay; the harness and patch counts are from the source.
- Mutation testing.
- The build at the minimum Rust version, 1.88; the baseline's stranger run covers it.
- The tests of the neighbors.
