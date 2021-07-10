import sys
from PIL import Image
import os
from queue import Queue

if sys.platform=="win32":
    from win32 import win32api, win32gui, win32print
    from win32.lib import win32con

    from win32.win32api import GetSystemMetrics

class ChangeRealSize(object):
    '''

    该类主要对屏幕进行像素适配，按照缩放比对像素进行换算为100%显示
    示例：
    RealSize = ChangeRealSize()
    x=RealSize.getreal_xy(500)
    此时就可以换算为当前屏幕的像素

    '''


    def get_real_resolution(self):
        """获取真实的分辨率"""
        hDC = win32gui.GetDC(0)
        w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
        h = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
        return w, h


    def get_screen_size(self):
        """获取缩放后的分辨率"""
        w = GetSystemMetrics (0)
        h = GetSystemMetrics (1)


        return w, h


    def getreal_xy(self,x):
        '''返回按照100%来算的真实的像素值'''
        real_resolution = self.get_real_resolution()
        screen_size = self.get_screen_size()
        screen_scale_rate = round(real_resolution[0] / screen_size[0], 2)
        try:
            x = x/screen_scale_rate
        except:
            #对笔记本进行适配，一般而言在100%比的机器上x不会出错
            x=1.25
        return int(x)

class Tools(object):
    def __init__(self):
        self.RealSize = ChangeRealSize()

    def CHANGESIZE_One(self,path,x,y,save=".\media\Out_Image.png"):
        #不传递save为单图模式，默认是单图模式的所以函数名字就是单图模式
        image = Image.open(path)
        if sys.platform=="win32":
            image = image.resize((self.RealSize.getreal_xy(x),self.RealSize.getreal_xy(y)), Image.ANTIALIAS)
        else:
            image = image.resize((x,y), Image.ANTIALIAS)
        image.save(save)


        pass
    def ERZHIHUA_One(self,path,save=".\media\Out_Image.png"):
        image = Image.open(path)
        image = image.convert('L')
        t = []
        for i in range(256):
            # 杂质越多,值越大(轮廓越黑越明显)
            if i < 120:  # 160
                t.append(0)
            else:
                t.append(1)

        image = image.point(t, '1')

        image.save(save)

    def DANSHANGSE_One(self,path,RGB,save=".\media\Out_Image.png"):
        if save==".\media\Out_Image.png":
            self.ERZHIHUA_One(path)  # 执行二值化
            path = r'{}'.format(os.path.dirname((os.path.abspath(__file__)))) + '\media\Out_Image.png'
            image = Image.open(path)
            image = image.convert("RGB")
            width = image.size[0]
            height = image.size[1]
            new_image = Image.new("RGB", (width, height))
            for x in range(width):
                for y in range(height):
                    r, g, b = image.getpixel((x, y))
                    rgb = (r, g, b)

                    if rgb == (0, 0, 0):
                        rgb = RGB
                    new_image.putpixel((x, y), (int(rgb[0]), int(rgb[1]), int(rgb[2])))  # 画图
            new_image.save(path)
        else:
            self.ERZHIHUA_One(path,save)  # 执行二值化
            path = save
            image = Image.open(path)
            image = image.convert("RGB")
            width = image.size[0]
            height = image.size[1]
            new_image = Image.new("RGB", (width, height))
            for x in range(width):
                for y in range(height):
                    r, g, b = image.getpixel((x, y))
                    rgb = (r, g, b)

                    if rgb == (0, 0, 0):
                        rgb = RGB
                    new_image.putpixel((x, y), (int(rgb[0]), int(rgb[1]), int(rgb[2])))  # 画图
            new_image.save(path)

    def LUNKUO_One(self,path,save=".\media\Out_Image.png"):
        if save==".\media\Out_Image.png":

            self.ERZHIHUA_One(path)#执行二值化
            path = r'{}'.format(os.path.dirname((os.path.abspath(__file__))))+'\media\Out_Image.png'
            image = Image.open(path)
            image = image.convert("RGB")
            new_img = Image.new("RGB", (image.size[0], image.size[1]))
            for x in range(image.size[0]):
                for y in range(image.size[1]):
                    r, g, b = image.getpixel((x, y))
                    rgb = (r, g, b)
                    if rgb != (255, 255, 255):
                        if y > 2 and y < image.size[1] - 3:
                            r1, g1, b1 = image.getpixel((x, y - 3))
                            rgb1 = (r1, g1, b1)
                            r2, g2, b2 = image.getpixel((x, y + 3))
                            rgb2 = (r2, g2, b2)
                            if rgb1 == (255, 255, 255) and rgb == (0,0,0) and rgb2 == (0,0,0):
                                rgb = (0,0,0)
                            elif rgb1 == (0,0,0) and rgb == (0,0,0) and rgb2 == (255, 255, 255):
                                rgb = (0,0,0)
                            if rgb1 == (0,0,0) and rgb == (0,0,0) and rgb2 == (0,0,0):
                                rgb = (255, 255, 255)

                    new_img.putpixel((x, y), (int(rgb[0]), int(rgb[1]), int(rgb[2])))

            new_img.save(path)

        else:
            self.ERZHIHUA_One(path,save)  # 执行二值化
            path = save
            image = Image.open(path)
            image = image.convert("RGB")
            new_img = Image.new("RGB", (image.size[0], image.size[1]))
            for x in range(image.size[0]):
                for y in range(image.size[1]):
                    r, g, b = image.getpixel((x, y))
                    rgb = (r, g, b)
                    if rgb != (255, 255, 255):
                        if y > 2 and y < image.size[1] - 3:
                            r1, g1, b1 = image.getpixel((x, y - 3))
                            rgb1 = (r1, g1, b1)
                            r2, g2, b2 = image.getpixel((x, y + 3))
                            rgb2 = (r2, g2, b2)
                            if rgb1 == (255, 255, 255) and rgb == (0, 0, 0) and rgb2 == (0, 0, 0):
                                rgb = (0, 0, 0)
                            elif rgb1 == (0, 0, 0) and rgb == (0, 0, 0) and rgb2 == (255, 255, 255):
                                rgb = (0, 0, 0)
                            if rgb1 == (0, 0, 0) and rgb == (0, 0, 0) and rgb2 == (0, 0, 0):
                                rgb = (255, 255, 255)

                    new_img.putpixel((x, y), (int(rgb[0]), int(rgb[1]), int(rgb[2])))

            new_img.save(path)



if __name__=="__main__":
    if sys.platform=="win32":
        RealSize = ChangeRealSize()
        x=RealSize.getreal_xy(250)
        print(x)
    else:
        print("there is not windows can not run this code")