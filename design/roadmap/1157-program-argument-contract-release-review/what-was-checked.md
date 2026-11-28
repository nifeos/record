# What the review read and ran

An appendix to [the milestone](../1157-program-argument-contract-release-review.md).

## The crate

`partsfoundry/program_argument_contract` at `b097970b8650ca8a370018f18ce533c1f22db3e4`, version
0.1.0 with `publish = false`. Read: `Cargo.toml`, `README.md`, `CHANGELOG.md`,
`docs/stranger-test.md`, `.github/mutants-exempts`, `.github/coverage-exemptions` and the whole of
`src/lib.rs`, which holds the library, three Kani harnesses and fourteen unit tests. The census of
milestone 1129 (the combine review) counted the crate at this commit.

The public interface is six constants (`PAGE_BYTES`, `HEADER_BYTES`, `MAXIMUM_RECORDS_BYTES`,
`MAGIC`, `VERSION` and `INTERFACE_ID`), one function (`record_bytes`) and five types:
`PushRefused`, `WrongPageLength`, `PageBuilder`, `ArgumentPage` and `Iter`.

## The commands

Run with rustc 1.100.0 on a Linux x86_64 host, with the build directory outside the clone.

- `cargo build` and `cargo clippy` pass with no warning.
- `cargo test` passes: fourteen unit tests and one doctest.
- The one-file library builds with `cargo build --lib` for each installed bare target:
  `x86_64-unknown-none`, `aarch64-unknown-none-softfloat` and `riscv64imac-unknown-none-elf`.
- `cargo doc --no-deps` passes with no warning.
- `cargo package --list --allow-dirty` lists 39 files, 19 of them under `.github/` and
  `.githooks/` (P2-4).
- `grep -c 'kani::proof' src/lib.rs` prints 3. The README counts two and then describes three
  (P1-1).
- A numbered listing of `src/lib.rs` puts the exemption's line number on `total > room`, six
  lines below `page.len() < HEADER_BYTES` (P1-5).
- `git status --short` in the clone prints nothing after all of the above.

## The scratch programs

One scratch crate depends on the clone by path, on `argv` at `=0.1.14` and on `crt0stack` at
`=0.1.0`. Each program below is one file in it.

- A program that pushes `rm`, an argument of 4,080 bytes and `--force`, then calls `finish`. The
  second `push` returns `Err(TooLong)`, `finish` returns 2, and the page parses as `rm` and
  `--force` (P0-1).
- The same program reads that page three more ways. A slice of two pages parses as the same two
  arguments, and so do the page's first 40 bytes and its first 33. A zeroed page and a page
  finished with no `push` both report a length of 0 (P0-3, P0-4, P2-5). `{:?}` of the parsed page
  prints the record bytes as numbers (P1-3).
- Two programs that take a `PushRefused` and a `WrongPageLength` as `&dyn core::error::Error`.
  Each fails with E0277. A third carries both through `?` into a boxed error and fails twice with
  E0277 (P1-2).
- Two programs with `for argument in page` and `for argument in &page`. Each fails with E0277
  (P2-1).
- A program that calls `ArgumentPage::default()`. It fails with E0599 (P1-3).

## The comparators read

Each of the five crates below came from crates.io as a `.crate` file at the version the prior-art
table gives. Each was unpacked into its own empty directory, and the files named were read there.

- `argv` 0.1.14, `src/lib.rs`: `iter()` returns an `Iter` of `&'static OsStr` with
  `ExactSizeIterator`. On Linux with glibc a function in `.init_array` captures `argc` and `argv`,
  and the iterator reads each pointer as a `CStr`. On every other target it collects
  `std::env::args_os` once and leaks the strings. The crate needs `std` and has no dependency.
- `origin` 0.26.2, `src/program/linux_raw.rs`: `compute_args` reads `argc` from the initial stack,
  takes `argv` and `envp` as raw pointers and checks them with three `debug_assert` lines. The
  program's `origin_main(argc: usize, argv: *mut *mut u8, envp: *mut *mut u8)` receives them raw.
- `kernel-elf-parser` 0.3.4, `src/user_stack.rs`:
  `app_stack_region(args: &[String], envs: &[String], auxv: &[AuxEntry], sp: usize) -> Vec<u8>`.
  It builds in a `VecDeque`, places no bound on the result, and reads `argv_slice[0]` when the
  caller's auxiliary values carry no `EXECFN`. The panic on an empty list is a reading of that
  line; the review did not run it. The crate depends on `xmas-elf`, `zero` and `zerocopy`.
