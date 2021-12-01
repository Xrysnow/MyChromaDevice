import websocket
import json
import time
import Common
from Common import EFFECTYPE
from threading import Thread

class Device:
    @staticmethod
    def getAddress():
        raise RuntimeError()

    @staticmethod
    def parseEffect(type, value):
        raise RuntimeError()

    @staticmethod
    def getColors(parsed):
        raise RuntimeError()

class DeviceConnector:
    def __init__(self, device: Device, handler=None):
        self._handler = handler
        self._end = False
        self._device = device
        self._addr = device.getAddress()
        self._ws = websocket.WebSocketApp(self._addr,
                                          on_message=self._on_message,
                                          on_error=self._on_error,
                                          on_close=self._on_close)
        self._ws.on_open = self._on_open

    def __del__(self):
        self.close()

    def start(self):
        self._ws.run_forever()

    def close(self):
        if self._end:
            return
        self._end = True
        self._thread.join()

    def _on_error(self, ws, error):
        print(error)

    def _on_close(self, ws, status_code, msg):
        print("closed:", self._device)

    def _on_message(self, ws, message):
        if not self._handler:
            return
        msg = json.loads(message)
        if 'type' in msg:
            type = msg.get('type')
            value = msg.get('value')
            parsed = self._device.parseEffect(type, value)
            colors = self._device.getColors(parsed)
            self._handler(colors)

    def _on_open(self, ws):
        print('connected:', self._device)
        payload = {'func': "Init"}
        msg = json.dumps(payload)
        ws.send(msg)

        def run(*args):
            while True:
                time.sleep(1)
                if self._end:
                    break
            ws.close()

        self._thread = Thread(target=run)
        self._thread.start()

def _parse_rgb(v):
    # reversed
    b = v >> 16 & 0xff
    g = v >> 8 & 0xff
    r = v & 0xff
    return [r, g, b]

DEFAULT_COLOR = [0, 0, 0]

class Blade(Device):
    MAX_ROW = 6
    MAX_COL = 22
    MAX_LED = 80
    LEDMapping = [
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
        22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
        45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58,
        66, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 81,
        89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101,
        110, 111, 112, 113, 116, 119, 120, 121, 122, 123, 124
    ]
    KeyNames = [
        "Esc", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "Insert", "Delete", "Tilde",
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "Dash", "Equal", "Backspace", "Tab", "Q", "W", "E", "R", "T",
        "Y", "U", "I", "O", "P", "StartSquareBracket", "EndSquareBracket", "Backslash", "Caps", "A", "S", "D", "F", "G",
        "H", "J", "K", "L", "SemiColon", "Apostrophe", "Enter", "LeftShift", "Z", "X", "C", "V", "B", "N", "M", "Comma",
        "Dot", "ForwardSlash", "UpArrow", "RightShift", "LeftCtrl", "LeftFunction", "Window", "LeftAlt", "Space",
        "RightAlt", "RightCtrl", "LeftArrow", "DownArrow", "RightArrow", "RightFunction"
    ]

    @staticmethod
    def getAddress():
        return Common.wsUri + Common.wsBlade

    @staticmethod
    def parseEffect(type, value):
        if not value:
            return []
        ledArray = []
        ledArraySize = 1
        if type in [EFFECTYPE.EFFECT_CUSTOM,
                    EFFECTYPE.EFFECT_CUSTOM2,
                    EFFECTYPE.EFFECT_VISUALIZER]:
            ledArraySize = Blade.MAX_ROW * Blade.MAX_COL
            assert len(value) == ledArraySize
        for i in range(ledArraySize):
            ledArray.append(_parse_rgb(value[i]))
        return ledArray

    @staticmethod
    def getColors(parsed):
        ''' 80 LEDs '''
        if len(parsed) == 1:
            return parsed * Blade.MAX_LED
        elif len(parsed) == Blade.MAX_ROW * Blade.MAX_COL:
            colors = [DEFAULT_COLOR] * Blade.MAX_LED
            for i in range(Blade.MAX_LED):
                mapped = Blade.LEDMapping[i]
                if mapped >= 0:
                    colors[i] = parsed[mapped]
            return colors
        return [DEFAULT_COLOR] * Blade.MAX_LED

