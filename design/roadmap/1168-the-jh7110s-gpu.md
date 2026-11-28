---
status: NOT-STARTED
raised: 2026-11-28
milestone_dependencies: none
decision_dependencies: none
machine_requirements: JH7110 silicon
specific_machine: radon (the only JH7110 board this project has)
needs_person: yes
---
# 1168. The JH7110's GPU: the Imagination BXE-4-32, powered up and given one job

*(The number, the title and the slug are provisional.)*

Raised 2026-11-28 (UTC) by lane `lane/radon-unexercised-hardware`. Milestone 1166 (an eMMC module in
radon's socket) says why.

## What is unexercised

nife has never powered the JH7110's GPU. The display ladder's rung five (`design/display-ladder.md`)
struck a bare-metal driver for it as the board's display path. It called that a Linux-scale effort
that proves nothing rung four does not, and milestone 157 (real display output on the board:
U-Boot's `simple-framebuffer` handoff) took the display path instead. This block does not reopen
that ruling for display. It records the GPU as unexercised hardware and asks what the smallest proof
of life costs. Whether the block stays on the roadmap at all is a question for calef, since rung
five's reasons may cover a proof of life too.

## The hardware, from primary sources

- The StarFive JH7110 datasheet (v1.63, JH7110-DSEN-001), section 2.3.3: an IMG BXE-4-32 MC1, up
  to 600 MHz with 400 MHz by default. It supports OpenCL 3.0, OpenGL ES 3.2 and Vulkan 1.2. It has
  its own virtual memory addressing of up to 64 GB and a dedicated firmware processor with 2 KB
  instruction and data caches.
- StarFive's vendor tree (`starfive-tech/linux` `JH7110_VisionFive2_devel` at `6d6aee034b81`):
  `gpu: gpu@18000000`, compatible `img-gpu`, interrupt 82, power domain `JH7110_PD_GPUA`, six
  clocks and two resets.
- Mainline Linux (`torvalds/linux` `cbbddb6b08cc`) has no GPU node in `jh7110.dtsi`. Its binding
  `gpu/img,powervr-rogue.yaml` lists `img,img-bxe-2-32` and no BXE-4-32. So mainline's
  `drivers/gpu/drm/imagination` does not claim this part at that revision.
- Unverified: whether Imagination publishes firmware for the BXE-4-32 under a license nife could
  ship. The vendor stack loads a firmware image the tree does not name.

## What it needs

- The power domain, the clocks and the resets, through the clock and reset path nife already has
  for the JH7110, extended to the GPU's domain.
- The firmware image, and a reading of its license.
- DMA confinement. The JH7110 has no IOMMU. The GPU's own MMU translates its accesses, but the
  driver writes those page tables, so a driver that is wrong or hostile aims the GPU anywhere. The
  block states the result plainly: the GPU driver can reach all of physical memory.

## Done when

On radon, a driver powers the GPU, reads its core identity register, boots its firmware, and runs
one job (a buffer fill or a copy), whose output the CPU checks. The log goes under nife's
`bench/radon-<date>/`. A finding that nife may not ship the firmware also closes the block, as a
recorded refusal with its evidence.

## Prior art

- Linux mainline: the `imagination` DRM driver (`drivers/gpu/drm/imagination`) for other Rogue
  and B-series parts, with Mesa's PowerVR Vulkan driver in user space. It loads firmware and
  talks to it through shared memory.
- StarFive's vendor kernel: Imagination's out-of-tree driver behind `img-gpu`.
- No driver for this GPU appears in OpenBSD's or FreeBSD's JH7110 support (`sys/arch/riscv64/dev`
  and `sys/riscv/starfive`, read for this block).
- Where nife differs: nife has no 3D stack, and rung four proves its graphics contract on
  virtio-gpu. A GPU driver here would sit behind the same contract, at EL0, with its trust stated.

Reuse: the JH7110 clock and reset crates. A search of the roadmap for `BXE`, `GPU` and `PowerVR`
found milestone 34 (GPU acceleration via virtio-gpu 3D), milestone 157 and the display ladder, none
of which drives this part.

## Index row

The JH7110's Imagination BXE-4-32 GPU has never had power from nife. Rung five of the display ladder
refused it as the board's display path; this block asks only for one job run and checked, with the
firmware's license read and the driver's trust in memory stated.
