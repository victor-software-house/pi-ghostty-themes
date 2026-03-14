# pi-ghostty-themes

[![Release](https://img.shields.io/github/v/release/victor-software-house/pi-ghostty-themes?sort=semver)](https://github.com/victor-software-house/pi-ghostty-themes/releases)

Ghostty-inspired themes for [pi](https://github.com/badlogic/pi-mono), adapted from the bundled Ghostty terminal palettes to pi's 51-token theme model.

## Variant naming

Every theme name ends with a **variant suffix** that describes the derivation strategy:

| Suffix | Strategy | When to use |
|---|---|---|
| `-semantic` | Colors assigned by **function** (success = green, error = red, warning = amber) even if the source palette lacks those hues | Default for daily use. Best role clarity. |
| `-literal` | Source palette colors used as directly as possible, minimal invention | When strict Ghostty fidelity matters more than role separation |
| `-high-contrast` | Semantic with stronger luminance separation | Dense UI, accessibility, bright monitors |
| `-steel` | Semantic with reduced accent pressure, leaning on neutrals | Calmer, less saturated |

Most themes ship only the `-semantic` variant. Additional variants exist for Tomorrow Night Burns.

## Included themes

65 semantic themes derived from Ghostty palettes:

Adventure, Adwaita Dark, Arcoiris, Arthur, Atom, Aura,
Black Metal (Bathory), Black Metal (Burzum), Black Metal (Khold),
Box, Brogrammer, Carbonfox, Catppuccin Mocha, Citruszest,
Cursor Dark, Cutie Pro, Dark Modern, Dark Pastel, Dimmed Monokai,
Doom Peacock, Dracula+, Earthsong, Everforest Dark Hard, Fahrenheit,
Flatland, Flexoki Dark, Front End Delight, Fun Forrest, Galizur,
GitHub Dark Colorblind, GitHub Dark High Contrast, Glacier,
Gruber Darker, Gruvbox Dark, Gruvbox Dark Hard, Gruvbox Material,
Guezwhoz, Hacktober, Hardcore, Havn Skumring, IC Orange PPL,
iTerm2 Smoooooth, iTerm2 Tango Dark, Japanesque, Jellybeans,
Kanagawa Wave, Kurokula, Later This Evening, Lovelace,
Material Darker, Matte Black, Mellow, Miasma, Nvim Dark,
Popping And Locking, Sea Shells, Sleepy Hollow, Smyck,
Tomorrow Night, Tomorrow Night Bright, Tomorrow Night Burns,
Twilight, Vague, Vesper, Xcode Dark hc

Tomorrow Night Burns also has `-literal`, `-high-contrast`, and `-steel` variants (68 theme files total).

## What "semantic" means

Ghostty themes define 16 ANSI colors plus background/foreground/cursor. pi requires 51 tokens for tool panels, diff colors, markdown, syntax highlighting, thinking borders, and footer readability.

A semantic variant assigns pi tokens by **role**, not by palette position:

- `success` is always in the green/teal hue family (hue 80-200)
- `error` is always in the red/warm hue family (hue <50 or >320)
- `warning` is always in the yellow/amber hue family (hue 30-80)
- All three are guaranteed 25+ degrees of hue separation

When a Ghostty palette lacks a needed hue (e.g., Tomorrow Night Burns has no green), the missing color is derived by mixing a canonical hue with the theme's foreground to preserve the palette's tone.

## Install

```bash
# From GitHub (recommended)
pi install git:github.com/victor-software-house/pi-ghostty-themes

# From local checkout
pi install /path/to/pi-ghostty-themes
```

Update:

```bash
pi update
```

## Use

Select a theme in `/settings`, or set it in `~/.pi/agent/settings.json`:

```json
{
  "theme": "catppuccin-mocha-semantic"
}
```

Theme names follow the pattern `{slugified-ghostty-name}-{variant}`. Examples:

```
gruvbox-dark-semantic
dracula-plus-semantic
tomorrow-night-burns-high-contrast
kanagawa-wave-semantic
github-dark-colorblind-semantic
```

## Derivation architecture

All per-theme variation lives in the `vars` block (19 values). The `colors` block is a fixed template identical across all semantic themes. See the [token derivation map](/.agents/skills/adapt-ghostty-theme-to-pi/references/token-derivation-map.md) for exact formulas.

### Generating themes

```bash
# Regenerate all semantic themes from Ghostty source
python3 scripts/generate-pi-themes.py

# Generate a single theme
python3 scripts/generate-pi-themes.py --name "Catppuccin Mocha"

# Validate without regenerating
python3 scripts/generate-pi-themes.py --validate
```

The script reads palette data from the Ghostty app bundle at `/Applications/Ghostty.app/Contents/Resources/ghostty/themes/`.

## Release process

This repository uses `release-please` for SemVer automation.

- Merge changes to `main`.
- `release-please` opens or updates a release PR.
- Merge the release PR to publish the next tag and GitHub release.

Commit messages follow Conventional Commits:

- `fix:` for patch releases (visual tuning, readability fixes)
- `feat:` for minor releases (new themes or variants)
- `feat!:` for major releases (renames, removals, structure changes)

## License

MIT
