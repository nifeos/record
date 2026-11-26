---
status: PROPOSED
raised: 2026-11-26
---

# 329. One error convention for the library crates

*(The section number and title are provisional until the merge lands them. So is every name below
that does not exist yet: the fields `offset` and `source`, the method `into_inner`, and each new
error type.)*

The survey reads each crate's `origin/main` on 2026-11-26 (UTC), at the commits in the first table.

## Background

The partsfoundry library crates report failure in many ways, from an error enum with `Display` and
`core::error::Error` to a raw `i32`. Milestone 1129 (the combine review) lists errors as the first
shape to share. Twelve release reviews (blocks 1134 to 1148) hold an
errors paragraph each, and six of their findings wait on this decision.

It matters now because the publishing hold waits on it: each crate's first crates.io publish and its
0.1.0 interface wait for every shared decision that touches it. Nothing is on crates.io yet, so an
edit can still change any shape. After publish, an error's shape becomes a one-way door. A new variant in an exhaustive enum, a new
field in a variant, or a tuple variant turned into a named one breaks every caller that matches it.
A new trait implementation breaks nobody. So the part that cannot wait is the shape, not the traits.

## The recommendation

Adopt option A, the convention below, for every library crate, and give each crate's release review
a finding that follows it.

1. A refusal is a `Result<_, E>`, where `E` is a type of the crate: never `()`, `bool`, a bare `T`
   or a raw integer. `Option` answers only an ordinary absence, such as a lookup that finds nothing,
   an iterator's end, or a report that carries no state (block 1111's decision 3 stands).
2. Every public error type implements `Debug`, `Display` and `core::error::Error`. A type generic
   over a device error `E` displays for any `E` and is an `Error` when `E` is one. The types hold
   plain data, so they are `Send`, `Sync` and `'static`.
3. A message describes its own level only, in lower case with no closing period. An error that wraps
   another returns it from `source` and leaves it out of `Display`.
4. Every public error enum is `#[non_exhaustive]`, and so is each of its variants that has fields. A
   unit variant stays plain. An error struct keeps its fields private behind accessors or carries
   `#[non_exhaustive]`.
5. Named fields hold a variant's data. A tuple variant holds one wrapped error and nothing else. A
   variant that holds a wrapped error beside other data names that field `source`.
6. A failure says where it happened and gives back what it took. A parser that walks a
   variable-length structure through offsets puts the byte offset in a field named `offset` on each
   variant that refuses a part of the structure. A variant with a fixed position needs none, such as
   a header field or a buffer that ends too soon. A call that takes ownership of a value and refuses
   it hands the value back through `into_inner`, as `TrySendError<T>` does.
7. Each family of operations that fail the same ways gets one error enum, named for what it refuses:
   one per module or per group of entry points, not one per crate and not one per function.

The crates write the implementations by hand. A derive crate such as `thiserror` needs its own
dependency ruling, and a crate can adopt one later without touching its interface.

The reason: rules 4 to 6 alone become one-way doors at publish, and they cover what the reviews keep
finding: positional variants, no location, a dropped value, enums that cannot grow. Deciding the traits alone (option B) leaves each crate to settle the one-way
part by itself, and the reviews already give four answers. On a close call the stricter rule wins:
a crate can drop `#[non_exhaustive]` after publish without breaking anyone, but cannot add it.

## Is the premise true

The premise is that the crates disagree in shape as well as in traits. The source agrees. Of 51
types and 261 variants in 17 crates, 32 variants in 8 crates keep data in positional fields. 19
types in 9 crates lack `core::error::Error` (18 lack `Display` too), and 18 types in 11 crates lack
`#[non_exhaustive]`. No crate marks a variant with it.

Wrapping takes four forms. `file_allocation_table` returns the inner error from `source` and
leaves it out of `Display`. `e1000e` does both. `designware_mobile_storage` renders it and has no
`source`. `designware_ethernet` and `domain_name_system` do neither. The standard library's `Error`
documentation says to do one or the other, never both.

The census of milestone 1129 missed `grant_plan`'s `NameSetFull` and `NoJobNamed` and
`program_argument_contract`'s `WrongPageLength`, and eight crates moved past its commits.

## What the crates do today

"D/E" counts the types with `Display` and `core::error::Error`; "n_e" counts the types marked
`#[non_exhaustive]`; "positional" counts variants with data in tuple fields, leaving out a tuple
variant that only wraps another error.

