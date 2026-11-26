# P2: may follow

An appendix to [the milestone](../1159-byte-sink-contract-release-review.md), holding its P2
findings in full. Effort is S (half a day) or M (a day or two).

## P2-1. No `embedded-io` writer

Verified in source. The crate has no type that implements a byte-writing trait, so a program
that takes `embedded_io::Write` cannot write to a sink without an adapter of its own.
`embedded-io` 0.7.1 has the kinds `BrokenPipe` and `Unsupported`, which are `Gone` and `NoSink`.
Its `Write` has no end of stream, so the adapter needs one method of its own for it.
Change: a writer type over a caller's send function, under a feature that the feature-name
decision names. An optional dependency is a ruling of its own (door D10).
Door: one-way if taken. Effort: M.

## P2-2. `pack` and `unpack` are not `const fn`

Verified by building at Rust 1.88, the crate's minimum. The seven functions that touch one word
are `const fn`, and the two that touch bytes are not. A scratch copy of `pack` with a `while`
loop in place of `copy_from_slice` builds as a `const fn` and binds a message in a `const`.
Change: make both `const fn`, so a fixed message such as a prompt costs nothing at run time.
Door: two-way. Effort: S.

## P2-3. No conversion between `MessageWords` and `[u64; 3]`

Verified in source. A caller that holds its registers as an array writes
`MessageWords::new(a[0], a[1], a[2])`.
Change: `From<[u64; 3]>` for `MessageWords` and the reverse.
Door: two-way. Effort: S.

## P2-4. The package ships the repository's CI files

Verified by building. `cargo package --list --allow-dirty` prints 44 files, 19 of them under
`.github/` and `.githooks/`. The manifest has no `include` and no `documentation` key. The
release workflow passes two secrets named for another project.
Change: an `include` that keeps the sources, the falsification patches, the README, the
changelog and both licenses; a `documentation` key; and the secrets under the organization's own
name.
Door: two-way. Effort: S.

## P2-5. Nothing says a message boundary may split a character

Verified in source. `KIND_TEXT` says the body is UTF-8 text. `pack` cuts at sixteen bytes, so a
character of two to four bytes may straddle two messages.
Change: one sentence at `KIND_TEXT`: a sink checks text across messages or not at all.
Door: two-way. Effort: S.

## P2-6. `unpack` writes through an out parameter

Verified by building. The API Guidelines item C-NO-OUT asks a function to return its result.
`unpack` fills a caller's `[u8; 16]` and returns the count, so a sink slices `out[..count]`
itself. A scratch decoder that returns `Bytes([u8; 16], usize)` takes 8.8 ns for a message where
`unpack` takes 5.3 ns.
Change: none to the signature. One sentence on the crate page gives the reason.
Door: two-way. Effort: S.
