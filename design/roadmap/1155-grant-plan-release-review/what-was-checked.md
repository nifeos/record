# What the review read and ran

An appendix to [the milestone](../1155-grant-plan-release-review.md).

## The crate

`partsfoundry/grant_plan` at `69aedfbc9adb70d877435c6a62dc4983ef035e0d`, version 0.1.0,
`publish = false`. Read in full: `Cargo.toml`, `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`,
`docs/stranger-test.md`, the `ci` and `fuzz` workflow callers, the two exemption lists under
`.github/` and `examples/plan_a_line.rs`. Read as library text, every file under `src/`:
`lib.rs`, `lexing.rs`, `word.rs`, `command.rs`, `escalation.rs`, `parsing.rs`, `planning.rs`,
`refusal.rs`, `line.rs`, `expansion.rs` and `navigation.rs`. Read in part: the Kani harnesses of
`word` and `line`, `refusal/tests.rs` and `test_support.rs`. The other test files were not read.
The review read `grant_contract` at `f84cd7e6` for the names of its public items only.
The baseline read:
the block of milestone 1094 (what an outside maintainer would fix before it leaves), its
prior-art, later-items and ruled-decisions appendices, and the cleared package.

## The commands

Run on a Linux x86_64 host with rustc 1.100.0, with the build directory outside the clone.

- `cargo build --locked` and `cargo clippy --locked --all-targets` pass with no warning.
- `cargo test --locked` passes: 193 unit tests, 2 integration tests and 6 documentation tests.
- `cargo doc --locked --no-deps` passes with one warning: the documentation of
  `Expansion::designated` links the private field `Expansion::at` (P1-4).
- `cargo build --locked --lib --target <t>` passes for `x86_64-unknown-none`,
  `aarch64-unknown-none-softfloat` and `riscv64imac-unknown-none-elf`.
- `cargo run --locked --example plan_a_line` plans one line and refuses two, as its text says.
- `cargo package --list --allow-dirty` lists 75 files, 18 of them under `.github/` (P1-6).
- `grep -rn` over `src/` finds no `non_exhaustive`, no `must_use`, no `# Errors`, no `# Panics`
  and no `unsafe`; it finds 9 `kani::proof` harnesses, the README's count.
- The crate has no features, so there is one combination.
- `git status --short` in the clone printed nothing afterward.

## The probe

A scratch binary that depends on the crate by path, run in a debug and a release build.

| call | result |
|---|---|
| `Expander::batch(b"*", Resume::Start)`, ten names offered, then `finish()` | debug: panics on the `debug_assert!`; release: `Ok`, a set of 8 names (P0-1) |
| `Expander::new(b"*")`, one name offered, then `finish_batch()` | debug: panics; release: `Ok`, a batch of 1 |
| a batch offered `b` to `h`, a 200-byte name, then `a`; and a set of the same eight names built by `try_push` | the two iterate alike, and `==` answers `false` (P1-1) |
| `component(1)` on a path one level deep | an empty slice |
| `component(depth())` on a path that fills all 512 bytes, and `component(600)` on any path | panics: index out of bounds (P0-5) |
| `descend(b"a/b")` on the root, result ignored | the path stays at the root (P1-8) |
| `render` into a 4-byte buffer | returns 4, the text cut short, as documented |
| `Name::new`, `NameSet::one` and `Expander` matching `a*`, each on `a:b` and on a name holding a zero byte | all accept it |
| `navigation::path` and `is_valid_component` on the same two names | both refuse it (P1-2) |
| `word::read(b"'it's'")` | `PartlyQuoted`: no line spells a name that holds both quote characters (D10) |
| `parse(b"--mem 4")` | `Run`, with an empty program name and a memory grant of 4 (P2-6) |
| `parse(b"-r count")` | `Run`, program `count`, option `r` |
| `rm_report::status(-1)` | 18,446,744,073,709,551,615 (P2-6) |
| `Refusal::ScopeCannotRestore.message()` | ends "'swish -c', side is reserved and not built yet" (P1-3) |

