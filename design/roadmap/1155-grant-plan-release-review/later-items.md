# The later items

An appendix to [the milestone](../1155-grant-plan-release-review.md): its P2 findings in full, read in
`partsfoundry/grant_plan` at `69aedfbc`. Effort and doors read as the milestone defines them.

## P2-1. The weekly fuzz job has no target, and one proof covers one byte

Verified in source.
`.github/workflows/fuzz.yml` runs weekly and the repository has no `fuzz/` directory. The
harness for `line::split` covers the empty line and lines of one byte, as the README says.
The probe ran three million generated lines through the line's entry points and found no panic.
Change: a fuzz target over `split`, `parse` and `plan_against`. Door: two-way. Effort: S.

## P2-2. No function spells a name back

Verified in source and by running the probe.
A shell that completes a name holding a space, or prints a command for a person to run, must
quote it. `shlex` has `try_quote` and `shell-words` has `quote`. Here a name that holds both
quote characters has no spelling at all (D10). Change: a function that writes a name as a word
into a caller's buffer, or answers that none exists. Door: two-way. Effort: S.

## P2-3. Bare `bool`s, and the conversion traits

Verified in source (C-CUSTOM-TYPE, C-CONV-TRAITS).
`kill_operands` returns `(bool, usize)`. `NameSet::one`, `try_push` and `iter` carry a bare
`bool` for "is a directory", `check_chain` takes one, and so does `resolve_steps`. `Name` has no
`TryFrom<&[u8]>` or `AsRef<[u8]>`, and `&NameSet` no `IntoIterator`. Change: named types for
the `bool`s, and the traits. A changed signature after 0.1.0 is a breaking release; the review
does not hold 0.1.0 for these. Door: two-way for the traits. Effort: S.

## P2-4. One limit has three constants

Verified in source.
`MAXIMUM_FILE_NAME_BYTES`, `expansion::MAXIMUM_NAME_BYTES` and `navigation::MAXIMUM_NAME_BYTES`
are one value, and `MAXIMUM_RENDERED_PATH_BYTES` equals `MAXIMUM_PATH_BYTES`. Change: say on
each that it is the other, or keep one. Door: two-way while both stay. Effort: S.

## P2-5. The manifest and `forbid(unsafe_code)`

Verified in `Cargo.toml` and in source.
The manifest has no `documentation` key, and its categories omit `no-std::no-alloc`. The crate
holds no `unsafe` and does not forbid it. Change: each. Door: two-way. Effort: S.

## P2-6. Two small edges

Verified by running the probe.
`rm_report::status(-1)` answers 18,446,744,073,709,551,615, since the cast extends the sign.
`parse(b"--mem 4")` answers `Run` with an empty program name. Change: a `u32` error number, or a
refusal of a negative one, if the module stays (P0-7); and a sentence on the empty name. Door:
two-way. Effort: S.
