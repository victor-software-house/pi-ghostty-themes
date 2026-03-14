#!/usr/bin/env python3
"""Generate pi semantic themes from Ghostty theme data."""
import json
import math
import os
import re

THEMES_DIR = "/Applications/Ghostty.app/Contents/Resources/ghostty/themes"
OUTPUT_DIR = "/Users/victor/workspace/victor/pi-ghostty-themes/themes"

THEME_NAMES = [
    "Adventure", "Adwaita Dark", "Arcoiris", "Arthur", "Atom", "Aura",
    "Black Metal (Bathory)", "Black Metal (Burzum)", "Black Metal (Khold)",
    "Box", "Brogrammer", "Carbonfox", "Catppuccin Mocha", "Citruszest",
    "Cursor Dark", "Cutie Pro", "Dark Modern", "Dark Pastel", "Dimmed Monokai",
    "Doom Peacock", "Dracula+", "Earthsong", "Everforest Dark Hard", "Fahrenheit",
    "Flatland", "Flexoki Dark", "Front End Delight", "Fun Forrest", "Galizur",
    "GitHub Dark Colorblind", "GitHub Dark High Contrast", "Glacier",
    "Gruber Darker", "Gruvbox Dark", "Gruvbox Dark Hard", "Gruvbox Material",
    "Guezwhoz", "Hacktober", "Hardcore", "Havn Skumring", "IC Orange PPL",
    "iTerm2 Smoooooth", "iTerm2 Tango Dark", "Japanesque", "Jellybeans",
    "Kanagawa Wave", "Kurokula", "Later This Evening", "Lovelace",
    "Material Darker", "Matte Black", "Mellow", "Miasma", "Nvim Dark",
    "Popping And Locking", "Sea Shells", "Sleepy Hollow", "Smyck",
    "Tomorrow Night", "Tomorrow Night Bright", "Tomorrow Night Burns",
    "Twilight", "Vague", "Vesper", "Xcode Dark hc",
]

SCHEMA_URL = "https://raw.githubusercontent.com/badlogic/pi-mono/main/packages/coding-agent/src/modes/interactive/theme/theme-schema.json"


# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------
def hex_to_rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgb_to_hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(
        max(0, min(255, int(r))), max(0, min(255, int(g))), max(0, min(255, int(b)))
    )


def lighten(c, amt):
    r, g, b = hex_to_rgb(c)
    return rgb_to_hex(r + amt, g + amt, b + amt)


def darken(c, amt):
    return lighten(c, -amt)


def mix(c1, c2, ratio=0.5):
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return rgb_to_hex(
        r1 * ratio + r2 * (1 - ratio),
        g1 * ratio + g2 * (1 - ratio),
        b1 * ratio + b2 * (1 - ratio),
    )


def luminance(c):
    r, g, b = hex_to_rgb(c)
    return 0.299 * r + 0.587 * g + 0.114 * b


def saturation(c):
    r, g, b = hex_to_rgb(c)
    mx, mn = max(r, g, b), min(r, g, b)
    return (mx - mn) / mx if mx > 0 else 0


def hue_angle(c):
    """Return hue in degrees (0-360)."""
    r, g, b = [x / 255.0 for x in hex_to_rgb(c)]
    mx, mn = max(r, g, b), min(r, g, b)
    d = mx - mn
    if d == 0:
        return 0
    if mx == r:
        h = ((g - b) / d) % 6
    elif mx == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4
    return h * 60


def hue_distance(c1, c2):
    h1, h2 = hue_angle(c1), hue_angle(c2)
    d = abs(h1 - h2)
    return min(d, 360 - d)


def tint_toward(base, tint, strength=0.08):
    return mix(tint, base, strength)


def ensure_contrast(fg, bg, min_diff=45):
    fl, bl = luminance(fg), luminance(bg)
    if abs(fl - bl) >= min_diff:
        return fg
    needed = int(min_diff - abs(fl - bl))
    if bl < 128:
        return lighten(fg, needed)
    return darken(fg, needed)


