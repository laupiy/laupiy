"""Small toolkit: pixel grids -> compact SVG paths, plus SVG docs with embedded pixel fonts."""
import base64, io, math, os, random
import numpy as np
from fontTools import subset
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_FILES = {
    'ps2p': ('Press Start 2P', 400, 'fonts/press-start-2p-latin-400-normal.woff'),
    'pix4': ('Pixelify Sans', 400, 'fonts/pixelify-sans-latin-400-normal.woff'),
    'pix7': ('Pixelify Sans', 700, 'fonts/pixelify-sans-latin-700-normal.woff'),
}
_fcache = {}


def _font(key):
    if key not in _fcache:
        _fcache[key] = TTFont(os.path.join(HERE, FONT_FILES[key][2]))
    return _fcache[key]


def text_width(key, s, size, spacing=0):
    f = _font(key)
    cmap, hmtx, upm = f.getBestCmap(), f['hmtx'], f['head'].unitsPerEm
    w = 0
    for ch in s:
        g = cmap.get(ord(ch))
        w += (hmtx[g][0] if g else upm * 0.6) / upm * size + spacing
    return w - spacing if s else 0


def subset_b64(key, chars):
    f = TTFont(os.path.join(HERE, FONT_FILES[key][2]))
    opt = subset.Options()
    opt.flavor = 'woff'
    opt.layout_features = []
    opt.name_IDs = [1, 2]
    opt.notdef_outline = True
    opt.hinting = False
    sub = subset.Subsetter(opt)
    sub.populate(text=''.join(sorted(set(chars))) + ' ')
    sub.subset(f)
    buf = io.BytesIO()
    f.flavor = 'woff'
    f.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


# ---------------------------------------------------------------- pixel grid
class Grid:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = np.full((h, w), -1, dtype=int)
        self.pal = []

    def c(self, hexc):
        if hexc not in self.pal:
            self.pal.append(hexc)
        return self.pal.index(hexc)

    def set(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x] = self.c(col)

    def rect(self, x, y, w, h, col):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, col)

    def fill_mask(self, m, col):
        self.a[m] = self.c(col)

    def blit(self, other, ox=0, oy=0):
        for y in range(other.h):
            for x in range(other.w):
                v = other.a[y, x]
                if v >= 0:
                    self.set(x + ox, y + oy, other.pal[v])

    def rects(self, ci):
        H, W = self.a.shape
        active, out = {}, []
        for y in range(H + 1):
            runs = []
            if y < H:
                row = self.a[y] == ci
                x = 0
                while x < W:
                    if row[x]:
                        x0 = x
                        while x < W and row[x]:
                            x += 1
                        runs.append((x0, x))
                    else:
                        x += 1
            cur = set(runs)
            for key in list(active):
                if key not in cur:
                    out.append((key[0], active.pop(key), key[1] - key[0]))
                    out[-1] = (out[-1][0], out[-1][1], out[-1][2], y - out[-1][1])
            for r in runs:
                if r not in active:
                    active[r] = y
        return out

    def svg(self):
        parts = []
        for ci, col in enumerate(self.pal):
            rs = self.rects(ci)
            if not rs:
                continue
            d = ''.join(f'M{x} {y}h{w}v{h}h-{w}z' for x, y, w, h in rs)
            parts.append(f'<path fill="{col}" d="{d}"/>')
        return ''.join(parts)


def ellipse_mask(w, h, cx, cy, rx, ry, shear=0.0):
    ys, xs = np.mgrid[0:h, 0:w]
    xs = xs + 0.5
    ys = ys + 0.5
    xc = cx - shear * (cy - ys)
    return ((xs - xc) / rx) ** 2 + ((ys - cy) / ry) ** 2 <= 1.0


def circle_mask(w, h, cx, cy, r):
    return ellipse_mask(w, h, cx, cy, r, r)


def shift(m, dx=0, dy=0):
    out = np.zeros_like(m)
    H, W = m.shape
    ys, xs = np.mgrid[0:H, 0:W]
    sy, sx = ys - dy, xs - dx
    ok = (sy >= 0) & (sy < H) & (sx >= 0) & (sx < W)
    out[ok] = m[sy[ok], sx[ok]]
    return out


def edge(m):
    """pixels of m that touch the outside (4-neighbourhood)."""
    inner = shift(m, 1, 0) & shift(m, -1, 0) & shift(m, 0, 1) & shift(m, 0, -1)
    return m & ~inner


def outline_fill(g, m, fill, line):
    e = edge(m)
    g.fill_mask(m & ~e, fill)
    g.fill_mask(e, line)


