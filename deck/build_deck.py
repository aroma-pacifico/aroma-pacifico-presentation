#!/usr/bin/env python3
"""Build the Aroma Pacifico defense deck (PPTX, PDF and PNG previews).

The deck is generated from two inputs:

* deck/content.yaml: slide text, speaker notes and the asset catalog,
  including the catalog of every diagram of aroma-pacifico-diagrams with its
  detail regions.
* deck/assets/tokens.json: a copy of aroma-pacifico-design-system
  tokens/tokens.json (colors, font families, sizes, spacing and radius).

Images (brand marks, icons, diagrams, design-system previews and the QR
code) are rendered once from the sibling repositories with --refresh-assets
and kept under deck/assets/, so a plain rebuild needs neither repository.
Each diagram is rendered whole from its SVG with headless Chrome in tiles at
3x, so no text is lost, then saved at twice the size of the slide box it
fills: the full view, plus one zoomed image per detail region.

Team portraits are cropped with --team-photos DIR into deck/assets/team/.
For each member the newest file in DIR whose name starts with the member's
photo key is used; its eye position and eye-to-chin distance are recorded
per file name in content.yaml, so every face has the same size and eye
height on the team slide.

Usage:
    python3 deck/build_deck.py                      # PPTX only
    python3 deck/build_deck.py --render             # PPTX, PDF and previews
    python3 deck/build_deck.py --refresh-assets \
        --design-system ../aroma-pacifico-design-system \
        --diagrams ../aroma-pacifico-diagrams --render
    python3 deck/build_deck.py --team-photos <dir> --render

Requirements: python-pptx, PyYAML and Pillow. --refresh-assets also needs
Google Chrome or Chromium (headless SVG rendering) and qrcode (QR code).
--render needs LibreOffice (soffice) and pdftoppm (poppler-utils); it writes
the PDF, one 1920-pixel PNG per slide and contact sheets of all slides.
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
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
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
PORTRAIT_FACE = 0.30  # eye-to-chin distance as a share of the portrait height
PORTRAIT_EYES = 0.365  # eye line as a share of the portrait height, from the top
PORTRAIT_MAX_H = 900  # pixels

# Diagram slides: a slim title band, then a content box of at least 85 % of
# the slide area that the diagram fills with a contain fit (never cropped,
# never stretched).
DIAGRAM_BAND = 56.0  # points of title band at the top
DIAGRAM_EDGE = 12.0  # points of margin left, right and bottom
DIAGRAM_BOX = (DIAGRAM_EDGE, DIAGRAM_BAND, SLIDE_W - 2 * DIAGRAM_EDGE,
               SLIDE_H - DIAGRAM_BAND - DIAGRAM_EDGE)
PREVIEW_PX = 1920  # width of the slide previews used for the visual gate
PX_PER_PT = PREVIEW_PX / SLIDE_W
# Diagram images are stored at twice the pixel size of the box at 1920 px.
DIAGRAM_MAX_PX = (round(DIAGRAM_BOX[2] * PX_PER_PT * 2), round(DIAGRAM_BOX[3] * PX_PER_PT * 2))
DIAGRAM_MASTER_SCALE = 3  # SVG units to pixels for the master render
DIAGRAM_MASTER_PIXELS = 80e6  # cap for the largest diagrams (memory)
LEGIBLE_PX = 10
# The caption under a linked diagram: the token caption color and weight,
# at the size that fits the 12 pt band under DIAGRAM_BOX.
DIAGRAM_CAPTION = 11
ARROW_FONT = "DejaVu Sans"  # smallest comfortable body text at 1920 px

WARNINGS: list[str] = []
NOTES: list[str] = []  # informational, do not fail the build


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

    def b_images(self, slide, b, x, y, w, h, where):
        t = self.t
        n = len(b["assets"])
        cw = (w - t.gap * (n - 1)) / n
        for i, name in enumerate(b["assets"]):
            cx = x + i * (cw + t.gap)
            box(slide, cx, y, cw, h, fill=t.surface_subtle, radius=t.radius)
            picture(slide, ASSETS / "images" / f"{name}.png", cx + 8, y + 8, cw - 16, h - 16)

    def b_stats(self, slide, b, x, y, w, h, where):
        """KPI cards: a large value and a label. `cols` wraps them into rows."""
        t = self.t
        items = b["items"]
        cols = b.get("cols", len(items))
        rows = -(-len(items) // cols)
        cw = (w - t.gap * (cols - 1)) / cols
        ch = (h - t.gap * (rows - 1)) / rows
        inner = cw - 2 * t.pad
        compact = ch < 120
        top = 12 if compact else 16
        vmax = t.size_title if compact else t.size_value + 8
        vs = min(fit([it["value"]], inner, vmax * LINE_HEIGHT, vmax, 18, bold=True,
                     where=f"{where}/value") for it in items)
        label_h = ch - top - vs * LINE_HEIGHT - 4 - t.pad_small
        ls = min(fit([it["label"]], inner, label_h, t.size_body, 11,
                     where=f"{where}/label") for it in items)
        for i, it in enumerate(items):
            cx = x + (i % cols) * (cw + t.gap)
            cy = y + (i // cols) * (ch + t.gap)
            box(slide, cx, cy, cw, ch, fill=t.surface, line=t.border_subtle, radius=t.radius)
            box(slide, cx + t.pad, cy, 40, 4, fill=t.accent)
            text(slide, cx + t.pad, cy + top, inner, vs * LINE_HEIGHT, [it["value"]], t, vs,
                 t.text_brand, bold=True)
            ly = cy + top + vs * LINE_HEIGHT + 4
            text(slide, cx + t.pad, ly, inner, cy + ch - ly - 4, [it["label"]], t, ls,
                 t.text_secondary)

    def b_steps(self, slide, b, x, y, w, h, where):
        """A left-to-right sequence of numbered steps joined by arrows."""
        t = self.t
        items = b["items"]
        n = len(items)
        arrow = 18
        cw = (w - arrow * (n - 1)) / n
        inner = cw - 2 * t.pad_small
        badge = 26
        avail = h - t.pad_small * 2 - badge - 8
        size = t.size_body
        while size > 10:
            ok = all(MEASURE.lines(it["title"], size, True, inner) * size * LINE_HEIGHT + 4
                     + MEASURE.lines(it["text"], size - 2, False, inner) * (size - 2)
                     * LINE_HEIGHT <= avail for it in items)
            if ok:
                break
            size -= 0.5
        else:
            WARNINGS.append(f"OVERFLOW risk: {where} steps do not fit at 10 pt")
        for i, it in enumerate(items):
            cx = x + i * (cw + arrow)
            box(slide, cx, y, cw, h, fill=t.surface_subtle, radius=t.radius)
            box(slide, cx + t.pad_small, y + t.pad_small, badge, badge, fill=t.surface_brand,
                radius=badge / 2)
            text(slide, cx + t.pad_small, y + t.pad_small, badge, badge, [str(i + 1)], t, 13,
                 t.text_inverse, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            ty = y + t.pad_small + badge + 8
            text(slide, cx + t.pad_small, ty, inner, y + h - ty - t.pad_small,
                 [it["title"], it["text"]], t, size, t.text_primary, space_after=4,
                 styles=[(size, t.text_primary, True), (size - 2, t.text_secondary, False)])
            if i < n - 1:
                ax = cx + cw + 3
                shp = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Pt(ax), Pt(y + h / 2 - 7),
                                             Pt(arrow - 6), Pt(14))
                st = shp._element.find(qn("p:style"))
                if st is not None:
                    shp._element.remove(st)
                shp.fill.solid()
                shp.fill.fore_color.rgb = rgb(t.accent)
                shp.line.fill.background()

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
    # Minimal chrome: the brand isotype and the slide number, nothing else.

    def footer(self, slide, index, dark=False):
        t = self.t
        y = SLIDE_H - 30
        color = t.text_inverse if dark else t.text_secondary
        iso = ASSETS / "brand" / ("isotype-negative.png" if dark else "isotype.png")
        picture(slide, iso, t.margin, y - 2, 20, 20)
        text(slide, SLIDE_W - t.margin - 60, y, 60, 16, [str(index)], t, 11, color,
             align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)

    def notes(self, slide, s):
        head = []
        if s.get("presenter"):
            who = " y ".join(self.member(c) for c in s["presenter"].split("+"))
            line = f"Presenta: {who}"
            line += f" · Tiempo objetivo: {clock(spoken(s))}"
            head.append(line)
        if s.get("source"):
            head.append(f"Fuente: {s['source']}")
        body = s.get("notes", "").strip()
        slide.notes_slide.notes_text_frame.text = "\n".join(head + ([""] if head else []) + [body])

    # --- slide kinds -----------------------------------------------------

    def content(self, slide, s, index):
        t = self.t
        box(slide, 0, 0, SLIDE_W, SLIDE_H, fill=t.surface)
        box(slide, 0, 0, SLIDE_W, 6, fill=t.surface_brand)
        tw = SLIDE_W - 2 * t.margin
        size = next((v / 2 for v in range(int(t.size_title * 2), 43, -1)
                     if MEASURE.lines(s["title"], v / 2, True, tw) == 1), None)
        if size is None:
            size = fit([s["title"]], tw, 52, t.size_title - 2, 18, bold=True,
                       where=f"slide {index} title")
        text(slide, t.margin, 20, tw, 50, [s["title"]], t, size, t.text_primary, bold=True,
             anchor=MSO_ANCHOR.BOTTOM)
        sub = s.get("subtitle", "")
        ss = fit([sub], tw, 22, t.size_body_large, 12, where=f"slide {index} subtitle")
        text(slide, t.margin, 74, tw, 24, [sub], t, ss, t.text_secondary)
        box(slide, t.margin, 104, 48, 3, fill=t.accent)
        top, bottom = 120, SLIDE_H - 44
        self.blocks(slide, s["blocks"], t.margin, top, tw, bottom - top, f"slide {index}")
        self.footer(slide, index)

    def diagram(self, slide, s, index):
        """A diagram on almost the whole slide: a slim title band, then the
        image placed with a contain fit inside DIAGRAM_BOX."""
        t = self.t
        box(slide, 0, 0, SLIDE_W, SLIDE_H, fill=t.surface)
        box(slide, 0, 0, SLIDE_W, 4, fill=t.surface_brand)
        x0 = DIAGRAM_EDGE + 4
        tw = SLIDE_W - x0 - 110
        size = next((v / 2 for v in range(44, 27, -1)
                     if MEASURE.lines(s["title"], v / 2, True, tw) == 1), None)
        if size is None:
            size = 14
            WARNINGS.append(f"OVERFLOW risk: slide {index} diagram title is long")
        text(slide, x0, 8, tw, 26, [s["title"]], t, size, t.text_primary, bold=True,
             anchor=MSO_ANCHOR.MIDDLE)
        sub = s.get("subtitle", "")
        ss = fit([sub], tw, 15, 11.5, 9, where=f"slide {index} diagram subtitle")
        text(slide, x0, 35, tw, 16, [sub], t, ss, t.text_secondary, anchor=MSO_ANCHOR.MIDDLE)
        chip = s.get("chip")
        right = SLIDE_W - DIAGRAM_EDGE - 4
        text(slide, right - 40, 12, 40, 18, [str(index)], t, 11, t.text_secondary,
             align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
        picture(slide, ASSETS / "brand" / "isotype.png", right - 64, 12, 18, 18)
        if chip:
            cw = MEASURE.width(chip, 9.5, True) + 16
            box(slide, right - cw, 33, cw, 16, fill=t.surface_brand, radius=8)
            text(slide, right - cw, 33, cw, 16, [chip], t, 9.5, t.text_inverse, bold=True,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        path = ASSETS / s["image"] if s.get("image") else diagram_image(s["asset"], s.get("detail"))
        x, y, w, h = DIAGRAM_BOX
        px, py, pw, ph = picture(slide, path, x, y, w, h)
        if not s.get("image"):
            self.placed.append((index, s["asset"], s.get("detail"), pw, ph))
        # Every diagram opens its high-resolution view on the project
        # website. The picture and its caption both carry the link, and
        # LibreOffice keeps both as link annotations in the PDF.
        url = f"{self.meta['website']}#diagrama/{diagram_slug(self.catalog[s['asset']])}"
        slide.shapes[-1].click_action.hyperlink.address = url
        cap = "Abrir con zoom en el sitio \u2197"
        cs = DIAGRAM_CAPTION
        cw = MEASURE.width(cap, cs, True) + 20
        ch = cs * 1.3 + 6
        cx = px + pw - cw
        # Below the picture when it leaves room, so the button never covers it.
        cy = py + ph + 4 if py + ph + 4 + ch <= SLIDE_H - 2 else min(py + ph - ch / 2,
                                                                       SLIDE_H - ch - 2)
        box(slide, cx, cy, cw, ch, fill="FFFFFF", line=t.brand_primary, radius=ch / 2)
        slide.shapes[-1].click_action.hyperlink.address = url
        text(slide, cx, cy, cw, ch, [cap], t, cs, t.brand_primary, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        caption = slide.shapes[-1]
        caption.click_action.hyperlink.address = url
        # Roboto has no arrow glyph and the fallback would pick a color emoji
        # font, so the arrow is its own run in a text symbol font.
        run = caption.text_frame.paragraphs[0].runs[0]
        run.text = cap[:-1]
        arrow = caption.text_frame.paragraphs[0].add_run()
        arrow.text = cap[-1]
        arrow.font.name = ARROW_FONT
        arrow.font.size = run.font.size
        arrow.font.color.rgb = rgb(t.brand_primary)
        self.links += 1

    def cover(self, slide, s, index):
        t = self.t
        box(slide, 0, 0, SLIDE_W, SLIDE_H, fill=t.surface_brand_strong)
        picture(slide, ASSETS / "brand" / "logo-negative.png", t.margin, 48, 300, 95,
                align="left")
        box(slide, t.margin, 178, 64, 4, fill=t.accent)
        text(slide, t.margin, 196, 760, 22, [s["eyebrow"].upper()], t, 14, t.text_inverse,
             bold=True, letter=1.5)
        text(slide, t.margin, 224, 860, 120, [s["title"]], t, t.size_display,
             t.text_inverse, bold=True)
        text(slide, t.margin, 344, 860, 30, [s["subtitle"]], t, t.size_heading,
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
        hw = (SLIDE_W - 2 * t.margin) / 2
        for i, (label, align) in enumerate(((s["institution"], PP_ALIGN.LEFT),
                                            (str(index), PP_ALIGN.RIGHT))):
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
        y = SLIDE_H - 34
        box(slide, t.margin, y - 10, SLIDE_W - 2 * t.margin, 1, fill=t.border_subtle)
        picture(slide, ASSETS / "brand" / "isotype.png", t.margin, y - 2, 22, 22)

    def annex_links(self, slide, s, index):
        """Annex: every diagram with its code and a link that opens it in the
        zoomable viewer of the project website."""
        t = self.t
        box(slide, 0, 0, SLIDE_W, SLIDE_H, fill=t.surface)
        box(slide, 0, 0, SLIDE_W, 6, fill=t.surface_brand)
        tw = SLIDE_W - 2 * t.margin
        text(slide, t.margin, 20, tw, 50, [s["title"]], t, 26, t.text_primary, bold=True,
             anchor=MSO_ANCHOR.BOTTOM)
        ss = fit([s["subtitle"]], tw, 22, t.size_body_large, 11, where=f"slide {index} subtitle")
        text(slide, t.margin, 74, tw, 24, [s["subtitle"]], t, ss, t.text_secondary)
        box(slide, t.margin, 104, 48, 3, fill=t.accent)
        items = list(self.catalog.items())
        half = (len(items) + 1) // 2
        gap = 24
        cw = (tw - gap) / 2
        top, rh = 118, 28.5
        for i, (key, spec) in enumerate(items):
            col, row = divmod(i, half)
            x, y = t.margin + col * (cw + gap), top + row * rh
            url = f"{self.meta['website']}#diagrama/{diagram_slug(spec)}"
            box(slide, x, y + 2, cw, rh - 4, fill="FFFFFF", line=t.border_subtle, radius=6)
            code = f"A{i + 1:02d}"
            box(slide, x + 6, y + 6, 36, rh - 12, fill=t.surface_brand, radius=4)
            text(slide, x + 6, y + 6, 36, rh - 12, [code], t, 9.5, t.text_inverse, bold=True,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            label = spec["title"]
            size = fit([label], cw - 76, rh - 8, 11.5, 8.5, where=f"slide {index} link {code}")
            text(slide, x + 50, y + 2, cw - 76, rh - 4, [label], t, size, t.text_primary,
                 anchor=MSO_ANCHOR.MIDDLE)
            slide.shapes[-1].click_action.hyperlink.address = url
            text(slide, x + cw - 24, y + 2, 18, rh - 4, ["\u2197"], t, 12, t.text_brand,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            arrow = slide.shapes[-1]
            arrow.text_frame.paragraphs[0].runs[0].font.name = ARROW_FONT
            arrow.click_action.hyperlink.address = url
            self.links += 1
        self.footer(slide, index)

    def qr(self, slide, s, index):
        t = self.t
        box(slide, 0, 0, SLIDE_W, SLIDE_H, fill=t.surface_brand_strong)
        picture(slide, ASSETS / "brand" / "logo-negative.png", t.margin, 64, 260, 82,
                align="left")
        box(slide, t.margin, 178, 64, 4, fill=t.accent)
        q = 372
        qx, qy = SLIDE_W - t.margin - q + 16, (SLIDE_H - q) / 2
        tw = qx - t.margin - 32
        size = fit([s["title"]], tw, 110, t.size_display, 28, bold=True,
                   where=f"slide {index} qr title")
        text(slide, t.margin, 196, tw, 110, [s["title"]], t, size, t.text_inverse, bold=True)
        ss = fit([s["subtitle"]], tw, 92, t.size_body_large, 14,
                 where=f"slide {index} qr subtitle")
        text(slide, t.margin, 306, tw, 92, [s["subtitle"]], t, ss, t.text_inverse)
        us = fit([s["url"]], tw, 22, t.size_body, 12, bold=True,
                 where=f"slide {index} qr url")
        text(slide, t.margin, 410, tw, 22, [s["url"]], t, us, t.accent, bold=True)
        slide.shapes[-1].click_action.hyperlink.address = self.meta["website"]
        # The QR image carries its own white quiet zone, so the card is only
        # the rounded frame around it.
        box(slide, qx, qy, q, q, fill="FFFFFF", radius=t.radius)
        picture(slide, ASSETS / "images" / "qr-web.png", qx + 6, qy + 6, q - 12, q - 12)
        slide.shapes[-1].click_action.hyperlink.address = self.meta["website"]
        self.footer(slide, index, dark=True)


def diagram_slug(spec: dict) -> str:
    """Slug of a diagram on the project website: the stem of its file in
    aroma-pacifico-web/assets/diagrams/, which is `<folder>-<name>` of the
    source path unless the name already starts with the folder."""
    folder, _, name = spec["src"].removesuffix(".svg").rpartition("/")
    return spec.get("web") or (name if name.startswith(f"{folder}-") else f"{folder}-{name}")


def diagram_image(key: str, detail: int | None) -> Path:
    name = key if not detail else f"{key}-d{detail}"
    return ASSETS / "diagrams" / f"{name}.png"


def expand(content: dict) -> list[dict]:
    """Expand `annex` into one slide per diagram view and drop slides whose
    optional diagram is not rendered yet. Fills the annex titles."""
    catalog = content["assets"]["diagrams"]
    out = []
    for s in content["slides"]:
        if s["kind"] == "diagram":
            spec = catalog[s["asset"]]
            if not s.get("image") and not diagram_image(s["asset"], s.get("detail")).exists():
                if spec.get("optional"):
                    NOTES.append(f"SKIPPED: diagram slide {s['asset']} (not rendered yet)")
                    continue
                sys.exit(f"ERROR: missing diagram image for {s['asset']}; run --refresh-assets")
            out.append(s)
        else:
            out.append(s)
    for i, s in enumerate(out, start=1):
        s["_index"] = i
    for s in out:
        if s.get("full_of"):
            s["subtitle"] += f" · vista completa en la diapositiva {s['full_of']['_index']}"
    return out


def build(content: dict, theme: Theme, out: Path):
    prs = Presentation()
    prs.slide_width = Emu(int(Pt(SLIDE_W)))
    prs.slide_height = Emu(int(Pt(SLIDE_H)))
    prs.core_properties.title = content["meta"]["title"]
    prs.core_properties.language = "es-CO"
    prs.core_properties.author = "Aroma Pacífico"
    blank = prs.slide_layouts[6]
    slides = expand(content)
    r = Renderer(theme, len(slides), content["meta"])
    r.placed = []
    r.catalog = content["assets"]["diagrams"]
    r.links = 0
    for i, s in enumerate(slides, start=1):
        slide = prs.slides.add_slide(blank)
        getattr(r, "team_slide" if s["kind"] == "team" else s["kind"])(slide, s, i)
        r.notes(slide, s)
    prs.save(out)
    legibility_report(content, r.placed)
    write_script(content, slides, r)
    NOTES.append(f"{r.links} diagram slides link to their high-resolution view")
    return len(slides)


WORDS_PER_MINUTE = 130


def spoken(s: dict) -> int:
    """Target seconds of a slide: its speaker notes read aloud at
    WORDS_PER_MINUTE, rounded to 5 seconds, never under 10."""
    words = len(s.get("notes", "").split())
    return max(10, round(words * 60 / WORDS_PER_MINUTE / 5) * 5)


def clock(n: int) -> str:
    return f"{n // 60}:{n % 60:02d}"


def write_script(content: dict, slides: list, r) -> None:
    """Write docs/guion-sustentacion.md from the same text as the speaker
    notes, so the script and the PPTX never disagree."""
    meta, script = content["meta"], content["script"]
    talk = [s for s in slides if s.get("presenter")]
    annex = [s for s in slides if s["kind"] == "annex_links"]
    total = sum(spoken(s) for s in talk)
    low, high = (int(v) for v in re.findall(r"\d+", script["target"])[:2])
    if not low * 60 <= total <= high * 60:
        WARNINGS.append(f"talk lasts {clock(total)}, outside the {script['target']} target")
    blocks = []
    for s in talk:
        if blocks and blocks[-1]["who"] == s["presenter"]:
            blocks[-1]["slides"].append(s)
        else:
            blocks.append({"who": s["presenter"], "slides": [s]})
    first = {m["code"]: m["first"].split()[0] for m in meta["team"]}
    full = {m["code"]: f"{m['first']} {m['last']}" for m in meta["team"]}

    def span(b):
        return f"{b['slides'][0]['_index']} a {b['slides'][-1]['_index']}"

    out = ["# Guion de la sustentación", "",
           "| Campo | Valor |", "|---|---|",
           f"| Estado | {script['status']} |",
           f"| Issue | {script['issue']} |",
           f"| Presentación | `deck/{OUT_NAME}.pptx` y `.pdf`: {len(slides)} diapositivas, "
           f"{talk[0]['_index']} a {talk[-1]['_index']} de exposición y "
           f"la {annex[0]['_index']} de anexo con los enlaces a cada diagrama"
           + (f", y la {slides[-1]['_index']} repite el cierre con el código QR"
              if slides[-1]["kind"] == "qr" and not slides[-1].get("presenter") else "")
           + " |",
           f"| Duración | {clock(total)} de exposición, dentro de la meta de "
           f"{script['target']} |",
           "| Fuente | Generado por `deck/build_deck.py` desde `deck/content.yaml`; "
           "las notas del orador del PPTX tienen el mismo texto. No se edita a mano. |",
           "", script["intro"].strip(), "",
           "## Reparto y tiempos", "",
           "| Bloque | Presenta | Diapositivas | Tiempo |", "|---|---|---|---|"]
    for n, b in enumerate(blocks, start=1):
        t = sum(spoken(s) for s in b["slides"])
        out.append(f"| {n} | {full[b['who']]} ({b['who']}) | {span(b)} | {clock(t)} |")
    per = {}
    for s in talk:
        per[s["presenter"]] = per.get(s["presenter"], 0) + spoken(s)
    out += [f"| Total | {', '.join(f'{c} {clock(v)}' for c, v in per.items())} | "
            f"{talk[0]['_index']} a {talk[-1]['_index']} | {clock(total)} |", ""]
    out += ["## Guion por diapositiva", ""]
    for n, b in enumerate(blocks, start=1):
        t = sum(spoken(s) for s in b["slides"])
        out += [f"### Bloque {n}: {full[b['who']]} ({b['who']}), diapositivas {span(b)}, "
                f"{clock(t)}", ""]
        for s in b["slides"]:
            title = s.get("title", "")
            out += [f"**Diapositiva {s['_index']} ({clock(spoken(s))}). {title}**", ""]
            out += [s.get("notes", "").strip(), ""]
            if s.get("source"):
                out += [f"Fuente: {s['source']}.", ""]
        if n < len(blocks):
            nxt = blocks[n]
            out += [f"*Transición: {first[b['who']]} cede la palabra a {first[nxt['who']]}, "
                    f"que continúa en la diapositiva {nxt['slides'][0]['_index']}.*", ""]
    out += ["## Anexo para preguntas", "", script["annex"].strip(), "",
            "| Anexo | Diagrama (enlace con zoom) | Fuente | Diapositiva |", "|---|---|---|---|"]
    for i, (key, spec) in enumerate(content["assets"]["diagrams"].items(), start=1):
        url = f"{meta['website']}#diagrama/{diagram_slug(spec)}"
        out.append(f"| A{i:02d} | [{spec['title']}]({url}) | `{spec['src']}` | {annex[0]['_index']} |")
    (DECK_DIR.parent / "docs" / "guion-sustentacion.md").write_text(
        "\n".join(out).rstrip() + "\n", encoding="utf-8")


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
    diagrams use foreignObject labels and the brand marks use SVG masks.
    Large images are rendered in tiles of at most TILE pixels and stitched,
    because a single very large Chrome screenshot silently truncates."""
    tile = 3000
    w, h = svg_size(svg)
    W, H = width_px, round(width_px * h / w)
    bg = background or "transparent"
    mode = "RGB" if background else "RGBA"
    canvas = Image.new(mode, (W, H), background or (0, 0, 0, 0))
    with tempfile.TemporaryDirectory() as tmp:
        for ty in range(0, H, tile):
            for tx in range(0, W, tile):
                tw, th = min(tile, W - tx), min(tile, H - ty)
                page = Path(tmp) / "page.html"
                page.write_text(
                    f'<html><body style="margin:0;background:{bg};overflow:hidden">'
                    f'<img src="{svg.resolve().as_uri()}" style="position:absolute;'
                    f'left:{-tx}px;top:{-ty}px;width:{W}px;height:{H}px;display:block">'
                    "</body></html>", encoding="utf-8")
                shot = Path(tmp) / "shot.png"
                subprocess.run([chrome_binary(), "--headless=new", "--disable-gpu",
                                "--no-sandbox", "--hide-scrollbars",
                                "--force-device-scale-factor=1", f"--window-size={tw},{th}",
                                "--default-background-color=00000000",
                                f"--screenshot={shot}", page.as_uri()],
                               check=True, capture_output=True, timeout=600)
                with Image.open(shot) as part:
                    canvas.paste(part.convert(mode).crop((0, 0, tw, th)), (tx, ty))
    canvas.save(out)


