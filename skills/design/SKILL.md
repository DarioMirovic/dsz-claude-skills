---
name: design
description: >
  Designs a change with the user before any code, or checks an existing
  change at the design level, against a checklist (scope, all code paths,
  concurrency and shutdown, upgrades and stored data, interfaces, config,
  metrics, test layer, delivery). This skill should be used when the user
  asks to design, plan or think through a fix or feature, asks "how should we
  do X", runs "/dsz:design", asks for a design or architecture review of a
  PR, branch or plan, or says a design missed something.
argument-hint: "<task, ticket key or description> | review <PR|branch|plan file> | feedback <note> | promote | help"
---

# dsz:design

Goal: the design is agreed with the user before code is written, and nothing
on the checklist is forgotten. `/code-review` finds bugs in lines. This skill
asks whether the change fits the system.

Files next to this one:

- `design-checklist.md`: the general numbered checklist.

## Usage

```
/dsz:design <task>                 design a change with the user, no code yet
/dsz:design review <target>        check a PR, branch or plan at the design level
/dsz:design feedback <note>        record a design miss or a reviewer push-back
/dsz:design promote                turn local log entries into checklist changes
/dsz:design help                   print this card
```

`<task>` is a ticket key, a GitHub issue, or a description. `<target>` is a
PR URL or number, a branch (its commits since the merge-base with the default
branch), or a plan file.

## Hard rules

1. **No code before the user approves the design.** Reading code, running
   existing tests and small experiments that answer a design question are fine.
2. **Questions in plain chat text,** numbered, each with a recommended answer,
   so the user can reply "1 ok, 2 no because ...". No question widgets.
3. **Claims about how the code works come from the code,** with `file:line`.
   Anything not checked is marked "unverified". Same for claims about what
   another system or a spec does. Before claiming a bound or an invariant,
   try to break it with every order of operations.
4. **Same bug, all paths.** A fix that leaves the same bug on another path is
   not an option to offer.
5. **The simplest design that meets the need wins.** No speculative config
   option, abstraction or extension point. Say what was left out and when it
   would be needed.
6. **Judge the shape, not the size of the diff.** The smallest change is not
   the best design when it leaves the code harder to follow.

## Project checklist

A project can bring its own checklist as a separate skill, usually from
another plugin. If the session lists a skill whose description says it is a
design checklist for this skill and for the project at hand, invoke it and
follow what it says. Its checklist replaces `design-checklist.md`, it names
the design docs to read, and its feedback goes to its own log.

## Design: `/dsz:design <task>`

1. **Frame.** Read the ticket or issue and its links. Write down in a few
   lines: what the user of the product sees today, what they should see, and
   for a bug the root cause (not the symptom). If the root cause is not known
   yet, finding it is the first step, not designing.
2. **Read.** Trace the code path end to end. Read the project's design docs
   for the area. List every path that reaches the changed code. Use an
   Explore agent only when the area is too wide to read directly.
3. **Checklist.** Go through the checklist, one item at a time. Read the
   local log first (see "Feedback"): its entries without a "Promoted" line
   count as items. For each item: it does not apply, it applies and the
   answer is clear (with evidence), or it is an open question.
4. **Ask.** Show the user a short summary: the frame, the paths found, the
   items that apply with their answers, and the open questions with your
   recommended answers. Stop and wait.
5. **Options.** When there is a real choice, give 2 or 3 approaches. For each:
   what changes, which checklist items it makes easier or harder, the test
   layer, and whether it can be backported. Recommend one and say why. With
   one obvious approach, give only that one and say why there is no other.
6. **Record.** After the user agrees, write down the frame, the chosen
   design, the rejected options with one line each on why, the checklist
   answers, and the test plan, where the user asked or in the usual notes
   place. The rejected options feed the PR description and answers to "why
   not X?" in review.
7. **After implementing,** run `/dsz:design review` on the branch to catch
   where the code drifted from the design.

## Review: `/dsz:design review <target>`

1. Read the PR description, the linked ticket and the diff. For a branch or a
   plan, read the commits or the file.
2. Read enough of the surrounding code to know every path into the changed
   code, and the project's design docs for the area.
3. Go through the checklist. Report only the items that apply: item number,
   what the change does there, the problem or the question, and what to check
   or change. Leave line-level bugs to `/code-review`.
4. Report in chat. Never post. For someone else's PR, comments to post go
   through the review and draft skills of this plugin.

## Feedback

When a design misses something, or a reviewer or maintainer pushes back on a
design, follow `${CLAUDE_PLUGIN_ROOT}/FEEDBACK.md`, the `FEEDBACK.md` in the
plugin's root directory.

- Local log: `~/.claude/dsz/feedback/design.md`. An entry has the date, the
  source, the quote, what was missed, and the checklist item that should have
  caught it, or that none did.
- On `promote`, a new or reworded item goes to `design-checklist.md`. Keep
  the items numbered and fix the references to them.
- When a project checklist skill is in use, the feedback goes to that skill's
  own log and checklist instead.
