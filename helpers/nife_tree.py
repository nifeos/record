#!/usr/bin/env python3
"""helpers/nife_tree.py: nife's tree at the commit basalt pins, for the record's lint.

    helpers/nife_tree.py commit            print the nife commit basalt's main pins
    helpers/nife_tree.py path              print a checkout of nife at that commit
    helpers/nife_tree.py history           print a git directory holding nife's history to that commit
    helpers/nife_tree.py overlay <root>    link into <root> every nife path <root> lacks
    helpers/nife_tree.py unoverlay <root>  remove the links `overlay` made
    helpers/nife_tree.py --selftest        prove the overlay hides, isolates and removes its links

The record names code that lives in nife: a roadmap block's `**Recorded.**` line names
`script/lint`, a citation names `xtask/src/host.rs`, a counted claim counts the kernel's harnesses.
Those names are checked against nife at the commit basalt's `main` pins, which is the rule
`helpers/qualified_paths.py` already follows for a `nifeos/<repo>:<path>` citation. It is the only
nife the record can name and have every reader see the same thing.

`path` prints `$NIFE_TREE` when it is set (CI checks nife out there, at `commit`), and otherwise a
checkout kept under `$NIFE_PINNED_TREES` (default `~/.cache/nife/pinned-trees`), fetched once per
pinned commit. A `$NIFE_TREE` at another commit is refused, because a check against the wrong nife
passes or fails for the wrong reason.

`history` prints a git directory that holds every commit of nife up to and including `commit`,
with their trees and without their file contents: `$NIFE_HISTORY` when it is set (a full clone,
which is refused if it is shallow or lacks the commit), and otherwise a bare blobless clone kept as
`nife-history.git` under the same cache, fetched once and then only by what a new pin adds. That
is enough for `git log --no-renames --name-only <commit>` and `git ls-tree -r <commit>`, which is
what `script/audits --worklist` asks of it. A commit's history never changes, so a log read at the
pin is the same on every machine. Run such a log with `GIT_NO_LAZY_FETCH=1`, because rename
detection or a content read would otherwise fetch blobs one at a time over the network.

`overlay` is what lets the record's checks, written when the record was half of nife's tree, run
unchanged: for each path nife tracks and the record does not, it puts a symbolic link in the
record's working tree, and names each link in the repository's `info/exclude` between two marker
lines (one block per worktree, since worktrees share the file), so git (status, grep, ls-files)
never sees them. A path the record has is never shadowed.
`unoverlay` removes the links listed there and the block, and any other untracked link in the tree
that points into a nife tree (what a run killed outright leaves). `script/lint` makes the overlay at
its start and removes it at its end, including on failure or interruption.
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qualified_paths  # noqa: E402

BEGIN = "# >>> helpers/nife_tree.py overlay: links into nife's tree, removed by unoverlay"
END = "# <<< helpers/nife_tree.py overlay"
# git refuses to read these through a link, and the record keeps its own.
NEVER_LINKED = {".gitignore", ".gitattributes", ".git"}


def _git(*args, cwd=None, check=True):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode:
        sys.exit(f"nife_tree: git {' '.join(args)}: {r.stderr.strip() or 'failed'}")
    return r.stdout.strip()


def commit():
    try:
        pins = qualified_paths._pins()
    except RuntimeError as e:
        sys.exit(f"nife_tree: cannot read basalt's pins.toml: {e}")
    if "nife" not in pins:
        sys.exit("nife_tree: basalt's pins.toml on main pins no nifeos/nife")
    return pins["nife"]


def path():
    want = commit()
    tree = os.environ.get("NIFE_TREE")
    if tree:
        have = _git("-C", tree, "rev-parse", "HEAD")
        if have != want:
            sys.exit(f"nife_tree: $NIFE_TREE ({tree}) is at {have[:12]}, and basalt's main pins "
                     f"nife at {want[:12]}. Check out that commit there, or unset NIFE_TREE.")
        return os.path.abspath(tree)
    tree = os.path.join(qualified_paths._cache_dir(), f"nife-tree-{want}")
    if os.path.isfile(os.path.join(tree, ".nife-tree-complete")):
        return tree
    tmp = tree + f".partial-{os.getpid()}"
    _git("init", "-q", tmp)
    _git("-C", tmp, "fetch", "-q", "--depth=1",
         f"https://github.com/{qualified_paths.ORGANIZATION}/nife", want)
    _git("-C", tmp, "checkout", "-q", "--detach", "FETCH_HEAD")
    open(os.path.join(tmp, ".nife-tree-complete"), "w").close()
    _read_only(tmp)
    try:
        os.rename(tmp, tree)
    except OSError:
        subprocess.run(["rm", "-rf", tmp])
    return tree


def _has_commit(where, sha):
    return subprocess.run(["git", *where, "cat-file", "-e", f"{sha}^{{commit}}"],
                          capture_output=True,
                          env=dict(os.environ, GIT_NO_LAZY_FETCH="1")).returncode == 0


def history(want=None):
    want = want or commit()
    have = os.environ.get("NIFE_HISTORY")
    if have:
        if _git("-C", have, "rev-parse", "--is-shallow-repository") != "false":
            sys.exit(f"nife_tree: $NIFE_HISTORY ({have}) is a shallow clone, so its log stops "
                     f"short. Fetch it whole, or unset NIFE_HISTORY.")
        if not _has_commit(["-C", have], want):
            sys.exit(f"nife_tree: $NIFE_HISTORY ({have}) lacks {want[:12]}, basalt main's nife "
                     f"pin. Fetch it there, or unset NIFE_HISTORY.")
        return _git("-C", have, "rev-parse", "--path-format=absolute", "--git-dir")
    git_dir = os.path.join(qualified_paths._cache_dir(), "nife-history.git")
    if not os.path.isdir(git_dir):
        tmp = git_dir + f".partial-{os.getpid()}"
        _git("init", "-q", "--bare", tmp)
        try:
            os.rename(tmp, git_dir)
        except OSError:
            subprocess.run(["rm", "-rf", tmp])
    if not _has_commit(["--git-dir", git_dir], want):
        _git("--git-dir", git_dir, "fetch", "-q", "--no-write-fetch-head", "--filter=blob:none",
             f"https://github.com/{qualified_paths.ORGANIZATION}/nife", f"{want}:refs/pins/{want}")
    return git_dir


def _read_only(tree):
    """Take the write bits off the checkout, outside .git, so a write through a link fails loudly.

    An editor or a `cp` that meets one of the overlay's links in the record's tree would otherwise
    write into this shared checkout and change what every later run reads. `chmod -R u+w` on it
    before removing it.
    """
    for top, dirs, files in os.walk(tree):
        if top == tree and ".git" in dirs:
            dirs.remove(".git")
        for name in files:
            p = os.path.join(top, name)
            if not os.path.islink(p):
                os.chmod(p, os.stat(p).st_mode & ~0o222)
        if top != tree:
            os.chmod(top, os.stat(top).st_mode & ~0o222)


def _exclude_file(root):
    return _git("-C", root, "rev-parse", "--path-format=absolute", "--git-path", "info/exclude")


def _markers(root):
    """The two marker lines of this worktree's block.

    The exclude file lives in the repository's common directory, so every worktree of the record
    shares one. Each worktree therefore gets a block of its own, named by its root, and one run
    never rewrites or drops another's.
    """
    return f"{BEGIN} [{root}]", f"{END} [{root}]"


def _read_block(exclude, root):
    begin, end = _markers(root)
    try:
        with open(exclude) as f:
            lines = f.read().split("\n")
    except FileNotFoundError:
        return [], []
    keep, block, inside = [], [], False
    for line in lines:
        if line == begin:
            inside = True
        elif line == end:
            inside = False
        elif inside:
            block.append(line)
        else:
            keep.append(line)
    return keep, block


def _nife_roots():
    """Directories a link made by an overlay can point into, without fetching anything."""
    roots = [os.path.realpath(qualified_paths._cache_dir())]
    if os.environ.get("NIFE_TREE"):
        roots.append(os.path.realpath(os.environ["NIFE_TREE"]))
    return roots


def _sweep(root):
    """Remove every untracked link in <root> that points into a nife tree, whatever pin or run.

    A run that was killed outright (SIGKILL, a power cut) never ran its cleanup, and its block may
    have been lost with the exclude file. The links are recognizable by where they point, and an
    untracked link that points there is never the record's own.
    """
    out = subprocess.run(["git", "-C", root, "ls-files", "-o", "-z"],
                         capture_output=True, text=True).stdout
    roots = _nife_roots()
    for rel in out.split("\0"):
        p = os.path.join(root, rel)
        if rel and os.path.islink(p):
            target = os.path.realpath(p)
            if any(target == r or target.startswith(r + os.sep) for r in roots):
                os.unlink(p)


def _write_exclude(exclude, root, keep, links):
    begin, end = _markers(root)
    text = "\n".join(keep).rstrip("\n") + "\n"
    if links is not None:
        text += begin + "\n" + "".join("/" + rel + "\n" for rel in sorted(links)) + end + "\n"
    with open(exclude, "w") as f:
        f.write(text)


def unoverlay(root):
    root = os.path.abspath(root)
    exclude = _exclude_file(root)
    keep, block = _read_block(exclude, root)
    for entry in block:
        rel = entry.lstrip("/")
        p = os.path.join(root, rel)
        if rel and os.path.islink(p):
            os.unlink(p)
    _sweep(root)
    if os.path.exists(exclude):
        _write_exclude(exclude, root, keep, None)


def overlay(root):
    root = os.path.abspath(root)
    unoverlay(root)
    nife = path()
    files = _git("-C", nife, "ls-files", "-z").split("\0")
    links = set()
    for f in files:
        if not f:
            continue
        parts = f.split("/")
        if parts[0] == ".git" or parts[-1] in NEVER_LINKED:
            continue
        for i in range(1, len(parts) + 1):
            rel = "/".join(parts[:i])
            here = os.path.join(root, rel)
            if not os.path.lexists(here):
                links.add(rel)
                break
            if os.path.islink(here) or not os.path.isdir(here):
                break
    exclude = _exclude_file(root)
    os.makedirs(os.path.dirname(exclude), exist_ok=True)
    keep, _ = _read_block(exclude, root)
    _write_exclude(exclude, root, keep, links)
    for rel in sorted(links):
        os.symlink(os.path.join(nife, rel), os.path.join(root, rel))
    print(f"nife_tree: {len(links)} nife paths linked into the record's tree from "
          f"{commit()[:12]}, basalt main's nife pin")


def selftest():
    """Two worktrees of a scratch repository and a fake nife tree: the overlay hides its links,
    two worktrees never disturb each other, and unoverlay removes every link even after a lost
    block."""
    import contextlib
    import io
    import shutil
    import tempfile

    global commit
    work = os.path.realpath(tempfile.mkdtemp(prefix="nife-tree-selftest."))
    saved = {k: os.environ.get(k) for k in ("NIFE_TREE", "NIFE_PINNED_TREES")}
    real_commit = commit
    ident = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    def git(*a, cwd):
        subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True,
                       env={**os.environ, **ident})

    def status(where):
        return subprocess.run(["git", "-C", where, "status", "--porcelain"],
                              capture_output=True, text=True).stdout

    def fail(msg):
        sys.exit(f"nife_tree selftest: {msg}")

    try:
        fake = os.path.join(work, "nife")
        os.makedirs(os.path.join(fake, "dir"))
        for f in ("only_in_nife.txt", "dir/deep.txt", "shared.txt"):
            open(os.path.join(fake, f), "w").write("x")
        git("init", "-q", cwd=fake)
        git("add", "-A", cwd=fake)
        git("commit", "-qm", "x", cwd=fake)
        commit_id = _git("-C", fake, "rev-parse", "HEAD")
        record = os.path.join(work, "record")
        os.makedirs(record)
        git("init", "-q", cwd=record)
        open(os.path.join(record, "shared.txt"), "w").write("own")
        git("add", "-A", cwd=record)
        git("commit", "-qm", "x", cwd=record)
        other = os.path.join(work, "other")
        git("worktree", "add", "-q", "-b", "o", other, cwd=record)
        os.environ["NIFE_TREE"] = fake
        os.environ["NIFE_PINNED_TREES"] = os.path.join(work, "cache")
        commit = lambda: commit_id  # noqa: E731
        for where in (record, other):
            with contextlib.redirect_stdout(io.StringIO()):
                overlay(where)
            if not os.path.islink(os.path.join(where, "only_in_nife.txt")):
                fail("the overlay linked nothing")
            if os.path.islink(os.path.join(where, "shared.txt")):
                fail("the overlay shadowed a record file")
            if status(where):
                fail(f"git sees the overlay's links in {where}: {status(where)!r}")
        unoverlay(other)
        if os.path.lexists(os.path.join(other, "dir")) or status(other):
            fail("unoverlay left something in the second worktree")
        if not os.path.islink(os.path.join(record, "dir")) or status(record):
            fail("another worktree's unoverlay disturbed the first one")
        # A killed run: the block is gone, the links remain.
        open(_exclude_file(record), "w").close()
        if "only_in_nife.txt" not in status(record):
            fail("the stale links were not visible to git, so the test proves nothing")
        with contextlib.redirect_stdout(io.StringIO()):
            overlay(record)
        unoverlay(record)
        if status(record) or os.path.lexists(os.path.join(record, "only_in_nife.txt")):
            fail("unoverlay left a stale link behind")
    finally:
        commit = real_commit
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(work, ignore_errors=True)
    print("nife_tree selftest: ok")


def main(argv):
    if argv[:1] == ["commit"] and len(argv) == 1:
        print(commit())
    elif argv[:1] == ["path"] and len(argv) == 1:
        print(path())
    elif argv[:1] == ["history"] and len(argv) == 1:
        print(history())
    elif argv[:1] == ["overlay"] and len(argv) == 2:
        overlay(argv[1])
    elif argv[:1] == ["unoverlay"] and len(argv) == 2:
        unoverlay(argv[1])
    elif argv == ["--selftest"]:
        selftest()
    else:
        sys.exit(__doc__.split("\n\n")[1])


if __name__ == "__main__":
    main(sys.argv[1:])
