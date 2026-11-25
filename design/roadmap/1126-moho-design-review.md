---
status: NOT-STARTED
raised: 2026-11-25
milestone_dependencies: none
decision_dependencies: unwritten
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1126. Moho against other capability interfaces: a design review

Raised by a read-only review of Moho, the capability binary interface that `nifeos/moho_abi`
defines and nife's kernel serves. The number is provisional, and the branch is
`milestone/1126-moho-design-review`. Milestone 1075 (`abi`: what an outside maintainer would fix
before the move) asked whether a stranger could adopt the crate. This block asks a different
question: is the interface itself solid and cohesive for a program author, judged against the
capability interfaces that came before it? It changes no code and no decision. It lists what an
architect rules and what later lanes build.

Reuse: none exists to take. The review reads the crate, the kernel's dispatch and the comparators'
own documents; it searched `notes/` and `design/roadmap/` for an earlier comparison and found only
the five-row table in milestone 1075's prior-art appendix.

## Goal

Every one-way door in the interface has a ruling before the crate publishes. A wire number, a
register layout, the meaning of an error code and a published name are such doors. Each
finding below names its door, so the rulings can come one at a time.

## What the review checked, and how

The trees, the kernel functions read and what was not run are in
[the appendix](1126-moho-design-review/what-was-checked.md).

## Prior art

The sources, one row per comparator and dimension, are in
[the appendix](1126-moho-design-review/prior-art.md). Every comparator claim in a finding rests
on a document fetched on 2026-11-25 (UTC), except where the text says "from memory".

## The verdict

Moho is a sound small core with four defects in its calling convention that cost little to fix now
and a rebuild of every program later. The object model holds together: five system calls, one
`invoke`, rights that only narrow, budgets the caller pays, and death as a message. The
convention around it grew one method at a time, and it shows. The status word shares a register
with a sender's data. A method number means a different operation on each object. Nothing refuses
a word or a bit the interface does not define. Fifteen error codes cover about forty distinct
refusals.

## The findings, ranked

Effort: S is under half a day for a lane, M a day or two, L more. A door is one-way when a program
built against the published crate depends on it: a wire number, a layout, a published name, or
what a call means. P0 must change before any publish, P1 before the first release that promises
stability, and P2 can follow.

| id | priority | door | finding |
|---|---|---|---|
| 1 | P0 | one-way | Word 0 carries the kernel's status and a sender's data in one register |
| 2 | P0 | one-way | A method number means a different operation on each object, so a wrong slot acts |
| 3 | P0 | one-way | Nothing refuses an undefined argument word, flag or rights bit |
| 4 | P0 | one-way | Fifteen error codes carry about forty refusals, and five codes carry most of them |
| 5 | P1 | one-way | One version number, compared by the spawner, with no level for additions |
| 6 | P1 | one-way | A full capability table loses memory, drops a capability or parks a caller |
| 7 | P1 | two-way | No method copies or narrows a capability inside its holder's table |
| 8 | P1 | two-way | No blocking call takes a deadline, and no rendezvous call can decline to block |
| 9 | P1 | one-way | `GRANT` carries four powers, and a borrower's `REVOKE` deletes the lender's capability |
| 10 | P1 | one-way | Four message shapes, and a receiver must guess which receive matches the sender |
| 11 | P1 | one-way | Eight numbers the crate itself calls provisional sit in the pinned set |
| 12 | P1 | one-way | Supervision rides on a reserved slot whose index derives from the table's size |
| 13 | P1 | two-way | Argument shapes live only in doc comments; no file a tool can read defines them |
| 14 | P1 | two-way | The crate alone does not tell an author how to trap or how a program starts |
| 15 | P2 | two-way | A holder cannot ask a capability what it is or which rights it carries |
| 16 | P2 | one-way | Names disagree across modules: three `WAIT`s, two `BIND`s, three `MAP`s |
| 17 | P2 | two-way | A fault ends in a death message; no handler can repair and resume |
| 18 | P2 | two-way | Device and board matter sits in the portable interface |
| 19 | P2 | two-way | Revocation reaches a region or a frame, never one delegation |

The P1 findings are in [the appendix](1126-moho-design-review/before-a-stable-release.md), and the
P2 findings in [the appendix](1126-moho-design-review/later-findings.md).

## P0: before any publish

### Finding 1: word 0 carries the kernel's status and a sender's data

