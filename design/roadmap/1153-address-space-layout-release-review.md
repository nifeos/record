---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1076, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1153. `address_space_layout`: the release review's findings

*(The number and the slug are provisional.)*

The release review of `partsfoundry/address_space_layout` at commit `9568826f`, version 0.1.0 with
no tag, under milestone 1129 (the combine review), whose
[block](1129-crate-interfaces-best-in-class.md) sets its form. The baseline is milestone 1076 (what
an outside maintainer would fix before it leaves), [its block](1076-address-space-map-outside-review.md)
and the cleared package [`notes/crate-reviews/address-space-layout.md`](../../notes/crate-reviews/address-space-layout.md).
Every 1076 finding reads Done. The band numbers, the crate's name and the names the clearance
ratified stay closed, and no later rule of [design/naming.md](../naming.md) touches them. The
clearance kept the three one-page band functions; door D2 brings that back with evidence.

Reuse: the crate's own tests, and a scratch program that prints what five calls return.

## Finding status

- P0-1, a caller can build a `Band` that `Band::new` refuses: Open.
- P0-2, `runtime_window` and `service_window` check one page under a window's name: Open.
- P0-3, `ImagePlacement` is exhaustive and is not an error: Waiting on the errors decision of milestone 1129.
- P0-4, `check_image` accepts bounds that are not on a page: Open.
- P0-5, `LOW_HALF_SPLIT_SHIFTS` fixes the count of architectures in its type: Open.
- P0-6, `VERSION` and `INTERFACE_ID` are provisional names: Waiting on the contract-layout decision of milestone 1129.
- P0-7, eighteen public names carry no ruling: Open.
- P1-1, the documentation names items a stranger cannot find and never names the system: Open.
- P1-2, two public doc comments tell history: Open.
- P1-3, no `# Panics` or `# Errors` section, and no example on the crate page: Open.
- P1-4, `Band` and `ImagePlacement` have no `Hash`: Open.
- P1-5, no overlap check for the hazard the crate lists three times: Open.
- P1-6, no stated rule for what a changed band does to `VERSION` and to the crate's version: Open.
- P2-1, `window` has no form that returns a refusal: Open.
- P2-2, a `Band` prints its addresses in decimal: Open.
- P2-3, no conversion to or from `core::ops::Range<u64>`: Open.
- P2-4, no function answers which band holds an address: Open.
- P2-5, the manifest has no `documentation` key and the package ships the repository's CI files: Open.
- P2-6, a linker script cannot read the table: Open.
- P2-7, a checked address is a bare `u64`: Open.

## Open decisions

The one-way doors D1 to D10 below.

## Goal

A stranger who builds programs for the system this layout belongs to reads one page and knows
whose layout it is. The compiler refuses every wrong page or window, and a bad image gets a
refusal that is an ordinary Rust error. No caller of 0.1.0 holds a band or a window the crate's
own checks would refuse.

## What the review read and ran

[The appendix](1153-address-space-layout-release-review/what-was-checked.md) lists what the lane
read in the crate, its neighbors and three kernels, with each command's result.
[The guidelines table](1153-address-space-layout-release-review/api-guidelines.md) marks the 54
API Guidelines items, and [the later items](1153-address-space-layout-release-review/later-items.md)
hold the P2 findings in full.

## Prior art

Measured from the crates.io API on 2026-11-26 at 22:26 (UTC). A stranger brings this crate one
problem: where each kind of page goes in a process of one system. Eight searches of crates.io
found no crate that solves it, so no comparator ranks. The systems that solve it publish C
headers and a document, and those set the bar. The crates below are neighbors that offer a range
type like `Band`.

| crate or system | role | version read | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `x86_64` | neighbor: `VirtAddr` and `PageRange` | 0.15.5 | 6,135,383 | 1,070,518 | 86 | 2026-09-24 |
| `vm-memory` | neighbor: regions checked for overlap when built | 0.18.0 | 10,850,485 | 3,901,850 | 57 | 2025-12-11 |
| `memory_addresses` | neighbor: address newtypes, measured and not read | 0.4.0 | 185,454 | 25,744 | 3 | 2026-05-08 |
| `memory_addr` | neighbor: `AddrRange`, the nearest type to `Band` | 0.4.1 | 186,438 | 14,078 | 31 | 2026-10-19 |
| FreeBSD `sys/amd64/include/vmparam.h` | outside Rust | release/14.3.0 | | | | |
| Linux `Documentation/arch/x86/x86_64/mm.rst`, `arch/x86/include/asm/page_64.h` and `processor.h` | outside Rust | v6.12 | | | | |
| seL4 `libsel4/sel4_arch_include/x86_64/sel4/sel4_arch/constants.h` | outside Rust | 13.0.0 | | | | |

