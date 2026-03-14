# AGENTS.md

## Scope

These instructions apply to the entire repository.

## Repository purpose

This repository publishes Ghostty-inspired themes for pi.

Current package:
- `@victor/pi-ghostty-themes`

## Ghostty source themes

The single source of truth for Ghostty palettes is the bundled theme directory:

```
/Applications/Ghostty.app/Contents/Resources/ghostty/themes/
```

Always read theme data from this path. Do not rely on external URLs, caches, or copied snippets. If the path changes after a Ghostty update, find the new location inside `Ghostty.app/Contents/Resources/`.

## Theme change policy

When editing themes:
- Keep theme names stable unless the user explicitly requests a rename.
- Treat visual tuning and readability fixes as patch-level changes.
- Treat new theme variants as minor-level changes.
- Treat renames, removals, or package structure changes as major-level changes.
- Preserve the Ghostty source palette identity unless the task explicitly asks for a different direction.
- Validate all theme JSON files after changes.

## Release policy

This repository uses `release-please` for release automation.

Required files:
- `release-please-config.json`
- `.release-please-manifest.json`
- `.github/workflows/release-please.yml`
- `CHANGELOG.md`

Release flow:
1. Merge changes to `main`.
2. `release-please` opens or updates a release PR.
3. Review the proposed version and changelog.
4. Merge the release PR to create the git tag and GitHub release.

## Commit message policy

Use Conventional Commits so `release-please` can infer SemVer changes.

Examples:
- `fix: adjust successful tool background tone`
- `feat: add a new Ghostty-derived variant`
- `feat!: rename theme identifiers`
- `docs: update README installation examples`
- `chore: update release automation config`

SemVer mapping:
- `fix:` -> patch
- `feat:` -> minor
- `!` or `BREAKING CHANGE:` -> major
- `docs:` and `chore:` -> no release by default

## Documentation policy

When the package behavior changes:
- Update `README.md` if installation, usage, or theme lineup changed.
- Keep `CHANGELOG.md` user-facing and concise.
- Do not mention AI tools in committed files or commit messages.

## Validation

Before committing changes:
- Run `jq empty themes/*.json` to validate theme files.
- Review `package.json`, `CHANGELOG.md`, and release config files for consistency.
