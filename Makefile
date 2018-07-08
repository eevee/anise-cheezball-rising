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

# Special intermediate targets

$(BUILD)/font.inc: util/font-to-tiles.py data/font.png
	$(PYTHON) util/font-to-tiles.py data/font.png > $(BUILD)/font.inc

# The regular expected stuff
# TODO: i've manually listed font.inc here because otherwise, on first build,
# rgbasm will balk that it doesn't exist, so it'll never create the deps file,
# so make will never know it needs to be built first.  this enforces build
# order without supplying the explicit dependency.  is there a better fix?
$(BUILD)/%.rgbasm.o: $(SRC)/%.rgbasm | $(BUILD)/font.inc
	$(RGBASM) -i $(SRC)/ -i $(BUILD)/ -M $(BUILD)/$*.rgbasm.deps -o $@ $<

$(TARGET): $(OBJECTS)
	$(RGBLINK) -o $(TARGET) -m $(MAPFILE) -n $(SYMFILE) $(OBJECTS)
	$(RGBFIX) -C -v -p 0 $(TARGET)

clean:
	rm -f $(OBJECTS)
	rm -f $(DEPS)
	rm -f $(TARGET)
	rm -f $(MAPFILE)
	rm -f $(SYMFILE)

# Include generated dependency files
# TODO: if i remove a dep, make will be unable to recreate it, but these
# lingering files will still say it's necessary.  is that fixable?
-include $(DEPS)
