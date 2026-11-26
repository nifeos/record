---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1140. `line_editor`: the release review's findings

The release review of `partsfoundry/line_editor` at commit `2c625ef6`, made under
milestone 1129 (the combine review), whose
[block](1129-crate-interfaces-best-in-class.md) sets its form. It compares the crate's public
interface with the no_std line editors a stranger would choose instead, and lists what changes
before the 0.1.0 interface. The baseline is milestone 1098 (what an outside maintainer would fix),
[its block](1098-line-editor-outside-review.md),
whose findings have all landed, and the cleared package
[`notes/crate-reviews/line-editor.md`](../../notes/crate-reviews/line-editor.md). Neither is
reopened here.

Reuse: the prior-art table weighs each line editor a caller could take instead.

## Finding status

The status words are those `script/review-status` reads.

- P0-1, `restore` answers `Option<()>` and `Refusal` is not an error: Open.
- P0-2, `Event::None` shadows `Option::None`: Open.
- P0-3, `pop_up_to_eight` returns the host's reply shape: Open.
- P1-1, the host protocol's words in the crate's documentation: Open.
- P1-2, four public types have no `Debug`: Open.
- P1-3, no `dyn Sink` fits the sink parameter: Open.
- P1-4, no failure sections and five items without an example: Open.
- P2-1, the manifest has no `documentation` key: Open.
- P2-2, an `embedded-io` adapter: Waiting on the byte-sink decision of milestone 1129.
- P2-3, capacities the caller chooses: Open.
- P2-4, UTF-8 input: Open.

## Open decisions

The one-way doors below, D1 to D4, each for the architect.

## Goal

A stranger who needs a line editor on a target without an operating system meets an interface as
plain as the best no_std editor's, with errors that say why, and with no word of the host it was
written for.

## What the review read and ran

The sources read, the commands run and the 54 API Guidelines items are in
[the appendix](1140-line-editor-release-review/what-was-checked.md) and
[the guidelines table](1140-line-editor-release-review/api-guidelines.md).

## Prior art

Measured from the crates.io API on 2026-11-26 (UTC). The problem a stranger brings to this crate is
line editing with no allocator and no input or output of its own, so the ranked crates are the
no_std editors. The std editors own the terminal and need an operating system; they stand in the
table as neighbors.

| crate | role | version read | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `embedded-cli` | ranked 1 | 0.2.1 | 67,517 | 18,816 | 0 | 2024-03-02 |
| `noline` | ranked 2 | 0.5.1 | 37,732 | 2,218 | 1 | 2024-12-12 |
| `menu` | neighbor: a command menu over a line | 0.6.1 | 177,866 | 81,611 | 2 | 2024-11-29 |
| `rustyline` | neighbor: std, owns the terminal | 19.0.0 | 62,718,541 | 15,764,807 | 1290 | 2026-10-17 |
| `reedline` | neighbor: std, owns the terminal | 0.53.0 | 4,449,121 | 1,305,973 | 164 | 2026-11-09 |
| `linefeed` | neighbor: std, owns the terminal | 0.6.0 | 667,251 | 49,665 | 36 | 2019-04-26 |
| `vte` | neighbor: an escape-sequence parser | 0.15.0 | 101,230,691 | 30,436,222 | 203 | 2025-02-02 |
| `embedded-io` | integration: byte sink | 0.7.1 | 203,586,087 | 93,397,838 | 352 | 2025-10-01 |
| `core::fmt::Write` | integration: text sink | the standard library | | | | |

`embedded-cli` passes 10,000 downloads in 90 days, so the review reads no system outside Rust.

### What `line_editor` does better

- Than `embedded-cli`: it is sans-IO, since `feed(byte, sink)` returns an `Event` and the caller
  owns every read. `embedded-cli` couples editing to command dispatch and `ufmt`. `line_editor`
  carries its state across a program replacement (`handoff`) and proves its editing with Kani;
  neither comparator does either.
