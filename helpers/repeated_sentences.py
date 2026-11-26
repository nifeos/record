"""The one-home check: a long sentence in two Markdown files is a copy, and a new copy fails.

Each rule or fact has one home, and every other file links to it (decided 2026-11-26 UTC,
nifeos/record#50). The rule is stated in design/tenets/documentation-standard.md, "One home for
each rule or fact". This holds the record to it: a sentence of 100 or more characters, after
whitespace is normalized, that appears in more than one Markdown file under `design/` and `notes/`
fails, unless `design/repeated-sentence-baseline.txt` lists that copy.

    python3 helpers/repeated_sentences.py --check      # what script/lint runs
    python3 helpers/repeated_sentences.py --report     # every listed sentence and its files, most copies first
    python3 helpers/repeated_sentences.py --bank       # drop the rows of copies that are gone
    python3 helpers/repeated_sentences.py --selftest   # the rules, as fixtures

Name: provisional, minted 2026-11-26 (UTC) by lane/one-home-rule. A shared helper under
`helpers/`, which `script/names` puts out of its own scope, so this paragraph is the record.
`repeated_sentences` for what it finds. calef has not named it.

**A copy.** A document's prose splits into blocks (paragraphs, list items, headings, table cells)
before it splits into sentences, by the prose ratchet's own splitter (`helpers/prose_ratchet.py`),
so a sentence never runs across a block. A link counts as its text, because two files that cite the
same page through different relative paths still say the same thing, and emphasis (`*`) is
dropped, so taking the italics off a sentence does not make it new. A sentence of at least
`MINIMUM` characters that appears in two files is a copy in each of them. A sentence repeated
inside one file is not this check's business.

**What may repeat, each for a stated reason.**

- A block quote (`>` lines). It quotes its source verbatim, and the quotation is the point.
- Front matter. It is fields a script reads, not prose.
- A table's header row. Two tables of one shape share their columns by design.
- A fenced code block. A command or a transcript repeats where each task needs it, and it is not
  rewritten into a link without losing the example.
- An HTML comment. An exception marker sits in the document it waives, by the rule that made it.
- A `Name:` paragraph. Each document carries its own provenance (nifeos/record:design/naming.md),
  so two that read alike state two facts about two files, and a link cannot stand in for either.
  Measured 2026-11-26: 15 sentences and 70 copies.

A citation's gloss is not exempt: the sentence around it is the writer's, and a dependency
restated in seventeen files is the drift this rule exists to stop.

**The baseline.** A row is `<hash> <path>`: the first 12 hex digits of the SHA-256 of the
normalized sentence, then a file that holds it. Rows sort by hash, so a sentence's copies sit
together, and `--report` prints the sentence behind each hash. The layout is
`helpers/baseline_layout.py`'s: a blank line after every row.

- A copy the list does not hold fails. Link to the sentence's home instead of restating it.
- A row with no copy behind it fails until it is removed, so the list cannot go stale. `--bank`
  removes it. A sentence left in one file is no longer a copy, and its last row goes too.
- Against the merge base a sentence's rows may not grow in number, and a sentence the base list
  does not hold may not appear. A file that moves takes its rows along: the count is per sentence,
  so a rename or a split passes once `--bank` re-keys the rows.
- A selection that matches no file fails, because a gate that judges nothing passes.
"""

import collections
import hashlib
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import baseline_layout  # noqa: E402
import prose_ratchet  # noqa: E402

BASELINE = 'design/repeated-sentence-baseline.txt'
SCOPE = ('design/', 'notes/')
MINIMUM = 100
HOME = 'design/tenets/documentation-standard.md ("One home for each rule or fact")'
FORMAT = '# format 1: one row per copy of a sentence of 100 or more characters'

