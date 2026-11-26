---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1079, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1159. `byte_sink_contract`: the release review's findings

*(The number and the slug are provisional.)*

The release review of `partsfoundry/byte_sink_contract` at commit `8a477c6a`, version 0.1.0 with
no tag, under milestone 1129 (the combine review), whose
[block](1129-crate-interfaces-best-in-class.md) sets its form. The baseline is milestone 1079 (what
an outside maintainer would fix before it leaves), [its block](1079-byte-sink-contract-outside-review.md)
and the cleared package [`notes/crate-reviews/byte-sink-contract.md`](../../notes/crate-reviews/byte-sink-contract.md).
Every 1079 finding reads Done. The crate's name, the identity values 6 and 1, the reserved words
of an end of stream and the ratified names stay closed, and no later rule of
[design/naming.md](../naming.md) touches them. The clearance left `MessageWords` for this review
(door D7). Doors D4 and D6 bring two ratified shapes back with evidence.

Reuse: the crate's own tests, and one scratch crate for a probe, a build check and the benchmark.

## Finding status

- P0-1, `unpack` accepts three things its documentation rules out: Open.
- P0-2, the severity field is provisional on the wire and a bare `u8` in the interface: Open.
- P0-3, `Malformed` is a variant of the decoded value and gives no cause: Waiting on the errors decision of milestone 1129.
- P0-4, `Sent` holds one success and two failures and is not an error: Waiting on the errors decision of milestone 1129.
- P0-5, the version rule contradicts the decoder: Open.
- P0-6, five free functions read a first word passed as a bare `u64`: Open.
- P0-7, `MessageWords` has no ruling: Open.
- P0-8, the identity, the opcodes and the shift are loose constants: Waiting on the contract-layout decision of milestone 1129.
- P1-1, the documentation names items a stranger cannot find and never names the system: Open.
- P1-2, two doc comments tell history: Open.
- P1-3, `with_severity` says it acts on any first word, and on an end of stream it builds a refused message: Open.
- P1-4, nine of eleven public functions have no example, and no test compiles the README's two: Open.
- P1-5, the three public types have no `Hash`: Open.
- P1-6, no item walks a buffer as messages: Open.
- P2-1, no `embedded-io` writer: Waiting on the byte sinks and sources decision of milestone 1129.
- P2-2, `pack` and `unpack` are not `const fn`: Open.
- P2-3, no conversion between `MessageWords` and `[u64; 3]`: Open.
- P2-4, the package ships the repository's CI files: Open.
- P2-5, nothing says a message boundary may split a character: Open.
- P2-6, `unpack` writes through an out parameter: Open.

## Open decisions

The one-way doors D1 to D10 below.

## Goal

A stranger writes a conforming writer or sink from the crate's page alone. The decoder refuses
every message the documentation rules out, and a refusal is an ordinary Rust error that names its
cause. No sink built against 0.1.0 accepts a message a later release must refuse.

## What the review read and ran

[The appendix](1159-byte-sink-contract-release-review/what-was-checked.md) lists what the lane
read in the crate, in four crates and in seL4, with each command's result and the benchmark.
[A table](1159-byte-sink-contract-release-review/api-guidelines.md) gives a verdict on each of
the 54 API Guidelines items. The P2 findings stand in full in
[the later items](1159-byte-sink-contract-release-review/later-items.md).

## Prior art

Measured from the crates.io API on 2026-11-26 at 22:53 (UTC). A stranger brings this crate one
problem: a byte stream carried in the registers of a kernel's message, with an end marker and a
decoder that refuses. Seven searches of crates.io found no crate that solves it, and the `sel4`
crate there drew 148 downloads in 90 days. No Rust comparator ranks, so seL4 sets the bar.

| crate or system | role | version read | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `embedded-io` | integration target: `Write` and `ErrorKind` | 0.7.1 | 204,395,110 | 94,206,861 | 353 | 2025-10-01 |
| `cobs` | neighbor: frames bytes on a stream | 0.5.1 | 103,994,487 | 47,498,600 | 44 | 2026-03-03 |
| `bitfield-struct` | neighbor: fields packed in one word, README read | 0.13.0 | 27,018,873 | 4,718,777 | 139 | 2026-04-04 |
| `syslog` | neighbor: a severity type | 7.0.0 | 10,777,296 | 1,518,501 | 81 | 2024-07-26 |
| seL4 `shared_types.bf`, `constants.h` and the x86_64 `syscalls.h` | outside Rust | 13.0.0 | | | | |
| rust-sel4 `crates/sel4/src/message_info.rs` | outside crates.io | v6.0.0 | | | | |

