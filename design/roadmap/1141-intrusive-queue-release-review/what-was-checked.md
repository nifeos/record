# What the review read and ran

An appendix to [the milestone](../1141-intrusive-queue-release-review.md).

## The crate

`partsfoundry/intrusive_queue` at `7368a9e32ec92095e2a7d246c93bc0bd8a858abb`, read in full:
`src/lib.rs`, `Cargo.toml`, `README.md` and `CHANGELOG.md`.

## The comparators read

Each `.crate` from crates.io at the version in the prior-art table, unpacked and read.

- `intrusive-collections` 0.10.3: the `Adapter`, `PointerOps` and `LinkOps` unsafe traits and
  the `intrusive_adapter!` macro; links built on `Cell`; `Box`, `Rc`, `Arc` and `UnsafeRef` as the
  owning pointers. `SinglyLinkedList` has `push_front` and cursors and no `push_back`;
  `LinkedList` has `push_back`, `pop_front`, `front` and a cursor's constant-time `remove`. Its
  `Iter` is `Clone` and `DoubleEndedIterator`.
- `cordyceps` 0.3.5: `Linked<L>` with `type Handle`, `into_ptr`, `from_ptr` and
  `links(NonNull<Self>) -> NonNull<L>`; `Links` wraps an `UnsafeCell`. `List` has `front` and
  `back` returning `Pin<&T>`, cursors, `append`, `split_off`, `drain_filter` and `pub unsafe fn
  remove` in constant time; it implements `Extend`, `FromIterator`, `IntoIterator`, `Drop`,
  `Debug` and `Default`, and is `Send` and `Sync` when `T` is. Its `Iter` is exact-size,
  double-ended and fused.
- `pin-list` 0.1.2 and `heapless` 0.9.4: their front pages and list types, for the roles in the
  table.

## The Miri experiments

`cargo +nightly miri test`, Miri 0.1.0 (f9ceb4a4d4 2026-10-31), on six small tests in two files,
each run alone under each model. Four of them came from the independent review of this block and
were rerun here. The first two run against the crate at the commit above. The others carry their
own queue or link, in one of two shapes: a raw projection to a bare `Option<NonNull<Self>>` field,
or a projection to an opaque `Link<T>` that wraps an `UnsafeCell`, as `cordyceps` 0.3.5's `Links`
does.

| test | Stacked Borrows (the default) | Tree Borrows (`MIRIFLAGS=-Zmiri-tree-borrows`) |
|---|---|---|
| the crate's `Node`, `&id` held across a push | undefined behavior: invalidated by the unique retag at `set_next` | passes |
| the crate's `Node`, no reference held | passes | passes |
| bare `Option` projection, `&id` held across a push | passes | passes |
| bare `Option` projection, `&mut id` held across a push | passes | passes |
| bare `Option` link, a whole-node `&Job` held while the link is written | undefined behavior | undefined behavior |
| opaque `Link<T>` around an `UnsafeCell`, a whole-node `&Job` held across a push | passes | passes |

The crate's `Node`, with a field reference held:

```rust
use core::ptr::NonNull;
use intrusive_queue::{Node, Queue, Unqueued};
struct Job { id: u32, next: Option<NonNull<Job>> }
unsafe impl Node for Job {
    fn next(&self) -> Option<NonNull<Self>> { self.next }
    fn set_next(&mut self, n: Option<NonNull<Self>>) { self.next = n; }
}
#[test]
fn shared_field_ref_across_push() {
    let a = Box::into_raw(Box::new(Job { id: 1, next: None }));
    let b = Box::into_raw(Box::new(Job { id: 2, next: None }));
    let mut q = Queue::new();
    unsafe {
        q.push_back(Unqueued::new(NonNull::new_unchecked(a)));
        let id: &u32 = &(*a).id;
        q.push_back(Unqueued::new(NonNull::new_unchecked(b)));
        assert_eq!(*id, 1);
        while let Some(t) = q.pop_front() { drop(Box::from_raw(t.as_ptr())); }
    }
}
```

The bare `Option` link with a whole-node reference held, where the write stands for the queue's
relink through a raw projection:

