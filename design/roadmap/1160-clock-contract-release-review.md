---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1083, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1160. `clock_contract`: the release review's findings

*(The number and the slug are provisional.)*

The release review of `partsfoundry/clock_contract` at commit `08ceb003`, version 0.1.0 with no
tag, under milestone 1129 (the combine review), whose
[block](1129-crate-interfaces-best-in-class.md) sets its form. The baseline is milestone 1083 (what
an outside maintainer would fix before it leaves), [its block](1083-clock-contract-outside-review.md)
and the cleared package [`notes/crate-reviews/clock-contract.md`](../../notes/crate-reviews/clock-contract.md).
Every 1083 finding reads Done. The two-copy page, the identity values (8, 1, `CLOCKv01`), the
three authorities and the step bounds stay closed. No rule of [design/naming.md](../naming.md)
later than the names ruling touches a name here. The clearance kept bare `u64` words and one page
type; doors D1 and D2 bring both back with evidence.

Reuse: the crate's own tests and loom models, and one scratch crate.

## Finding status

- P0-1, a value built over a read-only mapping offers `publish` and `initialize`: Open.
- P0-2, six kinds of word share the type `u64`: Open.
- P0-3, `Reading` is exhaustive, and its offset is usable while unknown: Open.
- P0-4, a state and a status share the reply's first word, and nothing reserves 4: Open.
- P0-5, the low 56 bits of a request word have no rule: Open.
- P0-6, no rule for what changes `VERSION`: Open.
- P0-7, the identity constants and the request functions: Waiting on the contract-layout decision of milestone 1129.
- P0-8, `real_time_clock` sits outside the identity, and three of its names lack a ruling: Open.
- P1-1, a refusal is a status word with no error type: Waiting on the errors decision of milestone 1129.
- P1-2, `publish` has no form that gives up: Open.
- P1-3, the word indices of the layout are private: Open.
- P1-4, the documentation carries name notes and parts a stranger cannot see: Open.
- P1-5, no example builds, reads or publishes a page: Open.
- P1-6, the page does not state its byte order: Open.
- P1-7, `Reading` has no `Hash` and no `Default`: Open.
- P2-1, a state or a status prints as a number: Open.
- P2-2, no conversion to `core::time::Duration`: Open.
- P2-3, no `documentation` key, and the package ships the CI files: Open.
- P2-4, `ClockPage::new` narrows its address on a 32-bit target: Open.
- P2-5, three spellings for one kind of time parameter: Open.

## Open decisions

The one-way doors D1 to D8 below.

## Goal

A stranger maps the page, reads the time and cannot use an offset the clock does not vouch for.
A process without the set authority cannot write a call that sets the clock. A program built at
0.1.0 knows which later changes it survives.

## What the review read and ran

[The appendix](1160-clock-contract-release-review/what-was-checked.md) lists what the lane read in
the crate, three crates and two kernels, with each command's result.
[The guidelines table](1160-clock-contract-release-review/api-guidelines.md) marks the 54 API
Guidelines items.

## Prior art

Measured from the crates.io API on 2026-11-26 at 22:53 (UTC). A stranger brings this crate one
problem: several address spaces read one small value that another writes, and no reader waits.
`mmap-sync` solves that for any value and ranks. No crate publishes a clock page, so two kernels
set the bar for the layout.

| crate or system | role | version read | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `mmap-sync` | ranked 1: one value across processes | 2.0.4 | 2,213,018 | 589,643 | 0 | 2026-04-09 |
| `seqlock` | neighbor: the retry loop | 0.2.0 | 5,610,424 | 1,226,473 | 16 | 2023-03-30 |
| `triple_buffer` | neighbor: a reader that never waits | 9.0.1 | 1,556,736 | 671,631 | 19 | 2026-11-07 |
| Linux `include/vdso/datapage.h`, `include/vdso/helpers.h`, `lib/vdso/gettimeofday.c`, `include/linux/seqlock.h` | outside Rust | v6.12 | | | | |
| FreeBSD `sys/sys/vdso.h`, `lib/libc/sys/__vdso_gettimeofday.c`, `sys/kern/kern_tc.c` | outside Rust | release/14.3.0 | | | | |

The lane measured `atomic-time` 1.0.0 (1,916,917 in 90 days) and `left-right` 0.11.8 (8,537,796)
and did not read them. No integration target applies.

### What `clock_contract` does better

- Than `mmap-sync`: a reader needs a read-only mapping and no file. `mmap-sync`'s reader adds to
  a counter on the shared state, so it maps that state writable, and its `read` is `unsafe` with
  a time limit on the result. It needs `std`, `rkyv` and three files.
