---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1049, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1150. `jh7110_entropy`: the release review's findings

*(The number and the slug are provisional.)*

The release review of `partsfoundry/jh7110_entropy` at commit `eac91efd`, version 0.3.0-pre.2,
under milestone 1129 (the combine review), whose [block](1129-crate-interfaces-best-in-class.md)
sets its form. Two blocks carry "release review" in their names. The baseline is milestone 1049
(`jh7110_entropy` is ready to publish), [its block](1049-jh7110-entropy-release-review.md), which
did for this crate what the outside reviews did for the others. This block is the comparison
with other crates that 1129 asks for. `notes/crate-reviews/` holds no package for this crate.
1049's open items stay its own. The names it ratified stand, and no later naming rule reopens
one. Three of its rulings meet comparator evidence and stand below as doors D5, D7 and D9.

Reuse: the prior-art table weighs each hardware random number generator crate a caller could take.

## Finding status

- P0-1, the ready bytes can be printed and copied: Open.
- P0-2, `GenerationOutcome` is exhaustive: Open.
- P0-3, the two status words share one type: Open.
- P0-4, `Discovered` is an exhaustive struct that no function uses: Open.
- P0-5, `Pool` compares its bytes with `==`: Open.
- P0-6, `Pool` drops the reason and lets a caller drop the count: Waiting on the errors decision
  of milestone 1129.
- P0-7, byte counts are `u64` in half the `Pool` interface: Open.
- P0-8, the register offsets are `u64`: Waiting on the register-access decision of milestone 1129.
- P1-1, two doc comments describe a caller's program: Open.
- P1-2, no example performs the register sequence: Open.
- P1-3, no function that answers is `#[must_use]`: Open.
- P2-1, a `rand_core` adapter: Waiting on the feature-name decision of milestone 1129.
- P2-2, the bring-up and generation sequences over a register trait: Waiting on the
  register-access decision of milestone 1129.
- P2-3, no attribute states that the crate has no `unsafe`: Open.
- P2-4, `take_into` moves one byte at a time: Open.

## Open decisions

The one-way doors D1 to D9 below.

## Goal

A stranger with a JH7110 board picks this crate over the peripheral access crate for the chip and
over porting Linux's driver. Its types refuse a swapped status word and a printed answer, and
its pool says why it ran dry.

## What the review read and ran

[The appendix](1150-jh7110-entropy-release-review/what-was-checked.md) lists the files, the
commands and the comparators, and
[the guidelines table](1150-jh7110-entropy-release-review/api-guidelines.md) marks the 54 items.

## Prior art

Measured from the crates.io API on 2026-11-26 (UTC). A stranger wants random bytes from the
JH7110's generator with no operating system. No crate for this chip draws 10,000 downloads in 90
days, so the review also reads Linux's driver. The ranked rows are the generator crates a
stranger knows from other chips, which set what a caller expects of this one.

| crate or system | role | version read | total | 90 days | reverse dependencies | version read released |
|---|---|---|---|---|---|---|
| `rdrand` | ranked 1: another device, the processor's own instruction | 0.9.0 | 47,151,088 | 5,313,118 | 8 | 2026-05-15 |
| `esp-hal` | ranked 2: another device, inside a whole HAL (`rng`) | 1.2.3 | 1,137,199 | 251,694 | 133 | 2026-11-26 |
| `embassy-stm32` | ranked 3: another device, inside a whole HAL (`rng`) | 0.6.0 | 866,904 | 203,708 | 47 | 2026-03-20 |
| `jh71xx-pac` | measured and read, not ranked: the same registers, no logic | 0.11.1 | 27,371 | 882 | 1 | 2025-03-04 |
| `jh71xx-hal` | measured and read, not ranked: the same chip, no generator module | 0.7.2 | 15,440 | 799 | 2 | 2025-03-23 |
| `nrf-hal-common` | neighbor: another device, inside a HAL (`rng`) | 0.19.0 | 414,371 | 99,894 | 11 | 2025-10-11 |
| `virtio-drivers` | neighbor: the virtio entropy device | 0.13.0 | 445,812 | 101,928 | 91 | 2026-03-03 |
| `rand_core` | integration: `TryRng`; its `block::BlockRng` is a neighbor of `Pool` | 0.10.1 | 2,322,813,641 | 693,909,165 | 2,832 | 2026-04-13 |
| Linux `drivers/char/hw_random/jh7110-trng.c` | outside Rust | v6.12 | | | | |