```rust
use core::ptr::NonNull;
struct Job { id: u32, next: Option<NonNull<Job>> }
#[test]
fn whole_node_shared_ref_across_push_raw() {
    let a = Box::into_raw(Box::new(Job { id: 1, next: None }));
    let b = Box::into_raw(Box::new(Job { id: 2, next: None }));
    unsafe {
        let whole: &Job = &*a;
        (&raw mut (*a).next).write(Some(NonNull::new_unchecked(b)));
        fn look(j: &Job) -> u32 { j.id }
        assert_eq!(look(whole), 1);
        drop(Box::from_raw(a)); drop(Box::from_raw(b));
    }
}
```

The opaque link:

```rust
use core::cell::UnsafeCell;
use core::ptr::NonNull;
pub struct Link<T>(UnsafeCell<Option<NonNull<T>>>);
pub unsafe trait Node { unsafe fn link(this: NonNull<Self>) -> NonNull<Link<Self>> where Self: Sized; }
pub struct Queue<T: Node> { head: Option<NonNull<T>>, tail: Option<NonNull<T>> }
impl<T: Node> Queue<T> {
    unsafe fn set(n: NonNull<T>, v: Option<NonNull<T>>) { unsafe { *(*T::link(n).as_ptr()).0.get() = v } }
    unsafe fn get(n: NonNull<T>) -> Option<NonNull<T>> { unsafe { *(*T::link(n).as_ptr()).0.get() } }
    pub unsafe fn push_back(&mut self, n: NonNull<T>) {
        unsafe {
            Self::set(n, None);
            match self.tail { Some(t) => Self::set(t, Some(n)), None => self.head = Some(n) }
        }
        self.tail = Some(n);
    }
    pub unsafe fn pop_front(&mut self) -> Option<NonNull<T>> {
        let h = self.head?;
        self.head = unsafe { Self::get(h) };
        if self.head.is_none() { self.tail = None; }
        Some(h)
    }
}
pub struct Job { pub id: u32, pub link: Link<Job> }
unsafe impl Node for Job {
    unsafe fn link(this: NonNull<Self>) -> NonNull<Link<Self>> {
        unsafe { NonNull::new_unchecked(&raw mut (*this.as_ptr()).link) }
    }
}
#[test]
fn whole_node_shared_ref_across_push_cell() {
    let a = Box::into_raw(Box::new(Job { id: 1, link: Link(UnsafeCell::new(None)) }));
    let b = Box::into_raw(Box::new(Job { id: 2, link: Link(UnsafeCell::new(None)) }));
    let mut q = Queue { head: None, tail: None };
    unsafe {
        q.push_back(NonNull::new_unchecked(a));
        let whole: &Job = &*a;
        q.push_back(NonNull::new_unchecked(b));
        fn look(j: &Job) -> u32 { j.id }
        assert_eq!(look(whole), 1);
        while let Some(t) = q.pop_front() { drop(Box::from_raw(t.as_ptr())); }
    }
}
```

The bare `Option` projection tests use the queue above with `link` returning
`NonNull<Option<NonNull<Self>>>` and writing through it by `write` and `read`.

## The benchmark

On a Linux x86_64 host, rustc 1.100.0 (0ef1bc386 2026-11-09), `cargo build --release &&
./target/release/iq_bench`, run twice. The manifest pins `intrusive-collections = "=0.10.3"` and
`cordyceps = "=0.3.5"` and takes the crate by path at the commit above.

