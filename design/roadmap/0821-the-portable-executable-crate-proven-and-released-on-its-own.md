---
status: REFUSED
raised: 2026-10-07
refused_by: 784
milestone_dependencies: 887
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 821. `portable_executable`: an ELF-to-PE converter, proven, then released on its own

Status REFUSED: calef ruled on 2026-10-21 (UTC), answering milestone 784 (reuse what the tree
wrote)'s item (g) on #2490 with "B". `portable_executable` is to read the ELF and write the PE
through `object` 0.40.0, keep its conversion policy, and stay unpublished. Its input is nife's own
build product, so the proofs below would protect no known user. The text below is the proposal's.

*(From calef's rulings on pull request #1806; the title and slug are drafts. Milestone 813 (a proven
FAT crate released on its own) is the shape this follows.)*

calef's rulings, quoted from the maintainer comments on #1806 of 2026-10-07 (UTC):

- Policy: *"Each publish-ours crate (NVMe, e1000e, the DesignWare pair, the JH7110 pair, xHCI, and
  `portable_executable` once it carries proofs) is published when ready (proofs passing, API
  stable), each through its own milestone at its review."* His words: *"Since the consumer would be
  other hobby OSes, I think it makes sense to publish them. [...] a nice legacy is a bunch of hobby
  oses that use its parts."*
- Crates: *"one milestone per crate, minted now, each keeping its tree name (all free on crates.io
  as of today): [...] and `portable_executable` (its milestone writes its proofs first). Names are
  ratified now and permanent on first publication."* His words: *"Yes, one per crate"*.
- The release rules are forks 1 to 4 and 6 of the same pull request, applied in *Release* below.

## What exists, checked 2026-10-07 (UTC)

- `crates/portable_executable`: 778 code lines (978 with comments), written by milestone 441 (the
  program that makes the stick: one download per host, a boot for every architecture). rustc has no
  riscv64 UEFI target, so the riscv64 loader is linked as a static-PIE ELF. `from_elf` converts it
  into the PE32+ image firmware loads: one section per `PT_LOAD` at the ELF's own addresses, and
  one `DIR64` fixup per `RELATIVE` relocation. Class A in #1806's note
  `notes/releasable-crates-2026-10-07.md`: no dependencies, `no_std` with `alloc`.
- **No Kani harnesses and no falsification patches.** Its one consumer is `xtask/src/stick.rs`.
- **Its `BUGS` says it is not hardened against a hostile ELF**, from the 2026-09-24 security audit.
  `phoff` near `u64::MAX` overflows before the bounds check, and a `PT_DYNAMIC` offset is never
  bounded. A `memsz` of 2^44 with `filesz` 0 sizes the image `Vec`, and `DT_RELAENT = 0` loops until
  memory runs out. That was safe while the only input was an ELF `xtask` linked seconds earlier. A
  published crate takes a stranger's ELF, so the hardening is now owed, and the proofs are what
  show it is done. Milestone 326 (nobody has been assigned to turn a mutation score upward) already
  fixed one wrong-accept here, a relocation bounded by `memsz` where `filesz` was meant.
- crates.io answers 404 for the name (checked 2026-10-07).

**Reuse:** the alternatives were surveyed in #1806's `other-implementations.md` appendix (looked up 2026-10-07),
and none is taken, because calef ruled this crate "publish ours". No ELF-to-PE converter crate
exists on crates.io. systemd's `tools/elf2efi.py` (LGPL-2.1+, Python) takes the same approach and is
the prior art. gimli-rs's `object` 0.40.0 has a PE writer but no converter. Building on it would put
a large dependency inside a crate whose point is that a model checker can reach all of it, which §46
(thin primitives or whole subsystems; we write everything in between) refuses. `goblin` parses both
formats and converts neither.

## What is proven

Nothing yet. The crate has no Kani harnesses today, so closing the audit's holes and writing all
five proofs is this milestone's scope, not a step before it. Each row is a property this crate must
prove before it publishes. The harness cell reads as in milestone 813's table. Each patch sits at
`crates/portable_executable/falsifications/<module.path>.<harness>.patch`, as §134 (a harness
carries a machine-replayable falsification record) and `script/falsifications` require. The first
four rows are the audit's holes, closed.

| property | harness |
|---|---|
| No panic and no overflow on any input: each structure read (file header, program header, dynamic entry, `Elf64_Rela`) takes symbolic bytes and returns a value or an error, with every offset sum checked | none yet |
| The image size is capped: no accepted ELF sizes the output beyond a stated limit, whatever `memsz` says | none yet |
| The relocation walk terminates: a zero or odd `DT_RELAENT` is refused, and the walk visits at most `DT_RELASZ / DT_RELAENT` entries | none yet |
| Every fixup lands inside the image: each `.reloc` entry names an 8-byte word inside a section, and the word holds the relocation's addend | none yet |
| The layout is the ELF's: each section's RVA equals its segment's virtual address and its raw bytes are the segment's file bytes, zero-filled to `memsz` | none yet |

