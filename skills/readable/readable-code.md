# Readable Code: Guidelines and Examples

Goal: code, tests, comments and messages that a human reviewer understands on
the first read, without decoding. Correct and short is not enough. A reviewer
who has to stop and work out what a line does will ask about it, and the
next reader pays the same cost.

This file is part of the readable skill. It grows from real review feedback.
The feedback itself is recorded in a local log (see `SKILL.md`). The rules
here and the invented examples at the end are what was learned from it.

For prose (commits, comments, docs) the house rules are in `writing-rules.md`,
next to this file. This file does not repeat them.

## Why this keeps happening

Code written by a model tends to fail human readers in the same few ways:

- **Compression.** A comprehension, `zip`, loop or helper replaces two or three
  plain lines, to avoid repetition. A model reads both forms at the same speed.
  A human reads the repeated plain lines faster.
- **Hedged expectations.** When the exact value was not measured, the test
  asserts a property instead ("non-zero", "equal to some other computed
  list"). The reader then has to work out what values are possible.
- **Too much at once.** Long docstrings and comments that explain every step,
  in dense, precise vocabulary. Each sentence is true, but the overview is lost.
- **Abstract names.** Names that describe the data structure (`errors_after`,
  `outcome`, `info`) instead of the thing in the domain (`upload_errors`,
  `refused_download`).

## Rules for code

1. **Repeat instead of compressing small sets.** For two or three items, write
   one plain line per item. Use a loop or comprehension only when there are
   many items or the count varies.
2. **Literal expected values.** Measure, then assert the exact number or
   string. If the number needs explaining, add a one-line comment above it
   (`# The client retries a refused request one time.`). Do not compute the
   expected value in the assertion.
3. **Counts in digits, next to the line they explain.** Do not stack count
   words in prose ("retries once, so twice, each of the two twice"). State the
   reason once, then put the arithmetic at the end of each assert line
   (`== 4  # 2 downloads, 2 attempts each`).
4. **Different numbers for different quantities.** If a test has 3 replicas,
   do not also make 3 writes: "3 writes applied 3 times on 3 replicas" can be
   read as 3, 9 or 27. Pick values that cannot be confused (2 writes, 3
   replicas, so each replica applies 2 entries).
5. **Fresh baseline per step.** When a test checks several steps, read the
   counter again right before each step and assert that step's own change
   (`== 0`, `== 1`). Do not carry a total from an earlier step.
6. **Wait and check together.** When a test waits until a value reaches a
   minimum and then asserts the exact value, keep both in one loop and say
   what the exact check adds (`# Not more: each entry is counted once.`).
   Split apart, the second check looks redundant.
7. **One idea per line.** No nested f-strings, no arithmetic inside calls, no
   chained indexing like `name.split(".")[1]` in an assertion. Name the piece
   first. Run a query on its own line and store the rows: no query inside a
   comprehension, a `for` header or an assertion. A comprehension over rows
   already in a variable is fine.
   In C++, no `if` with an initializer (`if (auto x = f(); !x)`): declare the
   variable on its own line, then test it.
8. **Names carry the meaning.** Use the domain word, and put the number that
   matters in the name when the test is about numbers (`doc_31`, "31 levels").
   Name a library object by what it does here (`no_retry =
   PassThroughPolicy()`). When a comment explains a default, say what the
   code does about it and why, not only what the default is.
   Name a local after what happens in its own function, not after a step in
   the caller, and keep one prefix per kind of value (a reading, an amount).
9. **Self-contained test cases.** One block per case, a fresh object, a short
   comment that states the expected outcome. Prefer this over a table of cases
   fed through generic code, unless the cases are many and truly uniform. In a
   test longer than about 20 lines, split each case into phases (set up,
   pause, act, check) with a blank line and a one-line comment that says what
   the phase is for. Reading only the comments should give the outline.
10. **No new machinery for one use.** No helper, fault injection point or
   parameter for a single caller or a single test case, unless it is clearly
   needed. Say "reproduced locally" in the PR instead of adding a one-off
   injection.
11. **One flagged spot means a sweep.** When a reviewer flags one place, fix
   every place in the diff with the same pattern, not only the flagged line.
12. **Readable, not slower.** Do not trade a real optimization for readability
   (a 1 s timeout instead of a 10 ms one). Keep the fast path and make it
   readable: plain inputs, a named inner helper, a loop condition that says
   when it stops.
13. **Read it as a stranger.** Before showing code, reread each changed line as
   someone who did not write it. Anything that needs a second look gets
   renamed, split or unrolled.

## Rules for comments and messages (short form)

- Overview level: say what the code is for and why, not each step.
- Effect before mechanism: what happens and who notices, then the code path.
- 1 to 3 lines. If it needs more, restructure the code instead.
- Only verified facts. A wrong comment is worse than none.
- Messages: proportional to the change, cover the whole diff in few lines.
- Full rules: `writing-rules.md`.

## Checklist before showing code

- [ ] Any comprehension, `zip`, `map` or loop over 2-3 items? Unroll it. (1)
- [ ] Any assertion with a computed or vague expected value? Measure, make it
      literal. (2)
- [ ] Count words piled up in a comment? Digits, at the line they explain. (3)
- [ ] The same number used for two quantities? Change one of them. (4)
- [ ] A total carried over from an earlier step? Take a fresh baseline. (5)
- [ ] A wait split from its exact check? Keep them together, say what the
      check adds. (6)
- [ ] Any line that needs a helper's body or a second look? Name the piece,
      rename, or split. (7, 8)
- [ ] A query inside a comprehension, `for` header or assert? Fetch the rows
      into a variable first. (7)
- [ ] An `if` with an initializer (`if (auto x = f(); !x)`)? Declare `x` on
      its own line, then test it. (7)
- [ ] A test over about 20 lines without blank lines and phase comments? Do
      the comments alone give the outline? (9)
- [ ] Any new helper, flag or injection with one user? Remove it, or justify
      it. (10)
- [ ] Each fix applied to every place in the diff with the same pattern? (11)
- [ ] Any optimization lost for readability? Keep it, make it readable. (12)
- [ ] Comments: overview, 1 to 3 lines, verified? Docstring shorter than the
      test?
- [ ] Diff minimal: no reformatting, no churn in lines we did not need to touch.
      Existing code that must be reindented (wrapped in a new block) gets a
      separate reindent commit after the change, so the change diff stays small.

The checklist runs on every test before it is shown, also on a test added
late in a session. Having the rules loaded is not the same as having checked.

## Examples

The examples are invented. Each one mirrors real review feedback: the same
lesson and the same before/after shape, in made-up code about a file storage
service (buckets, uploads, downloads, mirrors that keep copies). "Feedback"
is what the reviewer said, in general words.

### Code and tests

#### A `zip` for two counters (rules 1, 2)

Feedback: "For a model this is probably perfectly readable, for a human not
really. There is no need for `zip` over 2 counters."

Before:

```python
errors_before = [await get_counter(app, name) for name in (UPLOAD_ERRORS, DOWNLOAD_ERRORS)]
...
counters = await app.counters()
errors_after = [counters.get(name) or 0 for name in (UPLOAD_ERRORS, DOWNLOAD_ERRORS)]
over_quota = [counters.get(name, reason="over_quota") or 0 for name in (UPLOAD_ERRORS, DOWNLOAD_ERRORS)]
assert all(over_quota), "the refusal was not counted as over_quota"
assert [after - before for after, before in zip(errors_after, errors_before)] == over_quota, \
    "the refusal was counted under another reason"
```

After:

```python
# The client retries a refused request one time.
counters = await app.counters()
assert counters.get(UPLOAD_ERRORS, reason="over_quota") == 2    # 1 upload, 2 attempts
assert counters.get(DOWNLOAD_ERRORS, reason="over_quota") == 4  # 2 downloads, 2 attempts each
# No refusal is counted under another reason.
assert counters.get(UPLOAD_ERRORS) == 2
assert counters.get(DOWNLOAD_ERRORS) == 4
```

What was wrong: three list comprehensions and a `zip` for two counters
(rule 1), and a vague expectation (`all(...)`, "non-zero") because the real
counts were never measured (rule 2). Measuring showed exact, stable counts,
which made the plain form possible.

#### Tuple helpers and tuple asserts (rule 1)

Before: `assert counts() == (uploads_before + 2, downloads_before + 1)`, with
a helper that returns both counters as a tuple.

After: one helper and one assert per counter.

What was wrong: the reader has to match positions in two tuples to see which
number belongs to which counter.

#### Count words piled up (rule 3)

Feedback: "'Refuses twice, and each of the two twice.' I cannot tell which
number goes with which request."

Before:

```python
# The client retries a refused request once, so the server refuses the
# upload twice and each of the two downloads twice.
assert counters.get(UPLOAD_ERRORS, reason="over_quota") == 2
assert counters.get(DOWNLOAD_ERRORS, reason="over_quota") == 4
```

After:

```python
# The client retries a refused request one time.
assert counters.get(UPLOAD_ERRORS, reason="over_quota") == 2    # 1 upload, 2 attempts
assert counters.get(DOWNLOAD_ERRORS, reason="over_quota") == 4  # 2 downloads, 2 attempts each
```

What was wrong: four count words (once, twice, two, twice) in two lines, so
the reader has to untangle which number goes with which request.

#### The same number for two quantities (rule 4)

Feedback: "Is it 3 uploads x 3 mirrors x 3 copies each, or 3 uploads, so 3
files on each of the 3 mirrors?"

Before (docstring, with `for n in range(3)` and `== 3`):

```python
"""
Verify that every mirror counts the files it copies: 3 uploads to a bucket
with 3 mirrors are copied 3 times on each mirror.
"""
```

After (two plain uploads and `== 2`):

```python
"""
Verify that every mirror counts the files it copies: after 2 uploads, each of
the 3 mirrors has copied 2 files.
"""
```

What was wrong: 3 uploads and 3 mirrors, so every "3" in the sentence could
be either one.

#### Positional literals with the same value (rules 2, 4, 5, 7)

Before:

```python
[source_disk] = [disk for mirror_id, disk in copies if str(mirror_id) == source_id]
move = asyncio.create_task(admin.move_copy(bucket, name, source_id, source_disk, target_id, 0, 0))
assert refusals_after == refusals_before + 2
```

After:

```python
disk_of = {str(mirror_id): disk for mirror_id, disk in copies}
move = asyncio.create_task(admin.move_copy(
    bucket, name, src_mirror=source_id, src_disk=disk_of[source_id],
    dst_mirror=target_id, dst_disk=0, priority=0))
assert refusals_after - refusals_before == 2  # 1 via the source mirror, 1 via the target
```

What was wrong: positional literals with the same value but different
meanings (`0, 0` for a disk and a priority) need keyword arguments (rule 4).
A filter with list destructuring needs a second look (rule 7). Assert the
step's change, not `before + n` (rules 2, 5).

#### A total carried over from an earlier step (rule 5)

Feedback: "Maybe read the counter again here, and assert that the difference
is 0?"

Before:

```python
assert upload_count() - uploads_before == 2
assert download_count() - downloads_before == 1

# An upload of another tenant is not counted for this tenant.
other_tenant.upload("b.txt", data)
assert upload_count() - uploads_before == 2
```

After:

```python
# An upload of another tenant is not counted for this tenant.
uploads_before = upload_count()
other_tenant.upload("b.txt", data)
assert upload_count() - uploads_before == 0
```

What was wrong: the second step repeated the first step's total (`== 2`), so
the reader has to remember where 2 came from to see that the step added
nothing.

#### Wait and check split into two loops (rule 6)

Feedback: "Isn't the second loop redundant? If the first one waits for 2 or
more, what does the second one guard against?"

Before:

```python
for mirror in mirrors:
    async def all_copied():
        return await copied_files(mirror) >= 2 or None
    await wait_for(all_copied, deadline, label=f"{mirror} to copy 2 files")

for mirror in mirrors:
    assert await copied_files(mirror) == 2
```

After:

```python
for mirror in mirrors:
    # A mirror may copy the files after the uploads have returned.
    async def all_copied():
        return await copied_files(mirror) >= 2 or None
    await wait_for(all_copied, deadline, label=f"{mirror} to copy 2 files")
    # Not more: each file is counted once.
    assert await copied_files(mirror) == 2
```

What was wrong: split into two loops, the exact check looks redundant. Kept
together, with one comment each, the reader sees that the wait tolerates a
late mirror and the assert catches a file counted twice.

#### A query inside a comprehension (rules 7, 11)

Feedback: "It would be easier to fetch the rows first, then assert. These
'something for item in collection' lines are harder for humans when there is
more logic inside. Over a variable that is already fetched, it is fine."

Before:

```python
assert sorted(row.name for row in await db.fetch(f"SELECT name FROM {table}")) == names_before
```

After:

```python
rows = await db.fetch(f"SELECT name FROM {table}")
names_after = sorted(row.name for row in rows)
assert names_after == names_before
```

What was wrong: one line ran a query, transformed the rows and compared them,
so the reader had to unpack it from the inside out. The sweep also fixed
`for row in await db.fetch(...)` loop headers and asserts of the form
`assert [row.id for row in db.fetch(...)] == [1]`.

#### An `if` with an initializer (rules 7, 11)

Feedback: "Avoid these complex ifs. First assign the result, then test it."

Before:

```cpp
if (auto parsed = parse_header(std::move(line)); !parsed) {
    return make_error(std::move(parsed).error());
}
```

After:

```cpp
auto parsed = parse_header(std::move(line));
if (!parsed) {
    return make_error(std::move(parsed).error());
}
```

What was wrong: one line called a function, named its result and tested it,
so the call that does the work was hidden inside the condition. The same
shape was in three more places of the series. A `case` without braces needs
them once the variable is declared in it.

#### An expression that needed a comment (rule 7)

Before: `return now + (quota - used) / rate;  // when the quota runs out`

After:

```cpp
auto remaining = quota - used;
return now + remaining / rate;
```

What was wrong: the comment explained a piece of the expression. A named
variable explains it better, and the comment is not needed.

#### A library object with an unexplained name (rule 8)

Feedback: "I do not understand this policy. Does it mean that we do not
retry, and that is what we want here?"

Before:

```python
# Without PassThroughPolicy the client retries a refused request once.
with pytest.raises(OverQuota, match="bucket b1 is over its quota"):
    await client.upload("b1", "a.txt", data, retry_policy=PassThroughPolicy())
```

After:

```python
# The client retries a refused request one time by default.
# Without retries, each request is refused and counted once.
no_retry = PassThroughPolicy()
with pytest.raises(OverQuota, match="bucket b1 is over its quota"):
    await client.upload("b1", "a.txt", data, retry_policy=no_retry)
```

What was wrong: the comment stated the default and left the reader to work
out why the test avoids it, and the class name does not say "no retry". Two
more tests had the same policy with no comment at all. Each got its own true
reason.

#### Names that lean on another function (rule 8)

Feedback: "Two 'after's, and nothing here says what each one means. I
expected `used_before_unpack`, so the name does not depend on the order in
another function."

Before:

```python
used_after_download = disk_used()
unpack(archive)
used_after = disk_used()
download_used = archive.reported_size or (used_after_download - used_before_download)
report(download_used + (used_after - used_after_download))
```

After:

```python
used_before_unpack = disk_used()
unpack(archive)
used_after_unpack = disk_used()
download_size = archive.reported_size or (used_before_unpack - used_before_download)
unpack_size = used_after_unpack - used_before_unpack
report(download_size + unpack_size)
```

What was wrong: a local was named after a step in the caller (the download),
so the reader had to know the caller's order. Two names said "after" for
different points, and "used" meant a reading in one name and an amount in the
next. Name a local after what happens in this function, and keep one prefix
per kind of value (`used_<when>` a reading, `<what>_size` an amount).

#### Names must stay true after a change (rules 8, 11)

Feedback: "If an expired token can still be refreshed, we should not call it
an expired-token error."

Before: `expired_token_error()`, and commit titles "... for a session with an
expired token", after the rule changed to "expired and past the refresh
window".

After: `session_ended_error()`, and titles "... for a session that has
ended". Names that only time the token (`token_age()`, `track_expiry()`)
stay.

What was wrong: a design change narrowed when the function returns an error,
and its name and the commit titles kept describing the old, wider condition.
When a condition changes, sweep every name, title and message that states it.

#### Numbered names, assembled messages, derived values (rules 2, 7, 8)

Feedback: "You understand it, but human reviewers will have a hard time if it
is convoluted." Four lines flagged in one test file about nesting depth.

- Numbered names (`a_31`, `b_32`) confused once an object changed depth.
  Better: short names (`doc`, `field`, `wrapper`) with an end-of-line count
  (`# doc + 30 lists = 31 levels`). Rule 8.
- Expected messages assembled from fragments. Better: spell out each message
  in full. Rule 2.
- A derived expression, `name.split(".")[1]`, in an assertion. Better: fix
  the inconsistency at the source so the test can use a literal. Rule 7.

#### A long test without an outline (rule 9)

Feedback: "This test is big. Add empty lines and a comment for each logical
section, so a human gets an overview of the test without reading every line."

Before (each case, 15 lines with no blank line):

```python
# The bucket is gone before the requests check the quota.
await admin.create_bucket("b1")
...
pause = "pause_before_quota_check"
await admin.enable_pause(server, pause)
upload, download = start_upload_and_download("b1")
# Both requests wait at the same pause.
await admin.wait_for_paused(server, pause, count=2)
await delete_bucket_and_release("b1", [pause])
with pytest.raises(ServerError, match=...):
```

After:

```python
# Case 1: the bucket is gone before the requests check the quota.
...

# Pause both requests at the same point, before the quota check.
...

# Delete the bucket, then release the requests.
await delete_bucket_and_release("b1", [pause])

# Both fail, and each is counted once as bucket_deleted.
```

What was wrong: the comments explained single lines, so a reader had to read
every line to find where one phase ends and the next begins.

#### A table of cases fed through generic code (rules 2, 5, 9)

Feedback: "Two blocks, but with a common helper function."

Before: a table of cases and a `Counter`, run by one generic loop. One case
paused both requests at one point, the other at two. The expected error was
`(NotFound, ServerError)` with a three-way regex.

After: two explicit blocks that share `start_upload_and_download()` and
`delete_bucket_and_release()`. Each block has the measured `ServerError` and
its full message, takes its own baseline, and asserts `== 1`.

What was wrong: the reader had to run the generic loop in their head for each
row of the table. A first draft of the blocks asserted cumulative totals (1,
then 2), which rule 5 replaced.

#### A fault injection for one test (rule 10)

Feedback: "Add injections sparingly. If it is not really needed, make the fix
and say in the PR description that it was reproduced locally."

What was wrong: a new fault injection point in two production functions,
added only to test one narrow case.

#### Only the flagged test was fixed (rule 11)

Feedback: "Did you make all the tests more readable, or just the one I
mentioned?"

What was wrong: only the flagged line was fixed. The same patterns
(tuple-returning helpers, tuple asserts, loops over two items, a generic
retry helper) were in five more tests of the same PR.

#### Readable, not slower (rule 12)

Feedback: "Do not switch to 1 s. Write a helper or two. 1 s instead of 10 ms
is a big cost. Make it reasonable."

Before (callers passed request factories, 8 parameters):

```python
timeout_ms = 10
while True:
    before = (await app.counters()).get(counter, reason=reason) or 0
    with pytest.raises(error):
        await client.send(make_request(timeout_ms))
    if ((await app.counters()).get(counter, reason=reason) or 0) > before:
        return
    assert timeout_ms < 5000, f"no {reason} counted"
    timeout_ms *= 2
```

After (callers pass a plain path):

```python
async def timeouts() -> int:
    counters = await app.counters()
    return counters.get(TIMEOUTS, reason=reason) or 0

timeout_ms = 10
while timeout_ms <= 5000:
    timeouts_before = await timeouts()
    with pytest.raises(error):
        await client.download(path, timeout_ms=timeout_ms)
    if await timeouts() > timeouts_before:
        return
    timeout_ms *= 2
pytest.fail(f"no {reason} timeout counted for {path}")
```

What was wrong: the first readable version replaced the 10 ms timeout that
doubles with a fixed 1 s one. Keep the fast path and make it readable: plain
inputs, a named inner helper, a loop condition that says when it stops.

#### The checklist skipped on late tests (checklist)

Feedback: "Did you check that the tests follow the readable guidelines?"

What was wrong: three tests were written and shown with the rules loaded, but
without the item-by-item checklist pass. The pass then found six things.

### Comments and prose

#### Comments too detailed (overview level)

Feedback: a maintainer with many years on the code base could not follow
comments that listed buffers, quotas and retry steps one by one.

What was wrong: every step was explained and the overview was lost. Write a
short overview of what happens. A good overview is not a detailed one.

#### A header heavier than its function (writing rule 10)

Feedback: "This behemoth."

What was wrong: an 11-line header comment on a function that was readable
without it. Clear short code needs no comment.

#### A sentence squeezed until it stopped making sense (writing rules 1, 9)

Feedback: "What does this sentence mean?"

Before: "An upload paused while the bucket policy changes still succeeds, but
is not indexed, so the first search gets NOT_FOUND." It was the result of
cutting a description to half its length.

After: "If the bucket policy changes while an upload is paused, the client
still gets its success response, but the file is not added to the search
index. The first search does not find the file, and the next index run adds
it."

What was wrong: to save words, the actors were dropped. "An upload ... still
succeeds" hides who answers whom, "is not indexed" hides what is not indexed,
and the sentence stops before the part that tells the reader it is harmless
(the next index run adds the file). A participle ("paused while the bucket
policy changes") carried the condition. When a text has to get shorter, cut
whole sentences or points. Do not squeeze the words out of the ones that stay.

#### A chain of internal terms (writing rules 1, 2, 9)

Feedback: "This does not feel readable enough, though maybe I just do not
know the area well enough."

Before: "The closed pool fails that checkout ("pool is closed"), `flush()`
reports it as a sink error, and the worker reports a fatal error."

After: "With the connection pool closed, the checkout fails ("pool is
closed"), and so does `flush()`. The worker treats any `flush()` failure
other than a cancel as lost data, and exits."

What was wrong: one sentence chained three steps named by internal error
types ("sink error", "fatal error") and never said why they end in a crash.
The rewrite says the rule that matters in plain words (only a cancel is a
quiet failure), which also explains why the fix works.

#### Bare pointers (writing rule 8)

Before: "This covers the summed mode. The doc also says the histograms are
summed over the workers in per-worker mode, ..."

After: "The new tests run in the default mode, which sums the series per
host. ... as `docs/metrics.md` says."

What was wrong: "This", "the doc" and "summed mode" made the reader look up
what they point at.

#### Which split is "only" (writing rule 8)

Feedback: "Does this mean the import job splits per tenant and per bucket,
and we split only per tenant?"

Before (commit message): "The export job's counters were per worker only,
while the import job also splits its counters by tenant."

After: "The export job's counters had no tenant split, while the import job
splits its counters by tenant."

What was wrong: "per worker only" was read against another dimension
(buckets), so the sentence suggested that the import job splits per bucket.

#### Effect before mechanism (writing rule 9)

Feedback: "What you wrote in the chat summary is much more readable than the
comment." The request was a mix of the two, closer to the chat wording.

Before (posted comment): "When startup aborts during `register()` (SIGTERM
or an exception), `close()` runs from the "job queue client" cleanup. At that
point the listener accepts and the balancer knows the worker, so ..."

After (chat summary): "If a worker's startup is aborted partway, the job
queue client is closed before the HTTP listener stops. For that short time
the balancer still sends requests to the worker, and they get a 500. That is
the original bug. It is not a regression ..."

What was wrong: the comment opened with code locations and made the reader
work out the order of events ("at that point") and the effect. The summary
says the wrong order with "before", the effect for the client, and how it
relates to the PR.

#### Simpler words (writing rule 9)

Feedback: "I would prefer simpler language."

Before: "`shutdown()` calls `cancel_all()` before it waits", and "has the
index, the cache and `store::close()` left to run".

After: "the shutdown cancels the upload", and "the shutdown has a lot of work
left".

What was wrong: the sentences were lists of symbols. Plain words say the
same, and the author of the code can ask for the details.

#### A commit message that lists everything (messages)

Feedback: "Huge. This is visible from the diff, there is no need to mention
everything."

Accepted shape for a commit that adds tests: the bug in three lines, the
shared recipe of the tests in one sentence, one bullet per case.
