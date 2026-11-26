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

`cargo +nightly miri run`, Miri 0.1.0 (f9ceb4a4d4 2026-10-31), on two small programs. The first
runs against the crate at the commit above; the second carries its own queue whose trait projects
to the link by raw pointer, in the shape of `cordyceps`'s `Linked::links`. Each holds a shared
reference to a node's `id` field across a `push_back` that relinks that node.

| program | Stacked Borrows (the default) | Tree Borrows (`MIRIFLAGS=-Zmiri-tree-borrows`) |
|---|---|---|
| the crate's `Node` | undefined behavior: the reference is invalidated by the unique retag at `set_next` | passes |
| the projection shape | passes | passes |

The first program:

```rust
use core::ptr::NonNull;
use intrusive_queue::{Node, Queue, Unqueued};
struct Job { id: u32, next: Option<NonNull<Job>> }
unsafe impl Node for Job {
    fn next(&self) -> Option<NonNull<Self>> { self.next }
    fn set_next(&mut self, n: Option<NonNull<Self>>) { self.next = n; }
}
fn main() {
    let a = Box::into_raw(Box::new(Job { id: 1, next: None }));
    let b = Box::into_raw(Box::new(Job { id: 2, next: None }));
    let mut q = Queue::new();
    unsafe {
        q.push_back(Unqueued::new(NonNull::new_unchecked(a)));
        // A shared reference to a field of a queued node, held across a push that relinks it.
        let id: &u32 = &(*a).id;
        q.push_back(Unqueued::new(NonNull::new_unchecked(b)));
        println!("{}", *id);
        while let Some(t) = q.pop_front() { drop(Box::from_raw(t.as_ptr())); }
    }
}
```

The second:

```rust
// The same sequence against a queue whose trait projects to the link by raw pointer, in the shape of
// cordyceps 0.3.5 `Linked::links`, so the queue never forms a reference to the whole node.
use core::ptr::NonNull;
unsafe trait Node { unsafe fn link(this: NonNull<Self>) -> NonNull<Option<NonNull<Self>>>; }
struct Queue<T: Node> { head: Option<NonNull<T>>, tail: Option<NonNull<T>> }
impl<T: Node> Queue<T> {
    unsafe fn push_back(&mut self, n: NonNull<T>) {
        unsafe {
            T::link(n).as_ptr().write(None);
            match self.tail { Some(t) => T::link(t).as_ptr().write(Some(n)), None => self.head = Some(n) }
        }
        self.tail = Some(n);
    }
    unsafe fn pop_front(&mut self) -> Option<NonNull<T>> {
        let h = self.head?;
        self.head = unsafe { T::link(h).as_ptr().read() };
        if self.head.is_none() { self.tail = None; }
        Some(h)
    }
}
struct Job { id: u32, next: Option<NonNull<Job>> }
unsafe impl Node for Job {
    unsafe fn link(this: NonNull<Self>) -> NonNull<Option<NonNull<Self>>> {
        unsafe { NonNull::new_unchecked(&raw mut (*this.as_ptr()).next) }
    }
}
fn main() {
    let a = Box::into_raw(Box::new(Job { id: 1, next: None }));
    let b = Box::into_raw(Box::new(Job { id: 2, next: None }));
    let mut q = Queue { head: None, tail: None };
    unsafe {
        q.push_back(NonNull::new_unchecked(a));
        let id: &u32 = &(*a).id;
        q.push_back(NonNull::new_unchecked(b));
        println!("{}", *id);
        while let Some(t) = q.pop_front() { drop(Box::from_raw(t.as_ptr())); }
    }
}
```

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

- The crate's own Kani harnesses and falsification patches; milestone 1097 ran them, and this
  review changes nothing.
