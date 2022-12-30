SRC := src
BUILD := build
RGBASM := rgbasm
RGBLINK := rgblink
RGBFIX := rgbfix
PYTHON := python

NAME := anise-cheezball-rising
TARGET := $(BUILD)/$(NAME).gbc
MAPFILE := $(BUILD)/$(NAME).map
SYMFILE := $(BUILD)/$(NAME).sym

SOURCES := $(wildcard $(SRC)/*.rgbasm)
# src/foo.rgbasm -> build/foo.rgbasm.o
# TODO: won't work for nested files (which wildcard doesn't find anyway), needs a mkdir
OBJECTS := $(foreach src,$(SOURCES),$(patsubst $(SRC)/%,$(BUILD)/%.o,$(src)))
DEPS := $(foreach src,$(SOURCES),$(patsubst $(SRC)/%,$(BUILD)/%.deps,$(src)))

all: $(TARGET)


# ==============================================================================
# Special intermediate targets

# Please don't delete intermediate files, thanks
.SECONDARY:

# ------------------------------------------------------------------------------
# Build sprite images into data files, then into objects
# data/sprites/foo.png -> build/sprites/foo.png.rgbasm.o

SPRITE_IMAGES := $(wildcard data/sprites/*.png)
SPRITE_SOURCES := $(foreach src,$(SPRITE_IMAGES),$(patsubst data/%,$(BUILD)/%.rgbasm,$(src)))
SPRITE_OBJECTS := $(foreach src,$(SPRITE_SOURCES),$(src).o)

$(BUILD)/sprites/.keep:
	mkdir -p $(BUILD)/sprites
	touch $(BUILD)/sprites/.keep

$(BUILD)/sprites/%.rgbasm: data/sprites/% $(BUILD)/sprites/.keep util/png-to-tiles.py
	$(PYTHON) util/png-to-tiles.py spritesheet -o $@ $<
$(BUILD)/sprites/%.rgbasm.o: $(BUILD)/sprites/%.rgbasm
	$(RGBASM) -o $@ $<

# ------------------------------------------------------------------------------
# Build the test map into one big ol' data file

MAP_MAPS := data/maps/moon.tmx.json
MAP_SOURCES := $(foreach src,$(MAP_MAPS),$(patsubst data/%,$(BUILD)/%.rgbasm,$(src)))
MAP_OBJECTS := $(foreach src,$(MAP_SOURCES),$(src).o)

$(BUILD)/maps/.keep:
	mkdir -p $(BUILD)/maps
	touch $(BUILD)/maps/.keep

$(BUILD)/maps/%.rgbasm: data/maps/% $(BUILD)/maps/.keep util/png-to-tiles.py
	$(PYTHON) util/png-to-tiles.py tilemap -o $@ $<
$(BUILD)/maps/%.rgbasm.o: $(BUILD)/maps/%.rgbasm
	$(RGBASM) -o $@ $<

# ------------------------------------------------------------------------------
# Build the font

$(BUILD)/font.inc: util/font-to-tiles.py data/font.png
	$(PYTHON) util/font-to-tiles.py data/font.png > $(BUILD)/font.inc


# ==============================================================================
# The regular expected stuff
# TODO: i've manually listed targets here because otherwise, on first build,
# rgbasm will balk that it doesn't exist, so it'll never create the deps file,
# so make will never know it needs to be built first.  this enforces build
# order without supplying the explicit dependency.  is there a better fix?
$(BUILD)/%.rgbasm.o: $(SRC)/%.rgbasm | $(BUILD)/font.inc
	$(RGBASM) -L -h -i $(SRC)/ -i $(BUILD)/ -M $(BUILD)/$*.rgbasm.deps -o $@ $<


# ==============================================================================
# Finally, the game itself
ALL_OBJECTS := $(SPRITE_OBJECTS) $(MAP_OBJECTS) $(OBJECTS)
$(TARGET): $(ALL_OBJECTS)
	$(RGBLINK) -o $(TARGET) -m $(MAPFILE) -n $(SYMFILE) $(ALL_OBJECTS)
	$(RGBFIX) -C -v -p 0 $(TARGET)


# ==============================================================================
# Special rules

.PHONY: clean
clean:
	rm -f $(SPRITE_OBJECTS)
	rm -f $(SPRITE_SOURCES)
	rm -f $(BUILD)/sprites/.keep
	rmdir $(BUILD)/sprites
	rm -f $(MAP_OBJECTS)
	rm -f $(MAP_SOURCES)
	rm -f $(BUILD)/maps/.keep
	rmdir $(BUILD)/maps
	rm -f $(OBJECTS)
	rm -f $(DEPS)
	rm -f $(TARGET)
	rm -f $(MAPFILE)
	rm -f $(SYMFILE)


# Include generated dependency files
# TODO: if i remove a dep, make will be unable to recreate it, but these
# lingering files will still say it's necessary.  is that fixable?
-include $(DEPS)
