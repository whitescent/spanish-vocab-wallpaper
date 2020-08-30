from draw import *
import ctypes
import win32gui, win32api, win32con

'''         # 准备解决重启 explorer.exe 之后无法绘制 WorkerW 的问题，但是仍然还没有解决
def _EnumWindowsProc(a, b):
    shit = ctypes.create_unicode_buffer(64)
    shit = win32gui.GetClassName(a)
    if shit == "WorkerW":
        print(win32gui.SendMessage(a, 0x052C, 4, 0))

    return True
'''

def main():
    renderWallpaper()


if __name__ == '__main__':
    main()
