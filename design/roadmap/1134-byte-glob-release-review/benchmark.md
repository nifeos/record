# How the `byte_glob` benchmark ran

An appendix to [the release review](../1134-byte-glob-release-review.md), which holds the results.

## The machine and the command

A Linux x86_64 host with an Intel Xeon Platinum 8160 at 2.10 GHz and rustc 1.100.0. The harness is
a scratch binary crate outside every repository. It depends on `byte_glob` at `a095cd8` by path, and
on `glob` `=0.3.4`, `globset` `=0.4.22` without default features, and `wildmatch` `=2.7.0`.

```sh
cargo build --release
target/release/bench-glob <matcher> <shape> [name length]
```

The matcher is `byte_glob`, `glob`, `glob-compile`, `globset`, `globset-compile` or `wildmatch`. The
shape is `txt`, `class`, `tail`, `stars` or `brackets`, and the name length defaults to 4,096.

## What each number includes

- `byte_glob`: one call to `matches_with` under `LeadingDot::Ordinary`, so the timed call decodes
  the pattern, as every call does.
- `glob`, `globset`, `wildmatch`: one call to the compiled matcher. The compile happens once, before
  timing, and is not counted.
- `glob-compile`, `globset-compile`: the compile and one match, both inside the timed call.
- The harness built `globset` with `backslash_escape(true)`, so `\` means what it means to `byte_glob`.

## The timing loop

Each figure is the fastest of seven runs. A run repeats the call, doubling the count until one run
takes at least 50 ms, and divides by the count. Each input passes through `std::hint::black_box`.

```rust
fn time<F: FnMut() -> bool>(mut f: F) -> (f64, bool) {
    let mut iters = 1u64;
    let r = f();
    loop {
        let s = Instant::now();
        for _ in 0..iters { black_box(f()); }
        if s.elapsed().as_millis() >= 50 || iters >= 1 << 30 { break; }
        iters *= 2;
    }
    let mut best = f64::INFINITY;
    for _ in 0..7 {
        let s = Instant::now();
        for _ in 0..iters { black_box(f()); }
        best = best.min(s.elapsed().as_nanos() as f64 / iters as f64);
    }
    (best, r)
}
```

## The shapes

| shape | pattern | name |
|---|---|---|
| `txt` | `*.txt` | `notes.txt` |
| `class` | `[a-z]*[0-9].log` | `server-access-2026-11-26.7.log`, 30 bytes |
| `tail` | `*`, 63 `?`, `b` | n bytes of `a` |
| `stars` | `a*` ten times, then `b` | n bytes of `a` |
| `brackets` | n bytes of `[` | the same n bytes |

`glob` and `globset` refuse the `brackets` pattern as malformed, so they have no time for it.
`wildmatch` returns no match on `class`, because it reads `[` as an ordinary character.