def svg_text_sizes(svg: Path) -> list[float]:
    """Font sizes, in SVG units, of every text label in a draw.io export."""
    src = svg.read_text(encoding="utf-8", errors="ignore")
    return ([float(v) for v in re.findall(r"font-size:\s*([\d.]+)px", src)]
            + [float(v) for v in re.findall(r'font-size="([\d.]+)(?:px)?"', src)])


def body_size(sizes: list[float]) -> float:
    """The smallest font size used by at least five labels: the size of the
    body text, ignoring a stray footnote."""
    counts = {}
    for v in sizes:
        counts[v] = counts.get(v, 0) + 1
    common = [v for v, n in counts.items() if n >= 5]
    return min(common or sizes or [12.0])


def save_diagram(im: Image.Image, out: Path):
    """Fit inside DIAGRAM_MAX_PX (never upscaled) and save as an indexed PNG:
    the diagrams use flat colors, so 256 colors keep text and icons sharp at
    a fraction of the size."""
    im = im.convert("RGB")
    scale = min(DIAGRAM_MAX_PX[0] / im.width, DIAGRAM_MAX_PX[1] / im.height, 1.0)
    if scale < 1.0:
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    im.quantize(colors=256, method=Image.Quantize.MEDIANCUT,
                dither=Image.Dither.NONE).save(out, optimize=True)