### What `byte_sink_contract` does better

- Than seL4's `seL4_MessageInfo`, a label and a length whose meaning each protocol sets: one
  fixed meaning, an end of stream, and a decoder proved total.
- Than rust-sel4's `MessageInfo::new`, which panics on a value that does not fit: `first_word`
  takes a `u8` and a `u32`, so every argument fits.
- Than `cobs`: no scan for a sentinel, and a seventh of the time for sixteen bytes.
- Than `embedded-io`'s `Write`, which has `flush` and no end marker: the end is a message.
- Than all of them: six Kani harnesses, each with a patch that turns it red, and no dependency.

The comparators lead on four counts, which the items take up. `cobs` returns `Result` with a
cause, rust-sel4 reads its word through methods, `syslog` types its severity, and `embedded-io`
marks `ErrorKind` `#[non_exhaustive]`.

## The items

Effort is S (half a day) or M (a day or two). A one-way item binds every writer and sink from
the first 0.1.0 tag, which is why the P0 items cannot wait.

### P0: the 0.1.0 interface

#### P0-1. `unpack` accepts three things its documentation rules out

Verified by building. `KIND_SHIFT` says bits 55:48 stay zero, and a bytes message with all eight
set decodes as `Bytes(2)`. `severity` says a field past 8 is no level, and `unpack` passes a field
of 200. A message with a count of 2 and both words all ones decodes too, and `out` then holds
sixteen `0xff` bytes. `pack` sends none of the three. The end of stream already refuses its
reserved bits, and a refusal added after 0.1.0 changes published behavior.
Change: `unpack` refuses a bytes message with a bit set in 55:48, a severity field past 8 or a
non-zero byte past its count, each with a Kani harness.
Door: one-way (D1). Effort: S.

#### P0-2. The severity field is provisional on the wire and a bare `u8` in the interface

Verified in source and in the README's BUGS section, which calls the width and the plus-one
encoding provisional. A tag freezes both. `with_severity(word, 200)` returns level 7, so a wrong
level becomes debug in silence. `syslog` has an enum of the eight levels of RFC 5424.
Change: freeze the field as built, and take and return an enum of the eight levels, its name
provisional, so no caller can pass a ninth.
Door: one-way (D2). Effort: S.

#### P0-3. `Malformed` is a variant of the decoded value and gives no cause

Verified in source. `unpack` returns `Message`, not a `Result`, so `?` does not work and a sink
cannot log why it refused. `Malformed` stands for four causes: an unknown opcode, an unknown
kind, a count past sixteen and a reserved bit on an end of stream. P0-1 adds three. `Message` is
exhaustive, so a third opcode breaks every `match`.
`cobs::decode` returns `Result<DecodeReport, DecodeError>`, an enum of three with a named field.
Change: `unpack` returns `Result<Message, E>`, where `E` is an enum of the causes with `Display`
and `core::error::Error`. Both enums take `#[non_exhaustive]`, and the errors decision picks the
name.
Door: one-way (D3). Effort: S in the crate, M across callers.

#### P0-4. `Sent` holds one success and two failures and is not an error

Verified in source. The crate page says a standard library maps `NoSink` to
`ErrorKind::Unsupported` and `Gone` to `ErrorKind::BrokenPipe`, and `embedded-io` has both kinds.
Every caller writes that mapping by hand, since `Sent` has no `Display`, no `core::error::Error`
and no conversion.
Change: `classify` returns `Result<(), E>`, where `E` has the variants `Gone` and `NoSink` and
both traits.
Door: one-way (D4). Effort: S in the crate, M across callers.

#### P0-5. The version rule contradicts the decoder

Verified in source. `VERSION` says a break raises it and an addition owes no bump. `unpack`
refuses every opcode and kind it does not know, and a writer gets no reply. A writer that sends
an added opcode to a sink of the same `VERSION` loses its bytes and cannot learn it.
Change: the documentation states the rule of door D5.
Door: one-way (D5). Effort: S.

#### P0-6. Five free functions read a first word passed as a bare `u64`

Verified in source. `operation`, `len`, `kind`, `severity` and `with_severity` each take
`word_zero: u64`, so a caller writes `byte_sink_contract::len(word)` and any `u64` passes.
rust-sel4 wraps the same word in `MessageInfo` and reads it with `label()` and `length()`, and
`bitfield-struct` generates such methods. The clearance ratified the five as free functions.
Change: the five become methods of `MessageWords` under the same names, so a sink writes
`words.len()`. `first_word` and `end_of_stream` stay.
Door: one-way (D6). Effort: S in the crate, M across callers.

