# Open decisions, and the prior art

An appendix to [the milestone](../1128-moho-rulings-implementation-plan.md).

## Prior art

- Fuchsia generates its system call bindings and documentation from one definition file (its
  `kazoo` tool, now `zither`), the shape of step 1 (recalled, not read).
- seL4 landed its scheduling-context interface, a breaking change, behind a build option before it
  became the default, the shape of the `unstable` feature (recalled, not read).
- Linux assigns a new system call one number per architecture in one commit, so a table change
  lands whole (recalled, not read).

## Whether 2.0 may change between nife commits before it is whole

Ruled by the maintainer on 2026-11-25 (UTC), provisional: A. The version moves to 2.0 in step 9,
and steps 10 to 12 change 2.0 before any publish. Step 13 writes the pinned list for 2.0, and the
tag comes only after it. Two nife commits between steps 9 and 12 may both say 2.0 and disagree.

Reason: nobody holds a Moho program and the tag waits for step 13, so the door stays two-way until
the publish.

## What a call with an undefined method number answers

Ruled on 2026-11-25 (UTC): A. An undefined method number faults the caller, as an undefined argument
word, flag or rights bit does under finding 3. `std` stops probing method `0xffff` and reads the
version pair. Step 10 carries it.

Reason: the version pair now does the probe's job, and one rule for undefined input is simpler than two.

## Which fault finding 3 raises, and what the supervisor reads

Ruled on 2026-11-25 (UTC): A. A new fault kind, the argument fault (name provisional), carries the
method number and which word was wrong, zero for an undefined method number. Step 10 carries it.

Reason: the kernel has both in hand when it faults, and the supervisor cannot reliably recover them later.

## How the version pair travels

Ruled on 2026-11-25 (UTC): A. The pair is two 16-bit halves of one `u32`, breaking part high and
additions part low, so comparing whole words orders versions. Steps 8 and 9 carry it.

Reason: a version stays one word everywhere it travels today, and 16 bits leave far more room than the interface needs.

## How the kernel hands its pair to the first program

Ruled on 2026-11-25 (UTC): A. A fourth start register carries the pair, documented in step 2's
program-start section, and the start call takes four words on every architecture. Step 9 carries it.

Reason: one word does not justify a new page; a page or tagged list can be added later without changing the register.

## The largest table a creator may ask for

Ruled by the maintainer on 2026-11-25 (UTC), provisional: A. The table crate holds a bound, set
from today's measured peak with headroom until milestone 778 (capability tables sized per process)
measures, and a larger argument answers `InvalidArgument`.

Reason: a bound only grows, so a later raise stays compatible.

## Whether a method behind `unstable` moves the additions part

Ruled by the maintainer on 2026-11-25 (UTC), provisional: A. The additions part moves when a number
leaves `unstable`, and a program built with `unstable` gets no promise beyond the pair.

Reason: it is the stricter promise; loosening to every addition moving the part later is
compatible, and tightening is not.
