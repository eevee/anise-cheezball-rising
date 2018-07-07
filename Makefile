SRC := src
BUILD := build
RGBASM := rgbasm
RGBLINK := rgblink
RGBFIX := rgbfix

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

$(BUILD)/%.rgbasm.o: $(SRC)/%.rgbasm
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
-include $(DEPS)
