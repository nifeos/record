---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1087, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1136. `domain_name_system`: the release review's findings

*(The number and the slug are provisional.)*

Raised by review lane A of [milestone 1129](1129-crate-interfaces-best-in-class.md). The lane read
`partsfoundry/domain_name_system` at `513558c`, the head of its `main`, as a stub-resolver author
weighing it against `hickory-proto` would. It changed no repository. The baseline is
[the outside review, 1087](1087-domain-name-system-outside-review.md) and
[the review package](../../notes/crate-reviews/domain-name-system.md). Two settled choices stay
closed: 1087's item 12 keeps `Reject` exhaustive, and the IPv4-only scope is the crate's own.
The ratified names already meet the IPv4 qualifier rule and every later one, so none reopens.

Reuse: the crate's tests and its three reply fixtures in `tests/fixtures/`, and a scratch benchmark
crate that [the benchmark appendix](1136-domain-name-system-release-review/benchmark.md) describes.
No new tool.

## Goal

A resolver author who reads the crate page finds addresses in the standard library's type, errors
that print and chain like any other, and a README whose example runs.

## Finding status

Each line reads against `partsfoundry/domain_name_system` at `513558c`.

- Item 1 (P0), addresses as `[u8; 4]`: Open.
- Item 2 (P1), errors that neither print nor chain: Open.
- Item 3 (P1), the README's example does not compile: Open.
- Item 4 (P1), the package ships the repository: Open.
- Item 5 (P1), two types without `Debug`: Open.
- Item 6 (P2), twenty-two public functions without an example: Open.
- Item 7 (P2), `Name` cannot be a hash key: Open.
- Item 8 (P2), crates.io metadata: Open.

## Prior art

Measured from the crates.io API on 2026-11-26 at 07:32 (UTC). The leading comparator is
`hickory-proto`.

| crate | role | version | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `hickory-proto` | leading | 0.26.4 | 111,984,337 | 38,124,907 | 175 | 2026-11-24 |
| `trust-dns-proto` | the same crate under its former name | 0.23.2 | 68,427,471 | 5,805,308 | 45 | 2023-10-23 |
| `simple-dns` | comparator | 0.13.1 | 13,765,116 | 4,334,418 | 38 | 2026-11-16 |
| `domain` | comparator | 0.13.0 | 13,823,798 | 2,328,675 | 45 | 2026-11-24 |
| `dns-parser` | comparator | 0.8.0 | 5,439,268 | 513,530 | 32 | 2018-08-06 |
| `dns-protocol` | comparator | 0.1.2 | 30,915 | 2,779 | 3 | 2024-06-12 |
| `smoltcp` | integration target | 0.14.0 | 11,087,347 | 3,453,932 | 133 | 2026-08-17 |

The lane read `hickory-proto`, `simple-dns`, `domain` and `smoltcp` at these versions. It measured
`dns-parser` and `dns-protocol` and did not read them.

| axis | `domain_name_system` | `hickory-proto` 0.26.4 | `simple-dns` 0.13.1 |
|---|---|---|---|
| allocation | none | `alloc` | `alloc` |
| scope | one name's A records, and the checks | every record type, encode and decode | most record types, encode and decode |
| an A record's address | `[u8; 4]` | `A(pub Ipv4Addr)` | `A { address: u32 }` |
| reply policy | `Query::accept`: id, question, chain, owner | the caller's | the caller's |
| error trait | none | `thiserror`, `#[non_exhaustive]` | `impl Error for SimpleDnsError` |
| name hash | none, on purpose | folds case, like its equality | hashes its labels |
| TCP framing | `request_tcp`, `TcpReply` | none found in its `src/` | none |

`smoltcp` 0.14.0 carries its own `wire/dns.rs` and names `core::net::Ipv4Addr` as its address type
in `wire/ipv4.rs`. A caller that pairs the two crates meets that type at the boundary.

## What the crate does better

- Against `hickory-proto` and `simple-dns`: no allocation, so it runs where neither can. Both build
  a `Vec` of records per message.
- Against both: the acceptance policy is one call. `Query::accept` checks the id, the question, the
  canonical name chain and the owner of each address. A caller of either rival writes those checks
  itself, and a reply about one name could otherwise plant an address for another.
- Against both: that whole call took about the time `hickory-proto` takes only to parse the same
  reply (see *Benchmarks*).
- Against all of them: Kani proofs of the name decoder, the header codec and the TCP reassembly, each
  with the patch that breaks it.

## Findings

Every finding gives its evidence and its change, and says whether the lane verified it in the
source or inferred it. It names the door, and an effort size: XS under an hour, S a few hours, M a
day or two.

### P0

#### Item 1: Addresses as `[u8; 4]`

`Answer::ipv4_addresses` returns `&[[u8; 4]]`. The standard library's `core::net::Ipv4Addr` has
been stable since Rust 1.77, below the crate's `rust-version` of 1.88. `hickory-proto` 0.26.4's
`A(pub Ipv4Addr)` and `smoltcp` 0.14.0's address type are both that type. A caller converts each
address by hand before it can connect to it or compare it with one from either crate.

Change: return `&[Ipv4Addr]`, storing `Ipv4Addr` in `Answer`. Both are four bytes, and
`Ipv4Addr::octets` gives the array back. Verified in the source of all three crates. One-way: see
door 1 below. Effort XS.

### P1

#### Item 2: Errors that neither print nor chain

`Error` and `Reject` implement `Debug` and no `Display` or `core::error::Error`. The latter has been
in `core` since Rust 1.81. A caller cannot use `?` into a boxed error, cannot print a refusal for a
log, and loses the inner `Error` that `Reject::Malformed` carries. `hickory-proto` derives `Error`
on `DecodeError`, and `simple-dns` implements it on `SimpleDnsError`.

