---
status: NOT-STARTED
raised: 2026-11-28
milestone_dependencies: none
decision_dependencies: none
machine_requirements: JH7110 silicon
specific_machine: radon (the only JH7110 board this project has)
needs_person: yes
---
# 1169. The JH7110's video decoder, video encoder and JPEG codec

*(The number, the title and the slug are provisional.)*

Raised 2026-11-28 (UTC) by lane `lane/radon-unexercised-hardware`. Milestone 1166 (an eMMC module in
radon's socket) says why.

## What is unexercised

The JH7110 carries three media engines, and nife has driven none of them: a video decoder, a video
encoder and a JPEG codec.

## The hardware, from primary sources

- The StarFive JH7110 datasheet (v1.63, JH7110-DSEN-001), section 2.4:
  - the decoder: H.265 Main and Main10 and H.264 High and High10, up to 4096 x 2160 at 60 frames a
    second, one 4K channel at 30 or eight 1080p channels at 30, on a 128-bit AXI bus;
  - the encoder: H.265 at 1080p and 30 frames a second, I and P slices, with VBR, CBR and ABR rate
    control;
  - the JPEG codec: baseline and extended sequential ISO/IEC 10918-1, 8-bit or 12-bit samples, up
    to 32,768 x 32,768.
- StarFive's vendor tree (`starfive-tech/linux` `JH7110_VisionFive2_devel` at `6d6aee034b81`):
  - `vpu_dec@130A0000`, compatible `starfive,vdec`, interrupt 13, clocks named `WAVE511`;
  - `vpu_enc@130B0000`, compatible `starfive,venc`, interrupt 15, clocks named `WAVE420L`;
  - `jpu`, compatible `starfive,jpu`, registers at `0x1309_0000`, interrupt 14, clocks named
    `CODAJ12`.
  The clock names suggest Chips&Media's Wave511, Wave420L and CODA-J12; no StarFive document read
  here names the vendor. Every node is `dma-coherent` and `status = "disabled"`.
- Mainline Linux (`torvalds/linux` `cbbddb6b08cc`) has no node for any of the three. Its `wave5`
  driver (`drivers/media/platform/chips-media/wave5`) matches only `ti,j721s2-wave521c` at that
  revision.
- Unverified: whether the license on the firmware for these engines lets nife redistribute it. The
  vendor drivers load a firmware image.

## What it needs

- Power domains `JH7110_PD_VDEC` and `JH7110_PD_VENC`, with the clocks and resets each node lists.
- The firmware for each engine, and a reading of its license.
- DMA confinement. The JH7110 has no IOMMU, and each engine reads and writes frames in memory by
  physical address. A driver that hands an engine a buffer address can reach all of physical memory,
  unless the kernel checks every address the driver writes. The block chooses between those two and
  states the choice.

## Done when

On radon, the JPEG codec decodes one baseline JPEG file and the result matches a host decoder's
pixels exactly. The decoder then decodes a short H.264 stream, and each frame's checksum matches
a reference decoder's. The encoder's output then decodes back on the host. The log goes under
nife's `bench/radon-<date>/`. The JPEG codec comes first because it is the smallest of the three.

## Prior art

- Linux mainline: the `wave5` V4L2 stateful driver for the Wave5 family. It loads firmware, then
  queues bitstream and frame buffers through the V4L2 memory-to-memory interface.
- StarFive's vendor kernel: out-of-tree drivers for `starfive,vdec`, `starfive,venc` and
  `starfive,jpu`.
- No driver for these engines appears in OpenBSD's or FreeBSD's JH7110 support
  (`sys/arch/riscv64/dev` and `sys/riscv/starfive`, read for this block).
- Where nife differs: the driver would run at EL0 with a grant for its register page and its
  buffers, and the record states what the missing IOMMU leaves unconfined.

Reuse: the JH7110 clock and reset crates. A search of the roadmap for `codec`, `video`, `wave`,
`JPEG` and `H.264` found no block that drives these engines.

## Index row

The JH7110's Wave511 decoder, Wave420L encoder and CODA-J12 JPEG codec have never run under nife.
The JPEG codec decodes first, then H.264, each checked against a host decoder, with the firmware's
license read and DMA trust stated.
