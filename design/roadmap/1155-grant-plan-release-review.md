---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1094, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1155. `grant_plan`: the release review's findings

*(The number and the slug are provisional.)*

The release review of `partsfoundry/grant_plan` at commit `69aedfbc`, version 0.1.0
(unpublished), under milestone 1129 (the combine review), whose
[block](1129-crate-interfaces-best-in-class.md) sets its form. The baseline is milestone 1094
(what an outside maintainer would fix before it leaves),
[its block](1094-grant-plan-outside-review.md) and the cleared package
[`notes/crate-reviews/grant-plan.md`](../../notes/crate-reviews/grant-plan.md). 1094's rulings
stand: the three-crate boundary, the limits that carry their unit, and the names ratified on
2026-11-20. 1094 left one choice to this review, the arguments `plan_against` takes by reference
(D9). The release-review rule reopens two ratified names (P0-8).

Reuse: the crate's own tests and example, and two scratch crates, a probe and a benchmark.

## Finding status

- P0-1, a batched expander can finish as a whole set: Open.
- P0-2, no public enum or struct can grow: Open.
- P0-3, the refusals have no error trait and no place in the line: Waiting on the errors
  decision of milestone 1129.
- P0-4, `ParsedInvocation`, `Line` and `Word` mix public fields with private state: Open.
- P0-5, sequences are a fixed array, a callback and a bare index: Open.
- P0-6, `TwoRoots` is public and nothing uses it: Open.
- P0-7, one shell's refusals and one program's protocol sit in the interface: Open.
- P0-8, the names this review reopens, and the provisional ones: Open.
- P1-1, two name sets with the same names compare unequal: Open.
- P1-2, the crate has two rules for what a name is: Open.
- P1-3, a refusal sentence carries the damage of a rename: Open.
- P1-4, the crate's text names another tree's programs and dates: Open.
- P1-5, the crate page has no example, and no function has a failure section: Open.
- P1-6, the package ships the repository's machinery: Open.
- P1-7, two unpublished crates stand in the public signatures: Open.
- P1-8, `Debug`, `Hash` and `#[must_use]`: Open.
- P1-9, `BUILTINS` omits two of the words `parse` answers: Open.
- P2-1, the weekly fuzz job has no target, and one proof covers one byte: Open.
- P2-2, no function spells a name back: Open.
- P2-3, bare `bool`s, and the conversion traits: Open.
- P2-4, one limit has three constants: Open.
- P2-5, the manifest and `forbid(unsafe_code)`: Open.
- P2-6, two small edges: Open.

## Open decisions

The one-way doors D1 to D10 below.

## Goal

A stranger who writes a shell for a capability system gets a line read, a grant planned and a
refusal worded, with no allocator. The types refuse the wrong finish and the forged parse, each
refusal says where it stands, and the interface can grow.

## What the review read and ran

[The appendix](1155-grant-plan-release-review/what-was-checked.md) holds the crate's files, the
commands, the probe, the benchmark and each comparator file read.
[The guidelines table](1155-grant-plan-release-review/api-guidelines.md) marks the 54 items.

## Prior art

Measured from the crates.io API on 2026-11-26 at 22:49 (UTC). The crate's problem has two parts.
The first is reading a typed line, and three Rust crates rank for it. The second is deciding
what the line grants against a program's declaration. No Rust crate solves that: fourteen
searches found none. The bar for it is the shell of Plash, outside Rust.

| crate or system | role | version read | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `shlex` | ranked 1: splits a line into words | 2.0.1 | 1,166,214,781 | 396,658,502 | 846 | 2026-05-17 |
| `shell-words` | ranked 2: the same job | 1.1.1 | 189,653,529 | 51,611,713 | 921 | 2025-12-10 |
| `brush-parser` | ranked 3: a whole shell grammar, with pipes and redirections | 0.5.0 | 1,036,344 | 532,786 | 34 | 2026-11-26 |
| `yash-syntax` | comparator: a POSIX shell grammar | 0.25.0 | 64,591 | 20,208 | 6 | 2026-09-06 |
| `clap_lex` | neighbor: classifies options in an argument list | 1.1.2 | 1,103,581,987 | 273,096,242 | 37 | 2026-11-16 |
| `lexopt` | neighbor: the same job, with typed errors | 0.3.2 | 15,914,452 | 3,760,889 | 211 | 2026-02-28 |
| `cap-std` | neighbor: directories held as capabilities | 4.0.3 | 37,324,536 | 19,185,273 | 370 | 2026-08-20 |
| Plash `pola-shell`, `src/shell.gram` and `src/shell.c` | outside Rust: a shell whose line is the grant | commit `1d77bb2f` | | | | |

The crate integrates with no crate on crates.io. Its three dependencies are the organization's
own: `byte_glob`, `grant_contract` and `program_argument_contract` (P1-7).

