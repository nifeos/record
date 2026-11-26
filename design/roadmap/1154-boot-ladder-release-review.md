---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1078, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1154. `boot_ladder`: the release review's findings

*(The number and the slug are provisional.)*

The release review of `partsfoundry/boot_ladder` at commit `019d76c8`, version 0.1.0
(unpublished), under milestone 1129 (the combine review), whose
[block](1129-crate-interfaces-best-in-class.md) sets its form. The baseline is
milestone 1078 (what an outside maintainer would fix before it leaves),
[its block](1078-boot-ladder-outside-review.md) and the cleared package
[`notes/crate-reviews/boot-ladder.md`](../../notes/crate-reviews/boot-ladder.md). 1078's rulings
stand: the nine printed shapes, the fifteen printed check names and the eleven public names
ratified on 2026-11-19. No naming rule added since touches them. 1078 left the names in `verdict`
and the head types to the release name review, which is this one (P0-6).

Reuse: the crate's own tests, and a scratch crate that probes the interface and times the matcher.

## Finding status

- P0-1, a check is a bare `usize`: Open.
- P0-2, the reader accepts verdicts the writer cannot print: Open.
- P0-3, a damaged verdict and no verdict are the same `None`: Waiting on the errors decision of
  milestone 1129.
- P0-4, `Outcome`, `CheckLine` and `SubjectLine` are exhaustive: Open.
- P0-5, `ParsedVerdict` mixes public fields with getters: Open.
- P0-6, the provisional names in `verdict` and the head types: Open.
- P0-7, `Heads::new` takes a name no reader can key on: Open.
- P1-1, no function says whether a total is a known one: Open.
- P1-2, the crate page has no example, and no item has one: Open.
- P1-3, three printing types have no `Debug`, and no type has `Hash`: Open.
- P1-4, the package ships the repository's machinery: Open.
- P1-5, the matchers read `&str` only: Open.
- P2-1, no item lists the rungs in order: Open.
- P2-2, the check line has a printer and no reader: Open.
- P2-3, `find_in` over a whole transcript: Open.
- P2-4, a parsed verdict does not convert to a `Tally`: Open.
- P2-5, the manifest, `#[must_use]` and a getter for the name: Open.

## Open decisions

The one-way doors D1 to D9 below.

## Goal

A stranger who writes a kernel's boot self-test, or the program that reads its serial log, takes
this crate and holds the same bytes on both sides. The types refuse a check off the list, and the reader refuses a
verdict the writer could not have printed.

## What the review read and ran

[The appendix](1154-boot-ladder-release-review/what-was-checked.md) holds the crate's files, the
commands, the probe, the benchmark method and each comparator file read.
[The guidelines table](1154-boot-ladder-release-review/api-guidelines.md) marks the 54 items, and
[the comparison](1154-boot-ladder-release-review/comparison.md) sets the crate beside its
neighbors axis by axis.

## Prior art

Measured from the crates.io API on 2026-11-26 at 22:27 (UTC). The crate's problem is that the
program that boots and the program that reads its console must agree on the boot's lines. No Rust
crate solves it: seventeen searches found none, so every row is a neighbor. The bar
is outside Rust: the Linux kernel's KTAP format and the parser that reads it off a console.

| crate or system | role | version read | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `sd-notify` | neighbor: a readiness line, writer only | 0.5.0 | 18,719,977 | 4,783,089 | 71 | 2026-03-09 |
| `expectrl` | neighbor: a reader matching a needle in console bytes | 0.9.0 | 1,143,950 | 446,088 | 72 | 2026-05-11 |
| `rexpect` | neighbor: the same reader job | 0.7.2 | 2,307,147 | 429,949 | 77 | 2026-11-26 |
| `embedded-test` | neighbor: on-target results sent to a host runner | 0.7.3 | 617,409 | 136,911 | 9 | 2026-10-30 |
| `testanything` | neighbor: a TAP writer | 0.4.3 | 25,370 | 1,578 | 2 | 2026-04-26 |
| `tap_parser` | neighbor: a TAP reader | 0.1.1 | 3,881 | 87 | 1 | 2023-04-08 |
| `libtest-mimic` | measured, not read: a host test harness | 0.8.2 | 36,772,461 | 7,059,104 | 353 | 2026-03-16 |
| Linux KTAP, `Documentation/dev-tools/ktap.rst` | outside Rust: the format | v6.12 | | | | |
| Linux `tools/testing/kunit/kunit_parser.py` | outside Rust: its console reader | v6.12 | | | | |

### What `boot_ladder` does better