#### P0-7. `MessageWords` has no ruling

Verified in the cleared package. The fields are public and hold no invariant, since `unpack`
judges any three words. seL4's `seL4_SendWithMRs` passes the same registers as separate words.
Change: ratify `MessageWords`, `new` and the public fields as built.
Door: one-way (D7). Effort: S.

#### P0-8. The identity, the opcodes and the shift are loose constants

Verified in source. `INTERFACE_ID` is a `u64` of 6 and `VERSION` a `u32` of 1, with no magic.
The two opcodes and `KIND_TEXT` are bare `u8` constants, so a `match` on `operation(word)` needs
a wildcard arm. `OPERATION_SHIFT` says two more contract crates put their opcode in the same bits.
Change: the names, the types and the home of the shared shift that the contract-layout decision
picks.
Door: one-way (D8). Effort: S.

### P1: before the first release

#### P1-1. The documentation names items a stranger cannot find and never names the system

Verified in source and the README. The crate page builds on `Rendezvous`, `SEND`, `CALL` and
`WRITE` and never says which system has them. `classify` names a `PageFrame`, `VERSION` names the
`INTERFACES` note, and `GONE` restates the return of a kernel with no name. `OPERATION_SHIFT`
names `filesystem_contract`, and the organization's crate is `file_system_contract`.
Change: one sentence that names the binary interface (door D9), and a link or a plain
description for each foreign name.
Door: two-way, apart from D9. Effort: S.

#### P1-2. Two doc comments tell history

Verified in source. `OPERATION_BYTES` describes the framing a standard library sent before the
crate existed and what unifying the protocol changed. One test's comment repeats it.
Change: state the property: with the opcode at zero, the first word of a bytes message equals its
count.
Door: two-way. Effort: S.

#### P1-3. `with_severity` says it acts on any first word, and on an end of stream it builds a refused message

Verified by building: `unpack` returns `Malformed` for `(with_severity(end_of_stream(), 3), 0, 0)`.
The doc comment says the function acts on any first word.
Change: the comment says a severity on an end of stream makes a message that `unpack` refuses.
Door: two-way. Effort: S.

#### P1-4. Nine of eleven public functions have no example, and no test compiles the README's two

Verified in source. `pack` and `unpack` have examples. `classify`, `first_word`, `end_of_stream`,
the five readers and `MessageWords::new` have none, and the crate page has none.
Change: an example on the crate page and on each function, and the README included as a doctest.
Door: two-way. Effort: S.

#### P1-5. The three public types have no `Hash`

Verified in source. `MessageWords`, `Message` and `Sent` derive `Debug`, `Clone`, `Copy`,
`PartialEq` and `Eq`.
Change: derive `Hash` on all three. No `Default`: three zero words are an empty bytes message.
Door: two-way. Effort: S.

#### P1-6. No item walks a buffer as messages

Verified in the README, whose first example writes the loop by hand. `embedded-io` puts the same
loop in `write_all`.
Change: a function from `&[u8]` to an iterator of `MessageWords`, its name provisional, with an
`Iter` type.
Door: two-way. Effort: S.

### P2: may follow

Each is verified in source or by building. The evidence is in
[the later items](1159-byte-sink-contract-release-review/later-items.md).

- P2-1: a writer type that implements `embedded_io::Write`, under a feature. Door D10. M if taken.
- P2-2: `pack` and `unpack` as `const fn`. Two-way, S.
- P2-3: `From` between `MessageWords` and `[u64; 3]`. Two-way, S.
- P2-4: an `include` that leaves 19 CI files out of the package, and a `documentation` key.
  Two-way, S.
- P2-5: a sentence that a message boundary may split a character. Two-way, S.
- P2-6: `unpack` writes through an out parameter (C-NO-OUT). No change.

### Measured performance

Measured on a Linux x86_64 host;
[the appendix](1159-byte-sink-contract-release-review/what-was-checked.md) has the method and
every row. `pack` of sixteen bytes takes 5.4 ns and `unpack` 5.3 ns, against 38.6 ns and 39.1 ns
for `cobs::encode` and `cobs::decode`. A scratch `unpack` that returns the bytes by value takes
8.8 ns, so the out parameter stays (P2-6). The three refusals of P0-1 add at most 1.4 ns per
message across 256 messages.

## One-way doors

- D1, what `unpack` does with a bytes message the documentation rules out (P0-1). Recommended:
  refuse all three, the stricter choice. A later release can accept what this one refuses.
