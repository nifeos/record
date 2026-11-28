# What the review read and ran

An appendix to [the milestone](../1164-file-system-contract-release-review.md).

## The crate

`partsfoundry/file_system_contract` at `05515061699d24510ddffa7ef561c9f344227333`, version 0.1.0,
no tag, a fresh clone of `main`. The census of milestone 1129 (the combine review) counted it at
the same commit. The repository is a workspace of two crates. The review covers
`file_system_contract/`; of `file_system_fixture/` the lane read the head of the manifest and of
the README, which say the crate is test data and never publishes.

The lane read in full: the root `Cargo.toml` and `README.md`, and in the crate `Cargo.toml`,
`README.md`, `CHANGELOG.md` and eleven source files: `lib.rs`, `error.rs`, `block.rs`,
`file_system.rs`, `directory.rs`, `directory_entry.rs`, `volume_statistics.rs`, `nameset.rs`,
`verb.rs`, `grant.rs` and `extended_attribute.rs`. It read the first three harnesses of
`proofs.rs` and the names of the other seven, the head of `.github/mutants-exempts`, the last
line of `docs/stranger-test.md` and the names of the five fuzz targets. It read no test file.

## The commands

The lane ran each command on a Linux x86_64 host with rustc 1.100.0 and kept every build's
output in a `CARGO_TARGET_DIR` beside the clone, never in it. The clone's `git status --short`
was empty at the end. The first four commands ran at the workspace root.

- `cargo build` passes. `cargo` warns that `package.homepage` repeats `package.repository`
  (P2-4).
- `cargo test` passes: 81 unit tests and 7 doctests in the contract, and 23 tests and 1 doctest
  in the fixture.
- `RUSTDOCFLAGS="-D warnings" cargo doc --no-deps` passes with no warning.
- `cargo clippy --all-targets` passes with no warning, under the root's `clippy.toml`.
- `cargo build -p file_system_contract --lib --target` passes with `x86_64-unknown-none`, with
  `aarch64-unknown-none-softfloat` and with `riscv64imac-unknown-none-elf`.
- `cargo package --list --allow-dirty` in the crate's directory lists 48 files: the sources, 15
  falsification patches, the two licenses and no CI file.
- The crate declares no features, so there is one feature combination.
- `grep -rc 'kani::proof' src` counts 15 harnesses: 10 in `proofs.rs`, 3 in `directory.rs` and
  2 in `error.rs` (P1-4).
- `grep -c 'pub fn\|pub const fn'` over the library sources counts 66 public functions. `grep`
  finds six `# Examples` headings, five `# Panics` and no `# Errors` (P1-2).
- `grep -n 'RedoxFS\|redoxfs'` over the sources and the README finds nine lines (P1-3).
- `grep 'derive'` finds four: on `Operand`, `Verb`, `Policy` and `Rights` (P1-5).

A scratch program that depends on the crate by path printed, in a release build:

- `block::READ`, `file_system::READ`, `directory::rights::READ` and `grant::rights::READ` are 1,
  2, 2 and 1. The four `WRITE` constants are 2, 3, 4 and 2 (P0-1).
- `file_system::request(block::READ, 0, 4)` has the operation `OPEN` (P0-1).
- `Rights::root(grant::rights::WRITE)` allows `directory::rights::READ` and not
  `directory::rights::WRITE` (P0-1).
- `file_system::request(file_system::READ, 1024, 3)` decodes as handle 1024 and length 3 (P0-1).
- `file_system::request(257, 3, 10)` has operation 1, and `block::request(0x102, 1)` operation
  2. `request(0x1ff)` has operation 255 (P0-2).
- `block::request(block::READ, 4) | 0xabc << 8` decodes as a count of 4 and operation 1 (P0-3).
- `rename_destination(7, 5) | 0xff << 56` decodes as handle 7 and length 5 (P0-3).
- A request built with `MAXIMUM_LENGTH_BYTES` decodes as a length of 1099511627775, against
  `MAXIMUM_TRANSFER_BYTES` of 65536 (P0-3).
- A listing of three records, cut two bytes short, yields two entries. A record whose flags
  byte is `0xfe` reads as not a directory (P0-3, P1-1).
- `let t: [verb::Verb; 23] = verb::TABLE` compiles, and so does a `Verb` written as a struct
  literal with its seven fields (P0-4).
- `verb::of(0)`, `verb::of(24)` and `verb::of(file_system::BIND)` are `None`.
- A store of three attributes holds 27 bytes and counts 3. With bit 31 of the second record's
  kind set it counts 1. `store::set` of the first name on that blob returns 9 bytes, and the
  third attribute is absent from the result (P1-1).
- `store::set` with an empty name is `Err(34)`, `store::remove` of an absent name `Err(61)`, and
  `store::set` with a kind of `0x8000_0000` `Err(22)` (P0-5).
- `explain(95)` is "this capability does not carry extended attributes". `explain(71)` and
  `explain(5)` are "the filesystem refused" (P1-6).
