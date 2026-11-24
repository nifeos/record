#!/usr/bin/env python3
"""helpers/counted_claims_check.py: the record's counted claims, checked against nife at its pin.

    python3 helpers/counted_claims_check.py

A record document states a count with a marker after the number, `<!--count:NAME-->` (or
`-at-least:` and `-at-most:`), and this check derives each NAME and fails when the prose disagrees.
nifeos/record:notes/counted-claims.md is the manual. The prose lives here and almost every count is
of nife's code (Kani harnesses, `unsafe` blocks, system calls), so the markers are read from the
record's tree and each derivation runs in nife's tree at the commit basalt's main pins
(`helpers/nife_tree.py`), which is the only nife every reader of the record sees. The audit count
reads the record's own audit index.

This is the record half of the `counted claims` section of nife's `script/lint`, which keeps the
registry for markers in nife's own files. The registry below is the same one; a NAME added there
for a record document is added here too. What the record half leaves out: the three-way harness
cross-check, which compares nife's own derivations with each other and stays in nife.
`moho_abi`'s source is read at the revision nife's Cargo.lock names rather than through `cargo
metadata`, which would fetch every dependency; `cargo metadata --no-deps` still lists the workspace,
under the stable toolchain, because it reads no source.
"""
import json
import os
import pathlib
import re
import subprocess
import sys

# The derivations this gate shares with `script/metrics`, in one place rather than copied into both
# (milestone 236 (three derivations are copied between scripts), because nothing noticed when they
# drifted). This script `cd`s to the repository root on line 18, which is what lets a heredoc import
# at all; the block comment above `_unsafe_census` below says what stays here and why.
# `dont_write_bytecode` because the import would otherwise leave a `helpers/__pycache__/`
# behind on every run, which is an untracked directory a gate has no business creating.
sys.dont_write_bytecode = True
RECORD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RECORD, 'helpers'))
import counted_claims                                                       # noqa: E402
import nife_tree                                                            # noqa: E402
import rust_source                                                          # noqa: E402

NIFE = nife_tree.path()
os.chdir(NIFE)
# `cargo metadata --no-deps` reads manifests and no source, so any toolchain answers it; naming
# stable keeps rustup from installing nife's pinned nightly just to list the workspace.
os.environ.setdefault('RUSTUP_TOOLCHAIN', 'stable')

# --- the registry -------------------------------------------------------------------------------
#
# One entry per count name. `question` is the sentence the prose asks, in the prose's own words,
# because the failure this gate is most likely to have is answering a subtly different question than
# a human would and so failing a correct document. "How many `#!/bin/sh` scripts" has at least three
# defensible answers (`ls script/` gives 37; the shellcheck glob is wider), so the entry has to say
# which one it means and the prose has to mean the same one.
#
# `derive` returns an int and must be CHEAP and DETERMINISTIC: lint runs on every build, and a gate
# that is slow or flaky is a gate people route around. Anything needing a build (the frame numbers
# from script/stack-frame-check, say) does not belong here. Each derivation's comment states the
# SHAPE IT ASSUMES, because this tree already recorded a count that was wrong for exactly that
# reason: the grep behind it matched only single-line `#[path]` includes while several sites were
# two lines, and the resulting "three modules" went into AGENTS.md as fact.

# A proof harness: the attribute alone on its line, indented or not. Anchoring to the whole line is
# what keeps prose ABOUT the attribute out of the count -- helpers/kani-lint-shim/ spells
# `#[kani::proof]` twice inside doc comments, and neither is a harness. The `\b.*` tail admits
# `#[kani::proof_for_contract(...)]`, which the tree does not use today; matching only the bare form
# would give a count that is quietly low the day somebody does, and a low count is no better than a
# high one when the prose is copying it.
HARNESS = re.compile(r'^[ \t]*#\[kani::proof\b.*\][ \t]*$', re.M)

