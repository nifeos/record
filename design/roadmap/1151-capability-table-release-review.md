---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1081, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1151. `capability_table`: the release review's findings

*(The number and the slug are provisional.)*

The release review of `partsfoundry/capability_table` at commit `a0e8b159`, version 0.1.0, under
milestone 1129 (the combine review), whose [block](1129-crate-interfaces-best-in-class.md) sets its
form. The baseline is milestone 1081 (what an outside maintainer would fix before it leaves),
[its block](1081-capability-outside-review.md) and the cleared package
[`notes/crate-reviews/capability-table.md`](../../notes/crate-reviews/capability-table.md). 1081's
items are all closed, and nothing here repeats them. The seven names it ratified stand, and the
package lists them. Every other name waits for ratification, so the doors below that touch a name
reopen no ruling.

Reuse: the prior-art table weighs each capability table a caller could take.

## Finding status

- P0-1, the capability's fields are public: Open.
- P0-2, the error enum is exhaustive: Open.
- P0-3, `Rights::from_bits` truncates where the common `from_bits` refuses: Open.
- P0-4, the removal functions discard what they remove: Open.
- P0-5, `size`, `capacity` and `with_size` name one number three ways: Open.
- P0-6, four names differ from the standard library's and `bitflags`' spellings: Open.
- P1-1, the crate does not package: Open.
- P1-2, the package ships the repository's scaffolding: Open.
- P1-3, no table or capability item carries an example: Open.
- P1-4, no fallible function has an `# Errors` section: Open.
- P1-5, the documentation speaks in one kernel's terms and overstates one property: Open.
- P1-6, the table has no `Debug`, and the value types lack `Hash` and `Default`: Open.
- P2-1, `Rights` prints as a number: Open.
- P2-2, the iterator has no name and costs more than the comparators': Open.
- P2-3, every method needs `O: Copy`: Open.
- P2-4, the table stores a mark that only the `peak` feature's global reports: Waiting on the
  feature-name decision of milestone 1129.
- P2-5, no attribute states that the crate has no `unsafe`: Open.
- P2-6, the manifest has no `documentation` key: Open.

## Open decisions

The one-way doors D1 to D8 below.

## Goal

A stranger writing a kernel, a hypervisor or a sandbox picks this crate for the table that holds
each program's authority. Its names read as the standard library's and `bitflags`' do.

## What the review read and ran

See [the appendix](1151-capability-table-release-review/what-was-checked.md) and
[the guidelines table](1151-capability-table-release-review/api-guidelines.md).

## Prior art

Measured from the crates.io API on 2026-11-26 (UTC). A stranger brings this crate the problem of
holding, per program, a bounded set of object references with rights that copies can only narrow.
One Rust library solves it, `ruvix-cap`, at 173 downloads in 90 days. That is under 10,000, so
the review also reads the two kernels that set the bar, seL4 and Zircon.

| crate or system | role | version read | total | 90 days | reverse dependencies | last updated |
|---|---|---|---|---|---|---|
| `ruvix-cap` | ranked 1: a capability table with rights, derivation and revocation | 0.1.0 | 740 | 173 | 4 | 2026-03-14 |
| `ruvix-types` | read with `ruvix-cap`: its `CapRights`, `Capability` and `CapHandle` | 0.1.0 | 1,987 | 563 | 21 | 2026-03-14 |
| `sel4` | neighbor: bindings to seL4's own table, which holds no table | 0.0.12 | 19,040 | 148 | 1 | 2017-04-24 |
| `fuchsia-zircon` | neighbor: bindings to Zircon handles and their rights | 0.3.3 | 30,815,567 | 6,300,124 | 1 | 2018-01-05 |
| `slotmap` | neighbor: the slot mechanics, with no rights | 1.1.1 | 142,712,815 | 44,362,978 | 628 | 2025-12-06 |
| `cap-std` | neighbor in name only, measured and not read: capabilities over operating system handles | 4.0.3 | 37,324,536 | 19,185,273 | 370 | 2026-08-20 |
| `bitflags` | integration: the vocabulary of a bit set | 2.13.2 | 2,381,414,714 | 639,300,981 | 5,623 | 2026-09-10 |
| seL4, `src/object/cnode.c` and three more files | outside Rust | 13.0.0 | | | | |
| Zircon, `zircon/kernel/object/handle_table.cc` and three more files | outside Rust | `releases/f20` at `639288a0` | | | | |