| crate | commit | types | variants | D/E | n_e | positional | wrapping |
|---|---|---|---|---|---|---|---|
| `address_space_layout` | `9568826fc8` | 1 | 2 | Display only | 0 | 0 | none |
| `block_roster_contract` | `f0c199acc9` | 2 | 5 | 2/2 | 1 | 0 | none |
| `capability_table` | `a0e8b159e5` | 1 | 5 | 1/1 | 0 | 0 | none |
| `designware_ethernet` | `f518554c96` | 4 | 12 | 0/0 | 4 | 1 | 2 variants, neither form |
| `designware_mobile_storage` | `f52f89aca2` | 4 | 31 | 4/4 | 4 | 20 | 7 variants rendered, no `source` |
| `device_tree_blob` | `c888b6ace4` | 1 | 10 | 1/1 | 1 | 4 | none |
| `domain_name_system` | `748394ad7f` | 2 | 19 | 0/0 | 1 | 1 | 1 variant, neither form |
| `e1000e` | `42cdc139a8` | 4 | 20 | 4/4 | 4 | 0 | 2 variants, both forms |
| `entropy_contract` | `5150f14f78` | 3 | 2, and 2 unit structs | 2/3 | 1 | 0 | none |
| `environment_contract` | `62ea88d90a` | 1 | 3 | 1/1 | 0 | 0 | none |
| `file_allocation_table` | `b55594420e` | 15 | 87 | 15/15 | 15 | 3 | `source` only, in 8 types |
| `grant_plan` | `69aedfbc9a` | 5 | 51, and 2 unit structs | 0/0 | 0 | 1 | none |
| `interfaces_note` | `088baba279` | 2 | 4, and a struct with public fields | 0/0 | 0 | 1 | none |
| `line_editor` | `2c625ef614` | 1 | 3 | 0/0 | 0 | 1 | none |
| `non_volatile_memory_express` | `60b34280ec` | 2 | 2 structs | 2/2 | 2 | 0 | none |
| `program_argument_contract` | `b097970b86` | 2 | 1, and a unit struct | 0/0 | 0 | 0 | none |
| `universal_serial_bus` | `4612f6b5e5` | 1 | 6 | 0/0 | 0 | 0 | none |

Twelve crates have no error type. Rule 1 reaches three of them:

- `generational_table` (`b5243332a6`): `insert` returns `Option<EntryName<T>>` and drops the value
  when the table is full.
- `extensible_host_controller_interface` (`a10790e155`): `ProducerRing::complete` answers `false`
  for a stale and a foreign address alike, and `find_extended` answers `None` for four endings, two
  of which mean a broken controller.
- `file_system_contract` (`0551506169`): `extended_attribute::set` and `remove` return
  `Result<usize, i32>` with five error numbers.

The other nine have nothing to refuse. In the one repository that depends on the crates today, a
resolver matches `domain_name_system::Reject` with a wildcard arm already, and a shell names
`grant_plan::Refusal` variants 14 times.

## Prior art, read 2026-11-26 (UTC)

I read each crate's source from crates.io, the standard library in rustc 1.102.0-nightly
(2026-11-22), and the API Guidelines at `rust-lang/api-guidelines@97a0969cb0`. Demand comes from the
crates.io API the same day.

| crate | version | downloads | 90 days | reverse dependencies | last updated |
|---|---|---|---|---|---|
| `thiserror` | 2.0.21 | 1,955,601,074 | 576,609,056 | 82,345 | 2026-09-23 |
| `nom` | 8.0.0 | 940,000,930 | 255,249,950 | 2,637 | 2025-01-26 |
| `object` | 0.41.0 | 745,726,836 | 158,972,925 | 582 | 2026-11-10 |
| `arrayvec` | 0.7.8 | 731,364,861 | 198,482,924 | 1,283 | 2026-07-02 |
| `embedded-io` | 0.7.1 | 204,395,110 | 94,206,861 | 353 | 2025-10-01 |
| `heapless` | 0.9.4 | 192,753,758 | 64,850,554 | 1,239 | 2026-11-18 |
| `embedded-hal` | 1.0.0 | 41,184,610 | 10,193,281 | 1,852 | 2024-01-09 |
| `fdt` | 0.1.5 | 1,713,432 | 471,091 | 7 | 2026-10-01 |

### The standard library

`core::error::Error`'s documentation sets the message style (lower case, no trailing punctuation)
and the wrapping rule (`source` or `Display`, not both). `io::ErrorKind` is `#[non_exhaustive]`
with 44 variants. `Utf8Error` keeps `valid_up_to` private behind an accessor, and
`mpsc::TrySendError<T>` returns the unsent value in `Full(T)`. We choose `source` over rendering, so a
chain printer shows each level once.

