# Code Checks

Line-level checks for a review by hand (the light review), and for judging
the findings of `/code-review`. Design-level questions (scope, upgrades,
compatibility, tests) are in the design skill's `design-checklist.md`.

The checks below are general. A project code checks skill, when one is
installed for the project, replaces the "Checks" section. The "before
flagging" rules always apply.

## Before flagging

- Review only the changed lines. A problem in older code that the change
  makes worse counts. One it does not touch goes to the notes, not the
  review.
- Be certain. Read the whole function, its callers and the types involved.
  Look at how nearby code does the same thing before saying it does not fit.
- Give the realistic scenario: what input or timing gets there, and what
  goes wrong. No scenario, no finding.
- Check a convention in the code before calling something a violation.

## Checks

### Lifetimes

1. **Captured references.** A callback, closure or task that captures a
   local by reference, or an object that may be destroyed, can outlive it.
   Move or copy into the capture.
2. **References across a suspension point.** An iterator, pointer or
   reference into shared state can be invalidated by other code while this
   code is suspended (an `await`, a callback, a released lock).
3. **Moves and views.** A view, slice or pointer into an object dangles
   after the object is moved or reallocated. Watch structs that hold both
   the storage and views into it.

### Async work

4. **Dropped results.** A task, future or promise that nobody waits for
   loses its error, and shutdown does not wait for the work.
5. **Two ways to fail.** A function that reports errors through its return
   value (a future, a result type) should not also throw: callers that
   handle only one way miss the other.
6. **Long loops.** A loop over user-sized input, on a thread that must stay
   responsive, yields or is bounded.

### Memory and copies

7. **Hidden costs on hot paths.** Allocations, copies where a move or a
   reference would do, type erasure, an extra wrapper layer.
8. **Large allocations.** A container that grows with user input in one
   contiguous block.

### Errors and invariants

9. **Error type.** User errors use the same error type as the neighbouring
   checks, so the client gets the right error code.
10. **Invariant checks.** Abort only when going on would corrupt data.
    Otherwise fail the one operation.

### Safety

11. **Bounds.** Sizes from input checked before use, correct lengths in
    copies, no out-of-bounds index.
12. **Casts.** Unchecked casts need a reason. Narrowing conversions of sizes
    and counts are checked.
