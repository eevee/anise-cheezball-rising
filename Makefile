TARGET := gamegirl.gbc

all: $(TARGET)

$(TARGET): main.rgbasm
	rgbasm -o main.o main.rgbasm
	rgblink -o $(TARGET) main.o
	rgbfix -C -v -p 0 $(TARGET)
