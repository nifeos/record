---
status: PARTIAL
raised: 2026-10-07
milestone_dependencies: 887
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 819. `jh7110_clock_and_reset`: JH7110 clock and reset logic, proven, then released on its own

*(From calef's rulings on pull request #1806; the title and slug are drafts. Milestone 813 (a proven
FAT crate released on its own) is the shape this follows.)*

calef's rulings, quoted from the maintainer comments on #1806 of 2026-10-07 (UTC):

- Policy: *"Each publish-ours crate (NVMe, e1000e, the DesignWare pair, the JH7110 pair, xHCI, and
  `portable_executable` once it carries proofs) is published when ready (proofs passing, API
  stable), each through its own milestone at its review."* His words: *"Since the consumer would be
  other hobby OSes, I think it makes sense to publish them. [...] a nice legacy is a bunch of hobby
  oses that use its parts."*
- Crates: *"one milestone per crate, minted now, each keeping its tree name (all free on crates.io
  as of today) [...] Names are ratified now and permanent on first publication."* His words: *"Yes,
  one per crate"*.
- Fork 4: *"the release workflow refuses to publish unless the proof job is green."* His word:
  *"Yes"*. The other release rules are forks 1 to 3 and 6, applied in *Release* below.
- The crates take plain values, by the ruling in
  [milestone 857 (crates released on their own)](0857-crates-released-on-their-own.md#the-rulings).

## What exists, checked 2026-10-07 (UTC)

- `crates/jh7110_clock_and_reset`: 863 code lines (1,577 with comments), written by milestone 220
  (this kernel drives no clock or reset controller, and the first real device will need one), which
  is BUILT. It holds the JH7110 clock and reset generator's register offsets and bit fields, the
  bring-up plans the TRNG, the SD slots and the PMIC's I2C bus need, and the device-tree queries
  that find the controllers.
- **Nine Kani harnesses, each with a falsification patch**, in `src/lib.rs`'s `verification` module,
  proving the four properties below. `script/falsifications --sweep jh7110_clock_and_reset` reports
  all nine red under their patches. Fork 4 refuses a release without green proofs, and
  `script/verify` runs these. The note's
  "publish with the DesignWare pair" predates the one-milestone-per-crate ruling.
- Class B in #1806's note `notes/releasable-crates-2026-10-07.md`. **The cut** is codebase rule 2
  (a driver gets what it needs passed in), and the crate now depends on nothing. It holds each
  tree's spellings (`SYSTEM_TOP_GROUP_WINDOW`, `ALWAYS_ON_WINDOW`, `SYSTEM_WINDOW`,
  `POWER_MANAGEMENT_CHIP_COMPATIBLES`) and decoders over
  raw property values (`WindowLocation::from_regions`, `PmicBus::from_nodes`, `DevicePlan::from_specifiers`,
  which take a phandle lookup from the caller). The walks (`discover`, `discover_aon`,
  `discover_sys`, `pmic_bus`) are `machine_discovery::jh7110::clock_and_reset`'s, with their
  fixtures, and `jh7110_watchdog` builds its own `DevicePlan`.
- Its consumers, all in `kernel/src/`: `drivers/jh7110_clock_and_reset.rs` (the volatile shell),
  `designware_ethernet.rs`, `user/designware_mobile_storage_service.rs`, `user/entropy_service.rs`,
  `reboot.rs`, `memory.rs`, `lib.rs`, `storage_bench.rs` and `network_bench.rs`, plus
  `system_tests/src/user/entropy_tests.rs`.
- The crate name is ratified. The decoders and the newly public spellings carry provisional `Name:`
  blocks, and their names become permanent with the crate. `discover_aon` and `discover_sys` left
  the crate with the walk, so their provisional names no longer bind it.
- crates.io answers 404 for the name (checked 2026-10-07).
- A ruling of 2026-10-26 (UTC) ratified the crate's names and renamed eight of them first. The
  `Name:` blocks of its source hold them.

