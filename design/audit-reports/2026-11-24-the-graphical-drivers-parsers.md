# Security audit, 2026-11-24: the graphical drivers' parsers

**Kind:** security. **Lens:** every parser in the graphical stack that milestone 600 (the graphical
terminal stack is built in userspace) moved out of the kernel, read as the party on the other side
turned hostile: the terminal engine (`crates/video_terminal`) against the bytes a program writes,
`display_terminal` against the control page the compositor publishes, the compositor against its
input ring and its display driver, `gpu_driver` against the virtio-gpu device, and the two keyboard
drivers against their devices. For each, what it reads that another party wrote, and what it trusts
in it. **Findings:** fixed 6, minted 1, accepted 5.

The finding to carry off is the stride. In the compositor's wiring, `display_terminal` read its
window's width, height and stride off the compositor's control page and checked the width and
height against the grid, but not the stride. The stride sizes the surface mapping and every offset
`paint` writes at, so a control page with a large stride sent the terminal's writes past its surface,
and the `SAFETY` comment that claimed a 28 MB bound held for the other wiring only. The compositor
always publishes the packed width, so nothing has misbehaved, and the terminal now refuses any other
stride (finding 1).

The terminal engine came back close to clean. Its parameters saturate, its cursor clamps and it has
no path that answers a program, so nothing a program writes can be typed back to the shell. Its two
findings are a string that never ends (finding 2) and a record that said more than the decoder did
(finding 3).

## Why this lens

The 2026-11-17 security audit of radon's device authority named this lens as the README's remaining
candidate. Milestone 600 moved the terminal, the compositor and both display drivers into userspace
processes, and no audit since has read what those processes parse. Each one sits on a page or a ring
another process or a device writes, which is the place a confinement argument is only as good as the
reader's checks.

### The two uncountable triggers, answered

Has a new component taken device or network authority? **Not a component, but new device authority
has arrived.** The kernel now brings up radon's M.2 PCI Express root port before its PCI walk
(`kernel/src/drivers/jh7110_pci_express.rs`), so a device in that slot is reachable on radon for the
first time. That is kernel code and the device it exposes, not a userspace holder, and this report
does not read it. It is named below as the next lens.

Has this booted on a new machine class? **No.** The window's bench logs are radon's and xenon's, and
both booted before it.

## What was read, and what came back clean

Every file was read at nife `00f4046eb` (2026-11-24). The fixes land in nifeos/nife#4069. The two
external crates the USB driver uses were read at the revisions `components/Cargo.toml` pins:
`universal_serial_bus` at `0fbceff0ce95` and `extensible_host_controller_interface` at
`99daca365beb`.

**The terminal engine against a program's bytes.** `Vt::feed` is the whole input. `CSI` parameters
saturate, a seventeenth parameter makes the sequence ignored rather than truncated, and every cursor
motion clamps to the grid. Scrollback is a ring, and a test wraps it. Nothing in the engine writes to
the session's input side, so no sequence a program writes can make the terminal type on its behalf,
which is the echo-back class of terminal bug. `screen_console` was read and came back clean.

**The handoff.** `absorb_handoff`'s header checks (magic, layout and the grid's shape) came back
clean. One question about its two passes is listed under what was not examined.

**The drawing path.** `gpu_driver` refuses a flush rectangle outside the surface rather than
clamping it, and caps its rectangle fields at 14 bits before it multiplies them. Its reading of the
device's responses, `framebuffer_driver`, `glyph_atlas` and `bitmap_font` came back clean, and the
last two crates' tests pass (60).

**The USB keyboard's inputs.** Boot-report parsing, the descriptor walk in `universal_serial_bus`,
the scratchpad pages, the keymap and the UART input path (`components/src/input.rs`) came back clean.

## Findings

### 1. FIXED: a window's stride went unchecked

`negotiate_geometry` returned `MODE_WINDOW`'s stride from the control page as written, and `start`
mapped `stride * h` bytes at `SURFACE_VA` and painted at `y * stride + x * 4`. With a stride larger
than the window, the terminal's writes ran past its surface toward its other mappings. The compositor
publishes `Window::stride`, which is `w * 4`, so only a compositor bug or a hostile compositor could
send one. Severity medium: a fault in one process becomes stray writes in another's address space.
`start` now refuses a stride other than `w * gfx::BYTES_PER_PIXEL` with `E_GEOMETRY`, and its
`SAFETY` comment now says the bound holds in both wirings through that equality.

### 2. FIXED: a string that never ended hid the session

