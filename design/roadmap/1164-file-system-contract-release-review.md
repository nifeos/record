---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1090, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1164. `file_system_contract`: the release review's findings

*(The number and the slug are provisional.)*

The release review of `partsfoundry/file_system_contract` at commit `05515061`, version 0.1.0
with no tag, under milestone 1129 (the combine review), whose
[block](1129-crate-interfaces-best-in-class.md) sets its form. The baseline is milestone 1090
(what an outside maintainer would fix before it leaves),
[its block](1090-filesystem-contract-outside-review.md) and the cleared package
[`notes/crate-reviews/filesystem-contract.md`](../../notes/crate-reviews/filesystem-contract.md).
Every 1090 finding reads Done except items 9, 16 and 21, which wait. The opcode numbers, the
identity values (14 and 15, each at version 1), the limits, the error-code choices, `NARROW`,
`PARENT_RIGHTS` and the reply error range stay closed. The package left the names for a release
ratification, and door D8 brings them.

The repository's second crate, `file_system_fixture`, is test data that never publishes.
Milestone 1129 leaves it out, and the lane read its manifest and README alone.

Reuse: the crate's own tests, and two scratch crates.

## Finding status

- P0-1, an operation, a handle, a rights mask and a badge are each a `u64`: Open.
- P0-2, a packer turns an operation past 255 into another verb: Open.
- P0-3, the decoders refuse one field, and the rest of each word has no rule: Open.
- P0-4, the verb table is an array of 23 open structs: Open.
- P0-5, an error is a bare `i32` declared in four modules: Open.
- P0-6, the version text describes a check no verb carries: Open.
- P0-7, the identity constants, the three `request` functions and the decoders: Waiting on the contract-layout decision of milestone 1129.
- P0-8, one system's start conventions sit under no identity: Open.
- P0-9, the encoders disagree on argument order, and records travel as tuples: Open.
- P0-10, the names wait for their release ratification: Open.
- P1-1, a walk ends at damage without saying so, and an edit then drops what follows: Open.
- P1-2, six examples for 66 public functions, and no `# Errors` section: Open.
- P1-3, the documentation names one engine and one system's programs: Open.
- P1-4, the README counts fifteen harnesses and then eleven: Open.
- P1-5, the types miss common traits, and a rights set prints as a number: Open.
- P1-6, `explain` gives the block server's refusal the attribute sentence: Open.
- P2-1, a path of several components costs one call for each: Open.
- P2-2, `unpack_name` clamps a length in a crate that never truncates: Open.
- P2-3, two sibling records order their header bytes differently: Open.
- P2-4, the `documentation` key points at the repository, and `homepage` repeats it: Open.
- P2-5, the stranger run has no date, and the changelog promises dates it does not carry: Open.
- P2-6, the longest granted name is one engine's limit: Open.

## Open decisions

The one-way doors D1 to D8 below.

## Goal

A stranger writes a server or a client from this crate alone. The compiler
refuses a block opcode where a file verb belongs. A server refuses every bit it does not
understand. A release that adds a verb does not break a caller that compiled against the last
one.

## What the review read and ran

[The appendix](1164-file-system-contract-release-review/what-was-checked.md) lists what the lane
read in the crate, six crates and two systems, with each command's result.
[The guidelines table](1164-file-system-contract-release-review/api-guidelines.md) marks the 54
API Guidelines items.

## Prior art

Measured from the crates.io API on 2026-11-26 at 23:18 (UTC). A stranger brings this crate one
problem: the messages of a file service, defined once for the server and its clients. Three
crates that publish such a protocol rank by downloads, and `p9`, the nearest in shape, stands
unranked.

| crate or system | role | version read | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `russh-sftp` | ranked 1: the SFTP messages, client and server | 4.0.0 | 5,373,651 | 2,586,407 | 95 | 2026-11-21 |
| `fuser` | ranked 2: the FUSE messages, server side | 0.19.0 | 7,061,836 | 2,222,734 | 160 | 2026-11-20 |
| `fuse-backend-rs` | ranked 3: the FUSE messages, for virtiofs too | 0.14.0 | 2,258,759 | 1,538,329 | 8 | 2026-02-26 |
| `p9` | comparator: 9P2000.L, handles and walks | 0.3.2 | 288,768 | 61,504 | 0 | 2024-11-26 |
| `cap-std` | neighbor: directories as capabilities, over a host | 4.0.3 | 37,324,536 | 19,185,273 | 370 | 2026-08-20 |
| `virtio-drivers` | neighbor: the block side | 0.13.0 | 445,812 | 101,928 | 91 | 2026-03-03 |
| 9front `sys/man/5/version`, `sys/man/5/walk` | outside Rust | commit `d7e009b7` | | | | |
| Fuchsia `sdk/fidl/fuchsia.io/rights-abilities.fidl`, `directory.fidl` | outside Rust | commit `8ff2539f` | | | | |