### What `grant_plan` does better

- Than `shlex` and `shell-words`: it needs no allocator, where both build a `Vec` for every
  word. It names the cause of a refusal, where `shlex::split` returns `None`. It reads pipes
  and redirections.
- Than `brush-parser` and `yash-syntax`: it has no dependency outside the organization, where
  `brush-parser` 0.5.0 declares eleven and needs `std`. Both parse larger languages, and
  neither plans a grant.
- Than `clap_lex` and `lexopt`: the planner checks an option against the program's declaration
  before the program runs, and an option that widens a grant shows in the plan.
- Than Plash: the direction of a file grant comes from the program's declaration, where Plash
  asks the person to type `=>`. A pattern that matches nothing refuses the line, and `*` does
  not reach a dot file. Nine Kani harnesses cover the reader, the name set and the path walk.

## The items

Effort is S (half a day), M (a day or two) or L (longer). A door is one-way when code outside the
repository depends on the answer after 0.1.0, which is why a P0 cannot wait for a later release.

### P0: the 0.1.0 interface

#### P0-1. A batched expander can finish as a whole set

Verified by running the probe (`src/expansion.rs`, lines 406 to 442).
`Expander::new` and `Expander::batch` build the same type, and `finish` and `finish_batch` each
suit one of them. A `debug_assert!` guards the wrong pairing. In a release build
`Expander::batch(..)` offered ten matches answers `finish()` with `Ok` and eight names. That is
the grant of a prefix of what matched, which the crate's documentation calls its worst
outcome. In a debug build the same call panics.
Change: two types, one per collection policy, each with the one `finish` that suits it (the
second type's name is provisional). Door: one-way (D1). Effort: S.

#### P0-2. No public enum or struct can grow

Verified in source: `grep -rn non_exhaustive src` finds nothing.
`Refusal` has 43 variants and `CommandLine` 22, and a new variant breaks a caller's `match` on
either. `CapabilityKind` has one variant, and its documentation says more will come.
`Endowment` has twelve public fields, and six more structs are all public fields.
`shlex::QuoteError`, `brush_parser::ParseError` and `yash_syntax`'s `SyntaxError` are
`#[non_exhaustive]`.
Change: `#[non_exhaustive]` on `Refusal`, `CommandLine`, `PathRefusal`, `BindRefusal`,
`CapabilityKind`, `InterruptAction` and `UserVerb`, and on the structs the crate hands out:
`Endowment`, `FileGrant`, `DirectoryGrant`, `Batch` and `TouchOperands`. The caller builds
`ShellHoldings` and `Streams`, and the attribute forbids a struct literal outside the crate, so
they get a constructor and setters with private fields. Door: one-way (D2). Effort: M.

#### P0-3. The refusals implement no error trait and carry no place in the line

Verified in source and by `cargo doc`.
Five types stand in the error position of a public `Result`: `Refusal`, `PathRefusal`,
`BindRefusal`, `NoJobNamed` and `NameSetFull`. None implements `core::fmt::Display` or
`core::error::Error`; three have a `message` method that returns a fixed sentence. No refusal
says where in the line it stands. `line::split` answers `UnclosedQuote` with no offset, and
`plan_against` answers `Unexpected` while the token sits in another value. `nav_refusal` turns
all four `PathRefusal` causes into `Refusal::FileNotNameable`, whose sentence lists three limits
and cannot say which one the line met. `DirectoryPath::descend` returns `false` for three
causes. `NameSetFull` covers four, two of them not about room. `yash-syntax` pairs every cause with a `Location`, and its unclosed-quote
variants carry where the quote opened. `brush-parser` returns `ParsingNear(SourcePosition)`.
`lexopt` carries the option or value that failed.
Change: `Display` and `core::error::Error` on all five, with `message` kept as the text
`Display` prints. A refusal about a token carries the token's range in the line. A path refusal
inside a `Refusal` keeps its cause. `descend` and `ascend` return the `PathRefusal`. Named
causes replace `NameSetFull`. The shape is the one the errors decision of milestone 1129 picks.
Door: one-way (D3). Effort: M.

#### P0-4. `ParsedInvocation`, `Line` and `Word` mix public fields with private state

Verified in source (`src/parsing.rs`, `src/line.rs`, `src/word.rs`).
`ParsedInvocation` has four public fields (`program`, `memory_grant`, `unexpected`,
`misquoted`) beside six private ones with getters. `plan_against` trusts the public ones, so a
caller can set `unexpected` and `misquoted` to `None` and plan a line the parser refused. `Line`
has three public fields beside four private ones. `Word` is two
public fields, so a word is one slice of the line for good. A backslash escape or two joined
quotes need a word of several pieces. `shlex`, `shell-words`, `brush-parser` and Plash all read
escapes (D10).
Change: private fields with getters on the three. Door: one-way (D4). Effort: S.

#### P0-5. Sequences are a fixed array, a callback and a bare index

Verified in source, by running the probe and by measurement.
`tokenize(line, out)` fills a caller's array and stops when it is full, with no sign that tokens
remain. 1094's fix covers the planner's own call; a stranger's call still loses the seventeenth
token silently. `for_each_word` takes `&mut dyn FnMut`, and `word::token_end` takes `&dyn Fn`.
`DirectoryPath::component(level)` returns an empty slice one past the end on a short path and
panics there on a full one, and no method yields the components. `shlex::bytes::Shlex` is an `Iterator`. `for_each_word` takes 458 ns on twelve
words, where `tokenize` with `word::read` takes 217 ns.
Change: an iterator over a line's tokens and one over its words, which yields
`Result<Word, Refusal>`; `components()` on `DirectoryPath`, and `component` returning `Option`
as `slice::get` does. The array and callback forms go. Names are provisional. Door: one-way
(D5). Effort: M.

#### P0-6. `TwoRoots` is public and nothing uses it

Verified in source: outside its own tests, no line of the crate or its example names it.
`navigation::TwoRoots` composes two labeled roots; `MountedTree` and `ShellHoldings` do that job
for the planner. It derives nothing, and the documentation of `GrantSide` rests on its
arguments. The changelog records the removal of two of its methods for the same reason.
Change: remove `TwoRoots` before 0.1.0, and document `GrantSide` by the mounted tree. Door:
one-way (D6), since a removal after 0.1.0 is a breaking release. Effort: S.

#### P0-7. One shell's refusals and one program's protocol sit in the interface

Verified in source and by a count over `src/`.
Seven of `Refusal`'s 43 variants are never returned by the library: `EmptySegment`,
`TooManySegments`, `ScopeMalformed`, `ScopeTooDeep`, `ScopeCannotRestore`,
`GroupingParentheses` and `IsolationNotBuilt`. A shell returns them. Three of their sentences
name that shell's program (`'swish -c'`). Two quote limits this crate cannot see (three nested
blocks, eight commands), and the crate's own test says so of the second.
`rm_options` names the option order
of one program's declaration. `rm_report` is the reply protocol between that program and its
spawner: a slot number and a status word. `CommandLine` holds the builtins of one shell, among
them `vouch`, `user` and `apropos`. `brush-parser` and `yash-syntax` name no program. Plash's
grammar fixes five commands.
Change: the seven variants and their sentences move to the shell that returns them, which wraps
`Refusal` in its own type. `rm_options` and `rm_report` move to where the program and its
spawner share them. The crate page says the builtin list is one shell's. Door: one-way (D7).
Effort: M.

