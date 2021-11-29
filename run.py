import time
import Device
from HID import CTX12E4

def smooth(v1, v2, alpha):
    return v1 * (1 - alpha) + v2 * alpha

class Handler:
    def __init__(self):
        self._t = time.time()
        self._r = 0
        self._g = 0
        self._b = 0
        self._keyboard = CTX12E4.create()

    def update(self, colors):
        alpha = 0.5
        r, g, b = list(map(lambda *a: sum(a) / len(a), *colors))
        self._r = smooth(self._r, r, alpha)
        self._g = smooth(self._g, g, alpha)
        self._b = smooth(self._b, b, alpha)

    def handle(self, colors):
        # 30Hz => 10Hz
        t = time.time()
        if t - self._t < 0.1:
            return
        self._t = t
        self.update(colors)
        if self._keyboard:
            self._keyboard.setQMKColorRGB(self._r, self._g, self._b)

def main():
    # Ctrl+C to exit
    hdl = Handler()
    conn = Device.DeviceConnector(Device.Chromalink, hdl.handle)
    conn.start()
    conn.close()
    print('end')

if __name__ == '__main__':
    main()
