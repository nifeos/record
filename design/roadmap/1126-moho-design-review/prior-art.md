# Prior art

An appendix to [the milestone](../1126-moho-design-review.md).

Three research agents fetched each source on 2026-11-25 (UTC). A claim marked "from memory" or
"inferred" had no fetched page behind it. The seL4 manual is version 17.0.0. The Genode book is
edition 26.05. The WASI files are the `v0.2.0` tags.

## The sources

- seL4: the [reference manual](https://sel4.systems/Info/Docs/seL4-manual-latest.pdf) and
  [the source](https://github.com/seL4/seL4/tree/78b0c34efe12ddfe6e7dd616e8538ce49ebf2890/libsel4).
- Zircon: the [kernel concepts](https://fuchsia.dev/fuchsia-src/concepts/kernel/handles), the
  [system call reference](https://fuchsia.dev/fuchsia-src/reference/syscalls), the
  [interface rubric](https://fuchsia.dev/fuchsia-src/development/api/system) and
  [RFC-0002](https://fuchsia.dev/fuchsia-src/contribute/governance/rfcs/0002_platform_versioning).
- Genode: the [Foundations book](https://genode.org/documentation/genode-foundations/26.05/) and
  [the base headers](https://github.com/genodelabs/genode/tree/0f275e7afaab44e9a45cecd0eac0b88691278477/repos/base/include).
- Capsicum: FreeBSD's [rights(4)](https://man.freebsd.org/cgi/man.cgi?query=rights&sektion=4),
  [cap_enter(2)](https://man.freebsd.org/cgi/man.cgi?query=cap_enter&sektion=2),
  [cap_rights_limit(2)](https://man.freebsd.org/cgi/man.cgi?query=cap_rights_limit&sektion=2) and
  the [2010 paper](https://www.usenix.org/legacy/event/sec10/tech/full_papers/Watson.pdf).
- CloudABI: [cloudabi.txt](https://github.com/NuxiNL/cloudabi/blob/b3609d5686bbc04655e57fc3913fd2f14a77d41a/cloudabi.txt)
  and its [overview](https://github.com/NuxiNL/cloudabi/blob/b3609d5686bbc04655e57fc3913fd2f14a77d41a/docs/cloudabi.md).
- WASI 0.2 and the component model: the
  [explainer](https://github.com/WebAssembly/component-model/blob/585526aa1f2c7f76f07557d16e265dede38b3acb/design/mvp/Explainer.md),
  [WIT.md](https://github.com/WebAssembly/component-model/blob/585526aa1f2c7f76f07557d16e265dede38b3acb/design/mvp/WIT.md),
  [the canonical ABI](https://github.com/WebAssembly/component-model/blob/585526aa1f2c7f76f07557d16e265dede38b3acb/design/mvp/CanonicalABI.md),
  [poll.wit](https://github.com/WebAssembly/wasi-io/blob/v0.2.0/wit/poll.wit) and the filesystem's
  [types.wit](https://github.com/WebAssembly/wasi-filesystem/blob/v0.2.0/wit/types.wit).
- KeyKOS: the [principles of operation](http://cap-lore.com/Agorics/Library/KeyKos/Principles/chapter2b.html),
  the [nanokernel paper](http://cap-lore.com/CapTheory/upenn/NanoKernel/NanoKernel.html) and the
  [1985 architecture paper](http://cap-lore.com/CapTheory/upenn/OSRpaper.html).
- EROS: the [1999 paper](http://flint.cs.yale.edu/cs428/doc/eros.pdf), Shapiro's
  [2003 paper on synchronous IPC](http://web.archive.org/web/20160408020822id_/http://www.eros-os.org/papers/IPC-Assurance.ps)
  and [the CapROS source](https://github.com/capros-os/capros/tree/39a3b3e9bbd6723042e47f95193ec964346a385c/src/sys/eros).
- Coyotos: the [microkernel specification](http://web.archive.org/web/20160904092954/http://www.coyotos.org/docs/ukernel/spec.html),
  an archived copy, and a [mirror of the source](https://gitlab.com/william-ml-leslie/coyotos/-/tree/fcaf11835e75567a6151102543f241a51b5b15e3/src/sys).
- Hubris: the [reference](https://hubris.oxide.computer/reference/) and
  [sys/abi](https://github.com/oxidecomputer/hubris/blob/969bac2bf47c98710842eb232fdd4a9c54e7dd7f/sys/abi/src/lib.rs).

## Handles, rights and revocation

| system | a handle is | rights | narrowing | revocation |
|---|---|---|---|---|
| Moho | a slot index in a 64-slot table | 5 bits, one set for all objects | only on the way to another table | a region's `DESTROY`, a frame's `REVOKE` |
| seL4 | an address in a tree of CNodes the program builds | 4 (Read, Write, Grant, GrantReply) | `CNode_Mint`; an excess is "silently downgraded" | `CNode_Revoke` deletes derived copies |
| Zircon | a 32-bit value, per process | 25 bits, defaults per object type | `zx_handle_duplicate`, `zx_handle_replace` | none (inferred) |
| Genode | an index in a local capability space | none: "no superficial notion of access rights" | none | destroying the object revokes every copy |
| Capsicum | a file descriptor | 81 names in two 64-bit words | `cap_rights_limit`, "never expanded" | none (inferred) |
| CloudABI | a file descriptor | 31 bits, base and inheriting sets | `fd_stat_put` | none |
| WASI 0.2 | an `i32` index, per component instance | flags on a descriptor | only by `open-at` | `resource.drop` by the owner |
| KeyKOS | a key in one of 16 slots | a data byte and key variants | an order code that removes rights | the bank rescinds; keys turn null |
| EROS | a capability with a version number | weak and read-only variants | diminished fetch | version mismatch; an indirection object |
| Coyotos | a 16-byte capability | 5 restriction bits on memory | restriction on copy | `rescind`; an invalid one acts as null |
| Hubris | a task id with a generation | none | none | a restart bumps the generation |

## Calls, waiting, errors and versions

| system | message | reply | waiting | errors | version |
|---|---|---|---|---|---|
| Moho | 3 words, or 1 word and a capability | one-shot Reply capability, 2 words | notification bound to a thread; address wait; no deadline | 15 negative codes in word 0 | one number, equal at spawn |
| seL4 | a tag, up to 120 words, 3 capabilities | reply capability or reply object | bound notification; no timed IPC | 10 codes in the tag, detail in the buffer | none; one XML builds both sides |
| Zircon | up to 65536 bytes and 64 handles | transaction id in the message | `wait_one`, `wait_many`, ports, futex, all with a deadline | negative `zx_status_t` only; results in out parameters | vDSO; a target ABI revision per component |
| Genode | 1 KiB and 4 capabilities, typed | synchronous return | signals with no payload | result types in the base framework | none on a session (inferred) |
| CloudABI | file descriptor reads and writes | none | `poll` over clocks, descriptors, locks | 77 `errno` values | none in the definition file |
| WASI 0.2 | typed function calls | typed results | `poll` over `pollable` resources | `result` with an enumeration per interface | semantic version on each interface |
| KeyKOS | a word, a string, 4 keys | resume key, one-shot | none in the kernel | return codes; `kt+2` for an unknown order | none |
| EROS | 4 words, a string, 4 capabilities | resume capability, at most once | none in the kernel | result code; truncation reported | none |
| Coyotos | up to 8 words, 4 capabilities, a string | one-shot entry capability | non-blocking send; closed wait | a 64-bit exception code per interface | CapIDL interfaces carry a version |
| Hubris | up to 256 bytes and leases | `REPLY`, never fails visibly | 32 notification bits; closed receive | a response code; misuse faults the caller | an image identifier |

## What the comparison settles

Three patterns recur in the systems that reached outside users. Zircon keeps the status apart
from a peer's data. seL4 shares one field between them but gives a receive no error return for a
peer to imitate, and Hubris documents the forgery. A request the object does not understand gets
one uniform refusal: `UnknownRequest`, `kt+2`, `UndefinedOperation`. And a single definition
file generates both sides. Moho answers `BadMethod` for an unknown method on the right object,
but it has no refusal for a method aimed at the wrong object, and it has neither of the other
two patterns yet.

Two things Moho took from the field hold up. A one-shot reply that cannot move matches KeyKOS,
EROS and seL4. Generational names in place of a derivation tree match EROS, where "if the version
numbers do not match, the capability is invalid".

## What no fetch confirmed

- seL4's single numbering of invocation labels across objects, its fault endpoint as a
  configuration argument, and its debug-only identify call are from memory.
- Zircon's `zx_object_get_info` and its unbounded handle table are from memory. Four Fuchsia
  pages returned 404, among them the exception object's page.
- Zircon's and Capsicum's lack of revocation, and Genode's lack of a session version, rest on
  absence alone.
- The EROS and Coyotos sites no longer answer. The Coyotos specification is an archived copy of
  2016, its source a third party's mirror, and the EROS object reference was not reachable.
- The Hubris reference marks its RISC-V registers "TBD".
- Each "none" in a table cell for CloudABI, KeyKOS and EROS rests on absence in the
  documents read.