Searches of crates.io for jh7110, starfive, trng and hwrng find no other driver for this block.
The two `jh71xx` crates are GPL-3.0-only; the review read them for their interface shape only.

### What `jh7110_entropy` does better

- Than `jh71xx-pac`: it decides what a snapshot means, where the access crate only names fields.
  A caller can acknowledge `RAND_RDY` with it; the access crate's `Istat` is `Readable` only. It
  names `FEATURES`, the seed registers and the build configuration register. Its command values
  ran on a board. It has no dependencies and a permissive license.
- Than `rdrand`: every refusal has its own name (`Lockup`, `Unseeded`, `WrongOutputWidth`,
  `NotReady`), where `ErrorCode` has `HardwareFailure` for all of them.
- Than the three HAL crates: a fault is an answer. Their blocking `read`, `random` and
  `fill_bytes` cannot fail.
- Than `rand_core`'s `BlockRng`: `Pool` zeroes each byte as it serves it and is not `Clone`.
- Than Linux v6.12: a model checker exhausts the decision. It refuses a latched `RAND_RDY` on
  an unseeded core; the Linux driver defines `STARFIVE_STAT_SEEDED` and never reads it.

## The items

Effort is S (half a day), M (a day or two) or L (longer). A P0 changes a public item that callers
build on from the first published version, so it lands before that version or stays as it is.

### P0: the 0.1.0 interface

The first published version of this crate is 0.3.0, as 1049 ruled, and these items block it.

#### P0-1. The ready bytes can be printed and copied

Verified in source.
`GenerationOutcome` derives `Debug`, `Clone` and `Copy`, and `Ready` carries the 32 bytes. So
`{outcome:?}` prints the answer, and the README's own example formats an outcome that way. A copy
of the outcome is a second copy of the bytes that nothing zeroes. `rand_core`'s `BlockRng` has a `Debug` that leaves out its results (`src/block.rs`), and Linux
copies the words straight into the caller's buffer.
Change: a hand-written `Debug` that prints `Ready` without its bytes, and no `Clone` or `Copy`.
Door: one-way (D1). Effort: S.

#### P0-2. `GenerationOutcome` is exhaustive

Verified in source.
The enum has no `#[non_exhaustive]`, so a new variant breaks every `match`. It grew one already:
`WrongOutputWidth` arrived as a breaking change (`CHANGELOG.md`, 0.3.0-pre.1). More are in sight:
the crate names two alarm bits it does not decode, and its documentation leaves a health test
open. `esp-hal`'s `TrngError` is
`#[non_exhaustive]`. A wildcard arm is safe, because only `Ready` carries bytes.
Change: `#[non_exhaustive]` on the enum. Door: one-way (D2). Effort: S.

#### P0-3. The two status words share one type

Verified in source.
`generation_outcome(status: u32, interrupt_status: u32, ..)` takes `STAT` and `ISTAT` as two
bare `u32`s, so a call with the two swapped compiles. Swapped, the function looks for `SEEDED`
(bit 9) in the `ISTAT` word, which never sets it, and answers `Unseeded` on every poll. The
proofs cover the function, not the call. `jh71xx-pac` reads the two registers as two types,
`stat::R` and `istat::R`.
Change: a newtype over `u32` for each register, with provisional names. Door: one-way (D3).
Effort: S.

