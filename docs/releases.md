# Versions and releases

This Git repository is the maintained source. Installed copies are deployments.
Edit and test here, then install a chosen version. Keep private source registries,
dialogue, ledgers, and personal memory outside the package. Upgrading the skill
must preserve them and any local deployment fixes.

`VERSION` holds `MAJOR.MINOR.PATCH`; `SKILL.md` mirrors it in `metadata.version`.
Use patch releases for compatible fixes, minor releases for new capabilities,
and major releases for breaking changes after 1.0. During 0.x, document breaking
changes in a minor release. Git tags identify exact releases; `main` moves forward.
Published tags stay fixed.

| Ref | Meaning |
| --- | --- |
| `v0.1.0` | Exact previous GitHub main, `b1d2d06`; retrospective baseline |
| `codex/archive-v0.1.0` | Preserved branch at the same baseline |
| `v0.2.0` | First release with an installer and explicit package version |
| `main` | Current development source; use a tag for a repeatable install |

For future releases:

1. Update `VERSION`, `SKILL.md` metadata, and `CHANGELOG.md` together.
2. Run `python3 -m pytest tests -q` and the skill validator when available.
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
