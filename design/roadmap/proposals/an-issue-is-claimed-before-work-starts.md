---
status: PROPOSED
raised: 2026-11-25
milestone_dependencies: none
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: no
---
# Claim an issue before work starts on it

Raised by lane lane/issue-claims. Name: provisional, like every name below: the slug, the
`/claim` and `/release` commands, `script/claim --issue`, `helpers/issue_claim.py`, the
`issue claim` workflow and the 14 days.

Decided 2026-11-25 (UTC): a process claims an issue before work starts on it, and the mechanism
exists before third parties contribute. This proposal records how. It is a two-way door, so its
choices stand as provisional and nothing here waits on a ruling. Where a choice was close, it
takes the stricter rule, since loosening later breaks nobody and tightening does.

Reuse: GitHub's assignees, issue comments and closing keywords, which every part below rests on.
No bot service and no third-party action: the rule is one Python helper the lane command and the
workflow both call.

## Recommendation

An issue counts as held when any one of three things is true: a standing claim comment written by the
claim mechanism, any assignee at all, or an open pull request whose description closes it. A held
issue refuses a second claim. Nothing moves a claim from one holder to another except a release.

- A lane claims with `script/claim <branch> --new-work --issue N` (`owner/repo#N` for another
  repository). The command checks the issue before it touches git, posts the claim comment, reads
  the comments back, and gives way if an earlier claim won the race. It then cuts the worktree,
  opens the draft with `Closes #N`, and writes the draft's address into the claim comment's
  marker. If it stops before the draft opens, it deletes its claim comment. A token that cannot
  name its account, such as an App installation token, makes it refuse before it posts.
- An outsider claims by commenting `/claim` on a line of its own. The `issue claim` workflow
  replies with the claim comment, reads the comments back as a lane does, and assigns them, which
  GitHub allows because they commented. `/release` gives the claim back. An outsider holds one open claim at a time.
- What the issue shows: an assignee, and a claim comment naming the holder, the lane and branch
  for a lane, and the draft pull request. The comment carries a hidden marker, and the marker is
  the record the tools read.
- How a claim ends: the closing pull request merges and GitHub closes the issue; or the holder
  releases it; or the daily sweep releases a claim that has stood 14 days with no open pull request
  closing the issue. An open closing pull request keeps a claim alive however long review takes,
  and so does the open draft a lane's marker names, even after an edit drops `Closes #N`.
- A second attempt gets a reply that names the holder and refuses it. A lane prints the same reason
  and stops; it never steals and never works the issue unclaimed.

The design is not chosen for effort. At equal cost the refusing rule would still win, for the
reason in "Refuse, never move" below.

## Background

Today a draft pull request claims a branch, §90 (the claim is a draft pull request; the status flip
is a gate), and `script/claim` makes that claim in one command. Nothing claims an issue.
nifeos/nifeos.org#7 shows the gap: pull request #8 closed it, the issue had no assignee and
no comment saying anyone held it, and its timeline names only the account that every agent here
acts through. A second lane briefed on #7 that afternoon would have found nothing to stop it.

§90 considered GitHub issues and set them aside while the only workers were lanes that can branch.
It also said that once outside contributors need to file things, issues are the right answer and
§90 does not foreclose them. That day is near: partsfoundry's crates are public and take outside
pull requests, and an outsider who wants to work an issue cannot run `script/claim`.

Two facts shape everything below. First, every agent acts through one person's GitHub account, so
an assignee cannot tell two lanes apart; only the comment can name the lane. Second, GitHub assigns an
outsider only after they comment on the issue, or once they hold write access. The
`/claim` comment is that comment, so the assignment it triggers succeeds.

## Prior art, read

This lane read each at its source on 2026-11-25 (UTC).

**rustbot** (rust-lang/triagebot, `src/handlers/assign.rs`, and the forge page on issue
assignment). `@rustbot claim` assigns the commenter. When GitHub refuses the assignment, because
the commenter is not assignable, rustbot assigns itself and edits the issue body to say who holds
it "via this comment". `@rustbot release-assignment` gives it back, for the assignee or a team
member, and only team members may assign someone else. A claim on an issue someone else holds
reassigns it: nothing refuses. There is no stale rule and no link to a pull request.

