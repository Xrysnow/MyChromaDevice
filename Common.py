from enum import Enum
import math

class EFFECTYPE(Enum):
    EFFECT_NONE = 0
    EFFECT_WAVE = 1
    EFFECT_SPECTRUM_CYCLING = 2
    EFFECT_BREATHING = 3
    EFFECT_BLINKING = 4
    EFFECT_REACTIVE = 5
    EFFECT_STATIC = 6
    EFFECT_CUSTOM = 7
    EFFECT_CUSTOM2 = 8
    EFFECT_INIT = 9
    EFFECT_UNINIT = 10
    EFFECT_DEFAULT = 11
    EFFECT_STARLIGHT = 12
    EFFECT_SUSPEND = 13
    EFFECT_RESUME = 14
    EFFECT_INVALID = 15
    EFFECT_ACTIVE = 16
    EFFECT_VISUALIZER = 17

wsUri = 'ws://127.0.0.1:6789/razer/rzchromaemulator/'
wsBlade = '48DB6D85-B06B-40BE-A0C9-422C58E294C2'
wsKeyboard = '3BCB6007-D288-4238-8F23-98791A18A81D'
wsMouse = 'B3F86D5B-D749-4BE9-986D-9B049BCD4BBA'
wsMousepad = '8F481E4D-F8B9-451E-A531-E8FD0EE4A1B2'
wsKeypad = 'F7D505DB-49EC-4A39-971F-02B18382177E'
wsHeadset = '6E9CE40B-822B-4AB3-8043-9E2771E6E1CF'
wsChromalink = 'DB34A221-889A-43CB-B078-2776AAD0B137'

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
