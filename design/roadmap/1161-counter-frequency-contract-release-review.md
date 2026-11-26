---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1073, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1161. `counter_frequency_contract`: the release review's findings

*(The number and the slug are provisional.)*

The release review of `partsfoundry/counter_frequency_contract` at commit `4decec9d`, version
0.1.0-pre.2 and the tag `v0.1.0-pre.2`, under milestone 1129 (the combine review), whose
[block](1129-crate-interfaces-best-in-class.md) sets its form. The baseline is milestone 1073 (what
an outside maintainer would fix before it leaves),
[its block](1073-counter-frequency-contract-outside-review.md) and the cleared package
[`notes/crate-reviews/counter-frequency-contract.md`](../../notes/crate-reviews/counter-frequency-contract.md).
Every 1073 finding reads Done or ruled. The crate's name, the frozen identity and the thirteen
ratified names stay closed, and no later rule of [design/naming.md](../naming.md) reopens one. The
package settled two behaviors as two-way while the crate has no outside caller. A 0.1.0 tag ends
that, so doors D2 and D3 bring them back with evidence.

Reuse: the crate's own tests, Miri and two scratch programs.

## Finding status

- P0-1, the reader takes an integer address, and no safe function decodes sixteen bytes: Open.
- P0-2, a page built for 0 reads back as `Some(0)`, and the band binds neither half: Open.
- P0-3, `PAGE_VIRTUAL_ADDRESS` follows the build target and exists on every target: Open.
- P0-4, no rule says what the bytes after the sixteenth hold: Open.
- P0-5, `hertz` answers `None` for an unknown rate and for a page it cannot read alike: Waiting on
  the errors decision of milestone 1129.
- P0-6, `MAGIC`, `VERSION` and `INTERFACE_ID` have no shared spelling or type: Waiting on the
  contract-layout decision of milestone 1129.
- P1-1, the documentation names things a stranger cannot find and never names the system: Open.
- P1-2, no example on the crate page or on `new`: Open.
- P1-3, `is_plausible`, `build_page` and `hertz` are not `const fn`: Open.
- P1-4, `Debug` prints the address, and the page type has no equality: Open.
- P1-5, no stated rule for what a changed band or address does to `VERSION`: Open.
- P1-6, the manifest and the baseline disagree on whether the crate publishes: Open.
- P2-1, a reader that converts ticks to time must build its own multiplier: Open.
- P2-2, no `#[must_use]` on the three functions whose result is the point: Open.
- P2-3, the manifest has no `documentation` key and the package ships the repository's CI files:
  Open.
- P2-4, the rate has no conversion to a typed frequency: Open.
- P2-5, an example comment and a test comment refer to a check the reader never saw: Open.

## Open decisions

The one-way doors D1 to D9 below.

## Goal

A stranger reads one page and knows whose page this is. A reader holds a rate it can divide by,
or a refusal that says why. A caller that holds sixteen bytes decodes them without `unsafe`, and
a tool built on one architecture places the page for another.

## What the review read and ran

[The appendix](1161-counter-frequency-contract-release-review/what-was-checked.md) lists what the
lane read and each command's result.
[The guidelines table](1161-counter-frequency-contract-release-review/api-guidelines.md) marks
`counter_frequency_contract` against the 54 API Guidelines items, and
[the later items](1161-counter-frequency-contract-release-review/later-items.md) hold its P1 and
P2 findings in full.

## Prior art

Measured from the crates.io API on 2026-11-26 at 23:13 (UTC). A stranger brings this crate one
problem: how a process of one system learns its counter's rate from a page the kernel maps. Ten
searches of crates.io found no crate that solves it, so no comparator ranks. Linux's
`perf_event_mmap_page` sets the bar: a page the kernel maps read-only into a process, which
carries the counter's rate. The crates below are neighbors that learn a rate another way.

