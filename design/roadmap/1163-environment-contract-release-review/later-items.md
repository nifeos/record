# The later items

An appendix to [the milestone](../1163-environment-contract-release-review.md): the evidence for
its P1 and P2 findings, read in `partsfoundry/environment_contract` at `62ea88d9`. Each is
verified in source or by building. Line numbers are of `src/lib.rs`, and effort is S (half a day)
or M (a day or two).

## P1-1. No stated rule for what a new list member does to `VERSION` and to the crate's version

Verified in source and the README. The README says a pull request adds a member, and that a
fourth key is a new `VERSION`. Nothing says what a new member is. A reader built before the
member existed reads its key as `None`, so two programs built apart disagree without an error.
Nothing says what removing a member is, either. Linux never renumbers an `AT_*` key and adds new
ones at new numbers, and `chrono-tz` ships each release of the zone database as a new version of
the crate.
Change: a stability section stating the rule of door D8.
Door: one-way (D8). Effort: S.

## P1-2. `Debug` on `ConfigurationView` prints 107 numbers

Verified by building: `{:?}` of a view over a page with `TZ` set printed the 107 bytes in
decimal. The derive prints the field, and a reader of a log gets no key from it. Every accessor
answers only a list member, and the derived `Debug` is the one place the type shows anything
else.
Change: a `Debug` written by hand that prints the three accessors' answers.
Door: two-way. Effort: S.

## P1-3. No `# Errors` section, every example unwraps, and nothing compiles the README's example

Verified in source and by building. `grep` finds three `# Examples` headings and one `# Safety`,
and no `# Errors` on the three setters. The four examples call `unwrap`. `cargo test` runs three
doctests, and none is the README's example, so that example can drift. No accessor, no `domain`
function and no constant has an example, and the crate page has none. `rustix` gives `page_size`
its POSIX reference, and `zerocopy` gives `try_ref_from_bytes` an example.
Change: the `# Errors` sections, examples that use `?`, the README's example as a doctest, and one
example on the crate page.
Door: two-way. Effort: S.

## P1-4. The documentation uses terms a stranger cannot look up and never names the system

Verified in source and the README. The crate page, the README and the description say "a
process" and never say of which system. The page calls itself "the inert-configuration contract"
and does not define the term. Lines 6 and 432 say the page needs no seqlock, and line 151 says
the refusal is not an errno space; a stranger asked about neither. The second and third entries
of the crate page's BUGS section state properties, not bugs. The README has the layout, and the
crate page does not.
Change: one sentence that names the binary interface (door D9), a definition of the term, the
layout on the crate page, and the two properties moved out of BUGS.
Door: two-way, apart from D9. Effort: S.

## P1-5. Four public types lack `Hash`, and `ConfigurationPage` lacks `PartialEq`

Verified in source (lines 154, 195, 379 and 457). `Refused`, `PageBuilder` and
`ConfigurationView` derive `PartialEq` and `Eq` and no `Hash`. `ConfigurationPage` derives `Debug`,
`Clone` and `Copy` alone. `chrono-tz`'s `Tz` derives `Hash`.
Change: derive `Hash` on the three, and `PartialEq`, `Eq` and `Hash` on `ConfigurationPage` if
door D3 keeps it. No `Ord`, since none has a natural order.
Door: two-way. Effort: S.

## P1-6. The safe reader accepts one type, a reference to a 107-byte array

Verified in source (line 386) and by building. A reader that maps the page holds a 4096-byte
frame or a slice. The scratch program had to write
`frame[..PAGE_CONTENT_BYTES].try_into().unwrap()` before it could read. `zerocopy` pairs
`ref_from_bytes` with `ref_from_prefix` for this case.
Change: `TryFrom<&[u8]>` for `ConfigurationView`, taking a prefix, with the refusal the errors
decision shapes.
Door: two-way. Effort: S.

## P2-1. The field offsets are private

Verified in source (lines 137 to 143). The seven offset constants are private, and the README
gives the layout in prose. A reader in another language, or a debugger, copies numbers from the
README. Linux publishes every key of its vector in `auxvec.h`.
Change: the offsets as public constants, named by the page family's rule.
Door: two-way, since a constant added later breaks no caller. Effort: S.

## P2-2. A checked value is a bare `&str`

Verified in source (lines 89 to 101 and 214). `is_known_time_zone` answers a `bool`, the setter
searches the list again, and a function that wants a vetted zone takes a `&str`. `chrono-tz`
parses once into `Tz`, with `FromStr` and `name`.
Change: none at 0.1.0; door D10. M if taken.

## P2-3. A page cannot be built in a `const`

Verified by building: `const P: [u8; PAGE_CONTENT_BYTES] = PageBuilder::new().build()` fails with
E0015. `new` is `const`, and the setters and `build` are not. A writer with a fixed configuration
builds the page at run time.
Change: `const fn` setters and `build`, which need a byte loop in place of `contains`.
Door: two-way. Effort: S.

## P2-4. A lookup is exact, so `utc` and `en_US.utf8` are refused

Verified by building: both return a refusal. The crate's BUGS section names the `utf8` spelling.
`chrono-tz` offers a `case-insensitive` feature.
Change: none in the page, which carries the canonical spelling. A documented sentence, or a
function that maps a loose spelling to its member.
Door: two-way. Effort: S.

## P2-5. The package ships the repository's CI files

Verified by building: `cargo package --list --allow-dirty` lists 40 files, 21 of them under
`.github/`, `.githooks/` or `.cargo/`, or named `.gitignore`.
Change: an `include` list in the manifest.
Door: two-way. Effort: S.

## P2-6. `build` returns the page by value and cannot fill a caller's frame

Verified in source (line 247). The writer gets a `[u8; 107]` and copies it into the frame it
maps. The copy is small. A second entry that writes into `&mut [u8; PAGE_CONTENT_BYTES]` removes
it, and its spelling follows the contract-layout decision.
Door: two-way. Effort: S.
