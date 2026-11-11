#!/usr/bin/env python3
"""Build the Aroma Pacifico defense deck (PPTX, PDF and PNG previews).

The deck is generated from two inputs:

* deck/content.yaml: slide text, speaker notes and the asset catalog.
* deck/assets/tokens.json: a copy of aroma-pacifico-design-system
  tokens/tokens.json (colors, font families, sizes, spacing and radius).

Images (brand marks, icons, diagram crops and design-system previews) are
rendered once from the sibling repositories with --refresh-assets and kept
under deck/assets/, so a plain rebuild needs neither repository.

Team portraits are cropped once from the original photos with
--team-photos DIR into deck/assets/team/, using the eye position and the
eye-to-chin distance recorded per photo in content.yaml, so every face has
the same size and eye height on the team slide.

Usage:
    python3 deck/build_deck.py                      # PPTX only
    python3 deck/build_deck.py --render             # PPTX, PDF and previews
    python3 deck/build_deck.py --refresh-assets \
        --design-system ../aroma-pacifico-design-system \
        --diagrams ../aroma-pacifico-diagrams --render
    python3 deck/build_deck.py --team-photos <dir> --render

Requirements: python-pptx, PyYAML and Pillow. --refresh-assets also needs
Google Chrome or Chromium (headless SVG rendering). --render needs
LibreOffice (soffice) and pdftoppm (poppler-utils).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import io

import yaml
from PIL import Image, ImageFilter, ImageFont, ImageOps
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

DECK_DIR = Path(__file__).resolve().parent
ASSETS = DECK_DIR / "assets"
OUT_NAME = "aroma-pacifico-sustentacion"

SLIDE_W, SLIDE_H = 960.0, 540.0  # points, 16:9 (13.333 x 7.5 in)
BRAND_FILES = ["logo", "logo-negative", "isotype", "isotype-negative"]
LINE_HEIGHT = 1.3  # layout line height in em; covers Roboto and Arial metrics
PORTRAIT_RATIO = 3 / 4  # width / height of the team portraits
PORTRAIT_FACE = 0.25  # eye-to-chin distance as a share of the portrait height
PORTRAIT_EYES = 0.31  # eye line as a share of the portrait height, from the top
PORTRAIT_MAX_H = 900  # pixels

WARNINGS: list[str] = []


# --------------------------------------------------------------------------
# Design tokens
# --------------------------------------------------------------------------


class Tokens:
    """Resolves W3C design tokens, including {alias} references."""

    def __init__(self, path: Path):
        self.raw = json.loads(path.read_text(encoding="utf-8"))

    def _node(self, dotted: str):
        node = self.raw
        for key in dotted.split("."):
            node = node[key]
        return node["$value"]

    def value(self, dotted: str):
        val = self._node(dotted)
        while isinstance(val, str) and val.startswith("{"):
            val = self._node(val.strip("{}"))
        return val

    def color(self, dotted: str) -> str:
        val = self.value(dotted)
        return (val["hex"] if isinstance(val, dict) else val).lstrip("#").upper()

    def px(self, dotted: str) -> float:
        val = self.value(dotted)
        return float(val["value"] if isinstance(val, dict) else val)

    def font_size(self, dotted: str) -> float:
        val = self.value(dotted)
        size = val["fontSize"] if "fontSize" in val else val
        return float(size["value"])

    def families(self, dotted: str) -> list[str]:
        return list(self.value(dotted))


class Theme:
    """Slide styles derived from the tokens. One token pixel is one point."""

    def __init__(self, tokens: Tokens, font_override: str | None):
        t = tokens
        self.families = t.families("font.family.sans")
        self.font = font_override or self.families[0]
        mono = t.families("font.family.mono")
        self.mono = next((f for f in mono if _installed(f)), mono[0])
        c = t.color
        self.text_primary = c("color.text.primary")
        self.text_secondary = c("color.text.secondary")
        self.text_brand = c("color.text.brand")
        self.text_inverse = c("color.text.inverse")
        self.surface = c("color.surface.default")
        self.surface_subtle = c("color.surface.subtle")
        self.surface_sunken = c("color.surface.sunken")
        self.surface_brand = c("color.surface.brand")
        self.surface_brand_strong = c("color.surface.brand-strong")
        self.border_subtle = c("color.border.subtle")
        self.accent = c("color.brand.parchment.400")  # decorative only
        self.brand_primary = c("color.brand.primary.700")
        self.states = {
            name: (c(f"color.sack.{key}.background"), c(f"color.sack.{key}.text"),
                   c(f"color.sack.{key}.border"))
            for name, key in (("merged", "accepted"), ("review", "in-transit"),
                              ("pending", "in-preparation"))
        }
        # Typography (sizes in points).
        self.size_display = t.font_size("typography.web-wide.display")  # 44
        self.size_title = t.font_size("typography.web.title")  # 28
        self.size_value = t.font_size("typography.web-wide.value")  # 28
        self.size_heading = t.font_size("typography.web.heading")  # 20
        self.size_body_large = t.font_size("typography.phone.body-large")  # 18
        self.size_body = t.font_size("typography.web.body")  # 16
        self.size_caption = t.font_size("typography.web.caption")  # 14
        # Spacing and radius.
        self.margin = t.px("space.7")  # 48
        self.gutter = t.px("space.5")  # 24
        self.gap = t.px("space.4")  # 16
        self.pad = t.px("space.4")  # 16
        self.pad_small = t.px("space.3")  # 12
        self.radius = t.px("radius.lg")  # 12
        self.radius_md = t.px("radius.md")  # 8
        self.icon = t.px("size.icon-lg")  # 32


# --------------------------------------------------------------------------
# Text measurement, used to pick sizes that fit and to flag overflow
# --------------------------------------------------------------------------


def _font_file(pattern: str) -> str | None:
    try:
        out = subprocess.run(["fc-match", "-f", "%{file}", pattern],
                             capture_output=True, text=True, check=True).stdout
        return out or None
    except (OSError, subprocess.CalledProcessError):
        return None


def _installed(family: str) -> bool:
    try:
        out = subprocess.run(["fc-list", family], capture_output=True, text=True,
                             check=True).stdout
        return bool(out.strip())
    except (OSError, subprocess.CalledProcessError):
        return False


class Measurer:
    """Measures with the token font and with the Arial-metric fallback and
    keeps the wider result, so text that fits here also fits with the
    fallback face."""

    def __init__(self, font_name: str):
        self.files = {}
        for bold in (False, True):
            style = ":bold" if bold else ""
            files = [f for f in (_font_file(font_name + style),
                                 _font_file("Arial" + style)) if f]
            self.files[bold] = files
        self.cache = {}

    def width(self, text: str, size: float, bold: bool) -> float:
        best = 0.0
        for path in self.files[bold]:
            key = (path, size)
            if key not in self.cache:
                self.cache[key] = ImageFont.truetype(path, size=max(1, round(size * 4)))
            best = max(best, self.cache[key].getlength(text) / 4)
        return best or len(text) * size * 0.55

    def lines(self, text: str, size: float, bold: bool, width: float) -> int:
        count = 0
        for para in text.split("\n"):
            words, line = para.split(), ""
            count += 1
            for word in words:
                trial = f"{line} {word}".strip()
                if self.width(trial, size, bold) <= width or not line:
                    line = trial
                else:
                    count += 1
                    line = word
        return count


MEASURE: Measurer | None = None


def plain(text: str) -> str:
    return text.replace("**", "")


def fit(paragraphs, width, height, size, min_size, bold=False, space_after=0.0,
        where=""):
    """Largest size <= size whose wrapped paragraphs fit width x height."""
    s = size
    while s >= min_size:
        total = 0.0
        for p in paragraphs:
            n = MEASURE.lines(plain(p), s, bold, width)
            total += n * s * LINE_HEIGHT + space_after
        total -= space_after
        if total <= height:
            return s
        s -= 0.5
    WARNINGS.append(f"OVERFLOW risk: {where!r} does not fit at {min_size} pt")
    return min_size


# --------------------------------------------------------------------------
# Shape helpers
# --------------------------------------------------------------------------


def rgb(hex6: str) -> RGBColor:
    return RGBColor.from_string(hex6)


def box(slide, x, y, w, h, fill=None, line=None, radius=0.0, line_w=1.0):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    shp = slide.shapes.add_shape(shape_type, Pt(x), Pt(y), Pt(w), Pt(h))
    if radius:
        shp.adjustments[0] = min(0.5, radius / min(w, h))
    style = shp._element.find(qn("p:style"))
    if style is not None:
        shp._element.remove(style)
    if fill:
        shp.fill.solid()
        shp.fill.fore_color.rgb = rgb(fill)
    else:
        shp.fill.background()
    if line:
        shp.line.color.rgb = rgb(line)
        shp.line.width = Pt(line_w)
    else:
        shp.line.fill.background()
    shp.text_frame.text = ""
    return shp


def text(slide, x, y, w, h, paragraphs, theme, size, color, bold=False,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, space_after=0.0,
         bullet=None, letter=None, styles=None, font=None):
    """Add a text box. `styles` optionally gives (size, color, bold) per
    paragraph; `bullet` is a hex color for a native round bullet."""
    tb = slide.shapes.add_textbox(Pt(x), Pt(y), Pt(w), Pt(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, para in enumerate(paragraphs):
        p_size, p_color, p_bold = styles[i] if styles else (size, color, bold)
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = 1.08
        p.space_after = Pt(space_after) if i < len(paragraphs) - 1 else Pt(0)
        if bullet:
            ppr = p._p.get_or_add_pPr()
            indent = int(Pt(p_size * 0.9))
            ppr.set("marL", str(indent))
            ppr.set("indent", str(-indent))
            for tag, attrs in (("a:buClr", None), ("a:buSzPct", {"val": "100000"}),
                               ("a:buFont", {"typeface": "Arial"}),
                               ("a:buChar", {"char": "\u2022"})):
                el = ppr.makeelement(qn(tag), attrs or {})
                if tag == "a:buClr":
                    clr = el.makeelement(qn("a:srgbClr"), {"val": bullet})
                    el.append(clr)
                ppr.append(el)
        parts = re.split(r"(\*\*[^*]+\*\*)", para)
        for part in parts:
            if not part:
                continue
            run = p.add_run()
            is_bold = p_bold or part.startswith("**")
            run.text = part.strip("*") if part.startswith("**") else part
            f = run.font
            f.name = font or theme.font
            f.size = Pt(p_size)
            f.bold = is_bold
            f.color.rgb = rgb(p_color)
            if letter is not None:
                rpr = run._r.get_or_add_rPr()
                rpr.set("spc", str(int(letter * 100)))
    return tb


def picture(slide, path: Path, x, y, w, h, align="center"):
    with Image.open(path) as im:
        iw, ih = im.size
    scale = min(w / iw, h / ih)
    pw, ph = iw * scale, ih * scale
    px = x + (w - pw) / 2 if align == "center" else x
    py = y + (h - ph) / 2
    slide.shapes.add_picture(str(path), Pt(px), Pt(py), Pt(pw), Pt(ph))
    return px, py, pw, ph


def icon_path(name: str, variant: str) -> Path:
    return ASSETS / "icons" / f"{name}-{variant}.png"


def watermark(path: Path, opacity: float) -> io.BytesIO:
    """The brand mark with its alpha scaled down, as an in-memory PNG."""
    with Image.open(path) as im:
        im = im.convert("RGBA")
        alpha = im.getchannel("A").point(lambda a: round(a * opacity))
        im.putalpha(alpha)
        buf = io.BytesIO()
        im.save(buf, format="PNG")
    buf.seek(0)
    return buf


# --------------------------------------------------------------------------
# Blocks
# --------------------------------------------------------------------------


class Renderer:
    def __init__(self, theme: Theme, total: int, meta: dict):
        self.t = theme
        self.total = total
        self.meta = meta
        self.team = {m["code"]: m for m in meta["team"]}

    def member(self, code: str) -> str:
        """Full name, role and deck role of a presenter, for the notes."""
        m = self.team.get(code)
        if not m:
            return code
        return f"{m['first']} {m['last']} ({m['role']}, {code})"

    # --- block dispatch --------------------------------------------------

    def blocks(self, slide, blocks, x, y, w, h, where):
        t = self.t
        fixed = sum(b.get("h", 0) for b in blocks)
        flex = [b for b in blocks if "h" not in b]
        gaps = t.gap * (len(blocks) - 1)
        free = h - fixed - gaps
        if flex and free < 40:
            WARNINGS.append(f"LAYOUT: {where} leaves {free:.0f} pt for flexible blocks")
        cy = y
        for b in blocks:
            bh = b.get("h", free / len(flex) if flex else 0)
            getattr(self, "b_" + b["type"].replace("-", "_"))(slide, b, x, cy, w, bh,
                                                              f"{where}/{b['type']}")
            cy += bh + t.gap

    def b_split(self, slide, b, x, y, w, h, where):
        lw = (w - self.t.gutter) * b.get("ratio", 0.6)
        rw = w - self.t.gutter - lw
        self.blocks(slide, b["left"], x, y, lw, h, where + "/left")
        self.blocks(slide, b["right"], x + lw + self.t.gutter, y, rw, h, where + "/right")

    def b_image(self, slide, b, x, y, w, h, where):
        t = self.t
        box(slide, x, y, w, h, fill=t.surface, line=t.border_subtle, radius=t.radius_md)
        inset = 6
        path = ASSETS / "images" / f"{b['asset']}.png"
        px, py, pw, ph = picture(slide, path, x + inset, y + inset, w - 2 * inset,
                                 h - 2 * inset)
        for lab in b.get("labels", []):
            size = 11
            lw = MEASURE.width(lab["text"], size, True) + 2 * 8
            lh = size * LINE_HEIGHT + 8
            lx = min(max(px + lab["x"] * pw - lw / 2, px), px + pw - lw)
            ly = py + lab["y"] * ph - lh / 2
            box(slide, lx, ly, lw, lh, fill=t.surface_brand, radius=lh / 2)
            text(slide, lx, ly, lw, lh, [lab["text"]], t, size, t.text_inverse, bold=True,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    def b_images(self, slide, b, x, y, w, h, where):
        t = self.t
        n = len(b["assets"])
        cw = (w - t.gap * (n - 1)) / n
        for i, name in enumerate(b["assets"]):
            cx = x + i * (cw + t.gap)
            box(slide, cx, y, cw, h, fill=t.surface_subtle, radius=t.radius)
            picture(slide, ASSETS / "images" / f"{name}.png", cx + 8, y + 8, cw - 16, h - 16)

    def b_stats(self, slide, b, x, y, w, h, where):
        t = self.t
        items = b["items"]
        n = len(items)
        cw = (w - t.gap * (n - 1)) / n
        inner = cw - 2 * t.pad
        compact = h < 120
        top = 12 if compact else 16
        vmax = t.size_title if compact else t.size_value + 8
        vs = min(fit([it["value"]], inner, vmax * LINE_HEIGHT, vmax, 18, bold=True,
                     where=f"{where}/value") for it in items)
        label_h = h - top - vs * LINE_HEIGHT - 4 - t.pad_small
        ls = min(fit([it["label"]], inner, label_h, t.size_body, 11,
                     where=f"{where}/label") for it in items)
        for i, it in enumerate(items):
            cx = x + i * (cw + t.gap)
            box(slide, cx, y, cw, h, fill=t.surface, line=t.border_subtle, radius=t.radius)
            box(slide, cx + t.pad, y, 40, 4, fill=t.accent)
            text(slide, cx + t.pad, y + top, inner, vs * LINE_HEIGHT, [it["value"]], t, vs,
                 t.text_brand, bold=True)
            ly = y + top + vs * LINE_HEIGHT + 4
            text(slide, cx + t.pad, ly, inner, y + h - ly - 4, [it["label"]], t, ls,
                 t.text_secondary)

    def b_cards(self, slide, b, x, y, w, h, where):
        t = self.t
        items = b["items"]
        cols = b.get("cols", len(items))
        rows = -(-len(items) // cols)
        gap = t.pad_small if b.get("compact") else t.gap
        cw = (w - gap * (cols - 1)) / cols
        ch = (h - gap * (rows - 1)) / rows
        pad = t.pad_small if b.get("compact") else t.pad
        icon_d = 28 if b.get("compact") else 40
        for i, it in enumerate(items):
            cx = x + (i % cols) * (cw + gap)
            cy = y + (i // cols) * (ch + gap)
            box(slide, cx, cy, cw, ch, fill=t.surface_subtle, radius=t.radius)
            tx = cx + pad
            if it.get("icon"):
                box(slide, cx + pad, cy + pad, icon_d, icon_d, fill=t.surface,
                    radius=icon_d / 2)
                isz = icon_d * 0.6
                picture(slide, icon_path(it["icon"], "brand"),
                        cx + pad + (icon_d - isz) / 2, cy + pad + (icon_d - isz) / 2,
                        isz, isz)
                tx = cx + pad + icon_d + t.pad_small
            tw = cx + cw - pad - tx
            avail = ch - 2 * pad
            compact = b.get("compact")
            hmax = t.size_heading - 2 if compact else t.size_heading + 4
            bmax = t.size_body - 1 if compact else t.size_body_large + 2
            for hs in [v / 2 for v in range(int(hmax * 2), 25, -1)]:
                bs = min(bmax, hs - (3 if compact else 4))
                th = MEASURE.lines(it["title"], hs, True, tw) * hs * LINE_HEIGHT
                bh = MEASURE.lines(it["text"], bs, False, tw) * bs * LINE_HEIGHT
                if th + 4 + bh <= avail:
                    break
            else:
                WARNINGS.append(f"OVERFLOW risk: {where}/{it['title']}")
            text(slide, tx, cy + pad, tw, avail, [it["title"], it["text"]], t, hs,
                 t.text_primary, space_after=4,
                 styles=[(hs, t.text_primary, True), (bs, t.text_secondary, False)])

    def b_bullets(self, slide, b, x, y, w, h, where):
        t = self.t
        items = b["items"]
        size = fit(items, w - 20, h, t.size_body_large + 2, 12, space_after=t.pad,
                   where=where)
        text(slide, x, y, w, h, items, t, size, t.text_primary, space_after=t.pad,
             bullet=t.accent, anchor=MSO_ANCHOR.MIDDLE)

    def b_callout(self, slide, b, x, y, w, h, where):
        t = self.t
        strong = b.get("tone", "brand") == "brand"
        fill = t.surface_brand if strong else t.surface_subtle
        color = t.text_inverse if strong else t.text_primary
        box(slide, x, y, w, h, fill=fill, radius=t.radius_md)
        size = fit([b["text"]], w - 2 * t.pad, h - 2 * 8, t.size_body_large, 12,
                   bold=strong, where=where)
        text(slide, x + t.pad, y, w - 2 * t.pad, h, [b["text"]], t, size, color,
             bold=strong, anchor=MSO_ANCHOR.MIDDLE)

    def b_compare(self, slide, b, x, y, w, h, where):
        t = self.t
        rows = b["rows"]
        cw = (w - t.gap) / 2
        head_h = 40
        box(slide, x, y, cw, head_h, fill=t.surface_sunken, radius=t.radius_md)
        box(slide, x + cw + t.gap, y, cw, head_h, fill=t.surface_brand, radius=t.radius_md)
        for i, (label, color) in enumerate(((b["headers"][0], t.text_primary),
                                            (b["headers"][1], t.text_inverse))):
            text(slide, x + i * (cw + t.gap) + t.pad, y, cw - 2 * t.pad, head_h, [label],
                 t, t.size_heading, color, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        ry = y + head_h + t.pad_small
        rh = (y + h - ry - t.pad_small * (len(rows) - 1)) / len(rows)
        cells = [c for r in rows for c in r]
        size = min(fit([c], cw - 2 * t.pad, rh - 2 * t.pad_small, t.size_body_large, 12,
                       where=f"{where}/cell") for c in cells)
        for r, (old, new) in enumerate(rows):
            cy = ry + r * (rh + t.pad_small)
            for i, (val, color, fill) in enumerate(((old, t.text_secondary, t.surface_subtle),
                                                     (new, t.text_primary, t.surface_subtle))):
                cx = x + i * (cw + t.gap)
                box(slide, cx, cy, cw, rh, fill=fill, radius=t.radius_md)
                if i == 1:
                    box(slide, cx, cy + 8, 4, rh - 16, fill=t.surface_brand)
                text(slide, cx + t.pad, cy, cw - 2 * t.pad, rh, [val], t, size, color,
                     anchor=MSO_ANCHOR.MIDDLE)

    def b_table(self, slide, b, x, y, w, h, where):
        """A table: `columns` headers, `rows` of cells, optional `widths`
        ratios, `align` per column (l or r) and `total` to bold the last row."""
        t = self.t
        cols, rows = b["columns"], b["rows"]
        ratios = b.get("widths", [1] * len(cols))
        cws = [w * r / sum(ratios) for r in ratios]
        aligns = [PP_ALIGN.RIGHT if a == "r" else PP_ALIGN.LEFT
                  for a in b.get("align", "l" * len(cols))]
        head_h = b.get("head_h", 30)
        rh = (h - head_h) / len(rows)
        pad = 8
        size = b.get("size", 14)
        while size > 9:
            ok = all(MEASURE.lines(str(c), size, bool(i == 0 or (b.get("total") and r is rows[-1])),
                                   cws[i] - 2 * pad) * size * LINE_HEIGHT <= rh - 4
                     for r in rows for i, c in enumerate(r))
            ok = ok and all(MEASURE.lines(c, size, True, cws[i] - 2 * pad) * size
                            * LINE_HEIGHT <= head_h - 2 for i, c in enumerate(cols))
            if ok:
                break
            size -= 0.5
        else:
            WARNINGS.append(f"OVERFLOW risk: {where} table does not fit at 9 pt")
        box(slide, x, y, w, head_h, fill=t.surface_brand, radius=t.radius_md)
        cx = x
        for i, c in enumerate(cols):
            text(slide, cx + pad, y, cws[i] - 2 * pad, head_h, [c], t, size, t.text_inverse,
                 bold=True, align=aligns[i], anchor=MSO_ANCHOR.MIDDLE)
            cx += cws[i]
        for r, row in enumerate(rows):
            ry = y + head_h + r * rh
            last = b.get("total") and r == len(rows) - 1
            fill = t.surface_sunken if last else (t.surface_subtle if r % 2 else t.surface)
            box(slide, x, ry, w, rh, fill=fill)
            box(slide, x, ry + rh - 0.75, w, 0.75, fill=t.border_subtle)
            cx = x
            for i, c in enumerate(row):
                text(slide, cx + pad, ry, cws[i] - 2 * pad, rh, [str(c)], t, size,
                     t.text_primary if (i == 0 or last) else t.text_secondary,
                     bold=bool(last) or i == 0 and b.get("bold_first", True),
                     align=aligns[i], anchor=MSO_ANCHOR.MIDDLE)
                cx += cws[i]

    def b_code(self, slide, b, x, y, w, h, where):
        """Verbatim tool output in the mono token font on a dark panel; a
        line that starts with "> " is highlighted in the accent color."""
        t = self.t
        box(slide, x, y, w, h, fill=t.surface_brand_strong, radius=t.radius_md)
        title_h = 24
        text(slide, x + t.pad, y + 6, w - 2 * t.pad, title_h - 6, [b["title"]], t, 11,
             t.accent, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        lines = b["lines"]
        avail_w, avail_h = w - 2 * t.pad, h - title_h - 12
        size = 13.0
        while size > 7 and (max(len(ln) for ln in lines) * size * 0.6 > avail_w
                            or len(lines) * size * LINE_HEIGHT > avail_h):
            size -= 0.5
        styles = [(size, t.accent if ln.startswith("> ") else t.text_inverse, False)
                  for ln in lines]
        text(slide, x + t.pad, y + title_h + 4, avail_w, avail_h,
             [ln[2:] if ln.startswith("> ") else ln for ln in lines], t, size,
             t.text_inverse, styles=styles, font=t.mono)

    def b_status(self, slide, b, x, y, w, h, where):
        t = self.t
        items = b["items"]
        rh = (h - t.pad_small * (len(items) - 1)) / len(items)
        icons = {"merged": "check-circle", "review": "clock", "pending": "alert-triangle"}
        chip_w = 150
        for i, it in enumerate(items):
            cy = y + i * (rh + t.pad_small)
            bg, fg, border = t.states[it["state"]]
            box(slide, x, cy, w, rh, fill=t.surface, line=t.border_subtle, radius=t.radius_md)
            box(slide, x + 8, cy + 6, chip_w, rh - 12, fill=bg, line=border,
                radius=(rh - 12) / 2, line_w=1.5)
            isz = 16
            picture(slide, icon_path(icons[it["state"]], it["state"]), x + 20,
                    cy + (rh - isz) / 2, isz, isz)
            text(slide, x + 42, cy, chip_w - 40, rh, [it["label"]], t, t.size_caption, fg,
                 bold=True, anchor=MSO_ANCHOR.MIDDLE)
            tx = x + 8 + chip_w + t.pad
            size = fit([it["text"]], w - (tx - x) - t.pad, rh - 8, t.size_body, 11,
                       where=f"{where}/{i}")
            text(slide, tx, cy, w - (tx - x) - t.pad, rh, [it["text"]], t, size,
                 t.text_primary, anchor=MSO_ANCHOR.MIDDLE)

    # --- slide chrome ----------------------------------------------------

    def footer(self, slide, index, source, dark=False):
        t = self.t
        y = SLIDE_H - 34
        color = t.text_inverse if dark else t.text_secondary
        if not dark:
            box(slide, t.margin, y - 10, SLIDE_W - 2 * t.margin, 1, fill=t.border_subtle)
        iso = ASSETS / "brand" / ("isotype-negative.png" if dark else "isotype.png")
        picture(slide, iso, t.margin, y - 2, 22, 22)
        text(slide, t.margin + 30, y, 260, 18, [self.meta["footer"]], t, 11, color,
             anchor=MSO_ANCHOR.MIDDLE)
        if source:
            sw = SLIDE_W - 2 * t.margin - 30 - 260 - 70
            size = fit([source], sw, 18, 10, 8, where=f"slide {index} source")
            text(slide, t.margin + 300, y, sw, 18, [source], t, size, color,
                 anchor=MSO_ANCHOR.MIDDLE)
        text(slide, SLIDE_W - t.margin - 60, y, 60, 18, [f"{index} / {self.total}"], t, 11,
             color, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)

    def notes(self, slide, s):
        head = []
        if s["kind"] == "divider":
            head.append(f"Parte {s['part']}: {s['time']} en total · "
                        f"Presenta: {self.member(s['presenter'])}")
        elif s.get("time"):
            head.append(f"Tiempo objetivo: {s['time']} · "
                        f"Presenta: {self.member(s.get('presenter', ''))}")
        if s.get("number"):
            head.append(f"Diapositiva {s['number']} de {self.script_total} del guion "
                        "(docs/speaker-script.md)")
        body = s.get("notes", "").strip()
        slide.notes_slide.notes_text_frame.text = "\n".join(head + ([""] if head else []) + [body])

    # --- slide kinds -----------------------------------------------------

    def content(self, slide, s, index):
        t = self.t
        box(slide, 0, 0, SLIDE_W, SLIDE_H, fill=t.surface)
        box(slide, 0, 0, SLIDE_W, 6, fill=t.surface_brand)
        text(slide, t.margin, 26, SLIDE_W - 2 * t.margin, 18, [s["eyebrow"].upper()], t,
             12, t.text_brand, bold=True, letter=1.2)
        tw = SLIDE_W - 2 * t.margin
        size = next((v / 2 for v in range(int(t.size_title * 2), 47, -1)
                     if MEASURE.lines(s["title"], v / 2, True, tw) == 1), None)
        if size is None:
            size = fit([s["title"]], tw, 72, t.size_title, 22, bold=True,
                       where=f"slide {index} title")
        text(slide, t.margin, 48, tw, 76, [s["title"]], t, size, t.text_primary, bold=True,
             anchor=MSO_ANCHOR.MIDDLE)
        top, bottom = 136, SLIDE_H - 56
        self.blocks(slide, s["blocks"], t.margin, top, tw, bottom - top, f"slide {index}")
        self.footer(slide, index, s.get("source"))

    def cover(self, slide, s, index):
        t = self.t
        box(slide, 0, 0, SLIDE_W, SLIDE_H, fill=t.surface_brand_strong)
        picture(slide, ASSETS / "brand" / "logo-negative.png", t.margin, 48, 300, 95,
                align="left")
        box(slide, t.margin, 178, 64, 4, fill=t.accent)
        text(slide, t.margin, 196, 760, 22, [s["eyebrow"].upper()], t, 14, t.text_inverse,
             bold=True, letter=1.5)
        text(slide, t.margin, 224, 820, 120, [s["title"]], t, t.size_display,
             t.text_inverse, bold=True)
        text(slide, t.margin, 344, 820, 30, [s["subtitle"]], t, t.size_heading,
             t.text_inverse)
        team = self.meta["team"]
        cw = (SLIDE_W - 2 * t.margin - 3 * t.gap) / 4
        inner = cw - 2 * t.pad
        size = min(fit([m["first"], m["last"]], inner, 2 * 15 * LINE_HEIGHT, 15, 11,
                       bold=True, where="cover team") for m in team)
        for i, m in enumerate(team):
            cx = t.margin + i * (cw + t.gap)
            box(slide, cx, 392, cw, 68, line=t.text_inverse, radius=t.radius_md, line_w=1)
            text(slide, cx + t.pad, 392, inner, 68,
                 [f"{m['code']} · {m['role']}", m["first"], m["last"]], t, size,
                 t.text_inverse, anchor=MSO_ANCHOR.MIDDLE,
                 styles=[(11, t.text_inverse, False), (size, t.text_inverse, True),
                         (size, t.text_inverse, True)])
        text(slide, t.margin, 478, 400, 20, [s["date"]], t, t.size_caption, t.text_inverse)
        text(slide, SLIDE_W - t.margin - 60, 478, 60, 20, [f"{index} / {self.total}"], t, 11,
             t.text_inverse, align=PP_ALIGN.RIGHT)

    def divider(self, slide, s, index):
        t = self.t
        box(slide, 0, 0, SLIDE_W, SLIDE_H, fill=t.surface_brand)
        picture(slide, ASSETS / "brand" / "isotype-negative.png", 600, 110, 300, 300)
        text(slide, t.margin, 96, 520, 24, [f"PARTE {s['part']} DE 4"], t, 16,
             t.text_inverse, bold=True, letter=2)
        box(slide, t.margin, 128, 64, 4, fill=t.accent)
        size = fit([s["title"]], 520, 120, t.size_display, 30, bold=True,
                   where=f"slide {index} divider title")
        text(slide, t.margin, 146, 520, 120, [s["title"]], t, size, t.text_inverse,
             bold=True, anchor=MSO_ANCHOR.MIDDLE)
        lines = [f"{m['first']} {m['last']} · {m['role']}" for m in self.meta["team"]]
        size = min(fit([ln], 520, (t.size_heading + 2) * LINE_HEIGHT, t.size_heading + 2,
                       14, bold=True, where=f"slide {index} presenter") for ln in lines)
        m = self.team[s["presenter"]]
        text(slide, t.margin, 278, 520, 58,
             [f"{m['first']} {m['last']} · {m['role']}", f"{s['time']} minutos"], t, size,
             t.text_inverse, styles=[(size, t.text_inverse, True),
                                     (t.size_body_large, t.text_inverse, False)])
        text(slide, t.margin, 344, 520, 130, s["agenda"], t, t.size_body_large,
             t.text_inverse, space_after=6)
        self.footer(slide, index, None, dark=True)

    def team_slide(self, slide, s, index):
        t = self.t
        box(slide, 0, 0, SLIDE_W, SLIDE_H, fill=t.surface)
        # Background motif: the brand isotype as a faint watermark, partly
        # off the slide, behind everything else.
        size = 430
        slide.shapes.add_picture(watermark(ASSETS / "brand" / "isotype.png", 0.07),
                                 Pt(SLIDE_W - size * 0.72), Pt(SLIDE_H - size * 0.86),
                                 Pt(size), Pt(size))
        slide.shapes.add_picture(watermark(ASSETS / "brand" / "isotype.png", 0.05),
                                 Pt(-size * 0.42), Pt(-size * 0.38), Pt(size * 0.8),
                                 Pt(size * 0.8))
        # Header strip in the style of the content slides.
        box(slide, 0, 0, SLIDE_W, 6, fill=t.surface_brand)
        hw = (SLIDE_W - 2 * t.margin) / 3
        for i, (label, align) in enumerate(((s["institution"], PP_ALIGN.LEFT),
                                            (s["occasion"], PP_ALIGN.CENTER),
                                            (f"{index} / {self.total}", PP_ALIGN.RIGHT))):
            text(slide, t.margin + i * hw, 22, hw, 18, [label.upper()], t, 12,
                 t.text_brand, bold=True, letter=1.2, align=align, anchor=MSO_ANCHOR.MIDDLE)
        box(slide, t.margin, 50, SLIDE_W - 2 * t.margin, 1, fill=t.border_subtle)
        text(slide, t.margin, 62, SLIDE_W - 2 * t.margin, 40, [s["title"]], t,
             t.size_title, t.text_primary, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        # Four portrait cards of equal size, 3:4, with name and role below.
        team = self.meta["team"]
        n = len(team)
        pw = 184
        ph = pw / PORTRAIT_RATIO
        gap = (SLIDE_W - 2 * t.margin - n * pw) / (n - 1)
        py = 120
        name_size = min(fit([m["first"], m["last"]], pw, 2 * 20 * LINE_HEIGHT, 20, 14,
                            bold=True, where="team names") for m in team)
        for i, m in enumerate(team):
            px = t.margin + i * (pw + gap)
            pic = slide.shapes.add_picture(str(ASSETS / "team" / f"{m['photo']}.jpg"),
                                           Pt(px), Pt(py), Pt(pw), Pt(ph))
            pic.auto_shape_type = MSO_SHAPE.ROUNDED_RECTANGLE
            geom = pic._element.spPr.find(qn("a:prstGeom"))
            av = geom.find(qn("a:avLst"))
            av.append(av.makeelement(qn("a:gd"), {
                "name": "adj", "fmla": f"val {round(100000 * t.radius / pw)}"}))
            pic.line.color.rgb = rgb(t.border_subtle)
            pic.line.width = Pt(1)
            box(slide, px, py + ph + 12, 40, 4, fill=t.accent)
            ny = py + ph + 22
            text(slide, px, ny, pw, 2 * name_size * LINE_HEIGHT, [m["first"], m["last"]], t,
                 name_size, t.brand_primary, bold=True)
            text(slide, px, ny + 2 * name_size * LINE_HEIGHT + 2, pw, 22, [m["role"]], t,
                 t.size_body, t.text_secondary)
        iso = ASSETS / "brand" / "isotype.png"
        y = SLIDE_H - 34
        box(slide, t.margin, y - 10, SLIDE_W - 2 * t.margin, 1, fill=t.border_subtle)
        picture(slide, iso, t.margin, y - 2, 22, 22)
        text(slide, t.margin + 30, y, 260, 18, [self.meta["footer"]], t, 11,
             t.text_secondary, anchor=MSO_ANCHOR.MIDDLE)

    def closing(self, slide, s, index):
        t = self.t
        box(slide, 0, 0, SLIDE_W, SLIDE_H, fill=t.surface_brand_strong)
        picture(slide, ASSETS / "brand" / "isotype-negative.png", (SLIDE_W - 150) / 2, 90,
                150, 150)
        text(slide, t.margin, 262, SLIDE_W - 2 * t.margin, 70, [s["title"]], t, 52,
             t.text_inverse, bold=True, align=PP_ALIGN.CENTER)
        box(slide, (SLIDE_W - 64) / 2, 340, 64, 4, fill=t.accent)
        text(slide, t.margin, 356, SLIDE_W - 2 * t.margin, 34, [s["subtitle"]], t,
             t.size_title, t.text_inverse, align=PP_ALIGN.CENTER)
        text(slide, t.margin, 404, SLIDE_W - 2 * t.margin, 24, [s["line"]], t,
             t.size_body, t.text_inverse, align=PP_ALIGN.CENTER)
        self.footer(slide, index, None, dark=True)


def build(content: dict, theme: Theme, out: Path):
    prs = Presentation()
    prs.slide_width = Emu(int(Pt(SLIDE_W)))
    prs.slide_height = Emu(int(Pt(SLIDE_H)))
    prs.core_properties.title = content["meta"]["title"]
    prs.core_properties.language = "es-CO"
    prs.core_properties.author = "Aroma Pacífico"
    blank = prs.slide_layouts[6]
    slides = content["slides"]
    r = Renderer(theme, len(slides), content["meta"])
    r.script_total = max(s.get("number", 0) for s in slides)
    for i, s in enumerate(slides, start=1):
        slide = prs.slides.add_slide(blank)
        getattr(r, "team_slide" if s["kind"] == "team" else s["kind"])(slide, s, i)
        r.notes(slide, s)
    prs.save(out)
    return len(slides)


# --------------------------------------------------------------------------
# Assets
# --------------------------------------------------------------------------


def chrome_binary() -> str:
    for name in ("google-chrome", "chromium", "chromium-browser", "chrome"):
        path = shutil.which(name)
        if path:
            return path
    sys.exit("ERROR: --refresh-assets needs Google Chrome or Chromium on PATH")


def svg_size(path: Path) -> tuple[float, float]:
    head = path.read_text(encoding="utf-8", errors="ignore")[:4000]
    vb = re.search(r'viewBox="([\d.\s-]+)"', head)
    if vb:
        _, _, w, h = (float(v) for v in vb.group(1).split())
        return w, h
    w = re.search(r'width="([\d.]+)', head)
    h = re.search(r'height="([\d.]+)', head)
    return float(w.group(1)), float(h.group(1))


def render_svg(svg: Path, out: Path, width_px: int, background: str | None):
    """Render an SVG with headless Chrome. Chrome is used because the
    diagrams use foreignObject labels and the brand marks use SVG masks."""
    w, h = svg_size(svg)
    height_px = round(width_px * h / w)
    bg = background or "transparent"
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "page.html"
        page.write_text(
            f'<html><body style="margin:0;background:{bg}">'
            f'<img src="{svg.resolve().as_uri()}" '
            f'style="width:{width_px}px;height:{height_px}px;display:block">'
            "</body></html>", encoding="utf-8")
        shot = Path(tmp) / "shot.png"
        subprocess.run([chrome_binary(), "--headless=new", "--disable-gpu", "--no-sandbox",
                        "--hide-scrollbars", f"--window-size={width_px},{height_px}",
                        "--default-background-color=00000000",
                        f"--screenshot={shot}", page.as_uri()],
                       check=True, capture_output=True)
        shutil.copy(shot, out)


def crop_save(src: Path, out: Path, crop, max_w: int):
    with Image.open(src) as im:
        im = im.convert("RGB")
        w, h = im.size
        if crop:
            l, tp, r, b = crop
            im = im.crop((round(l * w), round(tp * h), round(r * w), round(b * h)))
        if im.width > max_w:
            im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
        im.save(out, optimize=True)


def crop_portrait(src: Path, out: Path, spec: dict):
    """Crop a 3:4 portrait whose eye line and face size match the others.

    `spec` gives the eye midpoint as fractions of the photo ([x, y]) and the
    eye-to-chin distance as a fraction of the photo height. Where the crop
    leaves the photo at the top, it is filled with the wall color and the
    photo fades into it; other edges are mirrored. A warning is printed."""
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
    w, h = im.size
    ex, ey = spec["eyes"][0] * w, spec["eyes"][1] * h
    ch = spec["eye_chin"] * h / PORTRAIT_FACE
    cw = ch * PORTRAIT_RATIO
    left, top = round(ex - cw / 2), round(ey - PORTRAIT_EYES * ch)
    right, bottom = left + round(cw), top + round(ch)
    pads = (max(0, -left), max(0, -top), max(0, right - w), max(0, bottom - h))
    if any(pads):
        WARNINGS.append(f"PORTRAIT: {src.name} extended at the edge by {pads} px "
                        "(left, top, right, bottom)")
        pl, pt, pr, pb = pads
        canvas = Image.new("RGB", (w + pl + pr, h + pt + pb))
        canvas.paste(im, (pl, pt))
        if pt:
            # Fill with the wall color sampled at both ends of the top row and
            # fade the first rows of the photo into it, so hair that touches
            # the top edge ends softly instead of in a straight cut.
            band = max(4, h // 40)
            edge = w // 20
            c_left = im.crop((0, 0, edge, band)).resize((1, 1), Image.BOX).getpixel((0, 0))
            c_right = im.crop((w - edge, 0, w, band)).resize((1, 1), Image.BOX).getpixel((0, 0))
            wall = Image.new("RGB", (2, 1))
            wall.putpixel((0, 0), c_left)
            wall.putpixel((1, 0), c_right)
            canvas.paste(wall.resize((w, pt + band), Image.BILINEAR), (pl, 0))
            ramp = Image.linear_gradient("L").resize((w, band))  # black at the top
            canvas.paste(Image.composite(im.crop((0, 0, w, band)),
                                         canvas.crop((pl, pt, pl + w, pt + band)), ramp),
                         (pl, pt))
        if pb:
            canvas.paste(im.crop((0, h - pb, w, h)).transpose(Image.FLIP_TOP_BOTTOM),
                         (pl, pt + h))
        if pl:
            canvas.paste(canvas.crop((pl, 0, 2 * pl, canvas.height))
                         .transpose(Image.FLIP_LEFT_RIGHT), (0, 0))
        if pr:
            canvas.paste(canvas.crop((pl + w - pr, 0, pl + w, canvas.height))
                         .transpose(Image.FLIP_LEFT_RIGHT), (pl + w, 0))
        im, left, top, right, bottom = canvas, left + pl, top + pt, right + pl, bottom + pt
    im = im.crop((left, top, right, bottom))
    if im.height > PORTRAIT_MAX_H:
        im = im.resize((round(PORTRAIT_MAX_H * PORTRAIT_RATIO), PORTRAIT_MAX_H), Image.LANCZOS)
    im.save(out, quality=90, optimize=True)
    return im.size


def refresh_team(content: dict, photos: Path):
    (ASSETS / "team").mkdir(parents=True, exist_ok=True)
    for name, spec in content["assets"]["team"].items():
        size = crop_portrait(photos / spec["src"], ASSETS / "team" / f"{name}.jpg", spec)
        print(f"Portrait {name}: {size[0]} x {size[1]} px")


def refresh_assets(content: dict, ds: Path, diagrams: Path, theme_colors: dict):
    for sub in ("brand", "icons", "images"):
        (ASSETS / sub).mkdir(parents=True, exist_ok=True)
    shutil.copy(ds / "tokens" / "tokens.json", ASSETS / "tokens.json")
    for name in BRAND_FILES:
        svg = ds / "brand" / f"{name}.svg"
        w, _ = svg_size(svg)
        render_svg(svg, ASSETS / "brand" / f"{name}.png", round(w * 8), None)
    with tempfile.TemporaryDirectory() as tmp:
        for svg in sorted((ds / "icons").glob("*.svg")):
            source = svg.read_text(encoding="utf-8")
            for variant, color in theme_colors.items():
                colored = Path(tmp) / f"{svg.stem}-{variant}.svg"
                colored.write_text(source.replace("currentColor", "#" + color),
                                   encoding="utf-8")
                render_svg(colored, ASSETS / "icons" / f"{svg.stem}-{variant}.png", 192, None)
        for name, spec in content["assets"]["diagrams"].items():
            svg = diagrams / spec["src"]
            w, _ = svg_size(svg)
            raw = Path(tmp) / f"{name}.png"
            render_svg(svg, raw, round(w * 2), "#FFFFFF")
            crop_save(raw, ASSETS / "images" / f"{name}.png", spec.get("crop"), 2600)
    for name, spec in content["assets"]["previews"].items():
        crop_save(ds / spec["src"], ASSETS / "images" / f"{name}.png", spec.get("crop"), 1200)
    print(f"Assets refreshed under {ASSETS}")


# --------------------------------------------------------------------------
# PDF and previews
# --------------------------------------------------------------------------


def render(pptx: Path):
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        sys.exit("ERROR: --render needs LibreOffice (soffice) on PATH")
    subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir",
                    str(pptx.parent), str(pptx)], check=True, capture_output=True)
    pdf = pptx.with_suffix(".pdf")
    previews = DECK_DIR / "previews"
    previews.mkdir(exist_ok=True)
    for old in previews.glob("slide-*.png"):
        old.unlink()
    subprocess.run(["pdftoppm", "-r", "96", "-png", str(pdf), str(previews / "slide")],
                   check=True)
    for png in previews.glob("slide-*.png"):
        num = int(re.search(r"(\d+)\.png$", png.name).group(1))
        png.rename(previews / f"slide-{num:02d}.png")
    print(f"PDF: {pdf}\nPreviews: {previews}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--refresh-assets", action="store_true",
                    help="re-render brand, icons and diagrams from the sibling repositories")
    ap.add_argument("--design-system", type=Path,
                    default=DECK_DIR.parent.parent / "aroma-pacifico-design-system")
    ap.add_argument("--diagrams", type=Path,
                    default=DECK_DIR.parent.parent / "aroma-pacifico-diagrams")
    ap.add_argument("--team-photos", type=Path,
                    help="crop the team portraits from the original photos in this folder")
    ap.add_argument("--render", action="store_true", help="also export PDF and PNG previews")
    ap.add_argument("--font", help="override the token font family (fallback test)")
    ap.add_argument("--out", type=Path, default=DECK_DIR / f"{OUT_NAME}.pptx")
    args = ap.parse_args()

    content = yaml.safe_load((DECK_DIR / "content.yaml").read_text(encoding="utf-8"))
    if args.refresh_assets:
        tokens = Tokens(args.design_system / "tokens" / "tokens.json")
        colors = {"brand": tokens.color("color.text.brand"),
                  "merged": tokens.color("color.sack.accepted.icon"),
                  "review": tokens.color("color.sack.in-transit.icon"),
                  "pending": tokens.color("color.sack.in-preparation.icon")}
        refresh_assets(content, args.design_system, args.diagrams, colors)
    if args.team_photos:
        refresh_team(content, args.team_photos)

    theme = Theme(Tokens(ASSETS / "tokens.json"), args.font)
    global MEASURE
    MEASURE = Measurer(theme.font)
    count = build(content, theme, args.out)
    print(f"Built {args.out} with {count} slides, font {theme.font} "
          f"(fallback chain: {', '.join(theme.families[1:])})")
    for w in WARNINGS:
        print("WARNING:", w)
    if args.render:
        render(args.out)
    return 1 if WARNINGS else 0


if __name__ == "__main__":
    sys.exit(main())
