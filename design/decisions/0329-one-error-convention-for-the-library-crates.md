---
status: DECIDED
raised: 2026-11-26
decided: 2026-11-26
ratified_by: calef
---

# 329. One error convention for the library crates

*(The section number and title are provisional until the merge lands them.)*

The survey reads each crate's `origin/main` on 2026-11-26 (UTC), and the record's blocks on
`origin/main` at `b687ebaaab`.
[`costs.md`](0329-one-error-convention-for-the-library-crates/costs.md) costs option A per crate.

## Background

The partsfoundry library crates report failure in many ways, from an error enum with `Display` and
`core::error::Error` to a raw `i32`. Milestone 1129 (the combine review) lists errors as the first
shape to share. Its release reviews hold an errors paragraph each. Blocks 1134 to 1154 and 1158 to 1160
are on main, and sixteen of their findings wait on this decision. A later block's waiting findings
follow the rules as written.

It matters now because the publishing hold waits on it: each crate's first crates.io publish and its
0.1.0 interface wait for every shared decision that touches it. Nothing is on crates.io yet, so an
edit can still change any shape. After publish, an error's shape becomes a one-way door. A new
variant in an exhaustive enum, a new field in a variant, a rename or a removed derive breaks every
caller that relies on it. A new trait implementation breaks nobody.

## The recommendation

Adopt option A, the convention below, for every library crate, and give each crate's release review
a finding that follows it.

1. A refusal is a `Result<_, E>`, where `E` is a type of the crate: never `()`, `bool`, a bare `T`
   or a raw integer. `Option` answers only an absence with one cause, such as a lookup that finds
   nothing or an iterator's end (block 1111's decision 3 stands). A public function panics only on
   a precondition the caller can check first, stated under `# Panics`, such as a `const fn`
   assertion that fails at compile time; what the input or the device decides is a refusal.
2. Every public error type implements `Debug`, `Display` and `core::error::Error`, which is stable
   in `core` since Rust 1.81; every crate declares 1.85 or later.
3. A message describes its own level only, in lower case with no closing period. An error that wraps
   another returns it from `source` and leaves it out of `Display`.
4. Every public error enum is `#[non_exhaustive]`, and so is each variant with named fields. A unit
   variant and a tuple variant that holds one wrapped error stay unmarked, so a caller can still
   build and match them. An error struct keeps its fields private or carries the attribute. An enum
   that another crate numbers one to one stays exhaustive, so a new variant breaks that crate's
   build: `domain_name_system::Reject` keeps block 1136's door 2.
5. Each cause has its own variant, and named fields hold its data. A tuple variant holds one wrapped error and nothing else. A
   variant that holds a wrapped error beside other data names that field `source`.
6. A parser that walks a variable-length structure reports the byte offset of each refusal that
   has one. When every refusal has a position, the error is a struct with a private `offset` and a
   `kind()` enum, as `Utf8Error`, `nom` and `dtoolkit` carry location outside the kind. When some
   have none, each variant with a position gets a field named `offset`.
7. A call that takes ownership of a value and refuses it hands the value back through `into_inner`,
   the name of the stable `PoisonError::into_inner`.
8. Entry points share an error enum when their sets of variants overlap; an enum splits when its
   entry points fall into groups that share no variant. Each fallible function's `# Errors` section
   lists the variants it returns.
9. Every error type derives `Clone`, `PartialEq` and `Eq`, and `Copy` unless it holds a refused
   value. A type that holds a refused `T` implements `Debug`, `Display` and `Error` for every `T`
   without printing it, as `PoisonError<T>` does, and is `Send` and `Sync` exactly when `T` is. A
   type generic over a device error `E` is an `Error` when `E` is one.
10. An error type's name ends in `Error`, in the verb-object-error order of the API Guidelines'
    C-WORD-ORDER. A crate or module with one family names it `Error`, as three modules each of
    `e1000e` and `designware_ethernet` do.

The crates write the implementations by hand. A derive crate such as `thiserror` needs its own
dependency ruling, and a crate can adopt one later without touching its interface.

The reason: rules 4 to 10 become one-way doors at publish. They cover what the reviews keep
finding: one variant for several causes, no location, a dropped value, enums that cannot grow and
names that do not say they refuse. Deciding the traits alone (option B) leaves each crate to settle the one-way
part by itself, and the reviews already give four answers. On a close call the stricter rule wins:
a crate can drop a `#[non_exhaustive]` or add a derive after publish without breaking anyone, but
cannot do the reverse.

