# Further properties of a good kernel ABI, and the evidence

An appendix to [the milestone](../1126-moho-design-review.md). It continues [the first
part](what-makes-an-abi-good.md), which explains what an ABI is and covers properties 1 to 4, the
four the milestone has ruled.

The review fetched its outside facts and marks the few it took from memory "(from memory)".

### Property 5 (finding 5): versioning leaves room to add

A version scheme has to tell two events apart. A breaking change means old programs must not run. An
addition means old programs run as before, and a new program on an old kernel must find out, before
it starts work, that something it needs is missing. One number compared for equality can express
only the first.

Fuchsia's RFC-0002 separates what a program targeted from what a system can run. At build time a
component receives its stamp: "the tools in the SDK include the target ABI revision associated with
the target API level in the manifest of the component". The system side holds a set: "The platform
maintains a list of supported ABI revisions." One kernel can therefore run programs from several
generations, and can refuse one cleanly at launch.

WASI puts a semantic version on each interface and marks every item with the release that added it:

```
interface foo {
    a: func();

    @since(version = 0.2.1)
    b: func();

    @unstable(feature = fancier-foo)
    d: func();
}
```

A program that imports version 0.2.1 runs on a host that provides 0.2.6. The component model's text
format gives exactly that case as the purpose of its matching rule. A build sees items marked
`@unstable` only when it opts in, so an interface can ship while parts of it stay undecided.

Moho today: one number, `ABI_VERSION`, and the starting program tests it for equality. The program
that starts others makes the check, against its own build-time copy of the number. The kernel
reports no version. Because the crate rules that "a new number owes nothing", a program built
against a later crate passes the check on an older kernel and then meets `BadMethod` in the middle
of its work.

What finding 5 ruled (2026-11-25 UTC): the number splits in two. The first part moves on a breaking
change and must be equal. The second counts additions, and a program runs when its second part is at
most the kernel's. The kernel hands its pair to the first program, and start checks use it. Finding
11 is the companion: six of the eight provisional numbers stay stable, and reboot sits behind a
Cargo feature that is off by default, as WASI does with `@unstable`.

### Property 6 (finding 13): one machine-readable definition generates both sides

When the argument layout of a call lives in prose, somebody writes the kernel's decoder by hand and
somebody else writes the program's wrapper by hand. The two agree only as far as both people read
the prose the same way. A definition that a tool can read removes that gap: the decoder, the
wrappers and the documentation come from one file, and a swapped argument becomes a build error.

seL4 keeps its object interface in XML. This is its capability copy operation, abridged from the
file:

```xml
<interface name="seL4_CNode" ...>
  <method id="CNodeMint" name="Mint" manual_label="cnode_mint">
    <param dir="in" name="dest_index" type="seL4_Word" .../>
    <param dir="in" name="dest_depth" type="seL4_Uint8" .../>
    <param dir="in" name="src_root"   type="seL4_CNode" .../>
    <param dir="in" name="rights"     type="seL4_CapRights_t"> ...
    <param dir="in" name="badge"      type="seL4_Word" .../>
    <error name="seL4_DeleteFirst"
           description="The destination slot contains a capability."/>
    <error name="seL4_RangeError"> ...
  </method>
```

Each parameter has a direction, a name and a type, and each method lists the errors it can answer.
The same file generates the manual's reference chapter. WASI's definition language, WIT (shown under
property 5), does the same job for a different kind of boundary, and its versioning marks live in
the definition, so tools can check compatibility as well as layout.

Moho today: the crate is constants and prose. Which word holds which argument, which right a method
needs and which errors it answers exist only in documentation comments. The review's example: two
mapping calls take `(address, writable, region slot)` and `(address, frame slot, mode)`. A wrapper
that swaps two words compiles, and only a boot test finds it.

The maintainer accepted finding 13 provisionally: a table in the crate with
one row per method: words in, words out, the right needed, the refusals. A tool generates the documentation and a typed wrapper from it. Properties 2, 3
and 4 then become things a tool can check on every change.

### Property 7 (findings 6 and 8): behavior is predictable on exhaustion, with deadlines

Two questions decide whether a server on this interface can be robust. When something runs out, does
the call fail before it changes anything, with a code that says what ran out? And can a program
bound how long it waits for a peer it does not trust?

