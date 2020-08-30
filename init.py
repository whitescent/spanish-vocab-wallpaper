import win32api, win32con

from PIL import Image

x = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)  # 获得屏幕分辨率X轴
y = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)  # 获得屏幕分辨率Y轴


def SetImgPixel(width, height, pic):
    for i in range(width):
        for k in range(height):
            color = pic.getpixel((i, k))
            color = color[:-1] + (100,)
            pic.putpixel((i, k), color)


img = Image.open(r'C:\Users\Anteayer\Documents\Misc\wall.jpg')
x, y = img.size

BlackTrans = Image.new("RGBA", (x, y), "Black")
x1, y1 = BlackTrans.size
SetImgPixel(x1, y1, BlackTrans)

img.paste(BlackTrans, (0, 0), BlackTrans)
img.save(r'C:\Users\Anteayer\Desktop\txt.png')