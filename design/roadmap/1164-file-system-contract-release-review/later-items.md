# P1 and P2: the later items

An appendix to [the milestone](../1164-file-system-contract-release-review.md), holding its P1 and P2
findings in full. Effort is S (half a day), M (a day or two) or L (longer).

## P1: before the first release

### P1-1. A walk ends at damage without saying so, and an edit then drops what follows

Verified by building. The four iterators stop at a record that runs off the buffer, and the
store's also stops at a kind past `MAXIMUM_KIND`. A caller cannot tell that stop from the end.
A store of three attributes with one damaged kind counts 1. `store::set` on it then returns a
blob of 9 bytes where 27 went in, and the third attribute is gone. `fuser` reports
`ShortRead` with both lengths, and `p9` returns `InvalidData`.
Change: each iterator says whether it consumed its buffer, and `set` and `remove` refuse a blob
their walk did not consume. Rule 6 of §329 (one error convention for the library crates)
asks a parser of a variable-length structure for the byte offset of each refusal.
Door: two-way to add; the refusal is a behavior a tag would bind. Effort: S.

### P1-2. Six examples for 66 public functions, and no `# Errors` section

Verified in source. Six items carry `# Examples`. No example walks a listing or edits an
attribute store. `store::set` and `store::remove` return `Result` and state their
errors in prose under no heading.
Change: an example for each encoding and the store, and `# Errors` on the two functions.
Door: two-way. Effort: S.

### P1-3. The documentation names one engine and one system's programs

Verified by building the documentation. Nine lines name RedoxFS, with `redoxfs::BLOCK_BYTES`,
its `Disk` trait, `TreePtr` and `DIR_ENTRY_MAX_LENGTH`. The text also names `START` words, an
initializer, a shell, `subtree_scope::Bindings::bind`, `bench/transfer-size-sweep.sh`, a clock
page and an `INTERFACES` note. It uses `r0`, `w1` and "caretaker" without defining them. A
stranger can find none of these. 9P's manual states a message's fields and nothing about the
server behind it.
Change: each engine fact becomes a plain statement of the contract. One section defines the
call, the reply word, the shared region and a caretaker.
Door: two-way. Effort: M.

### P1-4. The README counts fifteen harnesses and then eleven

Verified in source. "What is proven" says fifteen, and "Running the proofs" says all eleven
take about five seconds. The source has fifteen `#[kani::proof]` functions and fifteen patches.
Change: one count, and the time measured again.
Door: two-way. Effort: S.

### P1-5. The types miss common traits, and a rights set prints as a number

Verified by building. `Rights` has no `Hash`, and `{:?}` of the rights to remove a tree prints
`Rights(49)`. `Verb` has no `PartialEq`. `Operand` and `Policy` have no `Hash`. The four
iterator types derive nothing, so none is `Debug` or `Clone`. `fuser` derives `Hash` and `Ord`
on `INodeNo`, and a `bitflags` type prints its flags by name.
Change: the derives, a `Debug` for `Rights` that names its rights, and `FusedIterator` on the
four iterators.
Door: two-way. Effort: S.

### P1-6. `explain` gives the block server's refusal the attribute sentence

Verified by building. `block::FLUSH` answers 95 when the device cannot flush, and its text says
the code reaches a file client through `SYNC`. `directory::explain(95)` is "this capability
does not carry extended attributes". `explain(EPROTO)` and `explain(5)` are "the filesystem
refused".
Change: `explain` takes the verb, or the two meanings of 95 get two codes under §326.
Door: two-way. Effort: S.

## P2: may follow

The lane verified each in source, and P2-2 by building.

Each is two-way and S, except P2-1, which is M at each server.

- P2-1: `OPENDIR` resolves one name, so a path of five components costs five calls. 9P's `Twalk`
  carries up to sixteen names. A walk verb is an addition.
- P2-2: `grant::unpack_name` clamps a length past 16 to 16, and `specification_len` returns up to
  255 against a limit of 252. The crate's own rule is to refuse and never truncate.
- P2-3: a directory record is a flags byte, then a length byte. A name-set record is a length
  byte, then a flags byte. One sentence in each module says so.
- P2-4: `documentation` points at the repository, and `cargo` warns that `homepage` repeats
  `repository`.
- P2-5: `docs/stranger-test.md` reads "Last run: none", and `CHANGELOG.md` promises dates and
  carries none.
- P2-6: `grant::MAXIMUM_NAME_BYTES` is 252, one engine's entry limit, where POSIX allows 255.
  Raising it later is compatible, so nothing changes before the tag.
