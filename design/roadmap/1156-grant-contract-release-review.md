---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1094, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1156. `grant_contract`: the release review's findings

*(The number and the slug are provisional.)*

The release review of `partsfoundry/grant_contract` at commit `f84cd7e6`, version 0.1.0, under
milestone 1129 (the combine review), whose [block](1129-crate-interfaces-best-in-class.md) sets its
form. The crate split out of the crate that milestone 1094 (`grant_plan`: what an outside
maintainer would fix before it leaves) reviewed, and has no outside review of its own. The
baseline is [1094's block](1094-grant-plan-outside-review.md) and the cleared package
[`notes/crate-reviews/grant-contract.md`](../../notes/crate-reviews/grant-contract.md). The crate
boundary, the crate's name, interface identity 17 and the ratified names stay closed here. This
review also checks the floor the outside reviews set.

Reuse: the crate's own tests and one scratch crate. No new tool.

## Finding status

- P0-1, a verb table is a bare slice of `&'static str` entries that nothing checks: Open.
- P0-2, an empty verb table means the whole manifest: Open.
- P0-3, a manifest can name any slot for its diagnostic stream: Open.
- P0-4, the checks answer `bool` and `Option`, and the manifest check holds one rule: Waiting on the errors decision of milestone 1129.
- P0-5, every verb item has two paths: Open.
- P0-6, `delegated_identity` copies into an out-parameter and returns a length: Open.
- P0-7, the memory range carries no unit: Open.
- P0-8, seven fields say their names are provisional: Open.
- P0-9, `VERSION` says it covers the slot numbers, and the crate fixes more: Waiting on the contract-layout decision of milestone 1129.
- P1-1, the documentation names about sixty items a stranger cannot find: Open.
- P1-2, the README omits three things the crate's own stranger test asks for: Open.
- P1-3, the dependency is a git revision: Open.
- P1-4, missing common traits and set operations: Open.
- P1-5, two examples in the crate, and no `# Panics` heading: Open.
- P1-6, two narrowing rules live in a code comment: Open.
- P2-1, no proof covers the functions that read a page: Open.
- P2-2, names for the authorities: Open.
- P2-3, no test pins the rights numbers: Open.
- P2-4, the package carries the repository's tooling: Open.
- P2-5, the manifest has no `documentation` key: Open.
- P2-6, two getters are not `const`: Open.

## Open decisions

The one-way doors D1 to D10 below.

## Goal

A stranger building a system where a program holds only what its spawner hands it picks this
crate for the declaration. A manifest or a verb table that breaks a rule draws a refusal that
names the rule. A planner, a spawner and a program compile the same numbers, and the crate says
which numbers its version covers.

## What the review read and ran

[The appendix](1156-grant-contract-release-review/what-was-checked.md) lists the files, the
commands, the scratch crate, each comparator and the measurement's method.
[The guidelines table](1156-grant-contract-release-review/api-guidelines.md) marks the 54 API
Guidelines items: 17 met, 13 not met, 24 not applicable.

### The floor the outside reviews set

- **A stranger builds and tests from the README.** Met, on rustc 1.100.0, on the stated minimum
  1.88 and on the three bare targets.
- **A stranger proves from the README.** Not run: no Kani here. The harness count matches the
  source, and the README omits three required things (P1-2).
- **The documents match the code.** Met for the README. Not met for the item documentation
  (P1-1, P0-8).
- **The names follow [design/naming.md](../naming.md).** Read by hand. One finding: a quantity
  without its unit (P0-7).
- **Nothing one-way ships that a later release must take back.** Not met: P0-1 to P0-9.

## Prior art

Measured from the crates.io API on 2026-11-26 at 22:52 (UTC). The problem: a program declares
what it may hold, a spawner endows from the declaration, and one part of the program (a verb, a
command, a mode) holds less than the whole. Three Rust crates solve it for other platforms. None
is `no_std`, so the review also read OpenBSD's `pledge`, the best-known system where a program
states its own authority and narrows it by what its command line asked.

| crate or system | role | version read | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `tauri-utils` (its `acl` module) | ranked 1: permissions per command, which a capability file gives a window | 2.10.4 | 49,151,367 | 20,765,017 | 36 | 2026-11-18 |
| `deno_permissions` | ranked 2: a program's permission set, narrowed for a child | 0.119.0 | 961,864 | 254,712 | 37 | 2026-10-21 |
| `pledge` | ranked 3: a binding to OpenBSD's promises | 0.4.2 | 64,444 | 5,033 | 15 | 2021-06-16 |
| `landlock` | neighbor, measured and not read: enforces a rule set on Linux | 0.4.8 | 22,718,128 | 8,167,361 | 206 | 2026-11-20 |
| `bitflags` | integration: the flag-set vocabulary | 2.13.2 | 2,381,414,714 | 639,300,981 | 5,623 | 2026-09-10 |
| OpenBSD `sys/sys/pledge.h`, `sys/kern/kern_pledge.c`, `pledge(2)` | outside Rust: the promise set and its narrowing | commit `2bdf38a9` | | | | |
| OpenBSD `bin/rm/rm.c`, `usr.bin/ftp/main.c` | outside Rust: programs that narrow by their options | commit `2bdf38a9` | | | | |

The downloads of `tauri-utils` count every use of that crate, and `acl` is one module of it. The
appendix measures two more neighbors.

### What `grant_contract` does better

- Than `tauri-utils`: a manifest is a `Copy` value of 80 bytes that a constant can hold, with no
  allocation, no `std` and one dependency. `tauri-utils` 2.10.4 keeps `String`, `Vec` and
  `BTreeMap` fields and declares 35 dependencies, optional ones included. Its `Permission` derives
  `Default`, so a field left out is a silent choice.
- Than `deno_permissions`: the declaration is the program's own, and a planner reads it before
  the program runs. `PermissionsOptions` is eighteen optional lists and a flag, set at each launch.
- Than `pledge`: the authorities are constants of a type, where the binding passes a string the
  kernel parses. The narrowing is a pure function that Kani proves never widens.
- Than OpenBSD: the spawner narrows before the program runs, so `list` never holds the network.
  `rm.c` runs with its full authority until its own `pledge` call.

## The items

Effort is S (half a day), M (a day or two) or L (longer). A caller outside the repository acts on
a one-way item once 0.1.0 is out, so each P0 lands in 0.1.0 or not at all.

### P0: the 0.1.0 interface

#### P0-1. A verb table is a bare slice of `&'static str` entries that nothing checks

Verified in source (`src/verbs.rs`) and by building a scratch crate.
`VerbGrant::verb` is a `&'static str`. The crate's documentation says a verb table also travels
as bytes, sixteen to a verb, so a decoder must leak memory to build one. `ShortOptions` holds its
letters inline for that stated reason, and its constructors check its rules. A verb table has no
constructor and no check. Four mistakes compile and run. A verb of 26 bytes can
match no page. An empty verb passes. The same verb twice lets the first entry win. A verb with an
authority its manifest does not declare narrows to nothing without a word.
`tauri-utils` validates each `Identifier` through `TryFrom<String>` with seven named refusals.
OpenBSD's `parsepledges` returns `EINVAL` for a name it does not know, and `sys_pledge` returns
`EPERM` for a widening. `deno_permissions` returns `ChildPermissionError::Escalation`.
Change: a verb held inline as a checked value of at most `MAXIMUM_VERB_BYTES`, with a `const`
constructor, and one check of a table against its manifest (names provisional). The check refuses
a long, empty or repeated verb, a second space, and an authority the manifest does not declare.
`narrow_by_verb` has a clear receiver and can become a method then. Door: one-way (D2).
Effort: M.

#### P0-2. An empty verb table means the whole manifest

Verified in source and by building.
`narrow_by_verb` returns the manifest whole for an empty table, and keeps no verb-chosen field for
a verb the table lacks. A spawner whose decoder yields
an empty table for a damaged record endows everything the manifest declares. `tauri-utils` allows
a command only when a permission lists it (`acl/resolved.rs`), and `pledge(2)` says an empty
promise string leaves the process `_exit` alone.
Change: an empty table narrows to nothing, like any table without the verb. A caller whose
program has no verbs does not call the function. Door: one-way (D3). Effort: S.

#### P0-3. A manifest can name any slot for its diagnostic stream

Verified in source (`src/manifest.rs`) and by building.
`OutputDeclaration::BytesAndDiagnostics { slot: u64 }` carries a slot number. The documentation of
`DIAGNOSTICS_SLOT` says every declarer shares that one constant. A manifest that writes
`slot: ENTROPY_SLOT` compiles, and `is_well_formed` accepts it.
Change: the variant drops its field, and `diagnostics_slot` answers `DIAGNOSTICS_SLOT`. Door:
one-way (D4). Effort: S.

#### P0-4. The checks answer `bool` and `Option`, and the manifest check holds one rule

Verified in source and by building.
`Manifest::is_well_formed` returns `bool` and checks one rule, the widening option. A memory range
whose `minimum` exceeds its `maximum` passes. `ShortOptions::try_new` returns `None` for three
causes: too many letters, a byte that is no letter or digit, and a repeat. A caller that reports a
bad manifest to a person cannot say which rule broke. `tauri-utils` has
`Error::UnknownPermission { key, permission }`, and the kernel separates `EINVAL` from `EPERM`.
Change: a check that returns `Result` with one variant per rule (names provisional), in the shape
the errors decision of milestone 1129 picks. It gains the range rule and the rules of P0-1.
`is_well_formed` may stay beside it. Door: one-way (D5). Effort: S.

#### P0-5. Every verb item has two paths

Verified in source (`src/lib.rs`) and by building.
`pub mod verbs` is public, and the crate root re-exports its seven items, so
`grant_contract::verbs::narrow_by_verb` and `grant_contract::narrow_by_verb` both compile. The
`manifest` module is private. The cleared package lists both module names as provisional.
Change: `verbs` becomes private, so each item has one path and no module name needs a ruling.
Door: one-way (D6). Effort: S.

#### P0-6. `delegated_identity` copies into an out-parameter and returns a length

Verified in source and in the dependency's source (C-NO-OUT).
`delegated_identity(page, out: &mut [u8; 32]) -> Option<usize>` copies a word of the page into
`out`. The page iterator of `program_argument_contract` yields slices that borrow the page, so the
function can return `Option<&[u8]>` and copy nothing. The bound 32 and the word `--within` are literals with no public constant.
Change: return the borrowed name, and export the bound and the option word as constants (names
provisional). Whether the function belongs here is D7. Door: one-way (D7). Effort: S.

#### P0-7. The memory range carries no unit

Verified in source.
`MemoryGrantDeclaration::Required { minimum, maximum }` counts pages, as its documentation says.
[design/naming.md](../naming.md) ends a name that holds a quantity with its unit. The cleared
package counts 71 ratified names and does not list them, so these two fields may be among them.
Change: `minimum_pages` and `maximum_pages`. Door: one-way (D8). Effort: S.

#### P0-8. Seven fields say their names are provisional

Verified in source.
The documentation of `network`, `machine`, `share`, `reboot`, `installer`, `catalog` and `indexes`
ends with a line that calls the field name provisional. One adds what a draft called it. The
cleared package counts the manifest's names as ratified on 2026-11-20 (UTC). A stranger learns that seven names of 0.1.0 may change.
Change: the architect confirms the seven or renames them before 0.1.0, and the markers go either
way. Door: one-way (D8). Effort: S.

#### P0-9. `VERSION` says it covers the slot numbers, and the crate fixes more

Verified in source and in the census of milestone 1129.
The documentation of `VERSION` and `INTERFACE_ID` names the capability slot numbers alone. The
crate also fixes the twelve authority bits, which its own text says a verb record carries. It
fixes the sixteen-byte verb, the sixteen option letters, the five rights numbers and a virtual
address. A reader cannot tell whether a thirteenth bit is a new version.
Change: one paragraph beside `VERSION` that lists every number the version covers and what counts
as a break, in the form the contract-layout decision of milestone 1129 picks. Door: one-way (D9).
Effort: S.

### P1: before the first release

The six P1 items are in
[the appendix](1156-grant-contract-release-review/before-the-release.md).

### P2: may follow

The six P2 items are in [the later items](1156-grant-contract-release-review/later-items.md).

### Measured performance

Measured in a release build with rustc 1.100.0 on a Linux x86_64 host, lowest of seven passes. No
comparator ran: each one parses text into allocated collections, so a ratio would compare formats.
The method is in [the appendix](1156-grant-contract-release-review/what-was-checked.md#the-measurement).

| operation | time |
|---|---|
| `narrow_by_verb`, eight verbs, a two-word key in the last entry | 23.7 ns |
| `narrow_by_verb`, eight verbs, a miss that falls back to the first word | 30.6 ns |
| `page_verb`, a page of five words | 37.9 ns |
| `delegated_identity`, the same page | 39.7 ns |
| `ShortOptions::try_new`, sixteen letters | 137.7 ns |

A `Manifest` is 80 bytes. The interface shapes no cost that matters: each operation runs once
for each line a person types.

## One-way doors

- D1, the manifest's shape. `Manifest` has 24 public fields and no default, and no enum is
  `#[non_exhaustive]`. `tauri-utils` and `deno_permissions` give every field a default.
  Recommended: keep it as built, and say in the README that each new field or variant is a
  breaking release. This is the looser choice by the guidelines, and the reason is misuse. A
  planner that matches every variant must fail to compile when a grant it has not weighed appears.
- D2, the verb table's type (P0-1). Recommended: inline checked verbs and a checked table, the
  stricter choice. Opening the fields later is compatible, and closing them after 0.1.0 is not.
- D3, what an empty table means (P0-2). Recommended: it keeps nothing, and the caller says when a
  program has no verbs. A later release can relax this and cannot tighten it.
- D4, the diagnostic slot's field (P0-3). Recommended: drop the field, the stricter choice.
- D5, the shape of a refused manifest (P0-4). Recommended: a `Result` with one variant per rule,
  `#[non_exhaustive]`, decided once by the errors decision.
- D6, the module paths (P0-5). Recommended: one path, at the crate root.
- D7, `delegated_identity` (P0-6). It reads a protocol between an installer and its client, not
  a grant declaration. Recommended: leave it out of 0.1.0, with the code that serves the
  installer. Adding it later is compatible. If it stays, it takes the borrowed signature.
- D8, the names (P0-7, P0-8). Recommended: `minimum_pages` and `maximum_pages`, and a ruling on
  each of the seven fields. `WordGrant` and `VerbGrant` name parts of a declaration with the
  naming page's word for what a program gets; the review recommends keeping both.
- D9, what `VERSION` covers (P0-9). Recommended: every number a second party compiles in, listed
  beside the constant, decided once by the contract-layout decision.
- D10, the slot type. The slot constants, the diagnostic slot and the rights are bare `u64`
  values (C-NEWTYPE). Recommended: keep `u64`. The crate depends on no kernel interface crate
  that owns a slot type.

## Evidence for the shared decisions

- **Errors.** The crate has no error type. Seven public functions return `Option`, and
  `is_well_formed` returns `bool` (P0-4). `tauri-utils` uses `thiserror` enums with named fields
  (`acl::Error`, `ParseIdentifierError`), and so does `deno_permissions`
  (`ChildPermissionError`). The `pledge` crate has one enum with `Display` and `Error`. The
  evidence points to an enum that names the rule broken wherever a check can fail for more than
  one reason. `Option` stays right where absence is an answer, as in `diagnostics_slot`.
- **Direct memory access regions, doorbells and tails, register access, simulators.** Not
  applicable: the crate holds no hardware and no test double.
- **Byte sinks and sources.** `page_verb` and `delegated_identity` take a page as `&[u8]` and
  write into fixed arrays; the crate declares no trait. The evidence points to plain slices, and
  to returning a borrow of the input where one exists (P0-6).
- **Feature names.** The manifest declares none.
- **Contract layout.** The crate exports `INTERFACE_ID` (a `u64`, 17) and `VERSION` (a `u32`, 1)
  at its root, and no magic. It has no page and no byte layout of its own. The census lists `new`
  and `try_new` as its entry points; both are constructors of `ShortOptions`, and the crate has no
  encoder or decoder. Its contract is numbers that three parties compile in: slot numbers,
  authority bits, limits, rights and one address (P0-9). `ManifestAuthorities::from_bits` is the
  one decode rule, and it refuses an unknown bit, as OpenBSD's `parsepledges` refuses an unknown
  name. `pledge.h` is the same kind of contract: one header of bits and names, with no version.
  The evidence points to a layout that allows a contract of constants, with an identity and a
  version and no magic or codec, and that requires a statement of what the version covers.

## Follow-on

- **Outstanding.** The shared decisions of milestone 1129 take D5 and D9.
- **Outstanding.** The doors D1 to D4, D6 to D8 and D10, for the architect.

## Done when

The block reads BUILT in `script/review-status`: each P0 and P1 line above says Done or Will not
fix, and D1 to D10 each carry a ruling.

## BUGS

- No comparator ran. The measurement shows this crate alone.
- The review read `tauri-utils`'s `acl` module alone, and measured the neighbors without reading
  them.
- The OpenBSD sources are the head of its tree on the day, not a release.
- Kani and the name-check helper did not run, so the proof and naming parts of the floor rest on
  reading.

## Index row

The release review of `grant_contract` against `tauri-utils`, `deno_permissions`, `pledge` and
OpenBSD's promises. Nine one-way changes come before 0.1.0, among them a checked verb table and a
check that names the rule a manifest breaks. Six fixes land before the release, six may follow,
and ten doors wait.
