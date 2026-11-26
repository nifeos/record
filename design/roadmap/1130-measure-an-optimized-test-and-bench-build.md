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
release kernel with a debug user-space archive; milestone 797 (release userspace in board images)
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
untouched tree, with its 21 entries, is the O0 column. The rel column is dev made
release-equivalent: opt-level 3, debug assertions off, debuginfo off, 16 codegen units,
incremental off, overflow checks on. Two levels ran at a time, so wall times carry noise of
perhaps ten percent; the icount rows carry none.

A true `--release` bench of aarch64 matches the rel column to within one instruction on every row,
so rel stands for the shipped profile here. The same run on riscv64 and x86_64 is open work (see
Follow-on).

### The gating benchmark

Every row ran twice at every level, and the two runs are identical to the instruction. Every
optimized run fails `--check`, as it must, since the baseline holds opt-level 0 counts. Selected
rows, as instructions at O0 and the change from O0 (nifeos/nife#4108 holds every row):

| row | arch | O0 | O1 | O2 | O3 | rel |
|---|---|---|---|---|---|---|
| ipc_rtt | aarch64 | 803253 | -85% | -89% | -89% | -91% |
| call_reply | aarch64 | 836441 | -83% | -89% | -89% | -91% |
| spawn_reap | aarch64 | 183437 | -63% | -65% | -65% | -66% |
| map_new | aarch64 | 14628 | -48% | -50% | -50% | -50% |
| coremark | aarch64 | 17739199 | -90% | -90% | -92% | -92% |
| null_system_call | aarch64 | 238750 | -41% | -45% | -45% | -45% |
| ipc_rtt_el0 | aarch64 | 7978125 | -79% | -86% | -86% | -88% |
| ipc_rtt | riscv64 | 129381 | -86% | -88% | -88% | -90% |
| rfence_self | riscv64 | 5934 | -11% | -11% | -10% | -10% |
| null_system_call | riscv64 | 47400 | -26% | -24% | -24% | -26% |
| ipc_rtt_el0 | riscv64 | 1321739 | -82% | -84% | -85% | -87% |
| ipc_rtt | x86_64 | 13751053 | -86% | -89% | -89% | -91% |
| tss_iomap_switch | x86_64 | 19558051 | -68% | -91% | -91% | -72% |
| coremark | x86_64 | 263128262 | -87% | -87% | -89% | -89% |

Findings:

1. At opt-level 0 the bench counts mostly the compiler's unoptimized code, not the kernel's paths.
   Eight to nine instructions in ten on every IPC row are code that the shipped kernel does not
   execute.
2. The rows do not move together, so an opt-level 0 regression does not predict a shipped one.
   `rfence_self` falls 10 percent (it is firmware-bound), `map_new` about half, IPC nine tenths.
3. O1 against O2. Across every row of every architecture, O1 gets on average 96 percent of O2's
   reduction from O0. What it leaves still counts: O1's IPC rows hold 16 to 45 percent more
   instructions than O2's, and its EL0 rows on aarch64 up to 57 percent more. Its
   `tss_iomap_switch` holds 3.8 times O2's count.
4. O2 against rel. O2's IPC rows still hold 20 to 30 percent more instructions than the shipped
   profile's. O3 is within about five percent of O2 on every row but CoreMark, so most of that gap
   is what debug assertions and the dev profile's other settings cost on those paths.
5. `tss_iomap_switch` on x86_64 differs between O3 (-91%) and rel (-72%), deterministically, with
   every per-package entry deleted. The shipped profile spends 3.3 times O3's instructions on that
   path. Nothing explains it yet; only a release-profile bench shows it.
6. Compiler drift at opt-level 0 is large and at O1 and O2 almost nil. One toolchain change,
   nightly 2026-11-17 to 2026-11-18, measured on the same tree at each level:

   | level | aarch64 | riscv64 | x86_64 |
   |---|---|---|---|
   | O0 | -10.8 to -19.4% | -1.7 to -16.7% | -12.7 to -16.6% |
   | O1 | -0.01 to +0.25% | -0.06 to +0.08% | 0.00% |
   | O2 | -0.10 to +0.01% | -0.06 to +0.15% | -0.06 to 0.00% |

   The O0 row matches the 2026-11-18 baseline re-save (nifeos/nife@1547eb2af9) within half a point. The
   toolchain-bump workflow restamps only when every row moves under 0.5 percent and all under 2
   percent together; those bounds came from O0 drift. At O1 and O2 this toolchain change sits well
   inside them, though one change is a sample of one.
7. On main, `bench --release` builds a release kernel only on aarch64. The riscv64 and x86_64 paths
   call cargo directly and boot `target/<triple>/debug/kernel`, so they measure a dev kernel
   whatever the flag. #4108 routes both through the profile for the measurement.
8. With that change, the x86_64 release kernel printed both bench probes under icount and then made
   no progress for an hour, in one run. The release-equivalent dev build of the same path finishes.

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
   512 and every optimized series sits at its floor. With the margin forced to 64, series still
   sit at the floor: up to three at O1, one at O2 and O3 (the `call_reply` server REPLY), and one
   to three at rel. The release branch of this test has never run in any gate, because nothing
   runs the kernel suite in release.
3. The loader's test binary (O1 and up, aarch64 and x86_64). Optimized, `image_self_checker` has
   two loadable segments, not three, and no read-only one, so
   `a_read_only_segment_is_mapped_read_only` and `the_initial_ramdisk_holds_a_native_executable`
   fail. The cause is loaded_image_check's own level, not fixtures': raising loaded_image_check
   alone to O1 drops the segment, and holding it at O0 with everything else at O1 keeps it. Its
   one read of `RODATA_MARKER` is of an immutable static, which the optimizer folds to a constant,
   so no `.rodata` links. `black_box` on the reference keeps the read, and all three architectures
   then keep a read-only segment at O0 to O3 (on #4108). The tests still assert on the segment.
4. Debug assertions (rel only, one test). The host leg stops on
   `address_space_identifier`'s `a_second_free_of_one_identifier_is_caught`, a `should_panic` test
   of a `debug_assert!`. The tree has 43 `debug_assert!` sites in the kernel and 23 in crates; all
   go silent in the shipped build.

With items 1 to 3 patched, O1, O2 and O3 pass the whole suite, cold and warm, on all three
architectures, apart from item 2's series with its margin forced. At rel the kernel and system legs
pass on all three.

Wall time in seconds, from the suite's own timing record (run phases):

| leg | O0 | O1 | O2 | O3 | rel |
|---|---|---|---|---|---|
| aarch64 kernel and system, warm | 232 | 144 | 152 | 125 | 129 |
| riscv64 kernel and system, warm | 236 | 144 | 147 | 129 | 128 |
| x86_64 kernel, system, IOMMU and OVMF, warm | 399 | 277 | 257 | 249 | 272 |
| host crates, warm | 73 | 69 | 57 | 57 | stops at item 4 |
| host crates, cold build and run | 154 | 150 | 162 | 149 | stops at item 4 |
| whole suite, cold, end to end | 1723 | 1260 | 1373 | 1252 | stops at item 4 |

Build cost, in seconds:

| build | O0 | O1 | O2 |
|---|---|---|---|
| kernel builds within the cold suite, all legs | 61 | 80 | 99 |
| user programs (the ramdisk), cold, aarch64 | 7 | 7 | 9 |
| user programs, cold, riscv64 | 7 | 9 | 9 |
| user programs, cold, x86_64 | 6 | 8 | 9 |

The kernel legs run 31 to 46 percent faster optimized, not nine times faster, because most of a
leg is timer waits, device emulation and image builds. O1 and O2 are within noise of each other on
leg time. A cold O2 suite pays about 38 seconds more kernel build and two or three seconds more
per architecture for the user programs, against more than five minutes saved in run time.

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
- Debugger stepping. Under `cargo xtask gdb` on aarch64, `break kernel_main` and five `next`
  steps show source lines at O0, O1 and O2. Optimized, the breakpoint lands one statement in, the
  first step goes back one line, and the `boot_info_pointer` argument is gone. A backtrace there ends
  at `kernel_main` at every level, as it is the first Rust frame.
- Mutation testing. A sample of two host packages, coremark and capability_manifest_note, ran
  `script/mutation -p <package>` at O0 (the tree as it is) and at O2 (every per-package entry
  deleted), at the script's two jobs and four test threads:

  | package | level | mutants | caught | missed | timeout | unviable | wall | mutant builds | mutant tests |
  |---|---|---|---|---|---|---|---|---|---|
  | coremark | O0 | 109 | 106 | 2 | 1 | 0 | 56 s | 44 s | 45 s |
  | coremark | O2 | 109 | 106 | 2 | 1 | 0 | 63 s | 56 s | 45 s |
  | capability_manifest_note | O0 | 463 | 311 | 4 | 3 | 145 | 345 s | 527 s | 147 s |
  | capability_manifest_note | O2 | 463 | 311 | 4 | 3 | 145 | 411 s | 668 s | 136 s |

  Build and test columns sum each phase over all mutants, so they exceed the wall time of a
  two-job run. Optimization changes nothing that mutation testing finds here: both levels generate
  the same mutants, and every mutant lands in the same outcome, caught, missed, timeout and
  unviable alike. The timeouts are the same mutants at both levels (`-=` to `/=` in coremark's
  `list_work`, `+=` to `*=` in three of capability_manifest_note's encoders); each runs out the
  20-second floor, since both packages' baseline tests take under a second, so a hang stays a hang
  at O2 as expected. O2 costs 12 and 19 percent more wall time, and the cause is the rebuild each
  mutant pays: the mutated package and its test binary recompile at the profile's level, and those
  builds take 27 percent longer at O2 in both packages (about 1.1 to 1.4 seconds a mutant for
  capability_manifest_note). Test time does not offset it, because these tests are already short;
  capability_manifest_note's tests ran 8 percent faster at O2, coremark's the same. A package whose
  tests are long against its build would gain, and these two do not. Two packages are a sample, not
  the census.

### What option C costs beyond a baseline save

The icount numbers have readers outside the bench. A release bench re-saves all three baselines,
and `bench/attributions.tsv` (802 lines) loses continuity across that save. The toolchain-bump
workflow and `metrics.yml`'s drift check (`helpers/baseline_drift.py`) act on the numbers. About
twenty record notes and `notes/benchmarks.md` cite tick counts, and each would need a line saying
which profile it counted. The rule in `xtask/src/bench.rs` that release never runs under icount
would need rewriting, and the two bench paths of finding 7 would need the profile.

## Options

Each option's cost is what this measurement found, not an estimate.

- A. Keep dev at opt-level 0. No work. The gate keeps counting mostly unoptimized code and keeps
  absorbing compiler drift of ten to twenty percent as baseline saves. It never runs the release
  branch of `ipc_stack_depth` or any other release-only path.
- B1. Dev at opt-level 1, debug assertions, overflow checks and debuginfo kept, with B2's fixes.
  Run time and drift match B2. It counts 16 to 57 percent more instructions than O2 on the IPC
  and EL0 rows and misses most of the `tss_iomap_switch` change, so its bench stays further from
  what ships. Its host leg is 12 seconds slower warm.
- B2. Dev at opt-level 2, the same kept. Fix the three symbol comparisons and the loader fixture.
  Rework `ipc_stack_depth`'s margin so it keys on what it measures rather than on
  `debug_assertions`. Delete the 21 per-package entries. Save one bench baseline per architecture.
  Measured: kernel legs 34 to 38 percent faster, the cold suite 20 percent faster, toolchain drift
  under a quarter of a percent. Mutation testing finds the same results at 12 to 19 percent more
  wall time, unless `script/mutation` holds its own build at opt-level 0.
- C. The gating bench on a release build, the suite unchanged. Route the two bench paths through
  the profile, find why the x86_64 release kernel stalls under icount, and pay the costs above.
  O2 counts 20 to 30 percent more IPC instructions than it does, and only C sees the real
  `tss_iomap_switch`.
- D. B2 then C.

## Recommendation

D, with B2 first. B2 alone takes most of the gain: the bench stops counting unoptimized code,
toolchain drift drops from ten to twenty percent to under a quarter of a percent, and the suite
runs faster. Mutation testing finds the same mutants and outcomes at O2 and pays 12 to 19 percent
more wall time for the rebuild each mutant makes; that cost does not change the recommendation,
because the B2 lane can hold `script/mutation` at opt-level 0 with one cargo profile override,
since the level does not change what it finds. C then moves the bench onto the shipped profile, once its two blockers are fixed. The
seven questions:

1. What else did this consider? A loses because the gate measures a build nobody runs and pays a
   baseline save at every nightly. B1 loses to B2 at the same run time and the same drift, because
   it counts more code that does not ship. C alone loses because the suite keeps missing the
   optimizer-sensitive failures above, and C cannot start until the x86_64 stall has a cause.
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
   compiler artifacts built from merged commits. None of the four benchmarks an unoptimized build;
   Linux and seL4 are the precedent for B2's opt-level 2 with assertions kept apart.
4. Is the premise true? With two corrections: there are 21 per-package entries, three of them at
   opt-level 1, and board images ship a debug user space with the release kernel.
5. What does each cost? In Options above, measured.
6. How reversible? B2 is a two-way door: a profile is two lines and a baseline is one save. C is
   less so, because the workflows and notes above act on the numbers.
7. Would we still choose it at equal cost? Yes. The recommendation is about measuring the
   shipped build, not about effort; B2 even lowers the suite's run time.

## Follow-on

- **Recorded.** The choice among the options is calef's, in this block's Options and
  Recommendation. On D, a B2 lane carries the four test fixes, the profile change and the
  per-package deletions, and a C lane follows.
- **Recorded.** Open work before C: the x86_64 release kernel's stall under icount, the riscv64
  true-release bench, and the two bench paths that ignore `--release` on main.
- **Recorded.** Nothing explains the `tss_iomap_switch` difference between O3 and rel on x86_64
  yet. One icount run per setting bisects it over the five settings that separate the two.
- **Recorded.** Whether `script/mutation` follows the dev profile to O2 or holds opt-level 0 is the
  B2 lane's to settle; the two-package sample shows no difference in outcomes and a 12 to 19
  percent cost at O2.

## Index row

What building the test suite and the gating icount bench optimized would cost and find, measured
at opt-level 0 to 3 and release on three ISAs, with toolchain drift, options and a recommendation
for calef; no profile changed.