| crate or system | role | version read | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `raw-cpuid` | neighbor: the rate from x86 CPUID leaf 0x15 | 11.6.0 | 218,106,520 | 56,842,327 | 153 | 2025-09-05 |
| `quanta` | neighbor: calibrates the counter against the system clock in each process | 0.13.0 | 182,175,187 | 41,570,076 | 126 | 2026-09-27 |
| `aarch64-cpu` | neighbor: the `CNTFRQ_EL0` register | 12.0.0 | 1,147,326 | 267,546 | 37 | 2026-11-14 |
| `tick_counter` | neighbor: `frequency()` from the register or a one-second measurement | 0.4.5 | 173,178 | 80,057 | 1 | 2023-09-04 |
| `fugit` | integration target: typed rates, measured and not read | 0.6.0 | 6,893,710 | 1,456,814 | 154 | 2026-09-07 |
| Linux `include/uapi/linux/perf_event.h`, `struct perf_event_mmap_page` | outside Rust, sets the bar | v6.12 | | | | |
| Linux `arch/x86/include/asm/pvclock-abi.h` and `include/vdso/datapage.h` | outside Rust | v6.12 | | | | |
| Devicetree Specification, `timebase-frequency` and `clock-frequency` | outside Rust | v0.4 | | | | |

### What `counter_frequency_contract` does better

- Than Linux's three pages: the writer writes one number once, before any reader exists, so a
  reader needs no sequence loop. Its number is the exact rate, where the Linux pages carry a rounded
  multiplier and a shift.
- Than `pvclock-abi.h`, which has no magic and a comment that the layout must never change: the
  magic gives a zeroed or foreign frame a defined answer, and gives a layout break a path.
- Than the Devicetree Specification, whose property has a 32-bit and a 64-bit form: one width,
  one byte order, and a band that catches a value firmware never wrote.
- Than `quanta` and `tick_counter`: no `std`, no measurement in the process. `quanta` calibrates
  for up to 200 milliseconds in each process, and `tick_counter` sleeps one second on `x86_64`.
- Than `raw-cpuid` and `aarch64-cpu`: `is_plausible` refuses a rate of 1, which both accept.
  `TscInfo::tsc_frequency` refuses zero alone, and `CNTFRQ_EL0.get()` returns what firmware wrote.
- Than all of them: two Kani harnesses, each with a patch that turns it red.

`perf_event_mmap_page` carries its size and a compatible version and reserves its tail by name,
which the crate does not; P0-4 and P0-5 follow.

## The items

Effort is S (half a day), M (a day or two) or L (longer). A one-way item binds every caller from
the first 0.1.0 tag, which is why the P0 items cannot wait. Line numbers are of `src/lib.rs`.

### P0: the 0.1.0 interface

#### P0-1. The reader takes an integer address, and no safe function decodes sixteen bytes

Verified in source (lines 133 to 199) and by building. `CounterFrequencyPage::new` is the one way to
read a page, it is `unsafe`, and it takes a `u64` that it casts to a pointer. A caller that already
holds the bytes writes `bytes.as_ptr() as u64` inside `unsafe`, as every example does. Under Miri
with `-Zmiri-strict-provenance` the crate's own tests stop at that cast, and the default Miri run
warns about it. Nothing ties the 16 bytes to the value's lifetime: `new(0)` compiles, and the type
is `Copy`. `raw-cpuid`'s `TscInfo` and Linux's readers take a typed pointer or a value.
Change: a safe `const fn` that decodes `&[u8; PAGE_CONTENT_BYTES]`, which `hertz` calls. The
`unsafe` constructor takes `*const u8`, or takes no argument and names the fixed address.
Door: one-way (D1). Effort: S in the crate, one line at each caller.

#### P0-2. A page built for 0 reads back as `Some(0)`, and the band binds neither half

Verified by building. `build_page(0)` returns a page with the magic, `hertz()` on it returns
`Some(0)`, and a scratch program that divided by the result panicked. No function makes the page
of an unknown rate. Both doc comments hand the band to the caller. `raw-cpuid`'s `tsc_frequency`
returns `None` when a term is zero. The cleared package records the stricter reader as a choice
for a later release.
Change: `hertz` returns `None` outside the band, as `Option<core::num::NonZeroU64>`, and
`build_page` refuses a rate outside it. A constant or a function gives the page of an unknown rate.
Door: one-way (D2). Effort: S, with one host test, one harness and its patch.

#### P0-3. `PAGE_VIRTUAL_ADDRESS` follows the build target and exists on every target