The crates.io searches in the appendix find no other library that holds such a table.

### What `capability_table` does better

- Than `ruvix-cap`: `Rights::from_bits` keeps only defined bits, where `CapRights::from_bits`
  keeps any word. Its error type implements `Display` and `core::error::Error`, and its table is
  generic over the object. A 256-slot table of
  `u64` objects is 4,136 bytes against 14,352, and it finds a free slot in at most four words.
  Twelve Kani harnesses prove the narrowing rule and the bookkeeping.
- Than `sel4` and `fuchsia-zircon`: it is the table, not a binding to a kernel that has one.
- Than `slotmap`: rights, a delegation rule and placement by slot number, with no allocation.
- Than seL4 13.0.0 and Zircon: one flat array and a bounds check, where a seL4 lookup walks
  guarded CNodes and Zircon's `HandleTable` keeps a locked list.

A reader of those systems will miss two things. The crate keeps no derivation tree, so it revokes
by a sweep over objects, where seL4's `cteRevoke` deletes one capability's children. It keeps no
generation, where `ruvix-cap` answers `StaleHandle`.

## The items

Effort is S (half a day), M (a day or two) or L (longer). Each P0 names a public item that
callers build on from 0.1.0, so its change comes before that version or not at all.

### P0: the 0.1.0 interface

#### P0-1. The capability's fields are public

Verified in source.
`Capability<O>` has two public fields, `object` and `rights`, and no constructor. A caller builds
one with a struct literal, and any code holding a `&mut Capability` can assign `rights`. The
harnesses prove `delegate` and `mint_child`, and a field assignment passes through neither. A third field added
later, such as a badge, breaks every literal. `ruvix-types`' `Capability` has public fields and a
`new`; Zircon's `Handle` keeps `rights_` private and `const`.
Change: private fields, a `const fn new(object, rights)` for the mint site, and `object()` and
`rights()` to read them. Door: one-way (D1). Effort: S.

#### P0-2. The error enum is exhaustive

Verified in source.
`Error` has five unit variants and no `#[non_exhaustive]`, and the README's BUGS section says so.
A sixth refusal, such as a stale slot, breaks every caller that matches all five, and so does
adding the attribute after 0.1.0. `ruvix-cap`'s `CapError` is exhaustive too.
Change: `#[non_exhaustive]` on `Error`. Door: one-way (D2). Effort: S.

#### P0-3. `Rights::from_bits` truncates where the common `from_bits` refuses

Verified in source and in the comparator's source.
`Rights::from_bits(bits: u32) -> Rights` drops every undefined bit. In `bitflags` 2.13.2,
`Flags::from_bits` returns `Option<Self>` and refuses an undefined bit, and the dropping form is
`from_bits_truncate`. `fuchsia-zircon`'s `Rights` is a `bitflags` type and has that meaning. A reader who knows `bitflags` expects a refusal here and
gets a silent drop. Dropping is the right default for a word from a system call register.
Change: name the function `from_bits_truncate`, and leave `from_bits` free for a later form that
returns `Option<Rights>`. Door: one-way (D3). Effort: S.

#### P0-4. The removal functions discard what they remove

