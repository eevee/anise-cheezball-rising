"""Converts a PNG containing a variable-width font into a source
file for rgbasm.

The image format is similar to the one LÖVE uses: the upper-left
pixel of the whole image is considered to mark the start of a
new letter whenever it appears in the top row.  Unlike LÖVE,
that column is also part of the following letter, and is
replaced with color zero.  Also, no letter may be wider than 8
pixels (though the renderer includes a 1px gap after every
character).

The palette is ignored and indices are used directly, but
generally color 0 should be the background and color 1 should be
the primary text color.
"""
from pathlib import Path
import sys

import PIL.Image


TILE_SIZE = 8
METATILE_SIZE = 16


def main(font_image_path):
    im = PIL.Image.open(font_image_path)

    width, height = im.size
    if height != 16:
        # TODO well, not necessarily!  in fact i'd like to cut
        # it down to 12.  but for now, yes
        raise RuntimeError("Font image must be exactly 16 pixels tall")

    pixels = im.load()
    indicator = pixels[0, 0]  # this color starts a new glyph
    glyph_starts = []  # x-offsets of where glyphs begin
    glyphs = []  # lists of rows of pixels

    # Deal with the first row first, so we know where the
    # divisions are
    for x in range(width):
        pixel = pixels[x, 0]
        if pixel == indicator:
            glyph_starts.append(x)
            glyphs.append([[]])
            pixel = 0
        glyphs[-1][0].append(pixel)
        # TODO enforce no more than 8 pixels

    # Continue with subsequent rows
    for y in range(1, height):
        g = -1
        for x in range(width):
            if g + 1 < len(glyph_starts) and x == glyph_starts[g + 1]:
                g += 1
                glyphs[g].append([])
            pixel = pixels[x, y]
            glyphs[g][-1].append(pixel)

    # Write it out
    for g, glyph in enumerate(glyphs):
        if g + 1 < len(glyphs):
            glyph_width = glyph_starts[g + 1] - glyph_starts[g]
        else:
            glyph_width = width - glyph_starts[g]

        print(f"; {chr(g + 32)}")
        print(f"    db {glyph_width}")

        for row in glyph:
            row = (row + [0] * 8)[:8]
            print('    dw `' + ''.join(map(str, row)))


if __name__ == '__main__':
    main(*sys.argv[1:])