# ------------------------------------------------------------------- sprites
HEART = ['.X.X.', 'XXXXX', 'XXXXX', '.XXX.', '..X..']
FLOWER5 = ['..P..', '.PPP.', 'PPYPP', '.PPP.', '..P..']
SPARK5 = ['..S..', '..S..', 'SSSSS', '..S..', '..S..']
STAR3 = ['.S.', 'SSS', '.S.']


def sprite(rows, pal):
    g = Grid(len(rows[0]), len(rows))
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in pal:
                g.set(x, y, pal[ch])
    return g


def make_bunny(blink=False):
    """returns (body Grid, eyes_open Grid, eyes_shut Grid, size) - 28x33 chibi bunny."""
    W, H = 28, 33
    body = np.zeros((H, W), bool) | ellipse_mask(W, H, 14, 21, 13.5, 9.6)
    earL = ellipse_mask(W, H, 8.6, 7.6, 3.6, 7.6, shear=0.14)
    earR = ellipse_mask(W, H, 19.4, 7.6, 3.6, 7.6, shear=-0.14)
    footL = ellipse_mask(W, H, 8.5, 30, 4.6, 2.3)
    footR = ellipse_mask(W, H, 19.5, 30, 4.6, 2.3)
    allm = body | earL | earR
    OUT, WH, SH = '#c7688f', '#ffffff', '#f6dbe6'
    g = Grid(W, H)
    outline_fill(g, allm, WH, OUT)
    # inner ears
    for cx, sh in ((8.9, 0.14), (19.1, -0.14)):
        ie = ellipse_mask(W, H, cx, 8.4, 1.7, 5.6, shear=sh)
        g.fill_mask(ie & ~edge(allm), '#ffb5cb')
    # body shading (bottom-right crescent)
    lit = ellipse_mask(W, H, 12.6, 19.4, 13.2, 9.4)
    g.fill_mask(body & ~lit & ~edge(allm), SH)
    # feet (drawn in front)
    fm = footL | footR
    g.fill_mask(fm, WH)
    g.fill_mask(edge(fm), OUT)
    # cheeks / mouth / belly heart / flower
    for x0 in (4, 21):
        g.rect(x0, 21, 3, 2, '#ffadc2')
    for x, y in ((12, 21), (13, 22), (14, 21), (15, 22), (16, 21)):
        g.set(x, y, '#4a3848')
    hs = sprite(HEART, {'X': '#ff8fa8'})
    g.blit(hs, 12, 24)
    fl = sprite(FLOWER5, {'P': '#ff8fb1', 'Y': '#ffe27a'})
    g.blit(fl, 19, 1)
    eo, es = Grid(W, H), Grid(W, H)
    for x0 in (8, 18):
        eo.rect(x0, 17, 2, 3, '#4a3848')
        eo.set(x0, 17, '#ffffff')
        es.rect(x0 - 1, 19, 4, 1, '#4a3848')
    return g, eo, es, (W, H)


# ---------------------------------------------------------------- scene bits
BAYER = [[0, 2], [3, 1]]


def sky_bands(g, y0, y1, colors):
    n = len(colors)
    for y in range(y0, y1):
        t = (y - y0) / max(1, (y1 - y0 - 1)) * (n - 1)
        i = min(int(t), n - 2)
        f = t - i
        f = min(1, max(0, (f - 0.4) / 0.3))
        for x in range(g.w):
            thr = (BAYER[y % 2][x % 2] + 0.5) / 4
            g.set(x, y, colors[i + 1] if f > thr else colors[i])


def cloud_mask(W, H, cx, cy, w, h, rng):
    m = np.zeros((H, W), bool)
    n = max(3, int(w / 7))
    for i in range(n):
        t = i / (n - 1)
        bell = math.sin(math.pi * t) ** 0.8
        r = h * (0.34 + 0.55 * bell) * rng.uniform(0.85, 1.1)
        x = cx - w / 2 + t * w
        y = cy + h * 0.5 - r * 0.9
        m |= circle_mask(W, H, x, y, r)
    # flat-ish, wavy bottom
    ys = np.mgrid[0:H, 0:W][0]
    m &= ys <= cy + h * 0.5
    return m


def paint_cloud(g, m, hi, mid, lo, depth=2):
    g.fill_mask(m, mid)
    top = m & ~shift(m, 0, depth)
    bot = m & ~shift(m, 0, -depth - 1)
    g.fill_mask(bot & m, lo)
    g.fill_mask(top & m, hi)


def make_sparkle(c1='#ffffff', c2='#ffe3f1'):
    g = Grid(5, 5)
    g.set(2, 2, c1)
    for d in (1, 2):
        col = c1 if d == 1 else c2
        for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d)):
            g.set(2 + dx, 2 + dy, col)
    return g