Verified in source.
`delete(slot)` returns `Result<(), Error>`, though the private `empty` it calls returns the
capability. A caller that moves a capability to another table calls `get`, then `delete`. `delete_matching` returns nothing, so a sweep cannot report
how many slots it emptied. `slotmap`'s `remove` returns
`Option<V>`, Zircon's `RemoveHandle` returns the `HandleOwner`, and `ruvix-cap`'s
`DerivationTree::revoke` returns the count.
Change: `delete` returns `Result<Capability<O>, Error>`, and `delete_matching` returns the number
of slots it emptied. Door: one-way (D4), since a caller may return either result as it stands.
Effort: S.

#### P0-5. `size`, `capacity` and `with_size` name one number three ways

Verified in source.
`size()` and `capacity()` are both public and return the same value, and the constructor that
sets it is `with_size`. `capacity` is the ratified name. `slotmap`
and the standard library pair `with_capacity` with `capacity`.
Change: `size` leaves the public interface, and the constructor is `with_capacity`. Door: one-way
(D5). Effort: S.

#### P0-6. Four names differ from the standard library's and `bitflags`' spellings

Verified in source and in the comparators' source.
All four wait for ratification.

- `used()` counts the occupied slots, which the standard library, `slotmap` and `ruvix-cap` call
  `len()`. The crate has `is_empty()` and no `len()`. Milestone 1081 added no `len` because the
  function of that name counted slots, and `capacity` now answers that.
- `Rights::intersect` is `intersection` in `bitflags`, in `ruvix-types` and on the standard
  library's sets.
- `Rights::allows(needed)` is `contains` in `bitflags` and in `ruvix-types`.
- `Rights::is_subset_of(other)` is `is_subset` on the standard library's sets; `ruvix-types`
  spells it `is_subset_of`.

Change: `len`, `intersection`, `contains` and `is_subset`. Door: one-way (D6). Effort: S.

### P1: before the first release

#### P1-1. The crate does not package

Verified by building.
With `publish = false` removed in a copy, `cargo package --allow-dirty` stops: it finds no
`capability_table` in the registry. The crate depends on itself for its tests, to turn `peak` on,
and that entry carries a `version`. Change: drop the `version` key, so cargo leaves the entry out
of the published manifest; in a copy, `cargo package` then verifies and the 28 tests pass. Door: two-way. Effort: S.

#### P1-2. The package ships the repository's scaffolding

Verified by building.
`cargo package --list --allow-dirty` lists 50 files, among them `.github/`, `.githooks/`,
`deny.toml` and the twelve `falsifications/` patches. Change:
an `include` list. Door: two-way. Effort: S.

#### P1-3. No table or capability item carries an example

Verified in source (C-EXAMPLE).
The crate page and the README carry two examples, and both exercise `Rights` alone. No example
builds a `CapabilityTable`, so the first call a stranger makes has no model. Change: a crate-page
example that makes a table, inserts a capability, derives a narrower copy into a second table and
deletes the source, with `?`, and one example on `Capability::delegate`. Door:
two-way. Effort: S.

#### P1-4. No fallible function has an `# Errors` section

Verified in source and by building (C-FAILURE).
Seven public functions return a `Result`: `delegate`, `get`, `insert`, `insert_at_or_above`,
`insert_at`, `derive` and `delete`. `cargo clippy -- -W clippy::pedantic` reports the missing
section on each, and eleven functions that could carry `#[must_use]`. Change: an `# Errors` section on each of the seven, and `#[must_use]`
on the constructors and the pure accessors. Door: two-way. Effort: S.

#### P1-5. The documentation speaks in one kernel's terms and overstates one property

Verified in source.
The item documentation names things only one kernel has: a reply capability minted on every
`CALL`, a supervision rendezvous, a thread that joins a process (`Rights::BIND`). It calls
`CapabilityTable` a thread's table. The README says `Rights` has no operation that widens, and `union` is public and
widens. Nothing says that a deleted
slot's number names the next capability placed there. Change: state each item in the owner's
terms, tie the narrowing property to `delegate` and `derive`, and document slot reuse on `delete`. Door: two-way. Effort: S.