#### P0-4. `Discovered` is an exhaustive struct that no function uses

Verified in source.
`Discovered` has five public fields, and no function of the crate takes or returns one. The
binding the crate cites gives the node two clocks and one reset, which the README's BUGS section
leaves to the caller, and the struct carries neither. A new field breaks every struct literal,
and `#[non_exhaustive]` does not help, since callers are the only constructors. Linux keeps all
of them in its private `struct starfive_trng`.
Change: take the struct out of the published interface; the two decoders and `COMPATIBLES` stay.
Door: one-way (D4). Effort: S.

#### P0-5. `Pool` compares its bytes with `==`

Verified in source.
`Pool` derives `PartialEq` and `Eq`, which compare the buffers and stop at the first difference.
No test, proof or example compares two pools, and the comparison's time depends on unserved
bytes. `BlockRng` implements neither trait.
Change: remove both derives. Door: one-way (D5). Effort: S.

#### P0-6. `Pool` drops the reason and lets a caller drop the count

Verified in source.
The generator a caller hands to `refill`, `take_into` and `take` returns `Option<[u8; 32]>`. A
lockup, an unseeded core, the wrong width and the caller's own timeout all become `None`.
`take_into` then returns a bare `usize`, and the bytes of `out` past it keep their old contents.
A caller that ignores the count serves those old bytes as random.
`rand_core`'s `TryRng::try_fill_bytes` returns `Result<(), Self::Error>`, with `Error:
core::error::Error`. The crate has no error type.
Change: the generator returns `Result<[u8; 32], E>`, and `take_into` returns a `Result` whose
error carries the count served and the generator's `E`, in the form the errors decision of
milestone 1129 picks. Door: one-way (D6). Effort: M.

#### P0-7. Byte counts are `u64` in half the `Pool` interface

Verified in source.
`take` takes `byte_count: u64`, and `TakenBytes::byte_count` and `WORD_BYTES` are `u64`.
`take_into` and `remaining_bytes` return `usize`, so `take` casts three times. A count of bytes
in memory is `usize` in the standard library and in every comparator:
`VirtIORng::request_entropy` returns `Result<usize>`.
Change: `usize` for the three. Door: one-way (D7). Effort: S.

#### P0-8. The register offsets are `u64`

Verified in source.
The 26 constants of `registers` are `u64`, though the largest is `0x68`. The crate declares no
register trait, so a caller adds each offset to its mapped base, which takes a `usize`. Linux
adds a plain integer to `trng->base`, and `jh71xx-pac` places each register in a `#[repr(C)]`
struct.
Change: the width the register-access decision of milestone 1129 picks for every driver. Door:
one-way (D8). Effort: S.

### P1: before the first release

#### P1-1. Two doc comments describe a caller's program

Verified in source.
`Pool::remaining_bytes` says the program reports the count once, in its readiness message.
`WORD_BYTES` and `Pool::take` speak of a caller whose protocol clamps to 8. A stranger has
neither. Change: say what each item returns, with no caller in the sentence.
Door: two-way. Effort: S.

#### P1-2. No example performs the register sequence

Verified in source (C-EXAMPLE).
The README gives the order in one paragraph of prose: write the mode, clear `ISTAT`, reseed,
generate, poll, read the words, acknowledge `RAND_RDY`. No example performs it, and the crate
has no `examples/` directory. `interrupt_line`, `output_bytes` and `Pool::refill` have no
example either. `esp-hal`'s `Trng` page fills a buffer in a few lines. Change:
`examples/polling_driver.rs` (a provisional name), which runs the sequence against a fake
register file and feeds a `Pool`, added to the manifest's `include` list; and an example on each
of the three items. Door: two-way. Effort: S.

#### P1-3. No function that answers is `#[must_use]`

