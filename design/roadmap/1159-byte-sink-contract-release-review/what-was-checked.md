# What the review read and ran

An appendix to [the milestone](../1159-byte-sink-contract-release-review.md).

## The crate

`partsfoundry/byte_sink_contract` at `8a477c6a3167f6cb4cb76741cecebae20c306825`, version 0.1.0
with `publish = false` and no tag, a fresh clone of `main`. The census of milestone 1129 (the
combine review) counted the same commit. The lane read in full: `Cargo.toml`, `README.md`,
`CHANGELOG.md`, `docs/stranger-test.md`, `src/lib.rs` (the library and twelve unit tests),
`src/verification.rs` (six Kani harnesses), `.github/mutants-exempts` and
`.github/workflows/release.yml`.

## The commands

All of these ran with rustc 1.100.0 on a Linux x86_64 host, with the build directory outside the
clone. `git status --short` showed the clone clean afterward.

- `cargo build` passes.
- `cargo clippy --all-targets` passes with no warning.
- `cargo test` passes: 12 unit tests and 3 doctests.
- `RUSTDOCFLAGS="-D warnings" cargo doc --no-deps` passes with no warning.
- The bare-target build, `cargo build --lib --target <target>`, passes for each of the three
  targets the README names: x86_64, aarch64 and riscv64 with no operating system.
- `cargo package --list --allow-dirty` lists 44 files, 19 of them under `.github/` or
  `.githooks/` (P2-4).
- `grep -c 'kani::proof' src/verification.rs` prints 6, and `falsifications/` holds 6 patches,
  as the README says.
- The manifest declares no feature, so the crate has one combination to build.
- A search of the clone for the word "documentation" in `Cargo.toml` finds no key (P2-4).

## The scratch programs

One scratch crate depends on the clone by path, on `cobs` at `=0.5.1` with no default feature and
on `embedded-io` at `=0.7.1`. Each program is one file in it.

- A probe that prints what ten calls return. Its output, by finding:
  - P0-1: `unpack` of the words of `pack(b"hi")` with `0xff << 48` set in the first word returns
    `Bytes(2)`. With `200 << SEVERITY_SHIFT` set it returns `Bytes(2)`, and `severity` of that
    word is `None`. `unpack(MessageWords::new(2, u64::MAX, u64::MAX), &mut out)` returns
    `Bytes(2)` and leaves sixteen bytes of 255 in `out`.
  - P0-2: `severity(with_severity(0, 200))` is `Some(7)`.
  - P1-3: `unpack(MessageWords::new(with_severity(end_of_stream(), 3), 0, 0), &mut out)` returns
    `Malformed`.
  - `unpack` of a count of 17 returns `Malformed` and leaves `out` as it was.
  - `first_word(9, 40)` returns `0x900000000000028`, a word `unpack` refuses.
  - `classify(i64::MIN)` is `NoSink` and `classify(7)` is `Ok`.
  - `MessageWords` is 24 bytes, `Message` 16 and `Sent` 1.
- A build check with a `const fn` copy of `pack`, written with a `while` loop in place of
  `copy_from_slice`. `cargo +1.88 run` builds it, binds `pack_const(b"hello")` in a `const` and
  finds it equal to `pack(b"hello")` (P2-2). The lane wrote no `const` copy of `unpack`.
- The benchmark below.

## The comparators read

Each crate below came from crates.io at the version in the block's prior-art table, into a
directory of its own, and the lane read the files named.

- `embedded-io` 0.7.1, `src/lib.rs` and `Cargo.toml`. `ErrorKind` is `#[non_exhaustive]` and has
  `BrokenPipe`, `Unsupported` and `WriteZero`. The trait `Error` requires `core::error::Error` and
  adds `kind()`. `Write::write` returns `Result<usize, Self::Error>`, the count taken, and
  `write_all` holds the loop over it. The trait has `flush` and no end of stream. The features
  are `alloc`, `std` and `defmt`.
- `cobs` 0.5.1, `src/enc.rs`, `src/dec.rs` and `Cargo.toml`. `encode(source, dest) -> usize`
  panics on a short destination, and `try_encode` returns `Result<usize, DestBufTooSmallError>`.
  `decode(source, dest) -> Result<DecodeReport, DecodeError>`. `DecodeError` derives
  `thiserror::Error` and has `EmptyFrame`, `InvalidFrame { decoded_bytes }` and
  `TargetBufTooSmall`, with no `#[non_exhaustive]`. `encode` has a `# Panics` section.
- `bitfield-struct` 0.13.0, `README.md` only. The macro turns a struct into a wrapper over one
  integer, with a getter and a `with_` method for each field, and a checked form of each setter
  that returns a `Result`.
- `syslog` 7.0.0, `src/format.rs`. `Severity` is an enum of eight variants in the order of
  RFC 5424, spelled as the C constants (`LOG_EMERG` to `LOG_DEBUG`), and derives `Copy` and
  `Clone` alone.

Measured at the same time and not read:

| crate | version | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|
| `defmt` | 1.2.0 | 130,329,567 | 97,141,048 | 1,380 | 2026-10-15 |
| `postcard` | 1.2.0 | 103,293,885 | 46,645,473 | 1,820 | 2026-11-21 |
| `asynchronous-codec` | 0.7.0 | 40,605,589 | 7,396,487 | 107 | 2023-10-11 |
| `embedded-io-async` | 0.7.0 | 9,425,517 | 3,962,732 | 323 | 2025-09-30 |
| `ipc-channel` | 0.23.1 | 7,579,368 | 1,618,155 | 56 | 2026-10-24 |
| `rtt-target` | 0.6.2 | 1,594,538 | 261,341 | 86 | 2025-10-13 |
| `corncobs` | 0.1.4 | 513,853 | 69,601 | 6 | 2025-06-11 |
| `sel4` | 0.0.12 | 19,040 | 148 | 1 | 2017-04-24 |

