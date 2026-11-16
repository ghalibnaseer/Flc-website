#!/usr/bin/env python3
"""Make a Team page portrait in the site's house style.

Usage:
    python3 _tools/portrait.py <photo> <output name without extension> [--head 235] [--top 120]

Writes <name>.png and <name>.webp (800 x 834, transparent outside the ring).

House style: the person in greyscale, cut out and placed over the photo's own background,
which is blurred and tinted gold, all inside a brass ring. The figure is kept fully inside
the ring. The head is scaled to about --head pixels wide (measured across the ears at eye
level) with its top about --top pixels from the top. Where the photo is too narrow or too
short to fill the circle at that size, the figure is enlarged (cropped closer) instead of
fading the jacket into the background. For a tight passport-style crop, --top 150 or 160
places the head a little lower, which needs less enlargement.

Needs: pip install "rembg[cpu]" opencv-python pillow numpy
(rembg downloads the u2net_human_seg model on first use.)
"""
import argparse
import os
import urllib.request
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

W, H = 800, 834
CX, CY = 400, 452          # centre of the circle
R_PHOTO = 352              # radius of the photograph
R_FAINT = 358              # faint inner ring
R_RING = 365               # brass ring (3 px)
BRASS = (181, 135, 58)
GOLD_LIGHT = np.array([232, 190, 118], dtype=np.float32)  # colour of white after tinting


def cut_mask(img):
    from rembg import new_session, remove
    session = new_session('u2net_human_seg')
    return np.array(remove(img, session=session, only_mask=True, post_process_mask=True)).astype(np.float32) / 255