# ---------------------------------------------------------------------------
# Ghostty parser
# ---------------------------------------------------------------------------
def parse_ghostty(text):
    d = {}
    palette = {}
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^(\S+)\s*=\s*(.+)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if key == "palette":
            pm = re.match(r"^(\d+)=(.+)$", val)
            if pm:
                palette[int(pm.group(1))] = pm.group(2).strip()
        else:
            d[key] = val
    d["palette"] = palette
    return d


def slugify(name):
    s = name.lower()
    s = s.replace("+", "-plus")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


# ---------------------------------------------------------------------------
# Pick best color from candidates for a target hue family
# ---------------------------------------------------------------------------
def best_for_hue(candidates, target_hue, bg, min_sat=0.15, min_contrast=45):
    """Pick candidate closest to target_hue with decent saturation + contrast."""
    scored = []
    for c in candidates:
        s = saturation(c)
        if s < min_sat:
            continue
        hdist = hue_distance(c, rgb_to_hex(
            int(255 * (1 if target_hue < 60 or target_hue > 300 else 0)),
            int(255 * (1 if 60 <= target_hue < 180 else 0)),
            int(255 * (1 if 180 <= target_hue < 300 else 0)),
        ))
        contrast = abs(luminance(c) - luminance(bg))
        if contrast < 30:
            continue
        # lower hue distance is better, higher contrast is better
        score = -hdist + contrast * 0.3 + s * 50
        scored.append((score, c))
    if scored:
        scored.sort(reverse=True)
        return scored[0][1]
    return None


