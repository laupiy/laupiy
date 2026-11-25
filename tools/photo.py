"""Ubah fotomu jadi pixel-art Grid supaya bisa dipasang di header / about.

Taruh fotomu di  tools/photo.jpg  (atau photo.png).
"""
import os
from PIL import Image, ImageOps, ImageEnhance
from pixlib import Grid

HERE = os.path.dirname(os.path.abspath(__file__))
PHOTO = next((p for p in (os.path.join(HERE, 'photo.jpg'), os.path.join(HERE, 'photo.jpeg'),
                          os.path.join(HERE, 'photo.png')) if os.path.exists(p)), None)

FOCUS_Y = 0.30   # 0 = ambil bagian atas foto, 0.5 = tengah. Naikkan kalau wajah terpotong di atas.
FOCUS_X = 0.50
COLORS = 40      # makin kecil makin "retro"


def photo_grid(path, w, h, colors=COLORS):
    im = ImageOps.exif_transpose(Image.open(path)).convert('RGB')
    iw, ih = im.size
    tgt = w / h
    if iw / ih > tgt:                       # terlalu lebar -> potong kiri/kanan
        nw = int(ih * tgt)
        x0 = int((iw - nw) * FOCUS_X)
        im = im.crop((x0, 0, x0 + nw, ih))
    else:                                   # terlalu tinggi -> potong atas/bawah
        nh = int(iw / tgt)
        y0 = int((ih - nh) * FOCUS_Y)
        im = im.crop((0, y0, iw, y0 + nh))
    im = im.resize((w, h), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(1.15)
    im = ImageEnhance.Contrast(im).enhance(1.08)
    im = im.quantize(colors=colors, method=Image.MEDIANCUT, dither=Image.NONE).convert('RGB')
    g = Grid(w, h)
    px = im.load()
    for y in range(h):
        for x in range(w):
            r, gg, b = px[x, y]
            g.set(x, y, f'#{r:02x}{gg:02x}{b:02x}')
    return g


def photo_image(path, w, h, scale=2, quality=88):
    """Foto asli (tidak di-pixel) sebagai <image> SVG berukuran w x h, ditanam langsung di dalam SVG."""
    import io, base64
    im = ImageOps.exif_transpose(Image.open(path)).convert('RGB')
    iw, ih = im.size
    tgt = w / h
    if iw / ih > tgt:
        nw = int(ih * tgt)
        x0 = int((iw - nw) * FOCUS_X)
        im = im.crop((x0, 0, x0 + nw, ih))
    else:
        nh = int(iw / tgt)
        y0 = int((ih - nh) * FOCUS_Y)
        im = im.crop((0, y0, iw, y0 + nh))
    im = im.resize((w * scale, h * scale), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=quality, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f'<image x="0" y="0" width="{w}" height="{h}" preserveAspectRatio="none" href="data:image/jpeg;base64,{b64}"/>'