Verified by building. The constant is `0x0000_0038_0000_0000` under `cfg(target_arch =
"riscv64")` and `0x0000_7000_0000_0000` on every other target (lines 91 and 103). A `const`
assertion in a scratch crate showed the `x86_64` value on `aarch64-unknown-none-softfloat`, where
the crate says no page exists. A tool built for one architecture that places the page for another
reads its own target's address. Milestone 1153 (the release review of `address_space_layout`)
found the same question answered with one table for all architectures.
Change: one constant for each architecture under its own name, visible on every target, and
`PAGE_VIRTUAL_ADDRESS` defined on `x86_64` and `riscv64` alone as an alias of its own.
Door: one-way (D3). Effort: S in the crate, S at an aarch64 caller if one exists.

#### P0-4. No rule says what the bytes after the sixteenth hold

Verified in source (line 81) and the README. The doc comment says the rest of the frame is zeroes
and not whether a reader relies on that. So nobody can tell whether version 1 may gain a field at
offset 16. Linux's `perf_event_mmap_page` carries `size` and `compat_version`, and names its tail
`__reserved`.
Change: one sentence in the contract. A writer zeroes the bytes after the sixteenth, a reader
ignores them, and a field added there keeps the magic.
Door: one-way (D4). Effort: S.

#### P0-5. `hertz` answers `None` for an unknown rate and for a page it cannot read alike

Verified by building. A zeroed frame, a frame with a foreign magic and a frame with the magic
`TIMEBAS2` all read as `None`. A reader cannot tell a kernel that does not know the rate from a
kernel with a newer layout. The crate has no error type. Linux's page gives a reader `version` and
`compat_version` to tell the two apart.
Change: the shape the errors decision picks for a contract's decoder, with at least two refusals: no
page written, and a page of another layout.
Door: one-way (D5). Effort: S.

#### P0-6. `MAGIC`, `VERSION` and `INTERFACE_ID` have no shared spelling or type

Verified in source (lines 32, 36 and 42) and in the census of milestone 1129. `MAGIC` is a
`[u8; 8]` here and a `u64` in two sibling contract crates. `VERSION` is a `u32` and `INTERFACE_ID`
a `u64`. The three names are ratified, and the values are frozen.
Change: the types and entry points the contract-layout decision picks. The values do not move.
Door: one-way (D6). Effort: S.

### P1: before the first release

The evidence for each is in
[the later items](1161-counter-frequency-contract-release-review/later-items.md). Each is verified
in source or by building.

- P1-1: one sentence that names the binary interface (door D8), a link to `interfaces_note`, and
  plain words for two other unlinked names. Two-way apart from D8, S.
- P1-2: the README's example on the crate page, and a `no_run` example on `new`. Two-way, S.
- P1-3: `const fn` on `is_plausible`, `build_page` and `hertz`. Two-way, S.
- P1-4: a `Debug` that prints the rate, and `PartialEq` and `Eq` on the value type P0-1 leaves.
  Two-way, S.
- P1-5: a stability section stating the rule of door D7. One-way (D7), S.
- P1-6: the manifest and the README state whichever door D9 rules. One-way (D9), S.

### P2: may follow

The same appendix holds each in full.

- P2-1: a `const fn` from the rate to a multiplier and a shift for nanoseconds. Two-way, S.
- P2-2: `#[must_use]` on `is_plausible`, `build_page` and `hertz`. Two-way, S.
- P2-3: a `documentation` key, and an `include` that leaves 20 CI files out of the package.
  Two-way, S.
- P2-4: a conversion to `fugit`'s typed rate behind a feature; no change at 0.1.0. Two-way, S.
- P2-5: two comments cite a check the crate does not contain. Two-way, S.

### Measured performance

Measured on a Linux x86_64 host with a page of 2,100,000,000 hertz;
[the appendix](1161-counter-frequency-contract-release-review/what-was-checked.md) gives the
method and what each row includes.

| operation | nanoseconds per call |
|---|---|
| `build_page` | 1.98 |
| `CounterFrequencyPage::hertz` | 1.54 |
| ticks to nanoseconds by `ticks * 1e9 / hertz` | 30.02 |
| ticks to nanoseconds by a multiplier and a shift derived once | 0.71 |
| `quanta` 0.13.0 `Clock::delta_as_nanos` | 0.69 |

A process reads the page once. The division costs 42 times the multiply, and the page's unit
leads a reader to it; P2-1 removes that without changing the page.

## One-way doors

- D1, the reader's constructor (P0-1). Recommended: a safe decoder of `&[u8; 16]`, and an `unsafe`
  constructor that takes no address and reads the fixed one. A constructor from a pointer can join
  later; removing an integer one cannot happen after the tag.
