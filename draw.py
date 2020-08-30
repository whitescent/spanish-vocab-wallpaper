import sys
import os
import win32gui, win32api, win32con
from cefpython3 import cefpython as cef
from conversions import *

# Windows 桌面相关句柄
_workerw = 0
_defview = 0
_syslistview = 0

# CEF 浏览器相关窗口句柄
_handle = 0
_widget = 0
_legacy = 0

_wndproc0 = 0               # CEF 浏览器原本的事件处理函数
_screenSize = [0, 0]        # 屏幕分辨率
_cursorAtDesktop = False    # 鼠标是否位于桌面区域
_lastCursorAtDesktop = False
_lastMousePos = [0, 0]      # 鼠标上次所在的屏幕坐标（暂时没啥用）


def _EnumWindowsProc(a, b):
    global _workerw, _defview, _syslistview
    _defview = win32gui.FindWindowEx(a, 0, "SHELLDLL_DefView", None)
    if _defview != 0:
        _workerw = win32gui.FindWindowEx(0, a, "WorkerW", None)
        _syslistview = win32gui.FindWindowEx(_defview, 0, "SysListView32", None)

    return True


def _GetWorkerW():
    progman = win32gui.FindWindow("Progman", None)
    win32gui.SendMessageTimeout(progman, 0x052C, 0, 0, win32con.SMTO_NORMAL, 0x3E8)
    win32gui.EnumWindows(_EnumWindowsProc, None)
    win32gui.ShowWindow(_workerw, win32con.SW_HIDE)

    return progman


def _InputHandler(hwnd, msg, wparam, lparam):
    global _lastCursorAtDesktop, _cursorAtDesktop, _lastMousePos

    # 避免 Windows 10 自动发送鼠标离开的消息，从而无法触发浏览器的 hover
    if msg == win32con.WM_MOUSELEAVE:
        if _cursorAtDesktop:
            return False

    elif msg == 0xFF:
        dataSize = ctypes.c_ulong(0)
        ctypes.windll.user32.GetRawInputData(lparam, 0x10000003, None, ctypes.byref(dataSize),
                                             ctypes.sizeof(RAWINPUTHEADER))
        dataBuf = ctypes.create_string_buffer(dataSize.value)
        ctypes.windll.user32.GetRawInputData(lparam, 0x10000003, dataBuf, ctypes.byref(dataSize),
                                             ctypes.sizeof(RAWINPUTHEADER))
        inputData = ctypes.cast(dataBuf, ctypes.POINTER(RAWINPUT))
        if inputData.contents.header.dwType == 0:
            mouse = inputData.contents.data.mouse
            lastMousePos = win32gui.GetCursorPos()  # 获得鼠标当前所在的屏幕坐标

            # 鼠标移动的相对坐标（暂时没啥用）
            '''if mouse.usFlags & 1:
                _lastMousePos[0] = int((mouse.lLastX / 65535.0) * screenSize[0])
                _lastMousePos[1] = int((mouse.lLastY / 65535.0) * screenSize[1])
            else:
                _lastMousePos[0] += mouse.lLastX
                _lastMousePos[1] += mouse.lLastY'''

            # 获得鼠标当前指向的窗口句柄
            cursorAt = win32gui.WindowFromPoint((lastMousePos[0], lastMousePos[1]))

            # 检测到鼠标指向的是桌面（桌面显示图标时是 _syslistview，隐藏图标时是 _defview）
            _cursorAtDesktop = (cursorAt == _defview or cursorAt == _syslistview)
            if _cursorAtDesktop:
                win32gui.PostMessage(_legacy, win32con.WM_MOUSEMOVE, 0, (lastMousePos[1] << 16) | lastMousePos[0])
            elif _lastCursorAtDesktop and not _cursorAtDesktop:
                win32gui.PostMessage(hwnd, win32con.WM_MOUSELEAVE, 0, 0)
            _lastCursorAtDesktop = _cursorAtDesktop

    return win32gui.CallWindowProc(_wndproc0, hwnd, msg, wparam, lparam)


'''
# 复制当前壁纸到网页所在目录，并命名为 background（无后缀）
wallpaperPathBuf = ctypes.create_unicode_buffer(win32con.MAX_PATH)
ctypes.windll.user32.SystemParametersInfoW(0x73, win32con.MAX_PATH, ctypes.byref(wallpaperPathBuf), 0)
wallpaperPath = wallpaperPathBuf.value
shutil.copyfile(wallpaperPath, os.getcwd() + "/Website/background")
'''

def renderWallpaper():
    global _handle, _widget, _legacy, _cursorAtDesktop, _wndproc0

    sys.excepthook = cef.ExceptHook  # 替换python预定义异常处理逻辑，为保证异常发生时能够结束所有进程
    cef.Initialize(
        settings={},
        switches={"disable-gpu-compositing": None}  # 添加了用于解决高 DPI 问题的参数
    )

    # 启用 CEF 高 DPI 支持
    cef.DpiAware.EnableHighDpiSupport()

    # 初始化 CEF 浏览器，并设置加载完毕的事件处理代码
    broswer = cef.CreateBrowserSync(url="file:///" + os.getcwd() + "/Website/website.html")
    broswer.SetClientHandler(LoadHandler())

    # 获得与 CEF 浏览器有关的窗口句柄 (句柄名在 Spy++ 中查找的)
    _handle = broswer.GetWindowHandle()
    _widget = win32gui.FindWindowEx(_handle, 0, "Chrome_WidgetWin_0", None)
    _legacy = win32gui.FindWindowEx(_widget, 0, "Chrome_RenderWidgetHostHWND", None)

    # 获得屏幕分辨率
    _screenSize[0] = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    _screenSize[1] = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

    # 去除浏览器内核边框
    win32gui.SetWindowLong(
        _handle, win32con.GWL_STYLE,
        win32gui.GetWindowLong(_handle, win32con.GWL_STYLE)
        & ~(
            win32con.WS_CAPTION | win32con.WS_BORDER | win32con.WS_THICKFRAME
        )
    )

    # 将网页铺满全屏
    win32gui.SetWindowPos(_handle, win32con.HWND_TOP, 0, 0, _screenSize[0], _screenSize[1], win32con.SWP_NOACTIVATE)
    win32gui.SetParent(_handle, _GetWorkerW())

    # 更改 CEF 浏览器的一些行为
    _wndproc0 = win32gui.SetWindowLong(_legacy, win32con.GWL_WNDPROC, _InputHandler)
    mouseDevice = RAWINPUTDEVICE()
    mouseDevice.usUsagePage = 0x01
    mouseDevice.usUsage = 0x02
    mouseDevice.dwFlags = 0x100
    mouseDevice.hwndTarget = _legacy
    ctypes.windll.user32.RegisterRawInputDevices(ctypes.byref(mouseDevice), 1, ctypes.sizeof(mouseDevice))

    cef.MessageLoop()   # 正式启动浏览器

    cef.Shutdown()  # 浏览器关闭后释放资源

