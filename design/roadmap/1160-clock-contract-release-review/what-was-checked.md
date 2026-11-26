# What the review read and ran

An appendix to [the milestone](../1160-clock-contract-release-review.md).

## The crate

`partsfoundry/clock_contract` at `08ceb00319f3089268ed5ba6e60f26c845f69aea`, version 0.1.0, no
tag, a fresh clone of `main`. The census of milestone 1129 (the combine review) counted it at
`92079a486b`. `git log 92079a486b..HEAD` lists two commits: `66e0d2c`, which bumps nine pinned
GitHub Actions, and its merge, `08ceb00`. `git diff --stat` over that range shows nine files,
all under `.github/workflows/`, one line each. No file under `src/` and no manifest changed, so
no census count changes.

The lane read in full: `Cargo.toml`, `README.md`, `CHANGELOG.md`, `docs/stranger-test.md`,
`.github/mutants-exempts`, `src/verification.rs` and the library part of `src/lib.rs` (the first
680 of 1,515 lines). It read the names of the 16 unit tests and the 8 loom models, and the body
of the test helper `with_page`.

## The commands

The host is Linux x86_64 with rustc 1.100.0, and every build wrote to a `CARGO_TARGET_DIR`
outside the clone. `git status --short` showed the clone clean afterward.

- `cargo build` passes.
- `cargo test` passes: 16 unit tests and 3 doctests.
- `RUSTFLAGS="--cfg loom" cargo test --release` passes: 8 loom models and 3 doctests.
- `RUSTDOCFLAGS="-D warnings" cargo doc --no-deps` passes with no warning.
- `cargo clippy --all-targets` passes with no warning.
- The three bare-metal builds of the README pass: `cargo build --lib --target` with
  `x86_64-unknown-none`, with `aarch64-unknown-none-softfloat` and with
  `riscv64imac-unknown-none-elf`.
- `cargo package --list --allow-dirty` lists 40 files, 20 of them under `.github/`, `.githooks/`
  or named `.gitignore` (P2-3).
- The crate declares no features, so there is one feature combination.
- The index page of the built documentation gives `NANOSECONDS_PER_SECOND` a summary that opens
  with a note on the unit-symbol ruling of 2026-10-27 (P1-4).
- `grep -n '# Examples'` over `src/lib.rs` finds two, on `wall_nanoseconds` and `policy::decide`
  (P1-5). The file has 11 public functions.

A scratch program that depends on the crate by path printed, in a release build:

- `propose::request(300)` is `0x2c00000000000000`, which is operation 44. A debug build panics
  on the assertion, and a `const` holding the call fails to compile in a debug build alone
  (P0-2).
- `propose::operation(propose::request(PROPOSE) | 0xabc)` is 1 (P0-5).
- `policy::decide(99, now, now + 2 hours)` is 2, `REFUSED_TOO_FAR_FORWARD`: 99 counts as a known
  state (P0-2).
- `policy::decide(now, state::SYNCHRONIZED, now)`, with the state and a time swapped, compiles
  and is 2 (P0-2).
- `offset_for(monotonic, wall)`, with its arguments swapped, is 0 (P0-2).
- `read` of seven zeroed words is `Reading { state: 0, offset_nanoseconds: 0, generation: 0 }`.
- `publish(77, 5)` returns generation 1, `read` then gives state 77, and `state::is_known(77)`
  is true (P0-2).
- `publish(now, state::SET)`, with its arguments swapped, compiles; `read` then gives state
  1800000000000000000 and offset 2 (P0-2).
- `publish(state::UNKNOWN, 123)` leaves a reading with an unknown state and offset 123. Nothing
  stops a caller passing that offset to `wall_nanoseconds` (P0-3).
- `status::BAD_REQUEST` is 4, and `state::is_known(4)` is true (P0-4).
- `{:?}` of a `ClockPage` is `ClockPage { base: 0x... }`; it is 8 bytes and `Reading` 24.

Here `now` is 1,800,000,000 seconds after the epoch, in nanoseconds.

## The search for a comparator

On 2026-11-26 (UTC), `https://crates.io/api/v1/crates?q=<words>&sort=recent-downloads&per_page=8`
for each of: "seqlock", "clock page", "vdso", "shared memory clock", "wall clock no_std",
"wait-free read", "time synchronization policy", "seqcount latch", "ntp client no_std" and
"double buffer lock-free". No result publishes a clock page or a policy for stepping a clock.
"wait-free read" found `mmap-sync` and `triple_buffer`, which the demand appendix of milestone
1129 does not list. `mmap-sync` shares one value between processes with readers that never wait,
so it ranks. The search also showed `vdso` 0.2.2 (2,110 in 90 days), which resolves Linux vDSO
symbols, and `sntpc` 0.11.0 (154,350), a client that would feed a proposer. Neither solves this
problem, and the lane read neither.

The demand appendix's row, measured again: `seqlock` 0.2.0 has 1,226,473 downloads in 90 days and
16 reverse dependencies; the appendix recorded 1,229,856 and 16.

## The comparators read

The lane downloaded each `.crate` file from `static.crates.io` at the version in the block's
table and unpacked each apart from the others.

