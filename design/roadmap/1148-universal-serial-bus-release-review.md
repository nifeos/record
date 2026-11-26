---
status: PARTIAL
raised: 2026-11-26
milestone_dependencies: 1111, 1129
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1148. `universal_serial_bus`: the release review's findings

The release review of `partsfoundry/universal_serial_bus` at commit `4612f6b5`, version 0.1.0
(unpublished), under milestone 1129 (the combine review), whose
[block](1129-crate-interfaces-best-in-class.md) sets its form. The baseline is milestone 1111
(the outside review's findings), [its block](1111-usb-outside-review.md) and the cleared package
[`notes/crate-reviews/universal-serial-bus.md`](../../notes/crate-reviews/universal-serial-bus.md).
1111's three decisions stand and nothing here reopens them: every public name was ratified on
2026-11-19 with its specification alias, `changes` emits HID usages with the modifiers as 0xe0 to
0xe7, `DeviceDescriptor::parse` returns a `Result` while `BootReport::parse` keeps its `Option`,
and `Speed` has four variants. The one naming rule added since that ratification, the right and
permission rule, touches no name in this crate, so the release-review rule reopens none. The
usage-to-evdev table follows the standing rule for a keyboard table: it was written from the HID
Usage Tables and the evdev header, with Linux's `hid_keyboard[]` as a test cross-check only.

Reuse: the prior-art table weighs each host-side USB crate a caller could take instead, and the
device-side crates a caller may already know the vocabulary from.

## Finding status

- P0-1, `Refusal` and `Speed` are exhaustive: Open.
- P0-2, three public structs that will grow are exhaustive: Open.
- P0-3, `changes` reports through a callback of a bare `u8` and `bool`: Open.
- P1-1, `Refusal` has no `Display` and no `core::error::Error`: Waiting on the errors decision of
  milestone 1129.
- P1-2, no fallible function has an `# Errors` section: Open.
- P1-3, two items have an example, and neither uses `?`: Open.
- P1-4, the package ships the repository's machinery: Open.
- P2-1, a general descriptor iterator: Open.
- P2-2, the setup packet as bytes, and its parse: Open.
- P2-3, the fields `DeviceDescriptor` and `ConfigurationHeader` leave out: Open.
- P2-4, the manifest has no `documentation` key: Open.

## Open decisions

The one-way doors D1 to D5 below.

## Goal

A stranger writing a host controller driver with no operating system picks this crate for the
part of a keyboard driver that is about USB: it finds the keyboard's endpoint in bytes a device
sent, builds the four requests that bring it up, and turns two boot reports into key events,
without unsafe code, an allocator or a dependency. Its types can grow after 0.1.0 without breaking
that stranger's code, and its refusals print and compose with `?`.

## What the review read and ran

The sources, the commands and the systems outside Rust are in
[the appendix](1148-universal-serial-bus-release-review/what-was-checked.md), and the 54 API
Guidelines items in [the guidelines table](1148-universal-serial-bus-release-review/api-guidelines.md).

## Prior art

Measured from the crates.io API on 2026-11-26 (UTC). A stranger brings this crate the problem of
finding a boot keyboard behind a host controller and reading its keys. No crate on crates.io does
that alone: the host-side stacks bundle a controller driver, the user-space crates need an
operating system, and the busiest USB crates are for building a device. The review therefore also
reads OpenBSD and Linux, which do the same job in a kernel.

| crate or system | role | version read | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|
| `crab-usb` | ranked 1: a no_std host stack with xHCI, EHCI and DWC2 | 0.12.1 | 35,428 | 19,601 | 2 | 2026-09-11 |
| `usb-if` | `crab-usb`'s descriptor types | 0.8.0, measured | 33,202 | 21,184 | 2 | 2026-08-20 |
| `nusb` | ranked 2: user-space host access, the descriptor parser benchmarked | 0.2.9 | 2,420,609 | 1,142,486 | 182 | 2026-10-24 |
| `rusb` | measured, not read: libusb bindings | 0.9.4 | 10,538,976 | 2,063,423 | 170 | 2024-04-27 |
| `usbh` | ranked 3: a no_std host stack with a boot keyboard driver | 0.1.0 | 1,542 | 10 | 0 | 2023-08-06 |
| `usb-host` | a no_std host trait set with descriptor structs | 0.1.3 | 8,009 | 87 | 2 | 2022-10-12 |
| `usb` | measured, not read | 0.3.0 | 21,489 | 307 | 0 | 2025-03-02 |
| `usb-device` | neighbor: the device side's descriptor writer | 0.3.2 | 5,591,503 | 967,462 | 132 | 2024-03-06 |
| `usbd-hid` | neighbor: the device side's keyboard report | 0.10.2 | 1,619,958 | 301,549 | 20 | 2026-09-02 |
| `usbd-human-interface-device` | measured, not read: device-side HID | 0.6.1 | 47,402 | 3,047 | 2 | 2026-08-23 |
| `keycode` | neighbor: usage and scan code tables | 1.0.0 | 250,047 | 83,579 | 17 | 2025-03-19 |
| `hidreport` | measured, not read: a HID report descriptor parser | 0.6.0 | 76,240 | 42,456 | 6 | 2026-01-22 |
| `hut` | measured, not read: the HID Usage Tables as types | 0.6.0 | 70,457 | 37,296 | 6 | 2026-10-13 |
| OpenBSD `sys/dev/usb/ukbd.c`, `sys/dev/hid/hidkbd.c`, `sys/dev/usb/usb_subr.c` | outside Rust | revisions 1.91, 1.15, 1.169 | | | | |
| Linux `drivers/hid/usbhid/usbkbd.c`, `drivers/usb/core/config.c` | outside Rust | v6.18 | | | | |

### What `universal_serial_bus` does better

- Than `crab-usb`: it is the part a caller can take without the rest. `crab-usb` 0.12.1 needs
  `alloc` and takes 17 dependencies, with an eighteenth optional (among them `dma-api`, `tock-registers`, `xhci`, `futures`,
  `crossbeam` and `usb-if`); its descriptors arrive through its own async device type, and it has
  no HID keyboard layer. This crate has no dependencies, allocates nothing, forbids unsafe code and
  proves its walk and its report diff with five Kani harnesses.
- Than `nusb`: `nusb`'s `descriptors` module is the best descriptor reader read, with a general
  `DescriptorIter` and typed views, but it is a std crate whose module comes with the whole
  user-space stack. Its walk stops quietly (with a log line) at a descriptor whose length is below
  2 or past the buffer, where this crate answers `Refusal::Malformed { at }` naming the offset. On
  the same 94 bytes this crate's walk to the keyboard's endpoint took 41.6 ns and `nusb`'s
  took 75.5 ns (Measured performance).
- Than `usbh`: `usbh` 0.1.0's keyboard driver casts the report with `unsafe`, reports pressed keys
  with no release events and no phantom check, and parses descriptors with `nom`. It has not been
  updated since 2023.
- Than `usb-host`: `usb-host` 0.1.3 is a trait set with `repr(C)` descriptor structs and no walk;
  it has not been updated since 2022.
- Than `usbd-hid` and `keycode`: they build reports on the device side or map key names; neither
  reads a report from a device. Their `KeyboardReport` and `KeyMap` types are the vocabulary a
  caller may already know, and this crate's `BootReport` holds the same eight bytes.
- Than OpenBSD and Linux: it answers a bad descriptor length with a refusal naming its offset,
  where Linux's `usb_parse_configuration` logs one and skips the rest of the configuration and
  OpenBSD's `usbd_find_idesc` stops only at a length of 0; it drops a phantom report whole where Linux skips each slot holding 1 to 3; and it
  reports a key listed twice in one report once, where OpenBSD's `hidkbd_decode` adds it twice.

## The items

Effort is S (half a day), M (a day or two) or L (longer). One-way means a caller outside the
repository acts on it once 0.1.0 is out, so each P0 lands in 0.1.0 or not at all.

### P0: the 0.1.0 interface

#### P0-1. `Refusal` and `Speed` are exhaustive

Verified in source.
Neither enum has `#[non_exhaustive]`, and the README's BUGS list says so. A caller's `match` on
`Refusal` breaks when a parser learns a new refusal (a configuration with no interface, a device
descriptor that names zero configurations), and one on `Speed` breaks when the crate names
SuperSpeedPlus, which USB 3.2 already defines. Change: `#[non_exhaustive]` on both, and the BUGS
line goes. Door: one-way (D1). Effort: S.

#### P0-2. Three public structs that will grow are exhaustive

Verified in source.
`DeviceDescriptor` (six public fields), `ConfigurationHeader` (three) and `BootKeyboard` (five)
have every field public and no `#[non_exhaustive]`. Each leaves out fields of the descriptor it
reads (P2-3), so adding one later breaks every caller that builds or destructures it, and a caller
can build a `BootKeyboard` that no device described. `SetupPacket` and `BootReport` are different:
the specification fixes their eight bytes, every field is already present, and a caller's test
builds a `BootReport` to feed `changes`. Change: `#[non_exhaustive]` on the three, fields still
readable; leave `SetupPacket` and `BootReport` as they are. Door: one-way (D2). Effort: S.

#### P0-3. `changes` reports through a callback of a bare `u8` and `bool`

Verified in source (C-CUSTOM-TYPE, C-GENERIC).
`changes(before, after, event: &mut dyn FnMut(u8, bool))` calls back once per change, at most 20
times, in the order modifiers, releases, presses. The `bool` is press or release with nothing at
the call site to say which, and a caller who wants to stop early, count, or feed a queue must do it
inside a closure. 1111's decision 2 fixed what the events are (usages), not how they arrive. Every
comparator that reports keys hands back data: `usbh`'s `pressed_keys` is an iterator and
`take_event` returns a value, and `nusb`'s walk is an iterator. Change: `changes` returns an
iterator, a type holding the two reports and a cursor, of a `KeyChange` struct with `usage: u8` and
a two-variant `Press` and `Release` enum, both `#[non_exhaustive]`. A callback caller writes
`for_each`. The two Kani harnesses on events move to the iterator. The new type names need a
naming ruling. Door: one-way (D3). Effort: M.

### P1: before the first release

#### P1-1. `Refusal` has no `Display` and no `core::error::Error`

Verified in source (C-GOOD-ERR).
`Refusal` derives `Debug`, `Clone`, `Copy`, `PartialEq` and `Eq` only, so a caller cannot print it
or return it through a `Box<dyn Error>` or an `anyhow` chain. `crab-usb`'s `HostError` has both,
through `thiserror`. Change: a `Display` that names the offset or field each variant carries, and
`impl core::error::Error`, in the shape the errors decision of milestone 1129 picks. Adding them
later is additive. Door: two-way. Effort: S.

#### P1-2. No fallible function has an `# Errors` section

Verified in source (C-FAILURE).
`DeviceDescriptor::parse`, `ConfigurationHeader::parse` and `find_boot_keyboard` return `Result`,
and `BootReport::parse` and `control_maximum_packet_bytes` return `Option`. None has an `# Errors`
heading; the refusals are described in prose on some of them. Change: an `# Errors` section on
each, naming the variants it can return or when it answers `None`. Door: two-way. Effort: S.

#### P1-3. Two items have an example, and neither uses `?`

Verified in source (C-CRATE-DOC, C-EXAMPLE, C-QUESTION-MARK).
Only `find_boot_keyboard` and `changes` carry a doctest; the crate page has none, and the README's
example is not included as one, so it is not compiled. Nothing in `request` has an example. Both
doctests `unwrap`. Change: include the README as the crate page with `#![doc =
include_str!("../README.md")]`, give each public function an example, and use `?` in a function
returning `Result<(), Refusal>`. Door: two-way. Effort: S.

#### P1-4. The package ships the repository's machinery

Verified with `cargo package --list` (C-METADATA).
The manifest has no `include`, so the package carries `CODEOWNERS`, `_typos.toml`, `deny.toml`,
`rustfmt.toml`, `docs/stranger-test.md` and the five falsification patches beside the source.
Change: an `include` list of `src/`, the licenses, the README and the changelog. Door: two-way.
Effort: S.

### P2: may follow

#### P2-1. A general descriptor iterator

Verified in source (C-INTERMEDIATE).
`find_boot_keyboard` is the only walk, so a caller that wants a mouse, a hub or a second interface
writes its own, with the length checks this crate already proves. `nusb` 0.2.9's `DescriptorIter`
and its `interfaces()` and `endpoints()` views are the model. Change: a no_std `Descriptors`
iterator over a configuration that yields each descriptor's bytes or a `Refusal`, with
`find_boot_keyboard` rewritten above it and the walk's proofs moved to it. Door: two-way; it adds.
Effort: M.

#### P2-2. The setup packet as bytes, and its parse

Verified in source (C-CONV-TRAITS).
`SetupPacket::to_u64` packs the packet as the little-endian quadword an xHCI setup stage carries.
A DWC2 or EHCI driver writes eight bytes instead, and a test or a device-side reader wants to parse
them. `usb-host` and `usbh` both expose a typed request type. Change: `to_le_bytes() -> [u8; 8]`
and `from_le_bytes`, with `From` both ways. Door: two-way. Effort: S.

#### P2-3. The fields `DeviceDescriptor` and `ConfigurationHeader` leave out

Verified in source.
`DeviceDescriptor` has no subclass, protocol, device release or string indices, which a device
with class 0xef (interface association) or a log line needs; `ConfigurationHeader` has no
attributes or maximum power. `nusb` exposes all of them. Change: add them once P0-2 has made the
structs non-exhaustive. Door: two-way after P0-2. Effort: S.

#### P2-4. The manifest has no `documentation` key

Verified in `Cargo.toml` (C-METADATA).
Change: add it. Door: two-way. Effort: S.

### Measured performance

Run on a Linux x86_64 host, an Intel Xeon Platinum 8160 at 2.10 GHz, with rustc 1.100.0 in release
mode; the best of seven runs of ten million calls each. The bench and its exact bytes are in
[the appendix](1148-universal-serial-bus-release-review/what-was-checked.md).

| what | ns per call | what it includes |
|---|---|---|
| `find_boot_keyboard` | 41.6 | the header parse and the walk of 94 bytes, three interfaces, the keyboard last |
| `nusb` 0.2.9 walk | 75.5 | `ConfigurationDescriptor::new`, then `interface_alt_settings` and `endpoints` to the same endpoint |
| two `BootReport::parse` and `changes` | 40.4 | two parses with the phantom check, then seven events into a closure |
| a port of Linux `usb_kbd_irq`'s loop | 19.0 | the same seven events, no parse, no phantom check, no duplicate check |

The walk runs once per device, and a boot keyboard sends at most one report a millisecond at full
speed, so both costs are far below what a driver would notice. The interface does not limit speed
here; the numbers settle only that the refusals and the duplicate check cost tens of nanoseconds.

## One-way doors

- D1, exhaustive enums (P0-1). Recommended: `#[non_exhaustive]` on `Refusal` and `Speed` before
  0.1.0, the stricter choice; dropping the attribute later breaks no caller.
- D2, exhaustive structs (P0-2). Recommended: `#[non_exhaustive]` on `DeviceDescriptor`,
  `ConfigurationHeader` and `BootKeyboard`; keep `SetupPacket` and `BootReport` exhaustive, since
  their layouts are the specification's and cannot grow.
- D3, how `changes` delivers events (P0-3). Recommended: an iterator of a typed `KeyChange`, since a
  callback is one `for_each` away from it and the reverse needs a buffer.
- D4, one refusal type for the crate. `Refusal` is shared by the three descriptor parsers, so
  `DeviceDescriptor::parse` is typed as able to return `NoBootKeyboard`, which it never does.
  Splitting it into a type per parser later breaks every caller. Recommended: keep the one enum,
  which is what `nusb` and `crab-usb` do, and let the errors decision of milestone 1129 confirm the
  shape.
- D5, bare `u8` for the usage and the descriptor kind. `changes`, `evdev_code` and
  `SetupPacket::get_descriptor(kind, ...)` take a `u8` where a newtype would name it. Every one of the
  256 values is a valid usage id and a valid descriptor type (class descriptors such as 0x21 and
  0x22 among them), so a newtype would exclude no state, and OpenBSD, Linux, `usbd-hid` and
  `keycode` all index by the number. Recommended: keep `u8`; P0-3's `KeyChange` names the field.

## Evidence for the shared decisions

- **Errors.** One enum, `Refusal`, with six variants: `Truncated`, `NotThatDescriptor`,
  `Malformed { at: u16 }`, `NoBootKeyboard`, `NoInterruptIn { interface: u8 }` and
  `PacketTooSmall { maximum_packet_bytes: u16 }` (`src/descriptor.rs`). The fields are already
  named. It implements neither `Display` nor `core::error::Error` (P1-1) and is exhaustive (P0-1).
  `BootReport::parse` and `control_maximum_packet_bytes` answer `Option` by 1111's decision 3, since
  a short or phantom report has one cause. The census row counts one error type and zero `Error`
  impls.
- **Direct memory access regions.** Not applicable. The crate reads and writes only slices the
  caller passes (`&[u8]` in, values out); it hands no buffer to a device and holds no address.
- **Doorbells and tails.** Not applicable. There is no ring. The one place the crate meets a host
  controller's queue is `SetupPacket::to_u64` (`src/request.rs`), the quadword an xHCI setup stage
  carries; the caller's controller driver owns the ring and rings the doorbell.
- **Register access.** Not applicable. The crate touches no hardware (`src/lib.rs` documents it as
  pure computation) and defines no register trait.
- **Byte sinks.** Not applicable. Nothing streams bytes out; `changes` reports to a closure (P0-3),
  which is an event stream, not a byte stream.
- **Feature names and simulators.** Not applicable. The manifest declares no features and no
  dependencies, and the crate exports no simulator. Its tests build configuration bytes inline,
  and `fuzz/` has two targets, the configuration walk and the report diff.
- **Memory regions.** Not applicable. The crate allocates nothing and reserves no memory; its
  largest value is the eight-byte `BootReport`.

## Follow-on

- **Outstanding.** The errors decision of milestone 1129 takes P1-1 and D4. P0-3's two new type
  names go to a naming ruling before the change lands. No other shared decision applies.

## Done when

Every P0 and P1 finding reads Done, or Will not fix with its ruling, the architect has ruled D1
to D5, and `script/review-status` shows the block BUILT.

## BUGS

- Kani was not run; the harness count is from source.
- `rusb`, `usb`, `usb-if`, `usbd-human-interface-device`, `hidreport` and `hut` were measured and
  not read.
- The report-diff comparison is against a port of Linux's loop written for the bench, since no
  crate on crates.io diffs two boot reports.
- The OpenBSD files were read from the GitHub mirror's main branch, which carries no release tags;
  the revisions in the table are the files' own.

## Index row

The release review of `universal_serial_bus` against `crab-usb`, `nusb`, `usbh`, `usb-host`, the
device-side crates, OpenBSD and Linux: three one-way changes before 0.1.0 (non-exhaustive enums and
structs, and `changes` as an iterator of typed events), four smaller fixes before the release, and
five doors to rule.
