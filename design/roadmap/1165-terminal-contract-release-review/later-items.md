# P1 and P2: the later items

An appendix to [the milestone](../1165-terminal-contract-release-review.md), holding its P1 and P2
findings in full. Effort is S (half a day), M (a day or two) or L (longer).

## P1: before the first release

### P1-1. A refusal has no error type

Verified in source. `decode` returns `None` with no cause, and a refusal on the wire is a `u64`
a caller compares by hand. Nothing implements `core::error::Error` or `Display`. `termios`
returns `std::io::Result`, and `rustix` returns its own `io::Result`.
Change: what the errors decision picks, over the range of P0-3.
Door: two-way after P0-3. Effort: S.

### P1-2. The documentation speaks one kernel's vocabulary and never names it

Verified by building the documentation. The text uses `r0`, `r1`, `CALL`, `SEND`,
`SEND_CAPABILITY`, a rendezvous, a reply capability, a slot and an `INTERFACES` note. No page
defines one of them or names the system they come from. Fuchsia's file opens by saying what a
pty is and who holds each side.
Change: a section on the crate page that states what the contract needs from a transport: a
call of two words answered by two words, a badge per copy of an endpoint, and two shared pages.
Door: two-way. Effort: S.

### P1-3. The crate page promises limits, and the crate states none

Verified in source. The crate page lists limits among what the crate shares. No constant gives
the size of the output page, the input page or the longest line. `decode` returns any length up
to 4,294,967,295, and each terminal bounds it against a page size the crate does not carry.
`redox_termios` publishes `NCCS`, the length of its one array.
Change: the page size and the largest length as constants, names provisional, or one sentence
that the transport fixes them.
Door: two-way to add. Effort: S.

### P1-4. One example for six functions, and none on the crate page

Verified in source. `decode` carries the one example. `admits`, `req` and `is_retry` have none,
and no example reads a reply. The crate page of `termios` carries three examples under its
first heading.
Change: the README's example on the crate page, and one that reads a retry and a refusal.
Door: two-way. Effort: S.

### P1-5. No `#![forbid(unsafe_code)]`

Verified in source. The README says the crate has no `unsafe`, and the crate root does not
forbid it. The package records the gap.
Change: the attribute.
Door: two-way. Effort: S.

### P1-6. Four operations carry bytes in a word, and no function packs them

Verified in source. `OPERATION_BYTES`, `OPERATION_PRINT`, `OPERATION_READRAW` and
`OPERATION_READ_LINE_BYTES` carry up to eight bytes in a word, little-endian, with the count
apart. Each sender and each reader writes the packing by hand, and a count of 9 reaches
whichever reader forgot the bound.
Change: `pack_bytes` and `unpack_bytes` (provisional), the second refusing a count past 8.
Door: two-way to add. Effort: S.

### P1-7. A swap ends the input of a standard-input reader

Inferred from the documentation; the terminal that serves the words is not in this crate. A
parked `OPERATION_READLINE` or `OPERATION_READRAW` gets `FLAG_RETRY` at a quiesce. A parked
`OPERATION_READ_LINE_BYTES` gets a count of 0, which is also the answer for `^D`. A program
reading its standard input sees the end of its input when the terminal is replaced.
Change: the third read shape answers a retry too, which `is_retry` already reads.
Door: two-way; a 0.1.0 client still reads the count of 0. Effort: S here, M at the terminal.

## P2: may follow

The lane verified each in source, except P2-3, an inference from the documentation.

Each is two-way and S, except P2-1 and P2-2, which are M at the terminal.

- P2-1: no operation reports the terminal's size, and raw mode names a full-screen editor as its
  client. `redox_termios` and `rustix` publish `Winsize`, and Fuchsia has `GetWindowSize` and
  `EVENT_WINDOW_SIZE`.
- P2-2: a client learns of `^C` and `^Z` by polling two counts, as the README's BUGS section
  says. Fuchsia pairs `ReadEvents` with an event the client waits on.
- P2-3: raw mode stays on when the client that set it exits. Plan 9 ends raw mode when the
  holder closes `consctl`.
- P2-4: a `documentation` key, and an `include` that drops the 20 CI files of the 41 packaged.
- P2-5: `Debug` and `Display` for an operation by name, after P0-1.
- P2-6: `docs/stranger-test.md` reads "Last run: none", and `CHANGELOG.md` promises dates and
  carries none.