- Than `seqlock` and Linux's `vdso_data`: a writer stopped in the middle of a write never holds a
  reader. Their readers wait while the count is odd.
- Than `triple_buffer`: many readers and several writers, across address spaces.
- Than FreeBSD's `vdso_timekeep`: one count in one word, where a reader there checks `tk_current`
  and each record's `th_gen`.
- Than all of them: eight loom models and two Kani harnesses with falsification patches.

## The items

Effort is S (half a day), M (a day or two) or L (longer). A one-way item binds every caller from
the first 0.1.0 tag.

### P0: the 0.1.0 interface

#### P0-1. A value built over a read-only mapping offers `publish` and `initialize`

Verified in source. The `# Safety` section of `ClockPage::new` accepts a read-only mapping.
`publish` and `initialize` are safe methods of the same type, and the text says such a call
faults. Rust defines no behavior for a write to memory that is not valid for writes, and a safe
call reaches one from a constructor whose contract the caller kept. Linux's `vdso_read_begin`
takes a `const struct vdso_data *` and `vdso_write_begin` a mutable one. `triple_buffer` splits
into `Input` and `Output`, and `seqlock` writes through a guard.
Change: `ClockPage` keeps `read`. A writer type (`ClockWriter`, provisional) has its own `unsafe`
constructor, whose contract demands a read/write mapping, and carries `initialize`, `publish` and
`read`.
Door: one-way (D1). Effort: S in the crate, S at each writer.

#### P0-2. Six kinds of word share the type `u64`

Verified by building. A state, a status, an operation, a clock kind, a time and a generation are
each a `u64`. `publish(now, state::SET)` compiles and publishes the time as the state.
`policy::decide(now, state::SYNCHRONIZED, now)` compiles and answers 2. `decide(99, ...)` treats
99 as a known state, and `publish(77, 5)` stores it. `propose::request(300)` returns operation 44
in a release build. `mmap-sync` wraps its one word as `InstanceVersion(u64)` with `TryFrom<u64>`.
The cleared package wants a reader to keep a value a newer writer added, and a newtype with
associated constants does.
Change: `State`, `Status` and `Operation` (provisional) as `#[repr(transparent)]` newtypes over
`u64`, each with its constants, `from_word` and `to_word`. `State::is_known` replaces
`state::is_known`. `decide` takes a `State` and returns a `Status`.
Door: one-way (D2); it moves ratified names from modules to types. Effort: M.

#### P0-3. `Reading` is exhaustive, and its offset is usable while unknown

Verified in source and by building. `Reading` has three public fields and no `#[non_exhaustive]`,
so a fourth field breaks every caller that builds one. Its documentation calls the offset
meaningless while the state is `UNKNOWN`. `wall_nanoseconds(reading.offset_nanoseconds, monotonic)`
on such a reading returns uptime since 1970, the answer the crate exists to prevent. Linux's
`do_hres` returns -1 when the clock mode is `VDSO_CLOCKMODE_NONE`, and FreeBSD's `binuptime`
returns `ENOSYS` when `tk_enabled` is zero. Neither hands back a time.
Change: `#[non_exhaustive]`, and `Reading::wall_nanoseconds(&self, monotonic_nanoseconds) ->
Option<u64>` (name provisional), `None` when the state is unknown. The examples use it.
Door: one-way (D3). Effort: S.

#### P0-4. A state and a status share the reply's first word, and nothing reserves 4

Verified in source. The reply to `STATE` carries a state in its first word, and a request the
service does not know gets `status::BAD_REQUEST`, which is 4. The states end at 3. A fifth state
would take 4, and a proposer could not tell it from a refused request.
Change: the contract says no state ever takes the value 4, and a test pins it.
Door: one-way (D4). Effort: S.

#### P0-5. The low 56 bits of a request word have no rule

Verified in source and by building. `propose::operation` discards them:
`operation(request(PROPOSE) | 0xabc)` is 1. No text says whether a service refuses a word that
sets them. If services ignore them at 0.1.0, no later version can give them a meaning an old
service would refuse.
Change: the contract reserves the bits as zero, a service answers `BAD_REQUEST` to a word that
sets one, and a function decodes a word to an operation or a refusal.
Door: one-way (D5). Effort: S.

#### P0-6. No rule for what changes `VERSION`

Verified in source. The crate page freezes the seven-word layout. The documentation of `WORDS`
says a future field is a new index and leaves an old reader unaffected. The two disagree on
whether an eighth word is a break. The four policy constants decide what a service accepts, and
nothing says whether a new bound changes `VERSION` or the crate's major version. FreeBSD's
reader checks `tk_ver` before anything else.
Change: a stability section with the rule of door D6.
Door: one-way (D6). Effort: S.

