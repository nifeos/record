---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1106, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1157. `program_argument_contract`: the release review's findings

*(The number and the slug are provisional.)*

The release review of `partsfoundry/program_argument_contract` at commit `b097970b`, version 0.1.0,
under milestone 1129 (the combine review), whose [block](1129-crate-interfaces-best-in-class.md)
sets its form. The baseline is milestone 1106 (what an outside maintainer would fix before it
leaves) and [its block](1106-program-argument-contract-outside-review.md); the crate has no
package in `notes/crate-reviews/`. The layout, the magic `PROGARG2`, version 2, identity 18, the
absence of a checksum and the crate's name stay closed here. No naming rule is newer than the
ratification of the public names, so the release-review rule reopens none.

Reuse: the crate's own tests and one scratch crate the appendix describes. No new tool.

## Finding status

- P0-1, the builder keeps going after a refusal: Open.
- P0-2, the writer's two refusals are bare and exhaustive: Waiting on the errors decision of milestone 1129.
- P0-3, the reader has no refusal: Waiting on the contract-layout decision of milestone 1129.
- P0-4, `PageBuilder::new` checks a length at run time: Open.
- P0-5, the mapped-page reader takes a `u64`: Waiting on the contract-layout decision of milestone 1129.
- P0-6, the identity constants and the digit in the magic: Waiting on the contract-layout decision of milestone 1129.
- P1-1, the README contradicts the source: Open.
- P1-2, the refusals implement no `Display` or `Error`: Open.
- P1-3, missing common traits: Open.
- P1-4, one example in the crate: Open.
- P1-5, the mutation exemption names another line: Open.
- P2-1, no `IntoIterator`: Open.
- P2-2, a writer in one call: Open.
- P2-3, reaching one argument walks the records: Open.
- P2-4, the package carries the repository's tooling: Open.
- P2-5, a page of no arguments is valid: Open.

## Open decisions

The one-way doors D1 to D6 below.

## Goal

A stranger who must hand a new program its arguments, with no stack convention and no allocator,
picks this crate. Its types keep a line that does not fit from reaching the program in part. The
reader says why it refused a page, and each refusal prints itself.

## What the review read and ran

[The appendix](1157-program-argument-contract-release-review/what-was-checked.md) lists the files,
the commands, the scratch programs and each comparator.
[The guidelines table](1157-program-argument-contract-release-review/api-guidelines.md) marks the
54 API Guidelines items: 23 met, 10 not met, 21 not applicable.

## Prior art

Measured from the crates.io API on 2026-11-26 at 22:49 (UTC). The problem: whoever starts a program
writes its arguments where the program's runtime finds them. Each ranked crate solves one side of
it for the Linux initial stack, and `crt0stack` holds both.

| crate or system | role | version read | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `argv` | ranked 1: reads a process's arguments | 0.1.14 | 1,403,927 | 120,833 | 5 | 2026-09-08 |
| `origin` | ranked 2: a startup runtime | 0.26.2 | 164,628 | 17,084 | 4 | 2025-05-15 |
| `kernel-elf-parser` | ranked 3: writes the initial stack | 0.3.4 | 82,990 | 13,465 | 6 | 2026-02-07 |
| `crt0stack` | below the rank: builds and reads that stack | 0.1.0 | 380,387 | 3,654 | 5 | 2020-08-19 |
| `linux-loader` | neighbor: a kernel command line under a capacity | 0.14.0 | 5,084,360 | 1,318,805 | 9 | 2026-06-26 |
| `wasip1` | neighbor: bindings to WASI's argument calls | 1.0.0 | 1,606,575 | 842,558 | 5 | 2025-09-09 |
| `lexopt` | integration: an option parser over an iterator | 0.3.2 | 15,914,452 | 3,760,889 | 211 | 2026-02-28 |
| Linux `fs/exec.c`, `fs/binfmt_elf.c` | outside Rust | v6.12 | | | | |
| WASI preview 1, `args_sizes_get`, `args_get` | outside Rust | v0.2.0 | | | | |

