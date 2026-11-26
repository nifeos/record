---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1092, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1134. `byte_glob`: the release review's findings

*(The number and the slug are provisional.)*

Raised by review lane A of [milestone 1129 (the combine review)](1129-crate-interfaces-best-in-class.md). The lane read `partsfoundry/byte_glob` at `a095cd8`, the head of its `main`, as a
stranger choosing a glob crate would meet it. It changed nothing in any repository. The baseline is
[the outside review, 1092](1092-glob-outside-review.md), and
[the review package](../../notes/crate-reviews/byte-glob.md). The scope rulings, the one-backtrack
algorithm and the seven ratified names stay closed here. No name ratified before a later naming rule
fails a rule in force today, so the review reopens none.

Reuse: the crate's own tests and `benches/matching.rs`, and a scratch benchmark crate described in
[the benchmark appendix](1134-byte-glob-release-review/benchmark.md). No new tool.

## Goal

A stranger who compares `byte_glob` with `glob` and `globset` on crates.io finds a matcher whose
interface carries the ordinary traits and examples, and a stated answer for each feature the others
have and this one leaves out.

## Finding status

Each line reads against `partsfoundry/byte_glob` at `a095cd8`.

- Item 1 (P1), the missing common traits: Open.
- Item 2 (P1), no example on the front page or on two functions: Open.
- Item 3 (P2), no way to escape a literal name: Open.
- Item 4 (P2), no case-insensitive match: Open.
- Item 5 (P2), every call parses the pattern again: Open.
- Item 6 (P2), crates.io metadata: Open.

## Prior art

Measured from the crates.io API on 2026-11-26 at 07:32 (UTC). The leading comparator is `glob`.

| crate | role | version | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `glob` | leading | 0.3.4 | 760,909,296 | 184,592,625 | 4,207 | 2026-10-08 |
| `globset` | comparator | 0.4.22 | 307,389,111 | 82,156,731 | 2,113 | 2026-11-22 |
| `wildmatch` | comparator | 2.7.0 | 25,586,584 | 6,703,169 | 114 | 2026-10-20 |
| `glob-match` | neighbor (paths, captures) | 0.2.1 | 16,686,133 | 3,660,505 | 103 | 2023-02-07 |
| `fast-glob` | neighbor (paths) | 1.1.2 | 5,298,912 | 2,342,746 | 41 | 2026-09-21 |
| `wax` | neighbor (paths, a tree walk) | 0.7.0 | 3,638,783 | 1,028,997 | 59 | 2026-01-29 |

The review read the source of `glob`, `globset`, `wildmatch` and `glob-match` at these versions.
No integration target applies: the crate takes two byte slices and returns a `bool`.

How the four compare, read from each crate's `src/lib.rs`:

| axis | `byte_glob` | `glob` 0.3.4 | `globset` 0.4.22 | `wildmatch` 2.7.0 |
|---|---|---|---|---|
| input | `&[u8]` | `&str` or `&Path` | `AsRef<Path>`, `Candidate` | `&str` |
| `no_std`, no allocation | both | needs `std` | needs `std` | needs `std`, holds a `Vec<char>` |
| malformed pattern | matches itself | `PatternError { pos, msg }` | `Error` with a kind | not possible: only `*` and `?` |
| classes `[a-z]` | yes | yes | yes | no |
| options | `LeadingDot` | `MatchOptions`, three `bool` fields | `GlobBuilder`, several setters | the wildcard characters, case |
| escape a literal | no | `Pattern::escape` | `escape` | no |
| compile once | no | `Pattern` | `GlobMatcher`, `GlobSet` | `WildMatch` |
| cost bound | `step_bound`, proved | none stated | the regex engine's | none stated |

## What the crate does better

- Against `glob`: no `std`, no allocation, and bytes rather than text, so a name that is not
  UTF-8 still matches. One call with no compile step costs about a fifth of `glob`'s compile and match.
  `glob`'s derived `MatchOptions::default()` sets `case_sensitive` to `false` while `new()` sets it to
  `true`, a disagreement its own source marks as a FIXME. `byte_glob` has one default.
