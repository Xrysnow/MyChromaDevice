import win32api, win32gui
import ctypes

DWORD = ctypes.c_uint32
BOOL = ctypes.c_uint32
Dwmapi = ctypes.windll.LoadLibrary('Dwmapi.dll')
User32 = ctypes.windll.LoadLibrary('User32.dll')
Kernel32 = ctypes.windll.LoadLibrary('Kernel32.dll')
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

def _getPID(hwnd):
    pid = DWORD()
    tid = User32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid

def _openProcess(pid):
    if isinstance(pid, int):
        pid = DWORD(pid)
    try:
        hdl = Kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, BOOL(0), pid)
        return hdl
    except Exception as e:
        return 0

def _getProcessImageName(hdl):
    if hdl == 0:
        return None
    size = 1024
    lpdwSize = DWORD(size)
    buf = ctypes.create_string_buffer(size)
    ok = Kernel32.QueryFullProcessImageNameA(hdl, DWORD(0), buf, ctypes.byref(lpdwSize))
    if ok == 0:
        return None
    return ctypes.string_at(buf, lpdwSize.value).decode('mbcs')

def _getExeNameFromHWND(hwnd):
    pid = _getPID(hwnd)
    fullpath = _getProcessImageName(_openProcess(pid))
    name = fullpath.split('\\')[-1] if fullpath is not None else None
    return name

def hasWindow(name):
    hwnd = win32gui.FindWindow(None, name)
    return hwnd != 0

_CNameFilter = ['IME', 'MSCTFIME UI', 'tooltips_class32', 'TPUtilWindow', 'WorkerW']

def _getHWNDInfo(hwnd):
    if hwnd == 0:
        return None
    try:
        cname = win32gui.GetClassName(hwnd)
    except Exception as e:
        return None
    text = win32gui.GetWindowText(hwnd)
    name = _getExeNameFromHWND(hwnd)
    return cname, text, name

def _enumCallback(hwnd, d):
    info = _getHWNDInfo(hwnd)
    if info and not info[0] in _CNameFilter:
        d[hwnd] = [*info]

def enumWindows():
    d = {}
    win32gui.EnumWindows(_enumCallback, d)
    return d

def getForegroundWindow():
    hwnd = win32gui.GetForegroundWindow()
    info = _getHWNDInfo(hwnd)
    if info:
        return [*info]
    return [None, None, None]

def getColorizationColor():
    pcrColorization = DWORD()
    pfOpaqueBlend = BOOL()
    result = Dwmapi.DwmGetColorizationColor(
        ctypes.byref(pcrColorization),
        ctypes.byref(pfOpaqueBlend))
    if result == 0:
        color = pcrColorization.value
        b = color & 0xff
        g = color >> 8 & 0xff
        r = color >> 16 & 0xff
        a = color >> 24 & 0xff
        return [a, r, g, b]
    else:
        print('DwmGetColorizationColor failed')
        return [0, 0, 0, 0]
