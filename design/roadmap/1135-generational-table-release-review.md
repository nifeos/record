---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1048, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1135. `generational_table`: the release review's findings

*(The number and the slug are provisional.)*

Raised by review lane A of [milestone 1129 (the combine review)](1129-crate-interfaces-best-in-class.md). The lane read
`partsfoundry/generational_table` at `b524333`, the head of its `main`, as someone choosing between
it and `slotmap` would. It wrote nothing to any repository. The baseline is
[the outside review, 1048](1048-generational-table-outside-review.md), with
[the review package](../../notes/crate-reviews/generational-table.md). The first-fit order and the
two-array layout that 1048 settled stay closed. The ratified names all pass the naming rules in
force today, so none reopens.

Reuse: the crate's tests, its `benches/` target, and a scratch benchmark crate that
[the benchmark appendix](1135-generational-table-release-review/benchmark.md) describes. No new tool.

## Goal

A caller who outgrows `heapless` or cannot allocate for `slotmap` finds a table whose full-table
refusal keeps the value, whose iterators a caller can name and store, and whose every method shows its
use in an example.

## Finding status

Each line reads against `partsfoundry/generational_table` at `b524333`.

- Item 1 (P0), a full table drops the value it refused: Open.
- Item 2 (P1), fourteen public methods have no example: Done, partsfoundry/generational_table#29.
- Item 3 (P2), iterators a caller cannot name: Done, partsfoundry/generational_table#29.
- Item 4 (P2), no `for` loop over a table: Done, partsfoundry/generational_table#29.
- Item 5 (P2), no `retain`: Done, partsfoundry/generational_table#29.
- Item 6 (P2), no way to borrow two entries mutably: Done, partsfoundry/generational_table#29.
- Item 7 (P2), the worst insert scans every slot: Will not fix, ruled 2026-11-26 (provisional).
  A free-slot bitmap needs an array whose size is computed from `N`, which stable Rust cannot
  express, and each stable alternative (a second constant parameter, a free list, a third array)
  breaks the closed size, layout or first-fit order. It reopens when that size becomes
  expressible.
- Item 8 (P2), crates.io metadata: Done, partsfoundry/generational_table#29.

## Prior art

Measured from the crates.io API on 2026-11-26 at 07:32 (UTC). The leading comparator is `slotmap`.

| crate | role | version | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `slotmap` | leading | 1.1.1 | 142,344,145 | 43,994,308 | 624 | 2025-12-06 |
| `generational-arena` | comparator | 0.2.9 | 10,976,883 | 1,261,679 | 57 | 2023-05-22 |
| `thunderdome` | comparator | 0.6.1 | 1,203,898 | 198,775 | 32 | 2023-06-25 |
| `slotmap-careful` | comparator | 0.9.1 | 1,021,896 | 351,550 | 7 | 2026-11-04 |
| `typed-generational-arena` | comparator | 0.2.9 | 100,963 | 12,002 | 3 | 2025-05-26 |
| `slab` | neighbor (no generations) | 0.4.12 | 1,192,319,245 | 321,019,744 | 642 | 2026-01-31 |
| `heapless` | neighbor (fixed capacity, no generations) | 0.9.4 | 192,279,070 | 64,375,866 | 1,236 | 2026-11-18 |

The review read the source of `slotmap`, `thunderdome`, `generational-arena`, `slab` and `heapless`
at these versions. It measured `slotmap-careful` and `typed-generational-arena` without reading them.

| axis | `generational_table` | `slotmap` 1.1.1 | `thunderdome` 0.6.1 |
|---|---|---|---|
| allocation | none: `N` slots inline | `Vec`, needs `alloc` | `Vec`, needs `alloc` |
| full | `insert` returns `None` | `insert` panics; `try_insert_with_key` | grows |
| a reused generation | retires the slot at `u32::MAX` | wraps after 2^31 reuses | wraps to 1 |
| name type | `EntryName<T>`, typed by entry | a `Key` type the caller declares | one `Index` |
| `const` constructor | yes | no | no |
| named iterators | no | yes, `ExactSize` and `Fused` | yes |
| `retain`, `drain` | no | both | both |
| two mutable entries | no | `get_disjoint_mut` | `get2_mut` |
| `serde` | no | optional feature | no |