# Files holding `#[kani::proof]` that belong to no workspace package. Both are deliberate and
# neither is provable: the shim is source rustc compiles by hand for this file's harness-clippy
# pass, and `vendor/redoxfs` is upstream code kept out of the workspace on purpose (see the
# workspace Cargo.toml's own note). The verify-table check further down this file states the same
# two names in its own `EXEMPT`, and the duplication is deliberate rather than missed: the two checks
# are separate `python3` heredocs in a shell script, so there is no scope they could share. A new
# entry should be argued for rather than added, and it belongs in both.
_HARNESS_EXEMPT = {
    'helpers/kani-lint-shim/kani_attributes.rs',
    'vendor/redoxfs/src/node.rs',
}


def _harness_hits():
    """(workspace package, number of harnesses) for every package that has any.

    Scoped to the workspace because that is what `cargo kani` can reach, and **it was scoped to
    `crates/` until milestone 212 (script/falsifications walks crates/ only)**, with a docstring here that gave the reason as "the kernel, the
    user programs and xtask are not packages it compiles". That stopped being true a milestone
    later: 193 (put `kernel/src` within reach of the prover) and 197 (`user/` and `xtask` are out of
    reach of the prover) each added a row to `script/verify`'s crate table, and this count went on
    excluding both, so the tree carried two derived numbers for one question. That is precisely the
    failure `<!--count:-->` exists to prevent, one level up: the derivation was a snapshot of a
    scope somebody last checked.

    The package list comes from the same `cargo metadata` walk this file's verify-table check uses,
    with its EXEMPT set doing the work it already does: the `helpers/kani-lint-shim` source and
    `vendor/redoxfs` carry harnesses this suite has never run, and counting them would make the
    number describe a suite nobody executes.
    """
    meta = json.loads(subprocess.run(
        ['cargo', 'metadata', '--format-version', '1', '--locked', '--no-deps'],
        capture_output=True, text=True, check=True,
    ).stdout)
    # The separate workspaces `script/verify` also proves (rust_source.PROVED_WORKSPACES) count here
    # too, because the text-only derivation below cannot tell a workspace boundary and counts them.
    prefixes = {pkg['name']: rel + '/'
                for pkg, rel in rust_source.proved_packages(meta['workspace_root'], meta)}
    hits = {}
    for f in subprocess.run(['git', 'grep', '-lE', r'#\[kani::proof', '--', '*.rs'],
                            capture_output=True, text=True).stdout.split():
        if f in _HARNESS_EXEMPT:
            continue
        owner = None
        for name, prefix in prefixes.items():
            if f.startswith(prefix) and (owner is None or len(prefix) > len(prefixes[owner])):
                owner = name
        if owner is None:
            continue
        n = len(HARNESS.findall(pathlib.Path(f).read_text(errors='replace')))
        if n:
            hits[owner] = hits.get(owner, 0) + n
    return hits


def _sh_scripts():
    """Files under script/ and helpers/*.sh whose first line is exactly `#!/bin/sh`.

    Assumes script/ is flat (it is: every entry is an executable, no subdirectories) and that
    helpers/ mixes .sh files with directories, which is why only *.sh is globbed there. Deriving
    from the shebang rather than from the glob is what makes the NAME true: the prose says
    "`#!/bin/sh` scripts", so the gate counts files that start with `#!/bin/sh`.
    """
    files = [p for p in pathlib.Path('script').iterdir() if p.is_file()]
    files += [p for p in pathlib.Path('helpers').glob('*.sh') if p.is_file()]
    return sum(1 for p in files
               if p.read_text(errors='replace').split('\n', 1)[0].strip() == '#!/bin/sh')


