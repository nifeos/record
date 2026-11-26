---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1096, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1152. `interfaces_note`: the release review's findings

*(The number and the slug are provisional.)*

The release review of `partsfoundry/interfaces_note` at commit `088baba2`, version 0.1.0, under
milestone 1129 (the combine review), whose [block](1129-crate-interfaces-best-in-class.md) sets its
form. The baseline is milestone 1096 (what an outside maintainer would fix before it leaves),
[its block](1096-interfaces-note-outside-review.md) and the cleared package
[`notes/crate-reviews/interfaces-note.md`](../../notes/crate-reviews/interfaces-note.md). The
descriptor's layout, the equality check, the rule that an absent note or entry passes, the owner
string and the crate's name stay closed here. No naming rule is newer than the ratification of the
twenty public names, so the release-review rule reopens none. Two of those names meet comparator
evidence and stand as door D5.

Reuse: the crate's own tests and doctests, and two scratch crates the appendix describes. No new tool.

## Finding status

- P0-1, the decode refusal is exhaustive, with one positional variant for two causes: Waiting on the errors decision of milestone 1129.
- P0-2, `InterfacesNote` has a public field, and `of` takes a redundant length: Open.
- P0-3, a program can carry two lists: Open.
- P0-4, `Refusal` is exhaustive: Open.
- P0-5, the version and note-type constants: Waiting on the contract-layout decision of milestone 1129.
- P1-1, neither error type implements `Display` or `core::error::Error`: Open.
- P1-2, the owner string and the section name are private: Open.
- P1-3, nothing shows a reader how to reach the descriptor: Open.
- P1-4, no example on the crate page and no failure sections: Open.
- P1-5, missing common traits: Open.
- P1-6, `iter` returns an unnameable type, and there is no `IntoIterator`: Open.
- P2-1, an encoder that returns a refusal: Waiting on the byte sinks and sources decision of milestone 1129.
- P2-2, a bounded note walk in the crate: Open.
- P2-3, a check of a whole served table in one walk: Open.
- P2-4, a `const` decoder: Open.
- P2-5, the macro compiles for a big-endian target: Open.
- P2-6, the package carries the repository's tooling: Open.

## Open decisions

The one-way doors D1 to D6 below.

## Goal

A stranger who wants a program to declare what it was built against, and a loader to check it,
picks this crate. The macro places one note per program and no more. The reader finds the note with
the constants the crate exports, and both refusals print themselves and can take a new cause.

## What the review read and ran

[The appendix](1152-interfaces-note-release-review/what-was-checked.md) lists the files, the
commands, the scratch programs, each comparator and the benchmark's method.
[The guidelines table](1152-interfaces-note-release-review/api-guidelines.md) marks the 54 API
Guidelines items: 24 met, 10 not met, 20 not applicable.

## Prior art

Measured from the crates.io API on 2026-11-26 at 22:26 (UTC). The problem: a binary carries a
record of what it was built against, and whoever loads it checks the record. No Rust crate does
that with an ELF note, so the ranked crates solve it another way, and the C sources set the bar.

| crate or system | role | version read | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `auditable-serde` | ranked 1: the record `cargo auditable` embeds | 0.9.0 | 16,323,210 | 5,480,094 | 8 | 2025-07-04 |
| `auditable-extract` | ranked 1, same family: finds that record | 0.3.5 | 12,087,856 | 3,965,605 | 1 | 2024-10-14 |
| `stabby` | ranked 2: checks a library's layout report at load | 72.1.16 | 9,595,347 | 3,337,900 | 22 | 2026-07-20 |
| `abi_stable` | ranked 3: checks a library's version at load | 0.11.3 | 4,448,700 | 677,939 | 91 | 2023-10-12 |
| `solana-security-txt` | neighbor: a macro places a record, a parser finds it | 1.1.3 | 9,501,555 | 1,630,333 | 89 | 2026-05-15 |
| `object` | integration: walks ELF notes | 0.41.0 | 745,726,836 | 158,972,925 | 582 | 2026-11-10 |
| Linux `include/linux/elfnote.h` | outside Rust: the macro that places a note | v6.12 | | | | |
| Linux `include/xen/interface/elfnote.h` | outside Rust: a guest's notes for its hypervisor | v6.12 | | | | |
| glibc `csu/abi-note.c` | outside Rust: the oldest-kernel note | 2.40 | | | | |

