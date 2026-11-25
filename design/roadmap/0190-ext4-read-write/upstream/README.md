# Upstream drafts for milestone 190

[Milestone 190 (ext4, read and write: a Rust implementation with libext2fs as the host-side
oracle)](../../0190-ext4-read-write.md) sends its `rsext4` fixes to `rcore-os/tgoskits`.
Upstream takes one task per pull request and processes none without a linked Issue. Each
submission therefore has a draft here holding the Issue to file first and the pull request, each in
Chinese with an English rendering, then the base commit and the test evidence. A `.patch`
beside it holds the `git format-patch` output. Nobody files a draft until the architect has
reviewed its text and given a separate go.

- [`2a-free-empty-extent-index.md`](2a-free-empty-extent-index.md): upstream item 2's first
  defect, a depth-2 truncate that fails with `extent:empty_index`; merged as
  rcore-os/tgoskits#2827.
- [`2b-restore-truncate-tail.md`](2b-restore-truncate-tail.md): item 2's second defect, a failed
  truncate that leaves the file's tail zeroed; open as rcore-os/tgoskits#2829, with
  rcore-os/tgoskits#2845 stacked on it.
- [`4-fuzz-targets.md`](4-fuzz-targets.md): upstream item 4, seven `cargo fuzz` targets over the
  parsers, mount and journal replay, with an `mke2fs` seed corpus; merged as
  [rcore-os/tgoskits#2835](https://github.com/rcore-os/tgoskits/pull/2835).
- [`5a-crc32c-safety-arguments.md`](5a-crc32c-safety-arguments.md): upstream item 5, first half,
  a safety argument at each CRC32C `unsafe` use; merged as rcore-os/tgoskits#2831, which takes
  hardware CRC32C availability from the environment.
- [`5b-group-descriptor-decode.md`](5b-group-descriptor-decode.md): upstream item 5, second half,
  group descriptors decoded instead of cast from the table bytes; merged as
  rcore-os/tgoskits#2833.
- [`6-kani-harnesses.md`](6-kani-harnesses.md): upstream item 6, an Issue offering Kani harnesses
  for the on-disk parsers, rcore-os/tgoskits#2836, which has no answer; it has no `.patch`, and the
  harnesses run in partsfoundry/rsext4.
- [`7-mount-refusal-reason.md`](7-mount-refusal-reason.md): upstream item 7, a refused mount
  reports its reason instead of a bare `Io`; merged as rcore-os/tgoskits#2839.
- [`8-whole-inode-times.md`](8-whole-inode-times.md): upstream item 8, `InodeInfo` reports whole
  times, nanoseconds and epoch bits included; open as rcore-os/tgoskits#2840.
- [`9-inode-bitmap-padding.md`](9-inode-bitmap-padding.md): upstream item 9, the first inode
  allocated in an `INODE_UNINIT` group leaving its inode bitmap's padding clear; merged as
  rcore-os/tgoskits#2825.

*Name: provisional. For the drafts the parent's upstream round cites. calef names directories.*

- `2a-free-empty-extent-index` Name: provisional. The upstream item's number, a letter per
  submission, and what it fixes. calef names files.
- `2b-restore-truncate-tail` Name: provisional. As for `2a`. calef names files.
- `4-fuzz-targets` Name: provisional. The upstream item's number and what it adds. calef names
  files.
- `5a-crc32c-safety-arguments` Name: provisional. The upstream item's number and what it adds.
  calef names files.
- `5b-group-descriptor-decode` Name: provisional. The upstream item's number and what it fixes.
  calef names files.
- `6-kani-harnesses` Name: provisional. The upstream item's number and what it offers. calef names
  files.
- `7-mount-refusal-reason` Name: provisional. The upstream item's number and what it fixes. calef
  names files.
- `8-whole-inode-times` Name: provisional. The upstream item's number and what it fixes. calef
  names files.
- `9-inode-bitmap-padding` Name: provisional. The upstream item's number and what it fixes. calef
  names files.