#### P0-7. The identity constants and the request functions

Verified in source; the contract-layout evidence below lists each. Their types and spellings
are provisional, and the values stay frozen.
Change: the types and spellings the contract-layout decision picks.
Door: one-way. Effort: S.

#### P0-8. `real_time_clock` sits outside the identity, and three of its names lack a ruling

Verified in source and in the cleared package. The module tells a clock service which hardware
clock to drive. No page reader and no proposer sees its values, and `INTERFACE_ID` names the page
and the propose call alone. The documentation of `CMOS` calls its name and value provisional,
while the package records the spelling as kept. The package's table lacks `INDEX_PORT` and
`DATA_PORT`, and neither name says the port belongs to the CMOS clock.
Change: by door D7, the module leaves for the service that reads it, or it stays and door D8
rules the three names.
Door: one-way (D7, D8). Effort: S in the crate, S at the service.

### P1: before the first release

#### P1-1. A refusal is a status word with no error type

Verified in source. `policy::decide` returns a `u64`, and a caller compares it with five
constants. Nothing implements `core::error::Error` or `Display`. `mmap-sync` returns
`SynchronizerError`, one enum under `thiserror`.
Change: what the errors decision picks, over the `Status` type of P0-2.
Door: two-way after P0-2. Effort: S.

#### P1-2. `publish` has no form that gives up

Verified in source. `publish` spins until the claim is free, and the crate's BUGS section says a
stopped claim holder blocks every later writer. `seqlock` has `try_lock_write`, which returns
`None`, and `mmap-sync` returns `WriteLockConflict`.
Change: `try_publish` (provisional), which returns `None` when another writer holds the claim.
Door: two-way. Effort: S.

#### P1-3. The word indices of the layout are private

Verified in source. `WORDS` is public, and the five index constants are not. The documentation
of `WORDS` points to word indices below it, which the rendered page does not show. A reader in C
or assembly copies the numbers from prose. Linux and FreeBSD publish the `struct`.
Change: public index constants, their names provisional, pinned by the layout test.
Door: two-way to add. Effort: S.

#### P1-4. The documentation carries name notes and parts a stranger cannot see

Verified by building the documentation. The summary line of `NANOSECONDS_PER_SECOND` is a note
on a ruling of 2026-10-27, and that of `Reading::offset_nanoseconds` a note on an overlay. The
text names a console driver, a spawn step and a platform abstraction layer of an unnamed system.
Change: each item opens with what it is; each foreign part becomes a plain description.
Door: two-way. Effort: S.

#### P1-5. No example builds, reads or publishes a page

Verified in source. Two functions carry an example, `wall_nanoseconds` and `policy::decide`, and
the README has one, on the policy. No example calls `ClockPage::new`, `read`, `publish` or
`propose::request`. `seqlock` and `triple_buffer` open their crate pages with a write and a read,
and `mmap-sync` ships a reader and a writer.
Change: one example on the crate page over seven `AtomicU64`, and one for a request.
Door: two-way. Effort: S.

#### P1-6. The page does not state its byte order

Verified in source. `MAGIC` is a word, and its documentation says it reads in a hex dump. On the
three little-endian targets the README builds, a dump of bytes shows `10vKCOLC`.
Change: one sentence: every word is in the machine's own order.
Door: two-way. Effort: S.

#### P1-7. `Reading` has no `Hash` and no `Default`

Verified in source. A zeroed page reads as the unknown reading, the natural default.
Change: derive `Hash`, and a `Default` that is that reading.
Door: two-way. Effort: S.

### P2: may follow

The lane verified each in source, except P2-4, an inference: it has no such target installed.

Each is two-way and S.

- P2-1: `Display` for a state and a status, by name, after P0-2.
- P2-2: a time as a `core::time::Duration` since the epoch.
- P2-3: a `documentation` key, and an `include` that drops the 20 CI files of the 40 packaged.
- P2-4: `virtual_address as *const AtomicU64` drops the high half on a 32-bit target with 64-bit
  atomics. A `const` assertion.
- P2-5: `unix_nanoseconds`, `proposed_nanoseconds` and `proposed_unix_nanoseconds` name one kind
  of parameter.

### Measured performance

One thread on a Linux x86_64 host (Intel Xeon Platinum 8160, 2.10 GHz), rustc 1.100.0, release
profile. Each number is the lowest of seven passes divided by the calls in a pass.

