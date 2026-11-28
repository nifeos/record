# What the review read and ran

An appendix to [the milestone](../1161-counter-frequency-contract-release-review.md).

## The crate

`partsfoundry/counter_frequency_contract` at `4decec9d5e43054c88a6d5e6f5254b37906db92e`, version
0.1.0-pre.2, the tag `v0.1.0-pre.2`, a fresh clone of `main`. The census of milestone 1129 (the
combine review) counted the same commit. The lane read in full: `Cargo.toml`, `README.md`,
`CHANGELOG.md`, `docs/stranger-test.md`, `src/lib.rs` (351 lines, its tests and its two Kani
harnesses included), `.cargo/mutants.toml` and `.github/mutants-exempts`. It read the names of the
two patches in `falsifications/` and searched the other files for one word.

## The commands

Each command below ran against the `counter_frequency_contract` clone on a Linux x86_64 host, with
rustc 1.100.0 and the build output kept in the lane's scratch area. `git status --short` showed the
clone clean afterward.

- `cargo build` passes.
- `cargo test` passes: 7 unit tests and 4 doctests.
- `RUSTDOCFLAGS="-D warnings" cargo doc --no-deps` passes with no warning.
- `cargo clippy --all-targets -- -D warnings` passes.
- The bare-metal library build, `cargo build --lib --target <target>`, passes for
  `x86_64-unknown-none`, `aarch64-unknown-none-softfloat` and `riscv64imac-unknown-none-elf`, the
  three targets the README names and the three bare targets installed on the host.
- `cargo package --list --allow-dirty` lists 38 files, 20 of them under `.github/`, `.githooks/` or
  named `.gitignore` (P2-3).
- `cargo +nightly miri test --lib` passes all 7 tests and warns once about an integer-to-pointer
  cast. With `MIRIFLAGS=-Zmiri-strict-provenance` the first test stops at that cast with
  "integer-to-pointer casts and `ptr::with_exposed_provenance` are not supported" (P0-1).
- `grep -n '# Panics\|# Errors\|# Examples\|# Safety' src/lib.rs` prints `# Examples` at lines 64,
  114 and 179 and `# Safety` at lines 147 and 162, the second on a private function (P1-2).
- `grep -n 'must_use\|const fn' src/lib.rs` prints one line, the `const unsafe fn new` (P1-3, P2-2).
- The crate declares no features, so there is one feature combination.

A scratch program that depends on the crate by path and on `raw-cpuid` at `=11.6.0` printed:

- `build_page(0)` read through `hertz()` is `Some(0)`, and `1_000_000_000 / 0` from it panics with
  "attempt to divide by zero" (P0-2).
- `{:?}` of the page is `CounterFrequencyPage { base: 0x7ffedc9292f0 }` (P1-4).
- A page built for 1,000,000 hertz with its eighth byte set to `2` reads `None`, as a zeroed frame
  does (P0-5).
- `unsafe { CounterFrequencyPage::new(0) }` compiles, and the type is 8 bytes (P0-1).
- `raw_cpuid::CpuId::new().get_tsc_info().and_then(|t| t.tsc_frequency())` is `None` on this
  host.

A second scratch crate, `no_std`, asserted in a `const` that `PAGE_VIRTUAL_ADDRESS` equals
`0x0000_7000_0000_0000`. It builds for `x86_64-unknown-none` and `aarch64-unknown-none-softfloat`
and fails for `riscv64imac-unknown-none-elf` (P0-3).

## The search for a comparator

On 2026-11-26 (UTC), `https://crates.io/api/v1/crates?q=<words>&sort=recent-downloads&per_page=8`
for each of: "counter frequency", "timebase", "tsc frequency", "vdso", "pvclock", "timer
frequency", "cntfrq", "shared page", "time counter no_std" and "clocksource". No result publishes
a page that carries a counter's rate to a process. The results that hand a program a counter rate
became the neighbors. The lane measured `minstant` 0.1.7 (271,744 downloads in 90 days), `vdso`
0.2.2 (2,110) and `fdt` 0.1.5 (471,091) and set them aside. The first calibrates as `quanta`
does, the second resolves symbols in Linux's vDSO, and the third parses a device tree and has its
own release review.

## The neighbors read

The lane downloaded four `.crate` files from `static.crates.io`, at the versions the block's
table gives, and unpacked each apart from the others.