def _moho_abi_source():
    """The `src` directory of the `moho_abi` nife links, at the revision its Cargo.lock names.

    The crate lives in its own repository (`nifeos/moho_abi`), which nife pins by git revision, so
    the counts below describe the binary interface nife actually builds against. The checkout is
    kept beside the nife tree's, one per revision.
    """
    lock = pathlib.Path('Cargo.lock').read_text()
    m = re.search(r'name = "moho_abi"\nversion = "[^"]*"\nsource = "git\+(https://[^?#"]+)'
                  r'[^#"]*#([0-9a-f]{40})"', lock)
    if not m:
        sys.exit('lint: nife\'s Cargo.lock links no moho_abi from git, so the system call and rights '
                 'counts have no source')
    url, rev = m.groups()
    dest = pathlib.Path(nife_tree.qualified_paths._cache_dir()) / f'moho_abi-{rev}'
    if not (dest / '.complete').is_file():
        tmp = pathlib.Path(f'{dest}.partial-{os.getpid()}')
        for args in (['init', '-q', str(tmp)],
                     ['-C', str(tmp), 'fetch', '-q', '--depth=1', url, rev],
                     ['-C', str(tmp), 'checkout', '-q', '--detach', 'FETCH_HEAD']):
            subprocess.run(['git', *args], check=True)
        (tmp / '.complete').touch()
        try:
            tmp.rename(dest)
        except OSError:
            subprocess.run(['rm', '-rf', str(tmp)])
    return dest / 'src'


def _abi_system_calls():
    """`SYSTEM_CALL_*` u64 constants in moho_abi's src/lib.rs: the width of the system call trap.

    Assumes the system call numbers are the crate's only `SYSTEM_CALL_`-prefixed u64 constants, which they
    are and which the naming makes self-enforcing: every other constant in the crate is a method, a
    right, an object type or a sentinel, and none of those is spelled `SYSTEM_CALL_`. Optional leading
    whitespace so a future one nested in a module still counts; a nested one that was NOT counted
    would make this number quietly low, and a low count is no better than a high one when prose is
    copying it (the `_sh_scripts` entry records the same hazard).

    It is here because the 2026-08-17 documentation sweep found the ABI's own front page, the
    kernel's system call module, an `Error` variant's description and two notes all saying the surface
    was **three** calls. `SYS_CAP_DELETE` landed 2026-07-24 and moved none of them.
    """
    text = (_moho_abi_source() / 'lib.rs').read_text(errors='replace')
    return len(re.findall(r'^[ \t]*pub const SYSTEM_CALL_[A-Z_0-9]+: u64\b', text, re.M))


def _rights_bits():
    """Named single-bit rights in `moho_abi::rights`: how many rights a capability can carry.

    Counted from the ABI's rights module, which the kernel asserts equal to the rights mask of the
    capability table crate it links (`nifeos/capability_table`, a pinned dependency that is no
    longer in this tree). Only the single-bit constants count: `ALL` and `SPEND_ONLY` are masks of
    the others, so the shape assumed is `pub const NAME: u64 = 1 << N;` and neither mask matches it.

    That `ALL` is exactly the union of these bits is pinned by the kernel's assertion and by tests
    rather than here. This counts; those compare.
    """
    text = (_moho_abi_source() / 'rights.rs').read_text(errors='replace')
    return len(re.findall(r'^[ \t]*pub const [A-Z_0-9]+: u64 = 1 << \d', text, re.M))


def _loom_hits():
    """(crate directory name, loom harnesses) for every crate under crates/ that runs a loom model.

    A loom harness is a test that calls `loom::model`, or builds a `loom::model::Builder` to bound
    the search, which is the thing that makes it a harness rather than an ordinary test: the model
    is the search. Counted
    that way rather than by `#[test]` inside a `#[cfg(all(test, loom))]` module, because the cfg
    spelling is incidental and the call is the definition. The two agreed at 19 when this was
    written, which is how the shape was checked.

    Distinct from `kani-harnesses`, and the distinction is the point of having both: Kani proves
    properties of pure logic, loom searches interleavings of hand-rolled atomics, and
    `script/interleaving-check` runs only the second. A note that conflated them would be counting a
    suite nobody executes.
    """
    hits = {}
    for path in pathlib.Path('crates').rglob('*.rs'):
        n = len(re.findall(r'\bloom::model(?:\(|::Builder::new\(\))',
                           path.read_text(errors='replace')))
        if n:
            hits[path.parts[1]] = hits.get(path.parts[1], 0) + n
    return hits


