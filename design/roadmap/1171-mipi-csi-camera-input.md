---
status: NOT-STARTED
raised: 2026-11-28
milestone_dependencies: none
decision_dependencies: none
machine_requirements: a VisionFive 2 with a MIPI CSI camera module attached
specific_machine: radon (the only JH7110 board this project has)
needs_person: yes
---
# 1171. A MIPI CSI camera on radon: one raw frame into memory

*(The number, the title and the slug are provisional.)*

Raised 2026-11-28 (UTC) by lane `lane/radon-unexercised-hardware`. On that date calef asked for a
milestone for every part of the VisionFive 2 that nife has not yet exercised on the board, and
this is one of them.

## What is unexercised

radon's camera connector, the CSI-2 receiver behind it and the image signal processor. nife has no
camera driver of any kind.

## The hardware, from primary sources

- The VisionFive 2 datasheet (v1.53, VisionFive2-DSEN-001), section 5.3: one 2-lane MIPI CSI
  camera port, up to 1080p at 30 frames a second.
- The StarFive JH7110 datasheet (v1.63, JH7110-DSEN-001), sections 2.3.1 and 2.3.2: a CSI-2 v1.3
  receiver up to four lanes at 1.5 Gbps, raw formats from RAW6 to RAW20, a "direct memory dump", a
  receive D-PHY, and an ISP up to 1080p at 30.
- Mainline Linux `jh7110.dtsi` (`torvalds/linux` `cbbddb6b08cc`): `csi2rx: csi@19800000`,
  compatible `starfive,jh7110-csi2rx` and `cdns,csi2rx`; `csi_phy: phy@19820000`,
  `starfive,jh7110-dphy-rx`; their clocks from the ISP clock domain at `0x1981_0000`. Mainline's
  driver for the receiver is `drivers/media/platform/cadence/cdns-csi2rx.c`. At that revision
  mainline has no StarFive camera subsystem driver under `drivers/staging/media`.
- Mainline's VisionFive 2 tree also enables `i2c6` on GPIO 16 and GPIO 17. That it is the camera
  connector's control bus is an inference, unverified against the board schematic.

## What it needs

- A CSI-2 camera module with a documented sensor, which a person attaches with the board powered
  off. The block names none.
- The ISP clock and reset domain, which milestone 474 (a general JH7110 clock driver, covering all
  five domains) covers, and the ISP power domain.
- An I2C driver for the sensor's control bus, through the DesignWare I2C crate nife already runs
  on I2C5.
- DMA confinement. The receiver writes frames to memory by physical address and the JH7110 has no
  IOMMU, so the driver that sets the frame address can reach all of physical memory. The
  record states that plainly.

## Done when

On radon, with a camera attached, nife configures the sensor over I2C, brings up the receive
D-PHY and the CSI-2 receiver, and writes one raw frame to memory. The host converts the frame to
an image, and a person confirms it shows the scene in front of the lens. The log and the image go
under nife's `bench/radon-<date>/`. The ISP is not part of done: a raw frame proves the path.

## Prior art

- Linux mainline: `cdns-csi2rx.c` for the receiver, a sensor driver per module under
  `drivers/media/i2c`, and V4L2 to user space. StarFive's vendor kernel adds its VIN and ISP
  drivers behind `starfive,jh7110-vin`.
- Raspberry Pi's `libcamera` stack shows the split that suits nife: a small kernel driver that
  moves frames, and image processing in user space. That is a reading of its public design, not
  checked for this block.
- No driver for this path appears in OpenBSD's or FreeBSD's JH7110 support.
- Where nife differs: the receiver's driver runs at EL0 with a grant for its frame buffer, and
  the record states what the missing IOMMU leaves unconfined.

Reuse: the DesignWare I2C crate and the JH7110 clock and reset crates. A search of the roadmap for
`camera`, `CSI` and `ISP` found no block that drives this path.

## Index row

radon's MIPI CSI camera port has never carried a frame. nife brings up the sensor, the receive
D-PHY and the CSI-2 receiver, and writes one raw frame to memory that a person checks, with DMA
trust stated.
