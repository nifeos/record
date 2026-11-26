---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1089, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1163. `environment_contract`: the release review's findings

*(The number and the slug are provisional.)*

The release review of `partsfoundry/environment_contract` at commit `62ea88d9`, version 0.1.0 with
no tag, under milestone 1129 (the combine review), whose
[block](1129-crate-interfaces-best-in-class.md) sets its form. The baseline is milestone 1089 (what
an outside maintainer would fix before it leaves), [its block](1089-environment-contract-outside-review.md)
and the cleared package [`notes/crate-reviews/environment-contract.md`](../../notes/crate-reviews/environment-contract.md).
Every 1089 finding reads Done. The identity (13, 1, `ENVCONF1`), the 107-byte layout, the closed
lists and the ratified names stay closed, and no later rule of [design/naming.md](../naming.md)
touches a ratified name. Doors D2, D3 and D6 bring three ratified items back with evidence.

Reuse: the crate's own tests, two scratch programs and a scratch benchmark.

## Finding status

- P0-1, `PageBuilder<'a>` borrows the caller's string and only ever holds a list member: Open.
- P0-2, `ConfigurationPage::new` takes the address as a `u64`: Waiting on the contract-layout decision of milestone 1129.
- P0-3, two reader types carry the same three accessors: Open.
- P0-4, the reader has no refusal, and four different pages read as `None`: Waiting on the contract-layout decision of milestone 1129.
- P0-5, `Refused` is exhaustive and does not say which value it refused: Waiting on the errors decision of milestone 1129.
- P0-6, the spelling and types of `MAGIC`, `VERSION`, `INTERFACE_ID` and `build`: Waiting on the contract-layout decision of milestone 1129.
- P0-7, `ConfigurationView` and its four methods are provisional names: Open.
- P1-1, no stated rule for what a new list member does to `VERSION` and to the crate's version: Open.
- P1-2, `Debug` on `ConfigurationView` prints 107 numbers: Open.
- P1-3, no `# Errors` section, every example unwraps, and nothing compiles the README's example: Open.
- P1-4, the documentation uses terms a stranger cannot look up and never names the system: Open.
- P1-5, four public types lack `Hash`, and `ConfigurationPage` lacks `PartialEq`: Open.
- P1-6, the safe reader accepts one type, a reference to a 107-byte array: Open.
- P2-1, the field offsets are private: Open.
- P2-2, a checked value is a bare `&str`: Open.
- P2-3, a page cannot be built in a `const`: Open.
- P2-4, a lookup is exact, so `utc` and `en_US.utf8` are refused: Open.
- P2-5, the package ships the repository's CI files: Open.
- P2-6, `build` returns the page by value and cannot fill a caller's frame: Open.

## Open decisions

The one-way doors D1 to D10 below.

## Goal

A stranger reads one page and knows whose page this is. The writer's types carry no lifetime
they do not need. A reader on any target hands the crate a pointer or bytes and can tell a
missing page from a missing key. No shared decision of milestone 1129 changes a signature after
0.1.0.

## What the review read and ran

[The appendix](1163-environment-contract-release-review/what-was-checked.md) lists what the lane
read and ran, with the benchmark's method.
[The guidelines table](1163-environment-contract-release-review/api-guidelines.md) marks
`environment_contract` against the 54 API Guidelines items, and
[the later items](1163-environment-contract-release-review/later-items.md) hold the evidence for
its P1 and P2 findings.

## Prior art

Measured from the crates.io API on 2026-11-26 at 23:13 (UTC). The crate hands a new process its
time zone, locale and terminal type, with no string the starter did not vet. Eight searches of
crates.io found no crate that does, so no comparator ranks. Each crate below is a neighbor for
one part of the job, and the C headers set the bar.

| crate or system | role | version read | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `rustix` | neighbor: its `param` module reads the auxiliary vector at start-up | 1.1.6 | 1,476,082,831 | 399,671,137 | 2,401 | 2026-10-27 |
| `zerocopy` | neighbor: reads a fixed layout from bytes | 0.8.66 | 1,210,090,471 | 360,879,323 | 938 | 2026-11-25 |
| `heapless` | neighbor: a string bounded by a fixed field | 0.9.4 | 192,753,758 | 64,850,554 | 1,239 | 2026-11-18 |
| `chrono-tz` | neighbor: a closed list of time zones as a type | 0.10.4 | 209,171,873 | 62,379,932 | 1,225 | 2025-07-11 |
| Linux `include/uapi/linux/auxvec.h` and `fs/binfmt_elf.c` | outside Rust: the initial stack | v6.12 | | | | |
| Fuchsia `zircon/system/public/zircon/processargs.h` | outside Rust: the bootstrap message | `8ff2539f` | | | | |
| musl `src/time/__tz.c` | outside Rust: a reader that vets `TZ` | v1.2.5 | | | | |
| glibc `sysdeps/generic/unsecvars.h` | outside Rust: a list of refused variables | 2.40 | | | | |

