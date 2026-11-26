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

The shipped kernel builds with `--release`: opt-level 3, debug assertions off, and overflow checks
on, which is the one thing the root `[profile.release]` sets. `script/board-image` ships that
release kernel with a debug user-space archive; milestone 797 (release user space in board images)
would change that and has not started. `script/test` and the gating `script/bench --check` build
cargo's dev profile at opt-level 0, with 21 packages raised one at a time in the root `Cargo.toml`:
eighteen to opt-level 2, and fixtures, user_mode_runtime and moho_abi to opt-level 1. So the build
that gates every merge is not the build anyone boots. This is a measurement, as milestone 744
(measure the kernel's overflow checks) was for milestone 750 (overflow checks in the shipped
build): it changes no profile, and the choice it prepares is calef's.

No milestone or decision chose dev for the gate on its own merits. Milestone 25 (cross-OS
performance comparison) added `bench --release` in nifeos/nife@2ce5d1a97 on 2026-07-25, as a
statistical, hardware-accelerated path for magnitudes next to release Linux. It kept everything
else on dev, its message says for fast rebuilds and debuginfo for the tests.
`xtask/src/bench.rs` still says why release never gates: it changes instruction counts, so it never
runs under icount. That says the icount baseline holds dev counts; it gives no reason dev is the
right thing to count.

Reuse: none exists; the measurement uses the suite's own `script/test`, `script/bench --check` and
its timing record unchanged, with cargo's profile environment overrides. A search of nifeos/nife
`xtask/` and `script/` for an existing optimized test path found only `bench --release`.

## What was measured

All runs were on one 80-core x86_64 Linux host under TCG, against nifeos/nife main at
nifeos/nife@4727ab7cf2 merged into the measurement branch (nifeos/nife#4108, a draft not meant to
merge). Each level ran in its own worktree with every per-package entry deleted, which is what
option B below proposes, and cargo's dev-profile environment overrides set the base level. The
untouched tree, with its 21 entries, is the O0 column. The release column is a true `--release`
build of the bench kernel and its user programs, through a measurement switch on #4108. Two
levels ran at a time, so wall times carry noise of perhaps ten percent; the icount rows carry none.

Runs still going at this revision: O1, O3, the release-equivalent dev build, and the release bench
on riscv64 and x86_64. Their cells read pending.

### The gating benchmark