`ESC ]`, `ESC P`, `ESC X`, `ESC ^` and `ESC _` enter the string state, which ended only at BEL or
`ESC \`. A writer that opened one and stopped hid every byte after it, for the life of the session.
The DEC parser, which xterm follows, ends any sequence on CAN (`0x18`) or SUB (`0x1a`); this engine
handled neither. It now does, and a test holds it inside a string, after a string's `ESC` and inside
a `CSI`. Severity low: any writer could blank its own session, and none could reach another. What
remains is finding 8.

### 3. FIXED: overlong UTF-8 decoded, and the note said it did not

The decoder took any continuation byte after `0xe0` and `0xf0`, so `e0 80 9b` decoded to ESC and
`f0 80 80 80` to NUL. The decoder runs before the control-code match, so a decoded control
character was drawn with the fallback glyph and never acted on. notes/video-terminal.md said every
overlong form was refused. Severity low, records. The decoder now applies RFC 3629's narrower
second-byte ranges, and a test compares six inputs with `String::from_utf8_lossy`.

### 4. FIXED: a held modifier survived a replug

`usb_keyboard_driver` reset the last boot report at attach but not its `Keyboard`, so Shift or Control
held when one keyboard was unplugged stayed held for the next. Severity low. Attach now resets both.

### 5. FIXED: the compositor drained whatever the ring claimed

`drain_input` read `head` and `tail` off the input ring's page and made one `CALL` to the focused
client per byte between them. Both indices are on a page the input source writes, so the source
could ask for four billion calls in one frame. The ring holds 256 bytes, so anything older is already
overwritten; the drain now starts at most one ring's worth before `tail`. Severity low: the input
source is a driver the kernel starts.

### 6. FIXED: the GPU completion bound was described as a timeout

`gpu_driver::submit` waits at most 64 wake-ups for the used ring to move, and its comment said this
turned a device that never completes into a legible failure. A device that never raises its line
leaves the driver blocked in `interrupt_wait`, which has no timeout. The comment now says the bound
counts wake-ups and that the watchdog catches the silent case. Severity low, records.

### 7. MINTED: memory a peer writes is read through a reference

Three sites hold a Rust reference over memory a peer can write while it is alive: the USB driver's
descriptors, parsed from `control_buffer().as_slice()`; the compositor's `source(i)`, read while
clients other than the one that rang can write their surfaces; and `screen()`, whose comment rules
out aliasing because the process has one thread. `MappedWindow::as_slice`'s own contract forbids a
peer writer. The tearing is recorded in notes/compositor.md; the aliasing argument is not. Severity
low, with no misbehavior seen. Proposed as
[a driver copies memory a peer can write before it reads it](../roadmap/proposals/a-driver-copies-memory-a-peer-can-write-before-reading-it.md).

### 8. ACCEPTED: every writer to a session shares one parser

A writer that stops inside a sequence or a string hands that state to the next writer, which loses
its first bytes until a terminator, CAN or SUB. The engine cannot tell its writers apart, and a
program cannot reach past its own session this way. Recorded in notes/video-terminal.md.

### 9. ACCEPTED: one refused flush ends the compositor

`flush` dies on any non-zero reply from the display driver, so a driver that refuses or fails one
frame takes every window with it. Recorded in notes/compositor.md, beside the denial of service the
note already accepts from clients.

### 10. ACCEPTED: a device that lies about its rings can replay or drop keys

The virtio-input device can move the used index past what it completed, and the drain then replays
up to 65,535 posted event buffers in one wake-up. Every buffer below `EVENTS` is posted, so the
replay stays inside the page. A USB controller can report transfers the driver never queued, and
each one is dropped without queuing its report buffer again, so a few of them silence the keyboard.
Either device could stop the keyboard by staying silent. Recorded in `keyboard_driver` and
`usb_keyboard_driver`'s `BUGS`.

### 11. ACCEPTED: the input ring loses the oldest keys

In `MODE_RING`, `keyboard_driver` writes over bytes the compositor has not read once more than 256
are waiting, which happens only while the compositor is stalled on a client. Finding 5's drain now
agrees with the writer on which bytes are lost. Recorded in `keyboard_driver`'s `BUGS`.

### 12. ACCEPTED: rectangle arithmetic overflows on unclipped input

`Rect::intersect` and `Rect::union` in `crates/compositor` add a coordinate to a size, which
overflows for rectangles far off the screen. Every caller clips first, and release builds check
overflow, so an unclipped rectangle would halt the compositor rather than wrap. Recorded in
notes/compositor.md.

## Fatal-risk implications

Risk 7 (the confinement claim): none of these findings is a hole a program can reach. Finding 1 was
the nearest. It let a broken compositor write into a terminal's address space beyond the surface it
had granted, which is the kind of reach the claim says only the kernel decides. The kernel's grant
was never exceeded; the terminal's own code was the check, and it was missing.

## What was deliberately not examined

- Radon's PCI Express root port and the devices it exposes (the first trigger, above).
- Whether a rebuilt session reuses stale input-ring indices from the session before it. A reader
  suspected it and it was not settled.
- `absorb_handoff` reads the blob twice, once to check it and once to apply it. Whether an incumbent
  that changed the run between the passes could get an unchecked cell applied was not settled. Only a
  hostile incumbent, which has already handed over its screen, could try.
- The virtio-gpu device's own command handling and QEMU's implementation of it.
- The xHCI crate beyond the transfer and event paths the keyboard uses.
- Nothing ran on a board. Every finding was checked by reading code or by a host test.

## What wants a lane of its own

The proposal of finding 7. Then radon's PCI Express root port, read the way the 2026-11-17 audit read
radon's other device authority.
