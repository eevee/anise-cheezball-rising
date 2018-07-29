import json
from pathlib import Path
import sys

import PIL.Image


TILE_SIZE = 8
METATILE_SIZE = 16


def main(tiled_map_path):
    # I have:
    # - a tileset image made out of 16x16 tiles
    #   (...where each 8x8 subtile only uses colors from a single set of 4)
    # - a Tiled tileset and map of 16x16 tiles
    #
    # I need to end up with:
    # - 8x8 tile data
    # - Blocks of the tiles that make up a map
    # - Blocks of the attributes for those tiles

    print("SECTION \"Map dumping test\", ROM0")

    tiled_map_path = Path(tiled_map_path)
    with tiled_map_path.open() as f:
        tiled_map = json.load(f)

    if tiled_map['tilewidth'] != 16 or tiled_map['tileheight'] != 16:
        raise RuntimeError(
            "The Tiled map must use a tile size of 16 by 16, but this one is "
            f"{tiled_map['tilewidth']} by {tiled_map['tileheight']}.")

    # TODO will need object layer for events, later
    if len(tiled_map['layers']) != 1:
        raise RuntimeError("The Tiled map must have exactly one layer.")

    map_layer = tiled_map['layers'][0]
    if map_layer['type'] != 'tilelayer':
        raise RuntimeError("Only tile layers are supported.")

    if len(tiled_map['tilesets']) != 1:
        raise RuntimeError("The Tiled map must use only one tileset.")

    map_tileset = tiled_map['tilesets'][0]
    tileset_path = tiled_map_path.parent / map_tileset['source']
    with tileset_path.open() as f:
        tileset = json.load(f)

    if tileset['tilewidth'] != 16 or tileset['tileheight'] != 16:
        raise RuntimeError(
            "The Tiled tileset file must use a tile size of 16 by 16, but "
            f"this one is {tileset['tilewidth']} by {tileset['tileheight']}.")

    image_path = tileset_path.parent / tileset['image']
    im = PIL.Image.open(image_path)

    width, height = im.size
    if width != tileset['imagewidth'] or height != tileset['imageheight']:
        raise RuntimeError(
            f"The image at {image_path} is {width} by {height}, but "
            f"the Tiled tileset file at {tileset_path} is "
            f"{tileset['imagewidth']} by {tileset['imageheight']}.  "
            f"Try opening the tileset in Tiled to fix this.")

    # -------------------------------------------------------------------------

    # Get the palette.  There's a getpalette() method, but the palette it
    # returns has been padded to 256 colors for some reason, which makes it
    # useless for our purposes.  Instead, check out the poorly-documented
    # palette attribute, which has the palette as a flat list of channels.
    # God, I hate PIL.
    if im.palette is None:
        print("This tool only works on paletted PNGs!", file=sys.stderr)
        sys.exit(1)

    pal = im.palette.palette
    # TODO?  or divisible by four?  if len(pal) != 32:
    gbc_palettes = []
    asm_colors = []
    print("TEST_PALETTES:")
    for i in range(0, len(pal), 12):
        gbc_palette = []
        for j in range(i, i + 12, 3):
            r, g, b = color = pal[j:j + 3]
            gbc_palette.append(color)

            # Convert to RGB555
            asm_color = (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)
            asm_colors.append(asm_color)
            print(f"    dw %{asm_color:016b}")

        gbc_palettes.append(tuple(gbc_palette))

    for _ in range(len(asm_colors), 32):
        print("    dw 0")

    # -------------------------------------------------------------------------

    print("TEST_TILES:")

    # TODO if two colors in different palettes are identical, Do The Right
    # Thing (vastly more complicated but worth it i think)
    pixels = im.load()
    small_tile_index = 0
    # Flat list of the four little tiles that make up each big tile
    big_tile_subtiles = {}
    for ty in range(0, height, TILE_SIZE):
        for tx in range(0, width, TILE_SIZE):
            print(f"    ; tile {small_tile_index} at {tx}, {ty}")
            #seen_pixels = {}
            big_tile_index = (ty // METATILE_SIZE) * (width // METATILE_SIZE) + (tx // METATILE_SIZE)
            big_tile_subtiles.setdefault(big_tile_index, []).append(small_tile_index)
            for y in range(TILE_SIZE):
                print('    dw `', end='')
                for x in range(TILE_SIZE):
                    px = pixels[tx + x, ty + y]
                    #index = seen_pixels.setdefault(px, len(seen_pixels))
                    index = px % 4
                    # TODO track the palette this tile uses
                    print(index, end='')
                print()
            small_tile_index += 1

    # -------------------------------------------------------------------------

    print("TEST_MAP_1:")
    t0 = map_tileset['firstgid']
    layer_data = map_layer['data']
    layer_width = map_layer['width']
    # Print out the layer data
    for i in range(0, len(layer_data), layer_width):
        for tile in layer_data[i:i+layer_width]:
            tile -= t0
            subtiles = big_tile_subtiles[tile]
            print(f"    db {subtiles[0]}, {subtiles[1]}")
        for tile in layer_data[i:i+layer_width]:
            tile -= t0
            subtiles = big_tile_subtiles[tile]
            print(f"    db {subtiles[2]}, {subtiles[3]}")


def main(image_path):
    print("SECTION \"Image dumping test\", ROM0")

    im = PIL.Image.open(image_path)
    width, height = im.size

    # -------------------------------------------------------------------------

    # Get the palette.  There's a getpalette() method, but the palette it
    # returns has been padded to 256 colors for some reason, which makes it
    # useless for our purposes.  Instead, check out the poorly-documented
    # palette attribute, which has the palette as a flat list of channels.
    # God, I hate PIL.
    if im.palette is None:
        print("This tool only works on paletted PNGs!", file=sys.stderr)
        sys.exit(1)

    pal = im.palette.palette
    # TODO?  or divisible by four?  if len(pal) != 32:
    gbc_palettes = []
    asm_colors = []
    print("TEST_PALETTES:")
    for i in range(0, len(pal), 12):
        gbc_palette = []
        for j in range(i, i + 12, 3):
            r, g, b = color = pal[j:j + 3]
            gbc_palette.append(color)

            # Convert to RGB555
            asm_color = (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)
            asm_colors.append(asm_color)
            print(f"    dw %{asm_color:016b}")

        gbc_palettes.append(tuple(gbc_palette))

    for _ in range(len(asm_colors), 32):
        print("    dw 0")

    # -------------------------------------------------------------------------

    print("TEST_TILES:")

    # TODO if two colors in different palettes are identical, Do The Right
    # Thing (vastly more complicated but worth it i think)
    pixels = im.load()
    small_tile_index = 0
    # Flat list of the four little tiles that make up each big tile
    big_tile_subtiles = {}
    for ty2 in range(0, height, TILE_SIZE * 2):
        for tx in range(0, width, TILE_SIZE):
            for ty in (ty2, ty2 + TILE_SIZE):
                print(f"    ; tile {small_tile_index} at {tx}, {ty}")
                #seen_pixels = {}
                big_tile_index = (ty // METATILE_SIZE) * (width // METATILE_SIZE) + (tx // METATILE_SIZE)
                big_tile_subtiles.setdefault(big_tile_index, []).append(small_tile_index)
                for y in range(TILE_SIZE):
                    print('    dw `', end='')
                    for x in range(TILE_SIZE):
                        px = pixels[tx + x, ty + y]
                        #index = seen_pixels.setdefault(px, len(seen_pixels))
                        index = px % 4
                        # TODO track the palette this tile uses
                        print(index, end='')
                    print()
                small_tile_index += 1


if __name__ == '__main__':
    main(*sys.argv[1:])
