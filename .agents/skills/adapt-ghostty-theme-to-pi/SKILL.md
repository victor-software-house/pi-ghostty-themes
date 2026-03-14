---
name: adapt-ghostty-theme-to-pi
description: Adapt a Ghostty terminal theme into one or more pi themes. Use when deriving pi's 51 theme tokens from a Ghostty palette, tuning footer readability, inventing missing semantic UI colors, preserving Ghostty identity, or deciding whether a theme change is patch, minor, or major.
files:
  references:
    - mapping-rules.md
---

# adapt-ghostty-theme-to-pi

## Reference Index

- `references/mapping-rules.md` — read when you need the detailed token mapping rules, derivation heuristics, validation checklist, and release classification.

## Purpose

Use this skill to turn a Ghostty theme into a pi theme pack without losing the source theme's identity.

Ghostty provides terminal colors such as:
- background
- foreground
- cursor
- selection
- ANSI palette entries

pi requires a larger semantic model with 51 tokens, including:
- panel backgrounds
- tool result states
- markdown styling
- syntax colors
- thinking level borders
- footer-readable dim/muted colors

This skill explains how to bridge that gap.

## Workflow

### 1. Capture the Ghostty source theme

Get the source data from one of these:
- `ghostty +show-config`
- the Ghostty theme file under the app resources
- a custom Ghostty config file

Record at minimum:
- `background`
- `foreground`
- `cursor-color`
- `selection-background`
- `selection-foreground`
- palette entries `0-15`

### 2. Identify anchor colors

Pick the colors that define the theme's identity:
- base background
- main foreground
- muted gray / secondary neutral
- strongest accent(s)
- soft accent(s)
- darkest usable panel color
- brightest readable text color

These anchors become `vars` in the pi theme.

### 3. Split tokens into direct, semantic, and invented groups

Use three buckets.

**Direct**
- colors that map cleanly from Ghostty
- examples: `accent`, `text`, `mdCode`, `mdHeading`

**Semantic**
- colors that need a role-based choice from the existing palette
- examples: `success`, `warning`, `error`, `toolDiffAdded`, `toolDiffRemoved`

**Invented surfaces**
- colors that Ghostty does not define directly
- examples: `userMessageBg`, `customMessageBg`, `toolPendingBg`, `toolSuccessBg`, `toolErrorBg`, `selectedBg`

Invented surfaces must still feel native to the source theme.

### 4. Preserve theme identity first

When in doubt:
- keep the Ghostty background and foreground relationship intact
- prefer source palette colors over imported colors from other palettes
- derive surfaces by nudging the source background, not by introducing unrelated hues
- use the strongest accent sparingly for emphasis, not everywhere

### 5. Derive missing semantic colors carefully

If the Ghostty palette lacks a natural semantic color, derive by function, not by textbook color naming.

Examples:
- `success` does not need to be green if the source theme has no green identity
- `warning` can be a softer accent rather than yellow
- `toolSuccessBg` can be a warm neutral panel if green looks foreign to the palette

### 6. Treat footer readability as a hard requirement

pi uses dimmed colors heavily in the footer.

Rules:
- never make `dim` so dark that the footer disappears into the background
- test `dim` against the base background, not just against panels
- prefer readable subdued neutrals over ultra-low-contrast values

### 7. Make variants intentionally

Good variant strategies include:
- `literal` — closest possible mapping to source palette
- `semantic` — role-based balancing for daily use
- `high-contrast` — stronger readability for dense pi UI
- `steel` or equivalent — calmer variant that leans on neutral foregrounds

Each variant should have a clear reason to exist.

### 8. Keep names stable

Do not rename published theme identifiers unless explicitly requested.

Renames are breaking changes because users may reference theme names in pi settings.

### 9. Validate before release

Run:

```bash
jq empty themes/*.json
```

Also manually check:
- footer readability
- successful tool box background
- error tool box background
- markdown headings and links
- code blocks
- thinking border progression

### 10. Classify the change correctly for SemVer

In this repository:
- visual tuning and readability fixes -> patch
- new theme variants -> minor
- renamed/removed themes or package structure changes -> major

Use Conventional Commits so `release-please` can infer the release.

## Output expectations

When creating or revising a theme, include:
- what Ghostty theme was used as source
- which values were direct mappings
- which values were semantic derivations
- which values were invented surfaces
- why any difficult tokens were chosen differently from the source palette
- what release impact the change has