## What the crate does better

- Against `slotmap` and `thunderdome`: no allocation at all, and a `const fn new` that can fill a
  `static`. Both rivals need `alloc`.
- Against both: the table refuses a stale name forever. Their own documentation and source say their
  generation wraps, `slotmap`'s after 2^31 reuses of a slot and `thunderdome`'s back to 1. This crate
  retires the slot instead and proves the property with Kani.
- Against `thunderdome`: the name carries its entry type, so a name from one table cannot index a
  table of another entry type. `slotmap` needs a declared key type to get the same.
- Against both: `iter_from_slot_index` resumes a sweep after the caller gives a lock back, which neither has.
- On a sum over a half-empty table it was the fastest of the three (see *Benchmarks*).

## Findings

Each finding states its evidence, its change, and whether the lane verified it in the source or
inferred it. Each names its door and an effort size: XS under an hour, S a few hours, M a day or two.

### P0

#### Item 1: A full table drops the value it refused

`insert(value) -> Option<EntryName<T>>` drops `value` when every slot is live or retired, and its
documentation says so. A caller who must not lose the value, such as a handle it must close,
has to test for space first or build the value inside `insert_with_name`. The fixed-capacity
neighbor gives the value back: `heapless` 0.9.4's `Vec::push` returns `Result<(), T>`. `slotmap`
1.1.1 never refuses, and panics when full.

Change: `insert` returns a `Result` whose `Err` gives the refused value back, in the shape door 1
below settles. `insert_with_name` builds nothing on a full table and keeps `Option`. 1048's item 6 specified the
`Option` return. This review reopens the return type, not the ratified name. Verified in the source.
One-way: see door 1 below. Effort S, with the callers.

### P1

#### Item 2: Fourteen public methods have no example

`new`, `get`, `get_mut`, `contains_key`, `remove`, `len`, `is_empty`, `slot_count`, `values`,
`values_mut`, `iter`, `iter_mut`, `EntryName::to_bits` and `EntryName::from_bits` carry no example.
`slotmap` 1.1.1's `src/basic.rs` has thirty public functions and thirty examples. The crate page
and four methods do have one, and the README runs as a doctest.

Change: one short example on each. Verified by reading each item's documentation. Two-way.
Effort S.

### P2

#### Item 3: Iterators a caller cannot name

`values`, `values_mut`, `iter`, `iter_mut` and `iter_from_slot_index` return `impl Iterator`. A
caller cannot store one in a struct, and none reports an exact length or promises to stay finished.
`slotmap` names each iterator and implements `ExactSizeIterator` and `FusedIterator` on it. The
table knows its live count, so an exact length costs a counter.

Change: named iterator types with those two traits, and `DoubleEndedIterator` where a reverse walk
is cheap. Callers cannot name an opaque return type, so naming it later breaks nobody. Verified.
Two-way. Effort S.

#### Item 4: No `for` loop over a table

`for (name, value) in &table` does not compile, because the crate implements no `IntoIterator` for
`&Table` or `&mut Table`, and none for `Table` by value. `slotmap` and `thunderdome` implement all
three.

Change: the three implementations, over item 3's named types. Verified. Additive, two-way.
Effort XS.

#### Item 5: No `retain`

Removing every entry that fails a test takes `iter`, a buffer of names, then `remove` for each,
and a `no_std` caller has no growable buffer. `slotmap` and `thunderdome` each have `retain`.
`thunderdome`'s closure receives the name as well.

Change: `retain(|name, value| keep)`, bumping each removed slot's generation as `remove` does.
Verified absent; the lane infers the need from both comparators. Additive, two-way. Effort S, with a
Kani harness.

#### Item 6: No way to borrow two entries mutably

`slotmap` has `get_disjoint_mut([K; N]) -> Option<[&mut V; N]>`, and `thunderdome` has `get2_mut`.
Here a caller who updates two entries together removes one and inserts it back, which mints a new
name. Change: `get_disjoint_mut`, spelled as the standard library's slice method. Verified absent.
Additive, two-way. Effort S.

#### Item 7: The worst insert scans every slot