- Against `globset`: the same `no_std` gain, and no regex compile, so a pattern used once matches
  about 270 times sooner than `globset` compiles it (see *Benchmarks*).
- Against `wildmatch`: classes and escapes, which `wildmatch` lacks, and the right answer on the class
  shape, where `wildmatch` reads `[` as a literal byte.
- Against all three: a total function with a cost a caller computes before it calls, and Kani proofs
  with the patches that break them. None of the others states a bound or ships a proof.

## Findings

Each finding gives its evidence and the change. It also says whether the lane verified it in the
source or inferred it, which door it is, and an effort size: XS under an hour, S a few hours, M a
day or two.

### P1

#### Item 1: The missing common traits

`LeadingDot` derives `Clone`, `Copy`, `PartialEq`, `Eq` and `Debug`, and `Outcome` derives the same
five. Neither has `Hash`, and `LeadingDot` has no `Default`, although the crate documentation
calls `Special` the default. `glob` 0.3.4's `MatchOptions` derives `Hash`, `Default`, `PartialOrd` and
`Ord` beside them. A caller who keys a cache by policy, or whose own options struct derives
`Default`, has to write the implementation by hand.

Change: derive `Hash` on both, and `Default` on `LeadingDot` with `#[default]` on `Special`, so the
type and its documentation agree. Verified in the source. Adding a derive is additive, so two-way.
Effort XS.

#### Item 2: No example on the front page or on two functions

The crate documentation opens with the bold fragment "glob: does this pattern match this name?",
which docs.rs prints as the crate's summary, and it carries no code example. The README's example
compiles in no test, because the crate includes no README as a doctest. `has_magic` and
`step_bound` have no example. `glob` 0.3.4 opens its crate page with two examples under an
*Examples* heading.

Change: a first sentence that reads as a summary, the README's example in the crate documentation
or included as a doctest, and one example each on `has_magic` and `step_bound`. Verified in the
source and by `cargo test`, whose doctests cover only the items that carry one. Two-way. Effort XS.

### P2

#### Item 3: No way to escape a literal name

