# What the review read and ran

An appendix to [the milestone](../1148-universal-serial-bus-release-review.md).

## The crate

`partsfoundry/universal_serial_bus` at `4612f6b5e5ef739fa1ad6f14b3ca182cca0d1fd5`, version 0.1.0,
`publish = false`. Read: `Cargo.toml`, `README.md`, `CHANGELOG.md`, `docs/stranger-test.md` and
every module under `src/` (`descriptor`, `request`, `boot_keyboard` and `verification`), and the
two fuzz targets by name.

## The commands

Run on a Linux x86_64 host, an Intel Xeon Platinum 8160, in an exported copy of the repository.

- `cargo test` passes: 31 unit tests and 2 doctests.
- `cargo build --lib --target x86_64-unknown-none` passes.
- `cargo +1.85 build` passes, the declared minimum Rust version.
- `RUSTDOCFLAGS="-D missing_docs" cargo doc --no-deps` passes.
- `cargo clippy --all-targets` prints no warning.
- `cargo package --list --allow-dirty` lists `CODEOWNERS`, `_typos.toml`, `deny.toml`,
  `rustfmt.toml`, `docs/stranger-test.md` and five `falsifications/*.patch` files beside `src/`
  (P1-4).
- `grep -c 'kani::proof' src/verification.rs` prints 5.
- `grep -n '# Errors' src/*.rs` prints nothing (P1-2).

## The benchmark

A scratch binary depending on this crate by path and on `nusb` =0.2.9, built with
`cargo run --release` under rustc 1.100.0. Each figure is the best of seven runs of ten million
calls, after a warm-up of one million, with inputs and outputs passed through
`std::hint::black_box`.

- The configuration, 94 bytes: the header (three interfaces) and interface 0 as mass storage with
  two bulk endpoints. Interface 1 is a vendor interface with a 5-byte class descriptor and
  alternate settings 0 and 1, one interrupt endpoint each. Interface 2 is a boot keyboard with its
  9-byte HID descriptor and endpoint 0x84, 8 bytes, interval 10. Both walks return interface 2,
  endpoint 0x84, 8 bytes, which the bench asserts before timing.
- The `nusb` walk: `ConfigurationDescriptor::new`, then `interface_alt_settings()` filtered to
  alternate setting 0 and the class triple (3, 1, 1), then `endpoints()` to the first interrupt
  `IN` endpoint of at least 8 bytes.
- The reports: modifiers 0x02 and keys 0x04, 0x05, 0x06, then modifiers 0x20 and keys 0x05, 0x07,
  0x08, 0x09; seven events, which both versions count before timing.
- The Linux port: the modifier loop and the six-slot loop of `usb_kbd_irq` in
  `drivers/hid/usbhid/usbkbd.c`, written over two byte arrays for timing only and not kept.

| what | ns per call |
|---|---|
| `find_boot_keyboard` | 41.6 |
| `nusb` 0.2.9 walk | 75.5 |
| two `BootReport::parse` and `changes` | 40.4 |
| the Linux loop, ported | 19.0 |

## The comparators read

Each `.crate` from crates.io at the version in the prior-art table, unpacked and read.

- `crab-usb` 0.12.1: a host stack with xHCI, EHCI and DWC2 back ends behind async device and
  interface types. It needs `alloc`, takes 17 dependencies with one more optional, gets its
  descriptor types from `usb-if`, and has no HID or keyboard layer. Its `HostError` implements
  `core::error::Error` through `thiserror`.
- `nusb` 0.2.9, `src/descriptors.rs`: `Descriptor`, `DescriptorIter`, and views
  `DeviceDescriptor`, `ConfigurationDescriptor`, `InterfaceDescriptor` and `EndpointDescriptor`
  over borrowed bytes, with every field of each descriptor as a method. `DescriptorIter` stops at
  a length below 2 or past the buffer, logging a warning. The module uses std.
- `usbh` 0.1.0: a no_std host stack over a `HostBus` trait, with a boot keyboard driver in
  `src/driver/kbd.rs`. It casts its `InputReport` from the slice with `unsafe`, `pressed_keys`
  iterates the nonzero slots, and nothing computes releases or checks for a phantom report. Its
  descriptor parser uses `nom`.
- `usb-host` 0.1.3: the `USBHost`, `Endpoint` and `Driver` traits, `repr(C)` descriptor structs
  and a typed `RequestType`; no configuration walk.
- `usb-device` 0.3.2: the device side's `DescriptorWriter`, which writes the descriptors this
  crate reads.
- `usbd-hid` 0.10.2: the device side's `KeyboardReport`, with `modifier`, `reserved`, `leds` and
  `keycodes: [u8; 6]`, the layout `BootReport` reads.
- `keycode` 1.0.0: `KeyMap` tables from usage ids to scan codes and a `KeyboardState` that builds
  reports.
- `rusb`, `usb`, `usb-if`, `usbd-human-interface-device`, `hidreport` and `hut`: measured, not
  read.

## The systems outside Rust

- OpenBSD, from the GitHub mirror at commit `c31f732c3135f73ec492f4793614fbe158ae4b4b`, whose
  files carry their own revisions: `sys/dev/usb/ukbd.c` 1.91, `sys/dev/hid/hidkbd.c` 1.15 and
  `sys/dev/usb/usb_subr.c` 1.169. `hidkbd_decode` ignores a report whose first slot is 0x01, then
  emits modifier changes, releases and presses in that order, the order `changes` follows; it adds a
  key twice when the new report lists it twice. `usbd_find_idesc` walks to `wTotalLength` and
  stops at a length of 0.
- Linux v6.18: `drivers/hid/usbhid/usbkbd.c`, whose `usb_kbd_irq` reports the eight modifiers,
  then for each slot a release and a press, skipping a slot that holds 0 to 3. Its probe takes an
  interface with exactly one interrupt `IN` endpoint. And `drivers/usb/core/config.c`,
  whose `usb_parse_configuration` logs a descriptor longer than what remains or shorter than 2 and
  skips the rest of the configuration.

OpenBSD's files are under BSD licenses and Linux's under the GPL; the review read them
for behavior only and copied no text.

## What was not run

- Kani: the harness count is from source.
- The fuzz targets.
- Any comparator's tests; the bench built `nusb` only as its dependency.