#### P0-8. The names this review reopens, and the provisional ones

Verified in source, read against [design/naming.md](../naming.md).

- `GrantSide::First` and `GrantSide::Second`, ratified on 2026-11-20. The shapes rule says to
  name the property and not the count. Recommended: variants that say the shell's own tree and
  the mounted one.
- `Escalation::on_tick`. The vocabulary rule lists `tick`, and the constant beside it already
  reads `COOPERATIVE_GRACE_POLLS`. Recommended: `on_poll`.
- `BindRefusal::ReservedLabel`, which its own documentation calls provisional. Recommended: a
  name that says the bind would hide the mount point.
- The builtin variants of `CommandLine`. `Cd`, `Pwd`, `Ls` and `Mkdir` keep the typed word, as
  ruled on 2026-11-20; `Foreground`, `Background` and `Capabilities` spell theirs out.
  Recommended: one rule for all seven.
- `NameSetFull`, for a refusal with four causes (P0-3).
- `navigation::path` and `word::read`, constructors written as free functions (C-METHOD).
  Recommended: associated functions on `Path` and `Word`.

Every other name passes the rules in force.
Change: the architect rules each. Door: one-way (D8). Effort: S.

### P1: before the first release

[The appendix](1155-grant-plan-release-review/before-the-first-release.md) holds the nine in
full. P1-1 to P1-3 change what the crate answers; the rest are text, packaging and traits. Each
is a two-way door.

### P2: may follow

[The later items](1155-grant-plan-release-review/later-items.md) hold the six in full.

### Measured performance

