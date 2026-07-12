# New and Monitored Repository Modes

Choose the mode before changing a repository.

## New repository

Use new-repository mode when the project has no established memory contract or
output organization. Set up a computational-biology workspace that can support
multiple scientific goals and analysis types:

```text
repo/
├── AGENTS.md
├── ANALYSIS_INDEX.md
├── config/
├── data/
│   ├── raw/
│   ├── external/
│   ├── interim/
│   └── processed/
├── scripts/
│   ├── preprocessing/
│   ├── analysis/
│   ├── visualization/
│   └── utils/
├── notebooks/
├── results/
│   └── <goal>/<analysis>/runs/<variant>/
├── docs/
│   ├── LESSONS.md
│   └── pipelines/
└── tests/
```

List this tree and its ownership rules in `AGENTS.md`. Create only the common
homes; do not invent goal, analysis, or variant folders before real work exists.
Create a `.gitignore` that ignores data and generated outputs while tracking
`NOTES.md` and `analysis_manifest.json` files under `results/`.

## Monitored repository

Use monitored-repository mode when the repo already has a memory contract,
maintained analyses, or collector registration. Preserve its established
scientific organization unless a move is separately justified.

Audit for drift rather than applying the new-repo tree wholesale:

- stale or missing role statements in `AGENTS.md`
- protected instructions at risk of accidental removal
- duplicate or legacy output roots and unclear branch ownership
- analysis notes used as chronological logs
- lesson feeds that are not distilled decision guidance
- complex active variants without required manifests
- manifests ignored by Git, invalid manifests, or competing metadata formats
- an index that lists minor reruns rather than maintained branches

Repair the smallest governing contract first. Then clean one or two bounded
branches per maintenance run. Do not move large legacy trees, rename outputs,
or generate fake manifests merely to resemble a new repo.

`topic_analysis` is the model for this mode: it already has an index, lessons,
many maintained outputs, legacy `results/output/`, 12 direct variant
directories below `runs/` (plus deeper output subdirectories),
and several ad hoc metadata formats. The right response is to add the manifest
contract, make manifests trackable, identify active provenance-sensitive runs,
and migrate them gradually—not to reorganize the entire repository.