Take a table of 4,096 with only slots 0 and 4,095 free. The insert that lands in slot 4,095 scans
the whole array and takes 1,855 ns. `slotmap` takes about 5 ns and `thunderdome` 7 ns, because their
free lists pop in constant time. The cursor of 1048's item 9 removes the scan only when the next free slot sits
low.

Change: a bitmap of free slots, one bit per slot, so the scan reads `N / 64` words and keeps
first-fit order. The lane verified the measurement and infers the gain. Two-way, since it changes only
the inside. Effort M, with the proofs.

#### Item 8: crates.io metadata

`Cargo.toml` has no `documentation` field, and the categories lack `no-std::no-alloc`, which fits
exactly. Change: add both. Verified. Two-way. Effort XS.

## One-way doors

1. The return of `insert` (item 1). A bare `T` in `Err`, as `heapless` returns, cannot implement
   `core::error::Error`, so `?` cannot carry it into a caller's error and it prints as nothing in
   particular. `arrayvec` 0.7.8's `try_push` returns `CapacityError<T>`, which implements `Error` and
   gives the value back through `element`; the standard library's `TrySendError<T>` does the same
   for a channel. Recommended: a refusal type of that shape, generic over `T`, with a method that
   returns the value, decided together with milestone 1129's shared error decision so it prints and
   chains like the other crates' errors. It costs one call at a caller that wants the value back,
   and `.ok()` at one that wants the old `Option`.
2. The bit layout of `EntryName`. `to_bits` and `from_bits` make the generation-high, slot-low
   packing part of the interface, since a caller passes names across a boundary as words.
   `EntryName::NEVER_MINTED`, the word `u64::MAX`, is part of that layout: a caller may store it as
   "no entry", so no slot and generation may ever pack to it. Recommended: keep the layout and that
   reserved word as built, and say in the documentation that both are stable for the 0.x series.
3. Retiring a slot rather than wrapping its generation. A table shrinks by one slot after
   2^32 - 1 reuses of that slot. Recommended: keep it, since it is the safety property the proofs
   carry.
4. `Hash`, `Ord` and `PartialEq` on `EntryName<T>` for every `T`, and no `PartialEq` on `Table`.
   Adding a bound later breaks callers. Recommended: keep as built.

## Benchmarks

A Linux x86_64 host (an Intel Xeon Platinum 8160 at 2.10 GHz), rustc 1.100.0, release profile.
`N` is 4,096, the values are `u64`, and each rival reserved 4,096 slots in advance.

| workload | `generational_table` | `slotmap` | `thunderdome` |
|---|---|---|---|
| one insert and one remove | 6.62 ns | 3.70 ns | 6.30 ns |
| one `get`, cycling over 4,096 live names | 1.57 ns | 1.50 ns | 1.36 ns |
| one insert into the far free slot (item 7) | 1,855 ns | 4.89 ns | 6.92 ns |
| summing the values of a half-empty table | 2,098 ns | 2,511 ns | 2,768 ns |

What each row times and the command are in
[the benchmark appendix](1135-generational-table-release-review/benchmark.md).

## The checklist

[The checklist appendix](1135-generational-table-release-review/checklist.md) marks all 54 items of
the Rust API Guidelines checklist. Four are not met: C-ITER (item 4), C-ITER-TY (item 3),
C-EXAMPLE (item 2) and C-METADATA (item 8).

## Done when

- Item 1 lands, or the architect rules door 1 another way, before the 0.1.0 interface freezes.
- Item 2 lands before the first release.
- Items 3 to 8 land, or each carries a ruling against it.

## BUGS

- The lane neither read nor benchmarked `slotmap-careful` or `typed-generational-arena`.
- The benchmark ran on one machine.

## Follow-on

- **Outstanding.** Items 1 to 8, open on the crate's `main` at `b524333`.
- **Outstanding.** The four one-way doors, for the architect.

## Index row

The release review of `generational_table` against `slotmap` and `thunderdome`. One item blocks the
0.1.0 interface: a full table should hand the refused value back. Missing examples land before the
release. Six may follow: named iterators, `IntoIterator`, `retain`, two mutable borrows, a free-slot
bitmap and the manifest metadata. Four one-way doors are for the architect.