def blade_grass(g, y_base, rng, hmin, hmax, dark, mid, light=None, step=1):
    W = g.w
    for x in range(0, W, step):
        h = rng.randint(hmin, hmax)
        lean = rng.choice([-1, 0, 0, 1])
        for k in range(h):
            xx = x + (lean if k >= h * 0.55 else 0)
            col = mid if k < 3 else dark
            if light and k == h - 1 and rng.random() < 0.4:
                col = light
            g.set(xx, y_base - k, col)
            if k < h * 0.5:
                g.set(xx + 1, y_base - k, col)
    for yy in range(y_base + 1, g.h):
        for x in range(W):
            g.set(x, yy, dark)


def wheat(g, x0, yb, H, lean, col, ear=None):
    """tall wheat stalk with feather leaves (like the reference grass)."""
    ear = ear or col
    pts = []
    for k in range(H):
        sx = x0 + round(lean * (k / H) ** 2)
        g.set(sx, yb - k, col)
        pts.append((sx, yb - k))
    for k in range(int(H * 0.4), H - 2, 3):
        sx, sy = pts[k]
        for dx, dy in ((1, 0), (2, -1), (2, -2)) if k < H * 0.75 else ((1, 0), (2, -1)):
            g.set(sx - dx, sy + dy, ear)
            g.set(sx + dx, sy + dy, ear)
    sx, sy = pts[-1]
    g.set(sx, sy - 1, ear)
    g.set(sx, sy - 2, ear)


# ------------------------------------------------------------------ svg docs
class Doc:
    def __init__(self, w, h, vb=None, title=''):
        self.w, self.h = w, h
        self.vb = vb or (0, 0, w, h)
        self.body = []
        self.chars = {'ps2p': set(), 'pix4': set(), 'pix7': set()}
        self.css = []
        self.title = title

    def add(self, s):
        self.body.append(s)

    def text(self, x, y, s, font='pix7', size=16, fill='#000', anchor='start', extra='', spacing=0):
        self.chars[font].update(s)
        fam, wt, _ = FONT_FILES[font]
        fb = "monospace" if font == 'ps2p' else "'Courier New',monospace"
        s = s.replace('&', '&amp;').replace('<', '&lt;')
        ls = f' letter-spacing="{spacing}"' if spacing else ''
        self.add(f'<text x="{x}" y="{y}" font-family="\'{fam}\',{fb}" font-weight="{wt}" '
                 f'font-size="{size}" fill="{fill}" text-anchor="{anchor}"{ls} {extra}>{s}</text>')

    def tspans(self, x, y, parts, size=18, fill='#000'):
        """parts: list of (text, font, fill)."""
        out = ''
        for s, font, col in parts:
            self.chars[font].update(s)
            fam, wt, _ = FONT_FILES[font]
            out += f'<tspan font-family="\'{fam}\',monospace" font-weight="{wt}" fill="{col}">{s.replace("&", "&amp;")}</tspan>'
        self.add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" xml:space="preserve">{out}</text>')

    def save(self, path, reduce_motion=True):
        faces = ''
        for key, chars in self.chars.items():
            if not chars:
                continue
            fam, wt, _ = FONT_FILES[key]
            faces += (f"@font-face{{font-family:'{fam}';font-weight:{wt};font-style:normal;"
                      f"src:url(data:font/woff;base64,{subset_b64(key, chars)}) format('woff');}}")
        css = faces + ''.join(self.css)
        if reduce_motion:
            css += '@media (prefers-reduced-motion:reduce){*{animation:none!important}}'
        x, y, w, h = self.vb
        t = f'<title>{self.title}</title>' if self.title else ''
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
               f'viewBox="{x} {y} {w} {h}" shape-rendering="crispEdges" role="img">{t}'
               f'<style>{css}</style>{"".join(self.body)}</svg>')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(svg)
        return len(svg)


def px_frame(x, y, w, h, u, fill, line, shadow=None, sh=None):
    """notched pixel-art box: border `u` thick, corners cut by `u`, optional drop shadow."""
    def notched(x, y, w, h, col):
        return (f'<rect x="{x + u}" y="{y}" width="{w - 2 * u}" height="{h}" fill="{col}"/>'
                f'<rect x="{x}" y="{y + u}" width="{w}" height="{h - 2 * u}" fill="{col}"/>')
    s = ''
    if shadow:
        d = sh if sh is not None else u
        s += notched(x + d, y + d, w, h, shadow)
    s += notched(x, y, w, h, line)
    s += notched(x + u, y + u, w - 2 * u, h - 2 * u, fill)
    return s


def grid_svg(g, scale=1, tx=0, ty=0, cls='', style=''):
    c = f' class="{cls}"' if cls else ''
    st = f' style="{style}"' if style else ''
    return f'<g transform="translate({tx} {ty}) scale({scale})"><g{c}{st}>{g.svg()}</g></g>'
