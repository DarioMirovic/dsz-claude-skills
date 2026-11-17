---
name: draft
description: >
  Drafts commit messages, PR descriptions, update messages, review replies,
  review comments and ticket text, any number in one go, and never posts
  them. This skill should be used when the user asks to draft, write or
  reword a commit message, PR description, "V2" update message, reply to a
  review comment, review comment, bot finding dismissal, or ticket
  description or comment, or several of them at once.
argument-hint: "<what to draft: commit | pr | update | reply | review | ticket, any number> | feedback <note> | promote | help"
---

# dsz:draft

Drafts text the user will post. Never posts it.

Files next to this one:

- `drafting-rules.md`: what goes into each kind of message and its shape,
  plus invented before/after examples.

Sentence style and the final check come from the readable skill, in
`../readable/` next to this skill's directory. At the start, read its
`writing-rules.md` and the checklist in its `readable-code.md`. Do not invoke
the readable skill: with no argument it reviews the current diff.

Read the local logs too, if they exist: `~/.claude/dsz/feedback/draft.md` and
`~/.claude/dsz/feedback/readable.md`. Their entries without a "Promoted" line
count as rules.

## Usage

```
/dsz:draft <request>           draft everything the request names, in one go
/dsz:draft feedback <note>     record a better/worse note in the local log
/dsz:draft promote             turn local log entries into rule changes
/dsz:draft help                print this card
```

Examples of a request: "replies to the 3 new comments", "PR body and V3
update message", "commit message for the staged change", "ticket comment with
the decision". With no request, draft what the current task is waiting for
(open review comments, the update message for unpushed changes) and say
what that was.

## Procedure

1. **List the items.** Write down every draft the request needs: each review
   comment to answer, the PR body, the update message, and so on.
2. **Collect the facts for each item.** Use what this conversation already
   established: the decisions, what was changed, what was measured. Read the
   review comments, the code, the commits and the PR state where needed.
   Check every claim before it goes into a draft.
3. **Draft all items** with the rules in `drafting-rules.md` and the sentence
   rules in the readable skill's `writing-rules.md`. Where the project has
   its own convention for titles, trailers or PR text, the project's
   convention wins.
4. **Check all drafts at once** against every rule in `writing-rules.md` and
   the comment and message items of the checklist in `readable-code.md`,
   reading them as a stranger would. Fix every place with the same problem.
5. **Show them in one message:** for each item, a short heading (who, where,
   what) and the draft in a code block. Then one line per open question, for
   example a decision the user still has to make.
6. **Save** the drafts to the task's notes file when the task has one.

## Feedback

When the user says a draft reads better or worse, follow
`${CLAUDE_PLUGIN_ROOT}/FEEDBACK.md`, the `FEEDBACK.md` in the plugin's root
directory.

- Local log: `~/.claude/dsz/feedback/draft.md`. An entry has the date, the
  quote, before, after, and the rule it supports. A note about sentence style
  goes to the readable skill's log, `~/.claude/dsz/feedback/readable.md`.
- On `promote`, rules and invented examples go to `drafting-rules.md`.
