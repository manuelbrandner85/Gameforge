"""Deterministische, technische Bildprüfung ohne Fremdbibliotheken (reines Python, PNG 8 Bit).

Prüft: gültige PNG-Datei, Maße, nicht leer/einfarbig, Helligkeit/Kontrast, bei Pixel-Art Farbanzahl
und Pixelraster. Eine inhaltliche Bewertung (Anatomie, Kanon-Treue) leistet dieser Prüfer NICHT –
solche Bilder gehen immer zur menschlichen Freigabe.
"""
from __future__ import annotations
import struct
import zlib


def read_png(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Keine gültige PNG-Datei')
    pos, idat, w = 8, [], None
    while pos < len(data):
        ln, typ = struct.unpack('>I4s', data[pos:pos + 8])
        chunk = data[pos + 8:pos + 8 + ln]
        if typ == b'IHDR':
            w, h, depth, ctype, _, _, inter = struct.unpack('>IIBBBBB', chunk)
        elif typ == b'IDAT':
            idat.append(chunk)
        elif typ == b'IEND':
            break
        pos += 12 + ln
    if w is None:
        raise ValueError('PNG ohne Kopfdaten')
    if depth != 8 or ctype not in (2, 6) or inter:
        return {'width': w, 'height': h, 'pixels': None, 'channels': None}
    ch = 3 if ctype == 2 else 4
    raw = zlib.decompress(b''.join(idat))
    stride = w * ch
    rows, prev, i = [], bytearray(stride), 0
    for _ in range(h):
        ft = raw[i]; line = bytearray(raw[i + 1:i + 1 + stride]); i += 1 + stride
        if ft == 1:
            for x in range(ch, stride): line[x] = (line[x] + line[x - ch]) & 255
        elif ft == 2:
            for x in range(stride): line[x] = (line[x] + prev[x]) & 255
        elif ft == 3:
            for x in range(stride): line[x] = (line[x] + ((line[x - ch] if x >= ch else 0) + prev[x]) // 2) & 255
        elif ft == 4:
            for x in range(stride):
                a = line[x - ch] if x >= ch else 0; b = prev[x]; c = prev[x - ch] if x >= ch else 0
                p = a + b - c; pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(bytes(line)); prev = line
    return {'width': w, 'height': h, 'pixels': rows, 'channels': ch}


def check_image(path, expect_w=None, expect_h=None, pixel_grid=None, max_colors=None):
    res = {'checks': [], 'ok': True, 'needs_human_review': True}

    def add(name, ok, detail):
        res['checks'].append({'name': name, 'ok': bool(ok), 'detail': detail})
        if not ok:
            res['ok'] = False
    try:
        img = read_png(path)
    except (ValueError, OSError, zlib.error, struct.error) as e:
        add('Datei', False, str(e))
        return res
    add('Datei', True, f'PNG {img["width"]}×{img["height"]}')
    if expect_w and expect_h:
        add('Auflösung', (img['width'], img['height']) == (expect_w, expect_h), f'erwartet {expect_w}×{expect_h}')
    rows, ch = img['pixels'], img['channels']
    if rows is None:
        add('Pixelanalyse', True, 'Format nicht analysierbar (übersprungen)')
        return res
    w, h = img['width'], img['height']
    step = max(1, min(w, h) // 128)
    vals, colors = [], set()
    for y in range(0, h, step):
        r = rows[y]
        for x in range(0, w, step):
            o = x * ch
            px = (r[o], r[o + 1], r[o + 2])
            colors.add(px)
            vals.append((px[0] * 299 + px[1] * 587 + px[2] * 114) // 1000)
    mean = sum(vals) / len(vals)
    std = (sum((v - mean) ** 2 for v in vals) / len(vals)) ** .5
    res['stats'] = {'brightness_mean': round(mean, 1), 'contrast_std': round(std, 1), 'sampled_colors': len(colors)}
    add('Nicht leer', std > 6 and len(colors) > 8, f'Kontrast {std:.1f}, {len(colors)} Farben (Stichprobe)')
    add('Belichtung', 12 < mean < 243, f'mittlere Helligkeit {mean:.0f}/255')
    if pixel_grid:
        all_colors = set()
        bad = 0; blocks = 0
        for by in range(0, h - pixel_grid + 1, pixel_grid * 4):
            for bx in range(0, w - pixel_grid + 1, pixel_grid * 4):
                blocks += 1
                o = bx * ch
                ref = rows[by][o:o + 3]
                if any(rows[by + dy][o + dx * ch:o + dx * ch + 3] != ref for dy in range(pixel_grid) for dx in range(pixel_grid)):
                    bad += 1
        for y in range(0, h, 2):
            r = rows[y]
            for x in range(0, w, 2):
                o = x * ch; all_colors.add(r[o:o + 3])
        add('Pixelraster', bad == 0, f'{blocks - bad}/{blocks} geprüfte {pixel_grid}×{pixel_grid}-Blöcke einfarbig')
        if max_colors:
            add('Farbpalette', len(all_colors) <= max_colors, f'{len(all_colors)} Farben (Grenze {max_colors})')
    return res