**Reuse:** the alternatives were surveyed in #1806's `other-implementations.md` appendix (looked up
2026-10-07), and none is taken, because calef ruled this crate "publish ours". The only Rust JH7110
crates found, weathered-steel's `jh71xx-pac` 0.11.1 and `jh71xx-hal` 0.7.2 (Codeberg, 2025-03), are
register maps under GPL-3.0-only, which nife cannot take under its license. No Rust crate for the
clock and reset logic was found. Linux's `clk-starfive-jh7110-*` drivers stay the reference and are
read, never copied. The I2C timing function `standard_mode_100k` takes no text from any driver: its
counts follow from the I2C specification's standard-mode limits and the `DesignWare` count
registers' description, and its fill (the whole shortfall to the low count) is nife's own. OpenBSD's
`dwiic.c` (ISC) states no equations (read 2026-11-01), so no notice rides with the function. No
upstream offer goes anywhere, by the ruling in
[milestone 814 (proven NVMe queue logic)](0814-the-nvme-queue-crate-released-on-its-own.md).

## What is proven

Four properties, which nine harnesses prove in `crates/jh7110_clock_and_reset/src/lib.rs`. Every
harness carries a falsification patch that makes it fail at its own assertion, at
`crates/jh7110_clock_and_reset/falsifications/<module.path>.<harness>.patch`, as §134 (a harness
carries a machine-replayable falsification record) and `script/falsifications` require.

| property | harnesses |
|---|---|
| `with_parent` changes only the mux field: for every word and every parent, every bit outside `CLOCK_MULTIPLEXER_MASK` stays as it was and an over-wide parent never spills into the enable bit | `with_parent_changes_only_the_mux_field` |
| Every offset a domain answers is one of its own words: `Domain::clock_offset` and `Domain::reset_bit` return none past the domain's `clocks` or `resets` count, and otherwise a word-aligned offset inside its range and a one-bit mask, for all three domains | `a_clock_offset_is_one_of_the_domains_own_words`, `a_reset_line_is_one_bit_of_one_of_the_domains_own_words` |
| Every plan ungates its clocks before it releases its reset: the six fixed plans, and plans the crate builds from caller-supplied specifiers, hold only in-bounds ids, never more than `MAXIMUM_POWER_MANAGEMENT_CHIP_BUS_STEPS` (or `MAXIMUM_DEVICE_STEPS`), with every `EnableClock` ahead of every `DeassertReset` | `every_fixed_plan_ungates_its_clocks_before_releasing_a_reset`, `a_device_plan_from_specifiers_ungates_before_it_releases`, `the_pmic_bus_plan_is_never_empty_and_ungates_before_it_releases` |
| The status decoders (`is_deasserted`, `is_clock_enabled`, `clock_divider`) are total and match their definitions for every word | `is_deasserted_reads_the_bit_the_mask_names`, `is_clock_enabled_reads_bit_31_and_nothing_else`, `clock_divider_is_the_low_24_bits_and_nothing_else` |

The two built-plan harnesses take the solver 80 to 90 seconds each. They model the caller's phandle
lookup as one SYS controller with one cell per specifier, and feed two clock specifiers and one
reset specifier of whole length. Not proved:

- a lookup that answers with another provider, another cell count or an error;
- a property length that is not a whole number of specifiers;
- plans of more than three specifiers, so the truncation flag;
- the short inputs of the `reg` decoders.

The host tests cover those by example. A lookup that answered differently on every call ran for
over an hour without finishing, and five specifiers timed out at 280 seconds.

Not proven, by design: that a plan's order is the one the silicon needs, which only a board shows,
and the device-tree queries, which the cut moves out of the crate.

## Release, by #1806's rulings