def _security_audits():
    """Security audits on the record, counted from the index every one of them is filed in.

    A row in design/audit-reports/README.md's findings table that carries a **link to a report**,
    which is one per audit and is what distinguishes that table from the scale table below it: the
    two carry the same (date, kind) pairs, so counting those would double, and deduplicating them
    would silently merge two audits of one kind on one day. 2026-08-17 has two audits already.

    It is here because SECURITY.md told a reporter "four adversarial reviews are on the record" and
    pointed at four of them by name, while the index held five. That page is read by exactly the
    person we most want to have read the fifth one first, and the stale number sent them to look
    for a lens that had already been taken.
    """
    text = (pathlib.Path(RECORD) / 'design/audit-reports/README.md').read_text(errors='replace')
    return len(re.findall(r'^\| \d{4}-\d\d-\d\d \| security \|.*\]\(', text, re.M))


# The unsafe census (milestone 134 (the register of measures)), raised by calef on 2026-08-18 as one question: "how much
# unsafe code is there in a code base, and is that something we should be monitoring and driving in
# a particular direction over time?" A standalone census would have answered it with another
# one-time number nobody re-takes, which is the failure this milestone exists to fix, so it is a
# derivation here instead. See nifeos/record:notes/register-of-measures.md and nifeos/record:notes/unsafe-obligations.md.
#
# **The counting lives in `helpers/rust_source.py` and the file WALK lives here**, which is
# milestone 236's line and worth reading before moving either. `script/metrics` derives the same
# census over blobs it streams out of git at eight historical revisions, with nothing checked out,
# because AGENTS.md forbids the checkout that would be needed; this gate is asked about the tree in
# front of it and reads the working copy. Sharing the count removes the drift; sharing the walk
# would force one of those two to lie about which tree it is describing.
#
# Every regex, every exclusion and the reason for each is in that module, beside the code they
# govern rather than here.
_census = {}


def _unsafe_census():
    """Every unsafe number this tree tracks, in one pass over the source that runs on nife.

    Cached, because several numbers come out of one walk and `script/lint` runs on every build.
    The walk is about half a second over ~300 files, which is why it is one pass and not three.
    """
    if not _census:
        _census.update(rust_source.unsafe_census(_tracked_rust()))
    return _census


def _tracked_rust():
    """(path, text) for every tracked `.rs` file outside `vendor/`, read from the working tree.

    Cached for the same reason the census is: two derivations here walk it. `git ls-files` rather
    than a directory walk so an untracked scratch file cannot move a gate, and the same file set
    `script/metrics` gets from `git ls-tree` at a revision, which is what makes the two comparable
    at all.
    """
    if not _rust_files:
        names = subprocess.run(['git', 'ls-files', '*.rs', ':!vendor'],
                               capture_output=True, text=True, check=True).stdout.split()
        _rust_files.extend((name, pathlib.Path(name).read_text(errors='replace'))
                           for name in names)
    return _rust_files


_rust_files = []




def _markdown_files():
    """Markdown files the tree owns: everything but `target/` and `vendor/`.

    README.md tells a newcomer how large the corpus is, and that number rotted from 427 to 542
    without anybody noticing, because a count in prose is a claim nobody re-derives. Same argument
    counted-claims already makes everywhere else, applied to the one file a stranger reads first.

    `vendor/` is excluded for the reason it is excluded from every other sweep here: it is upstream's
    documentation, not ours, and a newcomer sent to read the corpus is not being sent there.
    """
    return sum(1 for p in pathlib.Path('.').rglob('*.md')
               if not str(p).startswith(('target/', 'vendor/')))


def _notes_files():
    """Files under `notes/`, which is what README.md calls the glossary."""
    return sum(1 for p in pathlib.Path('notes').glob('*.md'))


