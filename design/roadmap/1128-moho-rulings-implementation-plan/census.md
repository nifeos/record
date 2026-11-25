# The census

An appendix to [the milestone](../1128-moho-rulings-implementation-plan.md).

Measured at `nifeos/nife@6bed50566`, `nifeos/moho_abi@1e99eed` and
`partsfoundry/capability_table@968a16f`. Every nife count is `git grep -c -E <pattern>` over
`'*.rs' ':!vendor'`, summed: lines, not occurrences. A wrapper's count also leaves out
`crates/user_mode_runtime`, where the wrapper is defined.

## Wrapper call sites

Pattern `\b<name>\(`. `send`, `call` and `reply` also match functions that are not the wrappers,
so their counts are upper bounds.

| wrapper | lines | files | step |
|---|---|---|---|
| `send` | 551 | 167 | 11 |
| `call` | 528 | 119 | 11 |
| `reply` | 145 | 40 | 11 |
| `invoke` | 145 | 57 | 11 |
| `receive` | 126 | 51 | 11 |
| `map_page_frame` | 63 | 40 | 10 |
| `receive_capability` | 37 | 15 | 11 |
| `receive_request` | 36 | 30 | 11 |
| `send_capability` | 33 | 24 | 11 |
| `retype_into_page_frame` | 26 | 20 | 12 |
| `receive_message` | 25 | 15 | 11 |
| `retype_into_kernel_object` | 22 | 12 | 12 |
| `call_receiving` | 17 | 10 | 11 |
| `thread_control_block_capability_insert` | 9 | 5 | 12 |
| `split_memory_region` | 6 | 5 | 12 |
| `thread_control_block_configure` | 6 | 4 | 12 |
| `retype_page_frame_run` | 5 | 3 | 12 |
| `thread_control_block_start` | 4 | 4 | 12 |
| `slice_page_frame` | 2 | 2 | 12 |
| `receive_capability_message` | 2 | 2 | 11 |

The 145 `invoke(` lines split by top directory: `system_tests` 37 files, `patches` 9, `fixtures`
4, `kernel` 3, `components` 2, `crates` 2.

## Symbols

| symbol | pattern | lines | files | step |
|---|---|---|---|---|
| `Error::NotPermitted` | `Error::NotPermitted` | 144 | 43 | 10 |
| `RETYPE_OBJECT` | `\bRETYPE_OBJECT\b` | 91 | 33 | 10 |
| `SPLIT` | `\bSPLIT\b` | 77 | 25 | 10 |
| `REVOKE` | `\bREVOKE\b` | 63 | 28 | 12 |
| `Error::OutOfMemory` | `Error::OutOfMemory` | 46 | 21 | 10 |
| `CAPABILITY_TABLE_SLOTS` | `CAPABILITY_TABLE_SLOTS` | 40 | 23 | 12 |
| `BADGE` | `\bBADGE\b` | 39 | 19 | 10 |
| `Error::WrongObject` | `Error::WrongObject` | 39 | 21 | 10 |
| `Error::BadPointer` | `Error::BadPointer` | 38 | 15 | 10 |
| `FAULT_RENDEZVOUS_SLOT` | `FAULT_RENDEZVOUS_SLOT` | 33 | 20 | 12 |
| `rights::GRANT` | `rights::GRANT` | 31 | 10 | 12 |
| `CAPABILITY_INSERT` | `\bCAPABILITY_INSERT\b` | 30 | 15 | 10 |
| `Error::BadMethod` | `Error::BadMethod` | 30 | 13 | 10 |
| `SLICE` | `\bSLICE\b` | 29 | 13 | 10 |
| `ABI_VERSION` | `\bABI_VERSION\b` | 22 | 16 | 9 |
| `reboot::` | `reboot::` | 13 | 10 | 10 |
| `::WAIT` | `::WAIT\b` | 46 | 22 | 5 |
| `::BIND` | `::BIND\b` | 26 | 15 | 5 |
| `::MAP` | `::MAP\b` | 93 | 41 | 5 |
| `MAP_` | `MAP_` | 399 | 79 | 5, 10 |

## The `std` overlay

Over `patches/std-nife`: `rt::(invoke|send|receive|call)` on 38 lines in 15 files, `Error::` on 29
lines in 5 files, and `NO_SUCH_METHOD` on 8 lines in 4 files. `rt.rs` is 272 lines.

## Proofs

`kani::proof` counts: the kernel 27, `inter_process_communication` 16, `capability_table` 12,
`capability_manifest_note` 7, `capability_plan` 5. `capability_plan`'s proofs bound a slot by
`CAPABILITY_TABLE_SLOTS`.

## Elsewhere

- `moho_abi`: 125 public constants; `pinned-at-version-1.txt` is 116 lines.
- `moho_abi` is named in 17 nife manifests, 16 of them pinned by commit. 212 Rust files outside
  `user_mode_runtime` name `user_mode_runtime`.
- Falsification patches naming `moho_abi` or `user_mode_runtime`: 23 under `system_tests`, two
  under `xtask`, two under `crates/capability_plan`. Three name `ipc_send` or `ipc_call_reply`.
- basalt's `main` names no `moho_abi` symbol.
