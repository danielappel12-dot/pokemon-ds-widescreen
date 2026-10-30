#!/usr/bin/env python3
"""Copies the game list's pictures out of an existing Pokemon DS Widescreen program, so that a
rebuilt one shows the same ones. The program carries them as plain JPEG files, one after the
other, in the order CMakeLists.txt builds them in (IRBO IRAO IREO IRDO IPKE IPGE CPUE).

    python3 extract_art.py <old program> <output folder>
"""
import os
import sys

CODES = ['IRBO', 'IRAO', 'IREO', 'IRDO', 'IPKE', 'IPGE', 'CPUE']


def jpeg_end(d, s):
    """The end of the JPEG starting at s: its segments walked to the image data, then the
    image data scanned to its end marker (FF D9), skipping stuffed bytes and restart markers."""
    i = s + 2
    while i + 4 <= len(d):
        if d[i] != 0xFF:
            return None
        m = d[i + 1]
        if m == 0xFF:
            i += 1
            continue
        n = (d[i + 2] << 8) | d[i + 3]
        i += 2 + n
        if m == 0xDA:  # start of scan: entropy-coded data follows
            while i + 1 < len(d):
                if d[i] == 0xFF:
                    nxt = d[i + 1]
                    if nxt == 0xD9:
                        return i + 2
                    if nxt == 0x00 or 0xD0 <= nxt <= 0xD7 or nxt == 0xFF:
                        i += 1 if nxt == 0xFF else 2
                        continue
                    # (another marker: a progressive JPEG's next scan, or tables)
                    if nxt == 0xDA or 0xC0 <= nxt <= 0xFE:
                        break
                i += 1
            # (back to walking segments from the marker found)
    return None


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    d = open(sys.argv[1], 'rb').read()
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    found = []
    pos = 0
    while len(found) < len(CODES):
        s = d.find(b'\xff\xd8\xff', pos)
        if s < 0:
            break
        e = jpeg_end(d, s)
        # (Real pictures only: a JFIF or Exif header and a sensible size.)
        if e and d[s + 3] in (0xE0, 0xE1, 0xDB) and 2000 < e - s < 2000000:
            found.append((s, e))
            pos = e
        else:
            pos = s + 3
    if len(found) != len(CODES):
        sys.exit('found %d pictures, not %d: building without them' % (len(found), len(CODES)))
    for code, (s, e) in zip(CODES, found):
        with open(os.path.join(out, code + '.jpg'), 'wb') as f:
            f.write(d[s:e])
        print('%s.jpg  %d bytes' % (code, e - s))


if __name__ == '__main__':
    main()
