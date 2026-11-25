# The P1 findings: before a stable release

An appendix to [the milestone](../1126-moho-design-review.md). Each finding keeps the main page's
shape: what Moho does, what others do, whether somebody chose the difference, an example, a fix, the
effort and the door.

## 5. One version number, compared by the spawner

Moho: `ABI_VERSION` is one number, and "a new number owes nothing" (`src/lib.rs`). The check is
`serves_declared_abi` in the progenitor: it compares the program's note with the progenitor's
own build-time copy of the constant, by equality, and passes a program with no note. The
kernel reports no version, and no call asks which methods it serves.

Others: a WASI component imports each interface by version, and a host that provides 0.2.6
satisfies an import of 0.2.1
([Text.md](https://github.com/WebAssembly/component-model/blob/585526aa1f2c7f76f07557d16e265dede38b3acb/design/mvp/Text.md)).
Fuchsia stamps a component with a target ABI revision and keeps "a list of supported ABI
revisions"
([RFC-0002](https://fuchsia.dev/fuchsia-src/contribute/governance/rfcs/0002_platform_versioning)),
and `zx_system_get_features` answers at run time. seL4 and Hubris build kernel and programs from
one definition and negotiate nothing; Hubris exposes an image identifier.

Deliberate: half. The crate states equality at spawn and no dual serving beside `ABI_VERSION`. The
missing level for additions follows from "a new number owes nothing" and no decision weighs it.

Example: a program built against a later crate calls a method added after its kernel shipped.
Both sides say version 1, so the spawn passes. The call answers `BadMethod` in the middle of
the program's work, where the author has no way to offer a fallback at start.

Fix: split the number in two. The first part moves on a breaking change and must be equal. The
second counts additions, and a program runs when its second part is at most the kernel's. Have
the kernel hand its pair to the first program it starts, so start checks use the kernel's number
and not the spawner's copy. A query for a single method is not added now; it can arrive later as
an addition.

Effort: M. Door: one-way (the note's meaning).

## 6. A full capability table loses memory, drops a capability or parks a caller

Moho: a table has `CAPABILITY_TABLE_SLOTS` (64) slots. When it is full,
`memory_region::RETYPE` answers `OutOfMemory` and "the run is spent". The kernel drops a delegation that
arrives, and the receiver reads `NO_CAPABILITY`. A `CALL` whose Reply does not fit leaves the
caller parked until a teardown, as §12 (call/reply IPC: a one-shot reply capability) accepts.
Placement differs by method: `RETYPE_OBJECT` takes a `floor`, `CAPABILITY_INSERT` takes a target
written as the slot plus one, and `RETYPE`, `SPLIT`, `BADGE`, `SLICE` and both receives take the
first free slot.

Others: seL4 makes the caller name the destination, and "all slots must be empty or an error
will result"; a receiver names its one receive slot before it waits
([manual](https://sel4.systems/Info/Docs/seL4-manual-latest.pdf), sections 3.1.3 and 4.2.2).
Zircon reports `ZX_ERR_NO_RESOURCES` apart from `ZX_ERR_NO_MEMORY`, and its handle table has no
fixed size (the size is from memory). KeyKOS gives a domain sixteen key slots.

Deliberate: the record holds the size and the parked caller; the three placement conventions
are not a decision.

Example: a server holds 63 capabilities when a client calls. The Reply has no slot. The server
reads `NO_CAPABILITY` and has nothing to answer through, and the client waits until somebody
destroys it. §255 (each socket is its own capability) makes 63 open sockets an ordinary load.

Fix: every method that installs a capability takes the destination slot as its index and
refuses before it spends anything when that slot has an owner. A receive names its landing slot,
so the server reserves room for the Reply before it waits. No form means "any free slot". The
table stays one flat table. The creator of a process sets its size as an argument at creation, and
a table never shrinks. An index past the size answers `InvalidArgument`.

Effort: L. Door: one-way (argument layouts).

## 7. No method copies or narrows a capability in place

Moho: a capability narrows only on its way to another table, through
`rendezvous::SEND_CAPABILITY` or `thread_control_block::CAPABILITY_INSERT`.
`reply::REPLY_CAPABILITY` has no rights argument and says "a server narrows first". No method
lets it.

Others: `zx_handle_duplicate` copies with fewer rights and `zx_handle_replace` narrows in place
([duplicate](https://fuchsia.dev/fuchsia-src/reference/syscalls/handle_duplicate)). seL4's
`CNode_Mint` copies with fewer rights and a badge. Capsicum's `cap_rights_limit` narrows a
descriptor. CloudABI's `fd_stat_put` does the same. WASI 0.2 shares Moho's gap for descriptors.

Deliberate: no. §10 (process model: capability-based, microkernel) rules that rights narrow on
delegation and is silent on narrowing at rest.

Example: a file server wants to answer an open with a read-only frame. It holds the frame with
`READ`, `WRITE` and `GRANT`. `REPLY_CAPABILITY` sends all three, so the client can write the
server's cache.

Fix: one method on every object, or a sixth system call beside `capability_delete`, that copies
a slot with a rights mask. Give `REPLY_CAPABILITY` the mask too.

Effort: M. Door: two-way (an addition), if finding 3 lands first.

## 8. No deadline, and no way to decline to block

Moho: `SEND`, `RECEIVE`, `CALL` and `notification::WAIT` block without bound.
`address_space::WAIT` says "No timeout yet", so `std` cannot serve `park_timeout` or
`Condvar::wait_timeout` (`notes/address-wait.md`, `BUGS`). Only `notification::POLL` declines
to block.

Others: every Zircon wait takes a deadline, `zx_futex_wait` included
([futex_wait](https://fuchsia.dev/fuchsia-src/reference/syscalls/futex_wait)). seL4 has
`NBSend` and `NBRecv` and, like Moho, no timed IPC. Coyotos has a non-blocking send whose stated
use is "a server returning a reply to an untrusted client". Shapiro's 2003 paper names the
attack: a client that makes its server block
([paper](http://web.archive.org/web/20160408020822id_/http://www.eros-os.org/papers/IPC-Assurance.ps)).

Deliberate: yes for IPC. §101 (notification objects) refuses a timed wait and points at a timer
that signals a notification. The address wait's gap is a recorded bug.

Example: a server pushes an event to a client with `SEND`. The client never receives. The
server's only thread stays blocked, and every other client waits behind it.

Fix: add a non-blocking send and a polling receive now. Deadlines, including one on
`address_space::WAIT`, wait for a measurement of message-passing speed. Each arrives as an
addition once finding 3 reserves the words. The maintainer ruled this provisionally.

Effort: M. Door: two-way.

## 9. `GRANT` carries four powers

Moho: `rights::GRANT` allows delegation, `rendezvous::BADGE`, `page_frame::SLICE` and
`page_frame::REVOKE`. `REVOKE` deletes "every capability to it, the caller's own included".

Others: seL4's `Revoke` deletes only the capabilities derived from the one invoked
([manual](https://sel4.systems/Info/Docs/seL4-manual-latest.pdf), section 3.2). Zircon splits
`ZX_RIGHT_DUPLICATE` from `ZX_RIGHT_TRANSFER` and has 25 rights
([rights](https://fuchsia.dev/fuchsia-src/concepts/kernel/rights)). KeyKOS revokes by deleting a
relay the lender owns.

Deliberate: yes. §13 (capability revocation and untyped reclamation) gives `REVOKE` to a holder
of `GRANT`, and §16 (object revocation) refuses a derivation tree. Neither weighs the borrower.

Example: a compositor lends a client a frame with `GRANT`, so the client may pass it to a
decoder. The client calls `REVOKE`. The compositor's own capability and mapping go, and it
faults on its next write.

Fix: a sixth right, revoke, which revoking a page needs and `GRANT` no longer allows. The full
rights set includes it and the spend-only set does not. A lender passes `GRANT` without revoke, so
a borrower can lend further but cannot take back. Revocation stays per page.

Effort: S. Door: one-way (a rights bit and what `REVOKE` needs).

## 10. Four message shapes

Moho: `SEND` moves three words. `SEND_CAPABILITY` moves one word and a capability. `CALL` moves
two words, and `REPLY_CAPABILITY` two words and a capability. `RECEIVE` and `RECEIVE_CAPABILITY`
lay their answers out differently. A plain `RECEIVE` drops a delegated capability, and a `CALL`
that meets it delivers its words and answers `Gone`.

Others: seL4 has one message: a tag with a label, a length and a count of capabilities, then
registers ([manual](https://sel4.systems/Info/Docs/seL4-manual-latest.pdf), section 4.1). A
Zircon channel message is bytes and handles. KeyKOS and EROS send a code, a string and four keys
every time.

Deliberate: yes, three times: §12, §245 (a `CALL` server tells a Reply from a delegation) and
§246 (a plain `RECEIVE` never takes a capability).
Each ruling fixed one case. The cohesion argument for reopening them is that a program author now
learns six rules where one message shape would need none.

Example: a client calls a server that receives with plain `RECEIVE`. The server gets both
words and acts on them. The client reads `Gone` and retries elsewhere. The request ran once more
than the client believes.

Fix: one message and one receive. The message holds an information word that the kernel writes
(word count, capability present, reply awaited), the data words and an optional capability. Send,
call and reply share that shape, and the receive takes any of them into the slot it named.

Effort: L. Door: one-way (layouts).

## 11. Provisional numbers in the pinned set

Moho: the crate marks eight numbers provisional: `SYSTEM_CALL_EXIT_THREAD`,
`object_type::PROCESS`, `process::DESTROY`, `address_space::WAIT` and `WAKE`,
`thread_control_block::SET_THREAD_POINTER`, `reply::REPLY_CAPABILITY` and `reboot::REBOOT`.
`pinned-at-version-1.txt` pins them all.

Others: Zircon's documentation warns in place where a limit "is not yet finalized". WIT marks
such items `@unstable` and hides them unless a build opts in
([WIT.md](https://github.com/WebAssembly/component-model/blob/585526aa1f2c7f76f07557d16e265dede38b3acb/design/mvp/WIT.md)).

Deliberate: the marks are; publishing them is not yet weighed.

Example: an outside program pins the published crate and calls `REBOOT`. The architect then
rules a different number. The crate's own rule makes that a version bump for every program.

Fix: rule the six that the standard library and program start depend on, as stable at their
values under finding 2's renumbering, and put `reboot::REBOOT` behind a Cargo feature that is off
by default (name provisional: `unstable`). The number of `reply::REPLY_CAPABILITY` goes with
finding 10. A number added later starts behind the feature and leaves it when ruled.

Effort: S. Door: one-way (wire numbers).

## 12. Supervision rides on a reserved slot

Moho: `fault::FAULT_RENDEZVOUS_SLOT` is the table's last slot. A spawner inserts a rendezvous
there, and at `START` the kernel reads it, records it and clears it. The slot's index derives
from the table's size, so a larger table is a version bump. The name has its ratification; this
finding is about the mechanism.

Others: seL4 passes the fault endpoint as an argument when it configures a thread (from memory). Zircon creates
an exception channel on the task ([call](https://fuchsia.dev/fuchsia-src/reference/syscalls/task_create_exception_channel)).
Hubris fixes the supervisor at build time.

Deliberate: yes, to add no method. The coupling to the table's size is a side effect.

Example: a builder fills a child's table with first-free inserts and reaches the last slot
with an ordinary rendezvous. The kernel takes it as the supervision target and clears it.

Fix: `START` takes the supervision rendezvous as an argument: a slot index in the supervisor's
own table, in finding 6's encoding, plus a flag bit for whether the child is supervised. The
child's table reserves no slot. A method that sets the supervisor may follow as an addition.

Effort: M. Door: one-way (a slot convention programs build against).

## 13. No definition a tool can read

Moho: the crate is constants and prose. Which word holds which argument, which right a method
needs and which errors it answers exist only in doc comments. Somebody writes each wrapper by hand.

Others: seL4 generates the kernel's decoder and the library's stubs from one XML file. CloudABI
generates headers, documentation and Rust bindings from
[cloudabi.txt](https://github.com/NuxiNL/cloudabi/blob/b3609d5686bbc04655e57fc3913fd2f14a77d41a/cloudabi.txt).
WASI has WIT, Coyotos CapIDL and Hubris Idol.

Deliberate: no. §311 (a contract is code, not prose) asks for more than the crate gives.

Example: `page_frame::MAP` takes `(va, writable, memory_region_slot)` and
`address_space::MAP_INTO` takes `(va, frame_slot, mode)`. A wrapper that swaps two words
compiles, and only a boot test finds it.

Fix: a table in the crate, one row per method (words in, words out, right, refusals), with the
doc comments and a typed wrapper generated from it.

Effort: L. Door: two-way.

## 14. The crate does not say how to trap or how a program starts

Moho: the root's table names the registers. It does not name the instruction, the registers a
trap clobbers, or that word 0 returns in `rdi` on x86_64, where the platform's own convention returns in
`rax`. Modules still write `x0` to `x4`. The crate does not say what a new program finds in its
registers and table, or which crate defines that. `interrupt` and `virtual_io` state no rights,
and no text says how a program comes to hold an `Interrupt`, a `VirtualIo`, a `PortRange` or a
`Reboot` capability.

Others: seL4 ships `libsel4`, which holds the trap for each architecture. Fuchsia makes the vDSO
"the sole means of access" and documents `zx_process_start`'s two arguments. CloudABI defines
the entry point and the auxiliary vector in the same file as the calls.

Deliberate: §124 (ratify the x86_64 system call ABI) chose the registers; §15 (the native ABI)
left the start contract to each program. The silence in the crate is not a decision.

Example: an author writes the x86_64 trap from the table, reads the result from `rax` out of
habit, and reads a register the kernel never wrote.

Fix: a section at the crate root with the instruction and the clobbers for each architecture,
and a pointer to the crate that defines a program's start.

Effort: S. Door: two-way (documentation of a ruled convention).