The review read the newest stable version of `x86_64` and `memory_addr`; each has a newer
pre-release. No integration target applies.

### What `address_space_layout` does better

- Than FreeBSD's and Linux's headers: one table for three architectures, which tiles its range
  with no gap under a `const` assertion and a Kani harness. Their macros are per architecture and
  unchecked.
- Than seL4's `constants.h`, which publishes the top of user space alone: this crate places the
  image, the stack, the heap and each class of shared window.
- Than `memory_addr`: `Band::new` and `window` are `const fn`, so a wrong band stops the build.
  `AddrRange::new` panics at run time and accepts an empty range.
- Than `x86_64`: `PageRange` has public fields and no checked constructor.
- Than `vm-memory`: no allocation and no `std`.
- Than all of them: eleven Kani harnesses, each with a patch that turns it red.

Linux and FreeBSD randomize the stack and the mapping base. The crate's BUGS section says it
gives that up.

## The items

Effort is S (half a day), M (a day or two) or L (longer). A one-way item binds every caller from
the first 0.1.0 tag, which is why the P0 items cannot wait. Line numbers are of `src/lib.rs`.

### P0: the 0.1.0 interface

#### P0-1. A caller can build a `Band` that `Band::new` refuses

Verified in source (lines 84 to 128) and by building. `Band::new` refuses an empty band, an
inverted one and one off a page, but the fields are public. A scratch program wrote
`Band { start: 0x2000, end: 0x1000 }`, and `bytes()` on it panicked. `window` trusts the `Band`
it takes. `x86_64`'s `VirtAddr` keeps its field private, so every value passed its check.
Change: private fields with `const fn start(&self)` and `end(&self)`.
Door: one-way (D1). Effort: S, and one token at each caller.

#### P0-2. `runtime_window` and `service_window` check one page under a window's name

Verified in source (lines 262 to 281) and by building. Both pass `PAGE_BYTES` to `window`, so
`service_window(SERVICE_WINDOWS.end - PAGE_BYTES)` returns whatever the window's length. The
crate's BUGS section names the hazard. Its own `INITIAL_RAMDISK_VIRTUAL_ADDRESS` is
`runtime_window(0x2000_0000)`, one checked page of an archive of unstated length. `pair_page` has
the same body and an honest name.
Change: remove the two, so a caller writes `window(RUNTIME_WINDOWS, address, bytes)` and states
the length. `pair_page` stays, and the ramdisk constant goes through `window` with a largest
archive size.
Door: one-way (D2). Effort: S in the crate, M across callers.

#### P0-3. `ImagePlacement` is exhaustive and is not an error

Verified in source (lines 286 to 328). `check_image` returns `Result<(), ImagePlacement>`. The
type has `Display`, no `core::error::Error` and no `#[non_exhaustive]`, so a third refusal, which
P0-4 would add, breaks every caller that matches. Its name does not say it is a refusal. Its
fields are named, which is good. `vm-memory`'s `GuestRegionCollectionError` derives
`thiserror::Error`.
Change: `core::error::Error`, `#[non_exhaustive]`, and the name the errors decision picks.
Door: one-way (D3). Effort: S.

#### P0-4. `check_image` accepts bounds that are not on a page

Verified by building: `check_image(IMAGE.start + 1, IMAGE.start + 2)` returns `Ok(())`. The
documentation calls the arguments page bounds and the fields rounded to a page, and nothing checks
or rounds. `window` and `Band::new` refuse an address off a page. A refusal added after 0.1.0
changes published behavior.
Change: `check_image` refuses such bounds with a third variant, or its documentation says it
accepts any.
Door: one-way (D4). Effort: S.

#### P0-5. `LOW_HALF_SPLIT_SHIFTS` fixes the count of architectures in its type

Verified in source (line 368). The type is `[(&str, u32); 3]`, so a fourth architecture or a
second paging mode changes it. `BANDS` is a slice for this reason. The ratified name stays.
Change: `&[(&str, u32)]`.
Door: one-way (D5). Effort: S.

