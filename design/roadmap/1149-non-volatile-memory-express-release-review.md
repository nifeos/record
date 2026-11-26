---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1058, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1149. `non_volatile_memory_express`: the release review's findings

*(The number and the slug are provisional.)*

The release review of `partsfoundry/non_volatile_memory_express` at commit `60b34280`, version
0.1.0-pre.4, under milestone 1129 (the combine review), whose
[block](1129-crate-interfaces-best-in-class.md) sets its form. The baseline is milestone 1058 (the
outside review's findings), [its block](1058-non-volatile-memory-express-outside-review.md) and the
cleared package
[`notes/crate-reviews/non-volatile-memory-express.md`](../../notes/crate-reviews/non-volatile-memory-express.md).
1058's open items stay its own: the first release still waits for its two board runs. The names
1058 ratified stand, and the recheck against the later naming rules reopens none.

Reuse: the prior-art table weighs each NVMe driver a caller could take.

## Finding status

- P0-1, the memory page size is a bare `u64` that three functions each check alone: Open.
- P0-2, `Command` and `Capabilities` expose their words as public fields: Open.
- P0-3, the ring and identifier types are `Copy`: Open.
- P0-4, queues, commands and namespaces are all bare integers: Open.
- P0-5, the crate refuses with `Option` and panics, and gives no reason: Waiting on the errors
  decision of milestone 1129.
- P0-6, the doorbell takes an exponent a caller can mistake for bytes: Waiting on the doorbells
  decision of milestone 1129.
- P1-1, the documentation speaks of one driver and its targets: Open.
- P1-2, no fallible function has an `# Errors` section, and two panics have no heading: Open.
- P1-3, no `#[must_use]`, no `Hash` and no `From`: Open.
- P1-4, no attribute states that the crate has no `unsafe`: Open.
- P1-5, the builders and decoders a caller starts from carry no example: Open.
- P2-1, the command set stops at six commands and has no general builder: Open.
- P2-2, no little-endian byte form of a command, a completion or a list: Open.
- P2-3, `Completion` keeps dword 0 and drops dword 1: Open.
- P2-4, nothing ties `is_owned` to `pop`: Open.
- P2-5, a ring holds at most 65,535 entries: Open.
- P2-6, the test double is an example to copy: Waiting on the simulators decision of milestone
  1129.
- P2-7, the manifest has no `documentation` key, and the README names a file the package omits:
  Open.

## Open decisions

The one-way doors D1 to D7 below.

## Goal

A stranger writing an NVMe driver with no operating system picks this crate for the queue logic
and keeps it. No call compiles with two identifiers swapped or with a page size
the controller never got, and every refusal says why.

## What the review read and ran

See [the appendix](1149-non-volatile-memory-express-release-review/what-was-checked.md) and
[the guidelines table](1149-non-volatile-memory-express-release-review/api-guidelines.md).

## Prior art

Measured from the crates.io API on 2026-11-26 (UTC). A stranger brings this crate the problem of
driving an NVMe controller with no operating system. No Rust crate for it draws 10,000 downloads in 90
days, so the review also reads Linux's driver.

| crate or system | role | version read | total | 90 days | reverse dependencies | version read released |
|---|---|---|---|---|---|---|
| `nvme-driver` | ranked 1: a `no_std` driver that owns its memory and interrupts | 0.8.2 | 5,448 | 931 | 1 | 2026-09-09 |
| `tunnr-nvme` | ranked 2: a polled user-space driver over VFIO | 0.1.1 | 38 | 38 | 1 | 2026-10-31 |
| `nvme` | ranked 3: every release is yanked, so nothing is left to read | 0.0.0 | 4,863 | 6 | 0 | none |
| `nvme-cli-sys` | neighbor: bindings to Linux's NVMe ioctl structures | 1.0.0 | 17,331 | 16,457 | 1 | 2026-07-13 |
| `libnvme` | neighbor: bindings to the Linux `libnvme` C library | 0.9.0 | 918 | 597 | 0 | 2026-06-01 |
| `tock-registers` | integration: typed register fields, which `nvme-driver` uses | 0.12.0 | 2,366,974 | 622,973 | 75 | 2026-11-04 |
| `dma-api` | integration: the DMA trait `nvme-driver` uses | 0.10.2 | 133,029 | 27,518 | 35 | 2026-09-09 |
| Linux `drivers/nvme/host` | outside Rust | v6.12 | | | | |

The crates.io crate named `vroom` is a Vim macro runner, not the unpublished NVMe driver of that
name; `tunnr-nvme` descends from that driver and stands in for it. The appendix lists the names
searched and not found.

### What `non_volatile_memory_express` does better

- Than `nvme-driver`: no dependency against six, and no `unsafe`, where `nvme-driver` parses an
  Identify answer through pointer casts (`src/command.rs`). It refuses a submission queue head
  the controller cannot have reached; `nvme-driver` never reads `sq_head`. It tests the phase
  before it reads the rest of an entry, where `CompleteQueue::complete` reads all 16 bytes first.
- Than `tunnr-nvme`: it builds a page list into the caller's slice, where `spec::prp_pages`
  returns a `Vec`. It refuses an impossible head, where `QueuePair::take` folds it into the ring
  with `%`. It compiles for a bare target; `tunnr-nvme` needs `std` and `libc`.
- Than both: it holds no address and touches no memory, so no soundness contract rests on it,
  and eighteen Kani harnesses cover its arithmetic.
- Than Linux v6.12: the same ring discipline with no block layer, allocator or lock, and a
  checked `SQHD`, which `nvme_handle_cqe` only traces.

## The items

Effort is S (half a day), M (a day or two) or L (longer). A P0 changes a public item that 0.1.0
would freeze, so it lands before that version or stays as it is.

### P0: the 0.1.0 interface

#### P0-1. The memory page size is a bare `u64` that three functions each check alone

Verified in source and by running.
`enabled_controller_configuration(page_size_bytes)` returns `None` outside 4 KiB to 128 MiB. The
two pointer builders panic below 512 bytes or off a power of two, and
`Namespace::transfer_command` takes the size again on every call. Nothing ties the size the
controller was given to the size the pointers use; a doc comment asks the caller to keep them
equal. A probe passed 16,384 to the pair builder for a transfer that straddles a 4 KiB boundary
and got a zero second entry. A controller configured for 4 KiB pages reads that as a second page
at address zero. A size of `1 << 63` reaches an overflowing multiply in
`physical_region_page_pair`, a debug-build panic no doc names. `nvme-driver` holds one
`page_size` and checks it once in `begin_enable`; `tunnr-nvme` fixes `PAGE`.
Change: a `PageSize` type (name provisional) with a fallible constructor for 4 KiB to 128 MiB.
The configuration builder takes it and returns a plain `u32`, the pointer builders take it and
lose their panics, and `Namespace` holds it beside the unit. Door: one-way (D1). Effort: M.

#### P0-2. `Command` and `Capabilities` expose their words as public fields

Verified in source (C-STRUCT-PRIVATE).
`Command(pub [u32; 16])` and `Capabilities(pub u64)` each have a public field. A caller can
write any dword of a built command, so the builders' checks bind nobody and the layout can never
change. `PhysicalRegionPagePair` keeps its two public
fields, which a caller needs to chain list pages by hand. Milestone 1146 (the release review of
`extensible_host_controller_interface`) raises the same finding for its transfer request block,
and `nvme-driver` keeps `CommandSet` private.
Change: private fields; `Command::as_dwords(&self) -> &[u32; 16]`, `Capabilities::new(u64)` and
`Capabilities::raw()`. Door: one-way (D2). Effort: S.

#### P0-3. The ring and identifier types are `Copy`

Verified in source and by running.
`SubmissionQueue`, `CompletionQueue` and `CommandIdentifierSet` derive `Copy`. Each is a cursor
over state shared with a device, and a copy is a second cursor the controller knows nothing of.
`let mut copy = queue; copy.push();` compiles and leaves the original's tail unmoved, so its next
`push` hands out the same slot. A `CommandIdentifierSet<1024>` copies 8,192 bytes.
Change: drop `Copy` from the three types and keep `Clone`, `PartialEq` and `Eq`. Door: one-way
(D3), since removing the derive later breaks callers and adding it breaks none. Effort: S.

#### P0-4. Queues, commands and namespaces are all bare integers

Verified in source.
`Command::create_io_submission_queue` takes four `u16` values in a row (a command identifier, a
queue identifier, a depth, a second queue identifier), and `Command::read` takes four integers.
The compiler accepts a queue identifier where a depth belongs. Queue identifier 0 names the admin
pair, and the two queue builders accept it though their documentation tells the caller not to
pass it. No comparator does better.
Change: a newtype for the queue identifier, whose I/O constructor refuses 0, and one for the
command identifier, which `CommandIdentifierSet::acquire` returns and `release` takes. The
namespace identifier and the counts stay integers. Door: one-way (D4). Effort: M.

#### P0-5. The crate refuses with `Option` and panics, and gives no reason

Verified in source.
Twelve public functions return `Option`, nine panic on a caller's value, and two return a
`Result`. The split follows no rule a caller can learn: the configuration builder returns `None`
for a bad page size, and the pointer builders panic on one. `Namespace::transfer_command` returns
`None` for three causes the caller cannot tell apart. `parse_identify_namespace` returns `None`
for a short buffer and for an unsupported block size alike. A second public function,
`logical_block_size_shift`, exists only to recover the value the first refused, as an
`Option<u8>` where the field of that name is a `u32`. `nvme-driver`'s catch-all is
`Unknown(&'static str)` and `tunnr-nvme`'s variants hold a `String`, so neither sets the bar.
The crate's own `ImpossibleHeadError` does: a small type that carries the refused value.
Change: the convention the errors decision of milestone 1129 picks. This crate's evidence favors
a `Result` with a `#[non_exhaustive]` error per operation that carries what was refused, for the
Identify parses, the `Namespace` functions and the pointer builders. `logical_block_size_shift`
then goes. `push` and `acquire` keep `Option`, since a full ring has one cause. Door: one-way
(D5). Effort: M.

#### P0-6. The doorbell takes an exponent a caller can mistake for bytes

Verified in source and by running.
`doorbell(queue_id: u16, role: Doorbell, doorbell_stride_exponent: u32) -> u64` takes the raw
`CAP.DSTRD` field, and the README's example warns in a comment that it is not a byte count. The
function masks the exponent with `0xf` in silence, so 16 computes the offsets of 0.
`tunnr-nvme`'s `sq_doorbell(qid, stride)` takes bytes, the opposite convention. The result needs
its `u64`: queue 65,535 at the widest stride sits at `0x3_fffe_1000`.
Change: `Capabilities::doorbell(&self, queue_id, role) -> u64`, so the stride comes from the
register that defines it, in the shape the doorbells decision of milestone 1129 picks. Door:
one-way (D6). Effort: S.

### P1: before the first release

#### P1-1. The documentation speaks of one driver and its targets

Verified in source.
The doc comment of `Command` rests its byte order on two target instruction sets it does not
name. That of `logical_block_size_shift` explains itself by a server that never started.
`Capabilities`, `parse_identify_namespace` and `blocks_per_transfer` describe what one
particular driver does with 4096-byte blocks.
Change: rewrite those sentences for a caller who brings any driver, and state once that the dwords
are host values. Door: two-way. Effort: S.

#### P1-2. No fallible function has an `# Errors` section, and two panics have no heading

Verified in source (C-FAILURE).
`grep '# Errors' src` prints nothing; `record_head` and `release` describe their refusals in
prose, as the twelve `Option` functions do. `Command::read` and `write` panic on a count of zero
and say so in a parenthesis, where the seven other panicking functions have a `# Panics` section.
Change: the two headings where they belong. Door: two-way. Effort: S.

#### P1-3. No `#[must_use]`, no `Hash` and no `From`

Verified in source (C-COMMON-TRAITS, C-CONV-TRAITS).
`push` returns the slot the caller must write, `pop` the head it must ring, and `acquire` an
identifier that leaks if dropped; ignoring any of them compiles without a warning. The seven
value types derive no `Hash`, and `Capabilities` has no `From<u64>`.
Change: `#[must_use]` on the three methods and every builder, `Hash` on the value types, and the
conversion if P0-2 keeps an infallible constructor. Door: two-way (additions). Effort: S.

#### P1-4. No attribute states that the crate has no `unsafe`

Verified in source.
The README says so, and `src/lib.rs` does not enforce it.
Change: `#![forbid(unsafe_code)]`. Door: two-way. Effort: S.

#### P1-5. The builders and decoders a caller starts from carry no example

Verified in source and by building (C-EXAMPLE, C-QUESTION-MARK).
Thirteen doctests pass. `Capabilities`, the six `Command` builders, `Completion::from_dwords`
with its seven readers and `parse_identify_namespace` have none, and
`examples/software_controller.rs` ends five fallible calls with `expect`.
Change: an example on each of the four, one with a failing status, and `?` in the example's
loop. Door: two-way. Effort: S.

### P2: may follow

The seven P2 items are in
[the appendix](1149-non-volatile-memory-express-release-review/may-follow.md). Each is an
addition or a two-way fix. P2-1, a general command builder, lands with P0-2.

### Measured performance

 Measured on a Linux x86_64 host, release profile, against `tunnr-nvme` 0.1.1, whose
`spec` and `cmd` modules are public pure functions. A figure is the best of seven passes over the
repeat count, and a range spans three runs.

| operation | `non_volatile_memory_express` | `tunnr-nvme` 0.1.1 |
|---|---|---|
| pointers for 4 KiB that straddle a page | 2.7 to 2.8 ns | 24.1 to 25.6 ns |
| pointers and list for 128 KiB, 32 list entries | 17.4 to 17.9 ns | 195 to 208 ns |
| one Read command built | 5.1 to 5.6 ns | 4.9 ns |
| one whole command round | 24.3 to 26.0 ns | Not run |

The first two rows show the `Vec` that `spec::prp_pages` returns, where the crate writes into
the caller's slice. The third is a tie, and the fourth is the crate alone. `tunnr-nvme`'s `QueuePair` methods are private and `nvme-driver`
needs a mapped register block, so neither ran a round.

## One-way doors

- D1, the page size (P0-1). Recommended: one `PageSize` type, the stricter choice. A conversion
  from an integer can come later, and a bare `u64` cannot go back.
- D2, the public words (P0-2). Recommended: private fields with `as_dwords` and `raw`, the
  stricter choice; a mutable accessor can come later.
- D3, `Copy` on the cursors (P0-3). Recommended: drop it from the two rings and the identifier
  set, since adding it later breaks nobody.
- D4, identifier types (P0-4). Option A: newtypes for the queue and command identifiers, names
  provisional until ruled. Option B: keep the integers, as every comparator does. Recommended: A,
  the stricter choice; a `From<u16>` can loosen it later.
- D5, the refusals (P0-5). Recommended: `Result` with a small error per operation that carries
  the refused value, and `logical_block_size_shift` removed. The errors decision of milestone
  1129 decides it once for every crate.
- D6, the doorbell (P0-6). Recommended: a method on `Capabilities` returning a `u64`, and no
  trait. This crate rings one of up to 131,072 doorbells by number, which the two-method `Tails`
  trait of the ring drivers cannot name. The doorbells decision rules it with milestone 1146's
  `doorbell`.
- D7, the test double (P2-6). Recommended: keep it an example for 0.1.0, the stricter choice,
  since exporting it later is an addition.

## Evidence for the shared decisions

- **Errors.** The crate: two error structs with `Display`, `core::error::Error`,
  `#[non_exhaustive]` and the refused value; twelve `Option` functions and nine that panic
  (P0-5). `nvme-driver`'s `Error` (`src/err.rs`) wraps two dependencies' errors and ends in
  `Unknown(&'static str)`, which 21 call sites use. `tunnr-nvme`'s (`src/lib.rs`) carries a
  `String` in five variants. Points toward a small error per operation that carries the refused
  input.
- **DMA regions.** The crate declares no region trait. It takes bus addresses as `u64` arguments,
  writes a page list into a `&mut [u64]` the caller maps, and never touches device memory.
  `nvme-driver` owns `dma-api` `CoherentArray` rings; `tunnr-nvme` declares `Mapper`
  (`src/memory.rs`) and owns `DmaBuf`. Points toward leaving a pure-logic crate out of the shared
  trait.
- **Doorbells and tails.** The crate: an offset function and the values `tail` and `pop` return;
  no trait and no barrier. `nvme-driver` computes the pointer inside `write_sq_y_tail_doolbell`
  and batches after `wmb`; `tunnr-nvme` has two offset functions; Linux writes
  `dbs[qid * 2 * db_stride]`. Points toward an offset function for crates with many queues, with
  a `u64` or `usize` result (P0-6).
- **Register access.** The crate: seven `u64` offset constants and four status bits, no trait.
  Three of its registers are 64 bits wide. `nvme-driver` uses `tock-registers`'
  `register_structs!` (`src/registers.rs`); `tunnr-nvme` declares `Bar` with 32-bit and 64-bit
  reads and writes at a `usize` offset (`src/bar.rs`); Linux uses `readl` and `lo_hi_readq`.
  Points toward a shared trait with 64-bit accessors, and an offset wider than `u32` here.
- **Byte sinks and sources.** Not applicable: the crate moves no byte stream.
- **Feature names.** The crate declares none; the one candidate is an exported test double
  (P2-6). `tunnr-nvme` names its own `fake`. Points toward a feature named for what it exports.
- **Simulators.** An example that `cargo test` runs and callers copy. `tunnr-nvme` exports
  `FakeNvme` and `FakeMapper` under `fake` (`src/fake.rs`); `nvme-driver` keeps a `pub(crate)`
  test constructor. Points toward an example for a pure-logic crate, and an exported double for
  a crate with traits to implement (D7).
- **Contract layout.** Not applicable: the layouts are the specification's.

## Follow-on

- **Outstanding.** The shared decisions of milestone 1129 take D5 for errors, D6 for doorbells
  and D7 for simulators.

## Done when

The `non_volatile_memory_express` review is done once its P0 and P1 items read Done or Will not
fix, D1 to D7 have rulings, and `script/review-status` lists BUILT.

## BUGS

- The benchmark compares pure functions only; no comparator ran a whole round, and no device ran.
- `nvme`, ranked third, has every release yanked, so the review read none of it.
- The Linux reading covers three files at v6.12. The review read neither SPDK nor the Redox
  driver.
- The review counts twelve `Option` functions by reading. The census column E5 counts nine,
  since its pattern matches one-line signatures only.

## Index row

The release review of `non_volatile_memory_express` against two Rust drivers and Linux. Six
one-way interface changes come before 0.1.0, among them one page-size type and rings that are not
`Copy`, and five smaller fixes before the release. Its page-list builder runs eleven times faster
than the comparator's, which allocates. Seven doors wait.
