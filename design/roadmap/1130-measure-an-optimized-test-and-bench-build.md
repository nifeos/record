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
on, which is the one thing the root `[profile.release]` sets. `script/test` and the gating
`script/bench --check` build cargo's dev profile at opt-level 0, with seventeen packages raised to
opt-level 2 one at a time in the root `Cargo.toml`. So the build that gates every merge is not the
build anyone boots. This is a measurement, as milestone 744 (measure the kernel's overflow checks)
was for milestone 750 (overflow checks in the shipped build): it changes no profile, and the
choice it prepares is calef's.

No milestone or decision chose dev for the gate on its own merits. Milestone 25 (cross-OS
performance comparison) added `bench --release` in nifeos/nife@2ce5d1a97 on 2026-07-25, as a
statistical, hardware-accelerated path for magnitudes next to release Linux. It kept everything
else on dev, its message says for fast rebuilds and debuginfo for the tests.
`xtask/src/bench.rs` still says why release never gates: it changes instruction counts, so it never
runs under icount. That says the icount baseline holds dev counts; it gives no reason dev is the right
thing to count.

Reuse: none exists; the measurement uses the suite's own `script/test`, `script/bench --check` and
its timing record unchanged, with cargo's profile environment overrides. A search of nifeos/nife
`xtask/` and `script/` for an existing optimized test path found only `bench --release`.

## What was measured

All runs were on one 80-core x86_64 Linux host under TCG. The tree was nifeos/nife main at the
lane's base plus the measurement branch (nifeos/nife#4108, a draft not meant to merge). Cargo's
profile environment overrides on the dev profile set each level, so the suite's own scripts ran
unchanged. The level called rel is dev made release-equivalent: opt-level 3, debug assertions off, debuginfo off,
16 codegen units, incremental off; overflow checks stay on, as in the shipped profile. Host load
stayed between 11 and 17 on 80 cores; a second lane ran its own suite at the same time, so wall
times carry noise of perhaps ten percent and the icount rows carry none.

### The gating benchmark

Every row, every level, every architecture, run twice: the two runs are identical to the
instruction at every level, so icount stays deterministic when optimized. Every optimized run fails
`--check`, as it must, since the baseline holds opt-level 0 counts. Selected rows (instructions; nifeos/nife#4108
holds the full tables):

| row | arch | O0 | O1 | O2 | O3 | rel |
|---|---|---|---|---|---|---|
| ipc_rtt | aarch64 | 803253 | -87% | -89% | -89% | -91% |
| call_reply | aarch64 | 850878 | -85% | -89% | -89% | -91% |
| spawn_reap | aarch64 | 183389 | -63% | -65% | -65% | -66% |
| map_new | aarch64 | 14628 | -48% | -50% | -50% | -50% |
| coremark | aarch64 | 17739199 | -90% | -90% | -92% | -92% |
| ipc_rtt_el0 | aarch64 | 8293317 | -81% | -87% | -87% | -88% |
| ipc_rtt | riscv64 | 129380 | -85% | -88% | -88% | -90% |
| rfence_self | riscv64 | 5935 | -11% | -11% | -10% | -10% |
| null_system_call | riscv64 | 60000 | -43% | -41% | -41% | -44% |
| ipc_rtt | x86_64 | 13751053 | -87% | -89% | -89% | -91% |
| tss_iomap_switch | x86_64 | 19558051 | -68% | -92% | -92% | -72% |
| coremark | x86_64 | 263128262 | -87% | -87% | -89% | -89% |

Findings:

1. At opt-level 0 the bench counts mostly the compiler's unoptimized code, not the kernel's paths.
   Eight to nine instructions in ten on every IPC row are code that the shipped kernel does not
   execute. The 2026-11-18 baseline save shows the cost: one nightly moved every row 13 to 17
   percent, CoreMark with them, and the note had to explain it as code generation.
2. The rows do not move together, so an opt-level 0 regression does not predict a shipped one.
   `rfence_self` falls 10 percent (it is firmware-bound), `map_new` half, IPC nine tenths.
3. `tss_iomap_switch` on x86_64 is -92% at O2 and O3 but only -72% at rel, deterministically. The
   release-equivalent build does something on that path the O3 build does not; nothing explains it
   yet, and only a release bench would have shown it.

### The test suite

Each level ran the host leg and each architecture's kernel and system legs, one architecture at a
time. No level found a kernel bug. Every failure is a test that leans on opt-level 0 or on debug
assertions:

1. **Linker-symbol comparisons.** `interrupt_stack.rs`,
   `arch/x86_64/ist.rs` and `smp.rs` compare a linker symbol's address to a region the kernel
   computes. They fail at O1 and up. LLVM assumes two distinct globals never share an address and folds the comparison to
   unequal, so the assertion fails while printing two equal numbers. `core::hint::black_box` on one
   side fixes all three (on #4108). No code outside tests compares linker symbols for equality.
2. **`ipc_stack_depth` (O1 and up, and rel).** `cfg(debug_assertions)` chooses its
   paint margin, a stand-in for opt-level: 512 bytes in debug, 64 in release. At O1 to
   O3 assertions stay on, so the margin is 512 and every optimized series is at its floor. With the
   margin forced to 64, one or two series are still at the floor on every architecture. They are the two
   `send_receive` SEND series at O1, the `call_reply` server REPLY at O2, O3 and rel;
   at rel on riscv64 all three are. The rel run
   matters most: it is the shipped profile, and this test's release branch has never run in any
   gate, because nothing runs the kernel suite in release. It fails there today.
3. **The loader's test binary (O1 and up, aarch64 and x86_64).** Optimized, the binary the loader
   tests inspect has no read-only segment and fewer than three segments, so
   `a_read_only_segment_is_mapped_read_only` and `the_initial_ramdisk_holds_a_native_executable`
   fail on a fixture that changed shape. riscv64 keeps its `.rodata`.
4. **Debug assertions (rel only, one test).** With `--no-fail-fast` the whole host leg has one
   failure: `address_space_identifier`'s `a_second_free_of_one_identifier_is_caught`, a
   `should_panic` test of a `debug_assert!`. The kernel and system legs pass on aarch64, riscv64
   and x86_64 at rel with items 1 to 3 patched. The tree has 43 `debug_assert!` sites in the
   kernel and 23 in crates; all go silent in the shipped build.

No level hung. With items 1 to 3 patched locally, O1, O2, O3 and rel pass every kernel and system
leg on all three architectures.

Wall time, in seconds, for the run phases of each leg (from the suite's own timing record; the
builds are separate):

| leg | O0 | O1 | O2 | O3 | rel |
|---|---|---|---|---|---|
| aarch64 kernel and system | 254 | 143 | 144 | 154 | 147 |
| riscv64 kernel and system | 299 | 146 | 143 | 149 | 163 |
| x86_64 kernel, system and IOMMU | 331 | 195 | 196 | 202 | 178 |
| x86_64 under OVMF | 147 | 90 | 92 | 83 | 86 |
| host crates, warm | 78 | 57 | 57 | 56 | n/a |
| host crates, cold build and run | 147 | 167 | 171 | 160 | n/a |

The whole suite at O0 took 1399 seconds end to end. The kernel legs run 37 to 52 percent faster
optimized. They do not run nine times faster, because
most of a leg's time is timer waits, device emulation and the image builds, not kernel
instructions. A cold build of the riscv64 kernel and system test binaries takes 16 to 19 seconds
at O0 and 25 to 30 at O3, about ten seconds more per architecture.

### What else moves

- `SUITE_PAGE_FRAME_BUDGET` (25025). Holds, and gains room. The frames the system leg never
  returns fall with optimization: aarch64 25001 at O0 to 24590 at O1 and 24574 at rel; riscv64
  24645 to 24338 and 24304; x86_64 14490 to 14259 and 14234. The aarch64 margin at O0 is 24
  frames.
- fastpath-footprint and build-is-reproducible. Both already build `--release`; unaffected.
- Kani and Miri. Neither depends on opt-level: Kani compiles its own model and Miri interprets
  MIR. Both follow `cfg(debug_assertions)` from the profile, so they move only if assertions go
  off.
- Panic quality. Unchanged in what the kernel prints: `[PANIC]`, the location and the message
  come from `PanicInfo` at every level. The kernel keeps no frame pointers and scans the stack
  conservatively; inlining shortens what that scan can name. Stepping in a debugger with locals
  optimized out was not measured.
- The seventeen per-package entries. At a dev base of opt-level 2 all seventeen are no-ops,
  and deleting them changes nothing. At O1 they still raise; at O3 they lower those crates to 2.

## Options

Each option's cost is what this measurement found, not an estimate.

- A. Keep dev at opt-level 0. No work. The gate keeps counting mostly unoptimized code and keeps
  absorbing compiler drift as baseline saves. It never runs the release branch of
  `ipc_stack_depth` or any other release-only path.
- B. Dev at opt-level 2, debug assertions, overflow checks and debuginfo kept. Fix the three
  symbol comparisons. Rework `ipc_stack_depth`'s margin so it keys on what it measures rather than
  on `debug_assertions`, with its floor below the shallowest optimized series. Make the loader
  tests assert on the segments they need rather than a count. Delete the seventeen
  per-package entries. Save one bench baseline per architecture. About ten seconds more build per
  architecture, 37 to 52 percent less run time per leg.
- C. The gating bench on a release build, the suite unchanged. Build the bench kernel with the
  shipped profile under icount and save one baseline per architecture. The bench then counts what
  ships, including the `tss_iomap_switch` difference. The suite keeps every cost of A.
- D. Both B and C. The suite at opt-level 2 with assertions, and the bench on the shipped
  profile. Both need the `ipc_stack_depth` and loader fixes, since the bench kernel's
  release build and the suite would then share the paths those tests describe.

## Recommendation

D, in two lanes: B first, because its test fixes are what make a release-profile kernel testable
at all, then C. The seven questions:

1. What else did this consider? A loses because the gate measures a build nobody runs: nine in ten
   counted instructions are opt-level 0 code, and the shipped profile's own branch of a kernel test
   fails unseen. B alone loses because the bench would still not be the shipped build (rel differs
   from O3 on `tss_iomap_switch`). C alone loses because the suite would keep missing the
   optimizer-sensitive failures above and pay its slower legs.
2. What does this tree do in the analogous case? fastpath-footprint and build-is-reproducible
   already build the shipped profile because that is what they are about; milestone 750 turned on
   overflow checks in release for the same reason, to check what ships.
3. **Prior art, read.** Linux builds only at `-O2` or `-Os` (`CONFIG_CC_OPTIMIZE_FOR_PERFORMANCE`
   or `_SIZE`; Rust at `-Copt-level=2`); it has no `-O0` build, and its debug options are separate
   Kconfig switches. seL4 makes optimization (default `-O2`) and debugging
   (`KernelDebugBuild`, symbols and assertions) independent settings, and its binary verification
   is against `-O2`. Fuchsia's `fx set` documents the debug build as not suitable for performance
   testing and the release build as the one for benchmarking. rustc-perf counts instructions
   because they vary least, and measures the compiler's distributed artifacts, the build that
   ships. None of the four benchmarks an unoptimized build; seL4 is the precedent for B's split of
   assertions from optimization.
4. Is the premise true? Yes, with one correction: there are seventeen per-package entries, not
   about twenty. Shipped images are `--release`; the root `[profile.release]` sets only
   `overflow-checks`; `script/test` and `script/bench --check` build dev at opt-level 0.
5. What does each cost? In Options above, measured: three one-line test fixes, two test
   reworks, one baseline save per architecture per profile change, about ten seconds of build per
   architecture, and 37 to 52 percent less run time per kernel leg.
6. How reversible? A two-way door. A profile is two lines and a baseline is one save; nothing
   outside the tree acts on the icount numbers. Published comparisons with Linux already come from
   `bench --release`, so none goes stale.
7. Would we still choose it at equal cost? Yes. The recommendation is about measuring the
   shipped build, not about effort; B even lowers the suite's run time.

## Follow-on

- **Recorded.** The choice among A to D is calef's, in this block's Options and Recommendation.
  On D, a B lane carries the five test fixes, the profile change and the per-package deletions,
  and a C lane carries the bench profile and the baseline saves.
- **Recorded.** Nothing explains the `tss_iomap_switch` difference between O3 and rel on x86_64
  yet. One icount run per setting bisects it over the five settings that separate the two.

## Index row

What building the test suite and the gating icount bench optimized would cost and find, measured
at opt-level 1, 2, 3 and release on three ISAs, with options and a recommendation for calef; no
profile changed.
