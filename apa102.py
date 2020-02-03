import spidev
from struct import pack
from math import ceil

class Apa102:
    def __init__(self, led_count, spi_port=0, spi_cs=0, clock_speed_hz=8_000_000, global_brightness=30, autoshow=True):
        self._spi_port = spi_port
        self._spi_cs = spi_cs
        self._clock_speed_hz = clock_speed_hz
        self._global_brightness = global_brightness
        self._led_count = led_count
        self.autoshow = autoshow
        self._leds = [(0x00, 0x00, 0x00)]*self._led_count
        self._spi = spidev.SpiDev()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self):
        self.close()

    def __getitem__(self, key):
        return self._leds[key]

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            for i in range(*key.indices(len(self._leds))):
                self._leds[i] = value
        else:
            self._leds[key] = value
        if self.autoshow:
            self.show()

    def open(self):
        self._spi.open(self._spi_port, self._spi_cs)
        self._spi.max_speed_hz = self._clock_speed_hz

    def close(self):
        self._spi.close()

    def send(self, message):
        self._spi.writebytes(message)

    def show(self):
        start_frame = b"\x00\x00\x00\x00"
        end_frame = b"\x00"*int(ceil((len(self._leds)-1)/16))
        led_frames = []
        led_frame_header = 0b1110_0000
        global_brightness = self._global_brightness if 0<self._global_brightness<31 else 0 if 0<self._global_brightness else 31
        led_frame_header |= global_brightness
        for r,g,b in self._leds:
            led_frames.append(led_frame_header+pack("BBB", b, g, r))
        message = start_frame, b"".join(led_frames) + end_frame
        self.send(message)

def demo(strip):
    from time import sleep
    strip[1] = (0xFF, 0x00, 0x00)
    sleep(1)
    strip[5:15] = (0x00, 0xFF, 0x00)
    sleep(1)
    strip[17:] = (0x00, 0x00, 0xFF)
    sleep(1)
    strip[:] = (0x00, 0x00, 0x00)
    sleep(1)
    strip[:] = (0xFF, 0xFF, 0xFF)
    sleep(1)
    strip[:] = (0x00, 0x00, 0x00)
    sleep(1)


def main():
    clock_speed_hz = 8_000_000
    with Apa102(20, clock_speed_hz=clock_speed_hz) as strip:
        demo(strip)

if __name__ == "__main__":
    main()