REGISTRY = {
    'kani-harnesses': (
        'how many Kani proof harnesses the tree carries, which is what script/verify proves',
        lambda: sum(_harness_hits().values()),
    ),
    'harness-crates': (
        'how many workspace packages carry at least one Kani proof harness',
        lambda: len(_harness_hits()),
    ),
    # The per-crate harness counts nifeos/record:notes/verification/core-harnesses.md marks. One entry per crate
    # that appendix covers, added by milestone 427 (the documentation sweep the worklist already
    # ranks) after five of its nine counts were found wrong: a count that rots silently in prose
    # had already cost two sweeps their re-derivation. A lane landing a harness in one of these
    # crates bumps the number beside the marker in the same commit, which is the forcing function
    # the total `kani-harnesses` marker already exercises.
    'memory-regions-harnesses': (
        'how many Kani proof harnesses crates/memory_regions carries',
        lambda: _harness_hits().get('memory_regions', 0),
    ),
    'page-tables-harnesses': (
        'how many Kani proof harnesses crates/page_tables carries',
        lambda: _harness_hits().get('page_tables', 0),
    ),
    'page-frames-harnesses': (
        'how many Kani proof harnesses crates/page_frames carries',
        lambda: _harness_hits().get('page_frames', 0),
    ),
    'inter-process-communication-harnesses': (
        'how many Kani proof harnesses crates/inter_process_communication carries',
        lambda: _harness_hits().get('inter_process_communication', 0),
    ),
    'address-space-identifier-harnesses': (
        'how many Kani proof harnesses crates/address_space_identifier carries',
        lambda: _harness_hits().get('address_space_identifier', 0),
    ),
    'markdown-files': (
        'how many markdown files the tree carries outside target/ and vendor/, which is the corpus '
        "README.md's reading order sends a newcomer into",
        _markdown_files,
    ),
    'notes-files': (
        'how many notes there are, which is the glossary a newcomer is told the size of',
        _notes_files,
    ),
    'sh-scripts': (
        'how many `#!/bin/sh` scripts there are under script/ and helpers/, which is the set '
        'shellcheck gates',
        _sh_scripts,
    ),
    'system_calls': (
        'how many system call numbers the ABI defines, which is the whole width of the trap',
        _abi_system_calls,
    ),
    'rights-bits': (
        'how many named single-bit rights a capability can carry (moho_abi::rights)',
        _rights_bits,
    ),
    'loom-harnesses': (
        'how many loom harnesses the tree carries, which is what script/interleaving-check runs',
        lambda: sum(_loom_hits().values()),
    ),
    'loom-crates': (
        'how many crates carry at least one loom harness',
        lambda: len(_loom_hits()),
    ),
    'security-audits': (
        'how many security audits are on the record in design/audit-reports/README.md',
        _security_audits,
    ),
    rust_source.UNSAFE_DENSITY_MARKER: (
        'how many `unsafe {}` blocks there are per 10,000 lines of code outside '
        'kernel/src/arch/, which is the unsafe that is not paying for hardware access',
        lambda: _unsafe_census()['density'],
    ),
    'unsafe-thread-safety-claims': (
        'how many `unsafe impl Send`/`Sync` claims the tree makes, each one a hand-written '
        'assertion that the compiler is wrong about a type',
        lambda: _unsafe_census()['thread_safety'],
    ),
    # The census's third population (milestone 139 (drive the unsafe count down), 2026-10-07 UTC;
    # name provisional). Its opening measurement counted `unsafe impl` as one number and the gate
    # above watched only its Send/Sync half; this is the other half, held the same way, at the
    # tree's exact value. `unsafe fn` is deliberately still not here: nifeos/record:notes/unsafe-obligations.md
    # says why, beside this marker.
    'unsafe-trait-claims': (
        'how many `unsafe impl` of an unsafe trait other than Send/Sync the tree makes, each one a '
        "hand-written assertion that a trait's contract holds for a type",
        lambda: _unsafe_census()['trait_claims'],
    ),
    # The census's fourth population, added 2026-10-12 (UTC) by milestone 891 (a mutable static
    # becomes an atomic, a lock or a recorded cell); name provisional. A ratchet ceiling, so it
    # fails in both directions: a new `static mut` stops the lane that adds it, and one converted
    # away has to be banked by lowering the marker. nifeos/record:notes/unsafe-obligations/ceilings.md has the
    # scope.
    'static-mut-declarations': (
        'how many `static mut` declarations the Rust that runs on nife makes outside its test '
        'harnesses, each one shared mutable state whose soundness argument is a comment',
        lambda: _unsafe_census()['static_mut'],
    ),
}

