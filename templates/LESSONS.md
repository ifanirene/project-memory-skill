# Repository Lessons

> This file is distilled project memory, not a run log.
>
> Keep only lessons that are durable enough to change future work in this repo.
>
> Use `ANALYSIS_INDEX.md` to find the right branch and `NOTES.md` to
> understand what happened there.

## Theme Index

- `Cross-theme`: reusable operations and provenance checks

## Cross-theme

- Check: Before trusting a provenance-sensitive analytical output, validate its
  `analysis_manifest.json`, because note prose and script defaults do not bind
  the exact code, inputs, resolved parameters, outputs, and validation.
- Preference: When creating a normal-sized variant, keep outputs flat inside
  the variant directory, because artifact-type subfolders add navigation cost
  without improving provenance.