# ---------------------------------------------------------------------------
# Theme generation
# ---------------------------------------------------------------------------
def generate_theme(name, g):
    bg = g.get("background", "#1e1e1e")
    fg = g.get("foreground", "#cccccc")
    cursor = g.get("cursor-color", fg)
    p = g.get("palette", {})

    # Collect all ANSI colors
    ansi = {i: p.get(i, "#555555") for i in range(16)}
    red = ansi[1]
    green = ansi[2]
    yellow = ansi[3]
    blue = ansi[4]
    magenta = ansi[5]
    cyan = ansi[6]
    white = ansi[7]
    bright_black = ansi[8]
    bright_red = ansi[9]
    bright_green = ansi[10]
    bright_yellow = ansi[11]
    bright_blue = ansi[12]
    bright_magenta = ansi[13]
    bright_cyan = ansi[14]
    bright_white = ansi[15]

    all_colors = [ansi[i] for i in range(16)]

    # ---- Accent selection ----
    # Accent can be any hue. If it ends up matching error, we fix it later.
    cursor_sat = saturation(cursor)
    if cursor_sat > 0.3 and cursor != fg and cursor != bg and luminance(cursor) > 40:
        accent = cursor
    else:
        candidates = [bright_red, bright_green, bright_yellow, bright_blue,
                      bright_magenta, bright_cyan, red, green, yellow, blue, magenta, cyan]
        accent = max(candidates, key=lambda c: saturation(c) * (luminance(c) + 20) / 275)

    # ---- Three distinct hue families for success/error/warning ----
    # Target hues: green ~120, red ~0, yellow ~50
    # Hard rule: these three must never share the same hue family.
    # If the palette lacks three distinct families, derive the missing one.

    all_saturated = [c for c in all_colors if saturation(c) > 0.12 and abs(luminance(c) - luminance(bg)) > 25]

    # Error: prefer red family (hue < 30 or > 330)
    error_candidates = [c for c in all_saturated if hue_angle(c) < 30 or hue_angle(c) > 330]
    if not error_candidates:
        # Broaden to orange-red (hue < 45 or > 315)
        error_candidates = [c for c in all_saturated if hue_angle(c) < 45 or hue_angle(c) > 315]
    if not error_candidates:
        error_candidates = [red, bright_red]
    error_color = max(error_candidates, key=lambda c: saturation(c) * luminance(c))
    error_color = ensure_contrast(error_color, bg, 50)

    # Success: prefer green/teal family (hue 80-200), distinct from error
    success_candidates = [c for c in all_saturated if 80 < hue_angle(c) < 200
                          and hue_distance(c, error_color) > 60]
    if not success_candidates:
        # Try broader cyan/teal
        success_candidates = [c for c in all_saturated if 140 < hue_angle(c) < 240
                              and hue_distance(c, error_color) > 50]
    if not success_candidates:
        success_candidates = [green, bright_green, cyan, bright_cyan]
        success_candidates = [c for c in success_candidates if saturation(c) > 0.05]
    if not success_candidates:
        # Derive: tint the foreground toward green
        success_candidates = [mix("#5faf5f", fg, 0.6)]
    success_color = max(success_candidates, key=lambda c: saturation(c) * (luminance(c) + 20) / 275)
    success_color = ensure_contrast(success_color, bg, 45)

    # Warning: prefer yellow/amber (hue 30-80), distinct from BOTH error and success
    MIN_HUE_SEP = 30
    warning_candidates = [c for c in all_saturated if 25 < hue_angle(c) < 85
                          and hue_distance(c, error_color) > MIN_HUE_SEP
                          and hue_distance(c, success_color) > MIN_HUE_SEP]
    if not warning_candidates:
        # Broaden range
        warning_candidates = [c for c in all_saturated if 20 < hue_angle(c) < 100
                              and hue_distance(c, error_color) > 20
                              and hue_distance(c, success_color) > 20]
    if not warning_candidates:
        warning_candidates = [yellow, bright_yellow]
        warning_candidates = [c for c in warning_candidates if saturation(c) > 0.05]
    if not warning_candidates:
        # Derive: tint foreground toward amber
        warning_candidates = [mix("#d7af5f", fg, 0.6)]
    warning_color = max(warning_candidates, key=lambda c: saturation(c) * (luminance(c) + 20) / 275)
    warning_color = ensure_contrast(warning_color, bg, 45)

    # Final semantic validation pass
    # Error MUST be in warm/red family (hue < 50 or > 320).
    # If not, derive from palette tint toward red.
    err_hue = hue_angle(error_color)
    if not (err_hue < 50 or err_hue > 320):
        error_color = mix("#d75f5f", fg, 0.55)
        error_color = ensure_contrast(error_color, bg, 50)

    # Success MUST be in cool/green family (hue 80-200).
    suc_hue = hue_angle(success_color)
    if not (80 < suc_hue < 200):
        success_color = mix("#5faf5f", fg, 0.55)
        success_color = ensure_contrast(success_color, bg, 45)

    # Warning MUST be in yellow/amber family (hue 30-80).
    warn_hue = hue_angle(warning_color)
    if not (20 < warn_hue < 90):
        warning_color = mix("#d7af5f", fg, 0.55)
        warning_color = ensure_contrast(warning_color, bg, 45)

    # Pairwise distinctness: at least 25 degrees apart
    # Use pure yellow (#cccc00) for warning derivation to separate from orange errors
    if hue_distance(warning_color, error_color) < 25:
        warning_color = mix("#cccc00", fg, 0.50)
        warning_color = ensure_contrast(warning_color, bg, 45)
    if hue_distance(warning_color, success_color) < 25:
        warning_color = mix("#cccc00", fg, 0.55)
        warning_color = ensure_contrast(warning_color, bg, 45)
    if hue_distance(success_color, error_color) < 40:
        success_color = mix("#5faf5f", fg, 0.55)
        success_color = ensure_contrast(success_color, bg, 45)
    # Iterative fix: ensure all three are 25+ degrees apart.
    # Strategy: if error is in the amber zone (hue 30-55), push warning toward
    # yellow-lime (hue ~75) to separate from both error and success.
    err_h = hue_angle(error_color)
    for _attempt in range(6):
        ew = hue_distance(warning_color, error_color)
        sw = hue_distance(warning_color, success_color)
        if ew >= 25 and sw >= 25:
            break
        # If error is amber, shift warning toward lime; else toward pure yellow
        if 25 < err_h < 55:
            target = "#888800"  # pure yellow, hue 60
        else:
            target = "#999900"
        ratio = 0.70 + _attempt * 0.06
        warning_color = mix(target, fg, min(ratio, 0.92))
        warning_color = ensure_contrast(warning_color, bg, 45)
    # Final fallback: synthesize warning at a safe hue.
    # Warning must stay in yellow/amber range (hue 40-75), never green.
    if hue_distance(warning_color, error_color) < 25 or hue_distance(warning_color, success_color) < 25:
        import colorsys
        # Try hues from 45 to 70 in steps, pick first that has 25+ distance from both
        best_warn = None
        for try_hue in [60, 55, 65, 50, 70, 45, 75]:
            r, g, b = colorsys.hls_to_rgb(try_hue / 360, 0.55, 0.65)
            candidate = rgb_to_hex(int(r * 255), int(g * 255), int(b * 255))
            candidate = ensure_contrast(candidate, bg, 45)
            if hue_distance(candidate, error_color) >= 25 and hue_distance(candidate, success_color) >= 25:
                best_warn = candidate
                break
        if best_warn:
            warning_color = best_warn
        else:
            # Extreme fallback: amber that's at least readable
            warning_color = "#c8a832"
            warning_color = ensure_contrast(warning_color, bg, 45)

    # ---- Secondary accent (for links, distinct from accent AND from error) ----
    secondary_candidates = [c for c in all_saturated if hue_distance(c, accent) > 40
                            and abs(luminance(c) - luminance(bg)) > 35]
    if secondary_candidates:
        secondary = max(secondary_candidates, key=lambda c: saturation(c))
    else:
        secondary = bright_cyan if bright_cyan != accent else bright_magenta
    secondary = ensure_contrast(secondary, bg, 45)

    # Post-check: ensure secondary is not too close to error (will be set later)
    # (deferred until after error_color is determined)

    # ---- Grays and neutrals ----
    gray = bright_black if luminance(bright_black) > luminance(bg) + 25 else lighten(bg, 55)
    gray = ensure_contrast(gray, bg, 40)

    dim = gray  # footer readability
    dim = ensure_contrast(dim, bg, 45)

    dark_gray = lighten(bg, 15)
    white_color = bright_white if luminance(bright_white) > 200 else "#f5f5f5"

    # ---- Panel surfaces ----
    panel = lighten(bg, 5)
    panel_alt = lighten(bg, 8)
    panel_success = tint_toward(lighten(bg, 6), success_color, 0.07)
    panel_error = tint_toward(lighten(bg, 6), error_color, 0.10)
    panel_info = lighten(bg, 10)

    # ---- Fix secondary if it matches error ----
    if hue_distance(secondary, error_color) < 30:
        alt_candidates = [c for c in all_saturated if hue_distance(c, accent) > 30
                          and hue_distance(c, error_color) > 30
                          and abs(luminance(c) - luminance(bg)) > 35]
        if alt_candidates:
            secondary = max(alt_candidates, key=lambda c: saturation(c))
            secondary = ensure_contrast(secondary, bg, 45)
        else:
            secondary = mix("#5fafcf", fg, 0.55)
            secondary = ensure_contrast(secondary, bg, 45)

    # ---- Fix accent if it's identical to error (same hex or within 5 lum) ----
    # Same hue family is OK (red accent + red error) as long as shades differ.
    acc_err_lum_diff = abs(luminance(accent) - luminance(error_color))
    if accent == error_color or (hue_distance(accent, error_color) < 10 and acc_err_lum_diff < 15):
        # Try to pick a different shade of the same hue, or a different color
        alt_accent = [c for c in all_saturated if c != error_color
                      and abs(luminance(c) - luminance(error_color)) > 20
                      and saturation(c) > 0.2
                      and abs(luminance(c) - luminance(bg)) > 35]
        if alt_accent:
            accent = max(alt_accent, key=lambda c: saturation(c) * (luminance(c) + 20) / 275)
        else:
            # Shift the accent luminance away from error
            if luminance(accent) > 128:
                accent = darken(accent, 40)
            else:
                accent = lighten(accent, 40)
        accent = ensure_contrast(accent, bg, 45)

    # ---- Diff colors: related to but distinct from success/error ----
    diff_added = mix(success_color, fg, 0.7) if luminance(success_color) > 150 else success_color
    diff_added = ensure_contrast(diff_added, bg, 45)
    diff_removed = mix(error_color, fg, 0.7) if luminance(error_color) > 150 else error_color
    diff_removed = ensure_contrast(diff_removed, bg, 45)

    # ---- Markdown ----
    md_code = ensure_contrast(accent, bg, 50)
    md_link = ensure_contrast(secondary, bg, 50)

    # ---- Syntax ----
    syntax_keyword = ensure_contrast(accent, bg, 45)
    syntax_function = ensure_contrast(secondary, bg, 45)
    syntax_string = ensure_contrast(success_color, bg, 40)
    syntax_number = ensure_contrast(warning_color, bg, 40)
    syntax_operator = ensure_contrast(
        red if saturation(red) > 0.2 else error_color, bg, 40
    )

    # ---- Thinking border progression ----
    accent_lum = luminance(accent)
    if accent_lum > 80:
        t_dark = darken(accent, 80)
        t_low = darken(accent, 50)
        t_mid = darken(accent, 25)
    else:
        t_dark = darken(accent, 30)
        t_low = accent
        t_mid = lighten(accent, 25)

    slug = slugify(name)

    theme = {
        "$schema": SCHEMA_URL,
        "name": f"{slug}-semantic",
        "vars": {
            "bg": bg,
            "fg": fg,
            "gray": gray,
            "darkGray": dark_gray,
            "accent": accent,
            "accentDark": darken(accent, 50) if accent_lum > 70 else darken(accent, 25),
            "accentMid": mix(accent, fg, 0.5),
            "secondary": secondary,
            "white": white_color,
            "panel": panel,
            "panelAlt": panel_alt,
            "panelSuccess": panel_success,
            "panelError": panel_error,
            "panelInfo": panel_info,
            "success": success_color,
            "error": error_color,
            "warning": warning_color,
            "diffAdded": diff_added,
            "diffRemoved": diff_removed,
        },
        "colors": {
            "accent": "accent",
            "border": "gray",
            "borderAccent": "accent",
            "borderMuted": "darkGray",
            "success": "success",
            "error": "error",
            "warning": "warning",
            "muted": "gray",
            "dim": "gray",
            "text": "",
            "thinkingText": "gray",
            "selectedBg": "panelInfo",
            "userMessageBg": "panel",
            "userMessageText": "",
            "customMessageBg": "panelAlt",
            "customMessageText": "",
            "customMessageLabel": "accent",
            "toolPendingBg": "panelAlt",
            "toolSuccessBg": "panelSuccess",
            "toolErrorBg": "panelError",
            "toolTitle": "white",
            "toolOutput": "fg",
            "mdHeading": "white",
            "mdLink": "secondary",
            "mdLinkUrl": "gray",
            "mdCode": "accent",
            "mdCodeBlock": "fg",
            "mdCodeBlockBorder": "accentDark",
            "mdQuote": "gray",
            "mdQuoteBorder": "gray",
            "mdHr": "darkGray",
            "mdListBullet": "accent",
            "toolDiffAdded": "diffAdded",
            "toolDiffRemoved": "diffRemoved",
            "toolDiffContext": "gray",
            "syntaxComment": "gray",
            "syntaxKeyword": "accent",
            "syntaxFunction": "secondary",
            "syntaxVariable": "fg",
            "syntaxString": "success",
            "syntaxNumber": "warning",
            "syntaxType": "white",
            "syntaxOperator": "error",
            "syntaxPunctuation": "gray",
            "thinkingOff": "darkGray",
            "thinkingMinimal": "gray",
            "thinkingLow": "accentDark",
            "thinkingMedium": "accentMid",
            "thinkingHigh": "accent",
            "thinkingXhigh": "white",
            "bashMode": "accent",
        },
        "export": {
            "pageBg": bg,
            "cardBg": panel,
            "infoBg": panel_info,
        },
    }

    return theme


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def validate_themes():
    """Check all semantic themes for hue distinctness and contrast."""
    issues = []
    for f in sorted(os.listdir(OUTPUT_DIR)):
        if not f.endswith("-semantic.json"):
            continue
        with open(os.path.join(OUTPUT_DIR, f)) as fh:
            t = json.load(fh)
        v = t.get("vars", {})
        s, e, w = v.get("success", ""), v.get("error", ""), v.get("warning", "")
        bg = v.get("bg", "#000000")
        acc = v.get("accent", "")
        problems = []
        if s and e:
            se = hue_distance(s, e)
            if se < 25:
                problems.append(f"success-error hue={se:.0f}deg (<25)")
        if s and w:
            sw = hue_distance(s, w)
            if sw < 25:
                problems.append(f"success-warning hue={sw:.0f}deg (<25)")
        if e and w:
            ew = hue_distance(e, w)
            if ew < 25:
                problems.append(f"error-warning hue={ew:.0f}deg (<25)")
        if acc and e and acc == e:
            problems.append("accent identical to error")
        if acc and e and hue_distance(acc, e) < 10 and abs(luminance(acc) - luminance(e)) < 15:
            problems.append("accent nearly identical to error")
        # Footer contrast
        gray = v.get("gray", "")
        if gray and bg and abs(luminance(gray) - luminance(bg)) < 40:
            problems.append(f"dim/gray contrast too low ({abs(luminance(gray) - luminance(bg)):.0f})")
        if problems:
            issues.append((t.get("name", f), problems))
    if issues:
        print(f"{len(issues)} theme(s) with issues:")
        for name, probs in issues:
            print(f"  {name}: {', '.join(probs)}")
        return False
    else:
        count = len([f for f in os.listdir(OUTPUT_DIR) if f.endswith("-semantic.json")])
        print(f"All {count} semantic themes pass validation")
        return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate pi semantic themes from Ghostty palettes")
    parser.add_argument("--name", nargs="+", help="Generate only the named theme(s). Omit to generate all.")
    parser.add_argument("--validate", action="store_true", help="Validate existing themes without regenerating.")
    parser.add_argument("--themes-dir", default=THEMES_DIR, help="Ghostty themes directory.")
    parser.add_argument("--output-dir", default=OUTPUT_DIR, help="Output directory for pi themes.")
    args = parser.parse_args()

    if args.validate:
        ok = validate_themes()
        raise SystemExit(0 if ok else 1)

    names = args.name if args.name else THEME_NAMES
    themes_dir = args.themes_dir
    output_dir = args.output_dir

    generated = []
    for name in names:
        filepath = os.path.join(themes_dir, name)
        if not os.path.exists(filepath):
            print(f"SKIP: {name} (not found in {themes_dir})")
            continue
        with open(filepath) as f:
            raw = f.read()
        g = parse_ghostty(raw)
        theme = generate_theme(name, g)
        slug = slugify(name)
        out_path = os.path.join(output_dir, f"{slug}-semantic.json")
        with open(out_path, "w") as f:
            json.dump(theme, f, indent=2)
            f.write("\n")
        generated.append(name)
        print(f"OK: {name} -> {slug}-semantic.json")

    print(f"\nGenerated {len(generated)} theme(s)")

    # Auto-validate after generation
    print()
    validate_themes()


if __name__ == "__main__":
    main()
