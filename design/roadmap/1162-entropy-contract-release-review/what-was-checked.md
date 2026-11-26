# What the review read and ran

An appendix to [the milestone](../1162-entropy-contract-release-review.md).

## The crate

`partsfoundry/entropy_contract` at `5150f14f781160debacd33310a6941f8829d958c`, version
0.1.0-pre.1, a fresh clone of `main`. The tag `v0.1.0-pre.1` names the same commit. The census of
milestone 1129 (the combine review) counted the same commit. The lane read in full: `Cargo.toml`,
`README.md`, `CHANGELOG.md`, `docs/stranger-test.md`, `.github/mutants-exempts` and the library
part of `src/lib.rs` (lines 1 to 545 of 1,074). It read the test module and the `verification`
module for their lists of tests and harnesses.

## The commands

Each command below ran in the `entropy_contract` clone on a Linux x86_64 host, with rustc 1.100.0
and the build directory kept outside the clone. `git status --short` showed the clone clean
afterward.

- `cargo build` passes.
- `cargo test` passes: 24 unit tests and 13 doctests.
- `RUSTDOCFLAGS="-D warnings" cargo doc --no-deps` passes with no warning.
- `cargo clippy --all-targets` passes with no warning.
- The `entropy_contract` library builds with `cargo build --lib --target <target>` for the three
  bare targets its README names: RISC-V 64, AArch64 soft-float and x86_64.
- `cargo package --list --allow-dirty` lists 44 files, 20 of them under `.github/` or named
  `.gitignore` (P2-3).
- `grep -c 'kani::proof' src/lib.rs` prints 7, and `falsifications/` holds 7 patches, as the
  README says.
- `grep -n '# Errors' src/lib.rs` prints lines 103 and 252, the two builders (P1-4).
- In lines 1 to 545, `grep -c 'as usize\|as u64'` prints 15 and `grep -c 'MAXIMUM_BYTES as usize'`
  prints 6 (P0-4). `grep -c 'unwrap()\|\.expect('` prints 8 (P1-4), and `grep -c opcode` prints 13.
- The crate declares no features, so there is one feature combination.

A scratch program that depends on the crate by path printed:

- `request(GET, 0)` is `Ok(0x100000000000000)`, `requested_bytes` of it is 0, and `reply(&[])`
  is `(0, 0)` (P0-5).
- `fill_with` over a closure that answers `(8, 1)` to a request for four bytes returns
  `Err(ShortReply { asked: 4, delivered: 8 })` (P0-7).
- `fill_with` over a closure that answers `-4` as a `u64` returns `Err(NoService)` (P0-3).
- `fill_with` on twenty bytes, with the third answer dry, returns
  `Err(ShortReply { asked: 4, delivered: 0 })` and leaves sixteen bytes written.
- `let refusal = OperationOutOfRange;` compiles (P0-2).
- `bring_up_failure(0)` is `Ok(0xdead000000000000)` (P2-4).
- `copy_delivered_bytes(200, 7, &mut [0u8; 16])` returns 8.
- `delivered_bytes(READY)` and `delivered_bytes(BRING_UP_FAILED)` are both `None`.
- `readiness` answers `READY` for seven equal nonzero bytes, for `[0, 0, 0, 7, 0]` and for 256
  bytes that alternate two values. Each matches the documented rule.

A second scratch file did not compile, with these four errors, as expected:

- `readiness(&draw[..])`: a slice yields `&u8` (P2-2).
- A function bounded on `core::error::Error` refuses `Refusal`, and `{}` does not format it
  (P1-2).
- `let opcode: u8 = operation(0);` is a type mismatch (P0-1).

## The search for a comparator

On 2026-11-26 (UTC), `https://crates.io/api/v1/crates?q=<words>&sort=recent-downloads&per_page=8`
for each of: "entropy service", "entropy protocol", "virtio rng", "random bytes ipc", "entropy
source", "rng service", "getrandom", "entropy no_std", "hwrng" and "random device driver". No
result defines the words two processes exchange to move random bytes. `getrandom` and
`virtio-drivers` became the neighbors. The lane measured `rand_jitter` 0.6.1 (7,761,227 downloads
in 90 days) and `rdrand` 0.9.0 (5,313,118) and set them aside, since each is a source of bytes
and not an exchange. It saw `arcbox-virtio-rng` 0.11.3 (1,178) and did not read it: it is the
device's side of VIRTIO, inside one virtual machine monitor.

## The neighbors and the integration target

The lane downloaded each `.crate` file from `static.crates.io` at the version the block's table
gives, and unpacked each apart from the others.