The appendix lists eight more crates the lane measured and set aside. No integration target
applies.

### What `environment_contract` does better

- Than Linux's initial stack and Fuchsia's `zx_proc_args`, which carry any string under any
  name: three keys, each a member of a closed list that both sides check.
- Than musl's `__tz.c` and glibc's `unsecvars.h`, which vet in the reader and only for a
  privileged program: a refusal in the writer and again in the reader, for every program.
- Than `rustix`'s `param`, which must check the pointers the auxiliary vector supplies: the page
  holds no pointer.
- Than `zerocopy`: a derived struct of the same layout reads a field 2.8 to 5.8 times slower,
  since its caller must validate UTF-8. This crate returns the list's own `&'static str`.
- Than `chrono-tz`, whose `ParseError` implements `Error` under `std` alone: `Refused`
  implements `core::error::Error` with no dependency.
- Than all of them: two Kani harnesses over a fully symbolic page, each with a patch that turns
  it red.

`chrono-tz` knows 597 zone names and this crate 20, short on purpose by a closed decision.

## The items

Effort is S (half a day), M (a day or two) or L (longer). A one-way item binds every caller from
the first 0.1.0 tag, which is why the P0 items cannot wait. Line numbers are of `src/lib.rs`.

### P0: the 0.1.0 interface

#### P0-1. `PageBuilder<'a>` borrows the caller's string and only ever holds a list member

Verified in source (lines 195 to 243) and by building. Each setter stores the caller's `&'a str`
after it finds an equal member in a `&'static` list, so the type carries a lifetime. A scratch
program that returned a builder from a block owning its `String` did not compile (E0597).
`chrono-tz`'s `Tz` is a `Copy` value with no lifetime.
Change: the setters store the member they found, and the type is `PageBuilder`. A setter still
takes any `&str`.
Door: one-way (D1). Effort: S, and one token at each caller that names the type.

#### P0-2. `ConfigurationPage::new` takes the address as a `u64`

Verified in source (lines 478 to 482); the 32-bit case is inferred, since the host has no 32-bit
target. `new(virtual_address: u64)` casts the number to `*const u8`. A 32-bit target drops the
upper half silently, and on every target the pointer carries no provenance. Both doc examples
write `page.as_ptr() as u64`. `rustix` keeps the auxiliary vector's pointers as `AtomicPtr` and
`NonNull`, and `zerocopy` takes a reference. The sibling page crates share the shape.
Change: the pointer type the contract-layout decision picks, such as
`*const [u8; PAGE_CONTENT_BYTES]`. The ratified parameter name stays.
Door: one-way (D2). Effort: S.

#### P0-3. Two reader types carry the same three accessors

Verified in source (lines 379 to 508). `ConfigurationPage` holds an address, builds a
`ConfigurationView` in a private `view` and forwards `time_zone`, `locale` and `terminal_type`.
A stranger meets two types, six accessors and one behavior. `zerocopy` has one reading path, from
bytes.
Change: `ConfigurationPage` keeps `new`, `view` becomes public, and the three forwarding accessors
go. A reader writes `page.view().time_zone()`.
Door: one-way (D3). Effort: S in the crate, S at each reader.

#### P0-4. The reader has no refusal, and four different pages read as `None`

Verified in source (lines 340 to 354) and by building. A zeroed frame, a page whose magic ends
in `2`, a page whose `TZ` field holds `XYZ` and a page with no `LANG` each answered `None`.
Start-up code cannot tell a missing page from a missing key, nor from a member only a newer
writer knows. `ConfigurationView::new` cannot fail, and each accessor compares the magic again.
`zerocopy`'s `try_ref_from_bytes` refuses once, with an error that returns the source.
Change: the decoder shape the contract-layout decision picks. The review proposes a checked
constructor that refuses a frame without the magic, beside accessors that keep `Option`.
Door: one-way (D4). Effort: S.

#### P0-5. `Refused` is exhaustive and does not say which value it refused

