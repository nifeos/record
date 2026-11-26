---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1071, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1162. `entropy_contract`: the release review's findings

*(The number and the slug are provisional.)*

The release review of `partsfoundry/entropy_contract` at commit `5150f14f`, version 0.1.0-pre.1,
which the tag `v0.1.0-pre.1` names. It runs under milestone 1129 (the combine review), whose
[block](1129-crate-interfaces-best-in-class.md) sets its form. The baseline is milestone 1071
(what an outside maintainer would fix before 0.1.0), [its block](1071-entropy-contract-outside-review.md)
and the cleared package [`notes/crate-reviews/entropy-contract.md`](../../notes/crate-reviews/entropy-contract.md).
Every 1071 finding reads Done. The crate's name, the identity values (12 and 1, no magic), the
nineteen ratified names and the wire rules of 1071's decision 2 stay closed. No later rule of
[design/naming.md](../naming.md) touches a ratified name.

Reuse: the crate's tests and one scratch program.

## Finding status

- P0-1, three one-byte fields are `u64` values checked at run time: Open.
- P0-2, the two range refusals are unit structs a caller can build: Waiting on the errors decision of milestone 1129.
- P0-3, `Refusal::NoService` drops the word that was not a count: Open.
- P0-4, a byte count is a `u64` in four items and a `usize` in three: Open.
- P0-5, `request(GET, 0)` builds a request whose full answer reads as `NO_ENTROPY`: Open.
- P0-6, `VERSION`, `INTERFACE_ID` and the request and readiness entry points have no shared spelling: Waiting on the contract-layout decision of milestone 1129.
- P0-7, ten public names carry no ruling: Open.
- P1-1, the documentation leans on a kernel it never names: Open.
- P1-2, `Refusal` has no `Display` and is not an error: Waiting on the errors decision of milestone 1129.
- P1-3, nothing reads a readiness word back: Open.
- P1-4, `fill_with` has no `# Errors` section, and eight example lines unwrap: Open.
- P1-5, the three refusal types have no `Hash`: Open.
- P2-1, a `rand_core` adapter: Waiting on the feature-name decision of milestone 1129.
- P2-2, `readiness` does not take a slice: Open.
- P2-3, the package ships the repository's CI files: Open.
- P2-4, `bring_up_failure` builds a word for a reserved step: Open.
- P2-5, every word is a bare `u64`: Open.

## Open decisions

The one-way doors D1 to D10 below.

## Goal

A stranger who writes an entropy service, or a client of one, knows which system's call the two
words ride on. The compiler refuses an opcode or a step that does not fit its byte, and a failed
fill tells the caller what the kernel answered, in an ordinary Rust error.

## What the review read and ran

[The appendix](1162-entropy-contract-release-review/what-was-checked.md) lists what the lane
read and each command's result.
[The guidelines table](1162-entropy-contract-release-review/api-guidelines.md) marks
`entropy_contract` against the 54 API Guidelines items, and
[the later items](1162-entropy-contract-release-review/later-items.md) hold its P2 findings in full.

## Prior art

Measured from the crates.io API on 2026-11-26 at 23:13 (UTC). A stranger brings this crate one
problem: the words a client and a service exchange to move random bytes between two processes.
Ten searches of crates.io found no crate that defines such an exchange, so no comparator ranks.
The neighbors solve its two ends, and the systems outside crates.io set the bar.

| crate or system | role | version read | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `getrandom` | neighbor: the client's end, fill a slice or get an error | 0.4.3 | 2,766,488,994 | 889,422,779 | 6,791 | 2026-06-17 |
| `virtio-drivers` | neighbor: the device's end, `device::rng::VirtIORng` | 0.13.0 | 445,812 | 101,928 | 91 | 2026-03-03 |
| `rand_core` | integration target: `TryRng` | 0.10.1 | 2,322,813,641 | 693,909,165 | 2,832 | 2026-09-02 |
| Hubris `idl/rng.idol` and `drv/rng-api/src/lib.rs` | outside crates.io: the entropy service of a microkernel system | commit `969bac2b` | | | | |
| VIRTIO `device-types/entropy/description.tex` | outside Rust: the entropy device | v1.4-cs01 | | | | |
| Linux `drivers/char/random.c`, `drivers/char/hw_random/core.c` and `virtio-rng.c` | outside Rust | v6.12 | | | | |

### What `entropy_contract` does better

- Than Hubris's `rng.idol`: the words on the wire are in the source, and seven Kani harnesses
  prove them. Hubris generates its client stub in a build script.