- D2, the severity field (P0-2). Recommended: freeze eight bits at 39:32 holding the level plus
  one, and a level type of eight variants in place of `u8`.
- D3, the decoder's refusal (P0-3). Recommended: `Result<Message, E>` with a cause in each
  variant of `E`, and `#[non_exhaustive]` on both enums.
- D4, the send outcome (P0-4). The clearance ratified `Sent`; the evidence against it is the
  mapping every caller writes. Recommended: `Result<(), E>` with `Gone` and `NoSink`.
- D5, what an addition does to `VERSION` (P0-5). Recommended: every opcode, kind or field that a
  sink must decode raises `VERSION`.
- D6, free functions or methods (P0-6). The clearance ratified the free functions. Recommended:
  methods of `MessageWords`, under the ratified names.
- D7, `MessageWords` (P0-7). Recommended: ratify as built.
- D8, the identity and the opcode constants (P0-8). Recommended: follow the contract-layout
  decision.
- D9, whether the crate names its system (P1-1). Recommended: one sentence on the crate page,
  in the README and in the description says the framing belongs to the Moho binary interface.
- D10, an `embedded-io` dependency (P2-1). Recommended: none at 0.1.0, the stricter choice. An
  optional feature can join later and breaks no caller.

## Evidence for the shared decisions

- Errors. The crate has no error type. `unpack` reports refusal as the variant `Malformed` of
  the value it decodes, and `classify` reports two failures as variants of `Sent`. `cobs` returns
  `Result` with a `thiserror` enum whose `InvalidFrame` carries `decoded_bytes`. `embedded-io`
  asks each error for a `kind()` from one `#[non_exhaustive]` set. The evidence points to
  `Result`, an enum of causes with both traits, and `#[non_exhaustive]` wherever a new `VERSION`
  can add a variant.
- DMA regions, doorbells and tails, register access, simulators: not applicable.
- Byte sinks and sources. The crate declares no trait. `pack` takes `&[u8]` and returns the
  count it took, which is the contract of `embedded_io::Write::write`, and `unpack` fills a
  caller's `[u8; 16]`. `Gone` and `NoSink` have the kinds `BrokenPipe` and `Unsupported`. The
  trait has no end of stream, so an adapter needs one method beyond it. The evidence points to
  plain slices in the contract and to the trait in an optional feature.
- Feature names. The manifest declares none. `embedded-io` names a feature for the crate it
  turns on (`defmt`), with no version in the name.
- Contract layout. All items sit at the crate root, and the crate has no magic, since a message
  has no header beyond its first word. `VERSION` is a `u32` of 1 and `INTERFACE_ID` a `u64` of 6.
  The opcode is a `u8` at `OPERATION_SHIFT`, 56, with one `OPERATION_` constant for each of two
  opcodes and a `KIND_` constant beside them. The builders are `pack`, which returns
  `(MessageWords, usize)`, then `first_word`, `end_of_stream` and `MessageWords::new`. The decoder
  is `unpack(MessageWords, &mut [u8; 16]) -> Message`, and its one refusal is the variant
  `Malformed`. The decision needs a place for a contract with no reply, where the pair alone is
  the check and D5's rule stands in for a version exchange. It also needs one home for the opcode
  shift that three crates restate.

## Follow-on

- **Outstanding.** The twenty findings, open on the crate's `main` at `8a477c6`, read 2026-11-26
  (UTC).
- **Outstanding.** No decision file names any of the ten doors this block raises, read
  2026-11-26 (UTC).

## Done when

Each of D1 to D10 has a ruling, every P0 and P1 line of the finding status reads Done, and
`script/review-status` counts the block BUILT.

## BUGS

- No crate solves the same problem, so no comparator ranks, and the benchmark's `cobs` rows time
  a neighbor with a different job.
- The review read one architecture's system call header from seL4 and one file of rust-sel4.
- The review counted the callers of no function it recommends changing; the effort across
  callers is an estimate from the cleared package's list of dependents.
- Kani, mutation testing and the falsification patches were not run.

## Index row

The release review of `byte_sink_contract` against seL4's message word, rust-sel4's wrapper for
it, `cobs`, `syslog` and `embedded-io`; no crate ranks as a comparator. Eight findings touch the
0.1.0 interface. They are a decoder that accepts what its documentation rules out, a provisional
severity field, two refusals that are not errors and a version rule the decoder contradicts. The
rest are free functions over a bare word, an unruled struct name and loose identity constants.
Six land before the release, six may follow, and ten doors wait for the architect.
