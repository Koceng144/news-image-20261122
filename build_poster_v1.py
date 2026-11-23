#!/usr/bin/env python3
"""Build-time composer for Variant 1 (cinematic poster) of news-image-20261122.

REVISED (Rozak: v1 was "oke cuma terlalu basic") — maximal poster:
- three generated scenes (COP31 key art + 186-drones night sky + corvette
  Merkury sinking), all one style bible: ink-navy, amber-gold, painterly
- layered panels with gold rules/frames, corner ornaments, film grain,
  vignette, serif hierarchy, region color accents
- "THE DAY IN UTC" timeline band, stat strip with gold rings
- drawn spot pictograms on the 12 cards
POLISH PASS (Rozak: "bisa poles sedikit lagi?") — targeted fixes only:
- card body second line no longer clipped by panel bottom (taller cards,
  tighter body leading); DATE CHECK third line pulled inside its box
- vertical rhythm rebalanced to fund the extra card/box height
- drones thumbnail brightened to match the corvette scene; card
  pictograms lightened for legibility

Stories come from main.py (single source of truth). Writes poster_v1.png;
the grade-time entrypoint main_v1.py only copies it to /output/entry.png.
"""

import importlib.util
import os
import random

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
KEYART = os.path.join(
    HERE, "assets_v1",
    "media-generation-cop31-keyart-0-a5634ad5-ae67-4fac-bd44-e627aad64a55.jpg")
DRONES = os.path.join(
    HERE, "assets_v1", "ship",
    "media-generation-drones-ukraine-night-0-52c9df25-d1eb-4be5-a01e-89f76728f719.jpg")
CORVETTE = os.path.join(
    HERE, "assets_v1", "ship",
    "media-generation-corvette-benghazi-sinking-0-c3f04533-7939-4456-8a60-400b9524073c.jpg")
OUT = os.path.join(HERE, "poster_v1.png")

spec = importlib.util.spec_from_file_location(
    "broadsheet", os.path.join(HERE, "main.py"))
data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data)

W = H = 1024
MARGIN = 30
CW = W - 2 * MARGIN

BG = (8, 12, 19)
PANEL = (16, 22, 33)
PANEL_EDGE = (58, 70, 92)
GOLD = (216, 164, 65)
GOLD_DIM = (150, 112, 44)
CREAM = (238, 233, 221)
MUTED = (156, 164, 178)
FAINT = (108, 117, 132)

REGION_COLORS = {
    "EUROPE": (96, 150, 220),
    "ASIA": (230, 150, 70),
    "MIDDLE EAST": (170, 120, 220),
    "AFRICA": (160, 175, 80),
    "AMERICAS": (80, 190, 150),
    "OCEANIA": (90, 180, 210),
    "GLOBAL": (165, 165, 165),
}

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
COND_B = "/usr/share/fonts/truetype/noto/NotoSans-CondensedBold.ttf"
COND_R = "/usr/share/fonts/truetype/noto/NotoSans-Condensed.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def truncate(draw, text, fnt, max_w):
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    while text and draw.textlength(text + "…", font=fnt) > max_w:
        text = text[:-1]
    return text + "…"


def cover_crop(img, tw, th):
    sw, sh = img.size
    scale = max(tw / sw, th / sh)
    nw, nh = int(sw * scale + 0.5), int(sh * scale + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS)
    x = (nw - tw) // 2
    y = (nh - th) // 2
    return img.crop((x, y, x + tw, y + th))


def fade_bottom(canvas, y0, y1):
    strip = canvas.crop((0, y0, W, y1))
    bg = Image.new("RGB", strip.size, BG)
    h = y1 - y0
    mask = Image.new("L", (1, h))
    for i in range(h):
        mask.putpixel((0, i), int(255 * (i / max(h - 1, 1)) ** 1.6))
    mask = mask.resize(strip.size)
    canvas.paste(Image.composite(bg, strip, mask), (0, y0))


