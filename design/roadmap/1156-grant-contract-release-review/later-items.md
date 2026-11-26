# The later items

An appendix to [the milestone](../1156-grant-contract-release-review.md): its P2 findings, which
may follow the first release. Each is two-way, and each takes half a day.

## P2-1. No proof covers the functions that read a page

Verified in source; Kani not run.
The three harnesses cover `ShortOptions::try_new`, `is_well_formed` and `narrow_by_verb`.
`verb_key`, `page_verb` and `delegated_identity` copy bytes from a page another program wrote into
fixed arrays, and host tests alone cover them.
Change: a harness showing that `verb_key` never writes past its array and returns a key of at most
sixteen bytes, with its falsification patch.

## P2-2. Names for the authorities

Verified in the comparators' source.
OpenBSD's `pledge.h` keeps `pledgenames`, a table from each bit to its name, for the kernel and
for tools. `bitflags` 2.13.2 has `iter_names` and `from_name`. Here a tool that prints what a verb
holds writes its own table of twelve names.
Change: an iterator over the set bits with their names, and a lookup by name. Both are additions.

## P2-3. No test pins the rights numbers

Verified in source; the README's BUGS section says the same.
`WordGrant::rights` spells five rights as numbers that another contract crate defines.
Change: a development dependency on that crate, once crates.io has it, and one test that compares
the five.

## P2-4. The package carries the repository's tooling

Verified by `cargo package --list --allow-dirty`, which lists 47 files.
Thirty-one are repository files: workflows, hooks, falsification patches, lint configuration and
contributor documents.
Change: an `include` list of `src/`, the README, the changelog and the licenses.

## P2-5. The manifest has no `documentation` key

Verified in `Cargo.toml` (C-METADATA). Change: add it.

## P2-6. Two getters are not `const`

Verified in source.
`OutputDeclaration::is_byte_stream` and `diagnostics_slot` are plain functions, where `rights`,
`hears_words`, `letters` and `is_well_formed` are `const fn`. A constant assertion over a table of
manifests cannot call the two.
Change: `const fn` on both.
