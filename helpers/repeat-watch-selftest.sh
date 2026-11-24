#!/bin/sh
#
# Selftest: .github/workflows/repeat-watch.yml asks about the record's own scheduled workflows and
# files in the record, through nife's code. Run by script/lint, with nife's tree linked in.
#
# The repeat half and the issue filer are nife's (helpers/trunk-health.sh and
# helpers/repeat_issue.py, linked by helpers/nife_tree.py), and nife's own selftest proves their
# thresholds, the log strip and the issue rules. What only this tree can prove is the wiring: that
# here, with nife's workflow files linked in beside the record's, the half asks this repository
# about exactly the workflows the record tracks and schedules, and that its REPEAT rows open issues
# in this repository. A stub `gh` logs every call and answers every run list with four failures on
# one line, so any workflow the half asked about would print a row; no network.
#
# Name: provisional, minted 2026-11-24 (UTC) by lane/repeat-watch for #6, after the workflow.

set -eu
me="repeat-watch-selftest"
repo="nifeos/record"
cd "$(dirname "$0")/.."

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_PREFIX GIT_COMMON_DIR GIT_OBJECT_DIRECTORY GIT_CONFIG_PARAMETERS

fail() {
	echo "$me: $1" >&2
	[ -n "${tmp:-}" ] && [ -f "$tmp/calls.log" ] && sed 's/^/  gh /' "$tmp/calls.log" >&2
	exit 1
}

[ -f helpers/trunk-health.sh ] && [ -f helpers/repeat_issue.py ] ||
	fail "nife's helpers/trunk-health.sh and helpers/repeat_issue.py are not linked in; run under script/lint, or make the overlay with python3 helpers/nife_tree.py overlay ."

# A nife older than the flags reads `--repeat` as its watching form and never returns, so ask first.
grep -q -e '--repo)' helpers/trunk-health.sh ||
	fail "the linked helpers/trunk-health.sh has no --repo; basalt's nife pin predates nifeos/nife#4072"

# The wiring the workflow itself must carry: both halves told the repository.
wf=.github/workflows/repeat-watch.yml
grep -q 'helpers/trunk-health.sh --repeat --repo "$GITHUB_REPOSITORY"' "$wf" ||
	fail "$wf no longer runs the repeat half with --repo"
grep -q 'helpers/repeat_issue.py sync --repo "$GITHUB_REPOSITORY"' "$wf" ||
	fail "$wf no longer files with --repo"

tmp="$(mktemp -d "${TMPDIR:-/tmp}/record-repeat-watch-selftest.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT HUP INT TERM
mkdir "$tmp/bin"

cat >"$tmp/bin/gh" <<EOF
#!/bin/sh
# One line per call: an issue body's newlines would read as further calls.
printf '%s\n' "\$*" | tr '\n' ' ' >>"$tmp/calls.log"; echo >>"$tmp/calls.log"
case "\$1 \$2" in
"run view")
	printf 'job\tstep\t2026-10-16T00:00:00.0000000Z the same line\n'
	printf 'job\tstep\t2026-10-16T00:00:00.0000000Z ##[error]Process completed with exit code 1.\n'
	exit 0 ;;
"issue list") echo '[]'; exit 0 ;;
"issue create") echo "https://github.com/$repo/issues/1"; exit 0 ;;
esac
if [ "\$1" = api ]; then
	printf 'failure\t2026-10-12T10:00:00Z\t901\nfailure\t2026-10-05T10:00:00Z\t902\nfailure\t2026-09-28T10:00:00Z\t903\nfailure\t2026-09-21T10:00:00Z\t904\nsuccess\t2026-09-14T10:00:00Z\ts\nsuccess\t2026-09-07T10:00:00Z\ts\n'
	exit 0
fi
exit 1
EOF
chmod +x "$tmp/bin/gh"

# What the record tracks and schedules, read here from git and the files themselves.
want=$(git ls-files -- .github/workflows | grep -E '^\.github/workflows/[^/]+\.yml$' |
	while read -r f; do grep -q '^  schedule:$' "$f" && basename "$f" .yml; done | sort)
printf '%s\n' "$want" | grep -q -x audit-cadence || fail "audit-cadence is not a scheduled workflow the record tracks"
printf '%s\n' "$want" | grep -q -x repeat-watch || fail "repeat-watch is not a scheduled workflow the record tracks"

# The overlay must have put nife's workflows here for this test to mean anything.
linked=$(find .github/workflows -maxdepth 1 -type l -name '*.yml' | wc -l)
[ "$linked" -gt 0 ] || fail "no nife workflow is linked into .github/workflows, so nothing proves they are left out"

PATH="$tmp/bin:$PATH" helpers/trunk-health.sh --repeat --repo "$repo" >"$tmp/out" 2>"$tmp/err" ||
	fail "helpers/trunk-health.sh --repeat failed: $(cat "$tmp/err")"

asked=$(sed -n 's|^api repos/\([^/]*/[^/]*\)/actions/workflows/\([^/]*\)\.yml/runs.*|\1 \2|p' "$tmp/calls.log" | sort)
[ "$asked" = "$(printf '%s\n' "$want" | sed "s|^|$repo |")" ] ||
	fail "asked about <$asked>; the record's own scheduled workflows are <$(printf '%s ' $want)>"
if grep -v -e "^api repos/$repo/" -e "^run view [0-9]* --repo $repo " "$tmp/calls.log" | grep -q .; then
	fail "a call named another repository or an unexpected command"
fi

rows=$(grep -c ' REPEAT: the same line ' "$tmp/out" || true)
[ "$rows" -eq "$(printf '%s\n' "$want" | wc -l)" ] || fail "expected one REPEAT row per scheduled workflow: $(cat "$tmp/out")"

: >"$tmp/calls.log"
grep ' REPEAT: ' "$tmp/out" | PATH="$tmp/bin:$PATH" python3 helpers/repeat_issue.py sync --repo "$repo" >/dev/null ||
	fail "helpers/repeat_issue.py sync --repo failed"
created=$(grep -c "^issue create --repo $repo --title scheduled failure repeats: " "$tmp/calls.log" || true)
[ "$created" -eq "$rows" ] || fail "expected $rows issues opened in $repo, saw $created"
if grep -v -e "^issue list --repo $repo " -e "^issue create --repo $repo " "$tmp/calls.log" | grep -q .; then
	fail "the filer called gh for another repository"
fi

echo "$me: asked $repo about its $rows scheduled workflows and none of nife's $linked linked ones, and filed there"