def panel(draw, x, y, w, h, accent=None):
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=PANEL,
                   outline=PANEL_EDGE, width=1)
    draw.rectangle([x + 2, y + 2, x + w - 3, y + h - 3],
                   outline=(34, 43, 60), width=1)
    if accent:
        draw.rectangle([x, y, x + 3, y + h - 1], fill=accent)


def gold_rule(draw, y, x0=MARGIN, x1=W - MARGIN):
    draw.line([x0, y, x1, y], fill=GOLD_DIM, width=1)
    draw.line([x0, y + 3, x1, y + 3], fill=(70, 56, 28), width=1)
    cx = (x0 + x1) // 2
    draw.polygon([(cx, y - 3), (cx + 5, y + 1), (cx, y + 5), (cx - 5, y + 1)],
                 fill=GOLD)


def corner_ornament(draw, x, y, dx, dy):
    draw.line([x, y, x + 26 * dx, y], fill=GOLD, width=2)
    draw.line([x, y, x, y + 26 * dy], fill=GOLD, width=2)
    draw.ellipse([x + 5 * dx - 2, y + 5 * dy - 2, x + 5 * dx + 2,
                  y + 5 * dy + 2], fill=GOLD)


def story_block(draw, st, x, y, w, head_size, body_size, body_lines,
                num_size=15, text_x=None):
    num, region, loc, beat, head, body, src, cert = st[:8]
    color = REGION_COLORS.get(region, GOLD)
    tx = x + 34 if text_x is None else text_x
    f_num = font(SERIF_B, num_size)
    draw.text((x + 10, y + 5), str(num), font=f_num, fill=GOLD)
    f_meta = font(COND_B, 10)
    meta = ("%s · %s" % (loc, beat) if beat == cert
            else "%s · %s · %s" % (loc, beat, cert))
    draw.text((tx, y + 7), meta, font=f_meta, fill=color)
    f_head = font(SANS_B, head_size)
    draw.text((tx, y + 19),
              truncate(draw, head, f_head, x + w - tx - 8),
              font=f_head, fill=CREAM)
    f_body = font(COND_R, body_size)
    lines = wrap(draw, body, f_body, x + w - tx - 8)[:body_lines]
    ly = y + 19 + head_size + 2
    for ln in lines:
        draw.text((tx, ly), ln, font=f_body, fill=MUTED)
        ly += body_size + 2
    return ly


