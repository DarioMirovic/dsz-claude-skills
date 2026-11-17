# Feedback Flow

The skills of this plugin learn from feedback in two stages. The first stage
is private and stays on the machine. The second changes the skill, and the
user reviews it before it is committed.

`<skill>` below is `readable`, `draft`, `review` or `design`.

## Stage 1: record (`/dsz:<skill> feedback <note>`)

1. Work out what the feedback says was wrong, and which rule or checklist
   item should have caught it.
2. Add an entry at the top of the skill's local log,
   `~/.claude/dsz/feedback/<skill>.md`. Create the file if it is missing.
   An entry has:
   - a `###` heading: the date, the source, a few words on the lesson
   - the quote
   - before and after, where there are any
   - what was wrong
   - the rule or item it supports
3. Apply the lesson for the rest of the session.

The local log may hold real code, names and quotes. Never write an entry into
the skill's own files: the installed copy is replaced on every update, and the
repository is public.

When a skill runs, it reads its local log. Entries without a "Promoted" line
count as rules.

## Stage 2: promote (`/dsz:<skill> promote`)

1. Find the user's clone of the skills repository. Its path is the one line
   in `~/.claude/dsz/clone-path`. If the file is missing, ask the user for
   the path and write it there.
2. For each log entry without a "Promoted" line, decide whether it changes
   the skill. If it teaches something new, add or reword a rule or checklist
   item in the clone. Keep the numbering, and fix the numbers that refer to
   it.
3. Where the skill has an "Examples" section, add or update an example.
   Invent it: the same lesson and the same before/after shape, in made-up
   code and text. Nothing from the log goes into the clone: no real code, no
   names of people, clients or products, no quotes of other people, no ticket
   or PR numbers, no description of a specific bug.
4. Add a line under the heading of the log entry:
   `Promoted: <date>, <rule or item>`. For an entry that changes nothing:
   `Promoted: <date>, no change`.
5. Show the diff of the clone. Do not commit or push: the user reviews the
   diff first. Leave `version` in `plugin.json` as it is: the maintainer
   raises it at a release.
