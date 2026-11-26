---
status: BUILT
raised: 2026-11-26
built: 2026-11-26
milestone_dependencies: none
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: no
---
# 1130. Measure an optimized build of the test suite and the gating benchmark

Raised 2026-11-26 (UTC) by calef. The number 1130 is provisional until the integrator mints it at
merge; the title and the slug are drafts.

## Why

The shipped kernel builds with `--release`: opt-level 3, debug assertions off, debuginfo off, and
overflow checks on, which is the one thing the root `[profile.release]` sets. `script/test` and the
gating `script/bench --check` build cargo's dev profile at opt-level 0. The root `Cargo.toml` raises
21 packages one at a time: eighteen to opt-level 2, and fixtures, user_mode_runtime and moho_abi to
opt-level 1. So the build that gates every merge is not the build anyone boots. This is a
measurement, as milestone 744 (measure the kernel's overflow checks) was for milestone 750
(overflow checks in the shipped build). It changes no profile, and the choice it prepares is
calef's.

No milestone or decision chose dev for the gate on its own merits. Milestone 25 (cross-OS
performance comparison) added `bench --release` in nifeos/nife@2ce5d1a97 for magnitudes next to
release Linux, and kept the rest on dev for fast rebuilds and debuginfo. `xtask/src/bench.rs` says
release never runs under icount
because it changes instruction counts. That gives no reason dev is the right thing to count.

Reuse: the measurement uses the suite's own `script/test`, `script/bench --check` and timing record,
with cargo's profile environment overrides. No other optimized test path exists.

## What was measured

All runs were on one 80-core x86_64 Linux host under TCG, on nifeos/nife@a64a709eb2. That is main at
nifeos/nife@a42d91c57e with the measurement's fixes merged in (nifeos/nife#4108, a draft not meant
to merge).

Each optimized level ran in its own worktree with every per-package entry deleted, as the B options
below propose. The O0 column is the tree as it is. The rel column is a release-equivalent dev build:
opt-level 3, debug assertions off, debuginfo off, 16 codegen units, incremental off, overflow checks
on. A true `--release` icount bench matches rel on every row of all three architectures, within
0.23 percent, so rel stands for the shipped profile.

The levels ran one at a time, each alone on the host. Other users raised the host's load to about
30 at times, during the O2 and O3 cold suites in particular. Wall times are single runs and carry
that noise; icount rows carry none.

### The gating benchmark

