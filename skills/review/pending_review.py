#!/usr/bin/env python3
"""Adds review comments to the user's pending GitHub review. Never submits it.

Usage: pending_review.py REVIEW_JSON [--deny NAME]... [--dry-run]
       pending_review.py --test
Run it from a checkout of the PR's repository. REVIEW_JSON:
  {"pr": "https://github.com/OWNER/REPO/pull/N",
   "comments": [{"path": "a.cc", "line": 59, "body": "..."},
                {"path": "a.cc", "start_line": 10, "line": 14, "body": "..."}]}
"line" is the line at the PR head. A single RIGHT-side line is anchored to the
PR commit that last changed it. Ranges and "side": "LEFT" go on the final diff.
"commit": "<sha>" anchors to that commit, with "line" in that commit's file.
Names in ~/.claude/dsz/deny.txt, one per line, are held like --deny names.
"""
import argparse
import json
import os
import re
import subprocess
import sys

PR_QUERY = '''query($owner: String!, $name: String!, $number: Int!) {
  viewer { login }
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      id url headRefOid baseRefOid
      commits(first: 250) { nodes { commit { oid } } }
      reviews(states: PENDING, first: 20) {
        nodes { id author { login } commit { oid } comments(first: 100) { nodes { path body } } }
      }
    }
  }
}'''
NEW_REVIEW = '''mutation($pr: ID!, $commit: GitObjectID!) {
  addPullRequestReview(input: {pullRequestId: $pr, commitOID: $commit}) { pullRequestReview { id } }
}'''
ADD_LINE = '''mutation($review: ID!, $commit: GitObjectID!, $path: String!, $position: Int!, $body: String!) {
  addPullRequestReviewComment(input: {pullRequestReviewId: $review, commitOID: $commit, path: $path,
                                      position: $position, body: $body}) {
    comment { id originalLine originalCommit { oid } }
  }
}'''
ADD_THREAD = '''mutation($review: ID!, $path: String!, $line: Int!, $side: DiffSide!, $startLine: Int,
                 $startSide: DiffSide, $body: String!) {
  addPullRequestReviewThread(input: {pullRequestReviewId: $review, path: $path, line: $line, side: $side,
                                     startLine: $startLine, startSide: $startSide, body: $body}) {
    thread { line startLine comments(first: 1) { nodes { id } } }
  }
}'''
DROP_COMMENT = 'mutation($id: ID!) { deletePullRequestReviewComment(input: {id: $id}) { clientMutationId } }'