### What `file_system_contract` does better

- Than all four protocol crates: it needs neither `std` nor an allocator nor a dependency. Each
  of the four needs `std`.
- Than `russh-sftp` and `p9`: `directory_entry::iter` borrows each name from the reply.
  `russh-sftp` builds two `String`s for each file, and `p9` a `CString`.
- Than FUSE and SFTP: authority is in the protocol. A handle carries rights, and three Kani
  harnesses prove that no descent widens them. FUSE and SFTP leave access to the server.
- Than `fuchsia.io`: attenuation is one proven function. Each Fuchsia server must remove an
  inherit flag itself.
- Than `fuser` and `p9`: the wire items are public. Both keep theirs private, so a stranger
  cannot build a client from either.
- Than all of them: fifteen Kani harnesses with falsification patches, five fuzz targets, and
  limits that each refuse with their own error.

## The items

Effort is S (half a day), M (a day or two) or L (longer). A one-way item binds every caller from
the first 0.1.0 tag.

### P0: the 0.1.0 interface

#### P0-1. An operation, a handle, a rights mask and a badge are each a `u64`

Verified by building. `block::READ` is 1, `file_system::READ` is 2, `directory::rights::READ` is
2 and `grant::rights::READ` is 1. `file_system::request(block::READ, 0, 4)` compiles and
builds an `OPEN`. `Rights::root(grant::rights::WRITE)` compiles and allows
`directory::rights::READ`. `file_system::request(file_system::READ, 1024, 3)`, with the handle
and the length swapped, compiles. `fuser` wraps each: `INodeNo(pub u64)`, `FileHandle(pub u64)`
and a `bitflags` type for each flag word. `russh-sftp` has `SftpHandle` and `OpenFlags`, and
`fuchsia.io` declares `Operations` as `flexible bits`.
Change: an operation type for each protocol, a `Handle`, and a rights-mask type for each of the
two ladders (names provisional), each a `#[repr(transparent)]` newtype that keeps an unknown
value. `Rights::root`, `attenuate` and `allows` take the mask type.
Door: one-way (D1); it moves ratified names from modules to types. Effort: L, with the callers.

#### P0-2. A packer turns an operation past 255 into another verb

Verified by building. `file_system::request(257, 3, 10)` builds an `OPEN`, and
`block::request(0x102, 1)` builds a `WRITE`. The `request` functions assert the handle, the
length and the block count, as item 7 of milestone 1090 ruled, and not the operation. The
harness `a_file_request_round_trips` assumes an operation of at most 255.
Change: the three packers refuse an operation past 255 as they refuse the other fields. The type
of P0-1 then makes the case unwritable.
Door: one-way (D2). Effort: S.

#### P0-3. The decoders refuse one field, and the rest of each word has no rule

Verified by building. `block::request_block_count` refuses a count past 16. Nothing else
refuses. A block request with bits 19 to 8 set decodes as before, and so does a rename
destination with its top byte set. A directory record with flags `0xfe` reads as a file.
`request_length_bytes` returns up to 1,099,511,627,775 against a channel of 65,536, which the
text leaves to a server to clamp. Twelve of the 23 verbs carry nothing in their second word,
and no text says a server refuses a value there. A bit ignored at 0.1.0 can never gain a
meaning. `terminal_contract` refuses its reserved bits through one `decode`, and `fuser`
refuses a short request with `RequestError::ShortRead`.
Change: every undefined bit and unused word is zero, and a server answers `EINVAL` to one that
is not. Each protocol gains one `decode` that returns the typed request or the refusal.
Door: one-way (D3). Effort: M.

#### P0-4. The verb table is an array of 23 open structs

Verified by building. `verb::TABLE` has the type `[Verb; 23]`, `file_grant::POLICY` the type
`[Policy; 23]`, and `verb::LAST` is 23. A caller that names the type breaks at the next verb,
while `VERSION` says a new verb is no break. `Verb` has seven public fields and a caller can
build one, so an eighth field breaks that caller. `Operand` and `Policy` are exhaustive, so a
fifth operand shape breaks every `match`. `fuser` keeps its opcode enum private, and the
`Opcode` of `fuse-backend-rs` maps an unknown number to its member `MaxOpcode`.
Change: the two tables become private behind `verb::of`, `file_grant::of` and an iterator.
The three types gain `#[non_exhaustive]`, and the fields of `Verb` become methods.
Door: one-way (D4). Effort: M.

