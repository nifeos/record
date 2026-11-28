---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1098, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1165. `terminal_contract`: the release review's findings

*(The number and the slug are provisional.)*

The release review of `partsfoundry/terminal_contract` at commit `591aed99`, version 0.1.0 with no
tag, under milestone 1129 (the combine review), whose
[block](1129-crate-interfaces-best-in-class.md) sets its form. The crate split out of the crate
that milestone 1098 (`line_editor`: what an outside maintainer would fix before it leaves)
reviewed, so it has no outside review of its own. The baseline is
[that block](1098-line-editor-outside-review.md) and the cleared package
[`notes/crate-reviews/terminal-contract.md`](../../notes/crate-reviews/terminal-contract.md). The
identity values (25, 1, no magic), the refusal of bits 55 to 32 and the crate's name stay closed.
The package left 35 of the 36 public names without a ruling; door D6 brings them.

This review also checks the floor an outside review sets. The README's build, test and bare-metal
commands pass as written, and its text matches the code. Three gaps remain: the names (P0-6), a
missing `#![forbid(unsafe_code)]` (P1-5) and a stranger run that never happened (P2-6).

Reuse: the crate's own tests, and one scratch crate.

## Finding status

- P0-1, seven kinds of word share the type `u64`, and `req` drops what does not fit: Open.
- P0-2, `decode` answers a pair that cannot grow: Open.
- P0-3, one refusal word answers six causes, and nothing reserves a second: Open.
- P0-4, a reply has no rule for a bit its reader does not know: Open.
- P0-5, a count outside an operation's range has no answer: Open.
- P0-6, 35 of 36 public names carry no ruling: Open.
- P0-7, the identity constants, `req` and `decode`: Waiting on the contract-layout decision of milestone 1129.
- P0-8, `VERSION` does not say it covers the swap messages, and `QUIESCED` has two homes: Open.
- P1-1, `decode` owes an error type once it has a second cause: Open.
- P1-2, the documentation speaks one kernel's vocabulary and never names it: Open.
- P1-3, the crate page promises limits, and the crate states none: Open.
- P1-4, one example for six functions, and none on the crate page: Open.
- P1-5, no `#![forbid(unsafe_code)]`: Open.
- P1-6, four operations carry bytes in a word, and no function packs them: Open.
- P1-7, a swap ends the input of a standard-input reader: Open.
- P2-1, no operation reports the terminal's size: Open.
- P2-2, `^C` and `^Z` reach a client by poll alone: Open.
- P2-3, raw mode outlives the client that asked for it: Open.
- P2-4, no `documentation` key, and the package ships the CI files: Open.
- P2-5, an operation prints as a number: Open.
- P2-6, the stranger run has no date, and the changelog promises dates it does not carry: Open.

## Open decisions

The one-way doors D1 to D7 below.

## Goal

A stranger writes a terminal or a client from this crate alone. The compiler refuses a badge
where an operation belongs. A client built at 0.1.0 reads every reply a later terminal sends, and
knows a refusal from a count.

## What the review read and ran

[The appendix](1165-terminal-contract-release-review/what-was-checked.md) lists what the lane read
in the crate, three crates and two systems, with each command's result.
[The guidelines table](1165-terminal-contract-release-review/api-guidelines.md) marks the 54 API
Guidelines items.

## Prior art

Measured from the crates.io API on 2026-11-26 at 23:14 (UTC). A stranger brings this crate one
problem: the words a program and a terminal exchange, defined once for both sides. `termios`
publishes the POSIX words and ranks first. `redox_termios` publishes the words a microkernel's
terminal server and its clients share, the nearest in kind. No crate publishes a terminal
protocol over a message call, so two systems set the bar for the protocol itself.

| crate or system | role | version read | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `termios` | ranked 1: the POSIX terminal words | 0.3.3 | 70,792,562 | 20,822,010 | 104 | 2020-10-13 |
| `redox_termios` | ranked 2: the words a terminal server and its clients share | 0.1.4 | 7,491,624 | 1,255,672 | 3 | 2026-09-09 |
| `rustix` | neighbor: a whole system call layer; its `termios` module read | 1.1.6 | 1,476,082,831 | 399,671,137 | 2,401 | 2026-10-27 |
| `embedded-io` | integration target | 0.7.1 | 204,395,110 | 94,206,861 | 353 | 2025-10-01 |
| Fuchsia `sdk/fidl/fuchsia.hardware.pty/pty.fidl` | outside Rust | commit `8ff2539f` | | | | |
| 9front `sys/man/8/kbdfs` | outside Rust | commit `d7e009b7` | | | | |

