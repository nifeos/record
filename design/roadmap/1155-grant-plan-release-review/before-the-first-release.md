# Before the first release

An appendix to [the milestone](../1155-grant-plan-release-review.md): its P1 findings in full, read in
`partsfoundry/grant_plan` at `69aedfbc`. Effort and doors read as the milestone defines them.

## P1-1. Two name sets with the same names compare unequal

Verified by running the probe.
`NameSet` derives `PartialEq` over its whole byte array. `keep_smallest` drops a displaced name
by lowering the count and leaves its bytes behind. A batch in which a short name displaced a
200-byte one yields the same eight names as a set built by `try_push`, and `==` answers
`false`. `Batch`, `DirectoryGrant`, `Expansion` and `Endowment` derive their equality from it.
`DirectoryPath::ascend` zeroes what it pops for this reason, and its documentation says so.
Change: zero the bytes and the end of a dropped name, or compare the held names; and a test.
Door: two-way. Effort: S.

## P1-2. The crate has two rules for what a name is

Verified by running the probe.
`is_valid_file_name` refuses `/` and `\`. `navigation::is_valid_component` also refuses `:` and
the zero byte. `Name::new` and `NameSet` use the first, and a typed operand passes through the
second. So `a*` matched against a listing grants a file named `a:b`, and the planner
refuses the same name typed in full. Change: one rule, used by both. Door: two-way before the
first release.
Effort: S.

## P1-3. A refusal sentence carries the damage of a rename

Verified by running the probe.
`Refusal::ScopeCannotRestore.message()` ends "the commands need an isolated child, 'swish -c',
side is reserved and not built yet". The word before "is reserved" reads as a replaced
relative pronoun. Change: the sentence, and a test that reads every sentence for the old type
names. Door: two-way. Effort: S.

## P1-4. The crate's text names another tree's programs and dates

Verified in source, and `cargo doc` warns once.
Documentation names `swish::scope`, `jig`, `glob_grant_tests`, `least_authority_demo`,
`memory_grant_depleter` and a spawn protocol's `Activation::Vouch`, none of which a reader of
this repository can find. Two comments carry dates (2026-08-18 and 2026-09-27), and several say
what a verb was before its removal. One says "this OS" and one "in this tree". The
documentation of `Expansion::designated` links the private field `Expansion::at`.
Change: say each thing in the crate's own terms, state what holds now, and fix the link. Door:
two-way. Effort: S.

## P1-5. The crate page has no example, and no function has a failure section

Verified in source and by `cargo doc`.
`src/lib.rs` includes the README under `cfg(doctest)` only, so its example renders on no
documentation page. Five items carry an example (`line::split`, `word::Cursor`, `word::read`,
`job_operand`, `kill_operands`). `plan_against`, `Expander`, `DirectoryPath`, `ShellHoldings`,
`check_chain` and `Escalation` carry none. No function has an `# Errors` section, though 26
public functions return a `Result`, and none has `# Panics`. The examples use `unwrap`. The
README shows `use grant_contract::*` and does not say how to depend on that crate. 1094 left the
sizes of the planning values for the README, and it gives none: an `Endowment` is 4,344 bytes
and a `ShellHoldings` 3,312.
Change: the README as the crate page; an example on each item above; `# Errors` naming each
refusal a function returns; the sizes; the dependency lines. Door: two-way. Effort: M.

## P1-6. The package ships the repository's machinery

Verified by building: `cargo package --list --allow-dirty` lists 75 files, 18 of them under
`.github/`, with the commit hook, `CODEOWNERS`, `deny.toml` and the stranger-test record. The
manifest has no `include`. Change: an `include` naming `src/`, `examples/`, the README, the
changelog, both licenses and, if the proofs are to replay from the package, `falsifications/`
and `tests/`. Door: two-way. Effort: S.

## P1-7. Two unpublished crates stand in the public signatures

Verified in source and in `Cargo.toml` (C-STABLE).
`plan_against` takes `grant_contract::Manifest`, `Endowment` holds one, and
`write_argument_page` takes an array of `program_argument_contract::PAGE_BYTES`. Both crates are
at 0.1.0, pinned by git revision, and neither is re-exported. A caller names the same revision
in its own manifest, and a breaking release of either is a breaking release of this crate.
The README's example writes a `Manifest` literal of 24 fields. That type belongs to milestone
1156 (the release review of `grant_contract`),
[whose block](../1156-grant-contract-release-review.md) weighs it.
Change: this crate publishes after both, at versions that crates.io holds. The README states the
pairing. Adding a re-export later breaks no caller, so 0.1.0 needs none. Door: two-way.
Effort: S.

## P1-8. Two types have no `Debug`, no type has `Hash`, and nothing is `#[must_use]`

Verified in source (C-DEBUG, C-COMMON-TRAITS).
`Expander` and `TwoRoots` derive nothing, and `Cursor` has no `PartialEq`. No type derives
`Hash`, so no `Refusal`, `Name` or `DirectoryPath` keys a map. `grep -rn must_use src` finds
nothing. `DirectoryPath::descend` returns `false` when it did not move, and the probe's
`descend(b"a/b")` leaves the path at the root with no warning.
Change: `Debug` on `Expander`; `Hash` on the value types; `#[must_use]` on `descend`, `ascend`
and the predicates. Door: two-way. Effort: S.

## P1-9. `BUILTINS` omits two of the words `parse` answers

Verified in source.
`parse` answers twenty words as builtins. `BUILTINS`, which a shell completes from, lists
eighteen: `vouch` and `user` are absent. The test holds the list inside `parse`, not the reverse.
Change: one table that `parse` and `BUILTINS` both read. Door: two-way. Effort: S.
