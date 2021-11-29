import time
import Device
from HID import CTX12E4

class Handler:
    def __init__(self):
        self._t = time.time()
        self._r = 0
        self._g = 0
        self._b = 0
        self._keyboard = CTX12E4.create()

    def handle(self, colors):
        if time.time() - self._t < 0.1:
            return
        self._t = time.time()
        r_, g_, b_ = colors[0]
        alpha = 0.5
        self._r = self._r * (1 - alpha) + r_ * alpha
        self._g = self._g * (1 - alpha) + g_ * alpha
        self._b = self._b * (1 - alpha) + b_ * alpha
        if self._keyboard:
            self._keyboard.setQMKColorRGB(self._r, self._g, self._b)

def main():
    # Ctrl+C to exit
    hdl = Handler()
    conn = Device.DeviceConnector(Device.Headset, hdl.handle)
    conn.start()
    conn.close()
    print('end')

if __name__ == '__main__':
    main()