Moho: every call returns a result or a negative `Error` in word 0 (`src/lib.rs`, the crate
root's table). `rendezvous::RECEIVE` and `RECEIVE_CAPABILITY` put the sender's first word there,
`notification::WAIT` puts the signal word there, and `rendezvous::CALL` puts the server's `r0`
there. The crate lists the first two under `BUGS`.

Others: Zircon is the clean example: it forbids a payload in the status, "use an out parameter"
([rubric](https://fuchsia.dev/fuchsia-src/development/api/system)). seL4 does not separate them.
The kernel returns "an error code in the message tag", and on IPC between programs the tag's
label "is not interpreted by the kernel and is passed unmodified", so one field carries both
([manual](https://sel4.systems/Info/Docs/seL4-manual-latest.pdf), section 10.1). It avoids
forgery because a receive has no error return for a peer to imitate. Hubris shares Moho's shape and
says so: a server can "fake a dead task" by replying in the dead-code range
([reference](https://hubris.oxide.computer/reference/)).

Deliberate: partly. §245 (a `CALL` server tells a Reply from a delegation) made word 4 the one
register only the kernel writes, for this reason, and stopped at two tags. §325 (the services'
wire error vocabulary) keeps -1 to -255 for the kernel on a reply, and nothing enforces it.

Example: a log server loops on `RECEIVE` and exits when the answer is `Gone`. Any client that
holds `WRITE` sends -11 as its first word. The server reads `Gone` and exits, and every other
client loses the service.

Fix: make a kernel refusal unforgeable on all three paths. The kernel writes word 4 on every
return from a receive, a refusal included, and a refusal carries a third tag. Today a receive
that answers `Gone` returns before it writes word 4, so the caller reads back its own input. A
wrapper tests the tag, never the sign. `notification::WAIT` returns 0 in word 0 and the signal
word in word 1. `reply::REPLY` refuses an `r0` inside the kernel's range. The alternative is
stricter and costs every receiver a layout change: word 0 is always the kernel's status, and
each data word moves down one register.

Effort: M. Door: one-way (a register layout).

### Finding 2: a method number means a different operation on each object

Moho: each module numbers its methods from 0. Method 0 is `rendezvous::SEND`,
`memory_region::MAP`, `process::DESTROY`, `reboot::REBOOT`, `timer::ARM` and
`interrupt::WAIT`. The kernel's `invoke` picks the table by the object in the slot, so a call on
the wrong kind of object runs that object's method of the same number. `Error::WrongObject` is
never the answer for the invoked slot. `console::WRITE`'s own doc comment states the hazard.

Others: Coyotos derives each method code from a hash of its qualified name, and every object
answers an unknown one with `UnknownRequest`
([Cap.idl](https://gitlab.com/william-ml-leslie/coyotos/-/blob/fcaf11835e75567a6151102543f241a51b5b15e3/src/sys/idl/Cap.idl)).
KeyKOS keys answer an invalid order code with `kt+2`
([principles](http://cap-lore.com/Agorics/Library/KeyKos/Principles/chapter3.html)). Hubris
faults a client that sends an undefined operation, since it "intended the message for a different
kind of server"
([abi](https://github.com/oxidecomputer/hubris/blob/969bac2bf47c98710842eb232fdd4a9c54e7dd7f/sys/abi/src/lib.rs)).
seL4 numbers its invocation labels in one list across all objects (from memory, not fetched).

Deliberate: no. No decision chose per-object numbering. §325 records the effect in passing: a
slot holding another object runs that object's method 4.

Example: a supervisor keeps a child's rendezvous in slot 9 and its process capability in slot
10. An off-by-one makes it `SEND` on slot 10. The kernel reads method 0 on a process, which is
`DESTROY`, ignores the three words and kills the child. The supervisor sees 0, a success.

Fix: give every method a number unique across the interface, the object type in the high bits
and the method in the low ones. The kernel then answers `WrongObject` when the slot holds
another kind. The modules keep their names; only the values move.

Effort: M. Door: one-way (every wire number).

### Finding 3: nothing refuses an undefined word, flag or bit

Moho: the doc comments mark unused arguments with `_`, and the kernel never reads them.
`page_frame::MAP` takes any nonzero `writable` as read and write. The kernel converts a rights
word with `as u32` and drops bits it does not know. `address_wait` alone refuses what it does
not define. `survey::record::STATE` records how the rest fares: callers happened to pass 0 in
a then-unused word, which is the only reason a selector could later live there.

Others: Zircon refuses an unknown option bit call by call: `zx_vmo_create` answers
`ZX_ERR_INVALID_ARGS` when "options contains an unsupported combination of flags"
([vmo_create](https://fuchsia.dev/fuchsia-src/reference/syscalls/vmo_create)). Its rubric also
asks for room for future flags ([rubric](https://fuchsia.dev/fuchsia-src/development/api/system)). Hubris
faults a task on "any use of undefined attribute bits"
([syscalls](https://github.com/oxidecomputer/hubris/blob/969bac2bf47c98710842eb232fdd4a9c54e7dd7f/doc/syscalls.adoc)).
Capsicum fails a widening request with `ENOTCAPABLE`
([cap_rights_limit](https://man.freebsd.org/cgi/man.cgi?query=cap_rights_limit&sektion=2)). seL4
is the counterexample: a `Mint` that asks for more rights is "silently downgraded".

Deliberate: no. The entropy contract's wire rules, ruled 2026-11-14 (UTC), already refuse an
unknown operation and reserved bits. The kernel interface never received the same rule.

Example: `notification::WAIT` gains a deadline in word 2. A program built today leaves a stale
value in that register. On the new kernel its wait ends at a deadline it never asked for. The
only cure is a new method number for every call that grows.

Fix: one rule for the whole interface. An argument word, flag or rights bit the method does
not define is zero, or the kernel refuses the call. `writable` takes 0 or 1.

Effort: M. Door: one-way (what a call means). The rule can only loosen later.

### Finding 4: fifteen codes carry about forty refusals

Moho: `Error` has fifteen variants (`src/lib.rs`). Four belong to one method, `reboot::REBOOT`.
The other eleven serve every other refusal:

- `OutOfMemory`: a spent region, a full capability table, an occupied target slot, a full
  object registry, a process at its thread limit.
- `BadMethod`: an unknown method, object type, record selector or flags word.
- `WrongObject`: a wrong kind of capability, a thread in the wrong state, a register offset or
  queue number out of range.
- `BadPointer`: an address the caller could not touch, a cursor never minted, a count of zero,
  an address with nothing mapped.
- `NotPermitted`: a missing right, an object that refuses, a region with children, a
  notification already bound.

Others: seL4 has ten errors, among them `InvalidArgument`, `RangeError`, `DeleteFirst` and
`RevokeFirst`, and adds the argument number or the bounds
([errors.h](https://github.com/seL4/seL4/blob/78b0c34efe12ddfe6e7dd616e8538ce49ebf2890/libsel4/include/sel4/errors.h)).
Zircon separates `NO_MEMORY` from `NO_RESOURCES` and `INVALID_ARGS` from `OUT_OF_RANGE`, and its errors page groups the codes by
category: general, parameter, precondition and state ([errors](https://fuchsia.dev/fuchsia-src/concepts/kernel/errors)).
WASI gives each interface its own error enumeration.

Deliberate: yes for one code. §119 (splitting `OutOfMemory`'s three causes is declined for
want of a customer) weighed `OutOfMemory` on `SPLIT` and `RETYPE_OBJECT`: a spent budget, a full
table, or the system-wide region table full. It deferred the split and left guidance that favors
new variants, on the line POSIX draws between `EMFILE` and `ENFILE`. This finding reopens that
deferral. The customer it waited for is the publish: after it, moving a refusal to another code
is a version change. No decision weighs the other four codes.

Example: `memory_region::RETYPE` answers `OutOfMemory`. If the region has no pages left, the
program needs a larger budget. If the table is full, it needs to delete a capability. If the
system-wide table is full, nothing the program does locally helps. The code does not say which.

Fix: add `InvalidArgument`, `WrongState`, `TableFull` for the caller's own table and a separate
code for a full system-wide registry, the `ENFILE` case. Move each refusal above to the code a
program can act on. Move the four `Reset` codes into the second word of `REBOOT`'s answer. A new
number owes no version change; a moved meaning does. A second defect sits beside this one and is
a two-way fix of its own: `RETYPE` and `RETYPE_OBJECT` spend pages before they find the table
full, where `SPLIT` leaves the parent as it was.

Effort: M. Door: one-way (what a code means).

## What Moho does better

- `Gone` against `NoSuchSlot`. A stale capability keeps its slot and says so. WASI reuses a
  freed index with no generation check, so a stale handle can name a newer resource.
- `NotSupervised` reveals nothing about another supervisor's children, and the crate says why.
- The kernel tags a Reply in a word no sender writes. seL4 asks a receiver to "check the badge".
- The budget model. The caller pays for page tables through one region, where seL4 needs a
  capability for each paging structure.
- W^X is a refusal of the interface, in `address_space::MAP_INTO` and `page_frame::MAP`.
- A retired number stays reserved, a test pins every number, and a changed number fails until
  `ABI_VERSION` moves. No comparator's crate carries that gate.
- A corpse persists and `rendezvous::SURVEY` lists it, so a lister needs no cooperating parent.
- A Reply is one-shot and cannot move, as in EROS and KeyKOS, and the kernel guarantees it.

## Decisions for the architect

Each P0 finding and findings 5, 6, 9, 10, 11, 12 and 16 open a one-way door. None has a
ruling. The maintainer brings them one at a time, in the table's order, each with its background
first. Findings 7, 8, 13, 14, 15, 17, 18 and 19 are two-way, and the maintainer decides them.

## Done when

- Each one-way finding has a ruling recorded in `design/decisions/`, or a refusal with its reason.
- Each ruled change has a lane, and `ABI_VERSION` moves once for the set, not once per change.
- The crate's `BUGS` section no longer lists a defect of the calling convention.

## BUGS

- The review ran nothing. Each kernel claim comes from reading the functions the appendix names,
  confirmed against nife's `main` at `f04f8b4c9`.
- The lint refuses line-number citations, so a finding names a symbol and its file, never a line.
- The count of "about forty" refusals in finding 4 is a hand count of the doc comments.
- The appendix marks five comparator claims as from memory or as inferred from an absence.

## Index row

A design review compared Moho with seL4, Zircon, Genode, Capsicum, CloudABI, WASI, KeyKOS, EROS, Coyotos and Hubris. The object model holds up. The calling convention has four defects to fix before any publish. The status word shares a register with a sender's data. A method number means a different operation on each object. Nothing refuses an undefined word or bit. Fifteen error codes carry about forty refusals. Ten further findings wait for the first stable release and five can follow.