Every row ran twice at every level, and the two runs are identical to the instruction. Every
optimized run fails `--check`, as it must, since the baseline holds opt-level 0 counts. Selected
rows (instructions; nifeos/nife#4108 holds the full tables):

| row | arch | O0 | O2 | release |
|---|---|---|---|---|
| ipc_rtt | aarch64 | 803253 | -89% | -91% |
| call_reply | aarch64 | 836441 | -89% | -91% |
| spawn_reap | aarch64 | 183437 | -65% | -66% |
| map_new | aarch64 | 14628 | -50% | -50% |
| coremark | aarch64 | 17739199 | -90% | -92% |
| null_system_call | aarch64 | 238750 | -45% | -45% |
| ipc_rtt_el0 | aarch64 | 7978125 | -86% | -88% |
| ipc_rtt | riscv64 | 129381 | -88% | pending |
| rfence_self | riscv64 | 5934 | -11% | pending |
| null_system_call | riscv64 | 47400 | -24% | pending |
| ipc_rtt | x86_64 | 13751053 | -89% | pending |
| tss_iomap_switch | x86_64 | 19558051 | -91% | pending |
| coremark | x86_64 | 263128262 | -87% | pending |

Findings:

1. At opt-level 0 the bench counts mostly the compiler's unoptimized code, not the kernel's paths.
   Eight to nine instructions in ten on every IPC row are code that the shipped kernel does not
   execute.
2. The rows do not move together, so an opt-level 0 regression does not predict a shipped one.
   `rfence_self` falls 11 percent (it is firmware-bound), `map_new` half, IPC nine tenths.
3. Compiler drift is large at opt-level 0. The 2026-11-18 nightly re-save (nifeos/nife@1547eb2af9)
   moved x86_64 rows -12.5 to -16.6 percent, aarch64 -10.5 (`map_new`) to -19.6 (`map_el0`), and
   riscv64 -1.7 (`rfence_self`) to -16.8. Drift at O1 and O2 across a toolchain change is not yet
   measured. The toolchain-bump workflow restamps only when every row moves under 0.5 percent and
   all under 2 percent together; those bounds came from O0 drift and would need checking again.
4. On main, `bench --release` builds a release kernel only on aarch64. The riscv64 and x86_64 paths
   call cargo directly and boot `target/<triple>/debug/kernel`, so they measure a dev kernel whatever
   the flag. The first release run here showed it: riscv64 kernel rows matched O0 to the tick,
   and only `sink_throughput`, a user program, moved. #4108 routes both paths through the profile.
5. The x86_64 release kernel did not finish the bench under icount. It printed both probes and
   then made no progress for an hour, when the run was stopped. One run so far; a second run and
   the cause are pending. The earlier figure of -72 percent for `tss_iomap_switch` at the
   release-equivalent level came from a dev build that the per-package entries still shaped, and
   this revision withdraws it.

### The test suite

Each level ran the whole suite cold, then each architecture's kernel and system legs and the host
leg warm. No level found a kernel bug. Every failure is a test that leans on opt-level 0 or on
debug assertions:

1. Linker-symbol comparisons. `interrupt_stack.rs`, `arch/x86_64/ist.rs` and `smp.rs` compare a
   linker symbol's address to a region the kernel computes. They fail at O1 and up. LLVM assumes
   two distinct globals never share an address and folds the comparison to unequal, so the
   assertion fails while printing two equal numbers. `core::hint::black_box` on one side fixes all
   three (on #4108). No code outside tests compares linker symbols for equality.
2. `ipc_stack_depth` (O1 and up). `cfg(debug_assertions)` chooses its paint margin, a stand-in for
   opt-level: 512 bytes in debug, 64 in release. At O1 to O3 assertions stay on, so the margin is
   512 and every optimized series sits at its floor. With the margin forced to 64, O2 still leaves
   one series at the floor on every architecture (the `call_reply` server REPLY). The release
   branch of this test has never run in any gate, because nothing runs the kernel suite in release.
3. The loader's test binary (O1 and up, aarch64 and x86_64). Optimized, `image_self_checker` has
   two loadable segments, not three, and no read-only one, so
   `a_read_only_segment_is_mapped_read_only` and `the_initial_ramdisk_holds_a_native_executable`
   fail. The cause is loaded_image_check's own level, not fixtures': raising loaded_image_check
   alone to O1 drops the segment, and holding it at O0 with everything else at O1 keeps it. Its
   one read of `RODATA_MARKER` is of an immutable static, which the optimizer folds to a constant,
   so no `.rodata` links. `black_box` on the reference keeps the read, and all three architectures
   then keep a read-only segment at O0 to O3 (on #4108). The tests still assert on the segment.
4. Debug assertions (release only, one test). An earlier run with `--no-fail-fast` found one host
   failure: `address_space_identifier`'s `a_second_free_of_one_identifier_is_caught`, a
   `should_panic` test of a `debug_assert!`. The tree has 43 `debug_assert!` sites in the kernel
   and 23 in crates; all go silent in the shipped build.

With items 1 to 3 patched, O2 passes the whole suite, cold and warm, on all three architectures,
apart from item 2's series with its margin forced.

Wall time, in seconds, from the suite's own timing record (run phases; builds after the slash):

| leg | O0 | O2 |
|---|---|---|
| aarch64 kernel and system, warm | 232 | 152 |
| riscv64 kernel and system, warm | 236 | 147 |
| x86_64 kernel, system, IOMMU and OVMF, warm | 398 / 22 | 257 / 39 |
| host crates, warm | 73 | 57 |
| host crates, cold build and run | 154 | 162 |
| whole suite, cold, end to end | 1723 | 1373 |
| kernel builds within the cold suite | 61 | 99 |

The kernel legs run 34 to 38 percent faster at O2, not nine times faster, because most of a leg is
timer waits, device emulation and image builds. The cold suite as a whole takes 20 percent less.
Optimized builds cost 38 seconds more in the cold suite's kernel builds and 8 in the host leg; a
cold build of the user-space ramdisk alone is pending.

### What else moves

- The 21 per-package entries. At a dev base of O2, the eighteen at opt-level 2 are no-ops. The
  three at opt-level 1 are not: they would lower fixtures, user_mode_runtime and moho_abi below the
  base, so deleting them raises those packages to 2.
- `SUITE_PAGE_FRAME_BUDGET` (25025). Holds, and gains room: the frames the system leg never
  returns fall with optimization on every architecture. The aarch64 margin at O0 is 24 frames.
- fastpath-footprint and build-is-reproducible. Both already build `--release`; unaffected.
- Kani and Miri. Neither depends on opt-level: Kani compiles its own model and Miri interprets
  MIR. Both follow `cfg(debug_assertions)` from the profile, so they move only if assertions go
  off.
- Panic quality. Unchanged in what the kernel prints: `[PANIC]`, the location and the message
  come from `PanicInfo` at every level.
- Debugger stepping under `xtask gdb` at O1 and O2: pending.
- Mutation testing. The workflow derives each mutant's timeout as five times its package's
  baseline test time, with a floor of 20 seconds. Faster optimized tests shorten the derived
  timeouts in step, so the timeout column of the mutation baseline may shift. Not yet measured.

### What option C costs beyond a baseline save

The icount numbers have readers outside the bench. A release bench re-saves all three baselines,
and `bench/attributions.tsv` (802 lines) loses continuity across that save. The toolchain-bump
workflow and `metrics.yml`'s drift check (`helpers/baseline_drift.py`) act on the numbers. About
twenty record notes and `notes/benchmarks.md` cite tick counts, and each would need a line saying
which profile it counted. The rule in `xtask/src/bench.rs` that release never runs under icount
would need rewriting.

## Options

Each option's cost is what this measurement found, not an estimate.

- A. Keep dev at opt-level 0. No work. The gate keeps counting mostly unoptimized code and keeps
  absorbing compiler drift of ten to twenty percent as baseline saves. It never runs the release
  branch of `ipc_stack_depth` or any other release-only path.
- B1. Dev at opt-level 1, debug assertions, overflow checks and debuginfo kept. The same fixes as
  B2. Numbers pending.
- B2. Dev at opt-level 2, the same kept. Fix the three symbol comparisons and the loader fixture.
  Rework `ipc_stack_depth`'s margin so it keys on what it measures rather than on
  `debug_assertions`. Delete the 21 per-package entries. Save one bench baseline per architecture.
  Measured: 34 to 38 percent less run time per kernel leg, 20 percent off the cold suite.
- C. The gating bench on a release build, the suite unchanged. Fix the two bench paths that ignore
  the profile, find why the x86_64 release kernel stalls under icount, and pay the costs above.
- D. B then C.

## Recommendation

Pending the remaining runs, the direction is D with B first, and the choice between O1 and O2
waits on the O1 numbers. The seven questions:

1. What else did this consider? A loses because the gate measures a build nobody runs. C alone
   loses because the suite keeps missing the optimizer-sensitive failures above. B alone leaves the
   bench off the shipped build.
2. What does this tree do in the analogous case? fastpath-footprint and build-is-reproducible
   already build the shipped profile because that is what they are about; milestone 750 turned on
   overflow checks in release for the same reason, to check what ships.
3. Prior art, from sources read on 2026-11-26. Linux offers only `-O2` and `-Os`
   ([Makefile](https://github.com/torvalds/linux/blob/ebb7a8dc1e74/Makefile#L938-L949),
   [init/Kconfig](https://github.com/torvalds/linux/blob/ebb7a8dc1e74/init/Kconfig#L1465)); Rust
   builds at `-Copt-level=2` with debug assertions set apart by
   [RUST_DEBUG_ASSERTIONS](https://github.com/torvalds/linux/blob/ebb7a8dc1e74/lib/Kconfig.debug#L3616).
   seL4 sets optimization, default `-O2`, apart from `KernelDebugBuild`, which carries symbols and
   assertions ([config.cmake](https://github.com/seL4/seL4/blob/78b0c34efe12/config.cmake#L234-L304)).
   Its benchmarks apply release settings
   ([sel4bench](https://github.com/seL4/sel4bench/blob/18f9d5f079bc/settings.cmake#L69-L70),
   [seL4_tools](https://github.com/seL4/seL4_tools/blob/6493e0c6fab3/cmake-tool/helpers/application_settings.cmake#L93-L115)).
   [Fuchsia](https://fuchsia.dev/fuchsia-src/development/build/build_system/fuchsia_build_system_overview)
   calls its debug build not suitable for performance testing and its release build the one for
   benchmarking. [rustc-perf](https://github.com/rust-lang/rustc-perf/blob/463fb3a255f7/collector/README.md#L65-L68)
   counts instructions because they vary least, and
   [measures](https://github.com/rust-lang/rustc-perf/blob/463fb3a255f7/docs/glossary.md) the
   compiler artifacts built from merged commits. None of the four benchmarks an unoptimized build.
4. Is the premise true? With two corrections: there are 21 per-package entries, three of them at
   opt-level 1, and board images ship a debug user space with the release kernel.
5. What does each cost? In Options above.
6. How reversible? B is a two-way door: a profile is two lines and a baseline is one save. C is
   less so, because the workflows and notes above act on the numbers.
7. Would we still choose it at equal cost? Yes. The recommendation is about measuring the
   shipped build, not about effort; B even lowers the suite's run time.

## Follow-on

- **Recorded.** The choice among the options is calef's, once the pending runs fill this block.
- **Recorded.** The x86_64 release kernel's stall under icount, and the two bench paths that
  ignore `--release` on main, need fixes before option C can start.

## Index row

What building the test suite and the gating icount bench optimized would cost and find, measured
at opt-level 0 and 2 and a release bench on aarch64 so far, with options for calef; no profile
changed.