### The API Guidelines, C-GOOD-ERR

Every error type implements `Error`, `Send` and `Sync`, and `()` never serves as an error. Rules 1
and 2 restate this item; rules 4 to 6 add what it leaves out.

### embedded-hal 1.0.0

Each module's `Error` trait asks only for `Debug` and a `kind()` onto a shared `#[non_exhaustive]`
`ErrorKind`. The
trait does not extend `core::error::Error`, though each `ErrorKind` implements it. It serves one
trait with many implementers: a driver generic over SPI tests for `ErrorKind::Overrun` without
knowing the bus. Each of our crates is one implementer.

### embedded-io 0.7.1

`Error` extends `core::error::Error` and adds `kind()` onto an 18-variant `#[non_exhaustive]`
`ErrorKind` that mirrors the standard library's. `ReadExactError<E>` is exhaustive (`UnexpectedEof`,
`Other(E)`), displays its `Debug` form and has no `source`. Rule 3 would give `Other(E)` a
`source`; whether a device error exposes `embedded_io::ErrorKind` belongs to the byte sinks
decision.

### nom 8.0.0, a no_std parser

The default `Error<I>` has two public fields: `input`, the remaining input, which serves as the
location, and `code`, an exhaustive `ErrorKind` of 57 variants. It carries location, as rule 6 asks, through public fields over an
exhaustive kind, which rule 4 refuses.

### fdt 0.1.5 and object 0.41.0

`fdt`'s `FdtError` has three unit variants (`BadMagic`, `BadPtr`, `BufferTooSmall`), is exhaustive,
implements `Display` and lacks `Error`, with no location. `object`'s read `Error` wraps one private
`&'static str` with `Display` and `Error`: a caller can print it and cannot match it. Rule 7 keeps
enums a caller can match, and rule 6 adds the location both lack.

### thiserror 2.0.21

It is `no_std` and implements `core::error::Error`. Its `source` returns the field marked
`#[source]` or named `source`, and a `#[from]` variant holds the source error and nothing else.
Rule 5 matches that shape, so a crate that switches to it later changes no public item. We differ
only in writing the code by hand.

### arrayvec 0.7.8 and heapless 0.9.4

`arrayvec`'s `try_push` returns `CapacityError<T>`, which keeps the element private behind
`element()` and implements `Error` under `std`. `heapless`'s `Vec::push` returns a bare `T`, which
cannot implement `Error`. Rule 6 takes `arrayvec`'s shape with the standard library's method name.

## Options

### A. The full convention (recommended)

Rules 1 to 7. Cost by crate ("name" turns a positional variant into named fields, "mark" adds
`#[non_exhaustive]`, "traits" adds `Display` and `Error`):

| crate | what changes | types | variants |
|---|---|---|---|
| `address_space_layout` | `Error`; mark the enum and its two struct variants | 1 | 2 |
| `block_roster_contract` | mark `TooManyDevices` | 1 | 0 |
| `capability_table` | mark the enum | 1 | 0 |
| `designware_ethernet` | traits on four; one `source`; name 1; mark 4 variants | 4 | 5 |
| `designware_mobile_storage` | name 20; stop rendering 7 wrappers (2 among the 20); two `source` | 4 | 25 |
| `device_tree_blob` | name 4; `offset` on 5 (`BadToken` in both) | 1 | 8 |
| `domain_name_system` | traits on both; mark `Reject`; name 1; one `source`; `offset` on 8 | 2 | 10 |
| `e1000e` | stop rendering in two wrapping variants | 1 | 2 |
| `entropy_contract` | traits on `Refusal`; mark two unit structs and `ShortReply` | 3 | 1 |
| `environment_contract` | mark the enum | 1 | 0 |
| `file_allocation_table` | name 3; mark 5 variants | 4 | 8 |
| `grant_plan` | traits and mark on five; name `NoSuchCapability` | 5 | 1 |
| `interfaces_note` | traits and mark on both; name `BadField` | 2 | 1 |
| `line_editor` | traits and mark; name `Layout` | 1 | 1 |
| `program_argument_contract` | traits and mark on both | 2 | 0 |
| `universal_serial_bus` | traits and mark; mark 3 variants; `at` becomes `offset` | 1 | 3 |
| `generational_table` | a new refusal type generic over `T`, with `into_inner` | new 1 | new |
| `extensible_host_controller_interface` | new error types for `complete` and `find_extended` | new 2 | new |
| `file_system_contract` | a new error type for the five error numbers | new 1 | new |

