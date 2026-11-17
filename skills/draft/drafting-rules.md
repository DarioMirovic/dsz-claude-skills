# Drafting Rules

What goes into each kind of message, and its shape. How the sentences read
(short, plain words, no em dashes, present tense) is in the readable skill.
This file does not repeat it.

Where the project has its own convention (title format, trailers, PR
template), the project's convention wins over the shapes below.

## All drafts

1. **Drafts only.** Never post, push, comment or send. The user posts.
2. **Ready to paste.** One code block per draft, no hard wraps inside a
   paragraph, no `>` quote prefixes. Also save the drafts to a file in the
   task's notes directory when the task has one.
3. **Verified facts.** Check every claim against the current code, branch and
   PR state before writing it: symbols exist, numbers were measured, a PR named
   as a dependency is still open. A wrong fact in a public text is worse than a
   missing one.
4. **Cite one tracker key.** When a ticket exists in the project's main
   tracker, cite only its key (`PROJ-1234`), never a second number for the
   same thing (a mirrored issue in another tracker), in messages and in the
   strings a change touches.
5. **No hints at unfiled security bugs.** When the user decides not to file a
   bug that only a deliberate attack reaches, no public text may point at it,
   not even vaguely ("and at least one more case"). Justify related code on
   general grounds.
6. **Keep the user's voice.** When revising the user's own draft, keep the
   phrasing that works and add only the missing facts.
7. **No client names in public text.** Text meant for a public place
   (commits, PR text, review comments, replies, reproducers) never names a
   client or anything that identifies one: company, cluster, host, account or
   contact names. This holds even when the source (a private ticket, a log,
   an older PR) has the name. Write "a user" instead. Client details belong
   in the private tracker.
8. **Clean logs and test output before quoting them in public.** Keep only
   the lines that matter. Remove host names, IP addresses, cluster and account
   IDs, emails, keys and tokens.

## Commit messages

1. **Title:** `area: what changed`, lower case after the area, no period
   (`cache: count evictions per tenant`).
2. **Body:** why, not what: the problem, the constraint, the rejected
   alternative. The diff shows what changed. Test the motivation: if the
   inverse change ("make X not do Y") sounds just as reasonable, the why is
   missing.