Every row ran twice at every level, identical to the instruction. Selected rows, as instructions at
O0 and the change from O0 (nifeos/nife#4108 holds every row):

| row | arch | O0 | O1 | O2 | O3 | rel |
|---|---|---|---|---|---|---|
| ipc_rtt | aarch64 | 803253 | -87% | -89% | -89% | -91% |
| spawn_reap | aarch64 | 183437 | -63% | -65% | -65% | -66% |
| map_new | aarch64 | 14628 | -48% | -50% | -50% | -50% |
| coremark | aarch64 | 17739199 | -90% | -90% | -92% | -92% |
| ipc_rtt_el0 | aarch64 | 7978126 | -80% | -86% | -86% | -88% |
| ipc_rtt | riscv64 | 129381 | -86% | -88% | -88% | -90% |
| rfence_self | riscv64 | 5934 | -11% | -11% | -10% | -10% |
| null_system_call | riscv64 | 47400 | -26% | -24% | -24% | -26% |
| ipc_rtt | x86_64 | 13751053 | -86% | -89% | -89% | -91% |
| tss_iomap_switch | x86_64 | 19558051 | -68% | -92% | -92% | -72% |

Findings:

1. At opt-level 0 the bench counts mostly the compiler's unoptimized code. Eight to nine
   instructions in ten on every IPC row do not run in the shipped kernel.
2. The rows do not move together, so an opt-level 0 regression does not predict a shipped one.
3. O1 leaves 16 to 45 percent more IPC instructions than O2, and 3.8 times O2's
   `tss_iomap_switch`.
4. O2 and O3 are equal on every IPC row and differ on CoreMark. Both hold 20 to 30 percent more
   IPC instructions than rel, which is what debug assertions and the other dev settings cost.
5. The shipped profile spends 3.3 times O3's instructions on `tss_iomap_switch`, deterministically.
   Nothing explains it yet, and only a release bench sees it.
6. On main, `bench --release` boots a dev kernel on riscv64 and x86_64 (nifeos/nife#4122).
7. Cargo changed its dev debuginfo default from full to line tables only between nightly
   2026-11-17 and 2026-11-18. The tree set no level, so the pin bump changed it (nifeos/nife#4125,
   closed by nifeos/nife@4a807473a9, which sets the level).

### Drift

One tree, entries deleted, ran each level on nightly 2026-11-17, 2026-11-18 and 2026-11-25, the
pin. The largest move of any row, per interval and architecture:

| level | 17 to 18, aarch64 | riscv64 | x86_64 | 18 to 25, aarch64 | riscv64 | x86_64 |
|---|---|---|---|---|---|---|
| O0 | 19.4% | 16.7% | 16.6% | 0.1% | 5.5% | 0.1% |
| O1 | 0 | 0.5% | 0 | 0 | 2.2% | 2.1% |
| O2 | 2.0% | 1.5% | 0.1% | 0 | 2.2% | 0 |
| O3 | 2.0% | 1.6% | 0.1% | 0 | 4.5% | 0.1% |
| rel | 0 | 0.2% | 0.9% | 0.2% | 2.2% | 0.5% |

Holding debuginfo fixed separates the causes. Nightly 2026-11-17 with full debuginfo against line
tables moves O0 by all of its 17 to 18 change. With debuginfo held, the compiler moves O0 by 0.00
percent from 17 to 18, and O2 by up to 5.4 percent. From 18 to 25 the compiler moves riscv64 at
every level; main re-recorded the O0 row in nifeos/nife@f47aabfde3.

The toolchain-bump workflow restamps only when every row moves under 0.5 percent. Of the six pairs
above, four cross that bound at O0, three at O1, O2 and O3, and two at rel. Optimized moves are
smaller but cross about as often. Two intervals give no rate of re-saves.

The 2026-11-18 re-save, nifeos/nife@1547eb2af9, attributes its move to code generation; it was the
debuginfo default. The review inferred O1 moves of 12 percent over 18 to 25 from two worktrees.
One tree shows none on aarch64.

### The test suite

Each level ran the whole suite cold, then each architecture's legs warm. All failures but one lean
on opt-level 0 or on debug assertions:

1. Linker-symbol comparisons. `interrupt_stack.rs`, `arch/x86_64/ist.rs` and `smp.rs` compare a
   linker symbol to a computed address. LLVM folds the comparison of two distinct globals to
   unequal, so at O1 and up they fail printing two equal numbers. `core::hint::black_box` fixes all
   three.
2. `ipc_stack_depth`. `cfg(debug_assertions)` picks its paint margin: 512 bytes in debug, 64 in
   release. At O1 to O3 every series sits at the floor. With the margin forced to 64, series at the
   floor per run are 0 at O0, 0 to 3 at O1, 1 at O2 and O3, and 1 or 3 at rel. At rel that is the
   test's own release branch, which fails in the shipped profile and has never gated. #4108 prints
   instead of asserting, so no working fix exists.
3. The loader's test binary. Optimized, `image_self_checker` folds its one read of `RODATA_MARKER`
   to a constant and links no read-only segment. Two loader tests then fail on aarch64 and x86_64.
   `black_box` on the reference fixes it at every level.
4. Debug assertions, rel only. The host leg stops at `a_second_free_of_one_identifier_is_caught`, a
   `should_panic` test of a `debug_assert!`. A release leg would gate it on `debug_assertions`.
5. A real hang, nifeos/nife#4129. On riscv64,
   `a_driver_killed_mid_write_leaves_the_device_and_transport_sane` hung in O1's cold suite with a
   lost-wakeup report. Repeated 90 times per level, it passed every run at O0 and O1 and hung once
   at O2. Optimized timing exposes a race that opt-level 0 hides.

With items 1 and 3 patched and item 2 printed, O1, O2 and O3 pass the whole suite on all three
architectures apart from item 5; O1's cold rerun passed. At rel the kernel and system legs pass.

`SUITE_PAGE_FRAME_BUDGET` is 24,999. The frames the system leg never returns on aarch64 are 24,975
at O0 (24 spare), and about 24,600 at O1 to O3.

Wall time in seconds. Kernel legs are the kernel, system, IOMMU and OVMF legs, run phases summed;
O1's cold figures are from its rerun:

| measure | O0 | O1 | O2 | O3 | rel |
|---|---|---|---|---|---|
| kernel legs, cold suite | 905 | 613 | 627 | 631 | 576 |
| kernel builds, cold suite | 55 | 70 | 89 | 92 | 68 |
| aarch64 legs, warm | 271 | 189 | 168 | 187 | 173 |
| riscv64 legs, warm | 285 | 187 | 193 | 169 | 202 |
| x86_64 legs, warm | 603 | 408 | 417 | 369 | 373 |
| host leg, warm | 71 | 60 | 60 | 67 | stops at item 4 |
| one-line kernel edit, rebuild | 11 | 16 | 25 | 21 | 17 |
| the edit, rebuild and aarch64 legs | 270 | 200 | 209 | 204 | 190 |
| user programs, cold, per architecture | 6 to 7 | 8 to 9 | 7 to 9 | 7 to 8 | 7 to 8 |

The kernel legs run about 30 percent faster optimized; most of a leg is timer waits, device
emulation and image builds. O1, O2 and O3 are within noise of each other, and O3 builds no slower
than O2. The edit loop, the original reason for dev, rebuilds 10 seconds slower at O3 and finishes
66 seconds sooner. The std programs build in release in their own workspace, so the dev profile
does not reach them.

### What else moves

- The 21 entries. At a base of O2 or O3 they are no-ops, or hold fixtures, user_mode_runtime and
  moho_abi below the base.
- Board images. `script/board-image` packs dev-profile user programs next to the release kernel.
  Any B option changes what runs on boards and moves every board job-mix and soak number. This
  overlaps milestone 797 (release userspace in board images).
- fastpath-footprint and build-is-reproducible already build `--release`. Kani and Miri follow only
  `cfg(debug_assertions)`. Panic output comes from `PanicInfo` at every level.
- Debugging. Under `cargo xtask gdb` on aarch64, a break in `isa::initialize`, three frames deep,
  at two lines:

  | debuginfo | level | frames | argument | locals |
  |---|---|---|---|---|
  | line tables, the default | O0, O2 | names and lines | none | none |
  | full | O0 | names, lines, arguments | both lines | in full |
  | full | O1 to O3 | names, lines, most arguments | first line only | partly optimized out |

  With the default, O0 shows no argument or local either. nifeos/nife@4a807473a9 now builds
  `xtask gdb` with full debuginfo. Optimized, the backtrace resolves every frame, and values
  vanish after their last use.
- Mutation testing. coremark and capability_manifest_note ran `script/mutation` at O0 and at O2.
  Both levels generate the same mutants with the same outcomes. O2 costs 12 and 19 percent more
  wall time, from each mutant's rebuild: coremark's builds take 27 percent longer, and
  capability_manifest_note's viable mutants 66 percent longer.
- Mutation and the entries. Holding `script/mutation` at O0 conflicts with deleting the entries.
  With them deleted, globally_unique_identifier_partition_table's host tests take 50 seconds at O0
  and 7 at O2, network_time_protocol's 22 and 3. Eleven other packages take 2 seconds or less.
  Each of their mutants would pay the O0 time, so mutation should follow the dev profile.

### What option C costs beyond a baseline save

A release bench re-saves all three baselines once, and `bench/attributions.tsv` loses continuity
there. The toolchain-bump workflow and `metrics.yml`'s drift check act on the numbers. About twenty
record notes and `notes/benchmarks.md` cite tick counts and need the profile named. The rule against
release under icount needs rewriting, and #4122 needs fixing.

A true release bench completed on all three architectures. An earlier x86_64 hang was the
measurement's own: the release path inherited the suite's ramdisk, disk and network settings, which
nifeos/nife@a64a709eb2 strips. Nothing else blocks C.

## Options

Costs are measured unless marked unmeasured.

- A. Keep dev at opt-level 0. No work. The gate counts mostly unoptimized code, never runs a
  release-only path, and hides #4129. With debuginfo now set, its drift is like the optimized
  levels'.
- B1, B2, B3. Dev at opt-level 1, 2 or 3, with assertions, overflow checks and debuginfo kept. Fix
  the symbol comparisons and the loader fixture, delete the entries, and save one baseline per
  architecture. Each first needs #4129 fixed and `ipc_stack_depth` reworked; neither fix exists,
  and their cost is unmeasured. Board numbers move. B1 counts 16 to 45 percent more IPC
  instructions than B2. B2 and B3 cost the same to build and run, and B3 is the shipped opt-level.
- R. A release suite leg in the merge queue: the kernel and system legs on a release build, 173 to
  373 seconds per architecture warm here. It needs item 4 gated and `ipc_stack_depth`'s release
  branch fixed. It alone tests paths that exist only in the shipped build, such as `heal_self_pop`
  in `sched/switch.rs`.
- C. The gating bench on a release build, the suite unchanged. Fix #4122 and pay the costs above. It
  counts what ships, sees `tss_iomap_switch`, and is immune to the debuginfo default.
- D. B2, then C. Two baseline saves and two breaks in `attributions.tsv`, and C throws the O2
  baseline away. Holding the bench at O0 until C instead means keeping three entries for it,
  since any B option moves the EL0 rows.
- E. C, then B3, then R. One baseline save, since a release bench does not follow the dev profile.

## Recommendation

E. Move the gating bench to release now. Move the suite to opt-level 3 once #4129 and
`ipc_stack_depth` are fixed, and add the release leg to the merge queue after that.

The order follows blockers, not effort. C waits only on #4122. B3 and R wait on fixes of unknown
cost. Doing C first means B3 never touches a baseline.

The seven questions:

1. What else did this consider? A keeps a gate that counts a build nobody runs. B1 counts more code
   that does not ship. B2 costs what B3 costs and is further from what ships. D saves two baselines
   where E saves one. C alone leaves the suite hiding #4129.
2. What does this tree do in the analogous case? fastpath-footprint and build-is-reproducible build
   the shipped profile because that is what they check. Milestone 750 put overflow checks in
   release to check what ships.
3. Prior art, read on 2026-11-26. Linux and seL4 test at the level they ship, `-O2` for both. Linux
   offers only `-O2` and `-Os`
   ([Makefile](https://github.com/torvalds/linux/blob/ebb7a8dc1e74/Makefile#L938-L949),
   [init/Kconfig](https://github.com/torvalds/linux/blob/ebb7a8dc1e74/init/Kconfig#L1465)), with
   Rust debug assertions set apart by
   [RUST_DEBUG_ASSERTIONS](https://github.com/torvalds/linux/blob/ebb7a8dc1e74/lib/Kconfig.debug#L3616).
   seL4 keeps optimization apart from `KernelDebugBuild`
   ([config.cmake](https://github.com/seL4/seL4/blob/78b0c34efe12/config.cmake#L234-L304)), and its
   benchmarks use release settings
   ([sel4bench](https://github.com/seL4/sel4bench/blob/18f9d5f079bc/settings.cmake#L69-L70),
   [seL4_tools](https://github.com/seL4/seL4_tools/blob/6493e0c6fab3/cmake-tool/helpers/application_settings.cmake#L93-L115)).
   [Fuchsia](https://fuchsia.dev/fuchsia-src/development/build/build_system/fuchsia_build_system_overview)
   calls its debug build unsuitable for performance testing.
   [rustc-perf](https://github.com/rust-lang/rustc-perf/blob/463fb3a255f7/collector/README.md#L65-L68)
   counts instructions of the artifacts built from merged commits. None benchmarks an unoptimized
   build. The precedent is to test at the shipped level, which for nife is 3, and to bench the
   shipped build.
4. Is the premise true? Yes, with two corrections: three of the 21 entries are at opt-level 1, and
   board images ship a dev user space.
5. What does each cost? In Options.
6. How reversible? B3 and R are two-way doors: a profile is two lines and a leg is one job. C is
   less so, because workflows and notes act on its numbers.
7. Would we still choose it at equal cost? Yes. At equal cost one would test at the shipped level
   with assertions on, test the shipped build, and bench it. That is E.

The review's open questions, answered where a measurement could:

- The edit loop at O2 or O3 rebuilds in 25 or 21 seconds against 11, and finishes sooner.
- The shipped x86_64 kernel showed no bug; the hang was the measurement's.
- Board user space and milestone 797 move under any B option.
- No reason for O2 over the shipped level survives; O3 costs the same.
- An optimized baseline needs re-saving about as often as an O0 one, over two intervals.

## What remains unmeasured

- The build and run balance on CI runners; everything ran on one host.
- `script/coverage` at any optimized level.
- The full mutation census, and mutation at O3.
- Board images on hardware.
- The cost of fixing #4129 and `ipc_stack_depth`.
- Why `tss_iomap_switch` costs more in release. One icount run per setting bisects it over the five
  settings that separate O3 from rel.

## Follow-on

- **Recorded.** The choice among the options is calef's, in Options and Recommendation above.
- **Recorded.** Filed: nifeos/nife#4122 and nifeos/nife#4129. nifeos/nife#4125 is closed.
- **Recorded.** On E, a C lane fixes #4122 and moves the bench. A B3 lane follows #4129 and an
  `ipc_stack_depth` rework, and carries the test fixes from #4108. An R lane follows the rework.

## Index row

What building the test suite and the gating icount bench optimized would cost and find, measured at
opt-level 0 to 3 and release on three ISAs, with toolchain drift, options and a recommendation for
calef; no profile changed.