The lane measured `crossterm` 0.29.0 (62,317,184 in 90 days), `console` 0.16.6 (107,470,419),
`vte` 0.15.0 (30,673,502), `termion` 4.0.6 (4,130,496) and `nix` 0.32.0 (271,954,068), and did
not read them. They drive or parse a terminal and define no protocol. `embedded-io` is the trait
a client library would implement over these words; the crate carries no transport, so the
finding belongs to that library.

### What `terminal_contract` does better

- Than `termios` and `redox_termios`: a server decodes through one function that refuses a
  reserved bit. Their words are loose constants, and `redox_termios` hands a `Termios` out as a
  byte slice through `unsafe` blocks.
- Than every comparator: authority is in the protocol. A badge is an allowlist, `admits` is the
  whole table, and an operation added later is refused on every badge until a ruling admits it.
  POSIX grants every holder of the descriptor every call.
- Than Fuchsia's pty: `ReadEvents` clears the events it returns, so a second watcher misses
  them. The counts of `^C` and `^Z` here only rise, and every watcher sees each one.
- Than all of them: three Kani harnesses with falsification patches, no dependency and no
  `unsafe`. `termios` needs `std` and `libc`, and `rustix` needs `bitflags`.
- A swap is in the contract: a parked read gets `FLAG_RETRY`, and the replacement resumes the
  line. No comparator replaces a running terminal.

## The items

Effort is S (half a day), M (a day or two) or L (longer). A one-way item binds every caller from
the first 0.1.0 tag.

### P0: the 0.1.0 interface

#### P0-1. Seven kinds of word share the type `u64`, and `req` drops what does not fit

Verified by building. An operation, a badge, a reply flag, a control message, a note, a start bit
and a reply word are each a `u64`, and each of the first six has a member equal to 1.
`admits(OPERATION_QUIESCE, SUPERVISOR_BADGE)`, with its arguments swapped, compiles.
`admits(RAW_ONLY_BADGE, CTL_QUIT)` compiles, and `FLAG_RETRY == NOTE_NOT_WRITTEN` is true.
`req(257, 5)` builds the word for operation 1, a write. `req(OPERATION_WRITE, 1 << 32 | 7)`
builds a length of 7. The text of `req` mentions neither loss. `rustix` gives each kind a type:
`OptionalActions` is a `#[repr(u32)]` enum, `SpecialCodeIndex` a newtype with associated
constants, and each flag word a `bitflags` type that keeps unknown bits. Fuchsia's protocol
types every argument.
Change: `Operation` and `Badge` (provisional) as `#[repr(transparent)]` newtypes that keep an
unknown value, each with its constants. The reply flags become one flag type. `req` takes an
`Operation` and a `u32`, so nothing is left to drop.
Door: one-way (D1). Effort: M in the crate, S at each caller.

#### P0-2. `decode` answers a pair that cannot grow

Verified by building. `decode` returns `Option<(u64, usize)>`. `decode(0)` is `Some((0, 0))`,
an operation no terminal serves. The reserved bits exist so that a later version can give them a
meaning, and a pair has no place for a third field. `rustix` returns `Termios`, a struct, and
Fuchsia's replies are named structs and tables.
Change: `decode` returns a `Request` (provisional), `#[non_exhaustive]`, with the operation and
the count as fields or methods.
Door: one-way (D2). Effort: S.

#### P0-3. One refusal word answers six causes, and nothing reserves a second

Verified in source. `BAD_REQUEST` is `u64::MAX` in the first reply word. The documentation gives
it six causes: an unknown operation, a reserved bit, a badge that does not admit the operation,
the wrong mode, a second parked read, and a quiesce with no control endpoint. A client cannot
tell a request that will never succeed from one to send again. Every other value of the word is
a count, so a 0.1.0 client reads any second refusal word as a count. Fuchsia answers each method
with a `zx.Result` and names `ZX_ERR_ACCESS_DENIED` apart from `ZX_ERR_INVALID_ARGS`.
Change: the contract reserves a range at the top of the first reply word for refusals, and a
function answers whether a word is one. `BAD_REQUEST` stays the only member at 0.1.0.
Door: one-way (D3). Effort: S.

