# Planning Runtime Reference

## Positioning

`planning-runtime` is not a memory system and not a replacement for `work-control`.

It is the runtime control layer for complex execution.

## Boundary summary

- `memory/` and `MEMORY.md` keep continuity and long-term memory.
- `work-system/` keeps formal project and daily records.
- `planning-runtime` keeps execution-state files for one complex task.

## Why it exists

Without a runtime container, complex tasks drift because:
- goals are reassembled from chat each turn
- findings stay scattered
- errors are forgotten or paraphrased
- review lacks stable evidence
- retrospective relies on memory instead of process artifacts

## Core runtime principles

1. Filesystem as execution memory
2. Re-read plan before major pivots
3. Persist errors
4. Separate findings from progress
5. Check completion before stopping
6. Bridge runtime outcome back to formal work records
