# What the review read and ran

An appendix to [the milestone](../1163-environment-contract-release-review.md).

## The crate

`partsfoundry/environment_contract` at `62ea88d90aeaf00b718d49ceb445de1d108722c5`, version 0.1.0,
no tag, a fresh clone of `main`. The census of milestone 1129 (the combine review) counted the
same commit. The lane read in full: `Cargo.toml`, `README.md`, `CHANGELOG.md`,
`docs/stranger-test.md`, `src/lib.rs` lines 1 to 520 (the library), `.cargo/mutants.toml` and
`.github/mutants-exempts`. It read the test names in the rest of `src/lib.rs` (931 lines in all)
and the first harness and the module documentation of `src/verification.rs`.

It read the baseline first: the block of milestone 1089 (what an outside maintainer would fix
before it leaves) and the cleared package, for the Done findings, the frozen identity and the
ratified names. [design/naming.md](../../naming.md) and its pages carry two rules dated after
the ratification of 2026-11-19 (UTC): the spelling of `virtual_io` and the words `right` and
`permission`. Neither touches a name of this crate.

## The commands

Each command below ran in the clone of `environment_contract`, on a Linux x86_64 host with rustc
1.100.0, and wrote its build to a directory outside the clone. `git status --short` showed the
clone clean afterward.

- `cargo build` passes.
- `cargo test` passes: 19 unit tests and 3 doctests.
- `RUSTDOCFLAGS="-D warnings" cargo doc --no-deps` passes with no warning.
- `cargo clippy --all-targets` passes with no warning.
- The README's three bare-metal builds of `environment_contract` pass: `cargo build --lib
  --target` with `x86_64-unknown-none`, `aarch64-unknown-none-softfloat` and
  `riscv64imac-unknown-none-elf`.
- `cargo package --list --allow-dirty` lists 40 files. Of them, 21 are under `.github/`,
  `.githooks/` or `.cargo/`, or named `.gitignore` (P2-5).
- `grep -c 'kani::proof' src/verification.rs` prints 2, and `falsifications/` holds 2 patches, as
  the README says.
- `grep -n '# Panics\|# Errors\|# Examples\|# Safety' src/lib.rs` prints `# Examples` at lines
  169, 366 and 436 and `# Safety` at line 472 (P1-3).
- `grep -rn include_str src` prints nothing, so no test compiles the README's example (P1-3).
- The crate declares no features, so there is one feature combination.

A scratch program that depends on the crate by path printed:

- `PageBuilder::new().time_zone("utc")` is `Err(UnknownTimeZone)`, and `locale("en_US.utf8")` is
  `Err(UnknownLocale)` (P2-4).
- `time_zone("Europe/Madrid")` is `Err(UnknownTimeZone)`, and its `Display` is "TZ is not a
  member of KNOWN_TIME_ZONES" (P0-5).
- A 4096-byte frame reaches `ConfigurationView::new` only through
  `frame[..PAGE_CONTENT_BYTES].try_into().unwrap()` (P1-6).
- `time_zone()` is `None` on a zeroed frame, on a page whose magic ends in `2` and on a page
  whose field holds `XYZ`; `locale()` is `None` on a page that never set it (P0-4).
- `{:?}` of a `ConfigurationView` is `ConfigurationView { page: [69, 78, 86, ...] }` with all 107
  bytes in decimal (P1-2). `{:?}` of a `ConfigurationPage` prints its address.
- `size_of` is 48 bytes for `PageBuilder`, 8 for `ConfigurationView` and 1 for `Refused`.
- Two calls of `time_zone` on one builder keep the second value.

Two more scratch programs did not compile, as the findings say:

- A builder returned from a block that owns its `String` fails with E0597, "`s` does not live
  long enough" (P0-1).
- `const P: [u8; PAGE_CONTENT_BYTES] = B.build()` fails with E0015 (P2-3).

## The search for a comparator