Change: `Display` on both, `core::error::Error` on both, and `source` on `Reject::Malformed`
returning its `Error`. Verified. Additive, two-way. Effort S. It follows milestone 1129's shared
error decision for its wording.

#### Item 3: The README's example does not compile

The README ends its example with `assert_eq!(answer.ttl(), 300)`, but the method is `ttl_seconds`.
No test catches it, because the crate does not include the README as a doctest. The crate page has
no code example of its own, so docs.rs shows none. The example also calls `unwrap` where the
guidelines ask for `?`.

Change: the README included as a doctest, `ttl_seconds` in the example, and `?` in a function that
returns a `Result`. Verified by reading `src/lib.rs` and the README. Two-way. Effort XS.

#### Item 4: The package ships the repository

`Cargo.toml` has no `include` list. `cargo package --list` names the `.github/` workflows and issue
templates, `.githooks/`, `.cargo/mutants.toml`, `docs/`, `deny.toml`, `_typos.toml` and
`rustfmt.toml` beside the source. `generational_table` and `byte_glob` already carry an `include`
list.

Change: `include` the source, the proofs' patches if the proofs should build from the
package, the README, the changelog and the licenses. Verified by running the command. Two-way.
Effort XS.

#### Item 5: Two types without `Debug`

`Reader` derives only `Clone`, and `TcpReply` derives nothing. A caller whose own state holds a
`TcpReply` cannot derive `Debug`. Change: `Debug` on both, printing positions rather than the bytes.
Verified. Additive, two-way. Effort XS.

### P2

#### Item 6: Twenty-two public functions without an example

Among them are `decode_name`, `Header::parse`, `Header::write`, `Reader::record`, `Query::request`,
`Query::request_tcp` and `TcpReply::feed`. The rivals are no better: `hickory-proto`'s
`op/message.rs` has two examples over its thirty-three public functions, and `simple-dns`'s
`packet.rs` has none over nineteen.

Change: examples on the functions a caller starts from: `Query::new`, `request`, `request_tcp`,
`accept`, `TcpReply::feed` and `decode_name`. Verified by reading each item. Two-way. Effort S.

#### Item 7: `Name` cannot be a hash key

`Name` compares without regard to ASCII case and documents why it has no `Hash`. `hickory-proto`
0.26.4 shows the way: its `Hash for Name` lowercases each byte as it feeds the hasher, so equal names
hash equally. Change: the same folding `Hash` on `Name`, which makes it a key for a cache. Verified;
the lane infers the need from the comparator. Additive, two-way. Effort XS.

#### Item 8: crates.io metadata

`Cargo.toml` has no `documentation` field. The categories already include `no-std::no-alloc`.
Change: add the field. Verified. Two-way. Effort XS.

## One-way doors

1. The address type (item 1). Recommended: `core::net::Ipv4Addr`. The rival keeps `[u8; 4]`, which
   needs no type but makes every caller convert, and only the first publish can change it for free.
2. `Reject` stays exhaustive, as 1087's item 12 settled, so that a new refusal breaks the build of
   the contract that numbers each one. Recommended: keep it. Item 2 adds traits, not variants, and so
   leaves it as it is.
3. Public fields on `Header`, `Question` and `Record`. A field added later breaks every caller that
   builds one with a struct literal. RFC 1035 fixes all three layouts, and EDNS(0) lives in a record,
   not in the header. Recommended: keep the fields public.

`Header::flags` is a raw `u16` with `FLAG_` constants rather than a flag type. The crate takes no
dependency, and the constants carry names, so the review raises no finding there.

## Benchmarks

A Linux x86_64 host (an Intel Xeon Platinum 8160 at 2.10 GHz), rustc 1.100.0, release profile, over
two of the crate's own reply fixtures. Times are per reply.

| reply | `Query::accept` | `hickory-proto` parse | the same, then count A | `simple-dns` parse | the same, then count A |
|---|---|---|---|---|---|
| `example.com` | 333.6 ns | 398.1 ns | 414.0 ns | 315.9 ns | 505.2 ns |
| `www.github.com` | 412.1 ns | 470.6 ns | 663.5 ns | 366.6 ns | 487.4 ns |

`Query::accept` does more than the rivals' parse: it validates and follows the chain as well. The
count columns ran in a later invocation, so they are not exactly comparable with the parse columns
beside them. [The benchmark appendix](1136-domain-name-system-release-review/benchmark.md) gives the
command and what each column includes.

## The checklist

[The checklist appendix](1136-domain-name-system-release-review/checklist.md) marks all 54 items.
Seven are not met: C-COMMON-TRAITS (items 5 and 7), C-GOOD-ERR (item 2), C-CRATE-DOC and
C-QUESTION-MARK (item 3), C-EXAMPLE (item 6), C-METADATA (item 8) and C-DEBUG (item 5).

## Done when

- Item 1 lands, or the architect rules door 1 another way, before the 0.1.0 interface freezes.
- Items 2 to 5 land before the first release.
- Items 6 to 8 land, or each carries a ruling against it.

## BUGS

- The lane neither read nor benchmarked `dns-parser` or `dns-protocol`.
- The benchmark covers two replies, both small and well formed.

## Follow-on

- **Outstanding.** Items 1 to 8, open on the crate's `main` at `513558c`.
- **Outstanding.** The three one-way doors, for the architect.

## Index row

The release review of `domain_name_system` against `hickory-proto` and `simple-dns`. One item blocks
the 0.1.0 interface: addresses should be `core::net::Ipv4Addr`. Four land before the release:
printable errors, a README that compiles, an `include` list and `Debug` on two types. Three may
follow. Three one-way doors are for the architect.