## The decision

Ruled 2026-11-26 (UTC): option A, the full convention, rules 1 to 10 as written. A2 is rejected
because an unmarked variant cannot gain a field later. B is rejected because it leaves the one-way
part undecided per crate. C is rejected because the crates share no failure vocabulary and it binds
crates that stand alone. D is rejected because it merges families sharing no variant.

## Is the premise true

The premise is that the crates disagree in shape as well as in traits. The source agrees. Of 51
types and 261 variants in 17 crates, 31 variants in 8 crates keep data in positional fields. 17
types in 8 crates lack `core::error::Error`, and 16 of those lack `Display` too. 18 types in 11
crates lack `#[non_exhaustive]`, and no crate marks a variant. 18 type names in 11 crates do not end
in `Error`. Every type derives `Clone`, `Copy`, `PartialEq` and `Eq`, and 15 derive `Hash`.

Wrapping takes four forms. `file_allocation_table` and `domain_name_system` return the inner error
from `source` and leave it out of `Display`. `e1000e` does both. `designware_mobile_storage`
renders it and has no `source`. `designware_ethernet` does neither. The standard library's `Error`
documentation says to do one or the other, never both.

The census of milestone 1129 missed `grant_plan`'s `NameSetFull` and `NoJobNamed`,
`program_argument_contract`'s `WrongPageLength` and the crate `jh7110_clock_and_reset`, and eight
crates moved past its commits.

Rule 1 reaches ten crates that refuse with `Option`, `bool` or a raw integer for more than one
cause; `jh7110_clock_and_reset` is not among them.
[`costs.md`](0329-one-error-convention-for-the-library-crates/costs.md) has the table of today's
shapes. In the one repository that uses the crates, a resolver matches `Reject` with a wildcard
arm, and a shell names `grant_plan::Refusal` variants 14 times.

## Provisional names

The field `offset`, the field `source`, the methods `into_inner` and `kind`, each new error type
and each rename are provisional until a crate's review ratifies them.

## Prior art, read 2026-11-26 (UTC)

I read each crate's source from crates.io, the standard library's `library/` source in the nightly
toolchains of 2026-11-22 and 2026-11-26, and the API Guidelines at
`rust-lang/api-guidelines@97a0969cb0`. Demand comes from the crates.io API the same day.

| crate | version | downloads | 90 days | reverse dependencies | last updated |
|---|---|---|---|---|---|
| `thiserror` | 2.0.21 | 1,955,601,074 | 576,609,056 | 82,348 | 2026-09-23 |
| `nom` | 8.0.0 | 940,000,930 | 255,249,950 | 2,637 | 2025-01-26 |
| `object` | 0.41.0 | 745,726,836 | 158,972,925 | 582 | 2026-11-10 |
| `arrayvec` | 0.7.8 | 731,364,861 | 198,482,924 | 1,283 | 2026-07-02 |
| `embedded-io` | 0.7.1 | 204,395,110 | 94,206,861 | 353 | 2025-10-01 |
| `heapless` | 0.9.4 | 192,753,758 | 64,850,554 | 1,239 | 2026-11-18 |
| `embedded-hal` | 1.0.0 | 41,184,610 | 10,193,281 | 1,852 | 2024-01-09 |
| `dtoolkit` | 0.5.0 | 11,530 | 7,666 | 3 | 2026-11-03 |
| `fdt` | 0.1.5 | 1,713,432 | 471,091 | 7 | 2026-10-01 |

None of these marks a variant `#[non_exhaustive]`; rule 4 goes past them all.

### The standard library

`core::error::Error`'s documentation sets the message style and the wrapping rule. `io::ErrorKind`
is `#[non_exhaustive]` with 44 variants. `Utf8Error` keeps `valid_up_to` private behind an accessor.
`PoisonError<T>` hands its value back through a stable `into_inner` and implements `Debug`,
`Display` and `Error` for every `T`; `TrySendError::into_inner` exists but is unstable, behind
`try_send_error_into_inner`. Every error type C-WORD-ORDER lists ends in `Error`. We choose `source`
over rendering, so a chain printer shows each level once.

### The API Guidelines, C-GOOD-ERR

Every error type implements `Error`, `Send` and `Sync`, and `()` never serves as an error. Rules 1
and 2 restate this item; rules 4 to 10 add what it leaves out.

### embedded-hal 1.0.0

