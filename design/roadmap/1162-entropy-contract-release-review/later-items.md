# The later items

An appendix to [the milestone](../1162-entropy-contract-release-review.md): the evidence for its
P2 findings, read in `partsfoundry/entropy_contract` at `5150f14f`. The form is that of milestone
1129 (the combine review).

## P2-1. A `rand_core` adapter

Inferred from `rand_core` 0.10.1's `TryRng` (`src/lib.rs`) and from `getrandom` 0.4.3's `SysRng`
(`src/sys_rng.rs`), which implements it under the `sys_rng` feature. A type that holds the `CALL`
closure and implements `TryRng` through `fill_with` would hand this service to every consumer of
`rand`. `TryRng` requires `type Error: core::error::Error`, so the adapter needs P1-2 first. It
also needs a feature, whose name the feature-name decision picks. Door: two-way. Effort: S.

## P2-2. `readiness` does not take a slice

Verified by building. `readiness(&draw[..])` does not compile, since a slice yields `&u8` and the
parameter is `impl IntoIterator<Item = u8>`. An array works, and a slice needs
`.iter().copied()`. No example shows that form, and a backend that holds its first draw in a
buffer meets the error first. The change is to accept items that borrow a `u8`, or to show the
slice form in the example. Door: two-way. Effort: S.

## P2-3. The package ships the repository's CI files

Verified by building. `cargo package --list --allow-dirty` names 44 files, and 20 of them sit
under `.github/` or carry the name `.gitignore`. The manifest has no `include` and no `exclude`.
The change is an `include` list. Door: two-way. Effort: S.

## P2-4. `bring_up_failure` builds a word for a reserved step

Verified by building. `bring_up_failure(0)` returns `Ok(0xDEAD_0000_0000_0000)`. The contract
reserves step 0x00 and steps 0x13 to 0xff for later shared steps, and steps 0x01 to 0x0f belong
to each backend. The builder judges none of them, and its documentation does not say so. The
change is one sentence there. Door: two-way. Effort: S.

## P2-5. Every word is a bare `u64`

Verified in source. A request word, both reply words and a report word are each a `u64`, and
`reply` returns a tuple of two. `copy_delivered_bytes` takes a count that no type ties to the
word beside it, and `delivered_bytes(READY)` compiles. The words cross a system call as numbers,
so a newtype would wrap and unwrap at each `CALL`. Hubris hides the words behind a generated
stub. The block recommends no change at 0.1.0, as door D10. Effort: M if taken.
