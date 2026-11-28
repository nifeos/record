# What the review read and ran

An appendix to [the milestone](../1156-grant-contract-release-review.md).

## The crate

`partsfoundry/grant_contract` at `f84cd7e6ff2efccbaf18988c584ff9bb7b32e4e7`, version 0.1.0, in a
fresh clone that the review left unchanged. Read in full: `Cargo.toml`, `README.md`,
`CHANGELOG.md`, `docs/stranger-test.md`, `src/lib.rs`, `src/manifest.rs` and `src/verbs.rs`. Read
in part: `src/manifest/tests.rs` and the two `verification.rs` files, for what they cover. Read
for one signature: the page iterator of `program_argument_contract` at the pinned revision
`b097970b`, which yields slices that borrow the page.

The review read no pull request, issue or lane report of the crate.

## The commands

Each ran with the build directory outside the clone, on a Linux x86_64 host with rustc 1.100.0.

- `cargo build` passes.
- `cargo test` passes: 16 unit tests, one test in each of the two integration files, and two
  doctests (the README's example and `delegated_identity`'s).
- `cargo +1.88 test` passes with the same counts.
- `RUSTDOCFLAGS="-D warnings" cargo doc --no-deps` passes.
- `cargo clippy --all-targets` prints no warning.
- The library builds for three bare targets with `cargo build --lib --target <t>`:
  `x86_64-unknown-none`, `aarch64-unknown-none-softfloat` and `riscv64imac-unknown-none-elf`.
- `cargo package --list --allow-dirty` lists 47 files. Sixteen are the sources, the tests, the
  README, the changelog, the two licenses and Cargo's own four files; 31 are the rest (P2-4).
- `grep -c 'kani::proof'` over the two `verification.rs` files counts three harnesses, the
  README's number.
- `grep -ohE '<pattern>' src/lib.rs src/manifest.rs src/verbs.rs | wc -l` gave the counts of
  P1-1: `grant_plan::` 21, `abi::` 8, `std_runtime_contract` 9, the word `jig` 23, `caps` in code
  font 4, `progenitor` 21, and the marker of P0-8 seven times.
- `git status --short` in the clone prints nothing after all of the above.

## The scratch crate

One crate outside the clone, depending on `grant_contract` by path. It printed the sizes
(`Manifest` 80 bytes, `ShortOptions` 17, `VerbGrant` 24, `ManifestAuthorities` 2) and showed:

- A table with the verb `list` twice: the first entry wins (P0-1).
- A table entry of 26 bytes and an empty one: both match a `verb` argument of the same bytes.
- A verb granted `DOMAIN` under a manifest that does not declare it: the field stays false, and
  nothing reports the mismatch.
- A verb granted `INDEXES_WRITE` without `INDEXES`: the index store is `Forbidden`, as documented.
- An empty table: the manifest comes back whole (P0-2).
- A manifest with `BytesAndDiagnostics { slot: ENTROPY_SLOT }` and a memory range of 9 to 1:
  `is_well_formed` answers true (P0-3, P0-4).
- Both paths of `narrow_by_verb` compile (P0-5).
- `page_verb` on an empty page and on three bytes, and `delegated_identity` on a page of `0xff`
  bytes: each answers `None`.

## The comparators read

Each `.crate` came from crates.io at the version named, into its own directory.

- `tauri-utils` 2.10.4, the `acl` module: `mod.rs` (`Permission`, `Commands`, `Scopes`,
  `PermissionSet`, `Error`), `manifest.rs` (`Manifest`), `capability.rs` (`Capability`),
  `identifier.rs` (`Identifier`, `ParseIdentifierError`) and the command loop of `resolved.rs`.
  A plugin's manifest names permissions, each a list of commands to allow or deny with a scope. A
  capability file grants permissions to windows. The types hold `String`, `Vec` and `BTreeMap`,
  derive `serde` traits and often `Default`, and report failure through `thiserror` enums with
  named fields.
- `deno_permissions` 0.119.0, `lib.rs`: `PermissionsOptions`, `PermissionState`,
  `ChildPermissionsArg`, `ChildPermissionError` and `create_child_permissions`, which returns
  `Escalation` when a child asks for more than its parent holds.
- `pledge` 0.4.2, all three source files: a `Promise` enum generated from the manual page, a
  `pledge` function that passes two optional strings to the system call, and an `Error` enum with
  `Display` and `Error`. It needs `std` and `libc`.
- `bitflags` 2.13.2, `src/traits.rs`: the method names of the `Flags` trait, for P1-4 and P2-2.

The review measured four neighbors and read none. `landlock` is in the block's table. `cap-std`
4.0.3 has 37,324,536 downloads, 19,185,273 in 90 days, and 370 reverse dependencies. `getopts`
0.2.24 has 189,227,111, 42,416,849 and 528. `caps` 0.5.6 has 28,954,845, 5,990,123 and 84. The
crates.io record of `tauri-utils` gives 3.0.0-alpha.4 as its highest version; the review read
2.10.4, the newest stable one. Ten crates.io searches,
each sorted by recent downloads, found no closer crate:

- `capability manifest`, `permission manifest`, `sandbox manifest` and `privilege manifest`;
- `pledge`, `capabilities declare`, `capability no_std` and `entitlements`;
- `subcommand permissions` and `component manifest capabilities`.

## The system outside Rust

OpenBSD's source tree at commit `2bdf38a9e2f60c1bbcdef6772a9bd22e5ffb5b12`, five files fetched
one at a time from the project's public mirror.

- `sys/sys/pledge.h` (revision 1.55): 36 promise bits in a `uint64_t`, and `pledgenames`, the
  table from each bit to its name.
- `sys/kern/kern_pledge.c`: `parsepledges` splits the string at spaces and returns `EINVAL` for an
  unknown name. `sys_pledge` returns `EPERM` when the new set holds a bit the current one lacks.
- `lib/libc/sys/pledge.2`: the promises, the rule that a later call can only reduce, and the
  empty string that leaves `_exit`.
- `bin/rm/rm.c`: one promise set with `wpath` under `-P` and one without it.
- `usr.bin/ftp/main.c`: three promise sets, one for each way of invoking the program.

The files are ISC and BSD licensed; the review read them for their interface shape only.

## The measurement

The scratch crate above, `cargo run --release`, on a Linux x86_64 host (an Intel Xeon Platinum
8160 at 2.10 GHz) with rustc 1.100.0. Each row starts at 64 repeats and doubles until one pass
lasts 50 ms. It then times seven passes and reports the lowest, divided by the repeat count.
Inputs and results pass through `black_box`.

- The manifest declares seven fields a verb can take away. The table holds eight verbs, `list`,
  `install`, `remove`, `update`, `search`, `show`, `rollback` and `list -u`, each granted the
  catalog.
- The first row looks up `list -u`, the last entry. The second looks up `zzz -u`, which misses
  twice. Each row includes the copy of the 80-byte result.
- The page rows parse a 4096-byte page holding `jig`, `install`, `--within`, `lab-runner` and
  `greeting`. Each includes the parse and the copy into the output array.
- The last row builds an option set from sixteen distinct letters.

No comparator ran in the loop: none performs these operations on these inputs.

## What was not run

- Kani and mutation testing, by the review's rules. The harness count is from source.
- The naming helpers of the shared workflows. The review read the names against the naming page.
- The review built and ran no comparator.
- The crate's stranger run (`docs/stranger-test.md`) did not happen as such; the commands above
  cover its build and test steps and none of its proof steps.
