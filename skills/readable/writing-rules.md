# House Writing Rules

How the sentences of commit messages, code comments, docs, slides and PR text
should read. The goal is prose that any reader can follow on the first pass,
including readers whose first language is not English. What goes into each
kind of message, and its shape, is in the draft skill.

## Everywhere

1. **Keep sentences short.** One idea per sentence. If a sentence needs a
   breath in the middle, split it.

2. **Use simple, common words.** Prefer the word everyone knows over its
   fancier synonym. "Use", not "utilize". "Before", not "prior to". "Start",
   not "commence".

3. **Use plain verbs, not metaphors.** A verb should describe the mechanism,
   not paint a picture.
   - Avoid: the token travels with the request
   - Use: the token is stored on the request
   - Avoid: the retry budget is anchored at the first attempt
   - Use: the retry budget is counted from the first attempt

4. **No em dashes.** Use a plain " - ", a comma, or a colon instead. This
   applies to everything: commits, comments, docs, slides, notes.

5. **Prefer periods over semicolons.** Where a semicolon joins two thoughts,
   a period usually does it better. This is a lean, not a ban.

6. **State what is, not the history.** Write in present tense. Do not narrate
   how the code got here, and avoid timeline words like "still", "now",
   "no longer", "used to". Two exceptions: a commit message may describe its
   own diff ("X no longer requires Y"), and a regression test may cite a
   tracked bug ("Reproduces issue #NNN").
   - Avoid: originally this threw, later validation was added
   - Use: values outside the range are rejected with a configuration error

7. **Do not name other vendors' products.** Describe the generic idiom
   instead of the product that popularized it. Say "the connection check
   clients and pools send by convention", not the names of specific client
   libraries or databases. Notes about compatibility with a product the
   project follows are the one exception.

8. **Name things, not "X only" or a bare pointer.** "Per worker only" makes
   the reader guess which other split is missing: per tenant, per queue, per
   host? Say it: "had no tenant split". The same goes for pointers: "this",
   "the doc" or a bare term like "summed mode" send the reader to look up
   what they mean. Name the thing ("the new tests", `docs/metrics.md`), or
   define the term in a few plain words ("the default mode, which sums the
   series per host").

9. **Effect before mechanism.** Open with what happens and who notices, in
   the words of the domain: the trigger, the order of events that is wrong,
   what the client or operator sees. Spell out an order with "before" and
   "after". Do not leave it to "at that point". Then place it against what
   the reader knows ("the bug this PR fixes", "not a regression", how rare).
   Add a code symbol only where the reader needs it to find the spot, and
   keep the words simple: "the shutdown cancels the upload" over
   "`shutdown()` calls `cancel_all()`".
   - Avoid: `close()` runs from the "job queue client" cleanup. At that
     point the listener accepts, so the balancer can pick this worker.
   - Use: we close the job queue client before the HTTP listener stops, so
     for a short window the balancer may still pick this worker, and its
     requests get a 500.

## Code comments

10. **Comment only what the code cannot say.** A comment earns its place by
    stating a non-obvious "why" or a side effect invisible at the call site.
    Keep it to 1 to 3 lines. A comment that restates the code is noise, and
    clear short code needs no comment at all.

11. **Prefer restructuring over commenting.** If an expression needs
    explaining, a well-named variable often explains it better than a
    comment would.
    - Avoid: `now + (quota - used) / rate  // when the quota runs out`
    - Use: `auto remaining = quota - used;` then
      `return now + remaining / rate;`

12. **Write only verified facts.** A comment that asserts a mechanism (where
    a value is captured, who owns a lifetime, what sets a field) is a factual
    claim. Read the code that produces it before you write it. A wrong
    comment misleads reviewers and readers, so it is worse than no comment.

13. **No reviewer-directed narration.** Comments like "keeping X in sync
    with Y as the review asked" talk to the reviewer, not the next reader.
    They are noise the moment the change merges. The same goes for docs that
    point at other modules: each module describes only itself, and
    cross-module structure belongs in the commit message.

14. **Do not churn existing text.** Keep pre-existing comments. If a change
    makes one untrue, reword only the untrue part. Do not reformat code that
    did not functionally change. Churn buries the real diff and makes review
    and bisect harder.

---

Compiled from review feedback.