- `getrandom` 0.4.3, `src/lib.rs`, `src/error.rs`, `src/sys_rng.rs` and `Cargo.toml`.
  `fill(dest: &mut [u8]) -> Result<(), Error>` fails on a partial read and promises nothing about
  `dest` on error, and it returns at once for an empty slice. `fill_uninit` takes
  `&mut [MaybeUninit<u8>]`. `Error` is a newtype over a nonzero code, with `UNSUPPORTED`,
  `ERRNO_NOT_POSITIVE` and `UNEXPECTED` as constants, `raw_os_error`, `new_custom`, `Display`
  and `core::error::Error` (lines 210 and 229). The features are `std`, `sys_rng` and `wasm_js`.
  `SysRng` implements `rand_core`'s `TryRng` under `sys_rng`.
- `virtio-drivers` 0.13.0, `src/device/rng.rs`: `VirtIORng::request_entropy(&mut self, dst: &mut
  [u8]) -> Result<usize>` hands the buffer to the device and returns the count written. It has no
  loop, no readiness check and one queue of eight entries.
- `rand_core` 0.10.1, `src/lib.rs`: `TryRng` has `type Error: core::error::Error`,
  `try_next_u32`, `try_next_u64` and `try_fill_bytes(&mut self, dst: &mut [u8])`, which fills
  `dst` entirely. `Rng` follows for any `TryRng` whose error is `Infallible`. The manifest
  declares no features.

## The systems outside crates.io

- Hubris (`oxidecomputer/hubris`) at commit `969bac2bf47c98710842eb232fdd4a9c54e7dd7f`,
  `idl/rng.idol` and `drv/rng-api/src/lib.rs`. The interface `Rng` has one operation, `fill`. It
  takes a writable lease on the caller's `[u8]` and replies `Result<usize, RngError>`. `RngError`
  is a `repr(u32)` enum: `PoweredOff`, `NoData`, `ClockError`, `SeedError`, `UnknownRngError` and
  `ServerRestarted`, the last marked as the server's death. A build script generates the client
  stub.
- The VIRTIO specification at tag `v1.4-cs01`, `device-types/entropy/description.tex`: device 4,
  one queue, no feature bits and no configuration. The driver places writable buffers and must
  read the length the device wrote. The device must place one or more bytes and may fill less
  than the buffer.
- Linux v6.12, `drivers/char/random.c`: `getrandom` refuses an unknown flag with `EINVAL`, waits
  or answers `EAGAIN` until the generator is seeded, and `get_random_bytes_user` returns 0 for an
  empty buffer. `drivers/char/hw_random/core.c`: `rng_get_data` and `rng_dev_read` pass a
  driver's bytes on with a quality figure and no test of the bytes.
  `drivers/char/hw_random/virtio-rng.c`: `virtio_read` and `copy_data` return a short count.

The Linux files are GPL and the Hubris files are MPL-2.0; the review read them for the shape of
what they publish only.

## The benchmark

One scratch crate, release profile, depending on the crate by path and on `getrandom` at
`=0.4.3`, run with `cargo run --release` on a Linux x86_64 host (Intel Xeon Platinum 8160 at
2.10 GHz, 80 threads, rustc 1.100.0). The loop starts at 64 repeats and doubles until a pass
lasts 50 ms. It then runs seven passes and reports the lowest divided by the count. The buffer
and each result pass through `black_box`.

| buffer | `fill_with`, stubbed `CALL` | one stubbed call | `getrandom::fill` |
|---|---|---|---|
| 32 bytes | 23.1 ns | 12.4 ns | 90.1 ns |
| 4,096 bytes | 2,647.5 ns | 1,352.0 ns | 7,298.5 ns |

- The first column includes `fill_with`, the request packing, and a closure that reads the count
  with `requested_bytes` and answers one step of a 64-bit linear congruential generator.
- The second column includes the same generator writing the buffer eight bytes at a time in one
  call, with no request or reply word.
- The third column includes the system call and the kernel's generator.

The contract's own packing comes to 2,647.5 ns over 512 round trips, about 5 ns each. A 32-byte
key takes 4 round trips and a page takes 512.

Not run: the time of a real `CALL`. It needs the kernel the contract is written for, which this
host does not run.

## What the lane did not run

- Kani and the falsification replay; the harness and patch counts are from the source.
- Mutation testing.
- The build at the minimum Rust version, 1.88; the crate's stranger run covers it.
- The tests of the neighbors.
- A read of Fuchsia's `zx_cprng_draw`; the lane's fetch of its reference page failed, and the
  block makes no claim about it.