Verified in source.
The attribute stands on `Pool::new` and `remaining_bytes` only. `generation_outcome`,
`output_bytes`, `interrupt_line`, `is_status_okay`, `refill`, `take_into` and `take` return an
answer a caller may drop without a warning. Change: the
attribute on the seven functions, `GenerationOutcome` and `TakenBytes`. Door: two-way. Effort: S.

### P2: may follow

#### P2-1. A `rand_core` adapter

Verified in the comparators' source.
Every generator crate read here implements `rand_core`'s traits: `rdrand` those of 0.10 with no
feature, `esp-hal` 0.6, 0.9 and 0.10, `embassy-stm32` 0.6 and 0.9, and `nrf-hal-common` 0.9.
1049's item 17 declined an adapter. An adapter needs a type that owns the register access,
which P2-2 adds. Change: none before the first release; with P2-2, an optional
`TryRng` under the name the feature-name decision of milestone 1129 picks. Door: two-way as an
addition; the standing decline is D9. Effort: S.

#### P2-2. The bring-up and generation sequences over a register trait

Verified in source.
The crate never touches a register, so each caller writes the sequence of P1-2 and keeps two
rules the README states in prose: no command while one is in flight, and `RAND_RDY` acknowledged
after the words. Linux has them as code in `starfive_trng_wait_idle`, `starfive_trng_cmd`,
`starfive_trng_init` and `starfive_trng_read`. Change: a bring-up function and a generation
function over the trait the register-access decision of milestone 1129 picks, each taking the
caller's poll bound. Door: two-way (an addition).
Effort: M.

#### P2-3. No attribute states that the crate has no `unsafe`

Verified in source.
The README says the crate has no `unsafe`, and `src/lib.rs` does not enforce it. Change:
`#![forbid(unsafe_code)]`. Door: two-way. Effort: S.

#### P2-4. `take_into` moves one byte at a time

Verified in source; measured below.
The inner loop copies a byte and zeroes it. Change: `copy_from_slice` and `fill(0)` over each
run. Door: two-way. Effort: S.

### Measured performance

`Pool::take_into` against `rand_core` 0.10.1's `BlockRng::fill_bytes`, the nearest published
buffer over a block generator, on a Linux x86_64 host. Both draw 32-byte blocks from one
counter. Each range covers three runs of the program, and the appendix gives the loop.

| request | `Pool` | `BlockRng` |
|---|---|---|
| 8 bytes into a slice | 14.7 to 15.7 ns | 5.8 to 6.2 ns |
| 32 bytes into a slice | 48.0 to 53.3 ns | 10.3 to 10.9 ns |
| 1024 bytes into a slice | 1475 to 1680 ns | 280 to 293 ns |
| one `u64` (`take(8)`, `next_u64_from_u32`) | 13.1 to 13.4 ns | 1.2 ns |

`generation_outcome` on a ready snapshot takes 7.4 to 8.0 ns alone. The `Pool` columns include
that decode on each refill and the zeroing of each byte; `BlockRng` does neither.

Inferred: the interface does not bound the crate's speed on its device. The README measures one
generation on a board at 6.0 microseconds, about 190 ns for each byte, against 1.5 ns here.

## One-way doors

- D1, the ready bytes (P0-1). Recommended: a `Debug` that prints no bytes, and no `Clone` or
  `Copy`, the stricter choice; either trait can come back later.
- D2, the outcome enum (P0-2). Recommended: `#[non_exhaustive]`, the stricter choice.
- D3, the status words (P0-3). Option A: a newtype for each register. Option B: one struct for
  the snapshot. Recommended: A, which gives P2-2 its return types.
- D4, `Discovered` (P0-4). Option A: take it out. Option B: keep it and add the clocks and the
  reset. Recommended: A, the stricter choice.
- D5, `Pool`'s equality (P0-5). 1049's item 8 kept `PartialEq` and `Eq` when it removed `Clone`
  and `Copy`. Recommended: remove both, the stricter choice.
