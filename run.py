import time
import Device
import Win
from HID import CTX12E4
from threading import Thread, Lock
from Common import RGB2HSV, HSV2RGB

ChromaExeList = [
    #
]

CustomExeList = {
    'Code.exe': [0x00, 0x66, 0xb8],
    'devenv.exe': [0x86, 0x61, 0xc5],
    'pycharm64.exe': [0xfc, 0xf8, 0x4a],
    'idea64.exe': [0x12, 0x79, 0xf4],
    'GitHubDesktop.exe': [0x7a, 0x2f, 0x9f],
    'WINWORD.EXE': [0x28, 0x52, 0x95],
    'POWERPNT.EXE': [0xd0, 0x43, 0x24],
    'EXCEL.EXE': [0x1e, 0x6c, 0x41],
    'WindowsTerminal.exe': [0xcc, 0xcc, 0xcc],
}

def isChromaProgramRunning():
    running = Win.enumWindows().values()
    for item in running:
        if item[2] in ChromaExeList:
            return True
    return False

def getForegroundCustomColor():
    current = Win.getForegroundWindow()[2]
    if current in CustomExeList:
        return CustomExeList[current]
    return None

def smooth(v1, v2, alpha):
    return v1 * (1 - alpha) + v2 * alpha

class ChromaHandler:
    def __init__(self):
        self._t = time.time()
        self._last = [0, 0, 0]
        self._keyboard = CTX12E4.create()
        self._winColor = [0, 0, 0, 0]
        self._lock = Lock()
        self._end = False
        self._open()

    def __del__(self):
        self.close()

    def close(self):
        if self._end:
            return
        self._end = True
        self._thread.join()

    def _open(self):
        def run(*args):
            while True:
                if self._end:
                    break
                time.sleep(0.5)
                self._winColor = Win.getColorizationColor()
                hasChroma = isChromaProgramRunning() or time.time() - self._t < 0.5
                # foreground > chroma > windows
                custom = getForegroundCustomColor()
                if custom:
                    self.setColor(*custom)
                elif not hasChroma:
                    _, r, g, b = self._winColor
                    h, s, v = RGB2HSV(r, g, b)
                    r, g, b = HSV2RGB(h, s, min(v * 1.1, 1))
                    self.setColor(r, g, b)

        self._thread = Thread(target=run)
        self._thread.start()

    def setColor(self, r, g, b):
        if self._keyboard:
            self._lock.acquire()
            self._keyboard.setQMKColorRGB(r, g, b)
            self._lock.release()

    def update(self, colors):
        r, g, b = list(map(lambda *a: sum(a) / len(a), *colors))
        h, s, v = RGB2HSV(r, g, b)
        h0, s0, v0 = self._last
        # smooth color
        h = smooth(h0, h, 0.2)
        s = smooth(s0, s, 0.2)
        v = smooth(v0, v * 0.3 + 0.3, 0.5)
        self._last = [h, s, v]
        self.setColor(*HSV2RGB(h, s, v))

    def handle(self, colors):
        # 30Hz => 10Hz
        t = time.time()
        if t - self._t < 0.1:
            return
        self._t = t
        if not getForegroundCustomColor():
            self.update(colors)

def main():
    # Ctrl+C to exit
    hdl = ChromaHandler()
    conn = Device.DeviceConnector(Device.Chromalink, hdl.handle)
    conn.start()
    conn.close()
    hdl.close()

if __name__ == '__main__':
    main()
    print('end')
