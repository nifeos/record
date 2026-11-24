---
status: PROPOSED
raised: 2026-11-24
milestone_dependencies: none
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: no
---
# A search that reaches the design record

Raised by the documentation audit of 2026-11-24 (UTC), [the record's departure](../../audit-reports/2026-11-24-the-records-departure.md), finding 3. Severity medium: the pages
a newcomer most needs to find are the ones no search reaches.

Reuse: nife's `script/apropos` and the `documentation::index` crate it runs, which build and read
an inverted index over markdown and module headers. No new dependency.

## The problem

nife's `script/apropos` exists because three strangers could not reach the network note, the
capabilities note or any decision by following the tree (milestone 117, the stranger test). Since
the design record left nife, that search reads only nife's notes, root documents and module
headers. Every page its own header names as the reason it exists is now here, and this repository
has no search: its scripts are `audits`, `citations`, `claim`, `decisions`, `fatal-risks`,
`journeys`, `lint`, `review-status` and `roadmap`. A reader who types `script/apropos socket` in
nife finds the socket contract and the network stack, and not `notes/net.md` or the socket
decisions.

## The work

- This repository gains `script/apropos`, the same index and reader as nife's pointed at
  `notes/`, `design/decisions/` and the milestone blocks, so a search here answers the questions
  nife's search answered before the move.
- nife's search, finding nothing in its own tree, says in one line that the design record has its
  own search and how to run it.
- A host test in each repository searches for one word and checks which page leads. Here the
  word picks out a decision; in nife it picks out a crate header.

Milestone 1018 publishes the record as a website, which may carry its own search. If that comes
first, the second item points there and the first goes away.