A caller who builds a pattern from a name it holds, such as a file named `a[1].txt`, must
escape `*`, `?`, `[` and `\` itself. `glob` 0.3.4 has `Pattern::escape(&str) -> String` and
`globset` 0.4.22 has `escape(&str) -> String`. Both allocate.

Change: an escape function that writes into a caller's buffer and returns the written prefix or a
refusal when the buffer runs short. Its shape is the first output-buffer shape this crate would
carry, so it follows the shared byte-sink decision of milestone 1129 rather than inventing one.
The lane verified the gap and infers the demand from the two comparators. Additive, two-way. Effort S.

#### Item 4: No case-insensitive match

`glob` 0.3.4 (`MatchOptions::case_sensitive`), `globset` 0.4.22 (`GlobBuilder::case_insensitive`)
and `wildmatch` 2.7.0 (`WildMatch::new_case_insensitive`) each offer ASCII or Unicode case folding.
`byte_glob` has none. A file system that folds case, such as a FAT volume, needs it.

Change: an ASCII fold as a new function beside `matches_with`, leaving the third argument as
ratified (door 1 below). Verified absent; the lane infers the need. Additive, two-way. Effort S.

#### Item 5: Every call parses the pattern again

`matches` decodes the pattern on every call. For one pattern over many names, `globset` compiled
once beats it on every shape the benchmark ran but `*.txt`, by 2.4 times on ten stars over 4,096
bytes and by 150 times on a long tail of `?`. `glob`'s compiled `Pattern` is slower than `byte_glob`
on most shapes.

Change: an optional borrowed, compiled form, such as a type that holds a `&[u8]` pattern with its
classes decoded and a literal suffix found, so a caller with many names skips the decode. The
lane verified the measurement; it infers the gain, which needs its own benchmark.
Additive, two-way. Effort M.

#### Item 6: crates.io metadata

`Cargo.toml` has no `documentation` field, and its categories omit `no-std::no-alloc`, which
describes the crate exactly. Change: add both. Verified in the manifest. Two-way. Effort XS.

## One-way doors

1. The policy argument's shape. `matches_with` takes a `LeadingDot` enum as its third argument,
   where `glob` takes a `MatchOptions` struct and `globset` a builder. A struct takes a new option
   without a new function; an enum argument does not. Recommended: keep the enum as ratified, and
   give any later option, such as item 4's fold, its own function. A wider options struct can still
   arrive later beside these functions, and nothing a caller wrote breaks.
2. The input type. Both arguments are `&[u8]`. `impl AsRef<[u8]>` would take a `&str` directly, but
   a generic function cannot become a function pointer without naming its type parameter, and the
   `b"..."` literal already reads well. Recommended: keep `&[u8]`.
3. The name `Outcome`, provisional since the outside review's item P2-3. `glob` and `globset`
   return a bare `bool` and have no such type; `regex` 1.x calls its result `Match`, which here would
   mislead, because the type reports a failure too. Recommended: ratify `Outcome` as built.

## Benchmarks

Run on a Linux x86_64 host (an Intel Xeon Platinum 8160 at 2.10 GHz) with rustc 1.100.0, release
profile. Each figure is the fastest of seven runs, in time per match. `byte_glob` ran under
`LeadingDot::Ordinary`, and each comparator compiled its pattern once, outside the timed loop.

| pattern and name | `byte_glob` | `glob` | `globset` | `wildmatch` |
|---|---|---|---|---|
| `*.txt`, `notes.txt` | 50.3 ns | 67.5 ns | 54.1 ns | 25.5 ns |
| `[a-z]*[0-9].log`, a 30-byte log name | 364 ns | 432 ns | 80.8 ns | 7.4 ns, wrong answer |
| `*` then 63 `?` then `b`, 4,096 bytes of `a` | 1.12 ms | 0.82 ms | 7.4 µs | 0.34 ms |
| `a*` ten times then `b`, 16 bytes of `a` | 143 ns | 143 ns | 55 ns | 51 ns |
| the same, 32 bytes | 212 ns | 328 ns | 84 ns | 97 ns |
| the same, 4,096 bytes | 18.1 µs | 35.6 µs | 7.5 µs | 12.3 µs |
| 256 unterminated `[` | 63.8 µs | refuses the pattern | refuses the pattern | 319 ns |

Compiling and matching once, which is what `byte_glob` always does, cost `glob` 262 ns on `*.txt`
and 736 ns on the class shape, and `globset` 13.6 µs and 16.4 µs. The command and the harness are in
[the benchmark appendix](1134-byte-glob-release-review/benchmark.md).

## The checklist

All 54 items of the Rust API Guidelines checklist, each marked, are in
[the checklist appendix](1134-byte-glob-release-review/checklist.md). Four are not met:
C-COMMON-TRAITS (item 1), C-CRATE-DOC and C-EXAMPLE (item 2), and C-METADATA (item 6).

## Done when

- Items 1 and 2 land on the crate's `main`, and `cargo test` runs the new examples.
- Items 3 to 6 land, or each carries a ruling against it.
- The architect has ruled each one-way door above.

## BUGS

- The benchmark ran on one machine, and only the fastest of seven runs counts.
- The review did not measure `fast-glob` or `wax`, which match paths rather than one name.

## Follow-on

- **Outstanding.** Items 1 to 6, open on the crate's `main` at `a095cd8`.
- **Outstanding.** The three one-way doors, for the architect.

## Index row

The release review of `byte_glob` against `glob`, `globset` and `wildmatch`. Two items land before
the first release: the common traits and the missing examples. Four may follow: an escape function,
a case fold, a compiled form and the manifest metadata. Three one-way doors are for the architect.
