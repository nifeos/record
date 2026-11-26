# The later items

An appendix to [the milestone](../1153-address-space-layout-release-review.md): the evidence for
its P2 findings, read in `partsfoundry/address_space_layout` at `9568826f`.

## P2-1. `window` has no form that returns a refusal

`window` asserts, which suits a `const`. A loader that places a window at an address it computes
at run time risks a panic, so it writes the `holds` call and the two alignment checks itself.
`x86_64` 0.15.5 pairs `VirtAddr::new` with `try_new`, and `memory_addr` 0.4.1 does the same for
`AddrRange`. The change is a `const fn` beside `window` that returns a `Result`, with `window`
calling it.

## P2-2. A `Band` prints its addresses in decimal

`{:?}` of `IMAGE` prints `Band { start: 1610612736, end: 2130706432 }`. `memory_addr` 0.4.1
writes `Debug`, `LowerHex` and `UpperHex` by hand and prints `VA:0x60000000..VA:0x7f000000`.
`ImagePlacement`'s `Display` already prints hexadecimal.

## P2-3. No conversion to or from `core::ops::Range<u64>`

`Band` is a half-open range with the fields of `core::ops::Range`. `memory_addr` 0.4.1 has
`TryFrom<Range<T>>`, with `()` as its error. The change is `From<Band> for Range<u64>` and a
`TryFrom` the other way with a real refusal.

## P2-4. No function answers which band holds an address

A fault handler with an address loops over `BANDS` to name its band. The crate's proofs carry a
private `band_index` that does so.

## P2-5. The manifest and the package

`cargo package --list --allow-dirty` lists 49 files, 20 of them under `.github/` or `.githooks/`
or named `.gitignore`. `Cargo.toml` has no `include` and no `documentation` key (C-METADATA).

## P2-6. A linker script cannot read the table

Inferred. The README lists a linker script among the programs that must agree. It cannot read a
Rust constant, so its owner restates `IMAGE_BASE_VIRTUAL_ADDRESS` and tests the two for equality.
FreeBSD and Linux keep the numbers in C headers, which the C preprocessor feeds to their linker
scripts. An example that prints the `. =` line for a build script would close the gap.

## P2-7. A checked address is a bare `u64`

`pair_page`, `window` and the `_VIRTUAL_ADDRESS` constants are `u64`. A function cannot ask its
caller for an address that passed a check, and a length can stand where an address belongs.
`x86_64` 0.15.5 and `memory_addr` 0.4.1 both wrap the address in a `VirtAddr`. Door D10 of the
block recommends no change at 0.1.0.