On 2026-11-26 at 23:12 (UTC),
`https://crates.io/api/v1/crates?q=<words>&sort=recent-downloads&per_page=8` for each of:
"environment block", "process environment page", "environment variables no_std", "auxiliary
vector", "time zone locale", "config page", "fixed layout page" and "processargs". No result
publishes a page or a message that hands a process its environment. The lane then measured twelve
crates a stranger might reach for and kept four as neighbors. It set these aside:

| crate | version | total | 90 days | reverse dependencies | updated | why set aside |
|---|---|---|---|---|---|---|
| `bytemuck` | 1.25.2 | 504,649,085 | 156,761,109 | 4,797 | 2026-07-19 | the same job as `zerocopy`, which leads it |
| `arrayvec` | 0.7.8 | 731,364,861 | 198,482,924 | 1,283 | 2026-07-02 | the same job as `heapless`'s string |
| `jiff` | 1.0.3 | 309,221,371 | 136,224,053 | 2,535 | 2026-11-24 | reads a zone database; it does not close a list |
| `iana-time-zone` | 0.1.65 | 860,545,127 | 228,188,714 | 133 | 2026-01-28 | asks the host for its zone |
| `terminfo` | 0.9.0 | 50,441,940 | 19,299,660 | 29 | 2024-05-08 | reads a terminal database from files |
| `sys-locale` | 0.3.2 | 47,130,870 | 17,192,334 | 385 | 2024-11-01 | asks the host for its locale |
| `origin` | 0.26.2 | 164,628 | 17,084 | 4 | 2025-05-15 | program start-up on Linux; it passes `envp` through |
| `auxv` | 0.3.3 | 83,406 | 1,993 | 0 | 2017-01-20 | `rustix` leads it and is current |

## The neighbors read

The lane downloaded the four neighbors' `.crate` files from `static.crates.io`, at the versions
the block's table gives, and unpacked each in a directory of its own.

- `rustix` 1.1.6, `src/param/auxv.rs` and `src/backend/linux_raw/param/auxv.rs`. The public
  functions (`page_size`, `clock_ticks_per_second`, `linux_hwcap`, `linux_minsigstksz`,
  `linux_execfn`) are safe and take no argument. Each carries `#[doc(alias)]` lines for the C
  names and a references section. The backend reads the vector once in `init_from_aux_iter`,
  which returns `Option<()>`, keeps each pointer in an `AtomicPtr`, and runs `check_elf_base` on
  the vDSO address before it stores a `NonNull`.
- `zerocopy` 0.8.66, `src/lib.rs` and `src/error.rs`. `FromBytes::ref_from_bytes` and
  `ref_from_prefix` return `CastError<&[u8], Self>`, and `TryFromBytes::try_ref_from_bytes`
  returns `TryCastError`. `SizeError`, `AlignmentError` and `ValidityError` each have `into_src`
  and implement `Error`. Its manifest's features are `alloc`, `std`, `derive`, `simd`,
  `simd-nightly` and `float-nightly`.
- `heapless` 0.9.4, `src/lib.rs` and `src/string/mod.rs`: `String<N>` implements `FromStr`,
  `push_str` returns `Result<(), CapacityError>`, and `CapacityError` is a unit struct with
  `core::error::Error`. Its manifest names a feature `embedded-io-v0.7`.
- `chrono-tz` 0.10.4, `src/lib.rs` and `src/prebuilt/timezones.rs`. `Tz` is an enum that
  derives `Clone`, `Copy`, `PartialEq`, `Eq` and `Hash`, with one variant for each name.
  `TZ_VARIANTS` holds 597 of them, and the longest name the lane looked for,
  `America/Argentina/ComodRivadavia`, is among them. `FromStr` looks a name up in a `phf::Map`
  and returns `ParseError(())`, which has `Display` and implements `std::error::Error` under the
  `std` feature alone. `Tz::name` returns `&'static str`. The features are `std`,
  `case-insensitive`, `filter-by-regex` and `serde`, and the crate depends on `chrono` and `phf`.

## The systems outside Rust

