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

Background. Finding 3 rules that an undefined argument word, flag or rights bit faults the caller.
It does not say whether an undefined method number is the same kind of mistake. `std` probes the
kernel by calling method `0xffff` and reading `-1` in four files, and that probe must change in
step 10 either way.

Recommendation: A.

- A. An undefined method number faults, as an undefined bit does, and `std` stops probing.
- B. It answers `BadMethod`, and `std` keeps a probe with a number the table reserves for it.

Door: one-way once published.

Blocks: step 10.

## Which fault finding 3 raises, and what the supervisor reads

Background. The ruling says the supervisor reads the fault. The fault message today carries a kind
and an address for memory faults. An argument fault needs a kind of its own, and perhaps the
method number and the word that was wrong.

Recommendation: A.

- A. A new fault kind that carries the method number and the index of the first undefined word.
- B. A new fault kind with no detail; the supervisor reads the caller's registers if it needs more.

Door: one-way once published.

Blocks: step 10.

## How the version pair travels

Background. The pair has two parts. They can share one 32-bit word (16 bits each) or take two words,
in the `INTERFACES` note and in what the kernel hands the first program.

Recommendation: A.

- A. Two 16-bit halves of one `u32`, so a version stays one word everywhere it travels today.
- B. Two `u32` words, at the cost of a wider record in the note.

Door: one-way once published.

Blocks: steps 8 and 9.

## How the kernel hands its pair to the first program

Background. Finding 5 rules that the kernel hands its pair to the first program, and that start
checks use it. The first program receives its start arguments in registers today.

Recommendation: A.

- A. One more start register, documented in step 2's program-start section.
- B. A word in a page the kernel maps for the first program.

Door: one-way once published.

Blocks: step 9.

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