def face_box(img):
    grey = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'haarcascade_frontalface_default.xml')
    if not os.path.exists(path):
        # OpenCV's standard frontal-face detector, fetched once and kept beside this script
        urllib.request.urlretrieve('https://raw.githubusercontent.com/opencv/opencv/4.x/data/haarcascades/'
                                   'haarcascade_frontalface_default.xml', path)
    det = cv2.CascadeClassifier(path)
    faces = det.detectMultiScale(grey, scaleFactor=1.08, minNeighbors=6, minSize=(grey.shape[1] // 10,) * 2)
    if not len(faces):
        raise SystemExit('No face found in the photo.')
    return max(faces, key=lambda f: f[2] * f[3])


def head_metrics(mask, face):
    x, y, w, h = face
    eye_y = int(y + 0.42 * h)
    row = mask[eye_y] > 0.5
    cx = x + w // 2
    l = cx
    while l > 0 and row[l - 1]:
        l -= 1
    r = cx
    while r < len(row) - 1 and row[r + 1]:
        r += 1
    cols = mask[:, x + w // 4: x + 3 * w // 4] > 0.5
    top = int(np.argmax(cols.any(axis=1)))
    return r - l, top, cx


def make(photo, out, head=235, top_px=120):
    img = Image.open(photo).convert('RGB')
    sw, sh = img.size
    mask = cut_mask(img)
    face = face_box(img)
    head_w, head_top, face_cx = head_metrics(mask, face)

    # Scale: the head size asked for, enlarged only as far as needed so that no edge of the photo
    # that cuts through the figure (a shoulder at the side, the jacket at the bottom) shows inside
    # the circle. The circle's edge curves, so a cut low down at the side is often hidden anyway.
    touch_l = np.nonzero(mask[:, :3].max(axis=1) > 0.5)[0]
    touch_r = np.nonzero(mask[:, -3:].max(axis=1) > 0.5)[0]
    touch_b = np.nonzero(mask[-3:, :].max(axis=0) > 0.5)[0]

    def fits(s):
        ox, oy = CX - face_cx * s, top_px - head_top * s
        def half(dy):  # half-width of the circle at a vertical offset dy from its centre
            return np.sqrt(np.clip(R_PHOTO ** 2 - dy ** 2, 0, None))
        if len(touch_l) and np.any(ox > CX - half(oy + touch_l * s - CY) + 2):
            return False
        if len(touch_r) and np.any(ox + sw * s < CX + half(oy + touch_r * s - CY) - 2):
            return False
        if len(touch_b) and np.any(oy + sh * s < CY + half(ox + touch_b * s - CX) - 2):
            return False
        return True

    s = head / head_w
    while not fits(s):
        s *= 1.01
    ox = CX - face_cx * s
    oy = top_px - head_top * s

    def place(a, fill, resample):
        a = a.resize((max(1, round(sw * s)), max(1, round(sh * s))), resample)
        canvas = Image.new(a.mode, (W, H), fill)
        canvas.paste(a, (round(ox), round(oy)))
        return canvas

    # Background: the photo with the figure filled in by the surrounding colour, blurred, tinted gold.
    bg = np.array(img).astype(np.float32)
    m3 = (mask > 0.05)[..., None]
    small = cv2.resize(np.where(m3, 0, bg), (64, 64), interpolation=cv2.INTER_AREA)
    wts = cv2.resize((~m3[..., 0]).astype(np.float32), (64, 64), interpolation=cv2.INTER_AREA)
    for _ in range(40):  # spread the background colour into the figure's area
        num = cv2.GaussianBlur(small * wts[..., None], (0, 0), 3)
        den = cv2.GaussianBlur(wts, (0, 0), 3)[..., None] + 1e-6
        small = np.where(wts[..., None] > 0.5, small, num / den)
        wts = np.maximum(wts, (cv2.GaussianBlur(wts, (0, 0), 3) > 0.05).astype(np.float32))
    filled = np.where(m3, cv2.resize(small, (sw, sh), interpolation=cv2.INTER_CUBIC), bg)
    bg_img = place(Image.fromarray(np.clip(filled, 0, 255).astype(np.uint8)), (0, 0, 0), Image.LANCZOS)
    # extend the background past the photo's edges, if any, by repeating the edge
    arr = np.array(bg_img).astype(np.float32)
    x0, y0 = max(0, round(ox)), max(0, round(oy))
    x1, y1 = min(W, round(ox + sw * s)), min(H, round(oy + sh * s))
    arr = cv2.copyMakeBorder(arr[y0:y1, x0:x1], y0, H - y1, x0, W - x1, cv2.BORDER_REPLICATE)
    lum = cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
    lum = cv2.GaussianBlur(lum, (0, 0), 14)
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot(xx - CX, yy - (CY - 90)) / R_PHOTO
    lum = 0.74 + (lum - lum.mean()) * 0.9 + 0.12 - 0.34 * d ** 2     # keep the photo's light, add depth
    tint = np.clip(lum, 0.28, 0.97)[..., None] * GOLD_LIGHT
    background = Image.fromarray(np.clip(tint, 0, 255).astype(np.uint8))

    # Figure: greyscale with gentle contrast, a crisp (not feathered) edge.
    fig = place(img, (0, 0, 0), Image.LANCZOS)
    fig = ImageOps.autocontrast(fig.convert('L'), cutoff=0.4).convert('RGB')
    fm = place(Image.fromarray((mask * 255).astype(np.uint8)), 0, Image.LANCZOS)
    fm = fm.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.6))
    photo_disc = Image.composite(fig, background, fm)

    # Clip to the circle and draw the rings (drawn at 4x for smooth edges).
    k = 4
    disc = Image.new('L', (W * k, H * k), 0)
    ImageDraw.Draw(disc).ellipse([(CX - R_PHOTO) * k, (CY - R_PHOTO) * k, (CX + R_PHOTO) * k, (CY + R_PHOTO) * k], fill=255)
    disc = disc.resize((W, H), Image.LANCZOS)
    out_img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    out_img.paste(photo_disc, (0, 0), disc)
    rings = Image.new('RGBA', (W * k, H * k), (0, 0, 0, 0))
    dr = ImageDraw.Draw(rings)
    dr.ellipse([(CX - R_FAINT) * k, (CY - R_FAINT) * k, (CX + R_FAINT) * k, (CY + R_FAINT) * k], outline=BRASS + (140,), width=1 * k)
    dr.ellipse([(CX - R_RING - 1) * k, (CY - R_RING - 1) * k, (CX + R_RING + 1) * k, (CY + R_RING + 1) * k], outline=BRASS + (255,), width=3 * k)
    out_img = Image.alpha_composite(out_img, rings.resize((W, H), Image.LANCZOS))
    out_img.save(out + '.png', optimize=True)
    out_img.save(out + '.webp', quality=86, method=6)
    print(f'{out}: head {head_w}px in the photo, scale {s:.3f}, head about {round(head_w * s)}px')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('photo')
    ap.add_argument('out')
    ap.add_argument('--head', type=int, default=235)
    ap.add_argument('--top', type=int, default=120)
    a = ap.parse_args()
    make(a.photo, a.out, a.head, a.top)