Each module (`digital`, `i2c`, `pwm`, `spi`) declares its own `Error` trait, which asks only for
`Debug` and a `kind()`, and its own `#[non_exhaustive]` `ErrorKind`. Neither the traits nor the
kinds touch `core::error::Error`, since the crate declares Rust 1.60. It serves one trait with many
implementers; each of our crates is one implementer.

### embedded-io 0.7.1

`Error` extends `core::error::Error` and adds `kind()` onto an 18-variant `#[non_exhaustive]`
`ErrorKind`. `ReadExactError<E>` is exhaustive, displays its `Debug` form and has no `source`. Rule
3 would give `Other(E)` a `source`; whether a device error exposes `embedded_io::ErrorKind` belongs
to the byte sinks decision.

### nom 8.0.0, a no_std parser

The default `Error<I>` has two public fields: `input`, the remaining input, which serves as the
location, and `code`, an exhaustive `ErrorKind` of 57 variants. It carries location outside the
kind, which rule 6 allows, through public fields over an exhaustive kind, which rule 4 refuses.

### dtoolkit 0.5.0, fdt 0.1.5 and object 0.41.0

`dtoolkit`'s `FdtParseError` is a `#[non_exhaustive]` struct with a private `offset` and a public
`kind`, rule 6's struct shape. `fdt`'s `FdtError` has three unit variants, is exhaustive,
implements `Display` and lacks `Error`, with no location. `object`'s read `Error` wraps one private `&'static str`: a caller can print it
and cannot match it. Rule 8 keeps enums a caller can match, and rule 6 adds the location both lack.

### thiserror 2.0.21

It is `no_std` and implements `core::error::Error`. Its `source` returns the field marked
`#[source]` or named `source`, and a `#[from]` variant holds the source error and nothing else.
Rule 5 matches that shape, so a crate that switches to it later changes no public item.

### arrayvec 0.7.8 and heapless 0.9.4

`arrayvec`'s `try_push` returns `CapacityError<T>`, which keeps the element private behind
`element()` and implements `Debug` for every `T`. `heapless`'s `Vec::push` returns a bare `T`,
which cannot implement `Error`. Rule 7 takes `arrayvec`'s shape with the standard library's name.

## Options

### A. The full convention (recommended)

Rules 1 to 10, costed in [`costs.md`](0329-one-error-convention-for-the-library-crates/costs.md):

- 34 of the 51 types change in 16 crates, and 64 variants change shape.
- 15 new types: 14 in 10 crates under rule 1, and one kind enum under rule 6.
- 18 renames in 11 crates, under rule 10.
- 112 test expressions in 5 crates build a variant that gains an offset or a mark, and become
  `matches!` patterns or `kind()` comparisons; 72 of them would change under any option that adds
  `device_tree_blob`'s offset.
- Rule 8 keeps one enum for the two multi-entry enums traced; 13 others were not traced.

A caller gains `{ .. }` in a pattern on a marked variant and a wildcard arm in an exhaustive match.

### A2. A without marking variants

Rule 4 marks enums and structs but no variant. It saves 40 test rewrites in 4 crates and
constructors such as the sample's `ParseError::truncated`, and matches every cited crate, none of
which marks a variant. It loses because a field added later to an unmarked variant breaks every
caller, and the reviews keep asking for more data in variants (blocks 1142, 1144, 1152 and 1158).
Dropping a variant's mark later breaks nobody; adding one breaks callers.

### B. The traits only

Rules 1 to 3; each crate's review settles its own shape. Cost: 20 types in 10 crates and the same
14 new types. It skips the 18 markings, the 31 positional variants, the offsets and the names, which
make up the one-way part. A trait can arrive after publish in a minor release, and a shape cannot.

### C. A shared error kind

A, plus a new shared crate with one `#[non_exhaustive]` `ErrorKind` and a `kind()` on every error,
as `embedded-io` has for its own family. Cost: A's, plus a crate, a dependency from 25 crates and a
kind for each of 261 variants. The crates share no failure vocabulary: a FAT cluster chain and a
refused shell option have no common kind but `Other`, and it binds crates that stand alone.

### D. One error enum per crate

Rules 1 to 7, 9 and 10, with one enum per crate in place of rule 8, as `capability_table` has.
Cost: A's, and 45 types merge
into 11 in 11 crates (15 into 1 in `file_allocation_table`), and every fallible signature there
changes. It puts in one type the families whose entry points share no variant, which rule 8 keeps
apart.

