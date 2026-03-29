# Project Memory Repo Structure

Use these snippets when a repo needs clearer file placement rules in addition
to better documentation roles.

## Core idea

A durable repo should make it obvious where a new file belongs before the file
is created.

Use a small number of stable homes and make them answer distinct questions:

- `scripts/` or `src/`: where code and CLIs live
- `data/`: where raw, reference, and imported inputs live
- `results/`: where analysis outputs live
- `docs/`: where durable documentation lives

Avoid adding new top-level directories unless an existing home truly cannot fit
the artifact type.

## Branch-root model

For analysis-heavy repos, organize outputs by maintained branch root:

- `results/<branch-root>/`: the home of one maintained analysis direction
- `results/<branch-root>/figures/`: active figures owned by that branch
- `results/<branch-root>/runs/<variant>/`: child variants, parameter sweeps,
  sensitivity reruns, or alternate windows
- `results/<branch-root>/exports/` or `tables/`: branch-owned deliverables when
  needed

One branch root should usually pair with:

- one `ANALYSIS_INDEX.md` row
- one parent `NOTES.md`

Do not create a new root for every minor rerun.

## Placement rules

Use questions like these before creating a new file:

1. Is it executable logic?
   Put it under `scripts/` or `src/`.
2. Is it a raw input, reference, or imported dataset?
   Put it under `data/`.
3. Is it an output owned by one analysis branch?
   Put it under that branch root in `results/`.
4. Is it a child variation of an existing branch?
   Put it under `results/<branch-root>/runs/<variant>/`.
5. Is it a durable cross-branch memory or operating rule?
   Put it under `docs/` or the repo guide.

If none of these answers fit cleanly, the repo structure may need a clearer
rule before more files are added.

## Suggested repo-guide wording

```md
- Keep one durable home for code, one for inputs, one for outputs, and one for
  durable docs. Avoid adding new top-level folders unless an existing home
  truly cannot fit the artifact type.
- Organize outputs by branch root: `results/<branch-root>/` for the maintained
  branch, with child variants under `results/<branch-root>/runs/<variant>/`.
- Co-locate active figures with the branch that owns them instead of saving
  them into a global dumping-ground folder.
- New generated files should be placed by ownership first: code with code,
  inputs with data, branch outputs with their branch root, and cross-branch
  memory in durable docs.
```

## Smells that structure is drifting

- people keep asking where a new file should go
- one artifact type appears under multiple unrelated roots
- top-level folders are created for one-off outputs
- active figures are saved in a global curation folder
- sibling variant directories each grow their own notes and mini-systems
