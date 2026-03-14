# pi-ghostty-themes

[![Release](https://img.shields.io/github/v/release/victor-software-house/pi-ghostty-themes?sort=semver)](https://github.com/victor-software-house/pi-ghostty-themes/releases)

Ghostty-inspired themes for pi, starting from the `Tomorrow Night Burns` Ghostty theme and adapting it to pi's 51-token theme model.

## Included themes

| Theme | Strategy | Notes |
|---|---|---|
| `tomorrow-night-burns-literal` | Direct palette mapping | Closest to the Ghostty source palette |
| `tomorrow-night-burns-semantic` | Semantic mapping | Balanced default for daily use |
| `tomorrow-night-burns-high-contrast` | Readability-first | Stronger footer and tool visibility |
| `tomorrow-night-burns-steel` | Foreground/gray-led | Calmer variant with lighter accent pressure |

## Why multiple variants

Ghostty themes define terminal colors, but pi themes require additional semantic UI tokens for:

- tool panels
- markdown rendering
- syntax highlighting
- thinking levels
- footer readability
- diff colors

These variants explore different derivation strategies for those missing values.

## Install

### From local path

```bash
pi install /absolute/path/to/pi-ghostty-themes
```

### From GitHub

```bash
pi install git:github.com/victor-software-house/pi-ghostty-themes
```

## Use

Select a theme in `/settings`, or set it in `~/.pi/agent/settings.json`:

```json
{
  "theme": "tomorrow-night-burns-semantic"
}
```

## Notes on derivation

Source Ghostty palette values used as anchors:

- background: `#151515`
- foreground: `#a1b0b8`
- gray: `#5d6f71`
- dark gray: `#252525`
- warm accents: `#832e31`, `#a63c40`, `#d3494e`, `#fc595f`, `#df9395`, `#ba8586`

Not every pi token has a direct Ghostty equivalent. In particular:

- `success` has no natural green source in this palette
- panel backgrounds must be invented from the base background
- `dim` must stay readable enough for pi's footer
- syntax colors must be assigned by visual role, not by terminal ANSI meaning

## Release process

This repository uses `release-please` for SemVer automation.

- merge normal changes to `main`
- `release-please` opens or updates a release PR
- merge the release PR to publish the next tag and GitHub release

Commit messages should follow Conventional Commits:

- `fix:` for patch releases
- `feat:` for minor releases
- `feat!:` or `BREAKING CHANGE:` for major releases

## License

MIT