Seven searches of crates.io, sorted by recent downloads, found no crate for a byte stream in a
kernel's message registers: "byte sink", "message registers", "ipc framing", "inline message",
"end of stream", "pipe protocol no_std" and "sel4 ipc".

## The systems outside Rust

Each file came from the project's public repository at the tag named.

- seL4 13.0.0, `libsel4/mode_include/64/sel4/shared_types.bf`: the block `seL4_MessageInfo` has
  a label of 52 bits, `capsUnwrapped` of 3, `extraCaps` of 2 and a length of 7.
- seL4 13.0.0, `libsel4/include/sel4/constants.h`: `seL4_MsgLengthBits` is 7 and
  `seL4_MsgMaxLength` 120. The x86_64 `sel4_arch/constants.h` sets `seL4_FastMessageRegisters`
  to 4.
- seL4 13.0.0, `libsel4/sel4_arch_include/x86_64/sel4/sel4_arch/syscalls.h`: `seL4_SendWithMRs`
  takes the message info and four words as separate arguments, and `seL4_DebugPutChar` takes one
  character.
- rust-sel4 v6.0.0, `crates/sel4/src/message_info.rs`: `MessageInfo` wraps the generated word.
  `new(label, caps_unwrapped, extra_caps, length)` converts each `usize` with
  `try_into().unwrap()`. The readers are the methods `label`, `caps_unwrapped`, `extra_caps` and
  `length`. `MessageInfoBuilder` derives `Default` and sets one field per method.
- RFC 5424, section 6.2.1: severities 0, emergency, to 7, debug.

seL4 is under the GPL version 2 with BSD-licensed user headers, and rust-sel4 is MIT; the review
read them for their interface shape only.

## The comparison

| axis | `byte_sink_contract` | seL4 with rust-sel4 | `cobs` 0.5.1 | `embedded-io` 0.7.1 |
|---|---|---|---|---|
| what a message is | three words: opcode, kind, severity and count, then sixteen bytes | an info word and up to 120 words | bytes up to a zero | not applicable, a trait |
| end of stream | one exact message | each protocol's own | none; a frame ends at its zero | none |
| the first word | a bare `u64` and free functions | a wrapper type and methods | not applicable | not applicable |
| a builder given a value too large | cannot happen, by the parameter types | panics | panics, or `try_encode` | not applicable |
| the decoder's refusal | a variant of the value, no cause | none, the kernel checks the length | `Result`, an enum of three | `Result`, a kind for each error |
| a destroyed peer against none | `Gone` and `NoSink` | each protocol's own | not applicable | `BrokenPipe` and `Unsupported` |
| `no_std`, no allocation | both | both | both, with no default feature | both |
| proofs | six Kani harnesses | the kernel's own proof, not the library's | none | none |

## The benchmark

A scratch crate depends on the clone by path and on `cobs` at `=0.5.1`, built with
`cargo build --release --bin bench`, rustc 1.100.0, on a Linux x86_64 host (an Intel Xeon Platinum
8160 at 2.10 GHz, 80 threads).

Each row runs a closure in a loop that starts at 64 repeats and doubles until one pass lasts
50 ms. Seven passes follow at that count, and the figure is the lowest pass divided by the count.
`std::hint::black_box` wraps every input and every result. Each function under test sits behind
an `#[inline(never)]` wrapper, so a row includes one call.

The input is 4,096 bytes, none of them zero, so `cobs` writes one run for each 254 bytes. The
rows:

| operation | time |
|---|---|
| `pack`, 16 bytes | 5.41 ns |
| `pack`, 9 bytes | 9.82 ns |
| `unpack`, 16 bytes | 5.27 ns |
| `unpack`, 9 bytes | 5.38 ns |
| scratch `unpack` by value, 16 bytes | 8.78 ns |
| scratch `unpack` by value, 9 bytes | 8.96 ns |
| scratch strict `unpack`, 16 bytes | 5.43 ns |
| scratch strict `unpack`, 9 bytes | 5.92 ns |
| 4,096 bytes: `pack` and `unpack` for each of 256 messages | 4,917 ns |
| 4,096 bytes: the same with the strict `unpack` | 5,278 ns |
| `cobs::encode`, 16 bytes | 38.63 ns |
| `cobs::decode`, 16 bytes | 39.05 ns |
| 4,096 bytes: `cobs::encode` then `cobs::decode`, one frame | 13,444 ns |
| 4,096 bytes: `copy_from_slice`, the floor | 53.7 ns |

- The `pack` rows pack the first 16 or 9 bytes and read one word and the count.
- The `unpack` rows decode a message packed outside the loop into a fresh `[u8; 16]` and read its
  last byte.
- The by-value decoder is the crate's `unpack` with `Bytes([u8; 16], usize)` in place of the out
  parameter (P2-6).
- The strict decoder is the crate's `unpack` with the three refusals of P0-1: bits 55:48, a
  severity field past 8, and a non-zero byte past the count.
- The 256-message rows chunk the buffer with `pack`, decode each message and copy its bytes to a
  destination. They include no send, so they price the framing and leave the rendezvous out.
- The `cobs` rows encode into a buffer of `max_encoding_length` and decode into a destination of
  the input's length.

## What was not run

- Kani, mutation testing, the fuzz workflow and the six falsification patches.
- `cargo +1.88 test`, the README's minimum-version check; the lane ran the 1.88 toolchain for the
  `const fn` build check alone.
- No build for a target whose `usize` is narrower than 32 bits.
- No comparator's own tests, and no build of `bitfield-struct`, `syslog` or rust-sel4.
- No send through a kernel: every figure is the framing alone.
