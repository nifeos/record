---
status: NOT-STARTED
raised: 2026-11-25
milestone_dependencies: 1126
decision_dependencies: unwritten
machine_requirements: aarch64 silicon; PMU cycle counter
specific_machine: argon (the Jetson TX1 under seL4's published aarch64 numbers, so the comparison is like for like)
needs_person: yes
---
# 1127. Moho from sound to best in class, judged by measurement

The number, title and slug are provisional. The branch that wrote this block is
`milestone/1127-moho-best-in-class`.

Milestone 1126 (Moho against other capability interfaces: a design review) makes Moho sound: it
rules and fixes the interface's one-way findings. This block takes it from sound to best in
class, and a review alone cannot judge that. Each item below ends in a number, a check in CI, a
written promise or a record of what a stranger could not do.

It starts once 1126's P0 fixes land. Items 1 and 4 may start earlier against today's interface,
as a baseline that the later run compares against.

What drives it: the first publish of `nifeos/moho_abi`. Once a program depends on the crate, each
gap below costs a version change to close. What it saves: a second review, and the guesswork of
a program author who reads the crate.

Reuse: `script/bench`, with its `call_reply` and `ipc_rtt_el0` rows. The method and its limits
come from [calibration against seL4](../../notes/benchmarks/calibration-against-sel4.md).
Milestone 127 (the seL4 machine: a Jetson TX1) holds the board, and milestone 74 (cycle counters)
reads its PMU. `script/stranger-test`, from milestone 117 (the stranger test), isolates a fresh
agent.

## Done when

1. A run times message passing on a named target: call and reply, each with and without a
   capability. The result sits beside seL4's published IPC numbers and writes down the method:
   the board, the clock, the build, the iteration count and what each side's figure includes.
   It states the comparison's limits plainly. One side has a fastpath, seL4 publishes one-way
   costs where Moho's rows time a round trip, and the silicon differs wherever the target is not
   seL4's.
2. The machine-readable definition that finding 13's ruling accepts exists, and CI generates or
   checks both the kernel's dispatch and `moho_abi` from it.
3. A written stability promise exists, built on the ruling on finding 5. It says what may change
   in a pre-release, what each part of a version bump means, and how an addition arrives.
4. A fresh agent from outside the project, given only `moho_abi`'s published documentation,
   writes a small real program, such as a server and a client over a rendezvous. Its record names
   every gap it met.
5. The design review's checklist runs again against the fixed interface. A lane fixes each gap
   that remains, or records it with its reason.

## BUGS

- The board behind seL4's numbers is not in hand (milestone 127). Until it is, item 1 runs on
  another aarch64 target, and the result says that the silicon differs.
- Item 4's published documentation means the crate's rendered rustdoc at a pinned commit until
  the crate publishes.

## Index row

Milestone 1126 makes Moho sound; this block makes it best in class and judges it by measurement.
A run times message passing against seL4's published IPC numbers and writes down the method and
its limits. A machine-readable definition drives the kernel and the crate in CI. A stability
promise says what a version bump means. A fresh agent writes a real program from the crate's
documentation alone, and the review's checklist runs again on the fixed interface.
