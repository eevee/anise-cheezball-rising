TARGET := gamegirl.gb

all: $(TARGET)

$(TARGET): main.rgbasm
	rgbasm -o main.o main.rgbasm
	rgblink -o $(TARGET) main.o
	rgbfix -v -p 0 $(TARGET)