- A hand-built name set of ten records counts 8, and the tenth name is not in it.
- `grant::specification_len(0xff)` is 255, and `grant::unpack_name` with a length of 255
  returns 16 (P2-2).
- `{:?}` of `Rights::root(REMOVE_TREE)` is `Rights(49)`. `Rights` is 8 bytes, `Verb` 48 and
  `Policy` 8 (P1-5).

## The contract layout, item by item

In the crate's spellings, for the contract-layout decision of milestone 1129:

- Two interfaces in one crate, each a module: `block` and `file_system`.
- Magic: none.
- Version: `VERSION: u32 = 1` in each module. It is in no message.
- Identity: `block::INTERFACE_ID: u64 = 14` and `file_system::INTERFACE_ID: u64 = 15`.
- Opcodes: bare constants in the module (`file_system::OPEN`), with no `OPERATION_` prefix.
  `OPERATION_SHIFT: u32 = 56` sits at the root.
- Request builders: `request(operation)` at the root, `block::request(operation, blocks)` and
  `file_system::request(operation, handle, len)`, with `rename_destination` and two
  `specification` functions for a second word.
- Decoders: `operation(w0)` at the root and one function for each field. One of them,
  `block::request_block_count`, returns `Option`. No function decodes a whole request.
- Replies: `error::word` and `error::code` for the first word, and `extended_attribute::reply`
  with its two readers.
- Beyond the words: `verb::TABLE`, five record encodings, and the readiness words `READY` and
  `DESCENT_REFUSED`.

## The search for a comparator

On 2026-11-26 (UTC), `https://crates.io/api/v1/crates?q=<words>&sort=recent-downloads&per_page=8`
for each of: "9p protocol", "fuse protocol", "filesystem protocol no_std", "file server
protocol", "block device trait", "virtio blk", "capability filesystem" and "nfs protocol". The
lane also measured by name `fuser`, `p9`, `rs9p`, `ninep`, `nine`, `fuse-backend-rs`,
`polyfuse`, `fuse3`, `nfsserve`, `russh-sftp`, `cap-std`, `virtio-drivers`, `embedded-sdmmc`,
`embedded-storage`, `block_device`, `zerocopy`, `vhost-user-backend` and `wasi`.

Five crates publish the messages of a file service and draw more than 10,000 downloads in 90
days: `russh-sftp` (2,586,407), `fuser` (2,222,734), `fuse-backend-rs` (1,538,329), `nfsserve`
(1,041,355) and `p9` (61,504). The first three rank. The lane read `p9` as well, because 9P is
the nearest protocol in shape: handles a server checks, a walk by name, and no path from a
global root. `rs9p` 0.13.0 (220), `ninep` 0.6.0 (1,130) and `nine` 0.5.0 (220) fall under the
floor. No crate found puts rights on a handle.

## The comparators read

The six crates are the `.crate` files `static.crates.io` serves for the versions in the
block's table, each unpacked alone in an empty directory.

- `russh-sftp` 4.0.0: `src/lib.rs`, `src/error.rs`, and in `src/protocol/` the files `mod.rs`,
  `status.rs`, `handle.rs`, `name.rs`, `version.rs` and `init.rs`, with the heads of `file.rs`,
  `open.rs` and `file_attrs.rs`. The module `protocol` is public. `Packet` is an enum of 27
  message structs with `TryFrom<&mut Bytes>`, built on `serde`. `StatusCode` is an enum under
  `thiserror`, and its `From<u32>` maps an unknown code to `Failure`. `SftpHandle` is a newtype
  over `Vec<u8>`. `OpenFlags` is a `bitflags` type. `Init` and `Version` carry a version number
  and a map of extensions. `Error` has five variants that each hold a `String`. The features
  are `async-trait` and `raw-string`. It needs `std`, `tokio`, `serde` and `bytes`.
- `fuser` 0.19.0: `src/ll/mod.rs`, the heads of `src/ll/fuse_abi.rs` and `src/ll/request.rs`,
  `src/access_flags.rs` and the exports of `src/lib.rs`. The wire structs and the opcode enum
  are `pub(crate)` in `fuse_abi`. The public surface is typed: `Errno(NonZeroI32)` with a
  constant for each code and `From<std::io::ErrorKind>`, `INodeNo(pub u64)`, `FileHandle(pub
  u64)`, `Generation(pub u64)`, `Version(pub u32, pub u32)`, and a `bitflags` type for each
  flag word. `RequestError` is private, has four variants, two of which carry lengths, and
  implements `Display` and `Error`. An unknown opcode is `UnknownOperation(u32)`.
- `fuse-backend-rs` 0.14.0: the head of `src/abi/fuse_abi_linux.rs` and its `Opcode`, `InitIn`
  and `Dirent`. `KERNEL_VERSION` is 7 and `KERNEL_MINOR_VERSION` 33. `Opcode` is a public
  `#[repr(u32)]` enum whose `From<u32>` maps an unknown number to `MaxOpcode`. The flag words
  are `bitflags` types. `InitIn` carries `major` and `minor`.