- D2, who applies the band (P0-2). The cleared package kept `Some` for any page with the magic. The
  evidence against it is a division by zero in a scratch program and `raw-cpuid`'s refusal of zero.
  Recommended: both halves refuse a rate outside the band, and the reader returns a `NonZeroU64`,
  the stricter choice. Loosening later breaks no caller.
- D3, the address constants (P0-3). The cleared package kept the constant on aarch64. Recommended: a
  named constant for each architecture on every target, and the bare name on the two architectures
  that map the page. Adding the bare name elsewhere later is compatible.
- D4, the bytes after the sixteenth (P0-4). Recommended: writers zero them, readers ignore them, and
  an added field keeps the magic. A reader that refused a nonzero tail would close that path.
- D5, the refusal (P0-5). Recommended: by the errors decision, with a refusal for a foreign or newer
  page apart from an unknown rate.
- D6, the identity names and types (P0-6). Recommended: by the contract-layout decision.
- D7, what a changed band or address means (P1-5). Recommended: a change to either band constant or
  to an address raises `VERSION`, re-mints the magic and is a breaking release. Relaxing this later
  breaks no caller.
- D8, whether the crate names its system (P1-1). Recommended: one sentence that names Moho, the
  binary interface whose kernel maps this page, on the crate page and in the README and the
  description.
- D9, whether the crate publishes to crates.io (P1-6). Recommended: it does not, the stricter
  choice. The programs of one system pin it by its tag, and a published version cannot be withdrawn.
  The P0 items gate the 0.1.0 tag either way.

## Evidence for the shared decisions

- Errors. The crate has no error type: its one fallible function returns `Option<u64>`, and `None`
  covers three causes (P0-5). `raw-cpuid` returns `Option` for a rate too. Linux's page gives a
  reader a version pair and capability bits. The evidence points to a small refusal enum for a
  contract's decoder, where today's answer is `None`.
- DMA regions, doorbells and tails, register access, byte sinks and sources: not applicable. The
  page is plain memory read through one slice, with no volatile access and none needed.
- Feature names. The crate declares none. `quanta` has `mock` and `flaky_tests`, `raw-cpuid` has
  `std`, `serialize`, `display` and `cli`, and `aarch64-cpu` has `critical-section-single-core`.
  Each names what it turns on, and none carries a dependency's version.
- Simulators. The crate needs none: `build_page` makes the bytes a test reads, in the library and
  behind no feature. `quanta` ships its test double as the `mock` feature, on by default.
- Contract layout. `MAGIC: [u8; 8]`, `VERSION: u32` and `INTERFACE_ID: u64` at the root; private
  `_OFFSET_BYTES` constants; `PAGE_CONTENT_BYTES` and `PAGE_VIRTUAL_ADDRESS` for the size and the
  place; `build_page` as the builder; a method of an `unsafe` pointer type as the decoder; no
  refusal type. Linux's page puts `version`, `compat_version` and `size` inside the page. The
  decision needs three things from this crate: a safe decoder of a byte array in every page contract
  (D1), a stated rule for the tail (D4), and one spelling for an address that differs by
  architecture (D3).

## Follow-on

- **Outstanding.** The seventeen findings, open on the crate's `main` at `4decec9`, read
  2026-11-26 (UTC).
- **Outstanding.** No decision file names the nine doors of this page contract, D1 to D9, read
  2026-11-26 (UTC).

## Done when

Doors D1 to D9 each carry a ruling, the six P0 and six P1 lines of the finding status read Done,
and `script/review-status` counts 1161 as BUILT.

## BUGS

- No crate solves the same problem, so every Rust comparison is with a neighbor.
- The review read three Linux headers at one tag and no other kernel's or hypervisor's page.
- The review counted no callers; each effort at callers is an estimate.
- The benchmark ran on one x86_64 host, and no aarch64 or riscv64 core was measured.
- Kani, the falsification replay and mutation testing were not run.

## Index row

The release review of `counter_frequency_contract` against the pages Linux maps for the same job,
the Devicetree Specification's property and four neighbor crates; no crate ranks as a comparator.
Six findings touch the 0.1.0 interface. Four are open: a reader built from an integer address, a
band neither half enforces, an address constant that follows the build target, and an unstated rule
for the page's tail. Two wait on shared decisions. Six land before the release, five may follow, and
nine doors wait for the architect.