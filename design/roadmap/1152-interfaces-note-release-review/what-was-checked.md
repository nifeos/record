# What the review read and ran

An appendix to [the milestone](../1152-interfaces-note-release-review.md).

## The crate

`partsfoundry/interfaces_note` at `088baba279e29e6cd5a9ff5a73c57108cacc54c3`, version 0.1.0 with
`publish = false`. Read: `Cargo.toml`, `README.md`, `CHANGELOG.md` and the whole of `src/lib.rs`,
which holds the library, three Kani harnesses and seven unit tests. The census of milestone 1129
(the combine review) counted the crate at this commit.

## The commands

Run with rustc 1.100.0 on a Linux x86_64 host, with the build directory outside the clone.

- `cargo build` and `cargo clippy` pass with no warning.
- `cargo test` passes: seven unit tests and five doctests.
- `cargo build --lib` passes for `x86_64-unknown-none`, `aarch64-unknown-none-softfloat` and
  `riscv64imac-unknown-none-elf`.
- `cargo doc --no-deps` passes with no warning.
- `cargo package --list --allow-dirty` lists 39 files, 20 of them under `.github/` and
  `.githooks/` (P2-6).
- `grep -c 'kani::proof' src/lib.rs` prints 3, the count the README states.
- `git status --short` in the clone prints nothing after all of the above.

## The scratch programs

One scratch crate depends on the clone by path and on `object` at `=0.41.0`. Each program below
is one file in it.

- A program that calls `carry_interfaces!` with two records, then reads its own file. It walks
  each program header's notes with `object`, matches the owner string and the type, and decodes the
  descriptor. It finds one note and prints both records, and `check_served` returns the refusal for
  a served version that differs. `readelf -n` on that program shows the note inside the `NOTE`
  segment the host's linker builds, under the label `GO BUILDID` (P1-3).
- A program with the macro at the crate root and again in a module. It compiles, and `readelf -n`
  shows two notes with the owner string (P0-3). With both calls in one module it fails with
  E0428, the duplicate name.
- The macro's body copied with `#[unsafe(no_mangle)]` added to the static, called in two modules.
  It fails to compile: the symbol is already defined (P0-3).
- A program that builds `InterfacesNote::<4>([0xff; 4])`, which compiles, and calls
  `encode_interfaces` and `InterfacesNote::of` at run time with a list out of order and with a
  wrong `LEN`. Both panic (P0-2, P2-1).
- A program that takes an `Error` as `&dyn core::error::Error`, prints one with `{}` and runs a
  `for` loop over an `Interfaces`. Each of the three lines fails with E0277 (P1-1, P1-6).

## The comparators read

The review downloaded each crate below from crates.io at the version the prior-art table gives,
unpacked it into a directory of its own and read the files named.

- `auditable-extract` 0.3.5, `src/lib.rs`: `raw_auditable_data(&[u8]) -> Result<&[u8], Error>`
  finds the section `.dep-v0` by name in an ELF, Mach-O, PE or WebAssembly file. Its `Error` has
  seven unit variants, `Display` and `std::error::Error`, and no `#[non_exhaustive]`. It depends on
  `binfarce`, and on `wasmparser` under the default feature `wasm`.
- `auditable-serde` 0.9.0, `src/lib.rs` and `src/validation.rs`: `VersionInfo`, `Package`, a
  `#[non_exhaustive]` `Source`, and `VersionInfo::from_str` over JSON.
- `stabby` 72.1.16, `src/libloading.rs` only: the trait `StabbyLibrary`, whose `get_stabbied`
  looks up a symbol with a fixed suffix and calls it with a type report, and whose errors are
  `Box<dyn std::error::Error + Send + Sync>`.
- `abi_stable` 0.11.3, `src/library/errors.rs`, `src/library/lib_header.rs` and
  `src/sabi_types/version.rs`: `LibraryError`, with `IncompatibleVersionNumber { library_name,
  expected_version, actual_version }`, `Display` and `std::error::Error`; and
  `VersionNumber::is_compatible`, which orders versions as Cargo does.
- `solana-security-txt` 1.1.3, `src/lib.rs` and `src/parser.rs`: the public markers
  `SECURITY_TXT_BEGIN` and `SECURITY_TXT_END`, the macro `security_txt!`, whose static is
  `#[no_mangle]`, and `parse` and `find_and_parse` behind the feature `parser`.
- `object` 0.41.0, `src/read/elf/note.rs`: `NoteIterator` and `Note`, with `name`, `n_type` and
  `desc`. The scratch reader uses them.
- `goblin` 0.10.7, `src/elf/note.rs`: the headers `Nhdr32` and `Nhdr64` with no feature, and
  `NoteIterator` and `Note` inside `if_alloc!`.
- `elf` 0.8.0, `src/note.rs`: `NoteIterator`, and a `Note` enum with typed GNU notes and `NoteAny`.

Two more note walkers, measured at the same time as the prior-art table:

