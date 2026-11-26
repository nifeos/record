# How the `domain_name_system` benchmark ran

An appendix to [the release review](../1136-domain-name-system-release-review.md), where the
figures are.

One machine ran everything: a Linux x86_64 host, an Intel Xeon Platinum 8160 at 2.10 GHz, with
rustc 1.100.0. The harness is a scratch crate in no repository. It uses `domain_name_system` at
`513558c` by path, `hickory-proto` `=0.26.4` with only its `std` feature, and `simple-dns`
`=0.13.1`.

```sh
cargo build --release
target/release/bench-dns <dns|hickory|simple|hickory_a|simple_a> <example|github>
```

The two replies are the crate's own fixtures, `tests/fixtures/example.com.dns` and
`tests/fixtures/www.github.com.dns`, read in with `include_bytes!`.

## The columns

| column | the timed call |
|---|---|
| `dns` | `Query::accept` on the reply, with the matching id and name, through to the `Answer` |
| `hickory` | `Message::from_vec`, which parses every section into owned records |
| `simple` | `Packet::parse`, which parses every section into borrowed records |
| `hickory_a`, `simple_a` | the parse, then a count of the answers that are A records |

None of the rival columns checks the id, the question or the chain, which `Query::accept` does.

## The loop

A pass repeats the call, starting at 64 repeats and doubling until a pass lasts at least 50 ms.
Seven passes at that count follow. The figure is the lowest of the seven, divided by the count.
`std::hint::black_box` wraps each reply and each result.