3. **Proportional.** A small diff gets a few lines. Do not list every clause
   the change touches, and do not justify style choices ("this follows the
   existing style of..."). When a commit grows, rewrite the message shorter so
   it covers the whole commit. Do not append a paragraph per added item.
4. **Fix commit shape** (about 12 lines): one paragraph of context, "The old
   logic ... so <symptom>.", "The new logic ...". A preparatory commit of a
   series (see "Commit split" in the design skill's checklist) says what it
   changes, whether behaviour changes, and which later step needs it, in a
   few lines.
5. **Test commit shape:** the bug in about three lines, the shared recipe of
   the tests in one sentence, one bullet per case.
6. **One outcome, one statement.** When something behaves the same in every
   build mode, say it once ("crashes"), not per mode. Measurements stay in the
   notes, not in the message.
7. **Trailers:** every commit of a series gets `Refs PROJ-<n>`. Only the
   last code commit (not a docs or test-only one) gets `Fixes PROJ-<n>`,
   unless the series puts `Fixes` in the PR body instead. One trailer per line.
   No `Fixes` for an already closed ticket. Never "Fixes part of".
8. **No `Co-Authored-By`** trailer for an AI assistant.

## PR descriptions

1. **New description:** what the series does and why, in short paragraphs.
   Mention what was deliberately left out and where it is tracked. End with
   the ticket, and with a backport line where the project has release
   branches:

   ```
   Fixes PROJ-<n>

   Backport: <none|branches>, <one-line reason>.
   ```

2. **Backport line:** critical fixes are backported, performance fixes mostly
   not. Base the reason on whether a real deployment can reach the bug, not
   only on precedent.
3. **New version of a description:** keep the existing text and style, change
   only what the new version needs, and fix every stale fact (a merged
   dependency, a renamed symbol, a branch that now exists). List those fixes
   in one line for the user.
4. **A case with no test** (for example one that would need a new fault
   injection): say it was reproduced locally.

## Update messages (after a force-push)

- `Vn` counts published review rounds of the PR: the first push is V1, the
  push after the first review round is V2. It is not a local backup counter.
- Shape: a `V2:` line, then up to about five bullets of 2 to 15 words each.
  Only the important changes, what was done. No reviewer names, no mention of
  new tests or reworded messages.

```
V2:
- count uploads whose bucket is deleted before the quota check
- register the export counters only when the export job is enabled
```

## Review replies (on the user's own PR)

1. **Fixed:** agree in a word or two, say what changed and where, in one to
   three sentences. If a case has no test, say how it was checked.
2. **Answer only:** the verdict first ("Yes, it's intended."), then the reason
   in two or three sentences with the facts that settle it.
3. **Overlap with another PR:** say what each one covers, and what the end
   state is once both land.
4. **Findings of review bots:** if the claim is accurate but the behavior is
   a choice, dismiss it as "by design" (not "false positive") with one or two
   sentences of reason, ideally a precedent in the codebase.

## Review comments (on someone else's PR)

- Short declarative sentences, plain words, articles may be dropped ("New
  certificate path does that.").
- Plain and short (readable skill, writing rule 9). Say what is wrong and
  what it means for the client or the test, in simple words, then ask. Two to
  four short sentences is typical. No separate "in code" paragraph: name only
  the one or two symbols the author needs to find the spot, inline. The
  author knows the code and can ask for the details.
- End with a collaborative question or a soft proposal: "Could we add such a
  test?", "Should we consider throttling...?", "Consider reordering this
  one." "perhaps" is the preferred softener.
- Propose what the author could do. Never offer work from the user ("Should
  I send a follow-up?"): the user did not take it on.
- First person plural for the code under review: "we insert an audit row",
  not "you do X".
- Show where the gap sits. Name what the code or tests already cover (test
  names, flags, files), then the case left out, then what makes that case
  different. The reader sees the gap as the one missing piece without opening
  the code.
- Say the hidden step. When the point depends on something the reader can't
  see at the commented line (a name rewritten earlier, a caller's conversion),
  say it in plain words. Lead with the outside fact the point rests on ("The
  upstream API has 12 of these endpoints only"), not a list of names.
- One or two short paragraphs. No headings, no bullet lists inside a comment.
- Backticks for symbols, config keys and expressions. A spaced hyphen where an
  em dash would go.

## Ticket descriptions and comments

- Open with what the ticket or comment is about, in one or two sentences.
- Then the facts: what happens, where in the code, how it was checked.
- When a decision is needed, end with the question, phrased so it can be
  answered in one line.
- Short paragraphs. Code symbols in backticks.

## Examples

The examples are invented. Each one mirrors real feedback on a draft: the
same lesson and the same before/after shape, about a made-up file storage
service. "Feedback" is what the user said, in general words.

### Revising the user's draft changed its meaning (all drafts, rule 6)

Feedback: "You changed the meaning of my message. I want to refer to the
source."

Before (the user's draft): "A note on client libraries before this merges.
Here is the analysis from the assistant:" followed by the analysis in a code
block, then the user's own proposal and a cc.

After (the wrong revision): the attribution line was dropped and the analysis
was rewritten in the user's voice.

Right revision: keep the framing and the attribution. Fix only the form (a
`>` quote instead of a code block, which scrolls sideways) and the missing
cc.

What was wrong: the revision changed what the message says about its source,
not only its form. When revising the user's text, keep its framing and
claims, and change only what was asked or what is broken.

### Name the problem first (review comments, "Plain and short")

Feedback: "Can we reword it a bit? I did not understand what the issue is."

Before:

```
Before this PR the four uploads in this loop fail too, just with other errors: "Invalid size" for the number and "Size must be an integer" for the string. Perhaps add `match="exceeds the bucket limit"`, the error the commit message names? Then the loop checks the new limit, not just any error. Adding 99999999999999999999 to the list would also cover the overflow error.
```

After:

```
`pytest.raises(BadRequest)` passes with any error message. Before this PR these uploads fail too, with other messages, so the checks don't show which code rejects them. The commit message says the error is "Size ... exceeds the bucket limit". Perhaps check it with `match="exceeds the bucket limit"`? A number too big for 64 bits, like 99999999999999999999, could also go in the list.
```

What was wrong: the old text opened with a side fact (the uploads failed
before the PR too) and quoted two error strings before saying what was wrong.
The problem itself (no message check) came only at the end, as the reason for
the proposal. The new text names the problem in its first sentence, says why
it matters in the second, then proposes.

### Suggest, don't volunteer (review comments, "Propose what the author could do")

Feedback: "I do not know what my task would be. Why not just suggest what the
author could do?"

Before (last sentence): "Should I send a small follow-up for that, so the fix
doesn't have to touch it?"

After: "Perhaps we could change it that way in this PR, or mention it in
PROJ-512 for whoever fixes it?"

What was wrong: the comment signed the user up for a follow-up the user never
agreed to.

### The comment could not be understood (review comments, "Say the hidden step")

Feedback: "I did not understand anything from this comment." On a second
comment, the reader took a check at the commented line as already covering
the case.

Before: "This loop accepts all 21 formats in `formats::all()`, so
`export_as_raw`, `export_as_hex`, ... (9 names) also become export endpoints.
The exporter converts nothing else to these 9, so ..."

After: "The upstream API has export endpoints for 12 formats only, the ones
`test_export_by_name_all_formats` covers. This loop goes over all 21 internal
formats, so it also accepts names the upstream API doesn't have, like
`export_as_raw` or `export_as_hex`. ..."

What was wrong: the comment opened with nine names and the mechanism before
the reason it matters. The second comment left out the step the whole point
depends on: a name without a namespace gets the default namespace before the
check runs.

### No "in code" paragraph (review comments, "Plain and short")

Feedback: "I do not like a forced 'in code' section in every comment. Also, I
would prefer simpler language."

Before: two paragraphs, the second starting "In code:" with four symbols and
a call path.

After:

```
The PR changed the code that handles resumed uploads, but no test in the PR resumes an upload. That code never runs in them. Could we add such a test?
```

What made it better: three short sentences. What changed, what is missing,
the question. No symbols needed. Keep the plain story and drop the code
paragraph.

### Show where the gap sits (review comments)

Feedback: "The new version is much better. It explains the items more
precisely, so readers get the context, while not being too detailed."

Before:

```
This covers the summed mode. The doc also says the histograms are summed over the workers in per-worker mode, but no test runs the new series there. Perhaps check it in `test_export_metrics_per_worker`: the new histograms without a `worker` label, next to the queue series that have one?
```

After:

```
The new tests run in the default mode, which sums the series per host. `test_export_metrics_disabled` covers the mode with both flags off. Nothing checks the new series in per-worker mode (`enable_per_worker_metrics`). There they differ from the queue series. The counters get a `worker` label, but the histograms are summed over the workers, as `docs/metrics.md` says.

Perhaps add a check to `test_export_metrics_per_worker`, which runs in that mode? The new histograms should have no `worker` label, while the queue series in the same scrape have one.
```

What made it better: it lists all three modes with the test that covers each,
so per-worker mode stands out as the one gap. It says what differs in that
mode, so the reader sees why the gap matters. Pointers became names ("This",
"the doc", "summed mode"; see writing rule 8). The proposal is a short
question, and the expected result is its own sentence.