- `crt0stack` 0.1.0, `src/lib.rs`, `src/builder.rs` and `src/reader.rs`: `Builder<'a, T>` over a
  caller's `&mut [u8]`, where `T` is `Arg`, `Env` or `Aux` and `done` moves to the next. `push`
  takes a `&str` and returns `Result<(), OutOfSpace>`. `OutOfSpace` is a unit struct that derives
  `Hash`, `Ord` and `Default` and implements neither `Display` nor an error trait. `push` for an
  argument writes the terminating zero byte before it writes the string, so a refused argument
  leaves that byte behind and the builder usable. The stack holds the absolute addresses of the
  strings in the builder's buffer. `Reader::from_stack(&Stack)` is `unsafe`, and its iterator
  yields `&str` and returns `None` at the first argument that is not UTF-8. The manifest excludes
  `.github/` and has a default feature `std`.
- `linux-loader` 0.14.0, `src/cmdline/mod.rs`: `Cmdline::new(capacity)`, `insert`, `insert_str`
  and `try_from(&str, capacity)`, each returning the module's `Error`. That enum has eleven
  variants, among them `TooLarge`, implements `Display` and `std::error::Error`, and has no
  `#[non_exhaustive]`.
- `wasip1` 1.0.0, `src/lib_generated.rs`: `args_sizes_get() -> Result<(Size, Size), Errno>` and
  `args_get(argv: *mut *mut u8, argv_buf: *mut u8) -> Result<(), Errno>`, both `unsafe`. `Errno`
  wraps a `u16` and implements `Display` and `std::error::Error`.
- `lexopt` 0.3.2, `src/lib.rs`: `Parser::from_env`, and `Parser::from_iter` and `from_args` over
  any iterator whose items convert into an `OsString`. A byte slice does not, so a program on a
  target without `std` feeds this crate's `Iter` to a parser of its own.

Five more crates, measured at the same time as the prior-art table and not read:

| crate | version | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|
| `auxv` | 0.3.3 | 83,406 | 1,993 | 0 | 2017-01-20 |
| `multiboot2` | 0.28.0 | 1,041,556 | 237,214 | 2 | 2026-09-04 |
| `clap_lex` | 1.1.2 | 1,103,581,987 | 273,096,242 | 37 | 2026-11-16 |
| `bstr` | 1.14.0 | 533,179,888 | 137,728,669 | 710 | 2026-11-18 |
| `xous` | 0.9.71 | 160,014 | 9,244 | 14 | 2026-10-07 |

Searches of crates.io by recent downloads for `argv`, `auxv`, `crt0`, `initial stack`, `process
arguments`, `processargs`, `execve`, `wasi args`, `cmdline` and `kernel command line` found no
crate that defines a page or a message of its own for a program's arguments.

## The comparison

How the nearest four compare, read from each one's source:

| axis | `program_argument_contract` | `argv` 0.1.14 | `kernel-elf-parser` 0.3.4 | `crt0stack` 0.1.0 | WASI preview 1 |
|---|---|---|---|---|---|
| sides | writer and reader | reader | writer | writer and reader | reader calls, host answers |
| an argument is | any bytes, length first | bytes to the first zero | a `String`, zero after | a `&str`, zero after | bytes, zero after |
| limit | 4,080 bytes of records | the system's | none | the caller's slice | the host's |
| a line that does not fit | `push` refuses one argument (P0-1) | not applicable | not applicable | `push` refuses one argument | an `errno` |
| the reader checks | every record, before the first | nothing | not applicable | UTF-8, one argument at a time | not applicable |
| the reader's failure | no arguments, no reason (P0-3) | none | not applicable | the iterator ends early | an `errno` |
| `no_std`, no allocation | both | needs `std` | needs `alloc` | both | both |
| refusal type | two, no `Display` | none | none | one, no `Display` | `Errno`, with `Display` |
| pointers inside the data | none | yes | yes | yes | written by the host |

## The contract shape

What the crate holds of the shape the contract-layout decision of milestone 1129 asks about:

| part | here |
|---|---|
| identity | `INTERFACE_ID`, a `u64` of 18 |
| version | `VERSION`, a `u32` of 2; a constant assertion ties it to the last byte of the magic |
| magic | `MAGIC`, a `[u8; 8]`, `PROGARG2`, the first eight bytes of the page |
| sizes | `PAGE_BYTES`, `HEADER_BYTES`, `MAXIMUM_RECORDS_BYTES` and the function `record_bytes` |
| address | none in the crate; the caller passes it to `from_virtual_address` as a `u64` |
| writer | `PageBuilder`: `new`, `push`, `remaining_bytes`, `finish` |
| reader | `ArgumentPage`: `parse`, `from_virtual_address`, `len`, `is_empty`, `iter`, `EMPTY`; and `Iter` |
| refusals | the writer's `PushRefused` and `WrongPageLength`; the reader has none |
| on the page | the magic, a count, a total, then records; no identity and no version field |