1. The name is settled before anything leaves (857's Fork 5 as calef amended it on 2026-10-11 UTC).
   `script/names jh7110_clock_and_reset` reports it ratified, crates.io answers 404 for it (or it is
   already ours), and `nifeos/jh7110_clock_and_reset` does not exist yet. `script/crate-standalone`
   checks the first.
2. The proofs above exist with their falsification patches, and the cut stands. `cargo tree -p
   jh7110_clock_and_reset` then lists no nife crate.
3. In the tree, `script/verify` proves the harnesses and `Cargo.toml` says `publish = false`.
4. The package meets Fork 3 of
   [milestone 857 (crates released on their own)](0857-crates-released-on-their-own.md#the-rulings).
   `cargo package --list` shows its harnesses and falsification patches.
5. Ready means proofs passing and the API stable.
   [Milestone 814 (proven NVMe queue logic)](0814-the-nvme-queue-crate-released-on-its-own.md#release-by-1806s-rulings)
   says how each is measured; here the soak is step 6. When the soak exits, calef adds it to the
   lint-checked publish allowlist. The `nifeos/jh7110_clock_and_reset` repository is created when
   the crate moves, on the shared CI template (milestone 887), through reusable workflows: Kani
   through `kani-github-action`, lint, release. Its release workflow refuses to publish unless the
   proof job is green. Nothing here reads `target_arch`, so stock Kani serves. §218 (carry a Kani
   patch so riscv64 is proved) applies only if a harness comes to need riscv64. Milestone 589 (Kani
   can prove riscv64 from the hosts we already have) built it.
6. Soak, as its own repository, until the [soak's five end conditions](../../notes/crate-move.md#the-soaks-five-end-conditions)
   in the runbook hold.
7. Publish and consume the release by version, by the runbook's
   [publication steps](../../notes/crate-move.md#publication-and-consumption-by-version).

## Parity

Pure logic, tested on the host. This lane built it on 2026-10-07 with the pinned nightly for
`aarch64-unknown-none-softfloat`, `riscv64imac-unknown-none-elf`, `x86_64-unknown-none` and the
host, all exit 0. The release workflow builds the same four. The silicon is riscv64 only; the crate
is not.

## Standalone

`script/crate-standalone jh7110_clock_and_reset` is clean: it builds the crate in a copy on 1.88 for
the host and the three bare-metal targets, proves all nine harnesses with stock Kani, and replays
all nine falsification patches red. `script/names` reports the crate's name and every `Name:` block
ratified, `CLOCK_MULTIPLEXER_MASK` by the architect on 2026-11-11 (UTC).

## Before the move

The template's gates, run as
[milestone 816 (proven DesignWare Ethernet QoS logic)](0816-the-designware-ethernet-crate-released-on-its-own.md#before-the-move)
runs them, find:

| gate | findings | what they are |
|---|---|---|
| `spelled_out` | 7 | the private clock and reset ids named for the binding's `SDIO0`, `SDIO1` and `GMAC0_TX` |
| `register_names` | 8 | five `len` and `size` fields with no unit; the field `power_management_chip_address`, the PMIC's I2C bus address, with no `bus` qualifier; and two test names that say `addresses` |
| `prose_acronyms` | 28 | acronyms in doc comments not expanded at their first use |

Each is a rename or a doc-comment edit in this tree before the move, with its consumers. Who decides
each rename is as in milestone 816 (proven DesignWare Ethernet QoS logic). The README meets the
template's prose caps.

## Review before release

- The public API speaks the device's vocabulary, by the test milestone 813 states. A reviewer judges
  this; no script can. Known today: the decoders take raw property bytes and a phandle lookup
  generic over the caller's error type, and their names are provisional.
- The architect cleared the crate's review on 2026-11-11 (UTC), which approves creating
  `nifeos/jh7110_clock_and_reset`. The board run of the PMIC reset path follows the move, and the
  README states it as a limitation until then. The clearance covers neither the tag nor a
  publication. The move waits for the rename pass in *Before the move*.

## Exit

A check proves it. `script/verify` proves the four properties and `script/falsifications` reports
every harness `replayable`. In nife, `cargo tree --locked -i jh7110_clock_and_reset` resolves to
`v0.1.x` from crates.io with a checksum in `Cargo.lock`, `crates/jh7110_clock_and_reset` no longer
exists, and the tree builds for all three targets. In `nifeos/jh7110_clock_and_reset`, the run that
published 0.1.0 shows the Kani job green ahead of the publish job. The five soak criteria of release
step 6 hold before it publishes.

The name check of release step 1 passes first, by Fork 5 of milestone 857. Before the move,
`script/crate-standalone jh7110_clock_and_reset` exits 0 in nife, and every row of *What is proven*
names a harness that stock Kani proves in the copy and whose falsification patch makes it fail. No
crate publishes without the proofs milestone 857 (crates released on their own) requires.

## What the crate no longer cites

The crate's source cites nothing of this tree beyond its `Name:` blocks. This section keeps the
links it carried, by milestone 857's provenance rule.

- The crate doc: the volatile shell is `kernel/src/drivers/jh7110_clock_and_reset.rs`, and the
  story is `notes/jh7110-clock-and-reset.md`.
- `Step::SelectParent`, `AON`, `GMAC0_SYSTEM_BRING_UP`, `GMAC0_ALWAYS_ON_BRING_UP`, `SYSCLK_SDIO0_AHB`,
  `SD_INPUT_OUTPUT_BRING_UP` and `BringUpReport::resets` cite the JH7110's Ethernet and SD/MMC work, milestone 53
  (the board's own peripherals: network and storage on real silicon).
- `SYSTEM_TOP_GROUP_BASE`: why a fallback address is safe is the note's section "The one genuinely dangerous
  thing here, and what stops it".
- `SYS`, `PMIC_BUS_BRING_UP`, `PmicBus`, `I2cClockWords`, `COMPATIBLE_SYSTEM_CLOCK_AND_RESET_GENERATOR` and the direct reset
  write's banner: milestone 592 (radon's cold reboot dies in OpenSBI's PMIC write, and the kernel
  sets that write up). Its option B is the direct write, and its 2026-10-10 bench put radon in its
  outcome table's fourth row.
- `SYSRST_I2C5_APB`: every source for the reset line is in milestone 592's block.
- `StandardMode` and `PMIC_RESET_REG`: the vendor U-Boot tree milestone 592 pinned, and its block's
  reading of the PMIC register.
- `src/tests.rs`: the tests left `lib.rs` on 2026-10-12 (UTC), by lane
  maintainer/near-ceiling-splits, to keep the root under §266 (a Rust source file stays under
  2,000 lines, held by a ratchet that only falls).

## BUGS

- Steps 5 and 6 wait on milestone 887 (one CI template) and on 610's
  co-change column.
- The four properties are a proposal, read from the code, not a ruling. The milestone's `MAX_PMIC_BUS_STEPS`
  is `MAXIMUM_POWER_MANAGEMENT_CHIP_BUS_STEPS` in the code.
- The device-tree fixtures are excerpts of the mainline and vendor JH7110 trees. They moved to
  `crates/machine_discovery/tests/fixtures/` with the walk, so the crate ships none; their licenses
  were not checked.
- `standard_mode_100_kilohertz` has not run on the board since its rewrite. At the board's input clock of
  49.5 MHz it programs a high count of 198 and a low count of 297, where the earlier version
  programmed 208 and 229. Both meet the I2C standard-mode minimums by arithmetic, but a PMIC
  reset on the board must confirm the new counts before anyone calls them proven. The check is a
  bench item for the maintainers.
- `needs_person` is `yes` because the exit includes a publication only calef can approve. Everything
  before step 7 can start now.

## Follow-on

- **Outstanding.** The move. `crates/jh7110_clock_and_reset` is still in this tree and the crate
  repository does not exist. What remains is the repository, the tag `v0.1.0`, the soak's end
  conditions, the publication and nife consuming the release by semantic version. Checked by `ls
  crates/jh7110_clock_and_reset` and by `gh api repos/nifeos/jh7110_clock_and_reset`, which returns
  not found.

## Index row

nife's StarFive JH7110 clock and reset generator logic, which carries no proofs today, gains four
Kani proofs with falsification patches, is cut free of nife's device tree, and is published on
crates.io as `jh7110_clock_and_reset` 0.1 from its own `nifeos` repository.