Verified in source (lines 154 to 162 and 510 to 520). `Refused` has `Display` and
`core::error::Error` and no `#[non_exhaustive]`, so a variant for a fourth key breaks every
caller that matches. The cleared package answers that a fourth key is a new `VERSION`; a
compatible crate release can still carry one. The message names the list and not the value.
`chrono-tz`'s `ParseError` is opaque, and `zerocopy`'s errors return the source through
`into_src`.
Change: `#[non_exhaustive]`, and what the errors decision says about the name and the input.
Door: one-way (D5). Effort: S.

#### P0-6. The spelling and types of `MAGIC`, `VERSION`, `INTERFACE_ID` and `build`

Verified in source (lines 107, 111, 117 and 247). `MAGIC` is a `[u8; 8]`, `VERSION` a `u32` and
`INTERFACE_ID` a `u64`. The last byte of `MAGIC` is the digit of `VERSION`, so the layout has
nine versions. The writer's entry is `PageBuilder::build`, and the census of milestone 1129 lists
other spellings in the sibling crates. Fuchsia's `zx_proc_args` carries `protocol` and `version`
as two `uint32_t` fields. The frozen values stay.
Change: the names and types the contract-layout decision picks.
Door: one-way (D6). Effort: S.

#### P0-7. `ConfigurationView` and its four methods are provisional names

Verified in the baseline block, which records the name as provisional. The type and its `new`,
`time_zone`, `locale` and `terminal_type` carry no ruling, and a tag makes each permanent. The
accessors repeat ratified spellings. `View` says the type borrows, as `zerocopy`'s `Ref` does.
Change: ratify each as built.
Door: one-way (D7). Effort: S.

### P1: before the first release

Each is verified in source or by building, with the evidence in
[the later items](1163-environment-contract-release-review/later-items.md).

- P1-1: a stability section that says what a new list member does to `VERSION` and to the
  crate's version. One-way (D8), S.
- P1-2: a `Debug` for `ConfigurationView` that prints the three answers, not 107 numbers.
  Two-way, S.
- P1-3: `# Errors` on the setters, examples that use `?`, and the README's example as a doctest.
  Two-way, S.
- P1-4: one sentence that names the system (D9), a definition of "inert configuration", and the
  layout on the crate page. Two-way apart from D9, S.
- P1-5: `Hash` on `Refused`, `PageBuilder` and `ConfigurationView`, and equality on
  `ConfigurationPage`. Two-way, S.
- P1-6: `TryFrom<&[u8]>` for `ConfigurationView`, so a reader passes a frame or a slice.
  Two-way, S.

### P2: may follow

- P2-1: the seven field offsets as public constants. Two-way, S.
- P2-2: a checked value is a bare `&str` (C-NEWTYPE). No change at 0.1.0; door D10. M if taken.
- P2-3: `const fn` setters and `build`, so a fixed page builds in a `const`. Two-way, S.
- P2-4: a sentence, or a mapping function, for the refused spellings `utc` and `en_US.utf8`.
  Two-way, S.
- P2-5: an `include` list that leaves 21 CI files out of the package. Two-way, S.
- P2-6: a second writer entry that fills a caller's `&mut [u8; PAGE_CONTENT_BYTES]`. Two-way, S.

### Measured performance

Release profile on a Linux x86_64 host; [the appendix](1163-environment-contract-release-review/what-was-checked.md)
has the method and what each row includes.

| operation | time for each call |
|---|---|
| `ConfigurationView::time_zone`, first member (`UTC`) | 3.0 ns |
| `ConfigurationView::time_zone`, last member (`Pacific/Auckland`) | 3.3 ns |
| all three accessors, each key at its list's last member | 14.1 ns |
| `ConfigurationView::time_zone`, zeroed frame | 1.9 ns |
| `zerocopy` 0.8.66 struct of the same layout, `UTC` | 8.3 ns |
| `zerocopy` 0.8.66 struct of the same layout, `Pacific/Auckland` | 19.3 ns |
| three setters and `build`, each key at its last member | 57.1 ns |
| `domain::is_known_time_zone`, last of 20 | 4.3 ns |
| `chrono_tz::Tz::from_str`, the same name among 597 | 27.8 ns |

The interface does not cap the reader: returning the list's own string costs less than
validating the page's bytes. The linear search grows with the list.

## One-way doors

- D1, the lifetime of `PageBuilder` (P0-1). Recommended: no lifetime. A type cannot shed a
  parameter after 0.1.0.
