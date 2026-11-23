import random, math
import numpy as np
from pixlib import *

ROSE, PLUM, PLUM2 = '#e0678d', '#8b3d7c', '#5b2a5e'


# ============================================================= section titles
def make_title(name, text):
    size = 16
    tw = text_width('ps2p', text, size)
    w = int(tw + 2 * 58 + 4)
    d = Doc(w, 64, title=text)
    fw = w - 4
    d.add(px_frame(0, 0, fw, 60, 4, '#fff0f6', ROSE, '#f3b8cc', 4))
    heart = sprite(HEART, {'X': '#ff7fa6'})
    d.add(f'<g transform="translate(16 22) scale(3)">{heart.svg()}</g>')
    d.add(f'<g transform="translate({fw - 16 - 15} 22) scale(3)">{heart.svg()}</g>')
    d.text(fw / 2 + 2, 37 + 2, text, 'ps2p', size, '#f3b8cc', anchor='middle')
    d.text(fw / 2, 37, text, 'ps2p', size, '#b93b74', anchor='middle')
    d.css.append('.tw{animation:tw 2.4s steps(1) infinite}@keyframes tw{0%{opacity:1}50%{opacity:.25}}')
    sp = make_sparkle('#ffffff', '#ffc2d8')
    d.add(f'<g transform="translate({fw - 5} -2) scale(2)"><g class="tw">{sp.svg()}</g></g>')
    d.save(f'assets/{name}.svg')


TITLES = {
    'title-about': 'a little bit about me',
    'title-build': 'things i like to build',
    'title-toolbox': 'my little toolbox',
    'title-projects': 'things i’ve been working on',
    'title-garden': 'my github garden',
    'title-snake': 'my contributions are growing!',
    'title-connect': 'let’s be friends',
}


# ================================================================= chips row
def make_chips():
    items = [('AI', '#ffd1e3', '#d9609a', 'heart', '#ff7fa6'),
             ('Internet of Things', '#cdeef2', '#3f8f9f', 'flower', '#6fc4d2'),
             ('Computer Vision', '#eef5b8', '#7f9322', 'spark', '#a8b83a'),
             ('Web Development', '#ffd1e3', '#d9609a', 'flower', '#ff8fb1'),
             ('Mobile Apps', '#e6dcff', '#7a5cc4', 'heart', '#9c7ee0')]
    size, gap = 18, 18
    widths = [text_width('pix7', t, size) + 32 + 28 for t, *_ in items]
    total = sum(widths) + gap * (len(items) - 1) + 4
    d = Doc(int(total), 54, title='AI, Internet of Things, Computer Vision, Web Development, Mobile Apps')
    x = 0
    for (t, bg, ln, ic, icc), w in zip(items, widths):
        d.add(px_frame(x, 2, w, 42, 3, bg, ln, '#5b2a5e22', 4))
        spr = {'heart': sprite(HEART, {'X': icc}), 'flower': sprite(FLOWER5, {'P': icc, 'Y': '#fff3a8'}),
               'spark': sprite(SPARK5, {'S': icc})}[ic]
        d.add(f'<g transform="translate({x + 14} 16) scale(3)">{spr.svg()}</g>')
        d.text(x + 14 + 15 + 10, 30, t, 'pix7', size, '#4a2c58')
        x += w + gap
    d.save('assets/chips.svg')


# =============================================================== about card
def mini_scene():
    W, H = 44, 41
    g = Grid(W, H)
    rng = random.Random(3)
    sky_bands(g, 0, 36, ['#8f66c0', '#b274c6', '#d884c4', '#f598b4', '#fba9b0'])
    for cx, cy, w, h, p in ((9, 7, 18, 6, ('#d6a9de', '#b985d0', '#9b6dbf')), (36, 12, 20, 7, ('#fdd3e6', '#f7a6ca', '#e784b0')),
                            (8, 22, 20, 7, ('#fdd3e6', '#f7a6ca', '#e784b0'))):
        paint_cloud(g, cloud_mask(W, H, cx, cy, w, h, rng), *p)
    ys, xs = np.mgrid[0:H, 0:W]
    dmn = np.sqrt((xs + .5 - 33) ** 2 + (ys + .5 - 7) ** 2)
    g.fill_mask((dmn > 2.4) & (dmn <= 3.8) & ((xs + ys) % 2 == 0), '#ffe0ef')
    g.fill_mask(dmn <= 2.4, '#fff7fb')
    # tiny mountain
    for x in range(W):
        dx = x - 30
        r = int(26 + abs(dx) * 0.7)
        for y in range(r, 36):
            g.set(x, y, '#f0687f' if dx <= 0 else '#c94f72')
    for _ in range(14):
        x, y = rng.randint(1, W - 2), rng.randint(1, 20)
        if abs(x - 33) > 5:
            g.set(x, y, '#ffe9f5')
    blade_grass(g, 36, rng, 2, 4, '#2c2d27', '#3d4a31', '#58693f')
    return g


