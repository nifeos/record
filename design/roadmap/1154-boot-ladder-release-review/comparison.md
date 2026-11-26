# The comparison, axis by axis

An appendix to [the milestone](../1154-boot-ladder-release-review.md). It sets
`partsfoundry/boot_ladder` at `019d76c8` beside its nearest neighbors. The files behind each cell
are in [what the review read and ran](what-was-checked.md).

| axis | `boot_ladder` | KTAP with `kunit_parser.py` | `tap_parser` 0.1.1 | `sd-notify` 0.5.0 | `expectrl` 0.9.0 |
|---|---|---|---|---|---|
| writer and reader share | one crate | a document | nothing: reader only | nothing: writer only | nothing: reader only |
| `no_std`, no allocation | both | not applicable | needs `std`, builds `Vec`s | needs `std` | needs `std` |
| noise before the line | found anywhere in the line | the prefix before `KTAP version` is measured and cut | none allowed | not applicable | found anywhere in the buffer |
| input | `&str` | text lines | `&str` | not applicable | `&[u8]` |
| a declared total | `X of Y passed` | the plan, `1..N` | the plan | none | none |
| counts checked against results | no (P0-2) | yes: a missing or misnumbered result is an error | yes | not applicable | not applicable |
| a refusal says why | no: `None` (P0-3) | yes: an error per cause, and `FAILURE_TO_PARSE_TESTS` | yes: an `Error` of eleven variants | `io::Result` | `Error` |
| a format version in the output | none (D9) | `KTAP version 1` | `TAP version 14` | none | not applicable |
| whose tests | one fixed list of fifteen (D8) | any | any | not applicable | not applicable |
| proofs | two Kani harnesses | none | none | none | none |

## What `boot_ladder` does better

- Than KTAP and `kunit_parser.py`: the grammar is code both sides link, where KTAP is a document
  and its parser a set of regular expressions written apart from the C that prints. The verdict
  is one line that survives a photograph of a screen. An absent device is its own outcome, where
  KTAP has `# SKIP` as text on an `ok` line.
- Than `tap_parser` and `testanything`: no `std` and no allocation, so a kernel can link it.
  `testanything` builds a `String` per line and `tap_parser` collects `Vec`s.
- Than `sd-notify`: it reads what it writes. `NotifyState` prints and has no parser.
- Than `expectrl` and `rexpect`: the needle is not a literal the reader's author typed, which is
  the hand-spelled copy this crate exists to remove.
- Than all of them: Kani proves the reader's number and name-list parsing free of overflow and
  panics.

## The benchmark's results

The method is in [the benchmark section](what-was-checked.md#the-benchmark). Each column finds
the head `<name> self-test: ` in the same text.

| text | bytes | `Head::find_in` | `str::find`, joined | `expectrl` 0.9.0 |
|---|---|---|---|---|
| one verdict line after a replacement character | 86 | 16.8 ns | 74.0 ns | 26.7 ns |
| a transcript of 80-byte lines that each hold the name, the verdict last | 65,687 | 254 µs | 14.1 µs | 121 µs |
| 4,096 bytes of `a`, the name eight `a`, no match | 4,096 | 24.5 µs | 6.28 µs | 7.50 µs |

`ParsedVerdict::in_line` on the 86-byte line takes 92.4 ns, and 124 ns with both name lists
counted.