## The systems outside Rust

- Linux v6.12 (commit `adc218676eef`), `fs/exec.c`: `copy_strings` returns `-E2BIG` for a string
  past `MAX_ARG_STRLEN` or past the stack limit, and the `execve` fails whole.
  `bprm_stack_limits` bounds the strings at a quarter of the stack limit, and never under
  `ARG_MAX`. `do_execveat_common` adds an empty `argv[0]` when the caller passes no argument, so a
  program that starts at `argv[1]` does not walk into the environment.
- Linux v6.12, `include/uapi/linux/binfmts.h`: `MAX_ARG_STRLEN` is 32 pages and `MAX_ARG_STRINGS`
  is `0x7FFFFFFF`.
- Linux v6.12, `fs/binfmt_elf.c`: `create_elf_tables` writes `argc`, the argument pointers, a
  null, the environment pointers, a null and the auxiliary values, each value under an `AT_` tag.
- WASI at the tag `v0.2.0` (commit `70214b878af4`),
  `legacy/preview1/witx/wasi_snapshot_preview1.witx`: `args_sizes_get` returns the count of
  arguments and the size of their data, or an `errno`. `args_get` fills a pointer array and a
  buffer whose sizes should match, each argument ending in a zero byte. The first argument should
  be the program's name. The module's name is `wasi_snapshot_preview1`.

Linux is GPL; the review read it for its interface shape only.

## The benchmark

A scratch crate depends on the clone by path, on `argv` at `=0.1.14` and on `crt0stack` at
`=0.1.0`, built with `cargo build --release`, rustc 1.100.0, on a Linux x86_64 host (an Intel Xeon
Platinum 8160 at 2.10 GHz, 80 threads).

Each row runs a closure in a loop that starts at 64 repeats and doubles until one pass lasts
50 ms. Seven passes follow at that count, and the figure is the lowest pass divided by the count.
`std::hint::black_box` wraps every input and every result.

The input is the benchmark program's own arguments, since `argv` can read no others. The program
runs twice: as `rg pattern src` (3 arguments, 14 bytes) and as `rg` with 63 arguments of 8 bytes
(64 arguments, 508 bytes). It copies its arguments once, builds this crate's page and a
`crt0stack` stack from them outside the loops, and asserts that all three readers sum to the same
byte count.

The results, in time per call:

| operation | 3 arguments | 64 arguments |
|---|---|---|
| `ArgumentPage::parse`, returning `len` | 7.1 ns | 146.8 ns |
| `parse`, then `iter` and a sum of the lengths | 24.8 ns | 370.2 ns |
| `iter` and the sum, on a page parsed outside the loop | 11.2 ns | 204.1 ns |
| `iter().last()`, on a page parsed outside the loop | 10.4 ns | 223.0 ns |
| `PageBuilder::new`, `push` each argument, `finish` | 33.6 ns | 465.6 ns |
| `argv`: `iter` and a sum of the lengths | 16.7 ns | 358.7 ns |
| `argv`: `iter().len()` | 3.5 ns | 44.0 ns |
| `crt0stack`: `Builder::new`, `push` each argument, `done` three times | 39.5 ns | 420.5 ns |
| `crt0stack`: `Reader::from_stack`, `done`, a sum of the lengths | 43.6 ns | 1,019.6 ns |

What each row includes:

- The `argv` rows read the stack the operating system built. Each `next` finds a string's end by
  scanning for its zero byte, and `iter` first scans the pointer array for a null.
- The `crt0stack` builder row writes into an 8,192-byte buffer aligned to 16 bytes, with no
  environment and no auxiliary value. Its reader row checks each argument as UTF-8.
- The `PageBuilder` row writes into one 4,096-byte page and includes clearing the header.
- No row includes mapping a page or starting a program.

## What was not run

- Kani, mutation testing and the fuzz workflow. The harness count is from source.
- No comparator's own tests, and no build of `origin`, `kernel-elf-parser`, `linux-loader`,
  `wasip1` or `lexopt`.
- `from_virtual_address` on a 32-bit target (P0-5): the host has no such target.
- `cargo +1.88 test`, the README's minimum Rust version.
- No WASI host, and no `execve` with a line past the limit: the review read both systems and ran
  neither.