In all, 34 of the 51 types change in 16 crates, 67 variants change shape, and 3 crates gain 4 new
types. `non_volatile_memory_express` already conforms. A caller gains `{ .. }` in a pattern on a
marked variant and a wildcard arm in an exhaustive match.

### B. The traits only

Rules 1 to 3; each crate's review settles its own shape. Cost: 22 types in 11 crates and the same 4
new types. It skips the 18 markings, the 32 positional variants and the 13 offsets, which make up
the one-way part. A trait can arrive after publish in a minor release, and a variant's shape cannot.

### C. A shared error kind, as embedded-hal has

A, plus a new shared crate with one `#[non_exhaustive]` `ErrorKind` and a `kind()` on every error.
Cost: A's, plus a crate, a dependency from 17 crates and a kind for each of 261 variants. The crates
share no failure vocabulary: a FAT cluster chain and a refused shell option have no common kind but
`Other`, and it binds crates that stand alone.

### D. One error enum per crate

Every crate returns one enum, as `device_tree_blob` and `capability_table` do. Cost: 45 types merge
into 11 in 11 crates (15 into 1 in `file_allocation_table`), and every fallible signature there
changes. A caller then matches variants a call can never return: a FAT format call would carry a
device error it never produces.

## Which waiting findings each option settles

| finding | A | B | C | D |
|---|---|---|---|---|
| 1135 door 1, `insert` drops the refused value | yes | the type only | yes | yes |
| 1136 item 2, `Error` and `Reject` lack the traits | yes | yes | yes | yes |
| 1140 D1, `restore` answers `Option<()>`; `Refusal` traits | yes | not the marking | yes | yes |
| 1142 P0-2 and D2, positional variants | yes | no | yes | no |
| 1144 P0-3 and D3, no location | yes | no | yes | no |
| 1146 P0-8 and D9, refusals by `bool`, `Option` and panic | yes | the traits only | yes | yes |
| 1147 P0-3 and D3, no `Display`, `Error` or `source` | yes | yes | yes | yes |
| 1148 P1-1, D1, D4 and D7 | yes | P1-1 only | yes | yes |

Under A, rule 7 settles 1148's D4. `file_allocation_table` (1143) and `e1000e` (1145) have no waiting finding; A gives each one
more, of 8 and 2 variants.

## Reversibility, and who has acted on it

Before first publish every option is reversible, since a pre-release tag promises nothing. The
callers that acted on today's shapes live in the one repository that pins these crates, and the
lane that changes a crate changes them too. After publish, a marked enum or variant under A gains
variants and fields in a minor release; B, C and D leave enums that grow only in a major release.

## The seven questions

1. Alternatives: B, C and D under Options, each with why it lost.
2. The tree: `file_allocation_table` already writes rules 2 and 3 down in `src/error_display.rs`.
3. Prior art: read in source, above.
4. The premise: true, by the counts under Is the premise true.
5. Cost: measured per crate under option A; B, C and D beside it.
6. Reversibility: full until each crate's first publish; afterward A keeps growth compatible.
7. At equal cost, A still wins. It costs the most work, so effort does not drive it.

## A concrete example

```rust
// device_tree_blob today
#[non_exhaustive]
pub enum Error { BadMagic(u32), BadToken(u32), Truncated, /* seven more */ }

// under A (field names provisional)
#[non_exhaustive]
pub enum Error {
    #[non_exhaustive]
    BadMagic { found: u32 },
    #[non_exhaustive]
    BadToken { token: u32, offset: usize },
    #[non_exhaustive]
    Truncated { offset: usize },
    /* seven more */
}
```

A reader of the boot error learns the byte where the blob went wrong, and a later release can add a
field to any variant without breaking a caller. For wrapping,
`designware_mobile_storage`'s `InitializationError::GoIdle` would display `CMD0 failed` and return
the host controller's error from `source`.

## What was not checked

- Nothing compiled. A script made the counts, with a reading where it could not decide; the caller
  counts are rough greps, and I did not check which caller matches are exhaustive.
- Lanes E to J of milestone 1129 have not reviewed their crates yet, so the costs for `grant_plan`
  and the contract crates rest on this survey alone.
- Rule 6's reach over eight `domain_name_system` variants is this file's reading; block 1136 did not
  ask for an offset.
- `file_system_contract`'s error numbers are wire values, and the contract-crate layout decision
  may shape the type that replaces them.
- I did not check `Send` and `Sync` per type; every type read holds plain data.