#### P0-5. An error is a bare `i32` declared in four modules

Verified in source. `store::set` and `store::remove` return `Result<usize, i32>`, `error::code`
returns `Option<i32>`, and `Policy::Refused` holds an `i32`. `EROFS` and `ENOTDIR` are each
declared in `directory` and in `grant`, `EBADF` in `verb::file_grant`, and `explain` matches the
literals 2, 9, 17 and 24. §326 (the names and numbers of the services' wire error codes)
replaces these numbers, and item 16 of milestone 1090 waits on it. `fuser` has
`Errno(NonZeroI32)` with a constant for each code. `russh-sftp` has the enum `StatusCode`, with
`Display`.
Change: §329 (one error convention for the library crates) rules it. By rule 1 the `i32` and
each `None` with several causes become a `Result` over an error type of the crate, shaped by
rules 2, 4, 5, 9 and 10. The codes of §326 are declared once.
Door: one-way. Effort: M.

#### P0-6. The version text describes a check no verb carries

Verified in source. The text of both `VERSION` constants says a client asks for the served
versions and binds when its own is among them. Neither protocol has a verb that answers a
version. `CLIENT_WINDOWS` says a larger value is a new version, and `TRANSFER_PAGES` calls
itself a tuning number, though both ends must agree on it. 9P opens with `Tversion`, which
fixes the version string and the largest message. FUSE and SFTP open with an exchange too
(`InitIn`, `Init`).
Change: a stability section with the rule of door D5, and a version text that describes the
check where it happens.
Door: one-way (D5). Effort: S.

#### P0-7. The identity constants, the three `request` functions and the decoders

Verified in source; the evidence below points to the list. The values stay frozen.
Change: the types and spellings the contract-layout decision picks.
Door: one-way. Effort: M.

#### P0-8. One system's start conventions sit under no identity

Verified in source. Interface 14 names the block protocol and interface 15 the file protocol.
`grant`, `nameset`, `verb::file_grant`, `READY` and `DESCENT_REFUSED` belong to neither. They
pack a name into the argument words a process starts with, lay out a grant page, and fix that
page at the virtual address `0x70_0000`. No version covers them. The prior-art appendix of
milestone 1090 names the cost, and its item 12 moved `rm`'s report out for the same reason.
The protocol modules the lane read in the four crates carry no start convention.
Change: by door D6, the five leave for the crate that holds the grant conventions, or they
stay under an identity and a version of their own.
Door: one-way (D6). Effort: M.

#### P0-9. The encoders disagree on argument order, and records travel as tuples

Verified in source. `directory_entry::encode`, `volume_statistics::encode` and `list::encode`
take the output buffer first. `nameset::encode`, `store::set`, `store::list` and
`grant::write_page` take it last. `volume_statistics::decode` returns `Option<(u64, u64, u64)>`.
A caller can swap the three, and a longer record, the module's next version, has no place for
a fourth. The four iterators yield `(&[u8], bool)`, `&[u8]` and `(&[u8], u32, &[u8])`, and
`nameset::iter` returns `core::iter::Take<Names>`, which puts an adapter in the signature.
`p9` and `russh-sftp` give each record a struct with named fields (`Dirent`, `File`).
Change: one order, the output buffer last. `VolumeStatistics`, an entry and an attribute
record (names provisional) become `#[non_exhaustive]` structs, and `nameset::iter` returns a
type of the crate's own.
Door: one-way (D7). Effort: M.

#### P0-10. The names wait for their release ratification

Verified in the manifest and the cleared package. The manifest holds `publish = false` until a
review of the names, and the package asks the architect to ratify four tables. Against
[design/naming.md](../naming.md), ten public functions take a parameter named `w0`, `w1` or
`r0`, and `Verb` has the field `carries_w1`; each needs a decoder. The constant `ENOTSUP`
opens its text with `EOPNOTSUPP`.
Change: the ruling of door D8, built after P0-1 and P0-5, which move or replace many of the
names.
Door: one-way at the first tag (D8). Effort: S in the crate, M at the callers.

### P1 and P2: before the first release, and after

[The later-items appendix](1164-file-system-contract-release-review/later-items.md) holds the
six P1 findings and the six P2 findings in full.

### Measured performance

The numbers come from the benchmark of
[the appendix](1164-file-system-contract-release-review/what-was-checked.md#the-benchmark), on
one thread. The input is one listing of 100 names of 12 bytes.

| operation | `file_system_contract` | `russh-sftp` 4.0.0 |
|---|---|---|
| read the listing | 204 ns | 13,904 ns |
| write the listing | 918 ns | 9,580 ns |
| bytes on the wire | 1,400 | 2,413 |

The `russh-sftp` column includes a `Vec`, two `String`s for each file and an empty attribute
record, which its `Name` message requires. The lane ran no comparison with `fuser` or `p9`,
which keep their wire types private. No finding follows; P2-1 is the one place the interface
costs calls.

## One-way doors

- D1, typed words (P0-1). The baseline kept `u64` constants in modules. Recommended: newtypes
  that keep an unknown value. A `From<u64>` can follow; a `u64` parameter cannot narrow.
- D2, an operation past a byte (P0-2). Recommended: the packers refuse it, as they refuse a
  handle or a length, the stricter choice.
- D3, undefined bits and unused words (P0-3). Recommended: zero on the wire and refused by a
  server, the stricter choice. The file protocol refuses a length past the channel as the block
  protocol refuses a count.
- D4, the verb table (P0-4). Recommended: private tables behind functions, and
  `#[non_exhaustive]` on the three types.
- D5, what changes `VERSION` (P0-6). Recommended: a changed limit a peer relies on
  (`TRANSFER_PAGES`, `CLIENT_WINDOWS`, a record's bytes) is a new `VERSION`, and a new verb,
  right or code a minor release. The text names the pair in each program's note as the check.
- D6, what the crate holds (P0-8). Recommended: the five items leave for the crate that holds
  the grant conventions, the stricter choice. A module can join later, and a published one
  cannot leave.
- D7, argument order and record shapes (P0-9). Recommended: the output buffer last, and three
  `#[non_exhaustive]` structs.
- D8, the names (P0-10). Recommended: ratify the package's four tables as built, with three
  changes. The parameters become `first_word`, `second_word` and `reply_word`, and `carries_w1`
  becomes `carries_second_word`. The opcode and error names follow P0-1 and §326.

## Evidence for the shared decisions

- Errors. §329 is decided, and P0-5 follows it. Rule 1 reaches the two functions that return
  `Result<usize, i32>` and the four encoders whose `None` has several causes. Rule 6 reaches
  the four walkers (P1-1). The code on the wire is a wire value, and the contract-layout
  decision shapes its type. `russh-sftp` has `StatusCode`, an enum on the wire, and `fuser`
  has `Errno`, a newtype with `From<std::io::ErrorKind>`.
- DMA regions, doorbells and tails, and register access do not touch this crate: not applicable.
- Byte sinks and sources. The crate declares no trait. Every encoder writes into a `&mut [u8]`
  and returns the bytes used or `None`. The evidence points to plain slices in a contract, and
  to any trait in the client library.
- Feature names. The crate declares none. `russh-sftp` has `async-trait`, named for the crate
  it turns on, and `raw-string`.
- Simulators. The crate ships none. Its repository keeps test data in a second crate that never
  publishes, a third shape beside a feature and a test module.
- Contract layout. Two interfaces share the crate, each a module with its own `VERSION` and
  `INTERFACE_ID`, and neither has a magic. The opcodes are bare constants with no `OPERATION_`
  prefix. Three functions are named `request`, and one of the twelve field readers refuses.
  [The appendix](1164-file-system-contract-release-review/what-was-checked.md#the-contract-layout-item-by-item)
  lists each item. The evidence asks the decision for four things. One is a layout for a crate
  with two interfaces, and one a single spelling for an opcode constant. The others are a
  decoder that refuses, and one home for the reply error convention every service contract
  restates.

## Follow-on

- **Outstanding.** The twenty-two findings, open on the crate's `main` at `0551506`, read
  2026-11-26 (UTC).
- **Outstanding.** The doors D1 to D8 have no ruling, and no decision file names them, read
  2026-11-26 (UTC).

## Done when

Each of the eight doors has the architect's ruling, and no P0 or P1 line above reads Open or
Waiting. `script/review-status` then counts the block BUILT.

## BUGS

- No crate publishes a file protocol with rights on its handles, so the ranked comparators
  publish protocols that leave access to the server.
- The review read no server and no client of this crate, 9P or `fuchsia.io`, and counted no
  callers; each effort at callers is an estimate.
- The lane ran neither Kani, the fuzz targets nor mutation testing.

## Index row

The release review of `file_system_contract` against `russh-sftp`, `fuser`, `fuse-backend-rs`,
`p9`, 9P and `fuchsia.io`. Ten findings touch the 0.1.0 interface. The largest are four kinds of
word as `u64`, decoders that refuse one field, a verb table whose type changes with each verb,
and start conventions under no identity. Six land before the release, six may follow, and eight
doors wait for the architect.
