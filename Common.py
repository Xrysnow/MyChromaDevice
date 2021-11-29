from enum import Enum

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