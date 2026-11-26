# Stack: the appendices to notes/stack.md

`nifeos/nife:notes/stack.md` is the page to read. It explains the stack, records the first stack
incident and carries the `BUGS`, so a reader can act without opening anything here. Its incident
table is the index. These files hold each later stack incident in full, in date order.

Five of them, the incidents of 2026-08-14 to 2026-08-17 and the interrupt stack, were one file until
2026-09-25 (UTC), when they moved here under §212 (a prose budget). The move edited them only to
meet §213 (writing standards), splitting long sentences and dropping bold, with the meaning
unchanged. They read in the order the main page's table lists them, so "above", "below" and "this
file" in them mean that whole sequence.

*Name: provisional, for the directory and every stem in it. Each appendix's own preamble says the same of its stem. Naming is calef's;
`script/names --unratified` lists each stem.*

One appendix is not yet in that table: [progenitor-stack.md](progenitor-stack.md), the
progenitor's user stack, measured by a kernel gauge, gated in `script/swish-check` and raised from 8
pages to 12. Its `BUGS` says why the row waits.
[reading-a-guard-page-report.md](reading-a-guard-page-report.md) is not an incident. It says how
`kernel/src/stack.rs` builds the report a guard-page fault prints, and how to read it.