## Which waiting findings each option settles

| finding | A | B | C | D |
|---|---|---|---|---|
| 1135 door 1, `insert` drops the refused value | yes | the type only | yes | yes |
| 1140 D1, `restore` answers `Option<()>`; `Refusal` traits | yes | not the marking | yes | yes |
| 1142 P0-2 and D2, positional variants | yes | no | yes | yes |
| 1144 P0-3 and D3, no location | yes | no | yes | yes |
| 1146 P0-8 and D9, refusals by `bool`, `Option` and panic | yes | the traits only | yes | yes |
| 1147 P0-3 and D3, no `Display`, `Error` or `source` | yes | yes | yes | yes |
| 1148 P1-1, D1, D4 and D7 | yes | P1-1 only | yes | yes |
| 1149 P0-5 and D5, `Option` and panics with no reason | yes | rule 1 only | yes | yes |
| 1150 P0-6 and D6, `Pool` drops the reason | yes | the `Result` only | yes | yes |
| 1152 P0-1 and D1, exhaustive, one variant for two causes | yes | no | yes | yes |
| 1153 P0-3 and D3, `ImagePlacement` exhaustive and misnamed | yes | the traits only | yes | yes |
| 1154 P0-3 and D3, a damaged verdict reads as `None` | yes | yes | yes | yes |
| 1158 P0-4 and D4, `TooManyDevices` stands for two causes | yes | no | yes | yes |
| 1159 P0-3 and D3, `Malformed` gives no cause | yes | the `Result` only | yes | yes |
| 1159 P0-4, `Sent` holds two failures and is not an error | yes | yes | yes | yes |
| 1160 P1-1, a refusal is a status word | yes | yes | yes | yes |

Under A, rule 8 settles 1148's D4 the way it recommends. Block 1136's item 2 no longer waits: the
crate added the traits and `source` at `8f6dd771da`. `file_allocation_table` (1143) and `e1000e`
(1145) gain one finding each, and 1143's P0-3 takes rule 1.

## Reversibility, and who has acted on it

Before first publish every option is reversible, since a pre-release tag promises nothing. The
callers that acted on today's shapes live in the one repository that pins these crates, and the
lane that changes a crate changes them too. After publish, a marked enum or variant under A gains
variants and fields in a minor release, as it does under C and D; B leaves enums that grow only in
a major release.

## The seven questions

1. Alternatives: A2, B, C and D under Options, each with why it lost, and rule 8's stricter test in
   `costs.md`.
2. The tree: `file_allocation_table` already writes rules 2 and 3 down in `src/error_display.rs`.
3. Prior art: read in source, above.
4. The premise: true, by the counts under Is the premise true.
5. Cost: measured per crate in `costs.md`; B, C and D beside it.
6. Reversibility: full until each crate's first publish; afterward A keeps growth compatible.
7. Effort does not drive A. A2 and B cost less and C and D cost more; A wins on shape at any
   cost.

## A concrete example

```rust
// device_tree_blob today
#[non_exhaustive]
pub enum Error { BadMagic(u32), BadToken(u32), Truncated, /* seven more */ }

// under A: every refusal has a position, so rule 6's struct shape
#[non_exhaustive]
pub struct Error { kind: ErrorKind, offset: usize } // with kind() and offset()

#[non_exhaustive]
pub enum ErrorKind {
    #[non_exhaustive]
    BadMagic { found: u32 },
    #[non_exhaustive]
    BadToken { token: u32 },
    Truncated,
    /* seven more */
}
```

A later release can add a field to any marked variant without breaking a caller. A sample family
under rules 2 to 10 compiles with rustc 1.100.0 under `no_std`: both shapes of rule 6, a generic
wrapper with `source`, and a refused-value type with `into_inner` that is `Send` and `Sync` for a
`String`. A caller in another crate matches with
`{ .. }`, and rustc refuses its attempt to build a marked variant (E0639).

## What was not checked

- Only the sample compiled under the rules, no crate. The counts are pattern matches.
- Lanes G, I and J of milestone 1129 have not landed their reviews, so the costs for their nine
  crates rest on this survey alone.
- Rule 6's reach over eight `domain_name_system` variants is this file's reading; block 1136 did not
  ask for an offset.
- `file_system_contract`'s error numbers are wire values, and the contract-crate layout decision
  may shape the type that replaces them.
- Rule 8 was traced for 2 of 15 multi-entry enums.
