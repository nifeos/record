# The demand measurement that sets the order

An appendix to [the milestone](../1129-crate-interfaces-best-in-class.md).

Measured on 2026-11-25 (UTC) from the crates.io API: `/api/v1/crates/<name>` for the version, the
total downloads and the downloads in the last 90 days (`recent_downloads`), and
`/api/v1/crates/<name>/reverse_dependencies?per_page=1` for the count of reverse dependencies
(`meta.total`). "Updated" is the crate's `updated_at` date. The comparators here are the ones that
set the order. Each review lane chooses its own by the rule in the milestone. It measures them again,
and it may find a stronger one.

A crate ranks by its leading comparator: the most-downloaded crate in the last 90 days that solves
the same problem. A neighbor solves a nearby problem and does not rank. An integration target is a
crate the reviewed crate might implement or accept, not a rival.

## Crates with a Rust comparator

| rank | crate | comparator | role | version | total | 90 days | reverse dependencies | updated |
|---|---|---|---|---|---|---|---|---|
| 1 | `byte_glob` | `glob` | leading | 0.3.4 | 759,583,455 | 185,113,208 | 4,205 | 2026-10-08 |
| | | `globset` | comparator | 0.4.22 | 306,753,901 | 82,288,870 | 2,110 | 2026-11-22 |
| | | `wildmatch` | comparator | 2.7.0 | 25,536,173 | 6,715,450 | 114 | 2026-10-20 |
| 2 | `generational_table` | `slotmap` | leading | 1.1.1 | 141,978,757 | 43,982,979 | 622 | 2025-12-06 |
| | | `generational-arena` | comparator | 0.2.9 | 10,968,048 | 1,267,301 | 57 | 2023-05-22 |
| | | `thunderdome` | comparator | 0.6.1 | 1,203,149 | 200,772 | 32 | 2023-06-25 |
| | | `slab` | neighbor (no generations) | 0.4.12 | 1,189,866,199 | 321,676,627 | 642 | 2026-01-31 |
| 3 | `domain_name_system` | `hickory-proto` | leading | 0.26.4 | 111,719,582 | 38,227,507 | 173 | 2026-11-24 |
| | | `simple-dns` | comparator | 0.13.1 | 13,732,289 | 4,349,582 | 37 | 2026-11-16 |
| | | `domain` | comparator | 0.13.0 | 13,797,000 | 2,316,814 | 45 | 2026-11-24 |
| | | `smoltcp` | integration target | 0.14.0 | 11,054,867 | 3,441,725 | 130 | 2026-08-17 |
| 4 | `line_editor` | `rustyline` | leading (needs `std`) | 19.0.0 | 62,615,303 | 15,825,645 | 1,290 | 2026-10-17 |
| | | `reedline` | comparator (needs `std`) | 0.53.0 | 4,440,068 | 1,314,161 | 164 | 2026-11-09 |
| | | `menu` | comparator (`no_std`) | 0.6.1 | 177,603 | 81,484 | 2 | 2024-11-29 |
| | | `noline` | comparator (`no_std`) | 0.5.1 | 37,727 | 2,219 | 1 | 2024-12-12 |
| 5 | `intrusive_queue` | `intrusive-collections` | leading | 0.10.3 | 28,372,788 | 10,102,169 | 52 | 2026-08-04 |
| | | `cordyceps` | comparator | 0.3.5 | 10,903,656 | 5,016,172 | 12 | 2026-07-29 |
| | | `heapless` | neighbor (owning queues) | 0.9.4 | 191,822,576 | 64,501,842 | 1,236 | 2026-11-18 |
| 6 | `designware_mobile_storage` | `sdio-host` | leading (card registers, no controller) | 0.9.0 | 1,738,303 | 637,944 | 3 | 2022-07-27 |
| | | `embedded-sdmmc` | comparator | 0.10.0 | 412,182 | 62,294 | 39 | 2026-08-10 |
| | | `sdmmc` | comparator | 0.1.0 | 11,315 | 591 | 2 | 2026-01-28 |
| | | `dwmmc-host` | comparator (same controller) | 0.4.2 | 1,920 | 562 | 2 | 2026-09-09 |
| 7 | `file_allocation_table` | `fatfs` | leading | 0.3.6 | 1,973,907 | 542,215 | 60 | 2023-01-17 |
| | | `embedded-sdmmc` | comparator | 0.10.0 | 412,182 | 62,294 | 39 | 2026-08-10 |
| | | `embedded-io` | integration target | 0.7.1 | 202,819,167 | 93,348,830 | 353 | 2025-10-01 |
| 8 | `device_tree_blob` | `fdt` | leading | 0.1.5 | 1,708,239 | 470,333 | 7 | 2026-10-01 |
| | | `dtoolkit` | comparator | 0.5.0 | 11,363 | 7,502 | 3 | 2026-11-03 |
| | | `fdt-rs` | comparator | 0.4.5 | 115,325 | 4,123 | 1 | 2024-02-25 |
| | | `vm-fdt` | neighbor (writer only) | 0.3.0 | 3,320,128 | 762,674 | 15 | 2023-11-15 |
| 9 | `e1000e` | `ixgbe-driver` | leading (another Intel family) | 0.1.1 | 87,031 | 50,198 | 2 | 2026-02-26 |
| | | `e1000-driver` | comparator | 0.1.0 | 1,885 | 92 | 0 | 2023-02-24 |
| | | `virtio-drivers` | neighbor (another device class) | 0.13.0 | 445,035 | 101,691 | 91 | 2026-03-03 |
| | | `smoltcp` | integration target | 0.14.0 | 11,054,867 | 3,441,725 | 130 | 2026-08-17 |
| 10 | `extensible_host_controller_interface` | `xhci` | leading | 0.9.2 | 124,753 | 37,572 | 2 | 2023-07-19 |
| | | `crab-usb` | comparator | 0.12.1 | 35,412 | 20,067 | 2 | 2026-09-11 |
| 11 | `designware_ethernet` | `stm32-eth` | leading | 0.8.2 | 46,886 | 21,797 | 0 | 2026-02-16 |
| | | `embassy-stm32` | neighbor (a whole HAL) | 0.6.0 | 863,466 | 202,276 | 48 | 2026-03-20 |
| 12 | `universal_serial_bus` | `crab-usb` | leading (host side) | 0.12.1 | 35,412 | 20,067 | 2 | 2026-09-11 |
| | | `usbh` | comparator | 0.1.0 | 1,542 | 10 | 0 | 2023-08-06 |
| | | `usb-device` | neighbor (device side) | 0.3.2 | 5,585,145 | 969,224 | 132 | 2024-03-06 |
| | | `usbd-hid` | neighbor (device side) | 0.10.2 | 1,617,177 | 302,490 | 20 | 2026-09-02 |
| 13 | `non_volatile_memory_express` | `nvme-driver` | leading | 0.8.2 | 5,430 | 920 | 1 | 2026-09-09 |
| | | `vroom` | comparator | 0.1.0 | 1,641 | 12 | 0 | 2020-05-11 |
| 14 | `jh7110_entropy` | none found as a standalone crate | | | | | | |
| | | `rand_core` | integration target | 0.10.1 | 2,312,469,600 | 689,686,442 | 2,827 | 2026-09-02 |