- Than the VIRTIO entropy device: a service can say it has nothing to give. The specification
  requires one or more bytes and defines no report of a dry source.
- Than `virtio-drivers`: `fill_with` refuses a short answer. `VirtIORng::request_entropy` returns
  the count, and each caller writes its own loop.
- Than `getrandom`: the refusal is an enum that tells a missing service from a dry one.
  `getrandom::Error` is one opaque code. This crate forbids `unsafe`.
- Than Linux's `hw_random` core, which judges no byte: a readiness rule that refuses an all-zero
  or a stuck first draw.

Each of them moves a whole buffer in one round trip, and this crate moves eight bytes. Door D8
weighs that.

## The items

Effort is S (half a day), M (a day or two) or L (longer). Line numbers are of `src/lib.rs`.

### P0: the 0.1.0 interface

#### P0-1. Three one-byte fields are `u64` values checked at run time

Verified in source (lines 95, 118, 183 and 268) and by building. The opcode fills bits 63:56 and
a step fills bits 7:0. `request` takes the opcode as a `u64` and `bring_up_failure` takes the
step as a `u64`. Each returns a `Result` whose one refusal means the value did not fit a byte.
`operation` returns a `u64` that never exceeds 0xff. `GET` and the three `STEP_` constants are
`u64`. Hubris's stub takes no opcode from its caller. Milestone 1071's decision 4 chose the
`Result` over a panic, provisionally.
Change: `u8` for the opcode and the step, in the parameters, in `operation`'s return and in the
four constants. Both builders then return a bare word, and both refusal types go.
Door: one-way (D1). Effort: S in the crate, S across callers.

#### P0-2. The two range refusals are unit structs a caller can build

Verified in source (lines 126 and 276) and by building: `let refusal = OperationOutOfRange;`
compiles outside the crate. Neither type carries the value it refused, and neither is
`#[non_exhaustive]`, so neither can gain a field. The item stands only if door D1 keeps the two
types.
Change: the shape the errors decision picks, with the refused value as a field.
Door: one-way (D5). Effort: S.

#### P0-3. `Refusal::NoService` drops the word that was not a count

Verified in source (lines 475 to 488 and line 530) and by building. `fill_with` reads a first reply
word above `MAXIMUM_BYTES` as the kernel's answer and returns `NoService`. The word says which
failure it was, and the variant has no field for it. `getrandom::Error::raw_os_error` hands back the
code the system gave (`src/error.rs`). Hubris's `RngError` tells a restarted server from five device
faults. A unit variant cannot gain a field after 0.1.0 without breaking every caller that names it.
Change: `NoService { first_reply_word: u64 }`, the field's name provisional.
Door: one-way (D2). Effort: S.

#### P0-4. A byte count is a `u64` in four items and a `usize` in three

Verified in source. `MAXIMUM_BYTES`, `request`'s `byte_count`, `requested_bytes` and the first
word of `reply` are `u64`. `delivered_bytes`, `copy_delivered_bytes` and both fields of
`ShortReply` are `usize`. Fifteen lines of the library and its examples carry an `as usize` or an
`as u64` cast, six of them `MAXIMUM_BYTES as usize`. Every count a caller holds is a slice
length.
Change: a count is a `usize` wherever a function takes or returns one, and `MAXIMUM_BYTES` is a
`usize`. The two reply words stay `u64`, since they are words.
Door: one-way (D3). Effort: S in the crate, S across callers.

#### P0-5. `request(GET, 0)` builds a request whose full answer reads as `NO_ENTROPY`

Verified by building. `request(GET, 0)` returns `Ok(0x0100_0000_0000_0000)`, and `reply(&[])`
returns `(0, 0)`, which is `NO_ENTROPY`. A client that asks for nothing cannot tell a full answer
from a dry source. `fill_with` never sends a zero count, and no text says what one means. Linux's
`getrandom` answers a zero length with zero and no error. A refusal added after 0.1.0 changes
published behavior.
Change: `request` refuses a zero count, and the contract says a client never sends one.
Door: one-way (D4). Effort: S.

#### P0-6. `VERSION`, `INTERFACE_ID` and the request and readiness entry points have no shared spelling

Verified in source (lines 82 and 89). `VERSION` is a `u32` of 1 and `INTERFACE_ID` a `u64` of 12,
with no magic. The shared-decision section lists the entry points. Nothing says whether a new
`VERSION` is a breaking release of the crate.
Change: the names, types and places the contract-layout decision picks.
Door: one-way (D6). Effort: S.

#### P0-7. Ten public names carry no ruling