#### P0-6. `VERSION` and `INTERFACE_ID` are provisional names

Verified in source (lines 72 and 77) and in the README's BUGS section. `VERSION` is a `u32` of 1
and `INTERFACE_ID` a `u64` of 2. The crate has no wire form, so it has no magic and no decoder.
Change: the names and types the contract-layout decision picks.
Door: one-way (D6). Effort: S.

#### P0-7. Eighteen public names carry no ruling

Verified in the cleared package: `Band`, the eight band constants, `BANDS`, `bytes`, `contains`,
`holds`, `pair_page`, `runtime_window`, `service_window`, `check_image` and `ImagePlacement`. A
tag makes each permanent. `bytes` is `size` in both neighbors; `bytes` carries its unit, and
`len` would mislead, since `PageRange::len` counts pages. `holds(start, end)` is
`contains_range(other)` in `memory_addr`; two numbers let `check_image` ask about bounds that are
no valid `Band`.
Change: ratify each as built, less those P0-2 and P0-3 remove or rename.
Door: one-way (D7). Effort: S.

### P1: before the first release

#### P1-1. The documentation names items a stranger cannot find and never names the system

Verified in source and the README. The crate page, the README and the description say "a
process" and never say of which system. The doc comments name `std_runtime_contract::HEAP_BASE`,
`memory_region_heap::DEFAULT_BASE_VIRTUAL_ADDRESS` and `user_mode_runtime::initial_ramdisk`
(lines 158 and 274), none a published crate or a link. Line 5 assigns a timebase page above 2
GiB, and the crate holds no constant for it.
Change: one sentence that names the binary interface (door D8); each foreign name becomes a link
or a plain description; the timebase page gets a constant or a pointer to its owner.
Door: two-way, apart from D8. Effort: S.

#### P1-2. Two public doc comments tell history

Verified in source (lines 284 and 295): what the loader reported before, and an earlier layout at
`0x40_0000`. Two test names say "old". A stranger has neither to remember.
Change: state what each variant means now.
Door: two-way. Effort: S.

#### P1-3. No `# Panics` or `# Errors` section, and no example on the crate page

Verified in source. Five functions panic and say only that they stop the build, which is true in
a `const` alone. `check_image` has no `# Errors`. The crate page has no example, and no test
compiles the README's three. `pair_page` and the `Band` methods have none. Both neighbors give
their `new` a panics section.
Change: the sections, the README's examples as doctests, and the missing examples.
Door: two-way. Effort: S.

#### P1-4. `Band` and `ImagePlacement` have no `Hash`

Verified in source (lines 83 and 286). `x86_64`'s `PageRange` derives it.
Change: derive `Hash` on both; no `Default` and no `Ord`, since neither has a natural one.
Door: two-way. Effort: S.

#### P1-5. No overlap check for the hazard the crate lists three times

Verified in source. The crate says in three places that whoever places two windows in one band
asserts them disjoint, and `Band` offers nothing to assert with. `memory_addr` has
`AddrRange::overlaps`, and `vm-memory` refuses overlapping regions.
Change: `pub const fn overlaps(&self, other: Band) -> bool`, its name provisional, with an
example in a `const`.
Door: two-way. Effort: S.

#### P1-6. No stated rule for what a changed band does to `VERSION` and to the crate's version

Verified in source and the README. Nothing says when `VERSION` changes or whether a moved band is
a breaking release. A changed constant compiles everywhere, so two programs built apart disagree
at run time. seL4 publishes `seL4_UserTop` in its versioned library's headers.
Change: a stability section stating the rule of door D9.
Door: one-way (D9). Effort: S.

### P2: may follow

Each is verified in source or by building, except P2-6, which is inferred. The evidence is in
[the later items](1153-address-space-layout-release-review/later-items.md).

- P2-1: a `const fn` beside `window` that returns a refusal, as both neighbors pair `new` with
  `try_new`. Two-way, S.
- P2-2: a `Debug` that prints hexadecimal, and `LowerHex`. Two-way, S.
- P2-3: `From` and `TryFrom` with `core::ops::Range<u64>`. Two-way, S.
- P2-4: a function from an address to its band and name. Two-way, S.
- P2-5: a `documentation` key, and an `include` that leaves 20 CI files out of the package.
  Two-way, S.