class Chromalink(Device):
    MAX_LED = 5

    @staticmethod
    def getAddress():
        return Common.wsUri + Common.wsChromalink

    @staticmethod
    def parseEffect(type, value):
        if not value:
            return []
        ledArray = []
        ledArraySize = 1
        if type == EFFECTYPE.EFFECT_CUSTOM:
            ledArraySize = Chromalink.MAX_LED
            assert len(value) == ledArraySize
        for i in range(ledArraySize):
            ledArray.append(_parse_rgb(value[i]))
        return ledArray

    @staticmethod
    def getColors(parsed):
        ''' circle, dot*4 '''
        if len(parsed) == 1:
            return parsed * Chromalink.MAX_LED
        elif len(parsed) == Chromalink.MAX_LED:
            return parsed
        return [DEFAULT_COLOR] * Chromalink.MAX_LED

class Headset(Device):
    ''' Nari '''
    MAX_LED = 2

    @staticmethod
    def getAddress():
        return Common.wsUri + Common.wsHeadset

    @staticmethod
    def parseEffect(type, value):
        if not value:
            return []
        ledArray = []
        ledArraySize = 1
        if type == EFFECTYPE.EFFECT_CUSTOM:
            ledArraySize = Headset.MAX_LED
            assert len(value) == ledArraySize
        for i in range(ledArraySize):
            ledArray.append(_parse_rgb(value[i]))
        return ledArray

    @staticmethod
    def getColors(parsed):
        ''' left, right '''
        if len(parsed) == 1:
            return parsed * Headset.MAX_LED
        elif len(parsed) == Headset.MAX_LED:
            return parsed
        return [DEFAULT_COLOR] * Headset.MAX_LED

class Keyboard(Device):
    ''' Huntsman Elite '''
    MAX_ROW = 6
    MAX_COL = 22
    MAX_LED = 164
    LEDMapping = [
        -1, -1, 1, 3, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 17, 43, 23, 43,
        45, 65, 67, 65, 111, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 109,
        1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 23, 24, 25, 26,
        27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54,
        55, 56, 57, 58, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 80, 89, 91, 92,
        93, 94, 95, 96, 97, 98, 99, 100, 102, 111, 112, 113, 117, 121, 122, 123, 124, 37, 38, 39,
        59, 60, 61, 104, 125, 126, 127, 40, 41, 42, 43, 62, 63, 64, 65, 84, 85, 86, 106, 107,
        108, 109, 129, 130, 111, 109, 111, 109, 111, 113, 113, 117, 117, 117, 117, 121, 123, 124, 125, 126,
        127, 129, 129, 109
    ]

    @staticmethod
    def getAddress():
        return Common.wsUri + Common.wsKeyboard

    @staticmethod
    def parseEffect(type, value):
        if not value:
            return []
        ledArray = []
        ledArraySize = 1
        if type in [EFFECTYPE.EFFECT_CUSTOM,
                    EFFECTYPE.EFFECT_CUSTOM2,
                    EFFECTYPE.EFFECT_VISUALIZER]:
            ledArraySize = Keyboard.MAX_ROW * Keyboard.MAX_COL
            assert len(value) == ledArraySize
        for i in range(ledArraySize):
            ledArray.append(_parse_rgb(value[i]))
        return ledArray

    @staticmethod
    def getColors(parsed):
        ''' 164 LEDs, 1~2: Media, 3~40: Underglow, 41~144: Keys, 145~164: Wrist '''
        if len(parsed) == 1:
            return parsed * Keyboard.MAX_LED
        elif len(parsed) == Keyboard.MAX_ROW * Keyboard.MAX_COL:
            colors = [DEFAULT_COLOR] * Keyboard.MAX_LED
            for i in range(Keyboard.MAX_LED):
                mapped = Keyboard.LEDMapping[i]
                if mapped >= 0:
                    colors[i] = parsed[mapped]
            return colors
        return [DEFAULT_COLOR] * Keyboard.MAX_LED

