# What makes a kernel ABI good

An appendix to [the milestone](../1126-moho-design-review.md).

Moho is the system call interface of the nife microkernel, defined by the crate `moho_abi`. The
review compared it with ten capability systems and listed nineteen findings. Eleven of them are
decisions nobody can undo once the crate publishes. This appendix explains the eight properties
those findings are about, with one real example each, so that each ruling has its background. Skim
the tables and code. The review fetched its outside facts and marks the few it took from memory
"(from memory)". The second part lists the sources.

## What an ABI is, and why it sets hard

An application binary interface (ABI) is the contract that compiled programs target. An API is a
contract in source code: change it, and the compiler tells you. An ABI is a contract in machine
state: which number in which register asks for which operation, which register holds each argument,
which register holds the answer, and what each error number means. Nothing checks it at build time,
because the two sides build separately.

For Moho the contract is small. A program puts a system call number in one register and up to six
words in six others, then traps into the kernel. There are five system calls. Four act on the caller
itself. The fifth, `invoke(capability, method, a0, a1, a2)`, acts on everything else: word 0 names a
slot in the caller's capability table, word 1 a method number, and the rest are arguments. A
capability is an unforgeable reference to a kernel object together with the rights its holder has on
it. On return, word 0 is the result or a negative error code.

Almost none of this can change once programs exist. A compiled program has the number 4 baked in
where it means `CALL`, and reads its answer from the register the crate named on the day of the
build. If the kernel later moves a number, a register or the meaning of an error, that program still
runs, and does the wrong thing with no message. The only clean cure is a new version that every
program must be rebuilt for. This is why the review calls these choices one-way doors, and why it
asks for rulings before the first publish, while the number of outside programs is zero.

Two kinds of change stay cheap after a publish. Adding something new (a method number nobody used,
an error code nobody received) breaks no existing program, provided the interface allows it.
Loosening a rule (accepting what the kernel refused before) breaks nobody either. Tightening does.
Several of the eight properties below exist only to keep those two cheap kinds of change available.

## Eight properties of a good kernel ABI

Each property has a plain statement, one example from a real system, and then where Moho stands and
which finding of the review addresses it. For findings 1 to 4 the paragraphs state the rule in
force. The others remain proposals.

### Property 1 (finding 1): the kernel's answer cannot be forged

A program must be able to tell what the kernel said from what another program said. If both arrive
in the same register with the same encoding, a hostile or buggy peer can speak in the kernel's
voice. It can claim to a server that its endpoint is gone, or to a client that the kernel refused
the call.

Zircon, the kernel of Fuchsia, keeps the two apart by rule. Every call returns only a status, and
every result goes through a pointer the caller supplies. Its interface rubric says: "Do not return
other values through `zx_status_t`, for example using the positive value range. Instead, use an out
parameter."

```c
zx_status_t zx_vmo_create(uint64_t size, uint32_t options, zx_handle_t* out);
/* status in the return register; the new handle through *out */
```

Hubris, a small kernel from Oxide, shares Moho's present shape and documents the cost. Its reference
says of the code that reports a dead peer: "It is possible to fake a dead task by deliberately
sending a response code in the dead code range".

Moho before the ruling: on a receive, word 0 is the sender's first data word. On a refusal, word 0
is the kernel's negative error. A sender who writes `-11` as its first word makes the receiver read
`Gone`, the code for a destroyed endpoint. The review's example is a log server that exits on
`Gone`: any client allowed to write can shut it down for everyone. The crate records this as a bug
on `RECEIVE`. A wait on a notification (a doorbell object that carries a word of signal bits) has
the same shape: the signal word comes back in word 0.

What finding 1 ruled (2026-11-25 UTC): word 0 is always the kernel's status, and every data word
moves down one register.

| return from a receive | word 0 | word 1 | word 2 | word 3 | word 4 |
|---|---|---|---|---|---|
| Today: a message arrives | sender | sender | sender | kernel (badge) | kernel (0, or a tag) |
| Today: the kernel refuses (`Gone`) | kernel (`-11`) | not written | not written | not written | not written |
| Today: a sender forges `Gone` | sender (`-11`) | sender | sender | kernel (badge) | kernel (0) |
| Ruled: any return | kernel (status) | sender (data 0) | sender (data 1) | sender (data 2) | kernel (badge, tag after it) |

The last row is one possible layout. Where the badge and the tag move is not yet fixed. The
registers behind the words: word 0 to word 4 are `a0` to `a4` on riscv64, `x0` to `x4` on aarch64,
and `rdi`, `rsi`, `rdx`, `r10`, `r8` on x86_64. The badge is a number the kernel attaches to a
sender's capability so a server can tell its clients apart. The "today" rows are from the crate's
own documentation and the review's reading of the kernel.

The alternative the review proposed kept every existing layout and made word 4, which only the
kernel writes, the place to look. It was not chosen. The ruled layout is safe even for a careless
wrapper, and costs one data register on every message.

### Property 2 (findings 2 and 10): one operation number has one meaning, and an unknown request gets one refusal

If a number means "send" on one object and "destroy" on another, then a call aimed at the wrong slot
does not fail. It succeeds at something else. A good interface makes a misdirected request land on a
single, recognizable refusal, whatever object received it.

Coyotos, the successor of EROS, declares that refusal on the base interface that every capability
inherits:

```
/// Exceptional result returned when the operation requested on a
/// capability is not recognized by the implementing interface.
exception UnknownRequest;
```

KeyKOS, the 1980s ancestor of this family, states the same rule in one sentence of its manual:
"Primary keys return kt+2 for invalid order codes." Hubris goes further and has a reason code,
`UndefinedOperation`, with which a server faults a client whose message "almost certainly indicates
that the client intended the message for a different kind of server".