- `mmap-sync` 2.0.4, all of `src/synchronizer.rs`, `src/state.rs`, `src/instance.rs`,
  `src/guard.rs` and `src/lib.rs`, the head of `src/locks.rs`, `examples/reader.rs` and the
  manifest. `State` is a `u64` version and two `u32` reader counts in a mapped file, with two
  data files beside it. `Synchronizer::write` picks the copy readers do not use, waits up to a
  grace period for its reader count to reach zero, writes it and swaps the version.
  `Synchronizer::read` is `unsafe`; it adds one to a reader count (`State::rlock`), so a reader
  maps the state writable, and its result is good for the grace period alone.
  `InstanceVersion(u64)` is a newtype with `TryFrom<u64>`, whose error for zero is
  `UninitializedState`, and `From<InstanceVersion> for u64`. `SynchronizerError` derives
  `thiserror::Error` and has eight variants, `WriteLockConflict` among them. The lock strategies
  implement a sealed trait. The crate needs `std`, `memmap2`, `rkyv`, `bytecheck`, `wyhash` and
  `thiserror`.
- `seqlock` 0.2.0, `src/lib.rs` whole. `SeqLock<T: Copy>::read` loads the count, yields the
  thread while it is odd, reads, fences and compares. `lock_write` returns a `SeqLockGuard` under
  a `parking_lot::Mutex`, and `try_lock_write` returns `Option`. The crate page opens with an
  example. It needs `std`.
- `triple_buffer` 9.0.1, the head of `src/lib.rs` and its list of public items.
  `TripleBuffer::split` returns `(Input<T>, Output<T>)`, one type for each end, and the crate
  page opens with two examples. It is `no_std`, for one producer and one consumer. Its one
  feature is `miri`.
- `atomic-time` 1.0.0 and `left-right` 0.11.8: measured, not downloaded, not read.

## The systems outside Rust

Each file came from a public mirror at the named tag.

- Linux v6.12. `include/vdso/datapage.h`: `struct vdso_data`, whose first member is `u32 seq` and
  which has `s32 clock_mode`, and no magic. `include/vdso/helpers.h`: `vdso_read_begin(const
  struct vdso_data *)` spins while `seq` is odd, and `vdso_write_begin(struct vdso_data *)` takes
  a mutable pointer. `lib/vdso/gettimeofday.c`: `do_hres` returns -1 when `vdso_clocksource_ok`
  is false, which is `clock_mode == VDSO_CLOCKMODE_NONE`. `include/linux/seqlock.h`: the latch
  (`raw_write_seqcount_latch`, `raw_read_seqcount_latch_retry`), which the crate's documentation
  names as its model; a latch reader retries only when the count moved.
- FreeBSD release/14.3.0. `sys/sys/vdso.h`: `struct vdso_timekeep` with `tk_ver`, `tk_enabled`,
  `tk_current` and an array of `struct vdso_timehands`, each with `th_gen`.
  `lib/libc/sys/__vdso_gettimeofday.c`: the caller returns `ENOSYS` when `tk_ver` is not
  `VDSO_TK_VER_CURR`, and `binuptime` returns `ENOSYS` when `tk_enabled` is zero, then retries
  while `tk_current` moved, `th_gen` is zero or `th_gen` moved. `sys/kern/kern_tc.c`: the lane
  searched it for `th_generation`. The writer zeroes a record's generation, fills the record and
  stores the new generation with a release.

The Linux files are GPL; the review read them for the shape of what they publish only.

## The benchmark

A scratch crate outside the clone depends on `clock_contract` by path, `seqlock` at `=0.2.0` and
`mmap-sync` at `=2.0.4`, with `rkyv` 0.7.46 resolved. The command is `cargo build --release` and
then the binary, with a path prefix for the `mmap-sync` files on an ext4 file system. The host is
Linux x86_64, an Intel Xeon Platinum 8160 at 2.10 GHz with 80 threads, rustc 1.100.0. The
benchmark runs on one thread.

Each measurement starts at 64 calls and doubles the count until one pass lasts 50 ms. It then
runs seven passes and reports the lowest, divided by the count. `black_box` wraps the handle, the
inputs and the result. The value is a pair of `u64`: the state `SET` and one offset.

| measurement | what a call includes | run 1 | run 2 |
|---|---|---|---|
| `ClockPage::read` | the magic check, two loads of the count, two data loads | 2.65 ns | 2.67 ns |
| `SeqLock<(u64, u64)>::read` | two loads of the count, one volatile read of the pair | 1.34 ns | 1.17 ns |
| `ClockPage::publish` | the claim, the fence, two stores, the count, the release | 11.89 ns | 12.04 ns |
| `SeqLock::lock_write` and a store | the mutex, both count stores, the store of the pair | 17.60 ns | 16.79 ns |
| `Synchronizer::read::<Pair>(false)` | the version load, the reader count up and down, `archived_root` | 18.77 ns | 19.40 ns |
| `Synchronizer::read::<Pair>(true)` | the same with `check_archived_root` | 18.92 ns | 19.59 ns |
| `Synchronizer::write` | serialization, a checksum, a file write, the version swap | 472,284 ns | 457,347 ns |

The block's table gives run 1. The page in the benchmark is seven `AtomicU64` on the stack, so
the numbers hold no cost of a mapping.

## What the lane did not run

- Kani and the falsification replay; the harness and patch counts are from the source.
- Mutation testing.
- The build at the minimum Rust version, 1.88; the baseline's stranger run covers it.
- A build for a 32-bit target with 64-bit atomics; the host has none, so P2-4 is an inference
  from the cast in `ClockPage::new`.
- A benchmark with a writer publishing while readers read, on one machine or across processes.
- A read or a publish through a real read-only mapping; P0-1 rests on the `# Safety` text.
- The tests of the comparators.