- `p9` 0.3.2: `src/lib.rs`, `src/protocol/mod.rs`, and the heads of `src/protocol/messages.rs`
  and `src/protocol/wire_format.rs`. The module `protocol` is private, and the public surface
  is the server and one fuzzing entry point. `Tmessage` is an enum of message structs with
  named fields. `WireFormat::decode` takes a `std::io::Read` and returns `std::io::Result`.
  `P9String` holds a `CString`, and `Twalk` a `Vec<P9String>`. `Rlerror` carries `ecode: u32`.
- `cap-std` 4.0.3: the head of `src/fs/dir.rs`. `Dir` wraps an open directory, and `open`,
  `open_dir`, `create_dir` and `read_dir` resolve beneath it. The one way in from a path is
  `open_ambient_dir`.
- `virtio-drivers` 0.13.0: the item list of `src/device/blk.rs` and `Error` in `src/lib.rs`.
  `read_blocks(block_id, buf)`, `write_blocks`, `flush` and `capacity`; `SECTOR_SIZE` is 512;
  `RespStatus` is a newtype over `u8`; `Error` is one enum under `thiserror`.
- `nfsserve` and `embedded-storage`: measured, not downloaded, not read.

## The systems outside Rust

Each file came from a public mirror at the named commit.

- 9front at `d7e009b7866219fa6b2302941b939759ef2c2b68`, `sys/man/5/version` and
  `sys/man/5/walk`. `Tversion` carries `msize`, the largest message either side will send, and a
  version string; a server that does not know the string answers `unknown`. `Twalk` carries at
  most sixteen names, the constant `MAXWELEM`. The lane fetched `sys/man/5/0intro` and did not
  read it.
- Fuchsia at `8ff2539fd32def0c2b9ed84b8c8873c31af81d22`,
  `sdk/fidl/fuchsia.io/rights-abilities.fidl` and the `Flags` type of `directory.fidl`.
  `Operations` is `flexible bits : uint64` with nine members, `ENUMERATE`, `TRAVERSE` and
  `MODIFY_DIRECTORY` among them. A permission a connection lacks fails the request with
  `ZX_ERR_ACCESS_DENIED`. `PERM_INHERIT_WRITE` asks for the parent's write rights where it has
  them, and each server must remove the flag where the parent lacks one.

## The benchmark

A scratch crate outside the clone depends on `file_system_contract` by path and `russh-sftp` at
`=4.0.0`, with `bytes` 1.12.2, `serde` 1.0.229 and `tokio` 1.54.1 resolved. The command is
`cargo build --release` and then the binary. The host is Linux x86_64, an Intel Xeon Platinum
8160 at 2.10 GHz with 80 threads, rustc 1.100.0. The benchmark runs on one thread.

Each measurement starts at 64 calls and doubles the count until one pass lasts 50 ms. It then
runs seven passes and reports the lowest, divided by the count. `black_box` wraps the input
buffer and the sum of the results. The input is 100 names of 12 bytes, `file-0000000` to
`file-0000099`.

| measurement | what a call includes | run 1 | run 2 |
|---|---|---|---|
| `directory_entry::iter` | a walk of 1,400 bytes that sums each name's length and flag | 204 ns | 215 ns |
| `Packet::try_from(&mut Bytes)` | a clone of the `Bytes` handle, the decode of one `Name` of 2,409 bytes into a `Vec` of 100 `File`, the same sum, and the drop | 13,904 ns | 13,711 ns |
| `directory_entry::encode`, 100 times | the fill of a zeroed 4,096-byte array | 918 ns | 609 ns |
| `Bytes::try_from(Packet::Name)` | 100 `String` clones, the `Vec`, the encode into 2,413 bytes, and the drop | 9,580 ns | 6,773 ns |

The block's table gives run 1. Each SFTP file carries an empty long name and an attribute
record with no field set, the smallest the message allows. The two write rows moved by a third
between runs, and the lane did not find why.

A second scratch crate, on the crate alone, with the same loop:

| measurement | run 1 | run 2 |
|---|---|---|
| `file_system::request`, then the three field readers | 2.26 ns | 2.56 ns |
| `verb::of`, then two fields | 3.16 ns | 3.30 ns |
| `error::code` | 2.91 ns | 3.46 ns |
| `store::get`, the last of 16 attributes with 20-byte names and 60-byte values | 83 ns | 86 ns |
| `store::set`, replacing that attribute | 227 ns | 241 ns |

The lane ran no comparison with `fuser` 0.19.0 or `p9` 0.3.2: `fuser` keeps `ll::fuse_abi`
`pub(crate)`, and `p9` keeps `protocol` private, so no outside crate can call either decoder.

## What the lane did not run

- Kani and the falsification replay; the harness and patch counts are from the source.
- The five fuzz targets.
- Mutation testing.
- The build at the minimum Rust version, 1.88.
- Any server or client of the two protocols.
- The tests of the comparators.