def spot_icon(draw, kind, cx, cy, color):
    """Tiny line pictograms for the 12 cards, drawn at ~20px."""
    s = 9
    if kind == "building":
        draw.rectangle([cx - 6, cy - 8, cx + 6, cy + 8], outline=color)
        for yy in (-4, 0, 4):
            draw.line([cx - 3, cy + yy, cx + 3, cy + yy], fill=color)
    elif kind == "radar":
        draw.arc([cx - s, cy - s, cx + s, cy + s], 200, 340, fill=color)
        draw.arc([cx - 5, cy - 5, cx + 5, cy + 5], 200, 340, fill=color)
        draw.line([cx, cy, cx + 7, cy - 7], fill=color)
        draw.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], fill=color)
    elif kind == "flame":
        draw.polygon([(cx, cy - 9), (cx + 5, cy + 2), (cx + 3, cy + 8),
                      (cx - 3, cy + 8), (cx - 5, cy + 2)], outline=color)
    elif kind == "ballot":
        draw.rectangle([cx - 7, cy - 1, cx + 7, cy + 8], outline=color)
        draw.rectangle([cx - 3, cy - 8, cx + 3, cy - 1], outline=color)
    elif kind == "bat":
        draw.polygon([(cx - 2, cy - 9), (cx + 3, cy - 9), (cx + 5, cy + 9),
                      (cx - 4, cy + 9)], outline=color)
        draw.ellipse([cx + 4, cy + 3, cx + 9, cy + 8], outline=color)
    elif kind == "flag":
        draw.line([cx - 6, cy - 9, cx - 6, cy + 9], fill=color)
        for r in range(3):
            for c in range(3):
                if (r + c) % 2 == 0:
                    draw.rectangle([cx - 6 + c * 4, cy - 9 + r * 4,
                                    cx - 2 + c * 4, cy - 5 + r * 4], fill=color)
    elif kind == "ball":
        draw.ellipse([cx - s, cy - s, cx + s, cy + s], outline=color)
        draw.arc([cx - s, cy - 4, cx + s, cy + 4], 0, 180, fill=color)
        draw.line([cx, cy - s, cx, cy + s], fill=color)
    elif kind == "dome":
        draw.arc([cx - 8, cy - 7, cx + 8, cy + 5], 180, 360, fill=color)
        draw.line([cx - 9, cy + 5, cx + 9, cy + 5], fill=color)
        draw.line([cx - 9, cy + 8, cx + 9, cy + 8], fill=color)
        draw.line([cx, cy - 9, cx, cy - 6], fill=color)
    elif kind == "plane":
        draw.polygon([(cx - 9, cy + 3), (cx + 9, cy - 3), (cx + 3, cy + 1),
                      (cx + 5, cy + 7), (cx + 1, cy + 4), (cx - 5, cy + 6)],
                     outline=color)
    elif kind == "coin":
        draw.ellipse([cx - s, cy - s, cx + s, cy + s], outline=color)
        f = font(SERIF_B, 12)
        tw = draw.textlength("B", font=f)
        draw.text((cx - tw / 2, cy - 7), "B", font=f, fill=color)
    elif kind == "ship":
        draw.polygon([(cx - 9, cy + 2), (cx + 9, cy + 2), (cx + 5, cy + 8),
                      (cx - 5, cy + 8)], outline=color)
        draw.line([cx, cy + 2, cx, cy - 8], fill=color)
        draw.polygon([(cx, cy - 8), (cx + 6, cy + 1), (cx, cy + 1)],
                     outline=color)
    elif kind == "drone":
        draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=color)
        for dx, dy in ((-7, -6), (7, -6), (-7, 6), (7, 6)):
            draw.line([cx, cy, cx + dx, cy + dy], fill=color)
            draw.ellipse([cx + dx - 2, cy + dy - 1, cx + dx + 2, cy + dy + 1],
                         outline=color)


