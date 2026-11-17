# dsz skills for Claude Code

Four skills, packaged as the plugin `dsz`. They come from review feedback on
real work: each rule is there because a human reviewer asked for it.

| Skill | What it does |
|---|---|
| `/dsz:readable` | Readability pass for code, tests, comments and messages: rules, a checklist, and a read of the diff as a stranger. |
| `/dsz:draft` | Drafts commit messages, PR descriptions, update messages, review replies and comments. Never posts them. |
| `/dsz:review` | Reviews someone else's PR and puts the comments into your pending GitHub review. You publish it. |
| `/dsz:design` | Agrees the design with you before any code, against a numbered checklist. |

Every skill prints its usage card with `help`, for example `/dsz:design help`.

## Install

```
/plugin marketplace add DarioMirovic/dsz-claude-skills
/plugin install dsz@dsz
```

To try it for one session without installing, from a clone:

```
claude --plugin-dir /path/to/dsz-claude-skills
```

`/dsz:review` needs the `gh` CLI, logged in, and uses the built-in
`/code-review` skill.

## Feedback

The skills learn in two stages, described in [FEEDBACK.md](FEEDBACK.md):

1. `/dsz:<skill> feedback <note>` records what a reviewer said in a local
   log. The log may hold real code and quotes. It stays on your machine, and
   the skill reads it on every run.
2. `/dsz:<skill> promote` turns log entries into rule changes and invented
   examples in your clone of this repository. You review the diff and commit.

The examples in this repository are all invented. They mirror real feedback,
with made-up code.

## Local files

| Path | What it is |
|---|---|
| `~/.claude/dsz/feedback/<skill>.md` | The local feedback log of a skill. |
| `~/.claude/dsz/clone-path` | One line: the path of your clone, used by `promote`. |
| `~/.claude/dsz/deny.txt` | Names that `/dsz:review` never lets into a review comment, one per line. |
| `~/.claude/dsz/reviews/` | Review notes, when you have no notes directory of your own. |

## Project checklists

`/dsz:design` and `/dsz:review` ship with general checklists. A project can
replace them with its own, as a skill in another plugin. The skill's
description says that it is a design checklist for `dsz:design`, or code
checks for `dsz:review`, and names the project. The general skills find it by
that description and use its checklist in place of their own.

## Releases

The plugin has a `version` in `.claude-plugin/plugin.json`. Users get changes
only when that version changes, so commits and merged PRs on `main` reach
nobody until the next release.

- A PR does not change the version.
- The maintainer raises it when a set of changes is ready.
- Users then run `claude plugin update dsz@dsz`.

## What the skills do not do

They never publish on GitHub, push, or commit on their own. This is a rule in
the skill text, not an enforced block. If you want it enforced, add a hook
of your own that blocks `gh pr review`, `gh pr comment` and `gh issue comment`.

## License

MIT with the Commons Clause, see [LICENSE](LICENSE). In short: free to use,
change and share, also at work. Not to be sold.
