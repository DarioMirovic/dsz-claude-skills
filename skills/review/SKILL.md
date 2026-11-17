---
name: review
description: >
  Reviews someone else's PR and leaves the comments in the user's pending
  (unpublished) GitHub review, which the user publishes. This skill should be
  used when the user gives a PR URL to review into a draft review, runs
  "/dsz:review <PR>", or asks to push drafted review comments to GitHub as a
  pending review ("post the comments as a draft review", "/dsz:review post").
  A light mode ("--light") reviews by hand against a list of code checks
  instead of running /code-review.
argument-hint: "<PR URL> [code-review level] [--max-findings N|all] | <PR URL> --light | post | feedback <note> | promote | help"
---

# dsz:review

Puts review comments into the user's pending GitHub review. Never publishes:
the user reads the draft on GitHub and submits it (approve, comment or
request changes).

Files next to this one:

- `pending_review.py`: the only way this skill writes to GitHub. It adds to
  the user's pending review (or starts one), and has no submit path. It needs
  the `gh` CLI, logged in.
- `code-checks.md`: the "before flagging" rules and general line-level
  checks.

## Usage

```
/dsz:review <PR URL> [level] [--max-findings N|all]
                               review the PR, draft, fill the pending review
/dsz:review <PR URL> --light   the same, reviewed by hand instead of /code-review
/dsz:review post               push the review comments drafted in this session
/dsz:review feedback <note>    record a missed or wrongly flagged finding
/dsz:review promote            turn local log entries into check changes
/dsz:review help               print this card
```

## Hard rules

1. **Never publish.** No `--comment` for code-review, no `gh pr review`,
   `gh pr comment` or `gh issue comment`, no submitting a review, no GitHub
   write except through `pending_review.py`.
2. **No client names on GitHub** (draft skill, "All drafts" rules 7 and 8).
   A comment that may name a client, or anything that identifies one, is held
   back: not posted, not even into the draft. Tracker keys are fine. An older
   PR that has a client name is no precedent.
   - Collect the client names in this review's context (tickets linked from
     the PR or the code, support tickets, logs) and pass each to the script
     as `--deny NAME`.
   - Names that must never appear in any review (the user's own clients,
     internal domains) go to `~/.claude/dsz/deny.txt`, one per line. The
     script reads it on every run.
   - When a word only might be a client name, hold the comment and ask.
3. **Only the comment goes into the body.** Severity, confidence, finding
   numbers and notes for the user go to the notes file.
4. **Some text is never posted.** The review summary, comments for the
   conversation tab, and held comments go to the notes file for the user to
   paste or drop.
5. **Reproducers** go in the comment at the line they hit: the commit and
   command they ran with, the test in a fenced block, the failing output
   trimmed and cleaned, and a question ("Can you check whether this is a real
   issue?"). With no fitting line, it is a conversation comment. A bug only a
   deliberate attack reaches never goes to GitHub (draft skill, "All drafts"
   rule 5).

## Project code checks

A project can bring its own code checks as a separate skill, usually from
another plugin. If the session lists a skill whose description says it holds
code checks for this skill and for the project of the PR, invoke it. Its
checks replace the "Checks" section of `code-checks.md`. The "before
flagging" rules always apply.

## Full cycle: `/dsz:review <PR URL> [level] [--max-findings N|all]`

The user runs one session per PR and coordinates builds, RAM and worktrees
between sessions. Follow what they say about where to work.

1. Notes go to the user's notes directory for the PR when they have one,
   otherwise to `~/.claude/dsz/reviews/<owner>-<repo>-<N>/`. Work in a
   checkout of the repo. The script fetches the PR commits it needs.
2. Run `/code-review <level> <PR URL> --max-findings <N>`, N 20 unless the
   user gave one. Without a level, code-review reuses the last one the user
   typed.
3. Take every finding that survived verification. Read the code at each one.
   Drop a finding that turns out wrong and say so in the report. Judge the
   findings against the code checks.
4. Draft one comment per finding with the draft skill (review comment
   rules), which also runs the readable skill's checks.
5. Write `review.json` and `review.md` (shapes below), run the script with
   `--dry-run`, fix what it reports (reword, or move to "Held back"), then run
   it for real.
6. Report in chat: the "Files changed" link, how many comments were posted,
   every held or failed comment with its reason and full text, and the notes
   file path.

## Light cycle: `/dsz:review <PR URL> --light`

Steps 1 and 4-6 of the full cycle. Steps 2 and 3 become:

2. Read the PR description, the linked ticket, the commit messages and the
   diff, commit by commit. Read the surrounding code where a change depends
   on it.
3. Go through the code checks on the changed lines, starting with the
   "before flagging" rules. Keep at most 20 findings (or `--max-findings`),
   the most severe first, each with its scenario and the code that proves it.

When the user asks for the review in chat only, stop after drafting: show
the comments and the notes in chat and post nothing.

## Post only: `/dsz:review post`

For comments already drafted in this session: step 5, then step 6.

## The script

Run the `pending_review.py` that sits next to this file, from a checkout of
the PR's repository:

```
python3 ${CLAUDE_SKILL_DIR}/pending_review.py review.json [--deny NAME]... [--dry-run]
python3 ${CLAUDE_SKILL_DIR}/pending_review.py --test
```

`review.json`:

```json
{"pr": "https://github.com/OWNER/REPO/pull/123",
 "comments": [
  {"path": "src/x.py", "line": 59, "body": "..."},
  {"path": "docs/y.md", "start_line": 253, "line": 256, "body": "..."}
 ]}
```

- `line` is the line at the PR head, as code-review reports it.
- A single line is anchored to the PR commit that last changed it, at that
  commit's line number, so it shows in the per-commit view. A line the PR did
  not change goes on the final diff.
- Line ranges and `"side": "LEFT"` (deleted lines) go on the final diff, the
  only place GitHub accepts them.
- `"commit": "<sha>"` forces a commit, with `line` in that commit's file.
  `"commit": "head"` forces the final diff.

The script skips comments already in the pending review, so a rerun is safe.
It holds comments with emails, IP addresses other than 127.x, internal host
names, keys or secrets, bare `@name` mentions (GitHub notifies that user on
publish, so put code like `@pytest.fixture` in backticks), `--deny` names,
and the names in `~/.claude/dsz/deny.txt`. After posting each comment it
checks where GitHub put it, and removes and reports any it misplaced. Exit
code 1 means something was held or failed.

Missing PR commits are fetched from the checkout's own remote for the PR's
repository, so the fetch uses the protocol (SSH or HTTPS) the user has set
up. With no such remote, the script falls back to HTTPS.

## review.md

```
# PR <N> review draft, <date>, head <sha>

## Summary (paste when submitting)
## Conversation comments (paste in the PR conversation)
## Held back (not posted, reason first)
## Notes on posted comments (not for GitHub)
```

## Feedback

When a review missed something or flagged something wrongly, follow
`${CLAUDE_PLUGIN_ROOT}/FEEDBACK.md`, the `FEEDBACK.md` in the plugin's root
directory.

- Local log: `~/.claude/dsz/feedback/review.md`. An entry has the date, the
  source, the quote, what was missed or flagged wrongly, and the check it
  supports. Read the log at the start of a review: its entries without a
  "Promoted" line count as checks.
- On `promote`, checks go to `code-checks.md`. When a project code checks
  skill is in use, the feedback goes to that skill's own log instead.