`stm32-eth` ranks for `designware_ethernet` because STM32 parts carry a Synopsys DesignWare
Ethernet controller. This block recalls that and did not check it. Lane D checks it. From rank 13 on, no
leading comparator draws 10,000 downloads a quarter, so those reviews also name the system outside
Rust that sets the bar, such as the Linux and OpenBSD drivers or SPDK.

## Crates with no Rust comparator in the same problem

These rank after the fourteen above. The review of each names the system outside Rust that sets the
bar, and the shared contract-crate layout matters more to them than any one comparator.

| crate | nearest measured crate | role | 90 days | reverse dependencies |
|---|---|---|---|---|
| `capability_table` | `sel4` 0.0.12 | neighbor (bindings) | 140 | 1 |
| `interfaces_note` | `object` 0.41.0 | neighbor (reads ELF notes in general) | 158,062,924 | 577 |
| `address_space_layout` | none | | | |
| `boot_ladder` | none | | | |
| `grant_plan` | none | | | |
| `grant_contract` | none | | | |
| `program_argument_contract` | none | | | |
| `block_roster_contract` | none | | | |
| `byte_sink_contract` | `embedded-io` 0.7.1 | integration target | 93,348,830 | 353 |
| `clock_contract` | `seqlock` 0.2.0 | neighbor (the reader-never-waits mechanism) | 1,229,856 | 16 |
| `counter_frequency_contract` | none | | | |
| `entropy_contract` | `rand_core` 0.10.1 | integration target | 689,686,442 | 2,827 |
| `environment_contract` | none | | | |
| `file_system_contract` | none | | | |
| `terminal_contract` | none | | | |

Crates searched for and not found on crates.io on that day: `e1000`, and no standalone driver
crate for the JH7110's random number generator.
