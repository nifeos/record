---
status: NOT-STARTED
raised: 2026-11-28
milestone_dependencies: 157
decision_dependencies: none
machine_requirements: a VisionFive 2 with a MIPI DSI panel attached
specific_machine: radon (the only JH7110 board this project has)
needs_person: yes
---
# 1170. A MIPI DSI panel on radon: the display controller and the DSI transmitter

*(The number, the title and the slug are provisional.)*

Raised 2026-11-28 (UTC) by lane `lane/radon-unexercised-hardware`. On that date calef asked for a
milestone for every part of the VisionFive 2 that nife has not yet exercised on the board, and
this is one of them.

## What is unexercised

nife has never put a pixel on any display attached to radon. Milestone 157 (real display output on
the board: U-Boot's `simple-framebuffer` handoff) owns HDMI, and it relies on the firmware to
program the display controller. Neither U-Boot nor nife drives the board's two MIPI DSI connectors.
A DSI panel therefore needs nife to program the display controller and the DSI transmitter itself,
which is the mode-setting driver rung five of the display ladder left for "only if ever needed".

## The hardware, from primary sources

- The VisionFive 2 datasheet (v1.53, VisionFive2-DSEN-001), section 5.3: a 2-lane DSI port up to
  1080p at 30 frames a second and a 4-lane port up to 2K at 30. Only one DSI port can drive a
  display at a time. The 2-lane connector carries its panel's I2C on GPIO 3 (clock) and GPIO 2
  (data). The datasheet names CZ101B4001 as the 4-lane port's compatible panel.
- The StarFive JH7110 datasheet (v1.63, JH7110-DSEN-001), sections 2.5.1 and 2.5.3: a display
  controller whose six layers serve up to two displays at up to 4K. It also has a MIPI TX D-PHY of
  one clock lane and up to four data lanes at up to 2.5 Gbps a lane.
- StarFive's vendor tree (`starfive-tech/linux` `JH7110_VisionFive2_devel` at `6d6aee034b81`):
  `dc8200@29400000` (`verisilicon,dc8200`, interrupt 95), `mipi@295d0000` (`cdns,dsi`, interrupt
  98) and `mipi-dphy@295e0000` (`m31,mipi-dphy-tx`).
- Mainline Linux (`torvalds/linux` `cbbddb6b08cc`) has no node for any of the three in
  `jh7110.dtsi`. It has the Cadence DSI bridge driver
  (`drivers/gpu/drm/bridge/cadence/cdns-dsi-core.c`), and its `display/verisilicon,dc.yaml` binding
  lists only the T-Head TH1520's DC8200.
- Mainline's VisionFive 2 tree enables `i2c2` on GPIO 3 and GPIO 2, the DSI connector's I2C.

## What it needs

- A DSI panel. The block names none: the 4-lane port's CZ101B4001 is the datasheet's own choice,
  and any panel a person picks needs its initialization sequence.
- The VOUT power domain and the VOUT clock and reset domain at `0x295c_0000`, which
  milestone 474 (a general JH7110 clock driver, covering all five domains) covers.
- I2C2, for the panel's touch controller or bridge, through the DesignWare I2C crate nife already
  runs on I2C5.
- DMA confinement. The display controller scans out of memory by physical address and the JH7110
  has no IOMMU, so the driver that programs its layer addresses can aim it at any memory. As
  milestone 157 says of the framebuffer, the record states that trust plainly.

## Done when

On radon, with a DSI panel attached, nife programs the D-PHY, the DSI host and one display
controller layer. It fills a buffer with a test pattern, and a person sees the pattern on the
panel and photographs it. The boot log with the driver's register reads goes under nife's
`bench/radon-<date>/`.

## Prior art

- Linux: the vendor kernel's `verisilicon` DRM driver for the DC8200 with the Cadence DSI bridge,
  and panel drivers in `drivers/gpu/drm/panel`. Mainline has the bridge but not this board's
  display controller.
- U-Boot: StarFive's U-Boot carries `drivers/video/starfive/sf_mipi.c` and
  `mipi_dsi_host.c` beside its HDMI driver, a smaller model of the same bring-up.
- No driver for this display path appears in OpenBSD's or FreeBSD's JH7110 support.
- Where nife differs: the driver serves rung one's framebuffer contract (`gfx_proto`) at EL0 as a
  new backend, as milestone 157's does, rather than a second display protocol.

Reuse: the `gfx_proto` framebuffer contract, the DesignWare I2C crate and the JH7110 clock and reset
crates. A search of the roadmap for `DSI`, `MIPI` and `panel` found no block that drives this
path.

## Index row

radon's two MIPI DSI connectors have never driven a panel. nife programs the display controller,
the DSI host and the D-PHY itself, behind the existing framebuffer contract, with the display DMA's
trust in memory stated.