| crate | version read | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|
| `goblin` | 0.10.7 | 93,052,286 | 25,019,137 | 410 | 2026-05-28 |
| `elf` | 0.8.0 | 14,880,568 | 4,050,441 | 94 | 2025-05-14 |

The review measured `cargo-auditable` 0.7.8, the compiler wrapper, (1,579,261 downloads, 617,779 in 90
days, no reverse dependency, updated 2026-11-25) and did not read it. Searches of crates.io for an ELF
note writer by the names `elf-note`, `elfnote` and `elf_note` found no crate.

## The comparison

How the nearest five compare, read from each one's source:

| axis | `interfaces_note` | `auditable-serde` with `auditable-extract` | `abi_stable` 0.11.3 | `solana-security-txt` 1.1.3 | Linux `ELFNOTE` |
|---|---|---|---|---|---|
| what the binary carries | 12-byte records, id and version | compressed JSON, the dependency tree | a header the library exports | text between two markers | any value, under a name and a type |
| who places it | `carry_interfaces!` | a compiler wrapper | an attribute macro | `security_txt!` | the macro |
| a second record in one program | compiles, two notes | the reader takes one section by name | one root module for each library | a duplicate symbol, refused | any number, one per source line |
| how the reader finds it | not in the crate | `raw_auditable_data(&[u8])` | a symbol lookup | `find_and_parse(&[u8])` | the reader walks the notes |
| the check | equality per interface | none; a tool audits later | semantic-version order | none | none |
| `no_std`, no allocation | both | needs `std` | needs `std` | the macro only | not applicable |
| refusal type | two, no `Display` | `Display` and `Error` | `Display` and `Error`, named fields | `thiserror` | none |
| one encoding per value, proved | yes | no | no | no | no |

## The systems outside Rust

- Linux v6.12, `include/linux/elfnote.h`: `ELFNOTE(name, type, desc)` in assembly and
  `ELFNOTE32` and `ELFNOTE64` in C, which place a header, the name and the descriptor in the
  section `.note.<name>`, one note per source line.
- Linux v6.12, `include/xen/interface/elfnote.h`: the numbered note types a guest kernel carries
  for its hypervisor, among them `XEN_ELFNOTE_XEN_VERSION`, `XEN_ELFNOTE_FEATURES` and
  `XEN_ELFNOTE_SUPPORTED_FEATURES`, each with its descriptor's form in a comment.
- glibc 2.40, `csu/abi-note.c`: the note of type 1 under the owner `GNU`, four words naming an
  operating system and its earliest release. A search of `elf/dl-load.c` at that version for the
  note's names finds nothing that reads it.

The Linux headers are GPL and glibc is LGPL; the review read them for their interface shape only.

## The benchmark

A scratch crate depends on the clone by path and on `auditable-serde` at `=0.9.0`, built with
`cargo build --release`, rustc 1.100.0, on a Linux x86_64 host (an Intel Xeon Platinum 8160 at
2.10 GHz, 80 threads).

Each row runs a closure in a loop that starts at 64 repeats and doubles until one pass lasts
50 ms. Seven passes follow at that count, and the figure is the lowest pass divided by the count.
`std::hint::black_box` wraps every input and every result.

The results, in time per call:

| operation | 4 records | 64 records |
|---|---|---|
| `decode_interfaces` | 4.8 ns | 29.1 ns |
| `version_of`, the last id | 7.4 ns | 80.3 ns |
| `decode_interfaces` and `check_served`, the last id | 16.7 ns | 75.6 ns |
| `check_served` once for each record | 25.8 ns | 2,105 ns |
| one merge walk over `iter()`, the same answer | 13.0 ns | 190.9 ns |
| `auditable-serde`: `VersionInfo::from_str` | 970 ns | 15,199 ns |
| `auditable-serde`: `from_str` and a search for the last package | 949 ns | 15,287 ns |

The input is a list of 4 or of 64 records with ids 1, 4, 7 and so on, encoded once outside the
loop: 56 and 776 bytes. The rows:

- `decode_interfaces` on those bytes, returning the length.
- `version_of` for the last id, on a list decoded outside the loop.
- `decode_interfaces` then `check_served` for the last id.
- `check_served` once for each record's own id and version, on a decoded list.
- One loop over the same pairs that advances a peekable `iter()` and compares versions.
- `auditable_serde::VersionInfo::from_str` on JSON naming the same count of packages, each with a
  name, a version and a source: 234 and 3,588 bytes. The JSON is not compressed, so the row leaves
  out the decompression a reader of a real binary also pays.
- The same, then a linear search for the last package by name.

## What was not run

- Kani, mutation testing and the fuzz target.
- No comparator's own tests, and no build of `stabby`, `abi_stable` or `solana-security-txt`.
- No big-endian build (P2-5) and no bare-target program with a link script.
- `cargo +1.88 test`, the README's minimum-version check.
