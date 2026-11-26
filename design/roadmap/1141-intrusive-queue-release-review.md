---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1141. `intrusive_queue`: the release review's findings

The release review of `partsfoundry/intrusive_queue` at commit `7368a9e3`, under
[milestone 1129](1129-crate-interfaces-best-in-class.md). Its baseline is
[milestone 1097](1097-intrusive-queue-outside-review.md), every finding of which has landed, and
the cleared package [`notes/crate-reviews/intrusive-queue.md`](../../notes/crate-reviews/intrusive-queue.md).
The `Unqueued` token, the `Send` bound and the seven ratified names stand; the one thing reopened
is the shape of the `Node` trait, on Miri evidence 1097 did not have.

Reuse: the prior-art table weighs each intrusive list a caller could take instead.

## Finding status

- P0-1, `set_next` takes the whole node by `&mut`: Open.
- P1-1, `Iter` has no `Debug`, `Clone` or exact size: Open.
- P2-1, the standard collection traits: Open.
- P2-2, `front` and `append`: Open.
- P2-3, `Sync` when `T: Sync`: Open.
- P2-4, the examples unwrap: Open.
- P2-5, the bound on the struct declarations: Open.
- P2-6, removal in constant time: Open.

## Open decisions

One-way doors D1 and D2 below, for the architect.

## Goal

A stranger choosing between this crate, `intrusive-collections` and `cordyceps` finds the fastest
queue at what it does. Its trait lets a caller keep a reference to a node's other fields while the
node waits in the queue, and it implements the traits people expect of a collection.

## What the review read and ran

The commands, the Miri runs, the benchmark source and the comparators read are in
[the appendix](1141-intrusive-queue-release-review/what-was-checked.md). The 54 API Guidelines
items are in [the guidelines table](1141-intrusive-queue-release-review/api-guidelines.md).

## Prior art

Measured from the crates.io API on 2026-11-26 (UTC).

| crate | role | version read | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `intrusive-collections` | ranked 1 | 0.10.3 | 28,464,134 | 10,097,123 | 52 | 2026-08-04 |
| `cordyceps` | ranked 2 | 0.3.5 | 10,946,186 | 5,014,427 | 12 | 2026-07-29 |
| `pin-list` | ranked 3 | 0.1.2 | 1,491,602 | 1,441,663 | 5 | 2025-03-27 |
| `heapless` | neighbor: owning fixed-capacity queues | 0.9.4 | 192,279,070 | 64,375,866 | 1236 | 2026-11-18 |

No integration crate applies: the traits a queue meets are the standard library's.

### What `intrusive_queue` does better

- Than `intrusive-collections`: one trait with two methods, against an adapter macro and three
  unsafe traits (`Adapter`, `PointerOps`, `LinkOps`). Its singly linked list has no `push_back`, so a
  first-in, first-out queue there needs the doubly linked list and its second pointer per node.
  A pop and a push cost 1.48 to 1.71 ns here against 2.31 to 2.53 ns there (measured below).
- Than `cordyceps`: a pop and a push cost about half as much (3.02 to 3.36 ns there). Its
  `remove` is a safe function that walks the queue, where `cordyceps`'s constant-time `remove` is
  `unsafe` because the caller must promise the node is on that list. The `Unqueued` token makes
  pushing a node twice without popping it a type error; `cordyceps` takes the handle type the
  caller's `Linked` implementation names, and a raw `NonNull` handle carries no such guard.
- Than `pin-list`: no `Pin`, no allocation and no per-node lifetime: it fits a kernel's static
  tables, where `pin-list` serves an async waker's stack-pinned node.
- Than all three: a Kani harness and a falsification patch for each operation.

## The items

Effort is S (half a day), M (a day or two) or L (longer). A door is one-way when someone outside
the repository acts on it after 0.1.0. Every P0 is a one-way change, so it lands in 0.1.0 or never.

### P0: the 0.1.0 interface

#### P0-1. `set_next` takes the whole node by `&mut`

Verified with Miri (nightly, 2026-10-31).
`Node::set_next(&mut self, ...)` makes the queue form a unique reference to the whole node on every
push. A caller that holds `&(*node).id`, a shared reference to a field that is not the link,
across `push_back` has undefined behavior under Stacked Borrows: Miri reports the reference
"later invalidated ... by a Unique function-entry retag" at the queue's `set_next` call. The same
program passes under Tree Borrows. A trait in the shape of `cordyceps` 0.3.5's `Linked::links`,
`unsafe fn link(this: NonNull<Self>) -> NonNull<Option<NonNull<Self>>>`, projects to the link
field by raw pointer, and the same sequence passes under both models.
Milestone 1097 weighed the reference-free shape (its item 5) and kept this one, on the argument
that a held `&mut` breaks the aliasing rules under either shape. That holds for a `&mut` to the whole node; the
experiment here is about a shared reference to another field, which only the projection keeps
valid. `intrusive-collections` keeps its links in `Cell`s, which has the same effect.
Change: the projection shape, with the queue's every link access through it. Rule 3 of
`Unqueued::new` stays as written for 0.1.0; it can relax later to "no reference to the link",
which breaks no caller. Door: one-way (D1). Effort: M, with the harnesses and the patches.