- Than `noline`: it needs no buffer from the caller and no feature to build. It parses the SS3
  cursor keys that application mode sends; a search of both no_std comparators' sources finds no
  SS3 handling. `noline` returns an iterator of output bytes from
  each step, which a caller must drain before the next byte; `line_editor` writes through the sink
  as it goes.
- Than `menu`: it hands Tab and `^Z` to the caller as events, so the caller decides what
  completion and job control mean.
- Than the std editors: it runs where they cannot, on no operating system, with no allocator
  and no terminal-size query that could block.

## The items

Effort is S (half a day), M (a day or two) or L (longer). A door is one-way when someone outside
the repository acts on it once 0.1.0 is out. A P0 finding is one-way, so it lands in the 0.1.0
interface or not at all; a P1 finding is two-way and lands before the release.

### P0: the 0.1.0 interface

#### P0-1. `restore` answers `Option<()>`, and `Refusal` is not an error

Verified in source
(`src/handoff.rs`).
`Reader::new` returns `Result<Reader, Refusal>`, but `LineEditor::restore` and `RawQueue::restore`
return `Option<()>`, so a caller learns that a blob failed and not why. `Refusal` implements
neither `Display` nor `core::error::Error` and is not `#[non_exhaustive]`. `noline` 0.5.1 returns
`NolineError` and `rustyline` 19 returns `ReadlineError`, both with `Display`.
Change: `restore` returns `Result<(), Refusal>`. `Refusal` gains `Display`, `core::error::Error`
and `#[non_exhaustive]`, and a variant for a field that does not fit. The shared errors decision of
milestone 1129 governs the shape. Door: one-way (D1). Effort: S.

#### P0-2. `Event::None` shadows `Option::None`

Verified in source (`src/line_disc.rs`).
`feed` returns `Event`, whose first variant `None` means nothing to act on. A caller that writes
`use Event::*` shadows the prelude's `None`, and `Event::None` beside an `Option` reads as a second
kind of absence. No block ratifies the variant; the package lists it as part of the engine.
`noline` 0.5.1 returns `Option<Output>` from its `advance`.
Change: `feed` returns `Option<Event>` and the variant goes. The other five variants keep their
names. Door: one-way (D2). Effort: S.

#### P0-3. `pop_up_to_eight` returns the host's reply shape

Verified in source
(`src/raw_queue.rs`).
It returns `Option<(usize, u64)>`, a count and up to eight bytes packed little-endian, because one
host replies in registers. A stranger reads a wire shape where it expects a byte queue.
`std::io::Read::read` and `heapless::Deque` hand bytes out into the caller's buffer, or one at a
time.
Change: replace it with a method that fills the caller's `&mut [u8]` and returns the count; the
host packs its own registers. The name follows design/naming.md and is provisional until
ratified. Door: one-way (D3). Effort: S.

### P1: before the first release

#### P1-1. The host protocol's words in the crate's documentation

Verified in source.
`src/raw_queue.rs` names `OPERATION_READRAW` and "the register-only reply", `src/line_disc.rs`
names "a `READLINE` request", and the fuzz target `fuzz/fuzz_targets/line_editor_handoff.rs` names
"a granted frame". None names the host, but each assumes it.
Change: describe each in terms of the crate's own interface. Door: two-way. Effort: S.

#### P1-2. Four public types have no `Debug`

Verified in source.
`LineEditor`, `RawQueue`, `handoff::Writer` and `handoff::Reader` implement no `Debug`
(C-DEBUG), and `Event` has no `Hash`. Every comparator type a caller holds implements `Debug`.
Change: a `Debug` for each, printing lengths and positions rather than the line, and `Hash` on
`Event`. Door: two-way. Effort: S.

#### P1-3. No `dyn Sink` fits the sink parameter