#### P0-4. A reply has no rule for a bit its reader does not know

Verified by building. `is_retry(0, FLAG_RETRY)` is true, and `is_retry(0, FLAG_RETRY | 1 << 3)`
is false: the test is equality. The README says a new flag keeps the version. A later terminal
that sets a new flag beside `FLAG_RETRY` makes a 0.1.0 client drop the retry. No text says what
the second reply word holds for an operation that does not use it. The request side has the
rule: a terminal refuses bits 55 to 32.
Change: one rule for replies. A terminal sends zero in every bit and word it does not define, a
client ignores a bit it does not know, and `is_retry` tests the bit.
Door: one-way (D4). Effort: S.

#### P0-5. A count outside an operation's range has no answer

Verified by building. `OPERATION_BYTES` and `OPERATION_PRINT` carry a count of 1 to 8, and
`OPERATION_RAWMODE` carries 0 or 1. `decode(req(OPERATION_BYTES, 9))` is `Some((3, 9))`, and no
text says what a terminal answers. Five operations use no count and eight use no second word,
and nothing says a terminal refuses a value there. A terminal that ignores
them at 0.1.0 closes them to later use, as the reserved-bits ruling of the package argues.
Fuchsia's `ClrSetFeature` takes two masks and leaves 31 feature bits free.
Change: the contract gives each operation its range, a terminal answers `BAD_REQUEST` outside
it, and a function checks a decoded request against the table.
Door: one-way (D5). Effort: S.

#### P0-6. 35 of 36 public names carry no ruling

Verified in source and in the cleared package. The crate has 30 constants and 6 functions. The
package records one ruling, `NOTE_NOT_ABSORBED`, and asks for the rest. The README's BUGS
section says the names may change. Against [design/naming.md](../naming.md): `req`, `CTL_` and
`INTRCOUNT` abbreviate, and `READLINE`, `RAWMODE` and `READRAW` run words together beside
`OPERATION_READ_LINE_BYTES`. The parameters `w0`, `r0` and `r1` need a decoder. `QUIESCED`
holds the bytes `QUIT`.
Change: the ruling of door D6, built in one pass.
Door: one-way at the first tag (D6). Effort: S in the crate, M at the callers.

#### P0-7. The identity constants, `req` and `decode`

Verified in source; the contract-layout evidence below lists each. The spellings are
provisional, and the values stay frozen.
Change: the types and spellings the contract-layout decision picks.
Door: one-way. Effort: S.

#### P0-8. `VERSION` does not say it covers the swap messages, and `QUIESCED` has two homes

Verified in source and in the cleared package. `VERSION` is one number for the operations, flags,
badges and reply shapes. Its text leaves out the three control messages, the two start bits and
the four notes, which travel on other endpoints between a terminal and its supervisor. Nothing
says whether a changed note is a new version. The package records that another contract defines
the same `QUIESCED` word, held equal by an assertion in a program.
Change: by door D7, the version text names what it covers, and `QUIESCED` keeps one home.
Door: one-way (D7). Effort: S.

### P1 and P2: before the first release, and after

[The later-items appendix](1165-terminal-contract-release-review/later-items.md) holds the
seven P1 findings and the six P2 findings in full.

### Measured performance