class Keypad(Device):
    ''' Tartarus V2 '''
    MAX_ROW = 4
    MAX_COL = 5
    MAX_LED = 21
    LEDMapping = [
        0, 1, 2, 3, 4,
        5, 6, 7, 8, 9,
        10, 11, 12, 13, 14,
        15, 16, 17, 18, 19, 19
    ]

    @staticmethod
    def getAddress():
        return Common.wsUri + Common.wsKeypad

    @staticmethod
    def parseEffect(type, value):
        if not value:
            return []
        ledArray = []
        ledArraySize = 1
        if type == EFFECTYPE.EFFECT_CUSTOM:
            ledArraySize = Keypad.MAX_ROW * Keypad.MAX_COL
            assert len(value) == ledArraySize
        for i in range(ledArraySize):
            ledArray.append(_parse_rgb(value[i]))
        return ledArray

    @staticmethod
    def getColors(parsed):
        ''' 21 LEDs, 1~19: Keys, 20: Scrollwheel, 21: Key '''
        if len(parsed) == 1:
            return parsed * Keypad.MAX_LED
        elif len(parsed) == Keypad.MAX_ROW * Keypad.MAX_COL:
            colors = [DEFAULT_COLOR] * Keypad.MAX_LED
            for i in range(Keypad.MAX_LED):
                mapped = Keypad.LEDMapping[i]
                if mapped >= 0:
                    colors[i] = parsed[mapped]
            return colors
        return [DEFAULT_COLOR] * Keypad.MAX_LED

class Mouse(Device):
    ''' Lancehead '''
    LED_ARRAY_SIZE = 63
    MAX_LED = 16
    LEDMapping = [
        7, 17, 13, 14, 20, 21, 27, 28, 34, 35, 41, 42, 48, 49, 55, 52
    ]

    @staticmethod
    def getAddress():
        return Common.wsUri + Common.wsMouse

    @staticmethod
    def parseEffect(type, value):
        if not value:
            return []
        ledArray = []
        ledArraySize = 1
        if type in [EFFECTYPE.EFFECT_CUSTOM,
                    EFFECTYPE.EFFECT_CUSTOM2]:
            ledArraySize = Mouse.LED_ARRAY_SIZE
            assert len(value) == ledArraySize
        for i in range(ledArraySize):
            ledArray.append(_parse_rgb(value[i]))
        return ledArray

    @staticmethod
    def getColors(parsed):
        ''' 16 LEDs '''
        if len(parsed) == 1:
            return parsed * Mouse.MAX_LED
        elif len(parsed) == Mouse.LED_ARRAY_SIZE:
            colors = [DEFAULT_COLOR] * Mouse.MAX_LED
            for i in range(Mouse.MAX_LED):
                mapped = Mouse.LEDMapping[i]
                if mapped >= 0:
                    colors[i] = parsed[mapped]
            return colors
        return [DEFAULT_COLOR] * Mouse.MAX_LED

class Mousepad(Device):
    ''' Firefly '''
    MAX_LED = 20

    @staticmethod
    def getAddress():
        return Common.wsUri + Common.wsMousepad

    @staticmethod
    def parseEffect(type, value):
        if not value:
            return []
        ledArray = []
        ledArraySize = 1
        if type == EFFECTYPE.EFFECT_CUSTOM:
            ledArraySize = Mousepad.MAX_LED
            assert len(value) == ledArraySize
        for i in range(ledArraySize):
            ledArray.append(_parse_rgb(value[i]))
        return ledArray

    @staticmethod
    def getColors(parsed):
        ''' 20LEDs '''
        if len(parsed) == 1:
            return parsed * Mousepad.MAX_LED
        elif len(parsed) == Mousepad.MAX_LED:
            return parsed
        return [DEFAULT_COLOR] * Mousepad.MAX_LED
