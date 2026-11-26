# The documentation standard is FreeBSD's

*Appendix to `nifeos/nife:AGENTS.md`, which carries the rules: task-oriented, in-tree, real
`EXAMPLES`, an honest `BUGS` section beside the feature. This file carries why that standard was
chosen and what each of its four parts buys, and it is the home of the one-home rule below. Moved here 2026-09-23 (UTC) on calef's authorization,
unchanged in substance.*

The standard to aim at is FreeBSD's (calef, 2026-07-30): the Handbook and the man pages, which
are the best documentation in the field and are the reason a FreeBSD admin can answer a question
without leaving the system. Four things make them that, and all four are things we can do:

- Task-oriented. "How do I do X", in order, with the actual commands, rather than a reference
  dump the reader has to reassemble.
- In-tree and versioned with the code, so the docs cannot describe a system that no longer
  exists. Already true here; keep it true.
- Real `EXAMPLES`. A page without a worked example has not finished explaining itself.
- An honest `BUGS` section. FreeBSD man pages document known limitations *in the manual*, next
  to the feature, rather than only in a tracker. This is the one worth copying hardest, because it
  is the convention this project already reaches for by instinct: the map "tie", the spawn caveat,
  the scope notes on parity gaps. **Name the limitation where the reader meets the feature.** When a
  limitation graduates from record to plan, and what forces the graduation, is the convention of §71
  (a limitation is promoted when it becomes a plan). A `BUGS` entry is a fact, a roadmap row is
  intent, and the promotion triggers are listed there.

The point is not the format, which is theirs. It is the posture: documentation written for someone
who has to *use* the thing, and honest enough that they trust it when it says something works.

## One home for each rule or fact

Each rule or fact has one home, and every other file that needs it links to that home instead of
restating it (decided 2026-11-26 UTC, nifeos/record#50). A copy drifts: when the rule changes, the
copies nobody found keep the old one. The home is the file that owns the subject. A decision holds
its ruling, a runbook its steps, a milestone its own conditions. Another file names the rule in a
few words and links there.

The `repeated_sentences` section of `script/lint` holds the record to it. It refuses a sentence of
100 or more characters that appears in more than one Markdown file under `design/` and `notes/`,
unless `design/repeated-sentence-baseline.txt` lists that copy. The list holds the copies that
existed when the rule took effect, and it only shrinks. `helpers/repeated_sentences.py` says what
the check exempts and why.
