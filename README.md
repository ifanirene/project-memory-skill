# Project Memory

**What if your next AI session remembered both the work and the reasoning behind it?**

Project Memory is a skill for long-running research, analysis, and engineering projects. It helps you and your agent keep track of what is current, what to trust, and why decisions were made—so each session can build on the last.

The results are somewhere, the explanation is buried in a chat, and you are correcting the same assumption again. Saving conversations preserves history. Making that history useful requires structure and reflection.

![Two forms of context support the next task. Project context (organization adapted from Noble 2009) keeps stable homes for code, data, results, and docs; links an index to workstream notes and run variants; records code, inputs, parameters, and environment in manifests; and validates records and file hashes. Private personal context captures choices, reasons, and costs; checks cases and exceptions; distills principles with reasons and limits; and retrieves or revises them as work continues. Deeper values are explored together.](docs/assets/project-memory-overview.png)

**Two kinds of context**

**Project context: What did we do?** The design adapts [Noble (2009)](https://doi.org/10.1371/journal.pcbi.1000424): organize work so a newcomer can understand what happened and why, and prepare for experiments to be repeated. In our structure, code, data, results, and documentation have stable homes. An analysis index leads to each workstream's parent note, named run variants, and evidence. Notes explain the current answer and decisions; selective manifests capture code, inputs, parameters, and environment. Record validation and file-hash checks help detect broken links and changed files.

**Personal context: Why did we choose it?** An optional private workspace preserves choices, reasons, and accepted costs across projects. Reflection checks cases, corrections, and exceptions, then distills working principles with explicit reasons and limits. Tasks retrieve relevant guidance; later evidence can revise or retire it. Deeper interpretations of your values are discussed with you.

**Why this approach**

The goal is context that changes the next decision. A chat archive can recover a conversation; organized project memory connects the current answer to its evidence and provenance. A saved instruction records what you wanted; a working principle also explains when and why it applies. Keeping sources and exceptions attached makes that guidance easier to inspect and correct as your work changes.

**Try it**

Install the stable release with Python 3.10+ and Git (macOS or Linux):

```sh
git clone --branch v0.2.1 --depth 1 https://github.com/ifanirene/project-memory-skill.git
python3 project-memory-skill/scripts/install.py
```

The installer uses `$CODEX_HOME/skills/project-memory` (default:
`~/.codex/skills/project-memory`). The skill is available on your next turn.
For Claude Code, add `--dest ~/.claude/skills/project-memory` to the install
command. Existing installations are preserved; see
[setup and upgrades](docs/agent-setup.md#install-the-complete-skill).

Start with one repository. Give your agent the [Agent Setup Guide](docs/agent-setup.md), or point it at [the skill](SKILL.md), and ask:

> Use Project Memory to make this project easy to resume. Show me what we did, its evidence, why key choices were made, and the next decision.

Project documentation works on its own. Add private personal memory and scheduled upkeep when you need them.

**Versions**

The earlier baseline is preserved as `v0.1.0` and `codex/archive-v0.1.0`.
The current release is `v0.2.1`; `main` moves forward.
Install a tag for a fixed version. Read the installed `VERSION` file to check it.
See [changes](CHANGELOG.md) and [release policy](docs/releases.md).

**Your files and control**

Project notes stay in your repository. Personal evidence and principles live in a separate private workspace with sources you choose. Your agent reads selected material through its configured model; local storage does not mean offline inference.
