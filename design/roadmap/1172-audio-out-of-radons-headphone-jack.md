---
status: NOT-STARTED
raised: 2026-11-28
milestone_dependencies: none
decision_dependencies: none
machine_requirements: a VisionFive 2 with headphones or a line input on its 3.5 mm jack
specific_machine: radon (the only JH7110 board this project has)
needs_person: yes
---
# 1172. Audio on radon: a tone out of the 3.5 mm jack, then I2S

*(The number, the title and the slug are provisional.)*

Raised 2026-11-28 (UTC) by lane `lane/radon-unexercised-hardware`. On that date calef asked for a
milestone for every part of the VisionFive 2 that nife has not yet exercised on the board, and
this is one of them.

## What is unexercised

Every audio block on the JH7110 and the board's headphone jack. nife has no audio driver, and no
audio contract for one to serve.

## The hardware, from primary sources

- The VisionFive 2 datasheet (v1.53, VisionFive2-DSEN-001), section 5.7: analog audio output
  through a 4-ring 3.5 mm headphone jack.
- The StarFive JH7110 datasheet (v1.63, JH7110-DSEN-001), section 2.7: a PCM TDM block, two I2S
  transmitters (one of them for HDMI audio), and one I2S receiver. The receiver takes the internal
  PDM block's output or an external I2S converter's. The chip also has SPDIF transmit and receive,
  and a PDM block of up to four microphones.
- Mainline Linux `jh7110.dtsi` (`torvalds/linux` `cbbddb6b08cc`): `tdm@10090000`, the receiver at
  `i2s@100e0000`, `pwmdac@100b0000`, the transmitters at `i2s@120b0000` and `i2s@120c0000`, and the
  AXI DMA engine at `dma-controller@16050000` (`starfive,jh7110-axi-dma`) that each of them uses.
- Mainline's VisionFive 2 tree (`jh7110-common.dtsi`) builds a `simple-audio-card` named
  `StarFive-PWMDAC-Sound-Card` from the PWMDAC and a dummy codec, with the PWMDAC's left and right
  outputs on GPIO 33 and GPIO 34. Unverified: that those two pins drive the headphone jack through
  a filter. No source read here says so, but no other analog output exists on the board.

## What it needs

- A first path, the PWMDAC. It needs no codec chip and no I2C, only its clocks and resets, the two
  pins and a DMA channel.
- An audio contract, which nife does not have: sample format, rate, buffer ownership and
  underrun reporting. The block proposes one and the record holds it as provisional.
- The AXI DMA engine, which nife has never driven. The JH7110 has no IOMMU, so the DMA engine can
  reach all of physical memory, and so can whoever programs its descriptors. The record states
  which program that is.
- Then I2S, which on this board leaves the chip through header pins and needs an external
  converter that a person wires on.

## Done when

On radon, nife plays a 1 kHz sine wave at 48 kHz out of the headphone jack for ten seconds. A host
records the jack's output through a line input, and the recording's main frequency lies within
1 percent of 1 kHz. The recording and the log go under nife's `bench/radon-<date>/`. I2S counts
once the same tone reaches an external converter through the header.

## Prior art

- Linux mainline: `sound/soc/starfive/jh7110_pwmdac.c`, `jh7110_tdm.c` and the DesignWare I2S
  driver `sound/soc/dwc/dwc-i2s.c`, joined by ASoC's `simple-audio-card`.
- OpenBSD: `sys/dev/fdt/simpleaudio.c` matches `simple-audio-card` and joins a controller and a
  codec into one `audio(4)` device. It has no StarFive PWMDAC or I2S driver at `e70d4a7ea910`.
- Where nife differs: the driver runs at EL0 and serves a small byte-stream contract rather than a
  sound card framework, and the record states the DMA engine's trust in memory.

Reuse: the JH7110 clock and reset crates. A search of the roadmap for `audio`, `I2S`, `PWMDAC` and
`sound` found no block that drives these parts.

## Index row

radon's headphone jack and the JH7110's audio blocks have never made a sound under nife. The
PWMDAC plays a checked tone first, through the AXI DMA engine nife has not yet driven, and I2S
follows through the header.
