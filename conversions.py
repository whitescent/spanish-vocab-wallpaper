import threading
import ctypes
from sentence import *
from option import *

# 将一些 Win32 API 会用到的结构体用 python 的方式描述


class RAWINPUTDEVICE(ctypes.Structure):
    _fields_ = [
        ("usUsagePage", ctypes.c_ushort),
        ("usUsage", ctypes.c_ushort),
        ("dwFlags", ctypes.c_long),
        ("hwndTarget", ctypes.c_void_p)
    ]


class RAWMOUSE_DUMMYSTRUCTNAME(ctypes.Structure):
    _fields_ = [
        ("usButtonFlags", ctypes.c_ushort),
        ("usButtonData", ctypes.c_ushort)
    ]


class RAWMOUSE_DUMMYUNIONNAME(ctypes.Union):
    _fields_ = [
        ("ulButtons", ctypes.c_ulong),
        ("DUMMYSTRUCTNAME", RAWMOUSE_DUMMYSTRUCTNAME)
    ]


class RAWMOUSE(ctypes.Structure):
    _fields_ = [
        ("usFlags", ctypes.c_ushort),
        ("DUMMYUNIONNAME", RAWMOUSE_DUMMYUNIONNAME),
        ("ulRawButtons", ctypes.c_ulong),
        ("lLastX", ctypes.c_long),
        ("lLastY", ctypes.c_long),
        ("ulExtraInformation", ctypes.c_ulong)
    ]


class RAWINPUTHEADER(ctypes.Structure):
    _fields_ = [
        ("dwType", ctypes.c_ulong),
        ("dwSize", ctypes.c_ulong),
        ("hDevice", ctypes.c_void_p),
        ("wParam", ctypes.c_ulong)
    ]


class RAWINPUT_DATA(ctypes.Union):
    _fields_ = [
        ("mouse", RAWMOUSE)
    ]


class RAWINPUT(ctypes.Structure):
    _fields_ = [
        ("header", RAWINPUTHEADER),
        ("data", RAWINPUT_DATA)
    ]


# 将 python 获取的词库通过 CEF 的方法传输给 JS 函数并进行调用
class LoadHandler:

    # 当网页加载完毕时执行
    def OnLoadEnd(self, browser, frame, http_code):
        threading.Thread(target=LoadHandler._sbpython, args=(browser,)).start()   # 在别的线程加载词库

    @staticmethod
    def _sbpython(browser):
        browser.ExecuteFunction("loadWords", getWords())
        sen, trans = getSentence()
        browser.ExecuteFunction("loadSentence", sen, trans)



