# Design Checklist

Questions to answer before writing code, and to ask of a change in review.
Most items will not apply to a given change. Say so in one word and move on.

This is the general list. A project checklist skill, when one is installed
for the project, replaces it (see `SKILL.md`).

## Checklist

### A. Problem and scope

1. **What does a user see change?** Results, error messages, defaults,
   config, metrics, performance. A visible change needs docs and a line in
   the PR description. Docs that stop being true are fixed or removed.
2. **Root cause or defense?** Name the line where the behaviour first goes
   wrong. A check where the symptom shows up is a defense layer: fine as an
   extra, but say which of the two the change is.
3. **Every path into the changed code.** Same bug, all paths, same PR. Pairs
   that usually differ: cached and uncached, first call and repeated call,
   local and remote, single and batch, sync and async, first page and later
   pages, top-level and nested, each public interface that reaches the code.
   Special paths that copy shared logic (a dump, an internal call) miss later
   fixes: move them onto one helper. Shortcut predicates miss variants.
4. **A new path repeats every check of the old one.** Validation,
   permissions, paging, limits, routing. A cheap way to find the gaps: run
   the existing test suites with the new path as the default. Where the new
   path differs by design, write it down.
5. **Is there a realistic scenario?** A fix for a case no real workload or
   operator hits gets rejected. Say how a real deployment gets there.
6. **Does it need to exist, in this shape?** If a maintainer may answer
   "won't do", ask before building. Is it the best solution, or just one
   that works? Reuse existing machinery over a parallel implementation, even
   at a small cost. Every guard and special case must be needed: is the
   combination it rejects planned to be supported, and does rejecting it
   break normal clients?
7. **Is it worth it?** For an optimization: the gain on production-like
   data, the memory cost, and a fair benchmark. Prefer a better worst case
   over a better average when the bad case outlives its cause.

### B. Runtime: concurrency, memory, shutdown

8. **Who owns the state?** Which thread, task, process or node. Access from
   elsewhere goes through the owner. No shared mutable state without a clear
   rule. When the work runs somewhere else, move there once and use the
   state there, instead of carrying pointers back and forth.
9. **Can it block or stall?** Every loop over user-sized input yields or is
   bounded, including parsing, the error path, and freeing large structures.
   Nothing quadratic on user input, including hidden linear costs inside a
   loop. No blocking call on a thread that must stay responsive.
10. **Is recursion bounded on the stack it runs on?** Check the real stack
    size, do not assume it. User-controlled nesting needs a depth limit with
    a clear error.
11. **Is memory bounded?** Large single allocations sized by user input, and
    copies of large user values. Concurrent work needs a limit on how much
    memory it can hold. Backpressure works both ways: a bounded request
    queue with unbounded responses piling up still runs out of memory.
12. **Which priority or resource group runs it?** Work handed to a shared
    long-lived thread or queue runs with the settings of whoever started
    that thread, not of the caller, unless the code passes them on.
13. **Background work and shutdown.** Background work is tracked, shutdown
    waits for it, and unbounded work can be cancelled. Services stop in the
    right order. What happens if startup aborts halfway, a restart follows
    an interrupted one, or a request arrives during shutdown? No new global
    singleton: pass dependencies in, so the start order stays visible.
14. **Errors on the hot path.** An error that is part of normal operation
    (validation failures, a connection storm) should be cheap: return it
    where throwing is slow. Throwing is fine for errors that almost never
    happen.

### C. Versions, stored state, failures

15. **Mixed versions.** During a rolling upgrade, old and new instances talk
    to each other. Is the new behaviour gated until all are upgraded, and is
    the behaviour right before that? What does an old instance do with a new
    field, message or column? Can the deployment roll back? Does it need an
    upgrade test?
16. **Wire and on-disk formats.** A type change in a serialized structure is
    a format change unless both types encode the same.
17. **Data that exists today.** Never reject what is accepted today:
    existing schemas and stored values that break a new rule keep working.
    Deployments that already hit the bug: does the fix help them, or do they
    need a manual step and a release note?
18. **Can a stored value break things later?** Values that are stored and
    read back later (at load, replay or restart), often by every instance.
    Validate at write time, where a bad value is a user error and not a
    crash.
19. **Where does the state live?** A database, a replicated log, a local
    file, memory only. After a change, does a reader elsewhere see it at
    once, or does it have to wait or sync first? Slow work inside a step
    that others wait on can make them time out.