```rust
use core::hint::black_box;
use core::pin::Pin;
use core::ptr::NonNull;
use std::time::Instant;

const NODES: usize = 1024;
const ROUNDS: usize = 10_000_000;
const REMOVES: usize = 200_000;

// intrusive_queue
struct A { v: u64, next: Option<NonNull<A>> }
unsafe impl intrusive_queue::Node for A {
    fn next(&self) -> Option<NonNull<Self>> { self.next }
    fn set_next(&mut self, n: Option<NonNull<Self>>) { self.next = n; }
}
// intrusive-collections, LinkedList with UnsafeRef (doubly linked; its singly linked list has no push_back)
use intrusive_collections::{intrusive_adapter, LinkedList, LinkedListLink, UnsafeRef};
struct B { v: u64, link: LinkedListLink }
intrusive_adapter!(BAd = UnsafeRef<B>: B { link => LinkedListLink });
// cordyceps List
use cordyceps::{list::Links, Linked, List};
struct C { links: Links<C>, v: u64 }
unsafe impl Linked<Links<C>> for C {
    type Handle = NonNull<C>;
    fn into_ptr(h: NonNull<C>) -> NonNull<C> { h }
    unsafe fn from_ptr(p: NonNull<C>) -> NonNull<C> { p }
    unsafe fn links(p: NonNull<C>) -> NonNull<Links<C>> {
        unsafe { NonNull::new_unchecked(&raw mut (*p.as_ptr()).links) }
    }
}

fn best<F: FnMut() -> u64>(mut f: F) -> f64 {
    let mut b = f64::MAX;
    for _ in 0..5 { let t = Instant::now(); black_box(f()); b = b.min(t.elapsed().as_secs_f64()); }
    b
}

fn main() {
    let a: Vec<*mut A> = (0..NODES).map(|i| Box::into_raw(Box::new(A { v: i as u64, next: None }))).collect();
    let b: Vec<*mut B> = (0..NODES).map(|i| Box::into_raw(Box::new(B { v: i as u64, link: LinkedListLink::new() }))).collect();
    let c: Vec<*mut C> = (0..NODES).map(|i| Box::into_raw(Box::new(C { links: Links::new(), v: i as u64 }))).collect();

    // Round robin: pop the front, read it, push it to the back.
    let ta = best(|| unsafe {
        let mut q = intrusive_queue::Queue::new();
        for &p in &a { q.push_back(intrusive_queue::Unqueued::new(NonNull::new_unchecked(p))); }
        let mut s = 0;
        for _ in 0..ROUNDS { let t = q.pop_front().unwrap(); s += (*t.as_ptr()).v; q.push_back(t); }
        while q.pop_front().is_some() {}
        s
    });
    let tb = best(|| unsafe {
        let mut q = LinkedList::new(BAd::new());
        for &p in &b { q.push_back(UnsafeRef::from_raw(p)); }
        let mut s = 0;
        for _ in 0..ROUNDS { let t = q.pop_front().unwrap(); s += t.v; q.push_back(t); }
        q.clear();
        s
    });
    let tc = best(|| unsafe {
        let mut q: List<C> = List::new();
        for &p in &c { q.push_back(NonNull::new_unchecked(p)); }
        let mut s = 0;
        for _ in 0..ROUNDS { let t = q.pop_front().unwrap(); s += (*t.as_ptr()).v; q.push_back(t); }
        while q.pop_front().is_some() {}
        s
    });
    println!("round robin, {NODES} nodes, {ROUNDS} pop+push, best of 5:");
    for (n, t) in [("intrusive_queue", ta), ("intrusive-collections", tb), ("cordyceps", tc)] {
        println!("  {n:24} {:.2} ns per pop+push", t * 1e9 / ROUNDS as f64);
    }

    // Remove the middle node and push it back: O(n) walk against O(1) unlink.
    let mid = NODES / 2;
    let ra = best(|| unsafe {
        let mut q = intrusive_queue::Queue::new();
        for &p in &a { q.push_back(intrusive_queue::Unqueued::new(NonNull::new_unchecked(p))); }
        let mut s = 0;
        for _ in 0..REMOVES { let t = q.remove(NonNull::new_unchecked(a[mid])).unwrap(); s += (*t.as_ptr()).v; q.push_back(t); }
        while q.pop_front().is_some() {}
        s
    });
    let rb = best(|| unsafe {
        let mut q = LinkedList::new(BAd::new());
        for &p in &b { q.push_back(UnsafeRef::from_raw(p)); }
        let mut s = 0;
        for _ in 0..REMOVES { let t = q.cursor_mut_from_ptr(b[mid]).remove().unwrap(); s += t.v; q.push_back(t); }
        q.clear();
        s
    });
    let rc = best(|| unsafe {
        let mut q: List<C> = List::new();
        for &p in &c { q.push_back(NonNull::new_unchecked(p)); }
        let mut s = 0;
        for _ in 0..REMOVES { let t = q.remove(NonNull::new_unchecked(c[mid])).unwrap(); s += (*t.as_ptr()).v; q.push_back(t); }
        while q.pop_front().is_some() {}
        s
    });
    println!("remove a node from {NODES} and push it back, {REMOVES} times, best of 5 (after the first, the node sits at the back):");
    for (n, t) in [("intrusive_queue", ra), ("intrusive-collections", rb), ("cordyceps", rc)] {
        println!("  {n:24} {:.2} ns per remove+push", t * 1e9 / REMOVES as f64);
    }
    let _ = Pin::new(&0);
}
```

## Not run

- The crate's own Kani harnesses and falsification patches; milestone 1097 (what an outside maintainer would fix) ran them, and this
  review changes nothing.