def trim_white(im: Image.Image, pad: int) -> Image.Image:
    """Crop uniform white margins, keeping `pad` pixels of air."""
    gray = im.convert("L").point(lambda v: 255 if v < 245 else 0)
    bbox = gray.getbbox()
    if not bbox:
        return im
    l, t, r, b = bbox
    return im.crop((max(0, l - pad), max(0, t - pad), min(im.width, r + pad),
                    min(im.height, b + pad)))


def refresh_diagrams(content: dict, diagrams: Path):
    out_dir = ASSETS / "diagrams"
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {}
    with tempfile.TemporaryDirectory() as tmp:
        for key, spec in content["assets"]["diagrams"].items():
            svg = diagrams / spec["src"]
            if not svg.exists():
                if spec.get("optional"):
                    print(f"Diagram {key}: {spec['src']} not found, skipped (optional)")
                    continue
                sys.exit(f"ERROR: {svg} not found")
            w, h = svg_size(svg)
            raw = Path(tmp) / f"{key}.png"
            scale = min(DIAGRAM_MASTER_SCALE, (DIAGRAM_MASTER_PIXELS / (w * h)) ** 0.5)
            render_svg(svg, raw, round(w * scale), "#FFFFFF")
            for stale in out_dir.glob(f"{key}-d*.png"):
                stale.unlink()
            with Image.open(raw) as master:
                master = master.convert("RGB")
                save_diagram(trim_white(master, 24), out_dir / f"{key}.png")
                for k, d in enumerate(spec.get("details", []), start=1):
                    l, t, r, b = d["box"]
                    crop = master.crop((round(l * master.width), round(t * master.height),
                                        round(r * master.width), round(b * master.height)))
                    save_diagram(crop, out_dir / f"{key}-d{k}.png")
            meta[key] = {"svg_units": [w, h], "body_px": body_size(svg_text_sizes(svg))}
            print(f"Diagram {key}: {spec['src']} rendered with "
                  f"{len(spec.get('details', []))} detail views")
    (out_dir / "diagrams.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def legibility_report(content: dict, placed: list):
    """Body text height at 1920 px for every diagram view in the deck. A full
    view below LEGIBLE_PX needs detail views; the annex has them."""
    meta_path = ASSETS / "diagrams" / "diagrams.json"
    if not meta_path.exists():
        return
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    catalog = content["assets"]["diagrams"]
    lines = []
    for index, key, detail, pw, ph in placed:
        w, h = meta[key]["svg_units"]
        if detail:
            l, t, r, b = catalog[key]["details"][detail - 1]["box"]
            w, h = w * (r - l), h * (b - t)
        px = meta[key]["body_px"] * pw / w * PX_PER_PT
        has_detail = bool(catalog[key].get("details"))
        if px >= LEGIBLE_PX:
            flag = "OK"
        elif not detail and has_detail:
            flag = "FULL VIEW, SEE DETAIL VIEWS"
        elif px >= LEGIBLE_PX - 1:
            flag = "ABOUT 10 PX"
        else:
            flag = "SMALL"
        lines.append(f"{index:>4}  {key + (f' detail {detail}' if detail else ''):<44}"
                     f"{px:5.1f} px  {flag}")
        if flag == "SMALL":
            WARNINGS.append(f"LEGIBILITY: slide {index} {key} body text {px:.1f} px at 1920")
    report = DECK_DIR / "previews" / "diagram-legibility.txt"
    report.parent.mkdir(exist_ok=True)
    report.write_text("Body text height of each diagram view at 1920 px (smallest font used "
                      "by five or more labels)\n" + "\n".join(lines) + "\n", encoding="utf-8")


QR_DARK = "#0a3a41"  # brand primary, 12.4:1 on white


def make_qr(url: str, out: Path):
    """The website QR: error correction H, brand primary on white, with the
    standard four-module quiet zone. It is decoded back before it is kept."""
    try:
        import qrcode
        from qrcode.constants import ERROR_CORRECT_H
    except ImportError:
        sys.exit("ERROR: the QR code needs the qrcode package (pip install 'qrcode[pil]')")
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=24, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    qr.make_image(fill_color=QR_DARK, back_color="white").convert("RGB").save(out, optimize=True)
    decoded = decode_qr(out)
    if decoded is not None and decoded != url:
        sys.exit(f"ERROR: the QR code decodes to {decoded!r}, not {url!r}")


def decode_qr(path: Path) -> str | None:
    """Decode a QR image with zbar (pyzbar) or, without zbar, with zxing-cpp.
    Returns None when no decoder is installed."""
    with Image.open(path) as im:
        im = im.convert("L")
        try:
            from pyzbar import pyzbar
            found = pyzbar.decode(im)
            return found[0].data.decode() if found else ""
        except ImportError:
            pass
        try:
            import zxingcpp
            found = zxingcpp.read_barcodes(im)
            return found[0].text if found else ""
        except ImportError:
            NOTES.append("QR not decoded: install pyzbar (with zbar) or zxing-cpp")
            return None


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
    photo fades into it; other the sides are mirrored and the bottom row is extended. A warning is printed."""
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
            # Repeat the last row: clothing continues straight down instead
            # of reflecting the tie or the collar.
            canvas.paste(im.crop((0, h - 1, w, h)).resize((w, pb)), (pl, pt + h))
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


def newest_photo(photos: Path, key: str) -> Path:
    """The most recently modified photo in `photos` whose name starts with
    `key`, so a replacement photo is picked up without editing this file."""
    found = sorted((f for f in photos.iterdir()
                    if f.is_file() and f.name.lower().startswith(key.lower())),
                   key=lambda f: f.stat().st_mtime)
    if not found:
        sys.exit(f"ERROR: no photo starting with {key!r} in {photos}")
    return found[-1]


def refresh_team(content: dict, photos: Path):
    (ASSETS / "team").mkdir(parents=True, exist_ok=True)
    for name, variants in content["assets"]["team"].items():
        src = newest_photo(photos, name)
        if src.name not in variants:
            sys.exit(f"ERROR: {src.name} has no eye position in content.yaml assets.team.{name}")
        size = crop_portrait(src, ASSETS / "team" / f"{name}.jpg", variants[src.name])
        print(f"Portrait {name}: {src.name}, {size[0]} x {size[1]} px")


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
    for name, spec in content["assets"]["previews"].items():
        crop_save(ds / spec["src"], ASSETS / "images" / f"{name}.png", spec.get("crop"), 1200)
    make_qr(content["meta"]["website"], ASSETS / "images" / "qr-web.png")
    refresh_diagrams(content, diagrams)
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
    for old in list(previews.glob("slide-*.png")) + list(previews.glob("contact-sheet-*.png")):
        old.unlink()
    subprocess.run(["pdftoppm", "-scale-to-x", str(PREVIEW_PX), "-scale-to-y", "-1", "-png",
                    str(pdf), str(previews / "raw")], check=True)
    pngs = []
    for png in previews.glob("raw-*.png"):
        num = int(re.search(r"(\d+)\.png$", png.name).group(1))
        dest = previews / f"slide-{num:03d}.png"
        with Image.open(png) as im:
            # 256 indexed colors: the slides are flat colors, and the file
            # is less than half the size.
            im.convert("RGB").quantize(256, method=Image.Quantize.MEDIANCUT,
                                       dither=Image.Dither.NONE).save(dest, optimize=True)
        png.unlink()
        pngs.append((num, dest))
    contact_sheets(sorted(pngs), previews)
    print(f"PDF: {pdf}\nPreviews: {previews} ({len(pngs)} slides at {PREVIEW_PX} px)")


def contact_sheets(pngs: list, out_dir: Path, per_sheet: int = 30, cols: int = 5):
    """Thumbnails of every slide with its number, for the review."""
    tw = 380
    th = round(tw * SLIDE_H / SLIDE_W)
    label = 22
    font = ImageFont.truetype(_font_file("DejaVu Sans:bold") or _font_file("Arial:bold"), 15)
    for sheet, start in enumerate(range(0, len(pngs), per_sheet), start=1):
        chunk = pngs[start:start + per_sheet]
        rows = -(-len(chunk) // cols)
        im = Image.new("RGB", (cols * (tw + 12) + 12, rows * (th + label + 12) + 12), "#d9d9d9")
        draw = ImageDraw.Draw(im)
        for i, (num, path) in enumerate(chunk):
            x = 12 + (i % cols) * (tw + 12)
            y = 12 + (i // cols) * (th + label + 12)
            with Image.open(path) as sl:
                im.paste(sl.convert("RGB").resize((tw, th), Image.LANCZOS), (x, y + label))
            draw.text((x, y + 2), f"{num}", fill="#0a3a41", font=font)
        im.save(out_dir / f"contact-sheet-{sheet}.png", optimize=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--refresh-assets", action="store_true",
                    help="re-render brand, icons and diagrams from the sibling repositories")
    ap.add_argument("--design-system", type=Path,
                    default=DECK_DIR.parent.parent / "aroma-pacifico-design-system")
    ap.add_argument("--diagrams", type=Path,
                    default=DECK_DIR.parent.parent / "aroma-pacifico-diagrams")
    ap.add_argument("--refresh-diagrams", action="store_true",
                    help="re-render only the diagrams and their detail views")
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
    elif args.refresh_diagrams:
        make_qr(content["meta"]["website"], ASSETS / "images" / "qr-web.png")
        refresh_diagrams(content, args.diagrams)
    if args.team_photos:
        refresh_team(content, args.team_photos)

    theme = Theme(Tokens(ASSETS / "tokens.json"), args.font)
    global MEASURE
    MEASURE = Measurer(theme.font)
    if not (ASSETS / "images" / "qr-web.png").exists():
        make_qr(content["meta"]["website"], ASSETS / "images" / "qr-web.png")
    count = build(content, theme, args.out)
    print(f"Built {args.out} with {count} slides, font {theme.font} "
          f"(fallback chain: {', '.join(theme.families[1:])})")
    for n in NOTES:
        print("NOTE:", n)
    for w in WARNINGS:
        print("WARNING:", w)
    if args.render:
        render(args.out)
    return 1 if WARNINGS else 0


if __name__ == "__main__":
    sys.exit(main())