# --- finding the markers ------------------------------------------------------------------------
#
# `git grep` rather than a walk: it is one process, it reads only tracked files, and it skips
# binaries and anything ignored, so target/ and a stray build directory cannot slow it down or
# confuse it. vendor/ is excluded for the reason the rest of this script excludes it -- it is not
# our prose.
# The three relations, the marker shape and how its number is read are in
# `helpers/counted_claims.py`, which `script/metrics` reads a ceiling through as well.

# **A ratchet ceiling (2026-09-24): a ceiling that must also follow the tree DOWN.** An ordinary
# ceiling is silent when the tree falls below it, which is right for a quantity with headroom and
# wrong for one whose ceiling is meant to sit at the tree's exact value. `agents-md-lines` is the
# case. Its ceiling was 935 when #1189 split AGENTS.md into imperatives plus `nifeos/record:design/tenets/`
# appendices and took the file to 584 lines, and from then on the gate would have let the file
# regrow by 351 lines without a word: a fixed ceiling far above the file stops nothing. So a name in
# this set fails in BOTH directions. Above the ceiling is the old failure (take the addition out, or
# raise the ceiling with the reason beside it). Below it is new, and its only fix is to lower the
# number, so every shrink is banked and the ceiling can only move down without a written raise.
#
# The shape is `unsafe-thread-safety-claims`' (a ceiling written at the tree's exact value) with the
# slack direction closed, and the baseline stays where every counted claim's does: in the marker,
# beside the claim it counts (for `static-mut-declarations`, nifeos/record:notes/unsafe-obligations/ceilings.md;
# for `agents-md-lines`, nifeos/record:design/roadmap/0118-constitution-budget.md until 2026-10-06). Not a
# separate baseline file, because the marker already is one, and two places holding one number is
# the drift this convention exists to end. BUGS: a raise is still an ordinary edit to that marker. Nothing here compares the number
# against origin/main, because every raise on record (925 to 929, and before) was a considered act
# with its reason written beside it, and a gate that forbade them would be deleted the first time
# one was right. The raise shows in the diff; the reader of that diff is the check.
#
# Empty from 2026-10-06 to 2026-10-12 (UTC): calef dropped the line limit of milestone 118 (CLAUDE.md has a
# budget), "drop 118's limit and rely on §212's cap", so AGENTS.md is budgeted in words by the prose
# ratchet of §212 (a prose budget) and `agents-md-lines` is gone. The mechanism stays for the next ceiling that must sit at the tree's exact value.
#
# `static-mut-declarations` is that next one (milestone 891, 2026-10-12 UTC): a population of a few
# dozen that should only ever fall, where a fixed ceiling would let a converted static be quietly
# spent again.
RATCHET_CEILINGS = {'static-mut-declarations'}

grep = subprocess.run(
    ['git', '-C', RECORD, 'grep', '-n', '-e', '<!--count:', '-e', '<!--count-at-least:',
     '-e', '<!--count-at-most:', '--', ':!vendor'],
    capture_output=True, text=True,
)
# git grep exits 1 for "no matches", which is a legitimate state for a ratchet that starts empty.
if grep.returncode not in (0, 1):
    sys.stderr.write(grep.stderr)
    sys.exit(1)