The grammar is code that the writer and every reader link, with no `std` and no allocation, and
Kani proves its reader free of overflow and panics. No neighbor has all three.
[The comparison](1154-boot-ladder-release-review/comparison.md#what-boot_ladder-does-better)
takes each neighbor in turn.

## The items

Effort is S (half a day), M (a day or two) or L (longer). A door is one-way when code outside the
repository depends on the answer after 0.1.0, which is why a P0 cannot wait for a later release.

### P0: the 0.1.0 interface

#### P0-1. A check is a bare `usize`

Verified in source (`src/verdict.rs`) and by running the probe.
`verdict::check(name)` returns a `usize`, and `Tally::record` and `Tally::is_recorded` take one.
`record(20, Outcome::Passed)` on a full tally prints `example self-test: 16 of 15 passed`.
`record(64, Outcome::Failed)` panics in a debug build and in a release build wraps and fails
check 0. `record` documents no panic. `CheckLine::name` and `SubjectLine::check` are `&str`, so a
line can name a check the list does not hold.
Change: a `Check` type (name provisional) with a private index, which `check(name)` returns in a
`const` and an iterator over the list yields. `record`, `is_recorded`, `CheckLine` and
`SubjectLine` take it. Door: one-way (D1). Effort: S.

#### P0-2. The reader accepts verdicts the writer cannot print

Verified by running the probe against `ParsedVerdict::parse`.
`parse` returns a verdict for `99 of 3 passed`, for `1 of 2 passed, 5 FAILED: a` (a count of five
over one name) and for `1 of 2 passed, 1 FAILED: a  b` (a count of one, two names). `Verdict`
prints none of these, and a serial link that drops bytes produces such lines. `kunit_parser.py` and
`tap_parser` both check the plan against the results.
Change: `parse` refuses a tail in which a count differs from the number of names after it, names
are separated by anything but one space, or passed, absent and failed together exceed the total.
Door: one-way (D2). Effort: S.

#### P0-3. A damaged verdict and no verdict are the same `None`

Verified in source.
`ParsedVerdict::in_line` returns `None` when the line holds no verdict head and also when the head
is there and the tail is not the grammar. A reader walking a transcript skips both, so a
corrupted verdict line reads as a boot that printed none. For `Head::find_in` and
`strip_prefix_of` absence has one cause and `Option` is right. `kunit_parser.py` has
`FAILURE_TO_PARSE_TESTS` apart from `NO_TESTS`, and `tap_parser` returns an `Error` naming the
cause.
Change: `in_line` keeps `None` for a line with no head and returns a refusal, in the shape the
errors decision of milestone 1129 picks, for a head whose tail does not parse. `parse` returns
the same refusal. Door: one-way (D3). Effort: S.

#### P0-4. `Outcome`, `CheckLine` and `SubjectLine` are exhaustive

Verified in source.
`Outcome` has three variants and no `#[non_exhaustive]`, so a fourth outcome, such as a check
that ran out of time, breaks a caller's `match`. `CheckLine` and `SubjectLine` have three public
fields each, and a caller builds them by struct literal, so a new field breaks every printer.
Change: `#[non_exhaustive]` on `Outcome`; a constructor and private fields on `CheckLine` and
`SubjectLine`. Door: one-way (D4). Effort: S.

#### P0-5. `ParsedVerdict` mixes public fields with getters

Verified in source.
`passed` and `total` are public fields; the absent and failed counts are the methods
`absent_count` and `failed_count`.
Change: private fields, with `passed_count` and `total` as methods (names provisional). Door:
one-way (D5). Effort: S.

#### P0-6. The provisional names in `verdict` and the head types

Verified in source and in the cleared package's name table, which lists them: the head types and
their methods, the module `verdict`, and its types, constants, functions and sixteen methods.
Read against [design/naming.md](../naming.md) and the comparators, three stand out:

- `verdict::CHECKS` is a count, and `boot_ladder::SELF_TEST_CHECKS` is the list. The ratified
  `EARLIER_SELF_TEST_CHECK_COUNTS` names earlier values of the same quantity. Recommended:
  `SELF_TEST_CHECK_COUNT`.
- `ParsedVerdict::in_line` is a constructor that searches, and `Head::find_in` is the crate's own
  word for a search. Recommended: `ParsedVerdict::find_in`.
- `subject_thread(heads, line)` is a free function with a receiver (C-METHOD). Recommended: an
  associated function on `SubjectLine`, such as `SubjectLine::thread_in`.

Every other name passes the rules in force.
Change: the architect ratifies the list, with or without the three renames. Door: one-way (D6).
Effort: S.

#### P0-7. `Heads::new` takes a name no reader can key on

Verified by running the probe.
`Heads::new("")` builds heads that are the bare shapes, and its `banner`, ` on `, is found in
ordinary prose. A name holding a space, a control character or a line break builds a head that a
reader of one line cannot find.
Change: `Heads::new` stays `const` and panics on an empty name and on one holding white space or
a control character, as `check` does for an unlisted name, with a `# Panics` section. Door:
one-way (D7), since refusing these names later would break a caller that passed one. Effort: S.

### P1: before the first release

#### P1-1. No function says whether a total is a known one

Verified in source.
The README tells a reader to fail a verdict whose total is neither the list's length nor one of
`EARLIER_SELF_TEST_CHECK_COUNTS`. No function does it, and a reader that forgets takes
`0 of 0 passed` as green. Change: a method on `ParsedVerdict` that answers it (name provisional),
used in the README's example. Door: two-way. Effort: S.

#### P1-2. The crate page has no example, and no item has one

Verified in source and by `cargo doc`.
`src/lib.rs` includes the README only under `cfg(doctest)`, so its two examples render nowhere.
No public item carries an example, and the printing side (`Tally`, `CheckLine`, `SubjectLine`)
appears in none, the README's included. The README's examples use `unwrap`. Change: an example on the crate page that
records a tally, prints the verdict and reads it back, and one each on `Heads`, `Head::find_in`,
`Tally` and `ParsedVerdict`. Door: two-way. Effort: S.

#### P1-3. Three printing types have no `Debug`, and no type has `Hash`

Verified in source (C-DEBUG, C-COMMON-TRAITS).
`Verdict`, `CheckLine` and `SubjectLine` derive nothing. `Heads`, `Head`, `Outcome`, `Tally` and
`ParsedVerdict` derive no `Hash`, so none keys a map. Change: `Debug`, `Clone` and `Copy` on the
three, and `Hash` on the five. Door: two-way. Effort: S.

#### P1-4. The package ships the repository's machinery

Verified by building: `cargo package --list --allow-dirty` lists 41 files, 18 of them under
`.github/`, with the commit hook, `CODEOWNERS`, `deny.toml` and the stranger-test record. The
manifest has no `include`. Change: an `include` naming `src/`, the README, the changelog, both
licenses and, if the proofs are to replay from the package, `falsifications/`. Door: two-way.
Effort: S.

#### P1-5. The matchers read `&str` only

Verified in source.
The matching rule exists because a serial link corrupts bytes, and corrupted bytes are often not
UTF-8. A reader with an allocator converts lossily first; a `no_std` reader with none, which the
crate serves, cannot. `expectrl`'s `Needle::check` takes `&[u8]`. Change: byte-slice forms
of the matchers beside the `&str` ones (names provisional). Door: two-way. Effort: S.

### P2: may follow

#### P2-1. No item lists the rungs in order

Verified in source.
The crate's name is a ladder, and only prose states the order of its rungs, across five
doc comments. Change: a method that yields the rungs in order, without the two heads that are
not rungs. Its name is the architect's. Door: two-way. Effort: S.

#### P2-2. The check line has a printer and no reader

Verified in source.
`CheckLine` prints a line nothing reads back, and its words `ok`, `FAILED` and `absent` are
literals inside `fmt`.
Change: a reader for the check line, and the three words as items. Door: two-way. Effort: S.

#### P2-3. `find_in` over a whole transcript

Verified by measurement.
`find_in` tries every character boundary. The interface does not force that. Change: the faster search, or a
sentence saying the matcher is for one line. Door: two-way. Effort: S.

#### P2-4. A parsed verdict does not convert to a `Tally`

Verified in source.
A reader comparing a read verdict with an expected tally maps each name through `check`, which
panics on a name it does not know. Change: a fallible conversion for a verdict whose total is the
current list's. Door: two-way. Effort: S.

#### P2-5. The manifest, `#[must_use]` and a getter for the name

Verified in source.
`Cargo.toml` has no `documentation` key, and its categories omit `no-std::no-alloc`. No function
carries `#[must_use]`. `Heads` gives no way to read its name. Change: each. Door: two-way.
Effort: S.

### Measured performance

On one 86-byte line `Head::find_in` takes 16.8 ns, against 74.0 ns for `str::find` on the joined
head and 26.7 ns for `expectrl` 0.9.0. Over a 65,687-byte transcript it takes 254 µs against
14.1 µs and 121 µs (P2-3). The host, the inputs and the full table are in
[the appendix](1154-boot-ladder-release-review/what-was-checked.md#the-benchmark).

## One-way doors

- D1, a type for a check (P0-1). Recommended: the `Check` type with a private index. A later
  release can add a way to build one from a number; it cannot take `usize` back.
- D2, how strict the reader is (P0-2). Recommended: refuse every tail the writer cannot print.
  Accepting more later breaks no reader; refusing more later does.
- D3, what a damaged verdict returns (P0-3). Recommended: `None` for no head and a refusal for a
  bad tail, in the shape the errors decision picks.
- D4, exhaustive types (P0-4). Recommended: `#[non_exhaustive]` on `Outcome`, and constructors
  with private fields on `CheckLine` and `SubjectLine`.
- D5, `ParsedVerdict`'s fields (P0-5). Recommended: private, with getters.
- D6, the provisional names (P0-6). Recommended: ratify as built, with the three renames.
- D7, what `Heads::new` refuses (P0-7). Recommended: a compile-time panic for an empty name and
  for one with white space or a control character.
- D8, whose check list this is. The name is the caller's; the fifteen check names and the shapes
  ` capability shell` and `: the capability core runs on ` are one system's, ratified by 1078 as
  printed. KTAP and the TAP crates carry any test's name, so a stranger with another kernel can
  take them and cannot take this list. Recommended: keep the fixed list and shapes at 0.1.0, and
  say on the crate page and in the manifest's description that the crate carries one system's
  ladder. A general form, with the list passed as the name is, can join later as new types.
  Whether such a crate belongs on crates.io is the architect's to say here.
- D9, no version and no room to grow in the line. `parse` refuses any text after the two lists,
  so a reader built at 0.1.0 cannot read a later writer that appends a field. KTAP opens with
  `KTAP version 1`. 1078's version policy tells an older log by its list's length alone. Recommended: keep the strict reader and no version in the line,
  the stricter choice, and state in the README that a reader must be at least as new as the
  writer.

## Evidence for the shared decisions

- **Errors.** No error type; the census counts five `Option` returns. For the two `Head` matchers
  absence has one cause. For the verdict reader it has several, and `kunit_parser.py` and
  `tap_parser` (one `Error` enum of eleven variants) name them. The evidence points to one small
  matchable enum per crate (P0-3, D3).
- **Direct memory access regions, doorbells and tails, register access.** Not applicable. The
  crate touches no hardware.
- **Byte sinks and sources.** The crate declares no sink trait and needs none: every line prints
  through `core::fmt::Display`, as `sd-notify`'s states do. It reads `&str`, where `expectrl`
  reads `&[u8]` (P1-5). The evidence points to `Display` as the writing shape for a text
  contract.
- **Feature names and simulators.** Not applicable. The manifest declares no feature, and the
  tests need no double.
- **Contract layout.** The census does not count this crate, since it exports no `INTERFACE_ID`,
  `VERSION` or `MAGIC`. It is a contract in text all the same, and
  `Tally::to_words` and `to_packed` are a binary layout. `from_words` and `from_packed` drop
  unknown bits where the text reader refuses unknown text. The evidence asks the layout decision
  to say whether a decoder drops or refuses what it does not know, and where a text contract
  keeps its version (D9).

## Follow-on

- **Outstanding.** All seventeen findings and the nine doors, open on the crate's `main` at
  `019d76c`, read and probed on 2026-11-26 (UTC).
- **Outstanding.** The errors decision of milestone 1129, which P0-3 and D3 wait on; this block's
  parent lists it as step 6 and unruled on 2026-11-26 (UTC).

## Done when

`script/review-status` shows this block BUILT, with each P0 and P1 line at Done or at Will not
fix beside its ruling, and D1 to D9 each carry the architect's ruling.

## BUGS

- No Rust crate does this job, so every crates.io row is a neighbor and the benchmark's rival is
  a general matcher, not a peer.
- The review read KTAP at one Linux version and no other boot-test harness.
- The benchmark ran on one machine, and only the fastest of seven passes counts.

## Index row

The release review of `boot_ladder` against Linux's KTAP and its console parser, with `sd-notify`,
`expectrl`, `embedded-test` and two TAP crates as neighbors, since no Rust crate does the same
job. Seven one-way changes come before 0.1.0: a type for a check, a strict reader, a refusal
apart from an absent verdict, non-exhaustive types, private fields, the provisional names and a
refusal of unusable system names. Five fixes land before the release, five may follow, and nine
doors are for the architect, among them whose check list the crate carries.