HEADER = FORMAT + """
# The one-home check's baseline: helpers/repeated_sentences.py, whose header is the manual. One row
# per copy that existed when the rule was made (decided 2026-11-26 UTC): `<hash> <path>`, the hash
# of a sentence and a Markdown file under design/ or notes/ that holds it. The list only shrinks.
# A change that folds a copy into a link removes its row (`python3 helpers/repeated_sentences.py
# --bank` does it); `--report` prints the sentence behind each hash.
# Layout (helpers/baseline_layout.py): rows sorted, a blank line after every row.
"""

TABLE_SEPARATOR = re.compile(r'^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$')
NAME_PARAGRAPH = re.compile(r'^[*_]*Name:')


# --- reading a document ---------------------------------------------------------------------------

def blocks(text):
    """The prose blocks of a document, with every exemption in the header already out."""
    lines = list(prose_ratchet.prose_lines(text))  # front matter, comments and fenced code out
    out, cur = [], []

    def flush():
        if cur:
            out.append(' '.join(cur))
            cur.clear()

    for i, line in enumerate(lines):
        if not line.strip() or prose_ratchet.QUOTE_LINE.match(line):
            flush()
        elif prose_ratchet.TABLE_ROW.match(line):
            flush()
            following = lines[i + 1] if i + 1 < len(lines) else ''
            if TABLE_SEPARATOR.match(line) or TABLE_SEPARATOR.match(following):
                continue  # the separator, and the header row above it
            out.extend(cell.strip() for cell in line.strip().strip('|').split('|'))
        elif prose_ratchet.HEADING.match(line):
            flush()
            out.append(line.strip().lstrip('#').strip())
        elif prose_ratchet.LIST_ITEM.match(line):
            flush()
            cur.append(prose_ratchet.LIST_ITEM.sub('', line, count=1).strip())
        else:
            cur.append(line.strip())
    flush()
    return [b for b in out if b and not NAME_PARAGRAPH.match(b)]


def sentences(block):
    """The block's sentences of at least MINIMUM characters, whitespace normalized."""
    s = ' '.join(prose_ratchet.LINK.sub(r'\1', block).replace('*', '').split())
    pieces, start = [], 0
    for m in prose_ratchet.SENTENCE_END.finditer(s):
        before = s[:m.start() + 1].split()
        if before and before[-1].lower().lstrip('(') in prose_ratchet.ABBREVIATIONS:
            continue
        pieces.append(s[start:m.end()].strip())
        start = m.end()
    pieces.append(s[start:].strip())
    return [p for p in pieces if len(p) >= MINIMUM]


def digest(sentence):
    return hashlib.sha256(sentence.encode()).hexdigest()[:12]


def copies(texts):
    """`(rows, said)` for `{path: text}`: a Counter of `<hash> <path>` rows, one per copy, and
    the sentence behind each hash."""
    where, said = collections.defaultdict(set), {}
    for path, text in texts.items():
        for block in blocks(text):
            for sentence in sentences(block):
                h = digest(sentence)
                said[h] = sentence
                where[h].add(path)
    rows = collections.Counter(f'{h} {p}' for h, paths in where.items() if len(paths) > 1
                               for p in paths)
    return rows, {h: said[h] for h, paths in where.items() if len(paths) > 1}


def per_sentence(rows):
    out = collections.Counter()
    for row, n in rows.items():
        out[row.split(' ', 1)[0]] += n
    return out


# --- the tree and git -----------------------------------------------------------------------------