bad, checked, seen = [], 0, set()
derived = {}
for path in sorted({line.split(':', 1)[0] for line in grep.stdout.splitlines() if line}):
    text = (pathlib.Path(RECORD) / path).read_text(errors='replace')
    for lineno, relation, name, claimed in counted_claims.claims(path, text):
        seen.add(name)
        if name not in REGISTRY:
            bad.append(f'{path}:{lineno}: <!--count{relation or ""}:{name}--> names no entry in '
                       f'the registry')
            continue
        if claimed is None:
            bad.append(f'{path}:{lineno}: <!--count{relation or ""}:{name}--> has no number '
                       f'before it on this line (digits, or a cardinal up to twenty)')
            continue
        if name not in derived:
            derived[name] = REGISTRY[name][1]()
        actual = derived[name]
        checked += 1
        if relation == '-at-least':
            # A floor. Only a claim that has gone FALSE is a problem; the tree growing past it is
            # the expected case and must stay silent, which is the whole point of the relation.
            if claimed > actual:
                bad.append(f'{path}:{lineno}: claims at least {claimed}, the tree has {actual} '
                           f'({name}: {REGISTRY[name][0]}). A floor is only wrong when it stops '
                           f'being true, so this means the count went DOWN')
        elif relation == '-at-most':
            # A ceiling, the floor read upside down: the tree falling below it is the wanted
            # direction and must stay silent. The message says what the two honest responses are,
            # because a ceiling that only says "no" teaches a lane to delete the marker. Raising it
            # is a legitimate answer AS LONG AS the reason is written where the number lives, which
            # is the whole mechanism: the edit is cheap and the sentence beside it is the point.
            if claimed < actual:
                bad.append(f'{path}:{lineno}: claims at most {claimed}, the tree has {actual} '
                           f'({name}: {REGISTRY[name][0]}). A ceiling is only wrong when it stops '
                           f'being true, so this means the count went UP by {actual - claimed} '
                           f'past the headroom. Take the addition back out, or raise the ceiling '
                           f'in this commit and say beside it why the addition was worth it')
            elif claimed > actual and name in RATCHET_CEILINGS:
                bad.append(f'{path}:{lineno}: claims at most {claimed}, the tree has {actual} '
                           f'({name}: {REGISTRY[name][0]}). This ceiling is a ratchet (see '
                           f'RATCHET_CEILINGS in helpers/counted_claims_check.py): the count went DOWN, so bank it by '
                           f'lowering the ceiling to {actual} in this commit')
        elif claimed != actual:
            bad.append(f'{path}:{lineno}: says {claimed}, the tree says {actual} '
                       f'({name}: {REGISTRY[name][0]})')

if bad:
    print('lint: a counted claim disagrees with the tree:', file=sys.stderr)
    for entry in bad:
        print(f'  {entry}', file=sys.stderr)
    print('', file=sys.stderr)
    print('Fix the number, or fix the derivation in helpers/counted_claims_check.py if the tree is right and the gate '
          'is asking the wrong question. See nifeos/record:notes/counted-claims.md.', file=sys.stderr)
    sys.exit(1)

unused = sorted(set(REGISTRY) - seen)
extra = f'; {len(unused)} registered and unmarked ({", ".join(unused)})' if unused else ''
print(f'counted claims: {checked} markers over {len(derived)} counts, all agreeing with the tree'
      f'{extra}')

# The two unsafe numbers that are REPORTED rather than asserted, and the distinction is milestone
# 134's rule: a number with a consumer gets a relation, a number with only a reader gets printed.
#
# `kernel/src/arch/` deliberately has no ceiling. Driving that number down means either writing
# assembly wrong or moving it out of arch/, and DECISIONS rule 1 says arch code belongs there, so a
# target would be a gate pushing against the architecture. But an unmarked number in a note is a
# snapshot of whenever somebody last counted, which is this whole convention's founding complaint,
# so it is printed on every build instead: on screen every time, asserted never.
if _census:
    print(f'unsafe census: {_census["outside_arch"]} blocks in {_census["code_lines"]} lines '
          f'outside kernel/src/arch/, {_census["density"]} per 10,000 (ceiling); '
          f'{_census["inside_arch"]} blocks inside arch/ (no target: rule 1 puts assembly there); '
          f'{_census["thread_safety"]} Send/Sync claims (ceiling); '
          f'{_census["trait_claims"]} other unsafe trait impls (ceiling); '
          f'{_census["static_mut"]} static mut declarations (ceiling, follows the tree down). '
          f'See nifeos/record:notes/register-of-measures.md')