- D2, the reader's address type (P0-2). The clearance of 1089 ratified `virtual_address` on a
  `u64`. Recommended: a raw pointer to the array, by the contract-layout decision, with the name
  kept.
- D3, the second reader type (P0-3). The clearance ratified `ConfigurationPage` with three
  accessors. Recommended: one set of accessors, on `ConfigurationView`, reached through a public
  `ConfigurationPage::view`. A forwarding accessor can return later, and none can leave.
- D4, the reader's refusal (P0-4). Recommended: a checked constructor that refuses a frame
  without the magic, by the contract-layout decision. The accessors keep `Option`.
- D5, the refusal type (P0-5). Recommended: `#[non_exhaustive]`, the stricter choice, with the
  name and the carried input by the errors decision.
- D6, `MAGIC`, `VERSION`, `INTERFACE_ID` and `build` (P0-6). Recommended: ratify by the
  contract-layout decision; the frozen values stay.
- D7, the five names of `ConfigurationView` (P0-7). Recommended: ratify as built, less any that
  D4 replaces.
- D8, what a new list member means (P1-1). Recommended: a new member is a minor release and
  leaves `VERSION` alone, and an older reader answers `None` for it. Removing or respelling a
  member raises `VERSION` and is a breaking release, the stricter choice.
- D9, whether `environment_contract` names its system (P1-4). Recommended: its crate page, README
  and description each say the page belongs to the Moho binary interface.
- D10, a type for a checked value (P2-2). Recommended: keep `&str`, the looser choice. Typed
  members and `FromStr` can join the `&str` setters later without breaking them.

## Evidence for the shared decisions

- Errors. One enum, `Refused`, with three unit variants, `Display` and `core::error::Error`, no
  `#[non_exhaustive]` and no carried input; the reader answers `None`. `chrono-tz` returns an
  opaque `ParseError(())` with `Error` under `std` alone. `zerocopy`'s three errors return the
  source through `into_src`, and `heapless` has a unit `CapacityError` with
  `core::error::Error`. The evidence points to `core::error::Error` always and
  `#[non_exhaustive]` on an enum. It is split on carrying an input the caller still holds.
- DMA regions, doorbells and tails, register access, simulators: not applicable.
- Byte sinks and sources. Not applicable: the page is a fixed array, and no neighbor reads such a
  layout through a byte trait.
- Feature names. The crate declares none. `chrono-tz` names features for what they turn on
  (`case-insensitive`, `std`), and `heapless` names one for a dependency's version,
  `embedded-io-v0.7`.
- Contract layout. `MAGIC: [u8; 8]`, `VERSION: u32` and `INTERFACE_ID: u64` at the root, with the
  version's digit also in the magic. The writer is a builder whose `build` returns the array.
  The reader is two types with no refusal, one over a `u64` address, and the offsets are
  private. Fuchsia puts `protocol` and `version` in the message, and Linux numbers each key. The
  evidence points to one reader over bytes, an unsafe step that takes a pointer, a checked
  constructor, and one rule that ties the magic to the version.

## Follow-on

- **Outstanding.** The nineteen findings, open on the crate's `main` at `62ea88d`, read
  2026-11-26 (UTC).
- **Outstanding.** No decision file names doors D1 to D10 of `environment_contract`, which this
  block raises; read 2026-11-26 (UTC).

## Done when

The architect has ruled the ten doors of `environment_contract`, and no P0 or P1 line above
reads Open or Waiting. `script/review-status` then counts this block BUILT.

## BUGS

- No crate solves the same problem, so no comparator ranks.
- The review built for no 32-bit target, so it read P0-2's truncation from the cast.
- The benchmark's `zerocopy` rows use a struct the review wrote for this layout; no published
  crate ships it.
- The review counted no callers; each effort across callers is an estimate.
- The review read the Fuchsia header at the head of its main branch, not at a release.
- Kani, Miri and mutation testing were not run.

## Index row

The release review of `environment_contract` against the start-up data Linux and Fuchsia hand a
process, the vetting musl and glibc do, and the neighbors `rustix`, `zerocopy`, `heapless` and
`chrono-tz`; no crate ranks as a comparator. Seven findings touch the 0.1.0 interface. They are a
builder lifetime with no use, an address passed as a `u64`, two readers with the same accessors
and a reader with no refusal, then an exhaustive refusal type, the identity spellings and five
names without a ruling. Six land before the release, six may follow, and ten doors wait for the
architect.