The probe printed these sizes in bytes on the 64-bit host. The planning values: `Endowment`
4,344, `ShellHoldings` 3,312, `Streams` 2,368, `Bindings` 2,240 and `DirectoryGrant` 1,080.
The parts: `Sink` 792, `FileGrant` 784, `Expansion` 568, `NameSet` 544, `DirectoryPath` 528,
`Resume` 254 and `Name` 253. The parse: `CommandLine` 184, `ParsedInvocation` 184, `Line` 128,
`Manifest` 80 and `Refusal` 24.

The probe then generated three million lines of up to 39 bytes from a fixed seed. Its alphabet
holds letters, white space, both quotes, the operators, the pattern bytes, `/`, `.`, `-`, `%`,
`:`, a zero byte and `--mem`. Each line went through `word::read`, `line_verb`, `check_words`,
`write_argument_page`, the four operand classifiers and `last_component_has_magic`. It went
through `navigation::path` with `apply` and `resolve_path`. It went through `line::split` with
`parse` and `plan_against_with_streams`, against six manifests and a shell with a mounted tree
and a bound name. It planned 206,870 stages and caught no panic, in a debug build and in a release build.

## The benchmark

A scratch crate that depends on `grant_plan` by path, on `shlex` at `=2.0.1` and on
`brush-parser` at `=0.5.0`. It ran under `cargo run --release` on a Linux x86_64 host (an Intel
Xeon Platinum 8160 at 2.10 GHz) with rustc 1.100.0. The timing loop is
the one [milestone 1154 (the release review of `boot_ladder`) describes](../1154-boot-ladder-release-review/what-was-checked.md).
Inputs and results pass through `std::hint::black_box`. The two inputs:

- a line of 75 bytes and twelve words, two of them quoted:
  `count -v "my notes.txt" 'second file' plain.txt logs/report.txt a b c d e f`;
- a pipeline of 40 bytes: `wc < in.txt | sort -r | uniq > total.txt`.

The harness asserts that `tokenize` with `word::read` and `shlex::bytes::split` yield the same
twelve words before it times either.

| measurement | time | what it includes |
|---|---|---|
| `tokenize` into 16 slots, `word::read` on each token | 217.0 ns | no allocation; the sum of the word lengths |
| `for_each_word` | 457.7 ns | the callback, and one `tokenize` call for each word |
| `shlex::bytes::Shlex`, iterated | 482.1 ns | a `Vec<u8>` allocated and freed for each word |
| `shlex::bytes::split` | 590.6 ns | the same, and the outer `Vec` |
| `parse`, which runs `parse_invocation` | 284.9 ns | tokens, quotes, options and positionals classified |
| `line::split`, then `parse` on each of three stages | 365.4 ns | the pipeline line |
| `brush_parser::uncached_tokenize_str`, then `parse_tokens` | 5,048.1 ns | the pipeline line, to a syntax tree, with default options |
| `brush_parser::uncached_tokenize_str` alone | 2,751.8 ns | the pipeline line, to tokens |
| `parse`, then `plan_against`, for `count -v notes.txt` | 592.3 ns | one file grant planned, and the 4,344-byte `Endowment` returned |
| a copy of one `Endowment` | 57.3 ns | the copy alone |

`shlex` does less than the crate (words only) and `brush-parser` more (the whole bash grammar),
so neither row is a like-for-like rival. No comparator plans a grant, so the last two rows stand
alone.

## The comparators read

Each `.crate` file came from crates.io at the version the prior-art table gives, into a
directory of its own.

- `shlex` 2.0.1, `src/lib.rs` and `src/bytes.rs`. `bytes::Shlex` is an `Iterator` whose item is
  a `Vec<u8>`. It reads single quotes, double quotes, backslash escapes and `#` comments, and it
  joins adjacent quoted pieces into one word. On an unclosed quote it sets the public field
  `had_error` and ends; `split` returns `Option`. `QuoteError` is `#[non_exhaustive]`, derives
  `Hash` and `Ord`, and implements `Display`, and `std::error::Error` under the default `std`
  feature. `try_quote` and `try_join` are the inverse. The crate needs `alloc`.
- `shell-words` 1.1.1, `src/lib.rs`. `split(&str) -> Result<Vec<String>, ParseError>`, where
  `ParseError` is a unit struct with `Display`; its state machine has backslash states; `quote`
  and `join` are the inverse. A default `std` feature, and `alloc` without it.
