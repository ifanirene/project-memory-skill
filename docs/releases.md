# Versions and releases

This Git repository is the maintained source. Installed copies are deployments.
Edit and test here, then install a chosen version. Keep private source registries,
dialogue, ledgers, and personal memory outside the package. Upgrading the skill
must preserve them and any local deployment fixes.

`VERSION` holds `MAJOR.MINOR.PATCH`; `SKILL.md` mirrors it in `metadata.version`.
Use patch releases for compatible fixes, minor releases for new capabilities,
and major releases for breaking changes after 1.0. During 0.x, document breaking
changes in a minor release. Git tags identify exact releases; `main` moves forward.
Published tags stay fixed except when privacy removal requires an announced
history rewrite.

| Ref | Meaning |
| --- | --- |
| `v0.1.0` | Earlier archived baseline |
| `codex/archive-v0.1.0` | Preserved branch at the same baseline |
| `v0.2.0` | First release with an installer and explicit package version |
| `v0.2.1` | Privacy cleanup and publication checks; current release |
| `main` | Current development source; use a tag for a repeatable install |

For future releases:

1. Update `VERSION`, `SKILL.md` metadata, and `CHANGELOG.md` together.
2. Run `python3 -m pytest tests -q` and the skill validator when available.
   Run `python3 scripts/check_public_package.py` and repeat with `--history`
   before publication. Visually review changed images for private content.
   Install into a temporary directory and run the installed helper entrypoints.
3. Commit the tested source on `main`. Create an annotated `v<version>` tag at
   that commit, push `main` and that tag, and publish its GitHub release notes.
4. Verify the remote refs and install from the published tag. If preserving a
   pre-release main is useful, create `codex/archive-v<old-version>` at that
   exact commit before advancing main. Never replace an existing archive ref.

For an upgrade, compare the existing installation with the source first. Move
the old installation to a backup location and install into its original path.
Reconcile local fixes before using the new copy; generated prompts or bindings
may reference absolute installation paths. The installer creates no workspace,
changes no project instructions, and schedules no jobs. See the
[setup guide](agent-setup.md) for those separately requested operations.

## Public package boundaries

Keep audits, internal planning records, personal evidence, machine paths, and
operational screenshots outside the published package. Local review directories
and the old operational diagram are ignored by Git. The publication checker
reports common private paths, emails, evidence IDs, keys, and tokens; it cannot
prove that arbitrary prose or image content is suitable for publication.

Version 0.2.1 removes private material from the current package. A prepared scrub
of older branches and release tags awaits explicit approval. Until that rewrite,
older refs retain their historical contents. After a rewrite, use a fresh clone
and reapply only reviewed local changes; merging old history can restore removed
material. Rewriting public refs cannot erase existing external clones or cached
GitHub views; those require separate cleanup under
[GitHub's sensitive-data removal procedure](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).