### P1: before the first release

#### P1-1. `Iter` has no `Debug`, `Clone` or exact size

Verified in source (C-DEBUG, C-COMMON-TRAITS).
`Queue` and `Unqueued` print; the walk does not, and a caller cannot clone it to walk twice.
`intrusive-collections` 0.10.3's `Iter` is `Clone`, and `cordyceps` 0.3.5's is an
`ExactSizeIterator`; neither prints. The queue keeps its length, so this walk can report it too.
Change: `Debug`, `Clone` and `ExactSizeIterator` on `Iter`. Door: two-way. Effort: S.

### P2: may follow

#### P2-1. The standard collection traits

Verified in source (C-COLLECT).
There is no `Extend<Unqueued<T>>`, no `FromIterator<Unqueued<T>>` and no `IntoIterator for &Queue`.
`cordyceps` 0.3.5 implements all three. Change: add them. Door: two-way. Effort: S.

#### P2-2. `front` and `append`

Verified in source.
A caller cannot look at the head without popping it, or join two queues in constant time;
`cordyceps` has `front` and `append`, and `intrusive-collections` has `front` and a cursor's
`splice_after`. Change: `front(&self) -> Option<NonNull<T>>` and `append(&mut self, &mut Queue<T>)`,
names provisional. Door: two-way. Effort: S.

#### P2-3. `Sync` when `T: Sync`

Verified in source (C-SEND-SYNC).
`&Queue` offers only `is_empty`, `len` and `iter`, which yields pointers; it would be sound to
share. `cordyceps` is `Sync` for `T: Sync`. Change: the implementation, with a compile-fail
doctest as the `Send` bound has. Door: two-way. Effort: S.

#### P2-4. The examples unwrap

Verified in source (C-QUESTION-MARK).
Each example unwraps `NonNull::new` and `pop_front`. Change: examples that return a `Result` or
an `Option` and use `?`. Door: two-way. Effort: S.

#### P2-5. The bound on the struct declarations

Verified in source (C-STRUCT-BOUNDS).
`Queue<T: Node>` and `Iter<'a, T: Node>` bound the type parameter where the fields need no bound.
Change: move the bound to the `impl` blocks. Door: two-way, since removing a bound breaks no
caller. Effort: S.

#### P2-6. Removal in constant time

Measured (below).
`remove` walks from the head, as its documentation and the BUGS section state. Taking the node at
the back of 1024 costs about 1,300 ns here against 1.5 ns in `intrusive-collections` and 3 ns in
`cordyceps`, whose lists are doubly linked. A caller that removes often wants a doubly linked type.
Change: a separate doubly linked type when a caller asks, beside this one. Door: two-way (an
addition). Effort: L.

### Measured performance

Run on a Linux x86_64 host with rustc 1.100.0, `cargo build --release && ./target/release/iq_bench`,
twice, each figure the best of five passes timed with `std::time::Instant`. Every node is its own
heap allocation, and each step reads one field of the node it moves. The source is in the appendix.

| operation | `intrusive_queue` | `intrusive-collections` | `cordyceps` |
|---|---|---|---|
| pop the front and push it back, 1024 nodes, per step | 1.71 ns, 1.48 ns | 2.53 ns, 2.31 ns | 3.36 ns, 3.02 ns |
| remove one node and push it back, 1024 nodes, per step | 1312.85 ns, 1286.81 ns | 1.59 ns, 1.49 ns | 2.97 ns, 2.97 ns |

After the first removal the node sits at the back, so the second row is this crate's worst case.

## One-way doors

- D1, the `Node` trait's shape (P0-1). Recommended: the projection shape, as `cordyceps`
  has it, before 0.1.0. The current shape forbids, under Stacked Borrows, a reference that the
  projection allows, and the trait is the one thing every caller implements.
- D2, what `Iter` yields. Today `NonNull<T>`. Recommended: keep it. Yielding `&T` would hold a
  reference to the link while the caller could still push, which is sound only when the link sits
  in an `UnsafeCell`, as `cordyceps`'s `Links` does. A later release can add an adapter yielding `&T`.

## Follow-on

- **Outstanding.** D1 and D2 wait on the architect. The shared decisions take nothing from this
  crate, which has no error type, no byte sink and no feature.

## Done when

The P0 and P1 findings read Done, or Will not fix with its ruling, the architect has ruled D1 and
D2, and `script/review-status` shows the block BUILT.

## BUGS

- The Miri runs used a standalone program against the crate, not a caller's real tables.
- The benchmark is one machine and one node layout; a node in a table rather than in its own
  allocation would change every figure.

## Index row

The release review of `intrusive_queue` against `intrusive-collections`, `cordyceps` and
`pin-list`: the `Node` trait's shape as one P0 on Miri evidence, `Iter`'s traits, five additions,
and a benchmark where this queue leads on push and pop and trails on removal.