def make_about():
    W, H = 860, 320
    d = Doc(W, H, title='Hi! You can call me Anoy. Informatics student who loves exploring tech.')
    d.css.append(
        '.tw{animation:tw 2.4s steps(1) infinite}@keyframes tw{0%{opacity:1}50%{opacity:.2}}'
        '.bob{animation:bob 1.6s steps(1) infinite}@keyframes bob{0%{transform:translateY(0)}50%{transform:translateY(-1px)}}'
        '.bo{animation:bo 4.8s steps(1) infinite}@keyframes bo{0%{opacity:1}92%{opacity:0}96%{opacity:1}}'
        '.bs{animation:bs 4.8s steps(1) infinite}@keyframes bs{0%{opacity:0}92%{opacity:1}96%{opacity:0}}')
    # window
    d.add(px_frame(4, 4, 848, 308, 4, '#fff8fb', ROSE, '#f3b8cc', 4))
    d.add('<rect x="8" y="8" width="840" height="36" fill="#ffc2d6"/><rect x="8" y="44" width="840" height="4" fill="#e0678d"/>')
    d.text(24, 33, 'about_me.txt', 'ps2p', 16, PLUM)
    for i, col in enumerate(('#fff3a8', '#cdeef2', '#ffffff')):
        d.add(px_frame(764 + i * 26, 16, 20, 20, 2, col, PLUM))
    # checker dots on the content area
    dots = ''.join(f'<rect x="{x}" y="{y}" width="4" height="4" fill="#ffe9f1"/>'
                   for y in range(64, 290, 28) for x in range(268 if y > 0 else 0, 840, 28) if (x // 28 + y // 28) % 2 == 0 and x > 600)
    d.add(dots)
    # avatar
    d.add(px_frame(32, 64, 184, 172, 4, '#ffffff', ROSE, '#f3b8cc', 4))
    sc = mini_scene()
    d.add(f'<g transform="translate(36 68) scale(4)">{sc.svg()}</g>')
    bunny, eo, es, _ = make_bunny()
    d.add(f'<g transform="translate({36 + 8 * 4} {68 + 5 * 4}) scale(4)"><g class="bob">{bunny.svg()}<g class="bo">{eo.svg()}</g><g class="bs">{es.svg()}</g></g></g>')
    sp = make_sparkle('#ffffff', '#ffd6e8')
    d.add(f'<g transform="translate(46 78) scale(3)"><g class="tw">{sp.svg()}</g></g>')
    # badge
    bt = 'hi, i’m anoy!'
    bw = text_width('pix7', bt, 18) + 40
    d.add(px_frame(124 - bw / 2, 250, bw, 38, 4, '#ff8fb1', PLUM, '#f3b8cc', 4))
    d.text(124, 276, bt, 'pix7', 18, '#ffffff', anchor='middle')
    # bullets
    HI, FL = '#e0527f', '#e0527f'
    lines = [
        ('heart', '#ff7fa6', [('Hi! You can call me ', 'pix4', '#5b4468'), ('Anoy', 'pix7', HI)]),
        ('flower', '#6fc4d2', [('Informatics student who loves ', 'pix4', '#5b4468'), ('exploring tech', 'pix7', HI)]),
        ('heart', '#9c7ee0', [('Interested in ', 'pix4', '#5b4468'), ('AI · IoT · Computer Vision', 'pix7', HI)]),
        (None, None, [('& ', 'pix4', '#5b4468'), ('Software Development', 'pix7', HI)]),
        ('flower', '#a8b83a', [('I love turning ideas into ', 'pix4', '#5b4468'), ('small projects', 'pix7', HI)]),
        ('heart', '#ff7fa6', [('Currently growing & collecting ', 'pix4', '#5b4468'), ('tiny wins', 'pix7', HI)]),
    ]
    y = 100
    for ic, col, parts in lines:
        if ic:
            spr = sprite(HEART, {'X': col}) if ic == 'heart' else sprite(FLOWER5, {'P': col, 'Y': '#fff3a8'})
            d.add(f'<g transform="translate(250 {y - 15}) scale(3)">{spr.svg()}</g>')
        d.tspans(280 if ic else 280, y, parts, size=21)
        y += 38
    d.save('assets/about.svg')


# ================================================================== projects
def icon_drop():
    g = Grid(12, 13)
    rows = ['.....OO.....', '....OBBO....', '....OBBO....', '...OBBBBO...', '...OBBBBO...', '..OBBBBBBO..', '..OBWBBBBO..',
            '.OBBWBBBBBO.', '.OBBBBBBBBO.', '.OBBBBBBBBO.', '..OBBBBBBO..', '..OOBBBBOO..', '....OOOO....']
    return sprite(rows, {'O': '#2f7f90', 'B': '#6fc4d2', 'W': '#ffffff'})


def icon_flower():
    W = H = 15
    g = Grid(W, H)
    m = circle_mask(W, H, 7.5, 7.5, 2.4)
    for k in range(5):
        a = -math.pi / 2 + k * 2 * math.pi / 5
        m |= circle_mask(W, H, 7.5 + 3.9 * math.cos(a), 7.5 + 3.9 * math.sin(a), 2.7)
    outline_fill(g, m, '#ff8fb1', '#c7457a')
    g.fill_mask(circle_mask(W, H, 7.5, 7.5, 1.9), '#ffe27a')
    return g


def icon_gift():
    W, H = 14, 14
    g = Grid(W, H)
    ys, xs = np.mgrid[0:H, 0:W]
    box = (xs >= 1) & (xs <= 12) & (ys >= 6) & (ys <= 13)
    lid = (xs >= 0) & (xs <= 13) & (ys >= 4) & (ys <= 6)
    bow = ((xs >= 3) & (xs <= 6) & (ys >= 1) & (ys <= 3)) | ((xs >= 7) & (xs <= 10) & (ys >= 1) & (ys <= 3))
    m = box | lid | bow
    outline_fill(g, m, '#b5c83f', '#6b7a1a')
    e = edge(m)
    g.fill_mask(lid & ~e, '#d7e66a')
    g.fill_mask((xs >= 6) & (xs <= 7) & (ys >= 4) & ~e & (ys <= 12), '#fff0a0')
    g.fill_mask(bow & ~e & (xs != 6) & (xs != 7), '#fff0a0')
    return g


def icon_eye():
    W, H = 16, 11
    g = Grid(W, H)
    ys, xs = np.mgrid[0:H, 0:W]
    hh = 4.2 * np.sqrt(np.clip(1 - ((xs + .5 - 8) / 7.8) ** 2, 0, 1))
    m = np.abs(ys + .5 - 5.5) <= hh
    outline_fill(g, m, '#ffffff', '#6a4cb4')
    g.fill_mask(circle_mask(W, H, 8, 5.5, 3.1) & ~edge(m), '#8d6fe0')
    g.fill_mask(circle_mask(W, H, 8, 5.5, 1.6) & ~edge(m), '#2d1f5a')
    g.set(7, 4, '#ffffff')
    return g


def make_projects():
    W, H = 864, 330
    d = Doc(W, H, title='AquaVoice, Antara Aroma, SmartBorrow, Vision-to-Audio Bridge')
    d.css.append('.tw{animation:tw 2.4s steps(1) infinite}@keyframes tw{0%{opacity:1}50%{opacity:.2}}'
                 '.fl{animation:fl 2s steps(1) infinite}@keyframes fl{0%{transform:translateY(0)}50%{transform:translateY(-3px)}}')
    cards = [
        (0, 0, 'AquaVoice', ['Water quality monitoring & smart', 'mitigation concept'], '#e0f5f8', '#4fa9ba', '#3b8fa0', icon_drop()),
        (450, 0, 'Antara Aroma', ['A web project with a dynamic admin', 'experience'], '#ffe8ef', '#e0678d', '#d9457a', icon_flower()),
        (0, 180, 'SmartBorrow', ['A transparent public-asset borrowing', 'platform'], '#f6f9d6', '#a2b52f', '#7f9322', icon_gift()),
        (450, 180, 'Vision-to-Audio Bridge', ['Exploring computer vision with audio', 'feedback'], '#eee8ff', '#8366c8', '#7a5cc4', icon_eye()),
    ]
    for i, (x, y, title, desc, bg, ln, tc, icon) in enumerate(cards):
        d.add(px_frame(x, y, 410, 146, 4, bg, ln, ln + '55', 4))
        # icon panel
        d.add(px_frame(x + 18, y + 30, 88, 88, 3, '#ffffff', ln))
        sc = min(5, 76 // max(icon.w, icon.h))
        ix = x + 18 + (88 - icon.w * sc) / 2
        iy = y + 30 + (88 - icon.h * sc) / 2
        d.add(f'<g transform="translate({ix} {iy}) scale({sc})"><g class="fl" style="animation-delay:-{i * 0.5}s">{icon.svg()}</g></g>')
        size = 24
        avail = 410 - 124 - 14
        while text_width('pix7', title, size) > avail:
            size -= 1
        d.text(x + 124, y + 56, title, 'pix7', size, tc)
        words, lines_, cur = ' '.join(desc).split(), [], ''
        for wd in words:
            t = (cur + ' ' + wd).strip()
            if text_width('pix4', t, 17) <= avail:
                cur = t
            else:
                lines_.append(cur); cur = wd
        lines_.append(cur)
        for li, ln_ in enumerate(lines_):
            d.text(x + 124, y + 86 + li * 24, ln_, 'pix4', 17, '#5b4468')
        d.add(px_frame(x + 334, y + 14, 58, 26, 3, '#ffffff', ln))
        d.text(x + 363, y + 33, 'wip', 'pix7', 15, tc, anchor='middle')
        sp = make_sparkle('#ffffff', ln)
        d.add(f'<g transform="translate({x + 380} {y + 122}) scale(2)"><g class="tw" style="animation-delay:-{i * 0.4}s">{sp.svg()}</g></g>')
    d.save('assets/projects.svg')


# ==================================================================== footer
def make_footer():
    W, H, S = 200, 38, 5
    g = Grid(W, H)
    rng = random.Random(11)
    sky_bands(g, 0, 26, ['#a7dde8', '#c3ebee', '#dff4ee', '#f4f8e2'])
    cream = ('#ffffff', '#fff5da', '#ecdcb4')
    for cx, cy, w, h in ((100, 12, 56, 12), (60, 8, 30, 7), (146, 7, 34, 8)):
        paint_cloud(g, cloud_mask(W, H, cx, cy, w, h, rng), *cream)
    # distant pines + round trees (misty blue)
    for cx, top, tiers, col in ((74, 13, 3, '#8fb6d0'), (83, 9, 4, '#86afcc'), (91, 14, 3, '#8fb6d0'), (112, 11, 4, '#86afcc'),
                                (121, 14, 3, '#8fb6d0'), (129, 12, 3, '#86afcc')):
        for t in range(tiers):
            t0 = top + t * 4
            for y in range(t0, t0 + 6):
                half = int((y - t0) * 0.62) + (1 if y > t0 else 0)
                for x in range(cx - half, cx + half + 1):
                    g.set(x, y, col)
        for y in range(top + tiers * 4 + 1, 27):
            g.set(cx, y, col)
    g.fill_mask(circle_mask(W, H, 106, 22, 8), '#9cc7a8')
    g.fill_mask(circle_mask(W, H, 62, 24, 7), '#a6cfb0')
    # meadow
    for y in range(26, H):
        t = (y - 26) / (H - 27)
        for x in range(W):
            thr = (BAYER[y % 2][x % 2] + .5) / 4
            cols = ['#cdee82', '#b0e46c', '#8ccf68', '#6fbc66']
            ft = t * 3
            i = min(int(ft), 2)
            f = min(1, max(0, (ft - i - .4) / .3))
            g.set(x, y, cols[i + 1] if f > thr else cols[i])
    for _ in range(120):
        x, y = rng.randint(0, W - 1), rng.randint(27, H - 1)
        g.set(x, y, rng.choice(['#ffffff', '#ffd6e6', '#ff9fc0', '#fff6a8']))
        if rng.random() < .4:
            g.set(x + 1, y, '#e9f9b0')
    for _ in range(60):
        x, y = rng.randint(0, W - 1), rng.randint(27, H - 1)
        g.set(x, y, '#5aa956')

    def tree(trunk_x, trunk_w, canopy, flip=False):
        for y in range(0, 33):
            for x in range(trunk_x, trunk_x + trunk_w):
                g.set(x, y, '#232b4d' if x < trunk_x + trunk_w - 1 else '#33406b')
        m = np.zeros((H, W), bool)
        for cx, cy, r in canopy:
            m |= circle_mask(W, H, cx, cy, r)
        paint_cloud(g, m, '#ffd3e6', '#f7a9cc', '#e07fb0', depth=2)
        # re-draw trunk over canopy base
        for y in range(12, 33):
            for x in range(trunk_x, trunk_x + trunk_w):
                g.set(x, y, '#232b4d' if x < trunk_x + trunk_w - 1 else '#33406b')
        for k in range(18):
            xx = rng.randint(max(0, int(min(c[0] for c in canopy))), min(W - 1, int(max(c[0] for c in canopy))))
            yy = rng.randint(0, 22)
            if m[yy, xx]:
                g.set(xx, yy, '#fff0f6')

    def flare():
        pass
    tree(18, 5, [(8, 9, 11), (22, 6, 10), (30, 15, 9), (12, 20, 8), (-2, 14, 9)])
    tree(178, 5, [(192, 9, 11), (178, 6, 10), (170, 15, 9), (188, 20, 8), (203, 14, 9)])
    # foreground bushes with flowers
    for x0, x1 in ((0, 22), (178, 200)):
        for x in range(x0, x1):
            h = rng.randint(2, 5)
            for k in range(h):
                g.set(x, H - 1 - k, '#1f5f5a' if k < h - 1 else '#2f7f6a')
        for _ in range(7):
            x, y = rng.randint(x0, x1 - 2), rng.randint(H - 7, H - 2)
            g.set(x, y, '#ff9fc0'); g.set(x + 1, y, '#ffd6e6'); g.set(x, y + 1, '#ffd6e6')

    d = Doc(1000, 190, title='stay curious, keep creating, and let your little ideas bloom.')
    d.css.append('.pt{animation:pt 7s steps(32) infinite}@keyframes pt{0%{transform:translate(0,-3px);opacity:1}92%{opacity:1}100%{transform:translate(-8px,34px);opacity:0}}'
                 '.tw{animation:tw 2.4s steps(1) infinite}@keyframes tw{0%{opacity:1}50%{opacity:.25}}')
    d.add(f'<g transform="scale({S})">{g.svg()}')
    for i, (x, dl) in enumerate(((30, 0), (46, -2), (64, -4.5), (140, -1), (156, -3.2), (170, -5.5), (96, -6))):
        petal = Grid(3, 2)
        petal.set(0, 0, '#ffb6d0'); petal.set(1, 0, '#ff8fb8'); petal.set(1, 1, '#ffb6d0'); petal.set(2, 1, '#ff8fb8')
        d.add(f'<g transform="translate({x} 0)"><g class="pt" style="animation-delay:{dl}s">{petal.svg()}</g></g>')
    sp = make_sparkle('#ffffff', '#fff6c8')
    for x, y, dl in ((52, 30, 0), (150, 28, 1), (98, 34, 2)):
        d.add(f'<g transform="translate({x} {y})"><g class="tw" style="animation-delay:-{dl}s">{sp.svg()}</g></g>')
    d.add('</g>')
    l1, l2 = '“stay curious, keep creating,', 'and let your little ideas bloom.”'
    for dx, dy, col in ((3, 3, '#ffffff'), (0, 0, '#c0467a')):
        d.text(500 + dx, 62 + dy, l1, 'pix7', 29, col, anchor='middle')
        d.text(500 + dx, 100 + dy, l2, 'pix7', 29, col, anchor='middle')
    d.save('assets/footer.svg')


# =============================================================== pixel garden
def make_garden():
    W, H, S = 80, 22, 6
    d = Doc(W * S, H * S, title='pixel flower garden')
    d.css.append('.sw{animation:sw 1.6s steps(1) infinite}@keyframes sw{0%{transform:translateX(0)}50%{transform:translateX(1px)}}'
                 '.fa{animation:fa .5s steps(1) infinite}@keyframes fa{0%{opacity:1}50%{opacity:0}}'
                 '.fb{animation:fb .5s steps(1) infinite}@keyframes fb{0%{opacity:0}50%{opacity:1}}'
                 '.bf{animation:bf 14s steps(70) infinite}@keyframes bf{0%{transform:translate(-8px,2px)}25%{transform:translate(18px,-2px)}50%{transform:translate(42px,3px)}75%{transform:translate(64px,-1px)}100%{transform:translate(90px,2px)}}')
    g = Grid(W, H)
    rng = random.Random(5)
    for x in range(W):
        h = rng.randint(2, 4)
        for k in range(h):
            g.set(x, H - 1 - k, '#7fc46a' if k < h - 1 else '#a6dc7e')
    for y in range(H - 2, H):
        for x in range(W):
            g.set(x, y, '#4f9c4f')
    d.add(f'<g transform="scale({S})">{g.svg()}')
    flowers = [(6, 10, '#ff8fb1'), (14, 13, '#ffe3ee'), (22, 8, '#c9a8ff'), (30, 12, '#ffd96a'), (38, 9, '#8fd6e0'),
               (46, 14, '#ff8fb1'), (54, 9, '#ffe3ee'), (62, 12, '#c9a8ff'), (70, 8, '#ffd96a'), (76, 13, '#8fd6e0')]
    for i, (x, h, col) in enumerate(flowers):
        top = H - 3 - h
        st = Grid(W, H)
        for y in range(top + 5, H - 3):
            st.set(x, y, '#3f8f4a')
        for ly, side in ((top + 9, -1), (top + 11, 1)):
            if ly < H - 4:
                st.set(x + side, ly, '#5ab45e'); st.set(x + 2 * side, ly - 1, '#5ab45e')
        d.add(st.svg())
        head = Grid(5, 5)
        petals = [(2, 0), (1, 1), (2, 1), (3, 1), (0, 2), (1, 2), (3, 2), (4, 2), (1, 3), (2, 3), (3, 3), (2, 4)]
        for px_, py_ in petals:
            head.set(px_, py_, col)
        head.set(2, 2, '#fff3a8')
        # soft outline shade
        if col in ('#ffffff',):
            for px_, py_ in ((2, 4), (1, 3), (3, 3)):
                head.set(px_, py_, '#ffe0ec')
        d.add(f'<g transform="translate({x - 2} {top})"><g class="sw" style="animation-delay:-{(i % 4) * 0.4}s">{head.svg()}</g></g>')
    # butterfly
    b1, b2 = Grid(7, 5), Grid(7, 5)
    for gg, wing_rows in ((b1, [(0, 0), (1, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2)]), (b2, [(1, 2), (2, 2), (1, 3), (2, 3), (2, 1)])):
        for x_, y_ in wing_rows:
            gg.set(x_, y_ + 1, '#ff8fb1'); gg.set(6 - x_, y_ + 1, '#ff8fb1')
        gg.set(3, 1, '#5b2a5e'); gg.set(3, 2, '#5b2a5e'); gg.set(3, 3, '#5b2a5e'); gg.set(3, 0, '#5b2a5e')
    d.add(f'<g transform="translate(0 4)"><g class="bf"><g class="fa">{b1.svg()}</g><g class="fb">{b2.svg()}</g></g></g>')
    d.add('</g>')
    d.save('assets/pixel-garden.svg')


if __name__ == '__main__':
    for n, t in TITLES.items():
        make_title(n, t)
    make_chips(); make_about(); make_projects(); make_footer(); make_garden()
    print('ok')