#### P1-6. The table has no `Debug`, and the value types lack `Hash` and `Default`

Verified in source (C-DEBUG, C-COMMON-TRAITS).
`CapabilityTable` derives nothing, so a struct that holds one cannot derive `Debug`. `Rights`
has neither `Hash` nor `Default`, and `Capability` lacks `Hash`. `ruvix-types`' `CapRights` has
both. Change: `Debug` on the table (the occupied slots as a map), `Hash` on
`Rights` and `Capability`, and `Default` for `Rights` as `NONE`. Door: two-way (additions).
Effort: S.

### P2: may follow

#### P2-1. `Rights` prints as a number

Verified in source (C-NUM-FMT).
`Debug` prints `Rights(5)` for `READ` and `GRANT`. `bitflags` prints the names, and implements
`Binary` and `LowerHex`. Change: `Debug` prints the names, and
`LowerHex` and `Binary` print `bits()`. Door: two-way. Effort: S.

#### P2-2. The iterator has no name and costs more than the comparators'

Verified in source; measured below (C-ITER-TY).
`iter` returns `impl Iterator`, so a caller cannot name it in a field, and `&CapabilityTable` does
not implement `IntoIterator`. It measures 2.4 ns an entry against 1.9 for `ruvix-cap` and 1.3 for
`slotmap`.
Change: a named `Iter` type, `IntoIterator` for `&CapabilityTable`, and one read per slot. Door:
two-way. Effort: S.

#### P2-3. Every method needs `O: Copy`

Verified in source.
The `impl` block that holds the constructors and every method requires `O: Copy`. An owner whose
object owns something, such as a counted reference, cannot make a table at all. Zircon's `Handle` holds a `RefPtr<Dispatcher>`, and
`slotmap` takes any value and lends `&V`. Change: drop the bound where no copy happens, and add a
`get` that lends. Door: two-way,
since relaxing a bound breaks no caller. Effort: M.

#### P2-4. The table stores a mark that only the `peak` feature's global reports

Verified in source (C-CUSTOM-TYPE).
Every table keeps a 16-bit high-water mark, with or without the feature, and no public function
reads it. The `peak` feature adds `highest_seen() -> (usize, usize)`, one value for every table in
the program, and only where the target has 32-bit atomics. The pair's order is in the
documentation alone. `ruvix-cap` keeps its counters
per manager. Change: a public per-table read of the mark, a
named pair for `highest_seen`, and the name the feature-name decision of milestone 1129 picks. Door: two-way (additions, and the feature is off by default). Effort: S.

#### P2-5. No attribute states that the crate has no `unsafe`

Verified in source.
The crate has no `unsafe`, and `src/lib.rs` does not say so. Change: `#![forbid(unsafe_code)]`,
as `ruvix-cap` carries. Door: two-way. Effort: S.

#### P2-6. The manifest has no `documentation` key

Verified in `Cargo.toml` (C-METADATA).
Change: add it. Door: two-way. Effort: S.

### Measured performance

The table's cost per operation on a Linux x86_64 host, against `ruvix-cap` 0.1.0 and `slotmap`
1.1.1. Each table has room for 256 and holds 128 before the timed part. A range spans three runs,
and the appendix gives the method.

| operation | `capability_table` | `ruvix-cap` | `slotmap` |
|---|---|---|---|
| look up one of 128 | 1.20 ns | 1.36 to 1.40 ns | 1.15 to 1.21 ns |
| look up and derive a narrower copy | 1.65 to 1.68 ns | 3.90 to 3.99 ns | no such operation |
| insert one, then delete it | 8.07 to 8.21 ns | 8.97 to 9.14 ns | 7.01 to 7.69 ns |
| insert 128 more, then delete them, per operation | 3.44 to 3.53 ns | 7.77 to 7.92 ns | 4.13 to 4.28 ns |
| iterate, per entry | 2.36 to 2.40 ns | 1.91 to 1.93 ns | 1.33 to 1.37 ns |