The interface does not shape performance: each function is a shift, a mask or a match on two
words, and the comparators are constants and system calls. The lane ran no comparison. The
table gives the crate's own numbers from the benchmark of
[the appendix](1165-terminal-contract-release-review/what-was-checked.md#the-benchmark), on one
thread:

| operation | `terminal_contract` |
|---|---|
| `req` | 0.65 ns |
| `req`, then `decode` | 0.68 ns |
| `req`, `decode`, then `admits` | 3.69 ns |

No finding follows.

## One-way doors

- D1, typed words (P0-1). Recommended: newtypes that keep an unknown value, and a `req` that
  cannot drop a bit. A `From<u64>` can follow; a `u64` parameter cannot narrow.
- D2, the shape `decode` answers (P0-2). Recommended: a `#[non_exhaustive]` struct.
- D3, the refusal range (P0-3). Recommended: the top 256 values of the first reply word are
  refusals, the stricter choice; a range can shrink and cannot grow.
- D4, unknown reply bits (P0-4). Recommended: a terminal sends zero and a client ignores, so a
  flag can be added without a new version.
- D5, counts out of range (P0-5). Recommended: a terminal refuses them, the stricter choice.
- D6, the names (P0-6). Recommended: the package's table. `req` becomes `first_word`, as
  `byte_sink_contract` spells the same packing. The operations become `OPERATION_READ_LINE`,
  `OPERATION_RAW_MODE`, `OPERATION_READ_RAW` and `OPERATION_INTERRUPT_COUNT`, and `CTL_` becomes
  `CONTROL_`. The parameters become `first_word`, `first_reply_word` and `second_reply_word`.
  `STDIN_BADGE`, `FLAG_EOF` and `len` keep the standard library's spelling. `QUIESCED` keeps
  its value, and its text says why the bytes read `QUIT`.
- D7, what the identity covers (P0-8). Recommended: `VERSION` covers the control messages, the
  start bits and the notes, and says so. `QUIESCED` lives in one crate, and the other takes it
  from there.

## Evidence for the shared decisions

- Errors. §329 (one error convention for the library crates) is decided. Its rule 1 keeps
  an `Option` whose `None` has one cause, which `decode` has today (P1-1). No error type
  exists, and a refusal on the wire is the word `BAD_REQUEST`, a wire value the rules do not
  reach. `termios` returns `std::io::Result`, and `rustix` its own `io::Result`.
  `redox_termios` has no fallible function. Fuchsia puts a `zx.Result` in each
  reply. The evidence repeats the case milestone 1160 (the release review of `clock_contract`)
  found: a refusal that is a wire word needs a type that keeps the word and implements the
  traits. It adds that the word needs a reserved range (P0-3).
- DMA regions, doorbells and tails, register access and simulators do not touch this crate: not
  applicable.
- Byte sinks and sources. The crate declares no trait. Its write and read operations are a byte
  sink and a byte source over a call, and the crate holds the words alone. The evidence points
  to an `embedded-io` implementation in a client library, outside the contract.
- Feature names. The crate declares none, and neither `termios` nor `redox_termios` does.
  `rustix` names a feature for the module it turns on (`termios`).
- Contract layout, in the crate's spellings:
  - Magic: none; a message has no header beyond its first word.
  - Version: `VERSION: u32 = 1` at the root. It is in no message, and no operation returns it.
  - Identity: `INTERFACE_ID: u64 = 25` at the root.
  - Request builder: `req(operation: u64, len: u64) -> u64`, with `OPERATION_SHIFT: u32 = 56`,
    which this crate restates as two other contracts do. The opcodes are ten `OPERATION_`
    constants.
  - Decoder: `decode(w0: u64) -> Option<(u64, usize)>`, which refuses a reserved bit, and the
    field readers `operation` and `len`, which do not.
  - Replies: three `FLAG_` constants, the sentinel `BAD_REQUEST` and the test `is_retry`. No
    item decodes a reply.
  - One table beyond the words: `admits(badge, operation)`.

  The evidence asks the decision for four things. One is a place for a table of what each badge
  may send. One is a layout for the reply side. The last two are the refusal range of P0-3 and
  a rule for a contract whose version rides in no message. Fuchsia marks its library with the
  API level that added it and each method as strict.

## Follow-on

- **Outstanding.** The twenty-one findings, open on the crate's `main` at `591aed9`, read
  2026-11-26 (UTC).
- **Outstanding.** The doors D1 to D7 have no ruling, and no decision file names them, read
  2026-11-26 (UTC).

## Done when

Each of the seven doors has the architect's ruling. No P0 or P1 line above reads Open or
Waiting. `script/review-status` counts the block BUILT.

## BUGS

- No crate publishes a terminal protocol over a message call, so the ranked comparators publish
  the POSIX words.
- The review read one file of Fuchsia and one manual page of 9front, and no terminal that serves
  either.
- The review read no terminal and no client of this crate; P1-7 and P2-3 rest on the
  documentation.
- The review counted no callers; each effort at callers is an estimate.
- The lane ran neither Kani nor mutation testing.

## Index row

The release review of `terminal_contract` against `termios`, `redox_termios`, the `termios`
module of `rustix`, and the terminal protocols of Fuchsia and Plan 9. Eight findings touch the
0.1.0 interface. The largest are seven kinds of word as `u64`, one refusal word with no room for
a second, and replies with no rule for an unknown bit. Seven land before the release, six may
follow, and seven doors wait for the architect.
