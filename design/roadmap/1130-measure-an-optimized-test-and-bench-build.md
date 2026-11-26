---
status: IN-PROGRESS
raised: 2026-11-26
branch: milestone/1130-measure-an-optimized-test-and-bench-build
milestone_dependencies: none
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: no
---
# 1130. Measure an optimized build of the test suite and the gating benchmark

Raised 2026-11-26 (UTC) by calef. The number 1130 is provisional until the integrator mints it at
merge; the title and the slug are drafts. The branch that writes this block is
`milestone/1130-measure-an-optimized-test-and-bench-build`.

## Why

The shipped kernel builds with `--release`, at opt-level 3. `script/test` and the gating
`script/bench --check` build cargo's dev profile, at opt-level 0, with seventeen crates raised one
at a time. So the build that gates every merge is not the build a customer boots. This is a
measurement, as milestone 744 (measure the kernel's overflow checks) was for milestone 750: it
changes no profile, and the choice it prepares is calef's.

## What is measured

1. The test suite at opt-level 1, 2 and 3 and at a release-equivalent profile, on aarch64, riscv64
   and x86_64: build and run time against the opt-level 0 suite, and every failure, hang or change.
2. The icount bench at each level, every row against the opt-level 0 build, each run twice.
3. What else moves: the frame budget, the fast-path footprint gate, Kani, Miri, debug assertions,
   panic messages, the reproducible-build check, and the seventeen per-crate entries.
4. Prior art: Linux, seL4, Fuchsia and the Rust compiler's own performance suite.