Verified in milestone 1071's decisions 1, 3 and 4, which call each provisional until this review:
`STEP_FIRST_ALL_SAME`, `request_is_well_formed`, `Refusal`, `NoService`, `ShortReply`, its fields
`asked` and `delivered`, `reply`, `OperationOutOfRange` and `StepOutOfRange`. A tag makes each
permanent. Two do not fit as built. `ShortReply` also names a reply longer than the request. A
scratch call that asked for four bytes and got eight returned
`ShortReply { asked: 4, delivered: 8 }`.
The yes-or-no rule of [design/naming.md](../naming.md) opens such a name with `is_`, and
`request_is_well_formed` carries it in the middle.
Change: ratify eight as built, less those P0-1 removes, and rule the two.
Door: one-way (D7). Effort: S.

### P1: before the first release

#### P1-1. The documentation leans on a kernel it never names

Verified in source and the README. Both define a `CALL` as the kernel's synchronous message call
and never say which kernel. `delivered_bytes` rests on a rule that kernel must keep. The README
names the note that lists a program's interfaces and links nothing.
Change: one sentence that names the binary interface (door D9), and a link for the note.
Door: two-way, apart from D9. Effort: S.

#### P1-2. `Refusal` has no `Display` and is not an error

Verified in source (line 475) and by building: a function bounded on `core::error::Error` refuses
`Refusal`, and `{}` does not format it. `getrandom::Error` implements both (`src/error.rs`, lines
210 and 229). `rand_core`'s `TryRng` requires `type Error: core::error::Error` (`src/lib.rs`, line
192), so P2-1 waits on this.
Change: both traits, in the wording the errors decision picks.
Door: two-way. Effort: S.

#### P1-3. Nothing reads a readiness word back

Verified in source. `readiness` and `bring_up_failure` build the word a service sends. The
program that receives it compares `READY` and `BRING_UP_FAILED` by hand, and no function
returns the step. The reply side has `delivered_bytes` for its word.
Change: a `const fn` from a report word to ready, a failed step, or neither, its name
provisional.
Door: two-way. Effort: S.

#### P1-4. `fill_with` has no `# Errors` section, and eight example lines unwrap

Verified in source. `request` and `bring_up_failure` have an `# Errors` heading, and `fill_with`
states its refusals in running text. Eight lines of the item examples call `unwrap` or `expect`
on a request, where the crate page's example uses `?`. Thirteen lines of prose say opcode for
what every name calls an operation.
Change: the heading, `?` in the examples, and one word for the field.
Door: two-way. Effort: S.

#### P1-5. The three refusal types have no `Hash`

Verified in source (lines 126, 276 and 473). Each derives `Debug`, `Clone`, `Copy`, `PartialEq`
and `Eq`.
Change: derive `Hash` on each that stays.
Door: two-way. Effort: S.

### P2: may follow

Each is verified in source or by building, except P2-1, which is inferred. The evidence is in
[the later items](1162-entropy-contract-release-review/later-items.md).

- P2-1: a type that holds the `CALL` closure and implements `rand_core`'s `TryRng`, behind a
  feature. It needs P1-2 first. Two-way, S.
- P2-2: `readiness` accepts a slice, or its example shows `.iter().copied()`. Two-way, S.
- P2-3: an `include` list that leaves 20 CI files out of the package. Two-way, S.
- P2-4: the documentation of `bring_up_failure` says it judges no reserved step. Two-way, S.
- P2-5: every word is a bare `u64` (C-NEWTYPE). No change at 0.1.0; door D10. M if taken.

### Measured performance

