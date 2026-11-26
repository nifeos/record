# Before the first release

An appendix to [the milestone](../1156-grant-contract-release-review.md): its P1 findings, which
land before the first release. Effort is S (half a day) or M (a day or two).

## P1-1. The documentation names about sixty items a stranger cannot find

Verified by `grep` over the three source files.
The item documentation names 21 paths under `grant_plan::`, 8 under `abi::` and
`std_runtime_contract` 9 times. It names `program_table`, `spawn_protocol`, `system_initializer`
and `capability_manifest_note`, and the programs `jig` (23 times) and `caps`. It says "the
progenitor" 21 times and defines it nowhere. It mentions a source directory, a "phase-1" and a
function `image_can_carry` that the crate does not hold. One example file name carries an
extension that spells the name of the system the crate came from. The README has none of these.
`grant_plan` is a sibling repository, reviewed in [1155](../1155-grant-plan-release-review.md); the
others are not on crates.io.
Change: each sentence says what a spawner, a planner or a shell does, in the README's words.
Door: two-way. Effort: M.

## P1-2. The README omits three things the crate's own stranger test asks for

Verified in source (`README.md`, `docs/stranger-test.md`).
`docs/stranger-test.md` says the README must name how long the proofs take, what a passing run
prints that looks alarming, and how to run and revert one falsification patch. The README names
none of the three. The same file records its last run as none.
Change: the three paragraphs, then one stranger run with its date. Door: two-way. Effort: S.

## P1-3. The dependency is a git revision

Verified in `Cargo.toml`.
The manifest names `program_argument_contract` by version 0.1.0 and by a git revision. A publish
resolves the version from crates.io alone, so this crate publishes after that one, whose review is
[1157](../1157-program-argument-contract-release-review.md). No type of the dependency appears in a
public signature here. Two functions use it, `page_verb` and `delegated_identity`.
Change: publish in order. Door: two-way. Effort: S.

## P1-4. Missing common traits and set operations

Verified in source (C-COMMON-TRAITS, C-CONV-TRAITS).
No type derives `Hash`. `ManifestAuthorities` has `union`, `contains`, `bits` and `from_bits`,
which are `bitflags` 2.13.2's spellings with the same meaning (`src/traits.rs`). It lacks that
crate's `intersection`, `difference` and `is_empty`, the `|` and `&` operators, and `Default`.
Narrowing is an intersection, and a caller cannot write one. `ShortOptions` has no
`TryFrom<&[u8]>`, and `ManifestAuthorities` has no `TryFrom<u16>`.
Change: `Hash` on every type, the three methods as `const fn`, `BitOr` and `BitAnd`, `Default` as
the empty set, and the two `TryFrom` implementations once D5 names their error. Door: two-way
(additions). Effort: S.

## P1-5. Two examples in the crate, and no `# Panics` heading

Verified in source and by `cargo test`, which runs two doctests (C-CRATE-DOC, C-EXAMPLE,
C-QUESTION-MARK, C-FAILURE).
The README's example and `delegated_identity`'s are the only two. The crate page shows no code,
since the crate includes the README for doctests only. `ShortOptions::new` panics on a bad set and
has no `# Panics` heading. `verb_key`, `page_verb`, `try_new`, `from_bits` and `is_well_formed`
have no example, and the one item example calls `unwrap`.
Change: the README as the crate page, an example on each of the five, and the heading. Door:
two-way. Effort: S.

## P1-6. Two narrowing rules live in a code comment

Verified in source (`narrow_by_verb` in `src/verbs.rs`).
`narrow_by_verb` keeps `console_input` only when the verb holds `INSTALLER`. A comment inside the
function body says so, and no documentation does. The fields `reboot` and `sync` have no bit, so a
program keeps them under every verb and under no verb. The documentation says so only as "what no
verb chooses".
Change: the first rule on `INSTALLER` and on `console_input`, and a list on `narrow_by_verb` of
the fields a verb cannot take away. Door: two-way. Effort: S.