20. **Windows of empty or stale state.** Between startup steps, in-memory
    state can be empty. Prefer a positive list ("known safe") so an empty
    set means unsafe. A snapshot copied from live state freezes it. Does the
    fix turn off an existing optimization?
21. **Acknowledged or applied?** A write that is acknowledged may not be
    visible everywhere yet. Readers and tests that need the applied state
    wait for it.
22. **Changes of membership or placement during the operation.** Is the set
    of instances or the location of the data read once and then stale? A
    background balancer can move things between two steps of a test.
23. **Failures.** An instance down, a timeout, a network partition. Are
    retries safe to repeat? Which error does the client get?
24. **Races.** A decision made on a snapshot and acted on later without a
    recheck (read, then unconditional delete). State captured at request
    start and used after a suspension point. An object deleted or altered
    during the operation. When reported numbers do not add up, ask when the
    inconsistent state happens: it can point at a wrong decision rule, not
    only at a reporting gap.

### D. Interfaces

25. **Compatibility.** Where the project follows another system or a spec:
    does that one do the same, and in which version? A difference is
    deliberate and written down.
26. **Errors.** The same error type as the neighbouring checks, so the
    client gets the right error code, never an internal error for a user
    mistake. The same goes for timeouts and lost connections on internal
    calls. A specific message, the same on every path. A refactor of
    validation keeps the specific message. Two different failures get two
    messages a user can tell apart. "Not yet supported" promises support:
    use it only when it is planned.
27. **Broken invariants.** What happens when "can't happen" happens? Abort
    only when going on would corrupt data. Otherwise fail the one operation.
    Log only what can safely be ignored.
28. **Untrusted input.** Input from any outside interface or a config
    template is validated, and escaped where it is inserted into another
    language (a query, a filter, a URL, JSON). Sizes are checked before
    buffers are used.
29. **Name and overload resolution.** Several exact matches are ambiguous.
    Duplicates of one candidate are not. A new built-in name can hide a
    user-defined one with the same name.
30. **Config.** Is an option needed at all? Its default. The same on all
    instances or per instance. Changeable at run time or not. A bad value at
    start fails startup, a bad live value keeps the last valid one. A new
    default applies to new objects only, and an explicit value wins. Tools
    that read the config know the option.
31. **New limits.** Applied to user input only, or also to internal callers,
    loading of existing data, and tools? When two instances disagree, whose
    value applies? One deployment-wide option is simpler than passing the
    sender's value along.
32. **Observability.** Metrics: name, labels, cost per label value, and the
    metrics docs. Tracing for the request path. Log levels that do not
    flood.
33. **Other surfaces.** Admin API, command-line tools, generated output
    (dumps, describe output), client libraries.

### E. Tests and delivery

34. **Test layer.** The lightest layer that reaches the behaviour: tests
    through the public interface first, unit tests only for what those
    cannot reach, multi-instance tests only for more than one instance. The
    test owns its signal: a counter of its own object, not a global one that
    other tests move too. A case that an existing fault injection can reach
    gets a test. A case that needs a new injection is never dropped
    silently: ask the user, who decides per case whether to add one. Tests
    check observable state, never log lines. One test per distinct code
    path, not one per input value that takes the same path.
35. **Reproducer first.** For a bug: a commit with the test marked as
    expected to fail, then the fix removes the marker. The repro is run on a
    build without the fix. Preparatory commits (item 36) may come before the
    reproducer or between it and the fix.
36. **Commit split.** Every commit builds and passes its tests. Where does
    each part of the design go? Aim for a series that tells a story: a few
    small preparatory commits (a refactor with no behaviour change,
    plumbing, making a service safe for a new order), each reviewable on its
    own, so that the fix at the end is small and obvious. Reproducer plus
    fix is the minimum shape, not the default one. Not every change needs
    preparation. No commit changes code that a later commit of the same
    series changes again. Moving tests between suites goes in stages: copy
    unchanged and disabled, then change, then enable. No commit leaves a
    test in neither suite.
37. **Backport.** Where the project has release branches. By severity: a
    crash that any user can trigger, yes. Performance, mostly no. Which
    branches have the bug, and do the code path and the test exist there? A
    backport wants a small change.
38. **Performance.** Is it on a hot path? If the design is about speed,
    plan the benchmark before coding.
