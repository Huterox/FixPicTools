# import sys
# if sys.platform =="win32":
#     print("yes")

import tkinter
from PIL import ImageTk 
 
win = tkinter.Tk()
win.title("软件小组")
icon = ImageTk.PhotoImage(file="media/tubioa.ico")
win.tk.call('wm', 'iconphoto', win._w, icon)
win.geometry("400x400+400+200")
win.mainloop()