The appendix measures `goblin` and `elf` as further note walkers, and compares the nearest five
[axis by axis](1152-interfaces-note-release-review/what-was-checked.md#the-comparison).

### What `interfaces_note` does better

- Than `auditable-serde` and `auditable-extract`: the loader checks the record before the program
  runs, where theirs waits for an audit tool. Decoding 64 records takes 29 ns here, against
  15.2 µs for 64 packages there.
- Than `stabby`: the check runs no code from the binary under test. `stabby` calls a function the
  library exports (`get_stabbied`) and returns a boxed `dyn Error`.
- Than `abi_stable`: the loader reads data, where `abi_stable` loads the library and reads a
  symbol. The crate needs neither `std` nor a dependency.
- Than `solana-security-txt`: a bounded layout and a decoder Kani proves panic-free, where that
  crate searches the whole binary for a marker string.
- Than the C sources: one crate holds the writer, the reader and the proof that they agree.
  `ELFNOTE` leaves each check to its reader, and glibc 2.40's `elf/dl-load.c` never reads the
  note its `csu/abi-note.c` places.

## The items

Effort is S (half a day), M (a day or two) or L (longer). A one-way item changes what a caller
outside the repository compiles against, so it ships in 0.1.0 or never.

### P0: the 0.1.0 interface

#### P0-1. The decode refusal is exhaustive, with one positional variant for two causes

Verified in source (`Error`, `decode_interfaces`).
`Error` has four variants and no `#[non_exhaustive]`. `BadField(usize)` reports a count past
`MAXIMUM_INTERFACES` and also ids that do not ascend, and only the offset tells them apart. A
second descriptor version with a new refusal breaks every caller that matches all four.
`abi_stable` names each field of `LibraryError::IncompatibleVersionNumber`.
Change: `#[non_exhaustive]`, one variant per cause and named fields (names provisional), in the
shape the errors decision of milestone 1129 picks. Door: one-way (D1). Effort: S.

#### P0-2. `InterfacesNote` has a public field, and `of` takes a redundant length

Verified by building.
`InterfacesNote<const N: usize>(pub [u8; N])` lets a caller build a note from any bytes:
`InterfacesNote::<4>([0xff; 4])` compiles. `of` takes a second constant, `LEN`, by turbofish. It
must equal `descriptor_bytes(list.len())`, and a wrong one panics. `LEN` is `N` less the twenty
header bytes, so `of` can write the records straight into its output.
Change: a private field with a `const fn as_bytes`, and `of(list)` with `N` alone. The macro
calls `of` and keeps working. Door: one-way (D2). Effort: S.

#### P0-3. A program can carry two lists

Verified by building.
The macro's documentation says its fixed static name holds a program to one list. The name
collides only inside one module. Two calls in two modules compile into two notes, and a
dependency that calls the macro adds a note to every program that links it. Nothing says what a
reader does with two. `solana-security-txt` marks its static `#[no_mangle]`,
so a second record is a duplicate symbol. The same attribute on this macro's static refuses the
second call at compile time in a scratch crate.
Change: an exported symbol name on the static (provisional), and a sentence that a library never
calls the macro. Door: one-way (D3). Effort: S.

#### P0-4. `Refusal` is exhaustive

Verified in source.
`Refusal` has three public fields and no `#[non_exhaustive]`. A caller can build one the check
never returned, and a fourth field, such as the descriptor's version, breaks every caller that
builds or destructures one.
Change: `#[non_exhaustive]`, fields still readable. `DeclaredInterface` stays as built (D4).
Door: one-way (D4). Effort: S.

#### P0-5. The version and note-type constants

Verified in source and in the census of milestone 1129.
The crate exports `INTERFACES_VERSION` where the other eleven contract crates export `VERSION`.
It names the note type `INTERFACES`, which reads as a list. Xen's header names each type as one
(`XEN_ELFNOTE_XEN_VERSION`), and `object` has `NoteType`. Both names are ratified (1096, decision
2), so this is evidence for a door and not a rename.
Change: the version constant as the contract-layout decision of milestone 1129 rules, and a
note-type name that says what it is. Door: one-way (D5). Effort: S.

### P1: before the first release

#### P1-1. Neither error type implements `Display` or `core::error::Error`

Verified by building: an `Error` does not coerce to `&dyn core::error::Error`.
`Error` and `Refusal` derive `Debug` only, so a loader's log reads `BadField(4)`.
`auditable-extract`, `abi_stable` and `solana-security-txt` implement both traits.
Change: both traits on both types. Door: two-way (an addition). Effort: S.

#### P1-2. The owner string and the section name are private

Verified in source.
A reader matches a note by owner string and type. The type is public. The owner string is a
private constant, and the section name exists only inside the macro, so a reader copies both from
the source. `solana-security-txt` exports both of its markers.
Change: two public constants (names provisional), and a test that the macro's literal equals the
section constant. Door: two-way (an addition). Effort: S.

#### P1-3. Nothing shows a reader how to reach the descriptor

Verified by building.
`decode_interfaces` takes a descriptor, and no document shows the walk that finds one. A scratch
reader does it with `object` in about a dozen lines, on a program built with the macro for a
Linux x86_64 host. `readelf -n` labels this note a Go build identifier, since it reads type 4
without the owner.
Change: that reader under `examples/`, with `object` as a development dependency, and one
sentence on the `readelf` label. Door: two-way. Effort: S.

#### P1-4. No example on the crate page and no failure sections

Verified in source and by `cargo test`, which runs five doctests (C-CRATE-DOC, C-EXAMPLE,
C-QUESTION-MARK, C-FAILURE).
The crate page carries no code, and the README's example compiles in no test. `iter`, `len`,
`is_empty`, `descriptor_bytes`, `note_bytes` and `InterfacesNote::of` have no example. No function
has a `# Panics` or `# Errors` heading, and the examples call `unwrap` where `?` would do.
Change: the README as the crate page or as a doctest, the six examples and the headings. Door:
two-way. Effort: S.

#### P1-5. Missing common traits

Verified in source (C-COMMON-TRAITS, C-DEBUG).
`DeclaredInterface`, `Error`, `Refusal` and `Interfaces` have no `Hash`. `DeclaredInterface` has
no `Ord`, although the format orders records by id. `InterfacesNote` derives nothing.
Change: `Hash` on the four, `PartialOrd` and `Ord` on `DeclaredInterface`, and `Debug`, `Clone`,
`PartialEq` and `Eq` on `InterfacesNote`. Door: two-way (additions). Effort: S.

#### P1-6. `iter` returns an unnameable type, and there is no `IntoIterator`

Verified by building (C-ITER, C-ITER-TY).
`Interfaces::iter` returns `impl Iterator<Item = DeclaredInterface> + use<'a>`. A caller cannot
hold it in a field, and it promises no `ExactSizeIterator`, though the length is known.
`for entry in list` does not compile. `object` and `elf` export a named `NoteIterator`.
Change: a named `Iter<'a>` with `ExactSizeIterator`, `DoubleEndedIterator` and `Clone`, and
`IntoIterator` for `Interfaces<'a>`. No caller can name the opaque type, so the swap breaks none.
Door: two-way. Effort: S.

### P2: may follow

#### P2-1. An encoder that returns a refusal

Verified by building.
`encode_interfaces` panics on a list out of order, a list past 64 and a wrong `LEN`: a compile
error in a constant, and a panic in a tool that builds the list at run time. The crate's BUGS
entry plans such a tool.
Change: a second encoder that writes into a caller's buffer and returns the length or a refusal,
in the shape the byte sinks and sources decision of milestone 1129 picks. Door: two-way (an
addition). Effort: S.

#### P2-2. A bounded note walk in the crate

Verified in the comparators' source.
`auditable-extract` (`raw_auditable_data`) and `solana-security-txt` (`find_and_parse`) take a
whole binary and return the record. `goblin` keeps its `NoteIterator` behind `alloc`, out of reach
of a loader with no allocator.
Change: a function from one note segment's bytes to this note's descriptor, or none, with a Kani
harness. What it does with two notes follows D3. Door: two-way (an addition). Effort: M.

#### P2-3. A check of a whole served table in one walk

Verified by measuring.
`check_served` walks the list from its start on each call. Checking 64 served interfaces against
64 records takes 2.1 µs in 64 calls, and 191 ns in one merge over `iter()`.
Change: a method that takes the served pairs in ascending order, or a binary search inside
`version_of`. Door: two-way (an addition). Effort: S.

#### P2-4. A `const` decoder

Verified in source.
The encoders are `const fn`. `decode_interfaces`, `len`, `version_of` and `check_served` are not,
so a program cannot assert at compile time what its note declares. Change: `const fn` on the
four. Door: two-way to add. Effort: S.

#### P2-5. The macro compiles for a big-endian target

Inferred from source; no big-endian target was installed.
The encoder writes the note's header little-endian on every target. The macro still compiles for
a big-endian file, where no reader of that byte order can walk the note.
Change: a `compile_error!` in the macro under `cfg(target_endian = "big")`. Door: two-way.
Effort: S.

#### P2-6. The package carries the repository's tooling

Verified by `cargo package --list --allow-dirty`, which lists 39 files.
Twenty are under `.github/` and `.githooks/`. Change: an `include` list of `src/`, the README,
the changelog and the licenses. Door: two-way. Effort: S.

### Measured performance

Measured in a release build with rustc 1.100.0 on a Linux x86_64 host, lowest of seven passes.
The comparator parses uncompressed JSON naming the same count of packages. The other rows and the
method are in [the appendix](1152-interfaces-note-release-review/what-was-checked.md#the-benchmark).

| operation | 4 records | 64 records |
|---|---|---|
| `decode_interfaces` | 4.8 ns | 29.1 ns |
| `check_served` once for each record | 25.8 ns | 2,105 ns |
| one merge walk over `iter()`, the same answer | 13.0 ns | 190.9 ns |
| `auditable-serde` 0.9.0: `VersionInfo::from_str` | 970 ns | 15,199 ns |

The interface shapes one cost: `check_served` restarts its walk on every call (P2-3).

## One-way doors

- D1, the decode refusal's shape (P0-1). Recommended: `#[non_exhaustive]`, one variant per cause
  and named fields, decided once by the errors decision. Dropping the attribute later breaks no
  caller.
- D2, `InterfacesNote` (P0-2). Recommended: a private field and `of` with one constant. Opening
  the field later is compatible, and closing it after 0.1.0 is not.
- D3, how many lists a program carries (P0-3). The choices are one list, held by an exported
  symbol, or several, with a stated rule for the reader. Recommended: one, the stricter choice. A
  later release can drop the symbol and define a merge without breaking a program.
- D4, the exhaustive structs (P0-4). Recommended: `#[non_exhaustive]` on `Refusal`, and
  `DeclaredInterface` as built. That is the looser choice for `DeclaredInterface`, and the reason
  is misuse. A caller builds it by a literal with named fields. A constructor of two integers
  loses the names: `new(7, 4)` compiles as readily as `new(4, 7)`. A wider record is a new wire
  version and can be a new type.
- D5, two ratified names (P0-5). Recommended: the contract-layout decision rules the version
  constant for all twelve crates, and the note type takes a name that says so. Both renames are
  the architect's.
- D6, the fixed owner string, which 1096's decision 1 keeps. Linux's `ELFNOTE` takes the owner
  as an argument. Here type 4 and the ids mean something only under this owner. Recommended: keep
  it fixed. A macro arm that takes an owner is a compatible addition.

## Evidence for the shared decisions

- **Errors.** Two types: an exhaustive enum of four with one positional field (P0-1), and a
  struct of three named fields (P0-4). Neither has `Display` or `core::error::Error` (P1-1).
  `auditable-extract` and `abi_stable` use one enum per crate with both traits and no
  `#[non_exhaustive]`. The evidence points to both traits always, named fields, and
  `#[non_exhaustive]` wherever a new wire version can widen the type.
- **Direct memory access regions, doorbells and tails, register access, simulators.** Not
  applicable: the crate holds no address, no ring and no hardware.
- **Byte sinks and sources.** The decoder borrows `&[u8]` with no copy, and the encoder returns
  `[u8; LEN]` by value, which a constant needs. `auditable-extract` and `object`'s `Note::desc`
  also return a sub-slice. The evidence points to plain slices for a fixed-layout contract.
- **Feature names.** The manifest declares none. `goblin`'s `alloc` gate on its note iterator
  shows what a feature costs a loader with no allocator (P2-2).
- **Contract layout.** The crate exports `INTERFACE_ID` (a `u64`, 21) and `INTERFACES_VERSION` (a
  `u32`, 1) and no magic, since the owner string and the note type identify the note. Its entry
  points are `encode_interfaces`, `decode_interfaces` and `check_served`. A program lists every
  contract crate's pair as a `DeclaredInterface` of a `u64` id and a `u32` version. The layout
  decision therefore cannot widen either constant without a second descriptor version here.
  Xen's header keeps one owner's note types in one file, the registry this crate leaves out.

## Follow-on

- **Outstanding.** The shared decisions of milestone 1129 take D1, P2-1 and D5. Its block, read
  on 2026-11-26 (UTC), records no ruling on errors, byte sinks or contract layout.
- **Outstanding.** The doors D2, D3, D4 and D6, for the architect. Each is as built on the
  crate's `main` at `088baba2`, read on 2026-11-26 (UTC).

## Done when

The block reads BUILT in `script/review-status`: each P0 and P1 line above says Done or Will not
fix, and D1 to D6 each carry a ruling.

## BUGS

- The benchmark's comparator parses another format, so its row shows what each format costs a
  reader, not two decoders of one format.
- The review read `stabby` for its loading interface only.
- The scratch reader ran on one host and one linker, with no bare-target program.

## Index row

The release review of `interfaces_note` against `auditable-serde` with `auditable-extract`,
`stabby`, `abi_stable`, Linux's note macro and Xen's note header. Five one-way changes come before
0.1.0, among them a refusal that can widen and a macro that places one note per program. Six
smaller fixes land before the release, six may follow, and six doors wait for a ruling.