- P2-6: a documented way to hand the image base to a linker script. Two-way, S.
- P2-7: a checked address is a bare `u64` (C-NEWTYPE). No change at 0.1.0; door D10. M if taken.

### Measured performance

Not run. The interface does not shape performance: a caller binds each checked placement in a
`const`, and `check_image` is three comparisons for each image.

## One-way doors

- D1, the fields of `Band` (P0-1). Recommended: private fields with `start()` and `end()`, the
  stricter choice. Opening them later breaks no caller.
- D2, the one-page band functions (P0-2). The clearance of 1076 kept all three. The evidence
  against two is the crate's own BUGS entry and its ramdisk constant. Recommended: remove
  `runtime_window` and `service_window` and keep `pair_page`. Adding a function later is
  compatible.
- D3, the refusal type (P0-3). Recommended: `#[non_exhaustive]` and `core::error::Error`, and
  the name by the errors decision.
- D4, bounds off a page (P0-4). Recommended: refuse them, the stricter choice.
- D5, the type of `LOW_HALF_SPLIT_SHIFTS` (P0-5). Recommended: a slice.
- D6, `VERSION` and `INTERFACE_ID` (P0-6). Recommended: ratify by the contract-layout decision.
- D7, the eighteen names (P0-7). Recommended: ratify as built.
- D8, whether the crate names its system (P1-1). Recommended: name the binary interface, Moho,
  in one sentence of the crate page, the README and the description.
- D9, what a changed band means (P1-6). Recommended: a change to a band, to `PAGE_BYTES` or to a
  fixed address raises `VERSION` and is a breaking release. A new constant inside a band is
  neither. Relaxing this later breaks no caller.
- D10, a newtype for a checked address (P2-7). Recommended: keep `u64`, the looser choice. The
  value crosses into linker scripts, system calls and page tables as a number. A typed function
  can join the `u64` ones later without breaking them.

## Evidence for the shared decisions

- Errors. One enum, `ImagePlacement`, with named fields and `Display`, no `core::error::Error`
  and no `#[non_exhaustive]`; every other failure is a panic in a `const fn`. `vm-memory` derives
  `thiserror::Error`, `x86_64` returns a tuple struct with `Debug` alone, and `memory_addr`
  returns `Option` or `()`. The evidence points to an enum with named fields, both traits and
  `#[non_exhaustive]`. It adds one case for the decision: an asserting `const fn` paired with a
  form that returns a refusal.
- DMA regions, doorbells and tails, register access, byte sinks and sources, simulators: not
  applicable.
- Feature names. The crate declares none. `x86_64` names a feature for what it turns on, and
  `vm-memory` prefixes a family (`backend-mmap`). No evidence on a version in a name.
- Contract layout. `INTERFACE_ID: u64 = 2` and `VERSION: u32 = 1` at the root, no `MAGIC`, and
  `check_image` as the one fallible entry. The contract is the constants' values. The decision
  needs a place for such a crate: identity and version, no magic, no decoder, and the rule of D9
  where a wire contract has its version check.

## Follow-on

- **Outstanding.** The twenty findings, open on the crate's `main` at `9568826`, read 2026-11-26
  (UTC).
- **Outstanding.** The doors D1 to D10 have no ruling: this block raises them, and no decision
  file names them, read 2026-11-26 (UTC).

## Done when

The architect has ruled all ten doors, no P0 or P1 line above reads Open or Waiting, and
`script/review-status` counts the block BUILT.

## BUGS

- No crate solves the same problem, so no comparator ranks and every Rust comparison is with a
  neighbor's range type.
- The review read one architecture's header from each of FreeBSD and seL4, and Linux's document
  and two headers for x86_64 alone.
- The review counted the callers of no function it recommends removing or changing; the effort
  across callers is an estimate from the cleared package's count of dependents.
- Kani and mutation testing were not run.

## Index row

The release review of `address_space_layout` against the layouts FreeBSD, Linux and seL4 publish
and the range types of `memory_addr`, `x86_64` and `vm-memory`; no crate ranks as a comparator.
Seven findings touch the 0.1.0 interface: public `Band` fields, two one-page functions named for
windows, a refusal type that is not an error, unchecked image bounds, a fixed-length table,
provisional identity names and names without a ruling. Six land before the release, seven may
follow, and ten doors wait for the architect.
