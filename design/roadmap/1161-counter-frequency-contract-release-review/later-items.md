# The later items

An appendix to [the milestone](../1161-counter-frequency-contract-release-review.md). It holds
the P1 and P2 findings of the release review of `partsfoundry/counter_frequency_contract` at
`4decec9d` in full. The block keeps one line for each, and the doors D7 to D9 it names are the
block's. Line numbers are of `src/lib.rs`.

## P1: before the first release

### P1-1. The documentation names things a stranger cannot find and never names the system

Verified in source and the README. The crate page says "the kernel" and never says which system's
kernel maps a page at these two addresses. Line 31 cites "the sibling shared pages", line 35 "a
dated ledger entry" and line 38 "a program's `INTERFACES` note", and none is a link. The crate
that defines that note lives in the same organization.
Change: one sentence that names the binary interface (door D8); a link to `interfaces_note`; the
other two become plain descriptions or go.
Door: two-way, apart from D8. Effort: S.

### P1-2. No example on the crate page or on `new`

Verified in source. The crate page has an identity section and a BUGS section and no example. The
README's example compiles as a doctest, so the text exists. `new`, the one `unsafe` function, has a
`# Safety` section and no example of the fixed-address call a real reader makes.
Change: the README's example on the crate page, and a `no_run` example on `new` that reads the
page at `PAGE_VIRTUAL_ADDRESS`.
Door: two-way. Effort: S.

### P1-3. `is_plausible`, `build_page` and `hertz` are not `const fn`

Verified in source (lines 74, 124 and 191). `new` is `const`, and the three others are not, so a
caller cannot check a rate or build a page in a `const`. Every operation they use is available in
a `const fn` at the crate's minimum Rust version, apart from `RangeInclusive::contains` and the
comparison of two slices, which plain comparisons replace.
Change: make the three `const fn`, and the decoder of P0-1 with them.
Door: two-way, since adding `const` breaks no caller. Effort: S.

### P1-4. `Debug` prints the address, and the page type has no equality

Verified by building: `{:?}` prints `CounterFrequencyPage { base: 0x7ffedc9292f0 }`. The baseline
left this for the next change to the public interface, and P0-1 is that change. The type derives
`Debug`, `Clone` and `Copy` and no `PartialEq`, `Eq` or `Hash`.
Change: a `Debug` that prints the rate the page holds, and `PartialEq` and `Eq` on whatever value
type P0-1 and P0-5 leave.
Door: two-way. Effort: S.

### P1-5. No stated rule for what a changed band or address does to `VERSION`

Verified in source and the README. Both say a layout break ships as a new magic and version. They
do not say what a change to `MINIMUM_PLAUSIBLE_HERTZ`, `MAXIMUM_PLAUSIBLE_HERTZ` or an address
means. With P0-2 the band decides what a reader accepts, so two programs built apart can disagree
on a rate at run time.
Change: a stability section stating the rule of door D7.
Door: one-way (D7). Effort: S.

### P1-6. The manifest and the baseline disagree on whether the crate publishes

Verified in `Cargo.toml` (line 11) and in the block of milestone 1073 (what an outside maintainer
would fix before it leaves). The manifest says `publish = false` holds until the release that
publishes the crate. The baseline records a ruling that a contract crate never publishes and that
the tag is its release. Milestone 1129 (the combine review) gates a first publish of each of its
crates, this one among them.
Change: the manifest comment and the README state whichever door D9 rules.
Door: one-way (D9), since a publish cannot be taken back. Effort: S.

## P2: may follow

### P2-1. A reader that converts ticks to time must build its own multiplier

Verified by building. The page carries hertz, so a reader that turns ticks into nanoseconds
divides a 128-bit product by the rate, or derives a multiplier and a shift once. Linux's pages
publish the multiplier and the shift, and `quanta` computes them (`mul_div_po2_u64`). The block's
measurement gives 30.02 nanoseconds for the divide and 0.71 for the multiply.
Change: a `const fn` that turns a rate into a multiplier and a shift for nanoseconds, its name
provisional. The page does not change.
Door: two-way. Effort: S.

### P2-2. No `#[must_use]` on the three functions whose result is the point

Verified in source. `is_plausible`, `build_page` and `hertz` return the one thing each exists
for, and a caller that drops the result gets no warning.
Change: `#[must_use]` on the three.
Door: two-way. Effort: S.

### P2-3. The manifest has no `documentation` key and the package ships the repository's CI files

Verified by building. `cargo package --list` names 38 files, and 20 of them sit under `.github/`
or `.githooks/` or are `.gitignore`. The manifest has no `documentation` key and no `include`.
The release workflow reads a secret named for another project.
Change: the key, an `include` list, and a secret named for this organization.
Door: two-way. Effort: S.

### P2-4. The rate has no conversion to a typed frequency

Verified in source. `hertz` returns an integer. `fugit` gives embedded code a typed rate,
`HertzU64`, and drew 1,456,814 downloads in 90 days.
Change: none at 0.1.0. A conversion can join behind an optional feature, which the feature-names
decision of milestone 1129 names.
Door: two-way. Effort: S.

### P2-5. An example comment and a test comment refer to a check the reader never saw

Verified in source (line 249) and the README (line 42). Both cite a `> 0` check, and one calls it
old. The crate holds no such check, so a stranger cannot tell what the comment compares with.
Change: each comment says what the band refuses, and no more.
Door: two-way. Effort: S.
