import hid
import time
import math
from threading import Thread

READ_BUFF_MAXSIZE = 2048

def _valbyte2(b1, b2):
    return b1 * 256 + b2

def _tobyte2(x):
    return [x >> 8, x & 0xff]

def _fromcx(h_, c, x):
    h = math.floor(h_)
    if h == 0:
        return c, x, 0
    elif h == 1:
        return x, c, 0
    elif h == 2:
        return 0, c, x
    elif h == 3:
        return 0, x, c
    elif h == 4:
        return x, 0, c
    elif h == 5:
        return c, 0, x
    else:
        return 0, 0, 0

def RGB2HSV(r, g, b):
    pi_3 = math.pi / 3
    r, g, b = r / 255, g / 255, b / 255
    max_ = max(r, g, b)
    min_ = min(r, g, b)
    h = 0
    div = max_ - min_
    if min_ == max_:
        h = 0
    elif max_ == r:
        h = pi_3 * (g - b) / div
    elif max_ == g:
        h = pi_3 * (2 + (b - r) / div)
    elif max_ == b:
        h = pi_3 * (4 + (r - g) / div)
    if h < 0:
        h = h + math.pi * 2
    s = 0
    if max_ != 0:
        s = div / max_
    v = max_
    return h, s, v

def HSV2RGB(h, s, v):
    pi_3 = math.pi / 3
    ch = v * s
    h_ = h / pi_3
    x = ch * (1 - abs(h_ % 2 - 1))
    r1, g1, b1 = _fromcx(h_, ch, x)
    m = v - ch
    return int((r1 + m) * 255), int((g1 + m) * 255), int((b1 + m) * 255)

class ReadWorker:
    def __init__(self, device, callback=None):
        self._device = device
        self._callback = callback
        self._buf = []

    def execute(self):
        try:
            count = 0
            while len(self._buf) == 0:
                # will raise IOError if failed
                self._buf = self._device.read(READ_BUFF_MAXSIZE, 50)
                count += 1
                if count > 20:
                    break
            if self._callback:
                self._callback(self._buf)
        except IOError as e:
            print(e, self._device.error())

    def getResult(self):
        return self._buf

class HIDDevice:
    def __init__(self, vid, pid=None):
        if isinstance(vid, bytes):
            self._path = vid
            self._vid = None
            self._pid = None
        else:
            self._path = None
            self._vid = vid
            self._pid = pid
        self._h = hid.device()
        if self._path:
            self._h.open_path(self._path)
        else:
            self._h.open(self._vid, self._pid)
        self._h.set_nonblocking(1)

    def __del__(self):
        self._h.close()

    def reopen(self):
        self._h.close()
        if self._path:
            self._h.open_path(self._path)
        else:
            self._h.open(self._vid, self._pid)
        self._h.set_nonblocking(1)

    def read(self, cb=None):
        worker = ReadWorker(self._h, cb)
        Thread(target=worker.execute).start()

    def readSync(self):
        worker = ReadWorker(self._h)
        worker.execute()
        return worker.getResult()

    def write(self, data):
        result = self._h.write(data)
        if result < 0:
            print('write error:', self._h.error())
        return result >= 0

QMK_RGBLIGHT_BRIGHTNESS = 0x80
QMK_RGBLIGHT_EFFECT = 0x81
QMK_RGBLIGHT_EFFECT_SPEED = 0x82
QMK_RGBLIGHT_COLOR = 0x83
QMKUnderglowEffects = [  # 0~36
    ['All Off', 0],
    ['Solid Color', 1],
    ['Breathing 1', 1],
    ['Breathing 2', 1],
    ['Breathing 3', 1],
    ['Breathing 4', 1],
    ['Rainbow Mood 1', 0],
    ['Rainbow Mood 2', 0],
    ['Rainbow Mood 3', 0],
    ['Rainbow Swirl 1', 0],
    ['Rainbow Swirl 2', 0],
    ['Rainbow Swirl 3', 0],
    ['Rainbow Swirl 4', 0],
    ['Rainbow Swirl 5', 0],
    ['Rainbow Swirl 6', 0],
    ['Snake 1', 1],
    ['Snake 2', 1],
    ['Snake 3', 1],
    ['Snake 4', 1],
    ['Snake 5', 1],
    ['Snake 6', 1],
    ['Knight 1', 1],
    ['Knight 2', 1],
    ['Knight 3', 1],
    ['Christmas', 1],
    ['Gradient 1', 1],
    ['Gradient 2', 1],
    ['Gradient 3', 1],
    ['Gradient 4', 1],
    ['Gradient 5', 1],
    ['Gradient 6', 1],
    ['Gradient 7', 1],
    ['Gradient 8', 1],
    ['Gradient 9', 1],
    ['Gradient 10', 1],
    ['RGB Test', 1],
    ['Alternating', 1]
]

