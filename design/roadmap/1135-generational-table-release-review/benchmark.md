# How the `generational_table` benchmark ran

An appendix to [the release review](../1135-generational-table-release-review.md), which gives the
figures.

The host was a Linux x86_64 machine with an Intel Xeon Platinum 8160 at 2.10 GHz, building with
rustc 1.100.0. A scratch crate outside every repository took `generational_table` at `b524333` by
path, with `slotmap` `=1.1.1` and `thunderdome` `=0.6.1` from crates.io.

```sh
cargo build --release
target/release/bench-table <gt|sm|td> <cycle|get|worst|iter>
```

`gt` is `generational_table`, `sm` is `slotmap` and `td` is `thunderdome`. The table holds 4,096
slots of `u64`. `generational_table` sits in a `Box` so it stays off the stack. The other two
start from `with_capacity(4096)`, so no figure includes a reallocation.

## What each workload times

| workload | one timed operation |
|---|---|
| `cycle` | an insert into an empty table and the remove of what it returned |
| `get` | one lookup of a live name; the names cycle over all 4,096 |
| `worst` | half of: insert into slot 0, insert into slot 4,095, remove both; every other slot live |
| `iter` | the sum of the values of a table with every second entry removed |

## The loop

The repeat count starts at 1,024 and doubles until one pass lasts 50 ms or more. Seven passes then
run at that count. The figure kept is the smallest per-operation time of the seven. Inputs and
results go through `std::hint::black_box` so the compiler cannot drop the work.
