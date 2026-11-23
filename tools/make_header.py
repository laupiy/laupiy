import random, math
import numpy as np
from pixlib import *

W, H, S = 200, 64, 5   # grid 200x64, 1 grid px = 5 svg px -> 1000x320


def build(out):
    rng = random.Random(7)
    base = Grid(W, H)

    # --- sky -----------------------------------------------------------
    sky_bands(base, 0, 58, ['#7d5bb5', '#9467bf', '#b274c6', '#cf80c5', '#e68cbd', '#f598b4', '#fba9b0'])

    # --- clouds: lilac high, pink middle, rose low -----------------------
    lilac = ('#d6a9de', '#b985d0', '#9b6dbf')
    pink = ('#fdd3e6', '#f7a6ca', '#e784b0')
    rose = ('#fbaac3', '#f08aa8', '#da6e93')
    cl = [  # cx, cy, w, h, palette
        (22, 7, 44, 10, lilac), (78, 5, 40, 9, lilac), (152, 9, 50, 11, lilac), (196, 4, 30, 8, lilac),
        (14, 24, 54, 13, pink), (92, 28, 56, 13, pink), (166, 27, 56, 13, pink), (130, 14, 36, 9, pink),
    ]
    for cx, cy, w, h, p in cl:
        m = cloud_mask(W, H, cx, cy, w, h, rng)
        paint_cloud(base, m, *p)

    # --- moon + halo -----------------------------------------------------
    mx, my = 118, 14
    ys, xs = np.mgrid[0:H, 0:W]
    d = np.sqrt((xs + .5 - mx) ** 2 + (ys + .5 - my) ** 2)
    halo = (d > 3.6) & (d <= 5.6) & (((xs + ys) % 2) == 0)
    base.fill_mask(halo, '#ffe0ef')
    base.fill_mask(d <= 3.6, '#fff7fb')
    base.fill_mask((d <= 3.6) & (xs > mx + 0.5) & (ys > my), '#ffe3f0')

    # --- distant mountains -------------------------------------------------
    def mountain(cx, peak, slope, base_y, light, shade, snow, jag=1.0):
        for x in range(W):
            dx = x - cx
            if abs(dx) > (base_y - peak) / slope + 2:
                continue
            ridge = peak + abs(dx) * slope + round(math.sin(x * 0.9) * jag + math.sin(x * 0.37) * jag)
            ridge = int(max(peak, ridge))
            for y in range(ridge, base_y + 1):
                col = light if dx <= 0 else shade
                if y - ridge < 2 and dx <= 0:
                    col = snow
                elif dx <= 0 and (y - ridge) % 5 == 3 and (x + y) % 3 == 0:
                    col = snow
                elif dx > 0 and (y - ridge) % 5 == 2 and (x + y) % 3 == 0:
                    col = light
                base.set(x, y, col)

    mountain(176, 42, 0.6, 58, '#c97bb8', '#b062a4', '#e3a2cc', 0.6)
    mountain(100, 41, 0.62, 58, '#c97bb8', '#b062a4', '#e3a2cc', 0.7)
    mountain(138, 29, 0.6, 58, '#f0687f', '#c94f72', '#ffb4c0', 1.0)

    # low rose haze clouds in front of the mountain feet
    for cx, cy, w, h in ((30, 52, 60, 7), (86, 54, 30, 6), (196, 52, 46, 7)):
        m = cloud_mask(W, H, cx, cy, w, h, rng)
        paint_cloud(base, m, *rose, depth=2)

    # --- tiny static stars --------------------------------------------------
    for _ in range(46):
        x, y = rng.randint(1, W - 2), rng.randint(1, 40)
        if base.pal[base.a[y, x]] in ('#7d5bb5', '#9467bf', '#b274c6', '#cf80c5', '#e68cbd') and abs(x - mx) > 7:
            base.set(x, y, '#ffe9f5')

    # --- grass ground (back layer, static) -----------------------------------
    ground = Grid(W, H)
    blade_grass(ground, 56, rng, 2, 4, '#2c2d27', '#3d4a31', '#58693f')
    blade_grass(ground, 59, rng, 2, 4, '#1f211c', '#2c2d27')

    # --- animated pieces --------------------------------------------------------
    sparks = [(30, 12, 0), (62, 20, 1), (96, 8, 2), (144, 22, 0), (182, 14, 3), (10, 36, 2), (74, 36, 1),
              (160, 38, 3), (128, 40, 0), (190, 30, 1), (44, 30, 2), (104, 30, 3)]
    spark_svg = ''
    sp = make_sparkle()
    for i, (x, y, k) in enumerate(sparks):
        spark_svg += (f'<g transform="translate({x - 2} {y - 2})"><g class="tw" style="animation-delay:-{k * 0.5 + (i % 3) * 0.3:.1f}s">'
                      f'{sp.svg()}</g></g>')

    # wheat frames A/B (swaying), right side + far left edge only
    wheat_pos = [(3, 30, -3), (8, 24, 2), (114, 24, 3), (123, 19, -3), (133, 28, 3), (143, 21, -2),
                 (190, 27, 2), (196, 21, -2)]
    fa, fb = Grid(W, H), Grid(W, H)
    for x, h, l in wheat_pos:
        wheat(fa, x, 58, h, l, '#262822')
        wheat(fb, x, 58, h, l + (1 if l >= 0 else -1), '#262822')
    front = Grid(W, H)
    blade_grass(front, 62, rng, 1, 4, '#1b1d18', '#262822')

    bunny, eo, es, (bw, bh) = make_bunny()

    d = Doc(1000, 320, title="anoy's corner - too cute to compute")
    d.css.append(
        '.tw{animation:tw 2.4s steps(1) infinite}@keyframes tw{0%{opacity:1}35%{opacity:.15}55%{opacity:1}80%{opacity:.5}}'
        '.sa{animation:sa 1.8s steps(1) infinite}@keyframes sa{0%{opacity:1}50%{opacity:0}}'
        '.sb{animation:sb 1.8s steps(1) infinite}@keyframes sb{0%{opacity:0}50%{opacity:1}}'
        '.bob{animation:bob 1.6s steps(1) infinite}@keyframes bob{0%{transform:translateY(0)}50%{transform:translateY(-1px)}}'
        '.bo{animation:bo 4.8s steps(1) infinite}@keyframes bo{0%{opacity:1}92%{opacity:0}96%{opacity:1}}'
        '.bs{animation:bs 4.8s steps(1) infinite}@keyframes bs{0%{opacity:0}92%{opacity:1}96%{opacity:0}}'
        '.hr{animation:hr 3.6s steps(16) infinite}@keyframes hr{0%{transform:translateY(0);opacity:1}92%{transform:translateY(-16px);opacity:1}100%{transform:translateY(-16px);opacity:0}}'
        '.dr{animation:dr 70s steps(240) infinite}@keyframes dr{from{transform:translateX(-40px)}to{transform:translateX(200px)}}'
    )
    d.add('<g transform="scale(5)">')
    d.add(base.svg())
    # slow drifting little clouds (pixel-stepped)
    for cy, w, h, delay, p in ((12, 22, 6, 0, pink), (20, 16, 5, -34, lilac)):
        g = Grid(60, 16)
        m = cloud_mask(60, 16, 30, 8, w, h, random.Random(cy))
        paint_cloud(g, m, *p)
        d.add(f'<g transform="translate(0 {cy - 8})"><g class="dr" style="animation-delay:{delay}s">{g.svg()}</g></g>')
    d.add(ground.svg())
    d.add(spark_svg)
    d.add('</g>')

    # bunny on the grass
    bx, by = 770, 128
    d.add(f'<g transform="translate({bx} {by}) scale(5)"><g class="bob">{bunny.svg()}'
          f'<g class="bo">{eo.svg()}</g><g class="bs">{es.svg()}</g></g></g>')
    # rising hearts
    hs = sprite(HEART, {'X': '#ff8fa8'})
    for i, (x, y, dl) in enumerate(((742, 150, 0), (925, 175, -1.4), (950, 120, -2.6))):
        small = Grid(3, 3)
        for xx, yy in ((0, 0), (2, 0), (0, 1), (1, 1), (2, 1), (1, 2)):
            small.set(xx, yy, '#ffffff')
        d.add(f'<g transform="translate({x} {y}) scale(4)"><g class="hr" style="animation-delay:{dl}s">{small.svg()}</g></g>')

    d.add('<g transform="scale(5)">')
    d.add(f'<g class="sa">{fa.svg()}</g><g class="sb">{fb.svg()}</g>')
    d.add(front.svg())
    d.add('</g>')

    # --- overlay: pill, title, tags ---------------------------------------------
    pw = text_width('pix7', 'hello, welcome to', 18) + 62
    d.add(px_frame(60, 40, pw, 36, 4, '#fff6fa', '#d9609a', '#7a3a78', 4))
    hh = sprite(HEART, {'X': '#e7508a'})
    d.add(f'<g transform="translate(76 52) scale(2.4)">{hh.svg()}</g>')
    d.text(96, 65, 'hello, welcome to', 'pix7', 18, '#8b3d7c')

    title = 'anoy’s corner'
    tx, ty = 64, 150
    for dx, dy in ((-5, 0), (5, 0), (0, -5), (0, 5), (5, 5), (-5, 5), (5, -5), (-5, -5), (0, 10), (5, 10)):
        d.text(tx + dx, ty + dy, title, 'ps2p', 40, '#6a2a6c')
    d.text(tx, ty, title, 'ps2p', 40, '#ffe3ef')

    d.text(68, 192, 'INTP', 'pix7', 26, '#5b2a5e', spacing=3)
    d.text(66, 190, 'INTP', 'pix7', 26, '#ffffff', spacing=3)
    d.add(f'<g transform="translate(160 172) scale(3.4)">{make_sparkle("#ffffff", "#ffd6e8").svg()}</g>')

    tags = [('AI', '#ffd1e3', '#d9609a'), ('IoT', '#cdeef2', '#3f8f9f'),
            ('Computer Vision', '#eef5b8', '#7f9322'), ('Software Dev', '#e6dcff', '#7a5cc4')]
    x = 64
    for t, bg, ln in tags:
        w = text_width('pix7', t, 17) + 30
        d.add(px_frame(x, 208, w, 32, 3, bg, ln, '#5b2a5e', 3))
        d.text(x + w / 2, 231, t, 'pix7', 17, '#4a2c58', anchor='middle')
        x += w + 14
    return d.save(out)


if __name__ == '__main__':
    import sys
    print(build(sys.argv[1] if len(sys.argv) > 1 else 'assets/header.svg'))