Inferred from the signatures.
Every method takes `out: &mut impl Sink`, whose implicit `Sized` bound refuses `&mut dyn Sink`
(C-OBJECT), and `&mut S` does not implement `Sink`, so a caller cannot pass a sink by value
(C-RW-VALUE).
Change: the bound becomes `S: Sink + ?Sized`, and `Sink` gains a blanket implementation for
`&mut S`. Door: two-way, since relaxing a bound and adding an implementation break no caller.
Effort: S.

#### P1-4. No failure sections, and five items without an example

Verified in source.
`Reader::new`, `Writer::finish` and both `restore` methods describe their failures in prose
with no `# Errors` heading (C-FAILURE). `RawQueue`, `Sink`, `expand_output`, `Writer` and
`Reader` have no example (C-EXAMPLE). The crate page and `LineEditor` do.
Change: the headings and the examples. Door: two-way. Effort: S.

### P2: may follow

#### P2-1. The manifest has no `documentation` key

Verified in `Cargo.toml` (C-METADATA).
Change: `documentation = "https://docs.rs/line_editor"`. Door: two-way. Effort: S.

#### P2-2. An `embedded-io` adapter

Verified in the comparators' manifests.
All three no_std comparators write through `embedded_io::Write`, and `line_editor` has its own
`Sink`. An adapter type behind a feature lets a caller hand an `embedded-io` writer straight in.
Change: after the byte-sink decision, an optional adapter under the feature name it picks.
Door: two-way (an addition). Effort: S.

#### P2-3. Capacities the caller chooses

Verified in source.
The line, history and prompt sizes are constants (256, 8 and 64 bytes); `noline` 0.5.1 takes the
caller's buffers. Defaulted const generic parameters would let a caller size the editor with the
defaults unchanged. The handoff layout then needs the sizes in its blob or its `LAYOUT`.
Change: defaulted const generics, if a caller asks. Door: two-way. Effort: M.

#### P2-4. UTF-8 input

Verified in source and the README's BUGS section.
The editor drops a byte at or above 0x80, so typed UTF-8 vanishes; `noline` 0.5.1 edits UTF-8 by
character. Change: cursor movement by character, behind no feature. Door: two-way, as a behavior
change the CHANGELOG states. Effort: M.

### Measured performance

Not run. The interface takes one byte per call at the rate a person types or a serial line
delivers, and nothing in its shape (no allocation, no copy beyond the echo) is a cost a benchmark
would separate from the comparators'.

## One-way doors

Each for the architect, one at a time.

- D1, the handoff's error shape (P0-1). Recommended: `restore` returns
  `Result<(), Refusal>`, and `Refusal` is `#[non_exhaustive]` with `Display` and
  `core::error::Error`, in the shape the shared errors decision picks. A non-exhaustive enum can
  gain a refusal later; an `Option` cannot gain a reason.
- D2, the event that means nothing happened (P0-2). Recommended: `feed` returns
  `Option<Event>` and `Event::None` goes, as `noline` does.
- D3, the raw queue's output (P0-3). Recommended: the caller's buffer and a count, with the
  register packing in the host.
- D4, `Sink` stays the crate's own and infallible. Recommended: keep it. Echo that fails has no
  one to report to between keystrokes, and a caller's sink can record the failure. The byte-sink
  decision of milestone 1129 may add the adapter of P2-2, which leaves `Sink` as it is.

## Follow-on

- **Outstanding.** D4 and P2-2 are evidence for the byte-sink decision, and D1 for the
  errors decision.

## Done when

Every P0 and P1 finding reads Done, or Will not fix with its ruling, the architect has ruled D1
to D4, and `script/review-status` shows the block BUILT.

## BUGS

- The review read each comparator's behavior from its source at the version in the table, and ran
  none of them.

## Index row

The release review of `line_editor` against `embedded-cli`, `noline` and the std editors: three
one-way interface changes before 0.1.0, four two-way fixes before the release, four doors to rule.