def git(*args):
    r = subprocess.run(('git',) + args, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def tree_texts():
    """Every Markdown file in scope in the working tree, untracked files included.

    A symbolic link is skipped: script/lint links nife's tree into this one for its run, and those
    links are nife's documents, not the record's.
    """
    listed = git('ls-files', '-z', '--cached', '--others', '--exclude-standard', '--', *SCOPE) or ''
    root = os.path.realpath('.')
    texts = {}
    for p in sorted(set(listed.split('\0'))):
        if not p.endswith('.md') or not os.path.isfile(p):
            continue
        if not os.path.realpath(p).startswith(root + os.sep):
            continue
        with open(p, encoding='utf-8', errors='replace') as f:
            texts[p] = f.read()
    return texts


def read_baseline(text):
    return baseline_layout.rows_of(text)


def merge_base():
    base = (git('merge-base', 'HEAD', 'origin/main') or '').strip()
    head = (git('rev-parse', 'HEAD') or '').strip()
    return base if base and base != head else None


def base_rows():
    """The merge base's rows, or None where the base holds no baseline of this format."""
    base = merge_base()
    old = git('show', f'{base}:{BASELINE}') if base else None
    if old is None or FORMAT not in old.splitlines():
        return None
    return read_baseline(old)


# --- the rules, pure so the selftest can drive them -----------------------------------------------

def shorten(sentence, width=110):
    return sentence if len(sentence) <= width else sentence[:width - 3].rstrip() + '...'


def problems(judged, tree, said, rows, base=None):
    """Every failure. `judged` counts the files read; `base` is None where the base has no list."""
    if not judged:
        return ['the check read no Markdown file at all. A selector that matches nothing passes by '
                'checking nothing (nifeos/record:design/roadmap/0401-a-gate-that-selects-the-set-it-judges.md)']
    bad = []
    new = tree - rows
    holders = collections.defaultdict(list)
    for row in tree:
        h, path = row.split(' ', 1)
        holders[h].append(path)
    for h in sorted({row.split(' ', 1)[0] for row in new}):
        paths = sorted({row.split(' ', 1)[1] for row in new if row.startswith(h + ' ')})
        others = sorted(set(holders[h]) - set(paths)) or sorted(holders[h])
        named = ', '.join(others[:3]) + (f' and {len(others) - 3} more' if len(others) > 3 else '')
        bad.append(f'{", ".join(paths)}: a new copy of a sentence that {named} also '
                   f'holds: "{shorten(said[h])}" ({h}). State it once, in its home, and link to '
                   f'that file from here instead of restating it')
    for row, n in sorted((rows - tree).items()):
        bad.append(f'{BASELINE}: {row} has no copy behind it{f" ({n} rows)" if n > 1 else ""}. '
                   f'Remove it (--bank); the list cannot go stale')
    if base is not None:
        before, now = per_sentence(base), per_sentence(rows)
        for h in sorted(now):
            if now[h] > before[h]:
                was = f'{before[h]} copies' if before[h] else 'none'
                bad.append(f'{BASELINE}: {h} lists {now[h]} copies against {was} at the merge base. '
                           f'The list only shrinks; link to the home instead of adding a copy')
    return bad


def banked(old, tree):
    """The rows `--bank` writes: the tree's copies of each listed sentence, never more of them
    than the list held. A sentence whose copies grew keeps only its listed rows, so the new copy
    still fails; one whose copies moved takes their new paths."""
    held = per_sentence(old)
    out = collections.Counter()
    by_sentence = collections.defaultdict(collections.Counter)
    for row, n in tree.items():
        by_sentence[row.split(' ', 1)[0]][row] += n
    for h, rows in by_sentence.items():
        if not held[h]:
            continue
        if sum(rows.values()) <= held[h]:
            out += rows
        else:
            out += rows & old
    return out


# --- the verbs ------------------------------------------------------------------------------------

def write_baseline(rows):
    old = open(BASELINE).read() if os.path.exists(BASELINE) else None
    text = (baseline_layout.rewrite(old, HEADER, rows) if old is not None
            else baseline_layout.spaced(HEADER, rows))
    with open(BASELINE, 'w') as f:
        f.write(text)


def run_check():
    if not os.path.exists(BASELINE):
        print(f'repeated sentences: {BASELINE} is missing. The gate and its list are one change; '
              f'deleting one deletes the gate', file=sys.stderr)
        return 1
    texts = tree_texts()
    tree, said = copies(texts)
    text = open(BASELINE).read()
    rows = read_baseline(text)
    bad = baseline_layout.problems(text, BASELINE) + problems(texts, tree, said, rows, base_rows())
    if bad:
        print('repeated sentences: each rule or fact has one home, and every other file links to '
              f'it ({HOME}):', file=sys.stderr)
        for b in bad:
            print(f'  {b}', file=sys.stderr)
        print('\nThe home is the file that owns the subject; `python3 helpers/repeated_sentences.py '
              '--report` lists every copy with its sentence.', file=sys.stderr)
        return 1
    print(f'repeated sentences: {len(texts)} Markdown files, {len(per_sentence(tree))} sentences of '
          f'{MINIMUM} or more characters in more than one file, {sum(tree.values())} copies, all '
          f'held by the baseline')
    return 0


def bank():
    if not os.path.exists(BASELINE):
        print(f'repeated sentences: {BASELINE} does not exist; there is nothing to bank',
              file=sys.stderr)
        return 2
    tree, _said = copies(tree_texts())
    rows = banked(read_baseline(open(BASELINE).read()), tree)
    write_baseline(rows)
    print(f'repeated sentences: {sum(rows.values())} rows written to {BASELINE}')
    return 0


def report():
    tree, said = copies(tree_texts())
    by_sentence = collections.defaultdict(list)
    for row in sorted(tree):
        h, path = row.split(' ', 1)
        by_sentence[h].append(path)
    print(f'{len(by_sentence)} sentences, {sum(tree.values())} copies')
    for h, paths in sorted(by_sentence.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        print(f'\n{h} in {len(paths)} files: {said[h]}')
        for p in paths:
            print(f'  {p}')
    print('\nfiles with the most copies:')
    per_file = collections.Counter(row.split(' ', 1)[1] for row in tree.elements())
    for path, n in per_file.most_common(20):
        print(f'  {n:4} {path}')
    return 0


def selftest():
    long_a = 'This sentence states a rule that matters to every reader of the record, at a length well over one hundred characters.'
    long_b = 'A second sentence of the same kind, long enough to count, which a writer might paste into another file by habit alone.'
    assert len(long_a) >= MINIMUM and len(long_b) >= MINIMUM
    ha, hb = digest(long_a), digest(long_b)

    def tree(texts):
        return copies(texts)

    rows = collections.Counter
    two = {'design/a.md': long_a + '\n', 'notes/b.md': 'Intro.\n\n' + long_a + '\n'}
    t2, s2 = tree(two)
    cases = [
        ('a long sentence in two files is a copy in each', t2 == rows([f'{ha} design/a.md', f'{ha} notes/b.md'])),
        ('a sentence under the minimum is not', not tree({'a.md': 'Short.', 'b.md': 'Short.'})[0]),
        ('a sentence twice in one file is not', not tree({'a.md': long_a + ' ' + long_a})[0]),
        ('whitespace and wrapping do not hide a copy',
         bool(tree({'a.md': long_a, 'b.md': long_a.replace(' ', '\n', 3).replace('rule', 'rule  ')})[0])),
        ('emphasis does not hide a copy', bool(tree({'a.md': f'*{long_a}*', 'b.md': long_a})[0])),
        ('a link counts as its text',
         bool(tree({'a.md': long_a.replace('record', '[record](../x.md)'),
                    'b.md': long_a.replace('record', '[record](x.md)')})[0])),
        ('a block quote may repeat', not tree({'a.md': '> ' + long_a, 'b.md': '> ' + long_a})[0]),
        ('front matter may repeat',
         not tree({'a.md': f'---\nnote: {long_a}\n---\n\nBody.', 'b.md': f'---\nnote: {long_a}\n---\n'})[0]),
        ('a fenced code block may repeat',
         not tree({'a.md': f'```\n{long_a}\n```\n', 'b.md': f'```\n{long_a}\n```\n'})[0]),
        ('an HTML comment may repeat', not tree({'a.md': f'<!-- {long_a} -->', 'b.md': f'<!-- {long_a} -->'})[0]),
        ('a Name: paragraph may repeat',
         not tree({'a.md': f'*Name: {long_a}*', 'b.md': f'*Name: {long_a}*'})[0]),
        ('a table header row may repeat',
         not tree({'a.md': f'| {long_a} | b |\n|---|---|\n| x | y |\n',
                   'b.md': f'| {long_a} | b |\n|---|---|\n| z | w |\n'})[0]),
        ('a table body cell is prose',
         bool(tree({'a.md': f'| h | i |\n|---|---|\n| {long_a} | y |\n',
                    'b.md': f'| h | i |\n|---|---|\n| {long_a} | w |\n'})[0])),
        ('a list item is prose', bool(tree({'a.md': f'- {long_a}', 'b.md': f'1. {long_a}'})[0])),
        ('a sentence never runs across blocks',
         tree({'a.md': 'Opening words of a paragraph\n\n' + long_b,
               'b.md': 'Other words of another one\n\n' + long_b})[0]
         == rows([f'{hb} a.md', f'{hb} b.md'])),
    ]
    files = set(two)
    cases += [
        ('listed copies pass', not problems(files, t2, s2, t2, t2)),
        ('a new copy fails', bool(problems(files, t2, s2, rows()))),
        ('a third copy beside two listed fails',
         bool(problems(files, t2 + rows([f'{ha} notes/c.md']), s2, t2, t2))),
        ('a row with no copy behind it fails', bool(problems(files, rows(), s2, t2, t2))),
        ('a row added against the merge base fails',
         bool(problems(files, t2 + rows([f'{ha} notes/c.md']), s2, t2 + rows([f'{ha} notes/c.md']), t2))),
        ('a moved copy passes once banked',
         not problems(files, rows([f'{ha} design/a.md', f'{ha} notes/moved.md']), s2,
                      banked(t2, rows([f'{ha} design/a.md', f'{ha} notes/moved.md'])), t2)),
        ('--bank never admits a new copy',
         banked(t2, t2 + rows([f'{ha} notes/c.md'])) == t2),
        ('--bank drops a sentence left in one file', banked(t2, rows()) == rows()),
        ('--bank never admits a sentence the list did not hold',
         banked(t2, t2 + rows([f'{hb} a.md', f'{hb} b.md'])) == t2),
        ('a selector that matches nothing fails loudly', bool(problems(set(), rows(), {}, rows()))),
    ]
    msg = problems(files, t2, s2, rows())[0]
    cases.append(('the failure names the files, the sentence and the remedy',
                  'design/a.md' in msg and 'notes/b.md' in msg and long_a[:40] in msg and 'link' in msg))
    failed = [name for name, ok in cases if not ok]
    if not baseline_layout.problems('# h\na\nb\n\n', 'f'):
        failed.append('rows on adjacent lines pass the layout check')
    for name in failed:
        print(f'repeated sentences selftest: {name}', file=sys.stderr)
    if not failed:
        print(f'repeated sentences selftest: {len(cases)} cases pass')
    return 1 if failed else 0


def main(argv):
    root = git('rev-parse', '--show-toplevel')
    if root:
        os.chdir(root.strip())
    if argv and argv[0] == '--selftest':
        return selftest()
    if not argv or argv[0] == '--check':
        return run_check()
    if argv[0] == '--bank':
        return bank()
    if argv[0] == '--report':
        return report()
    # The option keeps its command-line abbreviation, `--init`; the code behind it spells `initialize`
    # (nifeos/record:design/naming/command-line-names.md).
    if argv[0] == '--init' and not os.path.exists(BASELINE):
        tree, _said = copies(tree_texts())
        write_baseline(tree)
        print(f'repeated sentences: wrote {sum(tree.values())} rows to {BASELINE}')
        return 0
    print(__doc__.split('\n\n')[1], file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