The appendix compares the nearest four
[axis by axis](1157-program-argument-contract-release-review/what-was-checked.md#the-comparison).

### What `program_argument_contract` does better

- Than `argv`: it needs neither `std` nor glibc, and it carries any byte, where `argv` 0.1.14 reads
  C strings. It checks the whole page first, where `argv` checks nothing, at a level cost: 370 ns
  against 359 ns for 64 arguments.
- Than `origin`: a checked iterator of slices, where `origin` 0.26.2 hands the program a raw
  `argc` and `argv`.
- Than `kernel-elf-parser`: no allocator, no dependency, and a refusal for a line that does not
  fit. `app_stack_region` returns a `Vec<u8>` of any size, and its `argv_slice[0]` panics on an
  empty list with no `EXECFN` entry.
- Than `crt0stack`: the reader is safe and never returns part of a line. The `Reader` of
  `crt0stack` 0.1.0 is `unsafe` to make and ends silently at the first argument that is not UTF-8.
- Than Linux and WASI: a frame nobody wrote reads as no arguments, and Kani proves the parser
  never panics.

## The items

Effort is S (half a day), M (a day or two) or L (longer). A one-way item lands in
0.1.0 or not at all, since outside callers compile against it afterward.

### P0: the 0.1.0 interface

#### P0-1. The builder keeps going after a refusal

Verified by building.
`push` refuses an argument that does not fit and leaves the builder usable. A scratch program
pushes `rm`, an argument of 4,080 bytes that `push` refuses, and `--force`. `finish` returns 2,
and the page parses as `rm --force`: a line nobody typed, the outcome the crate's documentation
says it prevents. Linux v6.12 fails the whole `execve` with `E2BIG` when one string does not fit
(`copy_strings`).
Change: a refusal marks the builder, and `finish` then returns the refusal and writes no header.
`finish` returns a `Result` of the count as a `usize`, the type of `len`, where it returns a bare
`u32` today. Door: one-way (D1). Effort: S.

#### P0-2. The writer's two refusals are bare and exhaustive

Verified in source.
`PushRefused` is an enum of one unit variant, `TooLong`, with no `#[non_exhaustive]`, and
`WrongPageLength` is a unit struct. A caller that matches `PushRefused` breaks when a second cause
arrives, and P0-1 adds one. `TooLong` carries neither the bytes the record needed nor the bytes
left.
Change: one `#[non_exhaustive]` refusal type for the builder, with named fields for both byte
counts (names provisional), in the shape the errors decision of milestone 1129 picks. Door:
one-way (D2). Effort: S.

#### P0-3. The reader has no refusal

Verified in source and by building.
`ArgumentPage::parse` returns `EMPTY` for a wrong magic, a short slice, a total past the page, a
record that overruns and a count that disagrees. A zeroed frame and a page built with no arguments
both report a length of 0, so a runtime cannot stop on a bad page or log the failed check. WASI's
`args_sizes_get` returns an `errno` apart from the sizes.
Change: a fallible reader that returns a `#[non_exhaustive]` enum naming the failed check, beside
the reader that answers `EMPTY`. The contract-layout decision says which of the two takes the name
`parse`. Door: one-way for the name (D3). Effort: S.

#### P0-4. `PageBuilder::new` checks a length at run time

Verified in source.
`new` takes `&mut [u8]` and returns `WrongPageLength` for any length but `PAGE_BYTES`. A parameter
of `&mut [u8; PAGE_BYTES]` makes the wrong call a compile error and removes the error type. The
slice arrived with item 12 of milestone 1106, for a proof over a short buffer, and the README's
BUGS section says the proof still needs the whole page. The reader differs: `parse` takes a slice
of any length.
Change: the array, which makes `new` infallible, or a slice of any length from `HEADER_BYTES` to
`PAGE_BYTES`, which matches `parse` and shrinks the proof. Door: one-way (D4). Effort: S.

#### P0-5. The mapped-page reader takes a `u64`

Verified in source.
`unsafe fn from_virtual_address(virtual_address: u64)` casts the number to a pointer through
`usize`. The crate's BUGS section records the cost: on a target narrower than 64 bits a large
address names another page. `crt0stack` 0.1.0 takes a typed reference, and
`core::slice::from_raw_parts` takes a pointer. Milestone 1106 ratified the name with its
parameter, and the sibling page contracts share the shape.
Change: the type the contract-layout decision rules for every page contract. The evidence here
points to a pointer, such as `*const [u8; PAGE_BYTES]`. Door: one-way (D5). Effort: S.

#### P0-6. The identity constants and the digit in the magic

Verified in source and in the census of milestone 1129.
The crate exports `INTERFACE_ID` (a `u64`, 18), `VERSION` (a `u32`, 2) and `MAGIC` (a `[u8; 8]`,
`PROGARG2`). The census finds `MAGIC` a `u64` in two contract crates and a byte array in three. A
constant assertion ties the magic's last byte to the digit of `VERSION`, so the page has no
version field and `VERSION` 10 does not compile.
Change: the three constants' types and spellings as the contract-layout decision rules, and one
sentence on what follows version 9. Door: one-way (D6). Effort: S.

### P1: before the first release

#### P1-1. The README contradicts the source

Verified in source.
The README says the identity is `VERSION` 1; the source says 2, and the magic ends in that digit.
It counts two Kani harnesses and then describes the three in the source. It says the builder
refuses all of a line that does not fit, which P0-1 shows is the caller's doing.
Change: version 2, three harnesses, and the builder sentence as P0-1 lands. Door: two-way. Effort: S.

#### P1-2. The refusals implement no `Display` or `Error`

Verified by building: neither type coerces to `&dyn core::error::Error`.
`linux-loader` 0.14.0 and `wasip1` 1.0.0 implement both traits on their error types;
`crt0stack` 0.1.0 implements neither.
Change: both traits on each refusal type that survives P0-2 and P0-4. Door: two-way (an addition). Effort: S.

#### P1-3. Missing common traits

Verified in source and by building (C-COMMON-TRAITS).
`ArgumentPage` has no `PartialEq`, `Eq`, `Hash` or `Default`, although `EMPTY` is its default. Its
derived `Debug` prints the record bytes as numbers, up to 4,080 of them, where `PageBuilder`'s
`Debug` stays short on purpose. The two refusals have no `Hash`.
Change: the four traits on `ArgumentPage`, a `Debug` that lists the arguments, and `Hash` on the
refusals. Door: two-way (additions). Effort: S.

#### P1-4. One example in the crate

Verified in source and by `cargo test`, which runs one doctest (C-CRATE-DOC, C-EXAMPLE,
C-QUESTION-MARK).
`PageBuilder` carries the one example. The crate page shows no code, and `parse`,
`from_virtual_address`, `iter`, `record_bytes` and `remaining_bytes` have no example. The README's
example compiles in no test, and both examples call `unwrap` where `?` would do.
Change: the README's example on the crate page as a doctest, an example on the five items, and
`?` in each. Door: two-way. Effort: S.

#### P1-5. The mutation exemption names another line

Inferred from source; the review ran no mutation test.
The one entry of `.github/mutants-exempts` gives the reason for a `<` against `<=` in the
header-length check of `check`. Its line number is that of `total > room`, six lines lower, which
holds no `<`. That file's header says the gate refuses an entry whose survivor no longer exists.
Change: the survivor's own line, confirmed by one mutation run. Door: two-way. Effort: S.

### P2: may follow

#### P2-1. No `IntoIterator`

Verified by building (C-ITER).
`for argument in page` and `for argument in &page` do not compile. `ArgumentPage` is `Copy` and
`iter` returns the named `Iter`, so each implementation is one line. Milestone 1106 left them out
for one consumer's build. Change: both implementations.
Door: two-way (an addition). Effort: S.

#### P2-2. A writer in one call

Verified in the comparators' source.
`kernel-elf-parser` 0.3.4 writes a whole line in one call, and `linux-loader` 0.14.0 builds from
one string (`Cmdline::try_from`). Here a caller loops over `push`, where P0-1's mistake happens,
and sums `record_bytes` by hand to check a line before it has a frame.
Change: a function from a page and an iterator of arguments to the count or a refusal, and one
that says whether a line fits (names provisional). Door: two-way (additions). Effort: S.

#### P2-3. Reaching one argument walks the records

Verified by measuring.
The format has lengths and no offsets, so `iter().last()` walks every record: 223 ns for 64.
`argv` 0.1.14 counts 64 arguments in 44 ns from an array of pointers a reader can index. An offset
table or a reverse iterator would change the closed layout. Change: `first` and `get`, documented
as linear. Door: two-way (additions). Effort: S.

#### P2-4. The package carries the repository's tooling

Verified by `cargo package --list --allow-dirty`, which lists 39 files, 19 of them under
`.github/` and `.githooks/`. Change: an `include` list
of `src/`, the README, the changelog and the licenses, and the `documentation` key the manifest
lacks (C-METADATA). Door: two-way. Effort: S.

#### P2-5. A page of no arguments is valid

Verified by building.
The README says the first argument is `argv[0]`, yet `finish` with no `push` writes a valid page
of zero arguments. Linux v6.12 adds an empty
`argv[0]` when `execve` gets none (`do_execveat_common`).
Change: one sentence in the contract that a reader must expect zero arguments. Door: two-way. Effort: S.

### Measured performance

Measured in a release build with rustc 1.100.0 on a Linux x86_64 host, lowest of seven passes.
The other rows and the method are
in [the appendix](1157-program-argument-contract-release-review/what-was-checked.md#the-benchmark).

| operation | 3 arguments, 14 bytes | 64 arguments, 508 bytes |
|---|---|---|
| `ArgumentPage::parse`, then iterate and sum the lengths | 24.8 ns | 370.2 ns |
| `argv` 0.1.14: `iter`, sum the lengths | 16.7 ns | 358.7 ns |
| `crt0stack` 0.1.0: `Reader`, iterate and sum the lengths | 43.6 ns | 1,019.6 ns |
| `PageBuilder`: `new`, `push` each, `finish` | 33.6 ns | 465.6 ns |
| `crt0stack` 0.1.0: `Builder`, `push` each, three `done` | 39.5 ns | 420.5 ns |

`parse` checks every record and `iter` reads each again, and the checked reader still stays level
with the leading comparator. The one cost the format sets is P2-3's.

## One-way doors

- D1, what a builder does after a refusal (P0-1). Recommended: a refusal marks it and `finish`
  fails, the stricter choice. A way to clear the mark is a compatible addition.
- D2, the builder's refusal type (P0-2). Recommended: one `#[non_exhaustive]` enum with named
  fields, decided once by the errors decision. `PushRefused` is a ratified name for one method's
  refusal, so a type that `finish` also returns needs the architect's name.
- D3, the reader's refusal and the name `parse` (P0-3). Recommended: the contract-layout decision
  gives the short name to the fallible reader in every contract crate, and the reader that answers
  `EMPTY` takes a name that says so.
- D4, what `PageBuilder::new` accepts (P0-4). Milestone 1106 settled a slice of exactly one page.
  Recommended: `&mut [u8; PAGE_BYTES]`, the stricter choice, which removes `WrongPageLength`. A
  constructor over a slice is a compatible addition.
- D5, the address parameter of `from_virtual_address` (P0-5). Recommended: the contract-layout
  decision rules the type for every page contract; the evidence here points to a pointer.
- D6, the identity constants (P0-6). Recommended: keep `INTERFACE_ID`, `VERSION` and a byte-array
  `MAGIC` as built unless the contract-layout decision rules another type. The digit in the magic
  belongs to the closed layout and stays.

## Evidence for the shared decisions

- **Errors.** Two types, both the writer's: an exhaustive enum of one unit variant and a unit
  struct, with neither `Display` nor `core::error::Error` (P0-2, P1-2). The census pattern counts
  `PushRefused` and misses `WrongPageLength`, so its reading of 0/1 is 0/2. The reader has no error
  type (P0-3). `linux-loader` 0.14.0 keeps one enum with both traits, and `crt0stack` 0.1.0 a unit
  struct with neither. The evidence points to one `#[non_exhaustive]` enum for each side of a
  contract, both traits, and named fields.
- **Direct memory access regions, doorbells and tails, register access, simulators.** Not
  applicable: the crate holds no ring, no register and no hardware.
- **Byte sinks and sources.** The builder writes into a caller's `&mut [u8]`, as `crt0stack`
  does, and the reader yields sub-slices of a borrowed `&[u8]`. The evidence points to plain
  slices for a fixed page, with no trait between.
- **Feature names.** The manifest declares none. `crt0stack` 0.1.0 has a default feature `std`.
- **Contract layout.** The identity is P0-6's. The writer is `PageBuilder` with `new`, `push` and
  `finish`, and the reader is `ArgumentPage` with `parse` and `from_virtual_address`. The census
  lists `parse` alone: its pattern misses `push`, `finish` and `from_virtual_address`, and its
  table leaves out `new`. `new` clears the header and `finish` writes the magic last, so a page left half-built is no
  page: an ordering worth sharing. The writer has two refusals and the reader none. WASI's header
  is this page's, a count and a total and then the bytes, with the error apart. The evidence
  points to one spelling for a writer's three steps, a fallible decoder with a named refusal in
  every contract crate, and a pointer for a mapped page.
  [The appendix](1157-program-argument-contract-release-review/what-was-checked.md#the-contract-shape)
  lists each part.

## Follow-on

- **Outstanding.** The shared decisions of milestone 1129 take D2 for errors, and D3, D5 and D6 for
  the contract layout. Its block, read on 2026-11-26 (UTC), records no ruling on either.
- **Outstanding.** The doors D1 and D4, for the architect. Each is as built at `b097970b`, read on
  2026-11-26 (UTC).

## Done when

`script/review-status` reads this block as BUILT: a Done or a Will not fix on each of its six P0
and five P1 lines, and a ruling on each of D1 to D6.

## BUGS

- Each ranked comparator solves one side of the problem for the Linux initial stack, so no
  benchmark row compares two readers of one format.
- The review read `origin` and `kernel-elf-parser` in their argument files only, and built neither.

## Index row

The release review of `program_argument_contract` against `argv`, `origin`, `kernel-elf-parser`,
`crt0stack`, Linux and WASI. Six one-way items come before 0.1.0, led by a builder that writes a
shortened line after a refusal. Five fixes land before the release, five may follow, and six doors
wait, four of them on shared decisions.