Exhaustion. seL4 makes the caller name the destination slot for every new capability, and the answer
for an occupied slot is `seL4_DeleteFirst`, as the XML above shows. The kernel spends nothing before
the check, and the server decides in advance where a capability will land.

Deadlines. In Zircon every blocking wait takes one, the futex wait included. The rubric fixes the
form: timeouts "must be expressed as absolute deadlines in nanoseconds".

```c
zx_status_t zx_futex_wait(const zx_futex_t* value_ptr,
                          zx_futex_t current_value,
                          zx_handle_t new_futex_owner,
                          zx_instant_mono_t deadline);
/* ZX_ERR_TIMED_OUT: "The thread was not woken before deadline passed." */
```

The other school. seL4 has no timed message passing, and this is a choice. Its sends and receives
take no time argument. It offers polling forms instead: `seL4_NBSend` "performs a polling send", and
if no receiver is waiting "the message is silently dropped"; `seL4_NBRecv` checks for a message
"without blocking". A program that wants a time limit arms a timer that signals a notification and
waits on both. The reasoning (from memory): a timeout value is policy, no single value is right, and
timeouts on every blocking path add states that a kernel with a machine-checked proof must then
prove correct. Without deadlines the kernel is smaller and the blocking paths are simpler, and every
bounded wait costs a timer object and extra calls. With deadlines the common case is one call, and
the kernel carries a timer queue on its message paths. Moho stands with seL4 for messages today, by
a recorded decision.

Moho today, exhaustion: a capability table has 64 slots. When it is full, three different things
happen depending on the call. A retype answers `OutOfMemory` after spending the pages. The kernel
drops a delegated capability and the receiver reads "no capability". A `CALL` whose one-shot reply
capability does not fit leaves the caller blocked until somebody destroys the callee. Where a new
capability lands follows three different conventions.

What finding 6 ruled (2026-11-25 UTC): every method that installs a capability takes the destination
slot as its index and refuses before it spends anything if the slot has an owner. A receive names
its landing slot, so a server reserves room for the reply before it waits. The table stays flat,
and the creator of a process sets its size.

Moho today, waiting: no blocking call takes a deadline, and only the notification poll declines to
block. The address wait has no timeout, so the standard library cannot offer `park_timeout` or a
timed condition-variable wait. A server that sends an event to a client that never receives stays
blocked, and every other client waits behind it.

What finding 8 became (a provisional ruling of the maintainer): non-blocking send and poll
variants now, for a server answering a client it does not trust, and an address-wait deadline.
Message-passing deadlines wait for a speed measurement. Each is an addition once finding 3 keeps the words they need at zero.

### Property 8 (finding 16): the interface is small and consistently named

Small means few things to learn, few things to secure and few things to keep working for ever.
Consistent means that knowing one call lets a programmer predict the next: the same verb means the
same act, and the same argument sits in the same place. Published names are a one-way door as much
as numbers are, because outside source code builds against them.

Zircon enforces a grammar on names: `zx_<noun>_<verb>`, as in `zx_futex_wait` and `zx_vmo_create`,
with the rule that "The nouns and verbs must not contain underscores (to avoid confusing the
grammar)". seL4 does the same by prefixing every operation with its object: `seL4_CNode_Mint`,
`seL4_TCB_Configure`. A verb never stands alone, so `wait` on one object is never confused with
`wait` on another. On size the two differ sharply. The seL4 manual says "we can regard the kernel as
providing three system calls: Send, Receive and Yield", with object operations layered on them.
Zircon lists 186 calls.

Moho today: on size Moho is at the seL4 end: five system calls, one `invoke`. On names, each module
chose its own. `WAIT` means three things on three objects. `BIND` is both a right and a method that
needs a different right. Three calls map a page with three argument orders. The prose uses one
vocabulary (endpoint, untyped, TCB) and the names another (rendezvous, memory region, thread control
block).

What finding 16 ruled (2026-11-25 UTC): the implementing lane makes one naming pass before the
publish. A verb never means two acts, the three maps share one argument order, and the prose uses
the names' own vocabulary. The release review ratifies the new names.

## The strongest examples, and what each leads on

No system leads on all eight properties. Four are worth knowing, each for a different strength.