Reading twelve words takes 217 ns against 482 ns for `shlex` 2.0.1, and a 40-byte pipeline
365 ns against 5,048 ns for `brush-parser` 0.5.0. Parsing and planning one file grant takes
592 ns, and copying the 4,344-byte `Endowment` it returns takes 57 ns. The host, the inputs and
the full table are in
[the appendix](1155-grant-plan-release-review/what-was-checked.md#the-benchmark).

## One-way doors

- D1, one expander type or two (P0-1). Recommended: two types, so the compiler refuses the wrong
  finish.
- D2, room to grow (P0-2). Recommended: `#[non_exhaustive]` on the seven enums and the five
  structs the crate hands out, and private fields with setters on `ShellHoldings` and `Streams`.
  Dropping the attribute later breaks no caller.
- D3, the shape of a refusal (P0-3). Recommended: both traits, the place in the line, and the
  path cause kept, in the shape the errors decision picks.
- D4, private fields on `ParsedInvocation`, `Line` and `Word` (P0-4). Recommended: private, with
  getters. Opening a field later breaks no caller.
- D5, iterators (P0-5). Recommended: iterators replace `tokenize`'s array and `for_each_word`'s
  callback, and `component` returns `Option`.
- D6, `TwoRoots` (P0-6). Recommended: remove it. It can return as a new type; it cannot leave
  after 0.1.0.
- D7, whose shell this is (P0-7). The grammar, the twenty builtins and the sentences are one
  shell's. Recommended: keep the one grammar at 0.1.0 and say so on the crate page. Move out the
  seven variants the library never returns, the shell's name, `rm_options` and `rm_report`. A
  grammar that takes its builtin list can join later. Whether a crate that carries one shell's
  builtins belongs on crates.io is the architect's to say here.
- D8, the names (P0-8). Recommended: the renames listed there, and one rule for the builtin
  variants.
- D9, what `plan_against` takes by reference. 1094 left `&ShellHoldings` (3,312 bytes),
  `&Expansion` (568) and `&Streams` (2,368) provisional until this review. Recommended: ratify
  them by reference, and keep `Manifest` (80 bytes) by value.
- D10, what a word is. 1094 recorded the cost: a word is one slice, no backslash escapes, and
  two quoted pieces do not join. The reader refuses `don't`, and no line spells a name that
  holds both quote characters. `shlex`, `shell-words`, `brush-parser` and Plash all read `\ `.
  Recommended: keep the rule at 0.1.0, the stricter choice, with D4 taken. Accepting an escape
  later breaks no line that runs today.

## Evidence for the shared decisions

- **Errors.** Five types in the error position, none with `Display` or `core::error::Error`:
  one enum of 43 variants, two small enums and two unit structs. The census reads three, since
  its pattern misses `NoJobNamed` and `NameSetFull`. Two functions return a `bool` that stands
  for a refusal. `shlex` and `brush-parser` mark their enums `#[non_exhaustive]` and implement
  both traits, `yash-syntax` pairs a cause with a location, and `lexopt` carries the failed
  input. The evidence points to one matchable enum for each crate, `#[non_exhaustive]`, with
  both traits and the place in the input (P0-3, D3).
- **Direct memory access regions, doorbells and tails, register access, simulators.** Not
  applicable. The crate touches no hardware, and its tests need no double.
- **Byte sinks and sources.** The crate declares no byte trait; it writes into a caller's
  buffer in `DirectoryPath::render`, `line_verb` and `write_argument_page`. `line::Sink` and
  `line::Source` are enums that name which capability fills a program's slot, where
  `line_editor::Sink` is a byte trait. The evidence asks the decision which meaning `Sink`
  keeps across the crates.
- **Feature names.** The crate declares none. `shlex` and `shell-words` have a default `std`
  feature, and `brush-parser` names each feature for what it turns on. No evidence on a
  version in a name.
- **Contract layout.** The crate exports no `INTERFACE_ID`. It holds copies of four limits that
  a file-system contract owns, which a consumer of both must pin, and one program's reply slot.
  The evidence asks the layout decision to give each shared constant one home (P0-7).

## Follow-on

- **Outstanding.** All twenty-three findings and the ten doors, open on the crate's `main` at
  `69aedfb`, read and probed on 2026-11-26 (UTC).
- **Outstanding.** The errors decision of milestone 1129, which P0-3 and D3 wait on.

## Done when

`script/review-status` shows this block BUILT, with each P0 and P1 line at Done or at Will not
fix beside its ruling, and D1 to D10 each carry the architect's ruling.

## BUGS

- No Rust crate plans a grant from a line, so the ranked crates answer the reading half only,
  and the benchmark's rivals do less (`shlex`) or more (`brush-parser`) than the crate.
- The review read Plash at one commit, and read no other capability shell.
- The benchmark ran on one machine, and the probe's generated lines are no proof.

## Index row

The release review of `grant_plan` against `shlex`, `shell-words`, `brush-parser` and
`yash-syntax` for reading a line, and against Plash's shell for granting from one, since no Rust
crate does that. Eight one-way changes come before 0.1.0, among them two expander types, room to
grow, refusals with a place in the line, private fields on the parse, and iterators. Nine fixes
land before the release, six may follow, and ten doors are for the architect.