- `raw-cpuid` 11.6.0, `src/lib.rs`, `TscInfo` (line 5538): private fields, a `Debug` written by
  hand that prints the derived rate, and `tsc_frequency(&self) -> Option<u64>`, which returns
  `None` when the crystal rate, the numerator or the denominator is zero. `Cargo.toml` gives the
  features `std`, `serialize`, `display` and `cli`.
- `quanta` 0.13.0, `src/lib.rs`: a private `Calibration` of `scale_factor` and `scale_shift`, kept
  in a `OnceLock` for the process, made by a loop bounded at 200 milliseconds
  (`MAXIMUM_CAL_TIME_NS`); `Clock::delta_as_nanos`, which calls `mul_div_po2_u64` (a 128-bit
  multiply and a shift). It needs `std`. Its features are `mock` and `flaky_tests`, both on by
  default.
- `aarch64-cpu` 12.0.0, `src/registers/cntfrq_el0.rs`: a unit struct `Reg` that implements the
  `tock_registers` `Read` and `Write` traits with `DataType = u64`, and a constant `CNTFRQ_EL0`.
  No check of the value. One feature, `critical-section-single-core`.
- `tick_counter` 0.4.5, `src/lib.rs`: `frequency() -> (u64, TickCounterFrequencyBase)`, which
  reads `cntfrq_el0` on aarch64 and on `x86_64` sleeps one second between two counter reads. The
  enum derives nothing. It needs `std`.
- `fugit` 0.6.0: the lane measured it and did not read it.

## The systems outside Rust

Read from the `torvalds/linux` repository at the tag `v6.12`, and from the
`devicetree-org/devicetree-specification` repository at the tag `v0.4`.

- `include/uapi/linux/perf_event.h`, `struct perf_event_mmap_page` (line 571): `version` and
  `compat_version` first, then a `lock` sequence field and capability bits, of which
  `cap_user_time` says the time fields hold data. After them come `time_shift` and `time_mult`,
  with the conversion written in a comment, `size`, and a named `__reserved` tail that pads the
  header to one kilobyte.
- `arch/x86/include/asm/pvclock-abi.h`: `struct pvclock_vcpu_time_info`, 32 bytes, packed, with
  `version` as a sequence field, `tsc_to_system_mul` and `tsc_shift`. Its comment says the
  structures must not change. It has no magic and no layout version.
- `include/vdso/datapage.h`, `struct vdso_data`: `seq`, `mult` and `shift`, private to the kernel
  and its own vDSO code, with no stable layout.
- `source/chapter3-devicenodes.rst`, the `/cpus/cpu*` node properties: `timebase-frequency` and
  `clock-frequency`, each in hertz, each as one `<u32>` or one `<u64>`.

The Linux files are GPL; the review read them for the shape of what they publish only.

## The benchmark

A scratch crate that depends on the crate by path and on `quanta` at `=0.13.0`, built with
`cargo build --release` and run once on the same host (Intel Xeon Platinum 8160 at 2.10 GHz, 80
threads). The loop starts at 64 repeats and doubles until a pass lasts 50 milliseconds. It then
runs seven passes and reports the lowest, divided by the count. Inputs and results pass through
`core::hint::black_box`. The page held 2,100,000,000 hertz, and the tick count was
`0x1234_5678_9abc` plus the loop index.

| operation | nanoseconds per call | calls per pass |
|---|---|---|
| `build_page(hertz)` | 1.98 | 33,554,432 |
| `page.hertz()` | 1.54 | 33,554,432 |
| `(ticks as u128 * 1_000_000_000) / hertz as u128` | 30.02 | 2,097,152 |
| `(ticks as u128 * mult as u128) >> 32`, with `mult` derived once from the rate | 0.71 | 134,217,728 |
| `quanta::Clock::delta_as_nanos(1000, ticks)` | 0.69 | 134,217,728 |

Each column includes the loop's add of the result into an accumulator. `build_page` is two copies
into a 16-byte array, and `hertz` is the magic compare and one 8-byte load. The division row is
one 128-bit multiply and one 128-bit divide. The last two rows are one 128-bit multiply and a
shift, with `quanta`'s own calibration supplying its multiplier. A second run gave 1.97,
1.54, 33.74, 0.78 and 0.77.

## What the lane did not run

- Kani and the falsification replay; the harness and patch counts are from the source.
- Mutation testing.
- The build at the minimum Rust version, 1.88; the baseline's stranger run covers it.
- The tests of the neighbors, and `quanta`'s calibration time in a fresh process.
- A build for a 32-bit target, since the host has none installed; the crate's `const` assertion
  on pointer width was read and not exercised.
- A benchmark on aarch64 or riscv64.