Run on a Linux x86_64 host, release profile;
[the appendix](1162-entropy-contract-release-review/what-was-checked.md#the-benchmark) gives the
method and what each column includes.

| buffer | `fill_with`, stubbed `CALL` | one stubbed call for the buffer | `getrandom::fill` 0.4.3 |
|---|---|---|---|
| 32 bytes | 23.1 ns, 4 round trips | 12.4 ns | 90.1 ns |
| 4,096 bytes | 2,647.5 ns, 512 round trips | 1,352.0 ns | 7,298.5 ns |

The contract's own packing costs about 5 ns for each round trip. The cost that matters is the
count of round trips, each a real `CALL`. Not run: the time of a real `CALL`, which needs the
kernel this host does not run.

## One-way doors

- D1, the type of an opcode and a step (P0-1). Recommended: `u8` in both parameters, in
  `operation`'s return and in the four constants. The compiler then refuses what the `Result`
  reports, and two refusal types go.
- D2, what `NoService` carries (P0-3). Recommended: the first reply word, as a named field.
- D3, the type of a byte count (P0-4). Recommended: `usize` in every function and in
  `MAXIMUM_BYTES`, and `u64` for the words alone.
- D4, a request for zero bytes (P0-5). Recommended: `request` refuses it, the stricter choice.
  Accepting it later breaks no caller. It keeps `request` fallible if D1 is taken.
- D5, the range refusals (P0-2). Recommended: none, if D1 is taken. Otherwise one
  `#[non_exhaustive]` shape with the refused value, by the errors decision.
- D6, `VERSION`, `INTERFACE_ID` and the entry points (P0-6). Recommended: ratify by the
  contract-layout decision, with a rule that a new `VERSION` is a breaking release.
- D7, the ten names (P0-7). Recommended: ratify eight as built. For `ShortReply`, a name that
  covers a longer reply too, such as `WrongCount`. For `request_is_well_formed`,
  `is_well_formed_request`. Both replacements are provisional.
- D8, eight bytes for each round trip, which the frozen identity fixes. Hubris fills a leased
  buffer in one message, and VIRTIO and Linux fill the caller's. Recommended: keep eight at
  `VERSION` 1. A wider reply is a new version, and nothing in 0.1.0 blocks one.
- D9, whether the crate names its system (P1-1). Recommended: `entropy_contract` says once, on
  its crate page, in its README and in its description, that a `CALL` is Moho's.
- D10, a newtype for a word (P2-5). Recommended: keep `u64`, the looser choice. The words cross a
  system call as numbers, and typed functions can join the `u64` ones later.

## Evidence for the shared decisions

- Errors. Three types. `OperationOutOfRange` and `StepOutOfRange` are unit structs with `Display`
  and `core::error::Error`. `Refusal` is a `#[non_exhaustive]` enum with a unit variant and a
  variant of named fields, and neither trait. `delivered_bytes` returns an `Option`.
  `getrandom` has one opaque `Error` with both traits and `raw_os_error`. Hubris has one C-like
  enum for the operation. The evidence points to
  one enum for each operation, named fields, both traits, `#[non_exhaustive]`, and the system's
  own answer carried in the refusal.
- DMA regions, doorbells and tails, register access, simulators: not applicable.
- Byte sinks and sources. The crate declares no trait. `fill_with` takes a `&mut [u8]` and a
  closure, the shape of `getrandom::fill` and `TryRng::try_fill_bytes`. The evidence points to
  `rand_core`, not `embedded-io`, as the trait a byte source of this kind implements.
- Feature names. The crate declares none. `getrandom` names a feature for what it turns on
  (`std`, `sys_rng`, `wasm_js`) and puts no version in a name. `rand_core` 0.10.1 declares none.
- Contract layout. `INTERFACE_ID: u64 = 12` and `VERSION: u32 = 1` at the root, no `MAGIC`. The
  request side spells `request`, `operation`, `requested_bytes` and `request_is_well_formed`. The
  reply side spells `reply`, `delivered_bytes` and `copy_delivered_bytes`. The decoder has two
  refusals of different kinds: a `bool` for a request and an `Option` for a reply. The decision
  needs a place for a message contract: no magic, and a builder and a reader for each word.

## Follow-on

- **Outstanding.** The seventeen findings, open on the crate's `main` at `5150f14`, read
  2026-11-26 (UTC).
- **Outstanding.** No decision file names a door of `entropy_contract`, so D1 to D10 have no
  ruling, read 2026-11-26 (UTC).

## Done when

Each of the ten `entropy_contract` doors has a ruling, every P0 and P1 line above reads Done,
and `script/review-status` counts block 1162 BUILT.

## BUGS

- No crate solves the same problem, so every Rust comparison is with a neighbor.
- The benchmark stubs the `CALL`, so it does not measure what a round trip costs.
- The review counted no callers; the effort across callers is an estimate.
- The review read Hubris at one commit of its main branch, which carries no release tag.
- Kani and mutation testing were not run.

## Index row

The release review of `entropy_contract` against Hubris's entropy interface, the VIRTIO entropy
device, Linux's `getrandom`, and the crates `getrandom`, `virtio-drivers` and `rand_core`; no
crate ranks as a comparator. Seven findings touch the 0.1.0 interface: one-byte fields typed
`u64`, unit refusals, a refusal that drops the kernel's word, mixed count types, a zero-byte
request, the identity spelling and names without a ruling. Five land before the release, five may
follow, and ten doors wait for the architect.