- Linux v6.12, `include/uapi/linux/auxvec.h`: the `AT_*` keys, 0 to 31 and 51, with 18 to 22
  reserved and `AT_NULL` ending the vector. Also `fs/binfmt_elf.c`, `create_elf_tables`: the
  `NEW_AUX_ENT` lines, then `argc`, the `argv` pointers, a zero, the `envp` pointers and a zero.
  The environment strings are whatever `execve` received.
- Fuchsia at commit `8ff2539fd32def0c2b9ed84b8c8873c31af81d22`, the head of its main branch on
  2026-11-26 (UTC), `zircon/system/public/zircon/processargs.h`: `ZX_PROCARGS_PROTOCOL`
  (`0x4150585d`), `ZX_PROCARGS_VERSION` (`0x0001000`) and `struct zx_proc_args`, whose `protocol`
  and `version` fields lead the message and whose `environ_off` and `environ_num` locate
  null-terminated strings. Its comment says each string canonically has the form `NAME=VALUE`
  and that nothing enforces this.
- musl v1.2.5, `src/time/__tz.c`: `do_tzset` reads `TZ` with `getenv`. For a value that is not
  in POSIX form it maps an absolute or dotted path only when the program is not secure, or when
  the path is `/etc/localtime`. It searches the standard directories for any other name of at
  most `NAME_MAX` bytes that has no dot.
- glibc 2.40, `sysdeps/generic/unsecvars.h`: `UNSECURE_ENVVARS`, 33 variable names removed for a
  program that runs with raised privilege, `TZDIR` among them.

The Linux and glibc files are GPL and LGPL; the review read them for the shape of what they
publish only.

## The benchmark

A scratch crate that depends on `environment_contract` by path, on `zerocopy` at `=0.8.66` with
its `derive` feature and on `chrono-tz` at `=0.10.4` without default features. The command was
`cargo run --release`, on a Linux x86_64 host with an Intel Xeon Platinum 8160 at 2.10 GHz, 80
threads and rustc 1.100.0.

Each row is one closure. The loop starts at 64 repeats and doubles the count until a pass lasts
50 ms. It then times seven passes and reports the lowest, divided by the count. Every input and
every result passes through `std::hint::black_box`.

- The pages: one with `UTC`, `C` and `dumb`, the first member of each list; one with
  `Pacific/Auckland`, `pt_BR.UTF-8` and `tmux-256color`, the last member of each; one zeroed.
- The reader rows build a `ConfigurationView` and call the accessor inside the closure.
- The `zerocopy` rows read through a struct the lane wrote with the page's seven fields,
  `#[repr(C)]` and the derives `FromBytes`, `KnownLayout`, `Immutable` and `Unaligned`. The
  closure calls `ref_from_bytes`, compares the magic, checks the length byte against the field,
  and calls `core::str::from_utf8` on the field's bytes. It searches no list.
- The writer row calls `PageBuilder::new`, the three setters and `build`.
- The lookup rows call `domain::is_known_time_zone` and `str::parse::<chrono_tz::Tz>` on
  `Pacific/Auckland`. A refused name, `Europe/Madrid`, took 4.4 ns in `is_known_time_zone`.

The block's table has the nine results. What each includes:

- A `time_zone` row: the magic check, the length check and the list search, over 1 member for
  `UTC` and all 20 for `Pacific/Auckland`. The zeroed frame stops at the magic check.
- The three-accessor row: three magic checks and three searches.
- A `zerocopy` row: `ref_from_bytes`, the same two checks and `core::str::from_utf8`.
- The writer row: three searches, then zeroing and filling 107 bytes.
- `is_known_time_zone`: a linear search. `Tz::from_str`: a perfect-hash lookup among 597 names.

## What the lane did not run

- Kani and the falsification replay; the harness and patch counts are from the source.
- Mutation testing, and Miri.
- A build for a 32-bit target: the host has none installed, so P0-2's truncation is inferred.
- The build at the minimum Rust version, 1.88; the baseline's stranger run covers it.
- The tests of the neighbors.