CHECKS = [
    ('email address', re.compile(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}')),
    ('IP address', re.compile(r'\b(?!127\.)(?:\d{1,3}\.){3}\d{1,3}\b')),
    ('internal host name', re.compile(r'[\w.-]+\.(?:amazonaws\.com|internal)\b', re.I)),
    ('key or secret', re.compile(r'AKIA[0-9A-Z]{16}|gh[pousr]_\w{30,}|xox[abp]-[\w-]+|-----BEGIN [A-Z ]*PRIVATE KEY'
                                 r'|(?i:password|passwd|secret|api[_-]?key)\s*[:=]\s*(?![\'"]?(?:cassandra|postgres|admin|example|changeme)\b)\S+')),
]
DENY_FILE = os.path.expanduser('~/.claude/dsz/deny.txt')
MENTION = re.compile(r'(?<![\w`])@[A-Za-z][\w-]*')
CODE = re.compile(r'```.*?```|`[^`\n]*`', re.S)
HUNK = re.compile(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@')


def run(*cmd, stdin=None):
    return subprocess.run(cmd, input=stdin, capture_output=True, text=True, check=True).stdout


def gql(query, **variables):
    assert not re.search(r'submit|\bevent\b', query), 'this script never submits a review'
    p = subprocess.run(['gh', 'api', 'graphql', '--input', '-'], capture_output=True, text=True,
                       input=json.dumps({'query': query, 'variables': variables}))
    out = json.loads(p.stdout or '{}')
    if out.get('errors') or p.returncode:
        raise RuntimeError('; '.join(e['message'] for e in out.get('errors', [])) or p.stderr.strip())
    return out['data']


def problems(body, deny):
    found = [what for what, pattern in CHECKS if pattern.search(body)]
    found += [f'name "{n}"' for n in deny if re.search(rf'\b{re.escape(n)}\b', body, re.I)]
    if MENTION.search(CODE.sub('', body)):
        found.append('bare @mention (notifies that user when published)')
    return found


def standing_deny(path=DENY_FILE):
    """Names held in every review: one per line in the deny file. A line that starts with '#' is a comment."""
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]


def fetch_url(remotes, owner, name):
    """URL of the checkout's remote for OWNER/NAME, so the fetch uses the user's protocol. HTTPS if there is none."""
    for line in remotes.splitlines():
        url = line.split()[1]
        if re.search(rf'[:/]{re.escape(owner)}/{re.escape(name)}(?:\.git)?/?$', url, re.I):
            return url
    return f'https://github.com/{owner}/{name}.git'


def position(diff, line):
    """Position of new-file `line` in a one-file diff: 1 is the line below the first @@."""
    pos, new = None, 0
    for text in diff.splitlines():
        m = HUNK.match(text)
        if m:
            pos = 0 if pos is None else pos + 1
            new = int(m.group(1))
            continue
        if pos is None:
            continue
        pos += 1
        if text.startswith(('-', '\\')):
            continue
        if new == line:
            return pos
        new += 1
    return None


def anchor(c, head, base, commits):
    """How to place comment `c`: ('line', commit, path, line, position) or ('thread',)."""
    if 'start_line' in c or c.get('side', 'RIGHT') == 'LEFT' or c.get('commit') == 'head':
        if c.get('commit') not in (None, 'head'):
            raise ValueError('ranges and LEFT-side lines can only go on the final diff')
        if 'start_line' in c or c.get('side', 'RIGHT') == 'LEFT':
            return ('thread',)
        commit, path, line = head, c['path'], c['line']
    elif 'commit' in c:
        matches = [oid for oid in commits if oid.startswith(c['commit'])]
        if len(matches) != 1:
            raise ValueError(f'commit {c["commit"]} is not one PR commit')
        commit, path, line = matches[0], c['path'], c['line']
    else:
        mb = run('git', 'merge-base', base, head).strip()
        out = run('git', 'blame', '--porcelain', '-L', f'{c["line"]},{c["line"]}', f'{mb}..{head}', '--', c['path'])
        sha, orig_line = out.split()[0], int(out.split()[1])
        if sha in commits:
            commit, path, line = sha, re.search(r'^filename (.*)$', out, re.M).group(1), orig_line
        else:
            commit, path, line = head, c['path'], c['line']
    mb = run('git', 'merge-base', base, commit).strip()
    diff = run('git', 'diff', '--no-color', '--no-ext-diff', '--diff-algorithm=myers', '-U3', mb, commit, '--', path)
    pos = position(diff, line)
    if pos is None:
        raise ValueError(f'{path}:{line} is not in the PR diff at {commit[:10]}')
    return ('line', commit, path, line, pos)


def parse_pr(ref):
    m = re.search(r'github\.com/([\w.-]+)/([\w.-]+)/pull/(\d+)', ref) or re.fullmatch(r'([\w.-]+)/([\w.-]+)#(\d+)', ref)
    if not m:
        sys.exit(f'cannot parse PR reference {ref!r}')
    return m.group(1), m.group(2), int(m.group(3))


def main(args):
    with open(args.review_json) as f:
        draft = json.load(f)
    owner, name, number = parse_pr(draft['pr'])
    data = gql(PR_QUERY, owner=owner, name=name, number=number)
    pr = data['repository']['pullRequest']
    head, base = pr['headRefOid'], pr['baseRefOid']
    commits = [n['commit']['oid'] for n in pr['commits']['nodes']]
    missing = [s for s in (head, base)
               if subprocess.run(['git', 'cat-file', '-e', s + '^{commit}'], capture_output=True).returncode]
    if missing:
        run('git', 'fetch', '--no-tags', '--quiet', fetch_url(run('git', 'remote', '-v'), owner, name), *missing)
    mine = [r for r in pr['reviews']['nodes'] if r['author']['login'] == data['viewer']['login']]
    review = mine[0]['id'] if mine else None
    review_commit = mine[0]['commit']['oid'] if mine else head
    existing = {(c['path'], c['body']) for c in mine[0]['comments']['nodes']} if mine else set()
    if review_commit != head:
        print(f'note: your pending review is on {review_commit[:10]}, the PR head is {head[:10]}')
    print(('dry run, nothing posted: ' if args.dry_run else '') + pr['url'] + '/files')

    deny = args.deny + standing_deny()
    bad = 0
    for i, c in enumerate(draft['comments'], 1):
        where = f'#{i} {c["path"]}:' + (f'{c["start_line"]}-' if 'start_line' in c else '') + str(c['line'])
        if (c['path'], c['body']) in existing:
            print(f'{where}  skipped, already in the pending review')
            continue
        held = problems(c['body'], deny)
        if held:
            bad += 1
            print(f'{where}  HELD, not posted: {", ".join(held)}')
            continue
        try:
            a = anchor(c, head, base, commits)
            if a[0] == 'thread' and review_commit != head:
                raise ValueError('final diff comments need a pending review on the PR head')
            target = 'final diff' if a[0] == 'thread' or a[1] == head else f'commit {a[1][:10]} line {a[3]}'
            if args.dry_run:
                print(f'{where}  ok, {target}')
                continue
            if not review:
                review = gql(NEW_REVIEW, pr=pr['id'], commit=head)['addPullRequestReview']['pullRequestReview']['id']
            if a[0] == 'line':
                got = gql(ADD_LINE, review=review, commit=a[1], path=a[2], position=a[4], body=c['body'])
                got = got['addPullRequestReviewComment']['comment']
                placed = (got['originalLine'], got['originalCommit']['oid']) == (a[3], a[1])
                comment_id = got['id']
            else:
                side = c.get('side', 'RIGHT')
                got = gql(ADD_THREAD, review=review, path=c['path'], line=c['line'], side=side,
                          startLine=c.get('start_line'), startSide=side if 'start_line' in c else None, body=c['body'])
                got = got['addPullRequestReviewThread']['thread']
                placed = (got['line'], got['startLine']) == (c['line'], c.get('start_line'))
                comment_id = got['comments']['nodes'][0]['id']
            if not placed:
                gql(DROP_COMMENT, id=comment_id)
                raise ValueError('GitHub placed it on another line, removed it again')
            print(f'{where}  posted, {target}')
        except (ValueError, RuntimeError, subprocess.CalledProcessError) as e:
            bad += 1
            print(f'{where}  FAILED: {getattr(e, "stderr", None) or e}'.strip())
    return 1 if bad else 0


def test():
    diff = '\n'.join(['diff --git a/f b/f', '--- a/f', '+++ b/f',
                      '@@ -1,3 +1,4 @@', ' a', '-b', '+B', '+C', ' d',
                      '@@ -10,2 +11,2 @@ ctx', ' x', '+y'])
    assert [position(diff, n) for n in (1, 2, 4, 12, 5)] == [1, 3, 5, 8, None]
    assert problems('see 10.0.0.12 in the log', []) == ['IP address']
    assert problems('connect to 127.0.0.1, mail me', []) == []
    assert problems('mail ops@example.com', []) == ['email address']
    assert problems('node ip-10-1-2-3.ec2.internal', []) == ['internal host name']
    assert problems("password: hunter2", []) == ['key or secret']
    assert problems("connect(password='cassandra')", []) == []
    assert problems('ping @someone', []) == ['bare @mention (notifies that user when published)']
    assert problems('```\n@pytest.mark.xfail\n```', []) == []
    assert problems('Acme sees this', ['acme']) == ['name "acme"']
    assert problems('node db1.acme.example', ['acme.example']) == ['name "acme.example"']
    assert standing_deny('/nonexistent/deny.txt') == []
    remotes = 'origin\tgit@github.com:me/app.git (fetch)\nupstream\tgit@github.com:acme/app.git (fetch)\n'
    assert fetch_url(remotes, 'acme', 'app') == 'git@github.com:acme/app.git'
    assert fetch_url(remotes, 'acme', 'other') == 'https://github.com/acme/other.git'
    print('ok')
    return 0


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('review_json', nargs='?')
    ap.add_argument('--deny', action='append', default=[], metavar='NAME', help='hold comments containing this name')
    ap.add_argument('--dry-run', action='store_true', help='check and anchor, post nothing')
    ap.add_argument('--test', action='store_true', help='run the self-check')
    args = ap.parse_args()
    if not args.test and not args.review_json:
        ap.error('REVIEW_JSON is required')
    sys.exit(test() if args.test else main(args))