**zulipbot** (zulip/zulipbot, its README and Zulip's contributing guide). `@zulipbot claim` works
only on issues labeled "help wanted" that nobody else holds, and refuses otherwise. A first-time
contributor gets read access as a collaborator so GitHub will assign them, and may hold one claim
until a first pull request merges. `@zulipbot abandon` gives it up. After 7 days with no activity
the bot posts a reminder, and after 3 more days with no reply it unassigns and removes the
"in progress" label. The contributing guide treats an issue as abandoned after two weeks with no
pull request update.

**prow** (kubernetes/test-infra, the `assign` plugin, and the Kubernetes triage guide). `/assign`
and `/unassign` start a line, ignore case, and work for anyone on anyone. GitHub decides who is
assignable: an organization member, a collaborator or someone who has commented; otherwise prow
replies that GitHub did not allow it. It never refuses an issue that already has an assignee; it
adds one, up to GitHub's cap of 10. The triage guide asks people not to self-assign an assigned
issue without asking first, and a triage engineer follows up after 30 days with no pull request.
A separate lifecycle bot marks an issue stale after 90 days.

**Plain GitHub assignment** (GitHub's documentation on assigning issues and its REST reference).
The assignable users are yourself, anyone who has commented on the issue, anyone with write access,
and organization members with read access. An issue takes at most 10 assignees. The add-assignees
call silently drops an assignee when the caller lacks push access, so a check after the call is the
only proof it worked. Closing keywords (`closes`, `fixes`, `resolves` and their tenses) close an
issue when the pull request merges into the default branch, and `Closes owner/repo#N` reaches
another repository. An `issue_comment` workflow runs from the default branch's copy of the file.
GitHub's hardening guide says to pass untrusted input through the environment, never through an
expression inside `run:`, and to grant the token the least it needs. Not confirmed from the
documentation: exactly which token permissions a fork's comment event receives; the workflow below
needs no secret, so the answer does not change it.

## Where this differs, and why

### Refuse, never move

rustbot and prow both let a second claim land on a held issue: rustbot replaces the holder, prow
adds one. Each leaves the courtesy of asking first to a written guide. Here a held issue refuses,
for lanes and outsiders alike, which is zulipbot's rule and the stricter one. The reason is the
failure this exists to prevent: two workers on one issue, neither knowing. A guide asks people to
remember, and lanes do not remember. A holder who has gone quiet loses the claim to the 14-day
sweep, and an owner can release one sooner by commenting `/release`.

### The first claim wins, and a pasted marker counts for nothing

The record is a marker comment, read in order: the first claim after the last release holds, and the
helper ignores a later claim. Only markers written by the workflow's bot or by the project's owners,
members and collaborators count, so an outsider who pastes a release marker into a comment changes
nothing. rustbot keeps its record in the issue body, which anyone with triage rights can edit; a
comment keeps its author.

### The lane goes in the comment, the account goes in the assignee

Because every agent shares one account, the assignee says only "the project holds this". The claim
comment names the lane, its branch and its draft, which is the line a second lane or a person reads.
None of the three bots needed this, since each of their claimers is one person.

### Stale after 14 days with no open closing pull request, and no reminder

zulipbot reminds after 7 days and releases after 10; Zulip's guide says two weeks; Kubernetes
follows up after 30. 14 days matches the guide a contributor would read, and the clock stops while
any open pull request closes the issue, so slow review never costs a contributor the claim. This
leaves out the reminder step: it is a second state to reason about, and the claim comment already
states the deadline. Adding a reminder later breaks nobody.

### One open claim per outsider, and none for members

Taken from zulipbot, with no exception after a first merge: a contributor who wants a second issue
finishes or releases the first. Members are exempt, since a lane holds one issue per draft already.
The limit counts open issues assigned to the outsider, read from the REST issues list rather than
search, which lags and allows about 30 calls a minute. An assignment made by hand counts too. Two
`/claim` comments on two issues in the same second can both pass that count, so each run counts
again after it assigns, and the claim outside the oldest one withdraws. Every run orders the
claims by age the same way, so a burst keeps exactly one.

### No "help wanted" gate, but held labels refuse

zulipbot claims only on "help wanted". This project has no such triage today, and a gate that
nobody keeps would refuse every claim. An issue labeled `needs-architect` refuses a claim, since
it waits on a ruling and nobody can finish it.

### Every claim posts, then reads back

A lane checks, posts its claim, and reads the comments back before it cuts a worktree. If an earlier
claim won, it deletes its own comment and stops, so a lost race costs one command. The workflow
does the same and rewrites a losing comment into a refusal, so a lane and an outsider never both
hold one issue. A concurrency group would not do: GitHub keeps one pending run per group and
cancels the one before, so any later comment on the issue could cancel a waiting `/claim` and
leave it with no reply. Only the sweep has a group of its own.

## The workflow is safe to run on a stranger's comment

- It runs on GitHub's hosted runners, never an owned machine, and holds no secret. Its only
  credential is the run's own token, limited to `issues: write` and the `contents: read` the
  checkout needs.
- An `issue_comment` event runs the default branch's workflow and helper, so a fork's code never
  runs. The job skips comments on pull requests, which share the event.
- The comment body never reaches a shell line. The helper reads GitHub's event file and matches a
  line that is exactly `/claim` or `/release`.
- The helper ignores a bot's comment, so the workflow cannot answer itself.

## How the record repositories follow

nife builds the mechanism first (nifeos/nife#4092). The other repositories follow in their own
pull requests, each citing the nife commit it copies:

- nifeos/record: copy `helpers/issue_claim.py` beside the copied `script/claim`, extend the
  `claim_copy` lint to cover it, and add the workflow.
- nifeos/nifeos.org: add the workflow and the helper.
- partsfoundry/crate-workflows: offer the workflow to every crate repository from the template, written
  with no mention of nife, so each partsfoundry crate gets it at its next template sync.
- nifeos/basalt: add the workflow and the helper.

## BUGS

- The sweep reads every open issue's comments once a day. At hundreds of open issues that is
  hundreds of calls a day; it stays well inside the token's budget at today's counts, and a search
  for assigned issues only would cut it.
- The outsider limit counts issues assigned to the outsider. A claim recorded in a comment when the
  assignment failed does not count toward it.
- A lane whose command dies between the draft and the link step leaves a claim comment that says
  its draft is to follow and names no pull request. The draft still says `Closes #N`, so the claim
  holds while that line stays in its body.
