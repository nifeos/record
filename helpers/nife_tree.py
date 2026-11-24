#!/usr/bin/env python3
"""helpers/nife_tree.py: nife's tree at the commit basalt pins, for the record's lint.

    helpers/nife_tree.py commit            print the nife commit basalt's main pins
    helpers/nife_tree.py path              print a checkout of nife at that commit
    helpers/nife_tree.py history           print a git directory holding nife's history to that commit
    helpers/nife_tree.py overlay <root>    link into <root> every nife path <root> lacks
    helpers/nife_tree.py unoverlay <root>  remove the links `overlay` made

The record names code that lives in nife: a roadmap block's `**Recorded.**` line names
`script/lint`, a citation names `xtask/src/host.rs`, a counted claim counts the kernel's harnesses.
Those names are checked against nife at the commit basalt's `main` pins, which is the rule
`helpers/qualified_paths.py` already follows for a `partsfoundry/<repo>:<path>` citation. It is the only
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
lines, so git (status, grep, ls-files) never sees them. A path the record has is never shadowed.
`unoverlay` removes exactly the links listed there and the block. `script/lint` makes the overlay at
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
        sys.exit("nife_tree: basalt's pins.toml on main pins no partsfoundry/nife")
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


def _read_block(exclude):
    try:
        with open(exclude) as f:
            lines = f.read().split("\n")
    except FileNotFoundError:
        return [], []
    keep, block, inside = [], [], False
    for line in lines:
        if line == BEGIN:
            inside = True
        elif line == END:
            inside = False
        elif inside:
            block.append(line)
        else:
            keep.append(line)
    return keep, block


def unoverlay(root):
    root = os.path.abspath(root)
    exclude = _exclude_file(root)
    keep, block = _read_block(exclude)
    for entry in block:
        rel = entry.lstrip("/")
        p = os.path.join(root, rel)
        if rel and os.path.islink(p):
            os.unlink(p)
    if os.path.exists(exclude):
        with open(exclude, "w") as f:
            f.write("\n".join(keep).rstrip("\n") + "\n")


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
    keep, _ = _read_block(exclude)
    with open(exclude, "w") as f:
        f.write("\n".join(keep).rstrip("\n") + "\n" + BEGIN + "\n")
        for rel in sorted(links):
            f.write("/" + rel + "\n")
        f.write(END + "\n")
    for rel in sorted(links):
        os.symlink(os.path.join(nife, rel), os.path.join(root, rel))
    print(f"nife_tree: {len(links)} nife paths linked into the record's tree from "
          f"{commit()[:12]}, basalt main's nife pin")


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
    else:
        sys.exit(__doc__.split("\n\n")[1])


if __name__ == "__main__":
    main(sys.argv[1:])
