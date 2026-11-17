---
name: readable
description: >
  Readability pass for code, tests, comments and messages, with house rules, a
  checklist, and a stranger read of the diff. This skill should be used when
  writing code, tests, comments, commit messages or PR text, when the user
  asks for a "readability pass", "readable", "human readable" or "stranger
  pass", when a reviewer says code is hard to follow, and when the user says
  one version reads better or worse.
argument-hint: "[messages] [<path|commit|range|branch|PR> | last <N>] [--fix] | draft | text <draft> | feedback <note> | promote | help"
---

# dsz:readable

Goal: a human reviewer understands each changed line on the first read.
Correct and short is not enough.

Files next to this one:

- `readable-code.md`: rules for code and tests, a checklist, and invented
  before/after examples.
- `writing-rules.md`: rules for prose: commit messages, comments, docs, PR
  text, replies.

## Usage

```
/dsz:readable                        report findings on the current diff
/dsz:readable <target>               the same on a path, commit, range, branch or PR
/dsz:readable last <N>               the same on the N latest commits
/dsz:readable messages [<target>]    commit messages only, no code
/dsz:readable [<target>] --fix       apply the fixes, then report what changed
/dsz:readable draft                  check the drafts in your last message
/dsz:readable text <draft>           check the text pasted after "text"
/dsz:readable feedback <note>        record a better/worse note in the local log
/dsz:readable promote                turn local log entries into rule changes
/dsz:readable help                   print this card
```

Targets:

- No argument: the uncommitted changes. If the tree is clean, the commits of
  the current branch, `<base>..HEAD`.
- A range uses git syntax: `A..B` is the commits in B that are not in A.
  `A..` means `A..HEAD`. Examples: `main..`, `HEAD~3..`.
- A branch name means the commits of that branch, `<base>..<branch>`, not
  only its tip.
- `last <N>` is `HEAD~N..HEAD`. It needs no base, so use it when the base is
  unclear.
- `<base>` is where the branch left the default branch: `git merge-base` with
  the local default branch (`main` or `master`).
- `messages` works on the same targets, `last <N>` included, and checks only
  the subjects and bodies of the commit messages: sentence style from
  `writing-rules.md`, and shape and trailers from the "Commit messages"
  section of `../draft/drafting-rules.md`.

Before reviewing commits, say which range was used and how many commits it
has. If any commit in it has another author than the user, or it has more than
15 commits, list them and ask before going on: the base is probably wrong.

Modes:

- Default: report each finding as location, what makes it hard to read, the
  plainer version. Change nothing.
- `draft` and `text <draft>`: check prose that is not posted yet, against
  `writing-rules.md` and the comment and message items of the checklist.
  Never fetch it from a public place. Report findings and give the revised
  text in a code block.
- `--fix`: apply the fixes to the files, run the tests they touch, and report
  what changed. Do not commit: where a fix goes in a commit series is the
  user's call. For commit messages, give the reworded messages instead of
  rewriting history. Never with code the user did not ask to change, such as
  someone else's PR: report only, and say so.
- `feedback <note>` and `promote`: follow "Feedback" below.
- `help`: print the card above and nothing else.
- Loaded by you while writing, not by the user's `/dsz:readable` command:
  follow "When writing" and "Stranger pass", and fix your own code directly.

## When writing

1. Read the rules and the checklist in `readable-code.md`, and skim its
   examples. For any prose, read `writing-rules.md` too. Read the local log
   `~/.claude/dsz/feedback/readable.md` if it exists: its entries without a
   "Promoted" line count as rules.
2. Measure before asserting: run the code and use the real values in tests and
   claims. Do not guess them.
3. Write the change.

## Stranger pass, before showing anything

1. Read only the changed lines (`git diff`), as someone who did not write them.
2. Go through the checklist in `readable-code.md`, one item at a time.
3. For each finding, fix every place in the diff with the same pattern, not
   only the first one.
4. Run the tests the change touches again.

## Feedback

When the user or a reviewer says something reads better or worse, follow
`${CLAUDE_PLUGIN_ROOT}/FEEDBACK.md`, the `FEEDBACK.md` in the plugin's root
directory.

- Local log: `~/.claude/dsz/feedback/readable.md`. An entry has the date, the
  source, the quote, before, after, what was wrong, and the rule it supports.
- On `promote`, prose rules go to `writing-rules.md`, code rules to
  `readable-code.md`, and the invented example to the "Examples" section of
  `readable-code.md`. Keep the rules numbered, and fix the rule numbers in the
  checklist and the examples.
