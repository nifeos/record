# The P2 findings: later

An appendix to [the milestone](../1126-moho-design-review.md), in the main page's shape.

## 15. A holder cannot ask a capability what it is

Moho: no method reports a capability's object type, its rights or its badge. A program learns a
slot's kind by calling a method and reading the refusal, which finding 2 makes unsafe.

Others: every Coyotos capability answers `getType`
([Cap.idl](https://gitlab.com/william-ml-leslie/coyotos/-/blob/fcaf11835e75567a6151102543f241a51b5b15e3/src/sys/idl/Cap.idl)).
Every KeyKOS key answers the order code `kt` with its alleged type
([note](http://cap-lore.com/CapTheory/KK/m/35.html)). Zircon's `zx_object_get_info` returns a
handle's type and rights (from memory, not fetched). seL4 offers one only in a debug build (from
memory).

Deliberate: §15 (the native ABI) refused a self-describing start for now: a program hardcodes
the slots its loader fills. No decision covers a capability received at run time.

Example: a server receives a capability by `RECEIVE_CAPABILITY` from a client it does not
trust. It expects a frame. It has no safe way to check before it maps, and the refusal it would
read depends on what the client sent.

Fix: one method number that every object answers with its rights, once finding 2 makes a shared
number possible. It reports no object kind. The maintainer ruled this provisionally.

Effort: S. Door: two-way (an addition).

## 16. Names disagree across modules

Moho: each module took its names alone.

- `WAIT` means three things: `notification::WAIT` takes a word, `interrupt::WAIT` takes an
  interrupt and `address_space::WAIT` parks on an address.
- `rights::BIND` joins a thread to a process. `notification::BIND` binds a notification to a
  thread and needs `WRITE`, not `BIND`.
- Three calls map a page with three argument orders: `memory_region::MAP`, `page_frame::MAP`
  and `address_space::MAP_INTO`. One takes a `writable` flag and one a `MAP_` mode.
- `page_frame::REVOKE` deletes the caller's capability on a frame and keeps it on a device.
  `port_range::REVOKE` is 1 and the module has no method 0.
- `address_space::LIST` ends on `survey::DONE`. `survey::record` nests its selectors and `usage`
  does not. `usage::RENDEZVOUS` is singular beside `ADDRESS_SPACES` and `THREADS`.
- The prose says endpoint, untyped, TCB and cspace where the names say rendezvous, memory
  region, thread control block and capability table.
- `CAPABILITY_INSERT` writes a target slot as the slot plus one; `RETYPE_OBJECT` writes a floor.

Others: seL4 prefixes every invocation with its object (`seL4_TCB_Configure`), and Zircon every
call with its noun (`zx_futex_wait`, `zx_port_wait`), so one verb never stands alone.

Deliberate: no. All but a few of these names read provisional
(`notes/crate-reviews/moho-abi.md`). `MAP_READ_ONLY` and `MAP_READ_WRITE` hold a ratification, and this
finding does not reopen them: it asks that `page_frame::MAP` take them.

Example: an author who learned `notification::BIND` assumes it needs `rights::BIND`, narrows a
capability to that right, and reads `NotPermitted`.

Fix: the implementing lane makes one naming pass before the publish. A verb never means two
acts. A right and a method share a name only when the method needs that right. The three maps
share one argument order and the ratified `MAP_` modes. The prose uses the names' own vocabulary.
Every new name stays provisional until the release review ratifies the list.

Effort: M. Door: one-way at publish (published names).

## 17. A fault ends in a death message

Moho: a fault or an exit sends one message to the supervision rendezvous, and the thread is a
corpse (`src/fault.rs`). The crate reserves word 4 for a reply protocol that does not exist. A death
read by `RECEIVE_CAPABILITY` loses the faulting program counter.

Others: in seL4 "replying to the exception message restarts the thread"
([manual](https://sel4.systems/Info/Docs/seL4-manual-latest.pdf), section 6.1.13). A Zircon
handler marks an exception handled and the thread resumes
([exceptions](https://fuchsia.dev/fuchsia-src/concepts/kernel/exceptions)). Hubris, like Moho,
restarts and never repairs.

Deliberate: yes. `src/fault.rs` states that restart policy lives in user mode and reserves the
word.

Example: a debugger cannot stop a thread at a breakpoint, show its state and let it run on,
and a pager cannot supply a missing page.

Fix: none now. The maintainer deferred this finding. Before the publish, the crate states that
the reserved word is where a reply protocol will arrive, so that its arrival is an addition.

Effort: S for the statement. Door: two-way.

## 18. Device and board matter sits in the portable interface

Moho: the crate holds a virtio ring layout with `QUEUE_ENTRIES` fixed at 8, a serial port's
register shape, firmware return codes (`reboot::from_psci`, `from_sbi`), a promise of a 10 ms
scheduler tick (`timer`), and prose that names one interrupt controller (`interrupt`).

Others: CloudABI's 49 calls name no device. seL4 keeps architecture invocations in interface
files apart from the portable ones, and Hubris keeps drivers' contracts in Idol files outside
`sys/abi` (both from memory).

Deliberate: in part. §16 (object revocation), in its amendment of 2026-10-27 (UTC), records the
virtio device slot as kernel state. Item 17 of milestone 1075 (`abi`: what an outside maintainer
would fix before the move) already questioned `CycleMeaning`.

Example: a second kernel that serves Moho on a board with another interrupt controller, or
with 256-entry queues, cannot claim version 1.

Fix: deferred by the maintainer. The open question is which modules every Moho kernel serves and
which belong to one platform, as two feature sets or two crates.

Effort: M. Door: two-way until a second kernel exists.

## 19. Revocation reaches a region or a frame, never one delegation

Moho: `memory_region::DESTROY` reclaims a region and stales every capability into it.
`page_frame::REVOKE` deletes every capability to a frame, and a slice escapes its source's
revoke. Nothing takes back one client's access to a rendezvous while the others keep theirs.

Others: seL4 revokes the children of one capability, so a server revokes one badged copy
([manual](https://sel4.systems/Info/Docs/seL4-manual-latest.pdf), section 3.2). EROS and KeyKOS
hand out an indirection object and destroy it
([EROS](http://flint.cs.yale.edu/cs428/doc/eros.pdf)). Genode revokes by destroying the session
object. Zircon and Capsicum have no revocation (inferred from its absence in their documents).

Deliberate: yes. §16 (object revocation) chose region ownership and generational names over a
derivation tree, and calls the tree a later addition.

Example: a server wants to cut off one misbehaving client of forty. It can stop answering that
badge, but the client still holds the capability and can still block in `CALL`.

Fix: none now. Finding 9 keeps revocation per page. A forwarder object, as in EROS, fits §16's
model without a derivation tree and can arrive as a new object type. A revoke scoped to one
derivation may also come later.

Effort: L. Door: two-way (an addition).