| system | leads on | weakness |
|---|---|---|
| seL4 | Rigor and speed. Its proofs run "from high-level specifications to binary code". A cross-address-space call takes 720 cycles on a 64-bit RISC-V board and 419 on a 64-bit Arm board, by its own published figures. One message shape, generated interface. | Hard to use directly. A program manages its own tree of capability tables and addresses a slot by index and depth (five addressing arguments in `Mint` above), and by the review's account needs a capability for each paging structure. The proofs assume, in the project's words, "assembly code, boot code, machine interface, hardware, and DMA", and do not cover every configuration (from memory). |
| Zircon | Readiness for outside developers. A written rubric for every call, deadlines on every wait, versioning that lets one system run several generations, and the vDSO: a library the kernel maps into each program, which is "the sole means of access to system calls", so the trap instruction and its numbers are private and can change. | A large surface (186 calls listed) and no general revocation: no call in the list takes back a handle that another process holds. That second point is inferred from absence. Its own page on `zx_vmo_create` says of running out of memory: "There is no good way for userspace to handle this". |
| WASI 0.2 and the component model | Definition and evolution tooling. WIT definitions with per-item `@since` and `@unstable` marks, semantic versions on each interface, typed results with an error list per interface, bindings generated for many languages. | It is not a kernel. It defines calls between a WebAssembly program and its host, and says nothing about traps, registers, scheduling or page tables.  The review also reports that a freed handle index is reused with no generation check. |
| KeyKOS and EROS | Clean capability semantics. The EROS paper: "All capabilities take the same arguments at the trap interface", four data words, a string and four capabilities every time. A reply capability is consumed on use, "ensuring an at-most-once reply". A capability whose version number no longer matches its object "is invalid and conveys no authority". | Neither is a living platform to learn deployment lessons from. The review found the EROS and Coyotos sites offline and worked from archived copies. Neither has interface versioning or kernel timeouts, by the review's tables. KeyKOS dates from the 1980s and EROS was a research system (from memory). |

Read as a set: the object model comes from KeyKOS and EROS, one message and a generated interface
from seL4, the rubric and versioning from Zircon, and the evolution marks from WIT.

## What Moho already does better

The review lists eight places where Moho leads. Protect them.

- "Gone" is a different answer from "nothing there". A capability whose object died keeps
  its slot and says so. A writer whose reader has exited can stop, while a program that was never
  given an output keeps running. 
- One error hides what should stay hidden. A supervisor that asks about a thread it does not
  supervise gets the same answer whether the thread belongs to somebody else, was already collected
  or never existed, so it cannot probe for other supervisors' children. 
- The kernel tags a reply in a word no sender writes. A server can tell the kernel's one-shot reply
  capability from a capability a client sent. By the review's reading, seL4 asks the receiver to
  check the badge instead.
- The budget model. A program pays for its page tables out of one memory region it holds, where
  seL4 needs a separate capability for each paging structure.
- No page is both writable and executable. The two mapping calls refuse a mapping that would leave
  a page writable through one mapping and executable through another. The rule is part of the
  interface, where no loader can forget it.
- A test guards the numbers. A retired number stays reserved, a test pins every number, and
  a changed number fails the build until the version moves. The review found no comparable gate in
  any of the other systems' crates.
- A dead thread stays visible. A corpse persists until its supervisor collects it, and a survey
  call lists it, so a tool that lists threads needs no cooperation from the parent.
- A reply is one-shot and stays with its holder. This matches KeyKOS and EROS, and the kernel
  guarantees it. A server cannot reply twice, reply to the wrong caller or hoard the right to reply.

## What best in class would further need

Fixing every finding would make Moho sound. It would not yet make the case that Moho is among the
best. Four things would, and none of them is a ruling. Each is evidence.

### Measured message-passing speed, set beside seL4's published numbers

In a microkernel every service is a message away, so the cost of one call and reply bounds the whole
system. seL4 publishes that cost in processor cycles, with the build commands, for five boards. The
default configuration, as fetched:

| board | IPC call | IPC reply | notify |
|---|---:|---:|---:|
| RISC-V 64, SiFive U54 at 1.5 GHz | 720 | 758 | 1183 |
| Arm 64, Cortex-A57 at 1.9 GHz | 419 | 431 | 1057 |
| x86_64, Haswell i7-4770 at 3.4 GHz | 789 | 653 | 1499 |

The figures are mean cycles. "IPC call" is "Time in cycles for invoking a server in a different
address space on the same core."