The table matches both on a lookup, halves `ruvix-cap`'s time on a derive and on a run of
inserts, and is the slowest on iteration (P2-2).

## One-way doors

- D1, the capability's fields (P0-1). Recommended: private fields with `new`, `object()` and
  `rights()`, the stricter choice. A public field can come back later.
- D2, the error enum (P0-2). Recommended: `#[non_exhaustive]`, the stricter choice; removing the
  attribute later breaks no caller.
- D3, the meaning of `from_bits` (P0-3). Option A: rename to `from_bits_truncate`. Option B: keep
  `from_bits` as the truncating form. Recommended: A, which matches `bitflags` and leaves the
  short name for the refusing form.
- D4, what removal returns (P0-4). Recommended: the capability and the count. The name `delete`
  matches seL4's `CNode_Delete`; the standard library's word is `remove`, and the architect picks.
- D5, one name for the table's size (P0-5). Recommended: `capacity` alone and `with_capacity`.
- D6, the four spellings (P0-6). Recommended: all four. The closest call is `is_subset_of`,
  which `ruvix-types` shares.
- D7, the slot number's type. Every function takes and returns a bare `u64`. `ruvix-cap` and
  `slotmap` return a key type that carries a generation; seL4 and Zircon use plain words. Recommended: keep
  `u64`. A newtype that any caller builds from a register proves nothing, and the table checks a
  slot number on every use.
- D8, the rights vocabulary. `Rights` is a closed set of six, and `from_bits` drops every other
  bit, so an owner cannot carry a right of its own.
  seL4 fixes four, Zircon 25 and `ruvix-types` seven. Option A: keep the six, and say that bits 6
  to 30 are the crate's to assign. Option B: a rights type the owner supplies. Recommended: A, the stricter choice and the one every comparator makes; a later release can add
  a right and cannot remove one.

## Evidence for the shared decisions

- **Errors.** The crate: one enum, `Error`, with five unit variants, `Display` and
  `core::error::Error`, exhaustive (P0-2), carrying no input. The comparators: `ruvix-cap`'s `CapError` (`src/error.rs`) derives `Debug`
  and has `as_str`, with no `Display`; `slotmap` returns `Option` and has no error type;
  `fuchsia-zircon` returns the kernel's `Status`. Points toward one enum per crate with `Display`,
  `core::error::Error` and `#[non_exhaustive]`; the crate conforms once P0-2 lands.
- **DMA regions, doorbells and tails, register access, byte sinks and sources, simulators.** Not
  applicable: the crate touches no device and moves no bytes.
- **Feature names.** The crate: one feature, `peak`, off by default, a provisional name, adding
  one function and one `static`. The comparators: `ruvix-cap` has `alloc`, `std`, `audit-log` and
  `metrics`, the last for the same kind of counters; `slotmap` has `std` and `unstable`;
  `bitflags` has `std` and `serde`. Points toward a feature named for what it adds, and toward a
  rule that a feature adding a process-wide `static` says so (P2-4).
- **Contract layout.** Not applicable: the crate exports no interface identity, version or magic.

## Follow-on

- **Outstanding.** The feature-name decision of milestone 1129 takes P2-4.

## Done when

The `capability_table` review ends once its P0 and P1 items read Done or Will not fix, D1 to D8
have rulings, and `script/review-status` lists BUILT.

## BUGS

- The ranked comparison is with a crate few use, and the review read seL4 and Zircon and ran
  neither.
- The benchmark stores a 16-byte capability here and `ruvix-cap`'s 56-byte entry there.
- The Zircon reading is of a release branch's head, named by its commit, not of a tag.

## Index row

The release review of `capability_table` against `ruvix-cap`, seL4 and Zircon. Six one-way
interface changes come before 0.1.0; the crate does not package today; a lookup measures 1.2 ns;
eight doors wait.