- D6, the generator's answer (P0-6). Option A: a `Result` in and a `Result` out. Option B: keep
  `Option` and the short count, with `#[must_use]` as the only guard. Recommended: A, the
  stricter choice.
- D7, the count type (P0-7). 1049's item 9 ratified `TakenBytes` with a `u64` count. Option A:
  `usize` for the three, with `word` still a `u64`. Option B: remove `take`, `TakenBytes` and
  `WORD_BYTES`. Recommended: A. B is smaller, but two of the eight proofs enter through `take`.
- D8, the register offset width (P0-8). Recommended: the one width the register-access decision
  gives every driver. Block 1145 (the release review of `e1000e`) recommends `u32`.
- D9, the `rand_core` adapter (P2-1). 1049's item 17 declined it, and every comparator ships
  one. Recommended: the decline stands for the first release, the stricter choice, since an
  adapter is an addition. P2-2 reopens it.

## Evidence for the shared decisions

- **Errors.** The crate has no error type, and `Pool` reports failure as `None`, `false` or a
  short count (P0-6). `rdrand`'s `ErrorCode`
  (`src/errors.rs`) is an exhaustive enum with `Display` and `core::error::Error`.
  `embassy-stm32`'s `rng::Error` implements neither. `esp-hal`'s `TrngError` is
  `#[non_exhaustive]`, and `TryRng` requires `Error: core::error::Error`. Points toward one enum
  for the crate with both traits and `#[non_exhaustive]`, and an error that says how far the
  operation got.
- **DMA regions.** Not applicable: the device has no direct memory access path.
- **Doorbells and tails.** Not applicable: the device has no ring.
- **Register access.** The crate declares offsets and bit constants and no trait. `jh71xx-pac`
  uses a `#[repr(C)]` block with typed readers and writers. The three HAL crates own their access
  crate's singleton, and Linux uses `readl` and `writel` on a base plus an offset. Only this
  crate leaves the sequence to prose (P2-2). Points
  toward a shared register trait under this crate's sequences, and one offset width (D8).
- **Byte sinks and sources.** The crate declares no byte trait. `Pool::take_into` fills a
  caller's `&mut [u8]`, the shape of `TryRng::try_fill_bytes` and `VirtIORng::request_entropy`.
  No comparator implements `embedded-io`'s `Read` on its generator. Points toward `rand_core` as
  this crate's integration (P2-1), not `embedded-io`.
- **Feature names.** The crate declares no features; the one candidate is the adapter.
  `esp-hal` renames each optional `rand_core` with its version (`rand_core-06`, `rand_core-09`,
  `rand_core-010`) and turns all three on under its `unstable` feature. `embassy-stm32` renames
  its two the same way. Points
  toward a name that carries the dependency and its version, as `file_allocation_table`'s
  `embedded-io-07` does.
- **Simulators.** The crate has none and needs none, since its functions take register values
  as arguments. No comparator ships one. Points toward a public example (P1-2).
- **Contract layout.** Not applicable: the crate exports no interface identity or magic.

## Follow-on

- **Outstanding.** The shared decisions of milestone 1129 take D6 for errors, D8 and P2-2 for
  register access and P2-1 for feature names.

## Done when

The `jh7110_entropy` review is done once its P0 and P1 items read Done or Will not fix, D1 to D9
have rulings, and `script/review-status` lists BUILT.

## BUGS

- The benchmark ran on a host against a counter, not on the device, and its comparator is a
  neighbor: no published crate buffers a hardware generator's blocks as `Pool` does.
- The ranked comparators drive other devices, and the one crate for the same registers has no
  logic to compare.
- The review read one Linux file at v6.12 and no NetBSD source.

## Index row

The release review of `jh7110_entropy` against eight crates and Linux. Eight one-way interface
changes come before the first published version and three smaller fixes before the release. The
pool serves a byte in 1.5 ns against the device's 190 ns, and nine doors wait.