Moho has no published figure, and the review ran nothing. The claim in the crate that three words in
registers "is the whole of the fastpath" is a design statement until somebody measures it the same
way: the same definition, a comparable board, the build recorded. A number within a small factor of
seL4's would be a strong result. A number far from it, found before the publish, could still reopen
a layout decision such as the one ruled under property 1, which gives up a data register.

### The generated definition actually built

Finding 13 accepted the table. Best in class means the kernel's decoder, the program-side wrappers
and the documentation are all produced from it in the normal build, so that the three cannot
disagree. A table that only the documentation reads does not reach that bar.

### A written stability promise

Fuchsia's RFC-0002 is the model: a short document that says what a program built today may rely on,
and for how long. It says which marks mean "not yet stable", how a release announces an addition and
how it retires a removal. Moho has the mechanism for half of this (the pinned numbers and the
version constant) and no statement of the promise itself.

### An outside author writes a real program from the documentation alone

This is the test that the other three cannot replace. Somebody who has never seen the kernel source
writes a program that does real work, using only the published crate and its documentation, and
keeps a list of every question the documentation did not answer. Finding 14 predicts the first
entries: the trap instruction, the registers a trap clobbers, and what a new program finds at start.
Running it on Moho before the first stable release is the cheapest way to learn what the eight
properties missed.

## Sources

- seL4: [errors.h](https://github.com/seL4/seL4/blob/78b0c34efe12ddfe6e7dd616e8538ce49ebf2890/libsel4/include/sel4/errors.h),
  [object-api.xml](https://github.com/seL4/seL4/blob/78b0c34efe12ddfe6e7dd616e8538ce49ebf2890/libsel4/include/interfaces/object-api.xml)
  and the manual's source chapters ([manual/parts](https://github.com/seL4/seL4/tree/78b0c34efe12ddfe6e7dd616e8538ce49ebf2890/manual/parts):
  ipc, cspace, threads, api, objects) at the commit the review pins, version 17.0.0-dev. Also the
  [performance page](https://sel4.systems/performance.html) and the
  [verification page](https://sel4.systems/Verification/). The review could not read the manual's
  PDF as text, so the chapter sources stand in for it and section numbers are absent.
- Zircon: the [system interface rubric](https://fuchsia.dev/fuchsia-src/development/api/system),
  [errors](https://fuchsia.dev/fuchsia-src/concepts/kernel/errors),
  [vDSO](https://fuchsia.dev/fuchsia-src/concepts/kernel/vdso),
  [RFC-0002](https://fuchsia.dev/fuchsia-src/contribute/governance/rfcs/0002_platform_versioning),
  the [system call reference](https://fuchsia.dev/fuchsia-src/reference/syscalls) (the fetching tool
  made the count of 186),
  [zx_futex_wait](https://fuchsia.dev/fuchsia-src/reference/syscalls/futex_wait) and
  [zx_vmo_create](https://fuchsia.dev/fuchsia-src/reference/syscalls/vmo_create).
- WASI and the component model: [WIT.md](https://github.com/WebAssembly/component-model/blob/585526aa1f2c7f76f07557d16e265dede38b3acb/design/mvp/WIT.md)
  and [Text.md](https://github.com/WebAssembly/component-model/blob/585526aa1f2c7f76f07557d16e265dede38b3acb/design/mvp/Text.md)
  at the review's commit, and the filesystem interface's
  [types.wit](https://github.com/WebAssembly/wasi-filesystem/blob/v0.2.0/wit/types.wit) at v0.2.0.
- Linux: the [openat2(2)](https://man7.org/linux/man-pages/man2/openat2.2.html) manual page.
- KeyKOS: the [principles of operation, chapter 3](http://cap-lore.com/Agorics/Library/KeyKos/Principles/chapter3.html).
  EROS: the [1999 paper](http://flint.cs.yale.edu/cs428/doc/eros.pdf). Coyotos:
  [Cap.idl](https://gitlab.com/william-ml-leslie/coyotos/-/blob/fcaf11835e75567a6151102543f241a51b5b15e3/src/sys/idl/Cap.idl)
  from a third party's mirror. Hubris: the [reference](https://hubris.oxide.computer/reference/)
  and [sys/abi](https://github.com/oxidecomputer/hubris/blob/969bac2bf47c98710842eb232fdd4a9c54e7dd7f/sys/abi/src/lib.rs).

The seL4 badge remark, the paging-structure capabilities, WASI's handle reuse and every statement
about Moho's kernel come from the review and were not fetched again.