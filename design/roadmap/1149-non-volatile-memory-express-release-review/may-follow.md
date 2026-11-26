# P2: may follow

An appendix to [the milestone](../1149-non-volatile-memory-express-release-review.md).

## P2-1. The command set stops at six commands and has no general builder

Verified in source and in the comparators' source.
`Command` builds Identify, the two queue creations, Read, Write and Flush, and `Command::new` is
private. A driver that asks for its queue count (Set Features, Number of Queues), deletes a queue,
reads a log page, writes zeroes or sets Force Unit Access has no builder. Once P0-2 closes the
public field, it has no way to write the dwords either. `tunnr-nvme`'s `cmd.rs` has
`set_num_queues`, `delete_io_submission_queue`, `write_zeroes` and `io_write_fua`; `nvme-driver`
has `Feature::NumberOfQueues`; Linux calls `nvme_set_queue_count` before it creates a queue.
Change: a public general builder that takes the opcode, the identifiers and the pointers and sets
dwords 10 to 15, and builders for Set Features (Number of Queues) and the two deletions. The
general builder lands with P0-2. Door: two-way (additions). Effort: M.

## P2-2. No little-endian byte form of a command, a completion or a list

Verified in source.
The wire format is little-endian. `Command` holds host `u32` values, `Completion::from_dwords`
takes them, and `physical_region_page_list` writes host `u64` values into the list, so a
big-endian host puts the wrong bytes on the bus, and the caller converts each word.
`tunnr-nvme` writes each list entry with `to_le_bytes` (`src/queues.rs`), and Linux declares every
field `__le16`, `__le32` or `__le64`. Milestone 1146 (`extensible_host_controller_interface`: the release review's findings) raises the same finding as its P2-5.
Change: `Command::to_le_bytes() -> [u8; 64]`, `Completion::from_le_bytes([u8; 16])`, and a
statement on the list builder of the byte order it writes. Door: two-way (additions). Effort: S.

## P2-3. `Completion` keeps dword 0 and drops dword 1

Verified in source.
`Completion::result` is dword 0, and `from_dwords` discards dword 1. Linux reads the two as one
64-bit `union nvme_result`, and `nvme-driver`'s `NvmeCompletion::result` is a `u64`. The struct
is `#[non_exhaustive]`, so a second field breaks nobody.
Change: a field for dword 1 when a command that returns one gains a builder. Door: two-way.
Effort: S.

## P2-4. Nothing ties `is_owned` to `pop`

Verified in source.
`CompletionQueue::pop` advances the head whether or not the entry at it belonged to the driver, so a caller
that pops on a stale entry loses its place in the phase. `nvme-driver`'s `take_complete` and
`tunnr-nvme`'s `take` test the phase and advance in one call.
Change: a method that takes the entry, returns the new head when the entry is owned and `None`
when it is not, beside the two it joins. Door: two-way (an addition). Effort: S.

## P2-5. A ring holds at most 65,535 entries

Verified in source.
`SubmissionQueue::new` and `CompletionQueue::new` take `entries: u16`, and
`Capabilities::maximum_queue_entries` returns up to 65,536 as a `u32`. The largest queue the
specification allows is one entry out of reach. Linux caps its depth at 4,095 (`NVME_PCI_MAX_QUEUE_SIZE`) and defaults to 1,024, so
no caller is likely to meet the bound.
Change: a sentence on both constructors. Door: two-way. Effort: S.

## P2-6. The test double is an example to copy

Verified in source.
`examples/software_controller.rs` models a controller over two `Vec`s, and the README tells the
caller to copy it. `tunnr-nvme` exports its `FakeNvme` under a `fake` feature, with power cuts and
injected failures, and `nvme-driver` keeps its test registers private.
Change: what the simulators decision of milestone 1129 (the combine review) picks. Door: two-way (an addition).
Effort: M.

## P2-7. The manifest has no `documentation` key, and the README names a file the package omits

Verified in `Cargo.toml` and by building (C-METADATA).
`cargo package --list` shows 41 files, and `docs/stranger-test.md`, which the README sends the
reader to for the QEMU run, is not among them.
Change: add the key, and add `/docs/**` to `include` or make the README's mention a link to the
repository. Door: two-way. Effort: S.