CARD_ICONS = ["building", "radar", "flame", "drone", "ballot", "bat",
              "flag", "ball", "dome", "plane", "coin", "ship"]


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # --- outer gold frame ---
    draw.rectangle([8, 8, W - 9, H - 9], outline=GOLD_DIM, width=1)
    draw.rectangle([12, 12, W - 13, H - 13], outline=(48, 40, 22), width=1)
    corner_ornament(draw, 16, 16, 1, 1)
    corner_ornament(draw, W - 16, 16, -1, 1)
    corner_ornament(draw, 16, H - 16, 1, -1)
    corner_ornament(draw, W - 16, H - 16, -1, -1)

    # --- masthead ---
    f_mast = font(SERIF_B, 22)
    mast = "T H E   W O R L D   I N   O N E   D A Y"
    tw = draw.textlength(mast, font=f_mast)
    draw.text(((W - tw) / 2, 18), mast, font=f_mast, fill=GOLD)
    f_strip = font(COND_B, 11)
    strip = "39 STORIES · 7 REGIONS · EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    tw = draw.textlength(strip, font=f_strip)
    draw.text(((W - tw) / 2, 46), strip, font=f_strip, fill=MUTED)
    gold_rule(draw, 64)

    # --- key art band ---
    art = Image.open(KEYART).convert("RGB")
    art = cover_crop(art, W - 24, 188)
    img.paste(art, (12, 72))
    fade_bottom(img, 208, 268)
    draw = ImageDraw.Draw(img)

    # --- date headline over the fade ---
    f_date = font(SERIF_B, 52)
    date = "SUNDAY 22 NOVEMBER 2026"
    tw = draw.textlength(date, font=f_date)
    dx = (W - tw) / 2
    draw.text((dx + 2, 222), date, font=f_date, fill=(0, 0, 0))
    draw.text((dx, 220), date, font=f_date, fill=CREAM)
    f_dek = font(SERIF_I, 15.5)
    tw = draw.textlength(data.DEK, font=f_dek)
    draw.text(((W - tw) / 2, 278), data.DEK, font=f_dek, fill=MUTED)

    # --- lead 1 caption bar (COP31 scene above) ---
    y = 302
    panel(draw, MARGIN, y, CW, 58, accent=GOLD)
    story_block(draw, data.LEADS[0], MARGIN, y, CW, 18, 11, 2, num_size=17)
    y += 64

    # --- leads 2 and 3 with generated scene thumbnails ---
    pw = (CW - 14) // 2
    thumbs = [DRONES, CORVETTE]
    for i, st in enumerate(data.LEADS[1:]):
        x = MARGIN + i * (pw + 14)
        panel(draw, x, y, pw, 98, accent=REGION_COLORS[st[1]])
        th = cover_crop(Image.open(thumbs[i]).convert("RGB"), 148, 92)
        if i == 0:
            # drones scene is much darker than the corvette scene; lift it
            # so the two lead panels balance
            th = ImageEnhance.Brightness(th).enhance(1.18)
            th = ImageEnhance.Contrast(th).enhance(1.05)
            th = ImageEnhance.Color(th).enhance(1.08)
        img.paste(th, (x + 4, y + 4))
        draw = ImageDraw.Draw(img)
        draw.rectangle([x + 4, y + 4, x + 151, y + 95],
                       outline=GOLD_DIM, width=1)
        story_block(draw, st, x, y, pw, 15.5, 11, 4, num_size=16,
                    text_x=x + 160)
    y += 104

    # --- timeline band: THE DAY IN UTC ---
    panel(draw, MARGIN, y, CW, 48, accent=GOLD)
    f_tl_h = font(COND_B, 11)
    draw.text((MARGIN + 10, y + 4), "THE DAY IN UTC", font=f_tl_h, fill=GOLD)
    f_tl_t = font(SERIF_B, 12.5)
    f_tl_l = font(COND_R, 9.5)
    cell = CW / len(data.TIMELINE)
    for i, (tm, lab) in enumerate(data.TIMELINE):
        cx = MARGIN + cell * i + cell / 2
        tw = draw.textlength(tm, font=f_tl_t)
        draw.text((cx - tw / 2, y + 18), tm, font=f_tl_t, fill=CREAM)
        lines = wrap(draw, lab, f_tl_l, cell - 8)[:2]
        for j, ln in enumerate(lines):
            tw = draw.textlength(ln, font=f_tl_l)
            draw.text((cx - tw / 2, y + 33 + j * 9), ln,
                      font=f_tl_l, fill=MUTED)
        if i:
            draw.line([MARGIN + cell * i, y + 16, MARGIN + cell * i, y + 44],
                      fill=(40, 50, 68), width=1)
    y += 52

    # --- stat strip with gold rings ---
    cell = CW / len(data.STATS)
    f_stat_n = font(SERIF_B, 21)
    f_stat_l = font(COND_R, 9)
    for i, (num, lab) in enumerate(data.STATS):
        cx = MARGIN + cell * i + cell / 2
        draw.ellipse([cx - 26, y, cx + 26, y + 30], outline=GOLD_DIM, width=1)
        tw = draw.textlength(num, font=f_stat_n)
        draw.text((cx - tw / 2, y + 3), num, font=f_stat_n, fill=GOLD)
        for j, ln in enumerate(wrap(draw, lab, f_stat_l, cell - 8)[:2]):
            tw = draw.textlength(ln, font=f_stat_l)
            draw.text((cx - tw / 2, y + 34 + j * 10), ln,
                      font=f_stat_l, fill=MUTED)
    y += 56
    gold_rule(draw, y)
    y += 8

    # --- 12 cards with spot pictograms ---
    f_sect = font(COND_B, 13)
    draw.text((MARGIN, y), "THE DAY IN FULL — 12 MORE STORIES",
              font=f_sect, fill=GOLD)
    y += 18
    cols, gap_x, gap_y = 3, 12, 2
    cw = (CW - gap_x * (cols - 1)) // cols
    ch = 57
    for idx, st in enumerate(data.CARDS):
        r, c = divmod(idx, cols)
        x = MARGIN + c * (cw + gap_x)
        yy = y + r * (ch + gap_y)
        panel(draw, x, yy, cw, ch, accent=REGION_COLORS[st[1]])
        story_block(draw, st, x, yy, cw, 12.5, 9.5, 2, num_size=13)
        icon_color = tuple(min(255, int(v * 1.3))
                           for v in REGION_COLORS[st[1]])
        spot_icon(draw, CARD_ICONS[idx % len(CARD_ICONS)],
                  x + cw - 16, yy + 13, icon_color)
    y = y + 4 * ch + 3 * gap_y + 5

    # --- also list ---
    draw.text((MARGIN, y), "ALSO ON SUNDAY — 24 MORE STORIES",
              font=f_sect, fill=GOLD)
    y += 16
    f_also = font(COND_R, 10.5)
    f_also_loc = font(COND_B, 10.5)
    per_col = 8
    col_w = (CW - 2 * 14) // 3
    for i, (num, loc, text, lon, lat) in enumerate(data.ALSO):
        c, r = divmod(i, per_col)
        x = MARGIN + c * (col_w + 14)
        yy = y + r * 11.5
        draw.text((x, yy), str(num), font=f_also_loc, fill=GOLD)
        line = "%s — %s" % (loc, text)
        draw.text((x + 22, yy),
                  truncate(draw, line, f_also, col_w - 22),
                  font=f_also, fill=CREAM)
    y = y + per_col * 11.5 + 3

    # --- DATE CHECK box ---
    box_h = H - y - 18
    panel(draw, MARGIN, y, CW, box_h, accent=GOLD)
    f_dc_h = font(COND_B, 11)
    draw.text((MARGIN + 10, y + 4), "DATE CHECK", font=f_dc_h, fill=GOLD)
    f_dc = font(COND_R, 10)
    lines = wrap(draw, data.DATE_CHECK, f_dc, CW - 20)
    ly = y + 16
    for ln in lines[:3]:
        draw.text((MARGIN + 10, ly), ln, font=f_dc, fill=MUTED)
        ly += 10

    # --- film grain + vignette (deterministic) ---
    rng = random.Random(20261122)
    grain = Image.new("L", (W, H), 0)
    gp = grain.load()
    for _ in range(26000):
        gp[rng.randrange(W), rng.randrange(H)] = rng.randrange(6, 26)
    grain = grain.filter(ImageFilter.GaussianBlur(0.6))
    img = Image.composite(
        Image.new("RGB", (W, H), (255, 246, 230)), img,
        grain.point(lambda v: v // 3))
    vig = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse([-W * 0.25, -H * 0.25, W * 1.25, H * 1.25], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(120))
    img = Image.composite(img, Image.new("RGB", (W, H), (2, 3, 6)),
                          vig.point(lambda v: 255 - (255 - v) // 3))

    img.save(OUT, "PNG", optimize=True)
    size = os.path.getsize(OUT)
    if size > 1024 * 1024:
        img.save(OUT, "JPEG", quality=88)
        size = os.path.getsize(OUT)
        print("saved as JPEG bytes (PNG was over 1MiB)")
    print("wrote %s (%d bytes)" % (OUT, size))


if __name__ == "__main__":
    main()