Kani bounds its inputs, so whole-file coverage comes from composing per-structure proofs, with
`script/fuzz` over whole files as the backstop. Not proven: that firmware boots the result, which
the riscv64 UEFI gate shows for this tree's own loader and nothing shows in general.

## Release, by #1806's rulings

1. The name is settled before anything leaves (857's Fork 5 as calef amended it on 2026-10-11 UTC).
   `script/names portable_executable` reports it ratified, crates.io answers 404 for it (or it is
   already ours), and `nifeos/portable_executable` does not exist yet. `script/crate-standalone`
   checks the first.
2. Close the four holes in `BUGS`, write the five proofs above with their falsification patches, and
   rewrite `BUGS` to say what the crate now refuses.
3. In the tree, `script/verify` proves the harnesses and `Cargo.toml` says `publish = false`.
4. The package meets Fork 3 of
   [milestone 857 (crates released on their own)](0857-crates-released-on-their-own.md#the-rulings).
   `cargo package --list` shows its harnesses and falsification patches.
5. Ready means proofs passing and the API stable.
   [Milestone 814 (proven NVMe queue logic)](0814-the-nvme-queue-crate-released-on-its-own.md#release-by-1806s-rulings)
   says how each is measured; here the soak is step 6. When the soak exits, calef adds it to the
   lint-checked publish allowlist. The `nifeos/portable_executable` repository is created when the
   crate moves, on the shared CI template (milestone 887), through reusable workflows: Kani through
   `kani-github-action`, lint, release. Its release workflow refuses to publish unless the proof job
   is green. Nothing here reads `target_arch`; the ELF's machine is data, not the build target. So
   stock Kani serves. §218 (carry a Kani patch so riscv64 is proved) applies only if a harness comes
   to need riscv64. Milestone 589 (Kani can prove riscv64 from the hosts we already have) built it.
6. Soak, as its own repository, until the [soak's five end conditions](../../notes/crate-move.md#the-soaks-five-end-conditions)
   in the runbook hold.
7. Publish and consume the release by version, by the runbook's
   [publication steps](../../notes/crate-move.md#publication-and-consumption-by-version).

## Parity

A host tool in nife, but `no_std` with `alloc`, so it builds anywhere. This lane built it on
2026-10-07 with the pinned nightly for `aarch64-unknown-none-softfloat`,
`riscv64imac-unknown-none-elf`, `x86_64-unknown-none` and the host, all exit 0. The release
workflow builds the same four. Its tests convert riscv64 PIEs; an aarch64 or x86_64 PIE is outside
the first release, since rustc emits PE for those directly.

## Standalone, measured 2026-10-11 (UTC)

`script/crate-standalone portable_executable` fails today, at base `ae6b91e79`. The manifest and
files fail as for all nine crates in
[milestone 814 (proven NVMe queue logic)](0814-the-nvme-queue-crate-released-on-its-own.md#standalone-measured-2026-10-11-utc).
Builds and tests on stable for the host and the three bare-metal targets, and has no harness for
Kani to run. Beyond manifest and files, 8 lines cite this tree: 3 tree paths, 2 `milestone N`, 1
`§N`, 1 naming calef and 1 provenance block.

Name: `portable_executable` is ratified today (`script/names`, checked 2026-10-11).

## Review before release

- The public API speaks the device's vocabulary, by the test milestone 813 states. A reviewer judges
  this; no script can. Known today: Errors are the crate's own; check that no type from `xtask`
  reaches a public signature.

## Exit

A check proves it. `script/verify` proves the five properties, `script/falsifications` reports every
harness `replayable`, and each of the four ELFs the audit described is refused with an error by a
host test. In nife, `cargo tree --locked -i portable_executable` resolves to `v0.1.x` from crates.io
with a checksum in `Cargo.lock`, `crates/portable_executable` no longer exists, and the riscv64
stick still boots in EDK2 under the existing UEFI gate. In `nifeos/portable_executable`, the run
that published 0.1.0 shows the Kani job green ahead of the publish job. The five soak criteria of
release step 6 hold before it publishes.

The name check of release step 1 passes first, by Fork 5 of milestone 857. Before the move,
`script/crate-standalone portable_executable` exits 0 in nife, and every row of *What is proven*
names a harness that stock Kani proves in the copy and whose falsification patch makes it fail. No
crate publishes without the proofs milestone 857 (crates released on their own) requires.

## BUGS

- Steps 5 and 6 wait on milestone 887 (one CI template) and on 610's
  co-change column.
- The five properties are this lane's proposal, read from the code and its audit, not a ruling.
- `needs_person` is `yes` because the exit includes a publication only calef can approve. Everything
  before step 7 can start now.

## Revisit

- **Condition.** `portable_executable` gets an input nife did not link: a second consumer, or a
  reason to publish it. The hardening and the five proofs above are owed again then.

## Index row

nife's ELF-to-PE/COFF converter, the only one on crates.io, hardened against a hostile ELF and given
its first Kani proofs, then published as `portable_executable` 0.1 from its own `nifeos` repository
and consumed back by `cargo xtask` from that release.