| operation | `clock_contract` | `seqlock` 0.2.0 | `mmap-sync` 2.0.4 |
|---|---|---|---|
| read one pair of `u64` | 2.65 ns | 1.34 ns | 18.77 ns |
| write one pair | 11.89 ns | 17.60 ns | 472,284 ns |

The `clock_contract` read includes the magic check, one load beyond `seqlock`'s. The `mmap-sync`
read is with `check_bytes` false, and its write includes a file write. No finding follows.

## One-way doors

- D1, one type or two for the page (P0-1). The clearance kept one. Recommended: two, the
  stricter choice.
- D2, typed words (P0-2). The clearance kept `u64` constants in modules. Recommended: three
  newtypes that keep unknown values. A `From<u64>` can follow; a `u64` parameter cannot narrow.
- D3, the shape of `Reading` (P0-3). Recommended: `#[non_exhaustive]` and the method that returns
  `None`. The fields stay public.
- D4, the reply's number space (P0-4). Recommended: no state takes 4, the stricter choice.
- D5, the reserved bits (P0-5). Recommended: a service refuses them, the stricter choice.
- D6, what changes `VERSION` (P0-6). Recommended: a word past the seventh, or a new meaning for a
  word, is a new magic and version. A new state, status or operation is a minor release. A
  changed policy bound is a major release and leaves `VERSION`.
- D7, where `real_time_clock` lives (P0-8). Recommended: outside this crate, the stricter choice;
  a module can join later.
- D8, the three names, if D7 keeps the module (P0-8). Recommended: ratify `CMOS`, and rename the
  ports `CMOS_INDEX_PORT` and `CMOS_DATA_PORT`.

## Evidence for the shared decisions

- Errors. No error type, and no function returns `Result` or `Option`. `read` never fails,
  `publish` waits, and a refusal is one of five `u64` status words. `mmap-sync` has one enum
  under `thiserror` with eight variants, three of which wrap `std::io::Error`. `seqlock` returns
  `Option` from `try_lock_write`. The evidence adds one case: a refusal that is also a word on
  the wire needs a type that keeps the word and implements the traits.
- DMA regions, doorbells and tails, register access, byte sinks and sources, and simulators do
  not touch this crate: not applicable.
- Feature names. The crate declares none; loom comes in under `cfg(loom)`. `triple_buffer` has
  one feature, `miri`.
- Contract layout, in the crate's spellings:
  - Magic: `MAGIC: u64 = 0x434c_4f43_4b76_3031` at the root. It is word 0 of the page, loaded as
    one `AtomicU64`, and written last by `initialize`. The decision needs a `u64` form beside
    `[u8; 8]` for a page of atomic words, and a rule on byte order (P1-6).
  - Version: `VERSION: u32 = 1` at the root. It is on no page and in no message; the magic's
    digits carry it.
  - Identity: `INTERFACE_ID: u64 = 8` at the root, with `WORDS: usize = 7`.
  - Request builder: `propose::request(operation: u64) -> u64` builds the first word. The second
    word is the caller's own. A debug build asserts the operation fits a byte.
  - Decoder: `propose::operation(word: u64) -> u64`, with no refusal. `ClockPage::read` decodes
    the page and refuses with a value: a wrong magic reads as `state::UNKNOWN`.
  - The reply has no item at all. FreeBSD publishes one `struct` with a version word, `tk_ver`.

  The evidence asks the decision for three things: the home of a decoder's refusals when the
  refusal is a status word (P0-5), whether a decoder refuses reserved bits, and a typed reply.

## Follow-on

- **Outstanding.** The twenty findings, open on the crate's `main` at `08ceb00`, read 2026-11-26
  (UTC).
- **Outstanding.** The doors D1 to D8 have no ruling, and no decision file names them, read
  2026-11-26 (UTC).

## Done when

The architect has ruled all eight doors, no P0 or P1 line above reads Open or Waiting, and
`script/review-status` counts the block BUILT.

## BUGS

- No crate publishes a clock page, so the ranked comparator shares any value.
- The review read the generic vDSO files of Linux and FreeBSD and no architecture's own.
- The benchmark has one thread and no reader under a publishing writer.
- The review counted no callers; each effort at callers is an estimate.
- The lane ran neither Kani nor mutation testing.

## Index row

The release review of `clock_contract` against `mmap-sync`, `seqlock`, `triple_buffer` and the
clock pages of Linux and FreeBSD. Eight findings touch the 0.1.0 interface. The largest are one
page type for readers and writers, six kinds of word as `u64`, and an unknown offset a caller can
use. Seven land before the release, five may follow, and eight doors wait for the architect.