class CTX12E4(HIDDevice):
    def __init__(self, path):
        super().__init__(path)

    @staticmethod
    def create():
        vendorProductId = 1465172993
        productId = vendorProductId & 0xffff
        vendorId = vendorProductId >> 16
        for device_dict in hid.enumerate():
            vid = device_dict.get('vendor_id')
            pid = device_dict.get('product_id')
            if vid == vendorId and pid == productId:
                path = device_dict.get('path')
                d = CTX12E4(path)
                try:
                    result = d.hidCommand(19)
                    if len(result) == 32:
                        return d
                except IOError as e:
                    print(e)

    #

    def getQMKBrightness(self):
        r = self.hidCommand(13, [0x80])
        return r[2]

    def getQMKEffectType(self):
        r = self.hidCommand(13, [0x81])
        return r[2]

    def getQMKEffectName(self):
        return QMKUnderglowEffects[self.getQMKEffectType()]

    def getQMKEffectSpeed(self):
        r = self.hidCommand(13, [0x82])
        return r[2], r[3], r[4]

    def getQMKColor(self):
        r = self.hidCommand(13, [0x83])
        return r[2], r[3]

    def setQMKBrightness(self, val):
        self.hidCommand(18, [0x80, val])

    def setQMKEffectType(self, val):
        self.hidCommand(18, [0x81, val])

    def setQMKEffectSpeed(self, v1, v2, v3):
        self.hidCommand(18, [0x82, v1, v2, v3])

    def setQMKColor(self, hue, sat):
        self.hidCommand(18, [0x83, hue, sat])

    #

    def setQMKColorRGB(self, r, g, b):
        r = max(0, min(r, 255))
        g = max(0, min(g, 255))
        b = max(0, min(b, 255))
        h, s, v = RGB2HSV(r, g, b)
        h = int(h / math.pi / 2 * 255)
        s = int(s * 255)
        v = int(v * 255)
        self.setQMKColor(h, s)
        self.setQMKBrightness(v)

    def getQMKColorRGB(self):
        h, s = self.getQMKColor()
        v = self.getQMKBrightness()
        h = h / 255 * math.pi * 2
        s = s / 255
        v = v / 255
        return HSV2RGB(h, s, v)

    #

    def getBacklightValue(self, x, y=1):
        # x = QMK_RGBLIGHT_xxx
        r = self.hidCommand(13, [x])
        return r[2], r[3], r[4]

    def setBacklightValue(self, x, *y):
        self.hidCommand(18, [x, *y])

    def getRGBMode(self):
        r = self.hidCommand(13, [10])
        return r[2]

    def getBrightness(self):
        r = self.hidCommand(13, [9])
        return r[2]

    def getColor(self, x):
        r = self.hidCommand(13, [x == 1 and 12 or 13])
        return r[2], r[3]

    def setColor(self, x, y, z):
        self.hidCommand(18, [x == 1 and 12 or 13, x, y, z])

    def getCustomColor(self, x):
        r = self.hidCommand(13, [23, x])
        return r[3], r[4]

    def setCustomColor(self, x, y, z):
        self.hidCommand(18, [23, x, y, z])

    def setRGBMode(self, mode):
        self.hidCommand(18, [10, mode])

    def saveLighting(self):
        self.hidCommand(17)

    def getMacroCount(self):
        return self.hidCommand(19)[1]

    def getMacroBufferSize(self):
        r = self.hidCommand(8)
        return _valbyte2(r[1], r[2])

    def getMacroBytes(self):
        size = self.getMacroBufferSize()
        t = []
        for i in range(0, size, 28):
            r = self.hidCommand(6, [*_tobyte2(i), 28])
            t += r[4:]
        return t

    def hidCommand(self, id, args=None):
        if args is None:
            args = []
        return self._hidCommand([id, args])

    def _hidCommand(self, item):
        id, args = item
        buf = [0] * 33
        cmds = [0, id, *args]
        for i in range(len(cmds)):
            buf[i] = cmds[i]
        ok = self.write(buf)
        if not ok:
            self.reopen()
            if not self.write(buf):
                print('failed to write')
                return []
        response = self.readSync()
        return response

if __name__ == '__main__':
    d = CTX12E4.create()
    d.setQMKEffectType(1) # solid color
    d.setQMKColorRGB(0, 0, 255)
    d.saveLighting()
    print(d.getQMKBrightness())
    print(d.getQMKEffectType())
    print(d.getQMKColor())
    print(d.getQMKColorRGB())
    hid.hidapi_exit()