Moho before the ruling: each module numbers its methods from 0, and the kernel picks the table by
the kind of object in the slot. Method 0 is `SEND` on a rendezvous (Moho's name for a synchronous
message endpoint), `MAP` on a memory region, `ARM` on a timer and `DESTROY` on a process. The
review's example: a supervisor that sends to slot 10 where it meant slot 9 destroys its child and
reads back 0, a success. An unknown method on the right object does get one answer, `BadMethod`. The
gap is the wrong object.

What finding 2 ruled (2026-11-25 UTC): method numbers are unique across the interface, with the
object kind in the high bits. A call on the wrong kind of object answers `WrongObject`. The names
stay and the values move.

What finding 10 adds, still a proposal: Moho has four message shapes and two kinds of receive, and a
mismatch between them is not refused either. A `CALL` that meets a plain `RECEIVE` delivers its
words and then tells the caller `Gone`, so the request ran and the caller believes it did not. seL4
has one message shape: a tag of four fields (a label, a length, a count of capabilities and a field
describing how they arrived), then the words. The review proposes one message and one receive, or at
least a refusal before the kernel delivers anything.

### Property 3 (finding 3): unused inputs must be zero, and are refused otherwise

This is the property that keeps additions cheap. If the kernel ignores a register or a flag bit
today, programs will pass garbage there, because nothing stops them. On the day the kernel gives
that register a meaning, those programs change behavior. A kernel that refuses anything it does not
define knows that every working program passes zero, so zero can keep meaning "the old behavior" for
ever.

Linux learned this in public. The `openat2` manual page states the difference: "Whereas openat(2)
ignores unknown bits in its flags argument, openat2() returns an error if unknown or conflicting
flags are specified in how.flags." Because `open` ignored unknown bits, nobody could add flags
safely: an old kernel accepts the new flag and silently does not honor it (from memory). `openat2`
takes a structure and its size, and applies the rule to fields that do not exist yet:

```c
struct open_how how = { 0 };              /* zero-fill everything */
how.flags   = O_RDONLY;
how.resolve = RESOLVE_BENEATH;
fd = syscall(SYS_openat2, dirfd, path, &how, sizeof(how));
/* a newer, larger struct on an older kernel:
   extra bytes all zero  -> accepted, old behavior
   any extra byte nonzero -> refused with E2BIG */
```

Zircon applies the rule call by call. `zx_vmo_create` answers `ZX_ERR_INVALID_ARGS` when "options
contains an unsupported combination of flags". seL4 is a counterexample in one place: when a copy
asks for more rights than the source has, "the destination rights are silently downgraded to those
of the source".

Moho before the ruling: the documentation marks unused arguments with `_` and the kernel never reads
them. One mapping call treats any nonzero value as "writable". The kernel truncates a rights word
and drops unknown bits. Only the address wait (Moho's futex-like call) refuses what it does not
define. The crate already holds a near miss: a selector was later placed in a word that callers
happened to pass as zero.

What finding 3 ruled (2026-11-25 UTC): an argument word, flag or rights bit that a method does not
define ends the calling program with a fault its supervisor can read. It is not an error return.
This is the cheapest of the four urgent findings and the one the others lean on. Deadlines,
destination slots and rights masks can all arrive later as additions because the words they will use
must be zero today. A later release can loosen the rule but can never tighten it.

### Property 4 (finding 4): errors are precise enough to act on

An error code is an instruction to the program: retry, free something, fix your argument, or give
up. Two causes deserve separate codes when the right reaction differs. They can share a code when no
program would act differently. The test is the reaction, and the count of codes matters less than
whether each one passes it.

seL4 has ten error codes and adds detail beside the code. A range error also returns the bounds, and
an invalid argument returns which argument:

```
seL4_InvalidArgument   seL4_InvalidCapability   seL4_IllegalOperation
seL4_RangeError        seL4_AlignmentError      seL4_FailedLookup
seL4_TruncatedMessage  seL4_DeleteFirst         seL4_RevokeFirst
seL4_NotEnoughMemory

seL4_RangeError:      IPCBuffer[0] = minimum allowed value
                      IPCBuffer[1] = maximum allowed value
seL4_InvalidArgument: IPCBuffer[0] = invalid argument number
```

`DeleteFirst` and `RevokeFirst` name the cure in the code itself. Zircon separates the two ways of
running out: `ZX_ERR_NO_MEMORY` is "The system was not able to allocate memory needed for the
operation" and `ZX_ERR_NO_RESOURCES` is the same sentence for "some resource". It also separates an
invalid argument from one that is "outside the valid range". WASI gives each interface its own error
list; the filesystem interface declares an `enum error-code` of its own.

Moho before the ruling: fifteen codes. Four belong to one method, the reboot call. The other eleven
carry about forty distinct refusals by the review's hand count, and five of them carry most.
`OutOfMemory` can mean that the caller spent its budget, that the caller's capability table has no
free slot, or that a system-wide table has none. The first needs a larger budget, the second needs
the program to delete a capability, and nothing the program does helps with the third.

What finding 4 ruled (2026-11-25 UTC): add `InvalidArgument`, `WrongState` and `TableFull` for the
caller's own table, and a separate code for a full system-wide table (the names are provisional).
Each refusal moves to the code a program can act on. The four reboot codes move into the second word
of the reboot call's own answer. On a refusal, the words after the status are zero. A new number is
an addition. Moving a refusal from one code to another after a publish changes what a code means,
which is a version change, so the move happens before the publish. An earlier decision declined to
split `OutOfMemory` until somebody needed it; the publish is that moment.

Properties 5 to 8, the comparison of the strongest systems, what Moho already does better and the
sources are in [the second part](abi-further-properties-and-evidence.md).