- `brush-parser` 0.5.0, `src/lib.rs`, `src/error.rs`, `src/ast.rs` (the pipeline, redirection
  and word types), and the entry points of `src/tokenizer.rs` and `src/parser/mod.rs`.
  `ParseError`, `WordParseError` and `BindingParseError` are `#[non_exhaustive]` and derive
  `thiserror::Error`. `ParseError::ParsingNear` carries a `SourcePosition`. `ast::Word` owns a
  `String` and an optional `SourceSpan`. `IoFileRedirectKind` has seven kinds, and
  `IoRedirect` has here-documents. The manifest declares eleven dependencies, four of them
  optional, and features named `serde`, `arbitrary`, `diagnostics`, `debug-tracing` and
  `winnow-parser`. It needs `std`.
- `yash-syntax` 0.25.0, `src/parser/error.rs` and the `Redir` type of `src/syntax.rs`.
  `Error` is a `cause` and a `Location`. `SyntaxError` is `#[non_exhaustive]`, and its
  unclosed-quote variants carry `opening_location`.
- `clap_lex` 1.1.2, the public items of `src/lib.rs`. `ParsedArg` answers `is_escape`,
  `to_long` and `to_short`, and `ShortFlags` yields each letter of a cluster. It uses
  `std::ffi::OsStr`.
- `lexopt` 0.3.2, the public items of `src/lib.rs` and its `Error`. The variants carry the
  option or value that failed (`UnexpectedOption(String)`,
  `UnexpectedValue { option, value }`). The enum is not `#[non_exhaustive]`, and a comment says
  the minimum Rust version is why.
- `cap-std` 4.0.3, the signatures of `src/fs/dir.rs`. `Dir::open`, `open_dir` and `entries`
  resolve a path against a held directory and return `io::Result`. It needs `std`.
- Measured and not read: `shellexpand` 3.1.2 (variable and tilde expansion; 76,686,700
  downloads, 19,478,015 in 90 days, 1,042 reverse dependencies, updated 2026-02-23),
  `deno_task_shell` 0.33.3 (1,361,225; 256,505; 19; 2026-08-04) and `conch-parser` 0.1.1
  (26,395; 2,689; 6; 2019-05-15).

Fourteen crates.io queries, sorted by recent downloads, found no crate that plans a grant from
a line: `capability shell`, `shell parser`, `shell grammar`, `pipeline redirection parser`,
`no_std shell`, `command line planner`, `shell lexer`, `least authority`, `pola shell`,
`manifest command line`, `posix shell`, `embedded shell`, `glob expansion` and `argv no_std`.

## The system outside Rust

Plash, from `https://github.com/mseaborn/plash` at commit
`1d77bb2fec3d9cdeb3547c42682818c447492bf4`, under `plash/`:

- `src/shell.gram`, the whole grammar. A command is `cd`, `fg`, `bg`, `def`, `source` or a
  pipeline. An argument list has `=>` (the program may read and write what follows), `+` (what
  follows joins the program's file namespace and stays out of its arguments) and braces to
  scope both. A string that is not a file name takes quotes, or begins with `-`. Redirections
  take a descriptor number. The `char` rule reads backslash escapes, and `*` is the one pattern
  byte.
- `docs/man_pola-shell.xxml`. Files named on the line are what the program can reach, read-only
  unless `=>` precedes them, and `ls` needs `.` typed to list the current directory.
- `src/shell-globbing.c`, lines 20 to 25: a comment says a match includes dot files.
- `src/shell.c`, line 397: a pattern that matched nothing prints
  `plash: glob pattern matched nothing` and adds no argument.

Plash is under the GNU Lesser General Public License; the review read it for its interface
shape only.

## What was not run

- Kani and mutation testing; the harness count, nine, is from source.
- No comparator's own tests. The review executed `shlex` and `brush-parser` in the benchmark
  and no other comparator.
- No shell that calls the crate, and no program that receives a planned grant.
- `cargo +1.88`, the stated minimum Rust version.
- A benchmark on a bare-metal target, or on a second machine.
