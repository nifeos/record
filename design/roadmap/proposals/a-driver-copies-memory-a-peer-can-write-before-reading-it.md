---
status: PROPOSED
raised: 2026-11-24
milestone_dependencies: 139
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: no
---
# A driver copies memory a peer can write before it reads it

Raised 2026-11-24 (UTC) by lane `lane/audit-2026-11`, as finding 7 of the security audit
[the graphical drivers' parsers](../../audit-reports/2026-11-24-the-graphical-drivers-parsers.md).
Name: provisional.

Reuse: `MappedWindow::read_volatile` and `MappedWindow::copy_within` in `user_mode_runtime`, which
milestone 139 (drive the unsafe count down) built for exactly this.

## The problem

`MappedWindow::as_slice` states its contract: nothing else, no peer process included, reads or
writes the range while the slice is alive. Three sites in the graphical stack hold a Rust reference
over memory that a peer can write while the reference is alive. Their `SAFETY` comments argue
against a well-behaved peer, not a hostile one.

- `components/src/usb_keyboard_driver.rs` parses the device, configuration and boot-interface
  descriptors from `control_buffer().as_slice()`. The comment says nothing writes the buffer until
  the next transfer. A compliant controller does not; a hostile or broken one can, since the buffer
  sits in its DMA domain.
- `components/src/compositor.rs`'s `source(i)` is a `&'static [u32]` over client `i`'s surface. Only
the client that rang waits in `CALL` during a frame, and every other client can be writing
  its surface while the compositor reads it. notes/compositor.md records the tearing this causes,
  not that the reference itself breaks the aliasing rule the compiler relies on.
- `screen()` is a `&'static mut [u32]` over the scanout, which the GPU driver and the device read.
  Its comment says there is no aliasing question because the process has one thread, which leaves
  out the peer.

Nothing misbehaves that a test has seen. The compiler may assume a shared reference's bytes do not
change. A hostile writer then turns a tear into a parse that reads different bytes on two loads of
the same field, a bug no bounds check can see.

## The work

- The USB driver copies each descriptor out of the control buffer with volatile reads into a local
  buffer before it parses, and parses the copy.
- The compositor reads client surfaces and writes the scanout through `MappedWindow` volatile
  accessors or a bounded copy, and holds no reference over either. A lane measures the frame's cost
  before and after on the QEMU suite, since composition is a copy and this changes how it copies.
- Each `SAFETY` comment that remains says what a hostile peer can do, not only what a correct one
  does.

## Done when

No reference into a mapping a peer can write is alive in `usb_keyboard_driver` or `compositor`, and
the compositor's isolation tests still pass.

## Index row

A driver copies memory a peer can write before it reads it.
