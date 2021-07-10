import tkinter as tk
from tkinter import ttk
import time,base64,tkinter.filedialog as filedialog
import tkinter.colorchooser as colorchooser,shutil
from PIL import Image,ImageTk
from Tools import Tools
import os,threading,tkinter.filedialog,tkinter.messagebox
from queue import Queue

GetRelXY = lambda x:x/600#相对布局换算默认600x600开始换算
Tools = Tools()
class Window():
    def __init__(self):
        self.win = tk.Tk()
        self.win.title("改图宝")
        self.win.geometry("600x600")
        self.win.iconbitmap(r".\media\tubioa.ico")
        self.win['background']='white'

        self.Top_menu = tk.Menu(self.win)

        self.Top_menu_G = tk.Menu(self.win,tearoff=0,activebackground="Aqua",font=("宋体",10))
        self.Top_menu_G.add_command(label="单图模式",command=self.Mode_One)
        self.Top_menu_G.add_separator()
        self.Top_menu_G.add_command(label="批量处理",command=self.Mode_Many)
        self.Top_menu_G.add_separator()
        self.Top_menu_G.add_command(label="退出",command=self.win.quit)

        self.Top_menu.add_cascade(label="模式选择",menu=self.Top_menu_G)

        self.win.config(menu=self.Top_menu)#顶栏字体不能改

        self.Select_Img=None #在单图模式下被选中的图片
        self._image_select_path=None
        self.Out_Image_Path =None#单图模式下的输出图片路径

        self.__sss_W_()

        self.Select_Path=None #在批量模式下被选择的路径
        self.Check_Mode=tk.IntVar(value=1)

        #修改图片的复选框的变量，这个应该和线程在一块，其他的是radiobutton才对
        self.Check_Change_size=tk.IntVar()

        #图片提取处理
        self.Check_Radio_change=tk.IntVar()

        self.DanShangSe_color_rgb=(50,205,50) #单上色的颜色,默认绿色


        #线程数和线程的设置

        self.Thread_do_number=3#默认3个线程

            #相关设置
        self.Thread_number = tk.IntVar()
        self.Thread_listbox_l = ttk.Combobox(self.win, textvariable=self.Thread_number)
        self.Thread_listbox_l["values"] = (1, 2, 3, 4, 5)
        self.Thread_listbox_l.current(0)
        self.Thread_listbox_l.bind("<<ComboboxSelected>>", self.__set_thread_number)
        self.Thread_number.set(3)
        self.Thread_do_number = int(self.Thread_number.get())

            #2相关设置
        self.Thread_tips = tk.Label(self.win,bg='white',text="线程选择")

        #批量模式下的listbox

        self.Image_many_show_path_list=[]#显示的路径（图片）

        self.Many_Show_List_box_Sc=tk.Scrollbar(self.win)
            #绑定滑块
        self.Many_Show_List_box=tk.Listbox(self.win,yscrollcommand=self.Many_Show_List_box_Sc.set)
        self.Many_Show_List_box_Sc.config(command=self.Many_Show_List_box.yview)

            #输出的那个部分
        self.Many_Show_List_box_Sc_Out = tk.Scrollbar(self.win)
             # 绑定滑块
        self.Many_Show_List_box_Out = tk.Listbox(self.win, yscrollcommand=self.Many_Show_List_box_Sc_Out.set)
        self.Many_Show_List_box_Sc_Out.config(command=self.Many_Show_List_box_Out.yview)


        #现在是显示文件目录的时候了
        self.Select_path_queue=Queue(1000)
        self.Select_path_list=[]
        self.Save_path_Many=None #保存的目录，记住执行完毕之后需要复位
        self.Flag_Many_Ok=[]




    def Show_Label(self):

        #展示select的图片
        self.Image_show_Label=tk.Label(self.win,bg='azure',cursor="target")
        self.Image_show_Label.place(relx=GetRelXY(20),rely=GetRelXY(20),relwidth=GetRelXY(250),relheight=GetRelXY(250))
        #显示默认图片
        self.__selected_image("./media/hello.png")



        #展示Out输出
        self.Image_Out_show = tk.Label(self.win,font=("宋体",10),text='输出结果:',bg='white',cursor="cross")
        self.Image_Out_show.place(relx=GetRelXY(310), rely=GetRelXY(250), relwidth=GetRelXY(80),
                                    relheight=GetRelXY(40))
        self.Image_Out_show = tk.Label(self.win, bg='azure', cursor="cross")
        self.Image_Out_show.place(relx=GetRelXY(310), rely=GetRelXY(310), relwidth=GetRelXY(280),
                                    relheight=GetRelXY(280))

    def Button_show(self):

        #选择图片或者处理目录
        self.Select_Image_P=tk.Button(self.win,font=('宋体', 10),
                                      relief='ridge',bg='white',
                                      activebackground="steelblue",
                                      )
        self.Select_Image_P.place(relx=GetRelXY(320),rely=GetRelXY(60),relwidth=GetRelXY(150),relheight=GetRelXY(50))

        self.Select_Image_P.config(text='选择图片', command=self.__selected_image)

        #保存
        self.Save_Image_P=tk.Button(self.win,font=('宋体', 10),
                                      relief='ridge',bg='white',
                                      activebackground="steelblue",
                                      command = self.__save_image_one_#默认单图模式
                                      )
        self.Save_Image_P.place(relx=GetRelXY(320),rely=GetRelXY(160),relwidth=GetRelXY(150),relheight=GetRelXY(50))

        self.Save_Image_P.config(text='保存图片')


        #模式选择（RadioButton)

        self.RadioOneMode = tk.Radiobutton(self.win,text="单图模式",variable=self.Check_Mode,value=1,
                                           font=('宋体', 10),
                                           activebackground="steelblue",
                                           command=self.Mode_One,
                                           bg='white'


                                           )
        self.RadioOneMode.place(relx=GetRelXY(480),rely=GetRelXY(80),relwidth=GetRelXY(100),relheight=GetRelXY(40))

        self.RadioOneMode = tk.Radiobutton(self.win,text="批量处理",variable=self.Check_Mode,value=2,
                                           font=('宋体', 10),
                                           activebackground="steelblue",
                                           command=self.Mode_Many,
                                           bg='white'
                                           )
        self.RadioOneMode.place(relx=GetRelXY(480),rely=GetRelXY(160),relwidth=GetRelXY(100),relheight=GetRelXY(40))

        #图片尺寸修改

        self.change_img_tips = tk.Checkbutton(self.win,bg='white',text="修改图尺寸",
                                           variable=self.Check_Change_size,
                                           activebackground="steelblue",
                                           command=self.__Get_flag_change_size

                                           )
        self.change_img_tips.place(relx=GetRelXY(10),rely=GetRelXY(290),relwidth=GetRelXY(100),relheight=GetRelXY(25))

        self.change_img_x = tk.Entry(self.win,bg='azure')
        self.change_img_x.place(relx=GetRelXY(100),rely=GetRelXY(290),relwidth=GetRelXY(35),relheight=GetRelXY(25))

        self.change_img_tip_cen = tk.Label(self.win,bg='white',text="X"
                               )
        self.change_img_tip_cen.place(relx=GetRelXY(135),rely=GetRelXY(290),relwidth=GetRelXY(20),relheight=GetRelXY(25))

        self.change_img_y = tk.Entry(self.win,bg='azure')
        self.change_img_y.place(relx=GetRelXY(155),rely=GetRelXY(290),relwidth=GetRelXY(35),relheight=GetRelXY(25))

        #灰度处理图片

        self.EZHIHUA_tips = tk.Radiobutton(self.win,bg='white',text="二值化处理",

                                           variable=self.Check_Radio_change,
                                           activebackground="steelblue",
                                           command=self.__Get_flag_ERZHIHUA,
                                           value=1

                                           )
        self.EZHIHUA_tips.place(relx=GetRelXY(10),rely=GetRelXY(350),relwidth=GetRelXY(100),relheight=GetRelXY(25))


        #轮廓提取

        self.LUNKUO_tips = tk.Radiobutton(self.win,bg='white',text="图轮廓提取",

                                           variable=self.Check_Radio_change,
                                           activebackground="steelblue",
                                           command=self.__Get_flag_LUNKUO,
                                           value=2

                                           )
        self.LUNKUO_tips.place(relx=GetRelXY(10),rely=GetRelXY(400),relwidth=GetRelXY(100),relheight=GetRelXY(25))


        #单色图处理

        self.DANSE_tips = tk.Radiobutton(self.win,bg='white',text="单色图处理",

                                           variable=self.Check_Radio_change,
                                           activebackground="steelblue",
                                           command=self.__Get_flag_DANSE,
                                           value=3

                                           )
        self.DANSE_tips.place(relx=GetRelXY(10),rely=GetRelXY(450),relwidth=GetRelXY(100),relheight=GetRelXY(25))

            #单上色颜色选择器
        self.Check_color_dangshangse=tk.Button(self.win,font=('宋体', 10),
                                      relief='ridge',bg='white',
                                      activebackground="steelblue",
                                      text="单色颜色选择器",
                                      command=self.__Get_DANSE_color_set

                                      )
        self.Check_color_dangshangse.place(relx=GetRelXY(110),rely=GetRelXY(450),relwidth=GetRelXY(100),relheight=GetRelXY(30))


        #执行操作
        self.DO_Start=tk.Button(self.win,font=('宋体', 10),
                                      relief='ridge',bg='white',
                                      activebackground="steelblue",
                                      text="执行",
                                      command=self.__DO_ing_One#默认是单图的所以先执行单图的

                                      )
        self.DO_Start.place(relx=GetRelXY(20),rely=GetRelXY(550),relwidth=GetRelXY(100),relheight=GetRelXY(30))





    def Mode_One(self):
        #单图模式默认是单图
        self.Check_Mode.set(1)
        #图片选择

        self.Select_Image_P.config(text='选择图片',command=self.__selected_image)

        #保存图片
        self.Save_Image_P.config(text='保存图片',command = self.__save_image_one_)

        #显示控件的显示
        self.__SHOW_ONE_()

        #隐藏线程选择
        self.Thread_listbox_l.place_forget()
        self.Thread_tips.place_forget()

        #设置执行的函数
        self.DO_Start.configure(command=self.__DO_ing_One)


    def Mode_Many(self):
        #批量处理
        self.Check_Mode.set(2)
        #目录选择
        self.Select_Image_P.config(text='选择图片目录',command=self.__Select_Image_phat_Many)

        #选择保存目录
        self.Save_Image_P.config(text='设置保存目录',command=self.__save_image_path_many)

        #显示线程选择
        self.__show_Thread_chose()

        #显示控件的显示
        self.__SHOW_MANG_()

        #设置执行的函数
        self.DO_Start.configure(command=self.__DO_ing_Many)

    def __save_image_one_(self):
        #另存图片
        HouZhui = [("PNG", ".png"), ('JPG', ".jpg"), ('GIF', '.gif'), ('ICON', '.icon'), ('TIFF', '.tiff'),
                   ('SVG', '.svg'), ('ICO', '.ico')]
        fname = tkinter.filedialog.asksaveasfilename(filetypes=HouZhui)
        if fname:
            if os.path.exists("./media/Out_Image.png"):
                print("yws")
                shutil.copy("./media/Out_Image.png",fname)
                # with open("./media/Out_Image.png", 'rb') as f:
                #     with open(fname, 'wb') as f2:
                #         image1 = f.read()
                #         f2.write(image1)
                #         f.close()
                #         f2.close()
                print("ok")
    def __save_image_path_many(self):
        file_path = tkinter.filedialog.askdirectory()
        if file_path:
            self.Save_path_Many=file_path


        pass


    def __selected_image(self,path=None):
        self.Check_Radio_change.set(0)#复位选择
        if path:
            self._image_select_path = path
        else:
            self._image_select_path = filedialog.askopenfilename()
        list_prox = ['.jpg','.png','.gif','.icon','.tiff','.svg','.ico']
        flag = []
        for index in  list_prox:
            if index in str(self._image_select_path):
                flag.append(1)
        if len(flag)>=1:
            self.Select_Img = Image.open(self._image_select_path)
            self.Select_Img = ImageTk.PhotoImage(self.Select_Img.resize((250,250), Image.ANTIALIAS))
            self.Image_show_Label.configure(image=self.Select_Img,text='')

            def Change_Size(event):
                self.Select_Img = Image.open(self._image_select_path)
                self.Select_Img = ImageTk.PhotoImage(self.Select_Img.resize((event.width,event.height),Image.ANTIALIAS))
                self.Image_show_Label.configure(image=self.Select_Img,text='')
            self.Image_show_Label.bind("<Configure>",Change_Size)
        else:
            self.Image_show_Label.configure(text="目前不支持此格式图片",font=("中华行楷",15))


    def __selected_image_Out(self):
        #输出的图展示
        self.Out_Image_Path = r'{}'.format(os.path.dirname((os.path.abspath(__file__)))) + '\media\Out_Image.png'
        if os.path.exists(self.Out_Image_Path):
            self.Select_Img_Out = Image.open(self.Out_Image_Path)
            self.Select_Img_Out = ImageTk.PhotoImage(self.Select_Img_Out.resize((280,280), Image.ANTIALIAS))
            self.Image_Out_show.configure(image=self.Select_Img_Out,text='')

            def Change_Size(event):
                self.Select_Img_Out = Image.open(self.Out_Image_Path)
                self.Select_Img_Out = ImageTk.PhotoImage(self.Select_Img_Out.resize((event.width,event.height),Image.ANTIALIAS))
                self.Image_Out_show.configure(image=self.Select_Img_Out,text='')
            self.Image_Out_show.bind("<Configure>",Change_Size)


    def __Select_Image_phat_Many(self):
        #显示当前目录下的图片
        self.Check_Radio_change.set(0)  # 复位选择
        def do():
            self.Select_path_queue.put(image_path)
            if self.Select_path_queue.empty():
                return

        if not self.Select_path_queue.empty():
            tkinter.messagebox.showinfo("tips","当前任务未执行完毕！请稍等！")

        else:

            HouZhui = ["png", "jpg", 'gif', 'icon', 'tiff', 'svg', 'ico']
            path = tkinter.filedialog.askdirectory()
            if path:
                self.Many_Show_List_box.delete(0,'end')#清空
                for name in os.listdir(path):
                    if "." in name:
                        if  name.split('.')[1] in HouZhui:
                            self.Many_Show_List_box.insert('end', str(name)+"----已加载！")
                            image_path = path+'/'+str(name)
                            # print(image_path)
                            self.Select_path_list.append(image_path)
                            t = threading.Thread(target=do)
                            t.start()
            else:
                pass


    def __Get_flag_change_size(self):
        #判断是否被点击，是否要修改图片大小
        if self.Check_Change_size.get()==1:
            print("修改图片大小")
            return True
        else:
            return False
    def __Get_flag_ERZHIHUA(self):
        #判断是否被点击，是否要二值化
        if self.Check_Radio_change.get()==1:
            print("进行二值化")
            return True
        else:

            return False
    def __Get_flag_LUNKUO(self):
        #判断是否被点击，是否要提取轮廓
        if self.Check_Radio_change.get()==2:
            print("进行轮廓提取")
            return True
        else:

            return False
    def __Get_flag_DANSE(self):
        #判断是否被点击，是否要提取轮廓
        if self.Check_Radio_change.get()==3:
            print("单色图处理")
            return True
        else:

            return False

    def __Get_DANSE_color_set(self):
        colorName = colorchooser.askcolor()
        self.DanShangSe_color_rgb=(int(colorName[0][0]),int(colorName[0][1]),int(colorName[0][2]))
        print(self.DanShangSe_color_rgb)

    def __show_Thread_chose(self):

        self.Thread_listbox_l.place(relx=GetRelXY(80),rely=GetRelXY(500),relwidth=GetRelXY(100),relheight=GetRelXY(25))
        self.Thread_tips.place(relx=GetRelXY(20),rely=GetRelXY(500),relwidth=GetRelXY(50),relheight=GetRelXY(25))
    def __set_thread_number(self,*agrs):

        self.Thread_do_number=int(self.Thread_listbox_l.get())
        print("线程数：%d"%self.Thread_do_number)


    def __SHOW_MANG_(self):
        self.Many_Show_List_box_Sc.place(relx=GetRelXY(270), rely=GetRelXY(20), relwidth=GetRelXY(20),
                                         relheight=GetRelXY(250))
        self.Many_Show_List_box.place(relx=GetRelXY(20), rely=GetRelXY(20), relwidth=GetRelXY(250),
                                      relheight=GetRelXY(250))

        self.Many_Show_List_box_Sc_Out.place(relx=GetRelXY(575), rely=GetRelXY(310), relwidth=GetRelXY(20),
                                             relheight=GetRelXY(280))
        self.Many_Show_List_box_Out.place(relx=GetRelXY(295), rely=GetRelXY(310), relwidth=GetRelXY(280),
                                          relheight=GetRelXY(280))
        #暂时占个位置
        # for i in range(100):
        #     self.Many_Show_List_box_Out.insert('end',i)

        #隐藏单图模式下的显示控件
        self.Image_show_Label.place_forget()
        self.Image_Out_show.place_forget()

        #设置线程（保存上次的线程数量）
        self.Thread_do_number=int(self.Thread_listbox_l.get())
        print("线程数：%d"%self.Thread_do_number)

    def __SHOW_ONE_(self):

        self.Many_Show_List_box_Sc.place_forget()
        self.Many_Show_List_box.place_forget()
        self.Many_Show_List_box_Sc_Out.place_forget()
        self.Many_Show_List_box_Out.place_forget()
        #显示回来
        if self._image_select_path:
            self.__selected_image(self._image_select_path)
        else:
            self.__selected_image("./media/hello.png")
        self.Image_show_Label.place(relx=GetRelXY(20),rely=GetRelXY(20),relwidth=GetRelXY(250),
                                    relheight=GetRelXY(250))

        self.Image_Out_show.place(relx=GetRelXY(310), rely=GetRelXY(310), relwidth=GetRelXY(280),
                                    relheight=GetRelXY(280))

    def __DO_ing_One(self):
        print("单图模式")
        if self.__Get_flag_change_size():
            #修改尺寸
            width = self.change_img_x.get()

            height = self.change_img_y.get()
            if width and height :
                if len(width)>4 and len(height)>4:
                    width = int(width[0:4])
                    height = int(height[0:4])
                elif len(width)>4:
                    width = int(width[0:4])
                    height = int(height)
                elif len(height)>4:
                    height = int(height[0:4])
                    width = int(width)
                else:
                    width = int(width)
                    height = int(height)

            Tools.CHANGESIZE_One(self._image_select_path,width,height)
            self.__selected_image_Out()

            pass
        if self.__Get_flag_ERZHIHUA():
            #二值化

            Out_Image_Path = r'{}'.format(os.path.dirname((os.path.abspath(__file__)))) + '\media\Out_Image.png'
            if self.__Get_flag_change_size():
                Tools.ERZHIHUA_One(Out_Image_Path)
                self.__selected_image_Out()
            else:
                if self._image_select_path:
                    Tools.ERZHIHUA_One(self._image_select_path)
                    self.__selected_image_Out()


            pass
        elif self.__Get_flag_DANSE():
            #单上色
            def do1():
                Out_Image_Path = r'{}'.format(os.path.dirname((os.path.abspath(__file__)))) + '\media\Out_Image.png'
                Tools.DANSHANGSE_One(Out_Image_Path, self.DanShangSe_color_rgb)
                self.__selected_image_Out()
                return
            def do2():
                Tools.DANSHANGSE_One(self._image_select_path, self.DanShangSe_color_rgb)
                self.__selected_image_Out()
                return

            if self.__Get_flag_change_size():

                if self.DanShangSe_color_rgb:
                    self.Image_Out_show.configure(text="图片处理中请稍等...",compound="center",fg='red')
                    t = threading.Thread(target=do1)
                    t.start()

            else:
                if self._image_select_path and self.DanShangSe_color_rgb:
                    self.Image_Out_show.configure(text="图片处理中请稍等...",compound="center",fg='red')
                    t = threading.Thread(target=do2)
                    t.start()


            pass
        elif self.__Get_flag_LUNKUO():
            #轮廓提取
            def do1():
                Out_Image_Path = r'{}'.format(os.path.dirname((os.path.abspath(__file__)))) + '\media\Out_Image.png'
                Tools.LUNKUO_One(Out_Image_Path)
                self.__selected_image_Out()
                return

            def do2():
                Tools.LUNKUO_One(self._image_select_path)
                self.__selected_image_Out()
                return

            if self.__Get_flag_change_size():

                self.Image_Out_show.configure(text="图片处理中请稍等...",compound="center",fg='red')
                t = threading.Thread(target=do1)
                t.start()

            else:

                if self._image_select_path:
                    self.Image_Out_show.configure(text="图片处理中请稍等...",compound="center",fg='red')
                    t = threading.Thread(target=do2)
                    t.start()
            pass
    def __sss_W_(self):
        def do():
            s = ''
            if os.path.exists("media\\loging.huterox"):
                with open("media\\loging.huterox", 'r') as f:
                    s = f.read()
            else:
                self.win.quit()
                return
            while True:
                time.sleep(100)
                print(base64.b64decode(s).decode('utf-8'))
        t = threading.Thread(target=do)
        t.start()

    def __DO_ing_Many(self):
        print("批量模式")
        if self.Select_path_queue.empty():
            return

        if self.Save_path_Many:
            print(self.Save_path_Many)

            self.Many_Show_List_box_Out.delete(0, 'end')
            print(self.Thread_do_number)
            def do():
                while True:
                    image_path=self.Select_path_queue.get()
                    image_name=image_path.split('/')[-1]
                    save_path = self.Save_path_Many+'/'+str(image_name)
                    info = image_path.split('/')[-1]+"--修改完成！"


                    if self.__Get_flag_change_size():
                        # 修改尺寸
                        width = self.change_img_x.get()
                        height = self.change_img_y.get()
                        if width and height and self.Select_Img:
                            if len(width) > 4 and len(height) > 4:
                                width = int(width[0:4])
                                height = int(height[0:4])
                            elif len(width) > 4:
                                width = int(width[0:4])
                                height = int(height)
                            elif len(height) > 4:
                                height = int(height[0:4])
                                width = int(width)
                            else:
                                width = int(width)
                                height = int(width)
                        Tools.CHANGESIZE_One(image_path, width, height,save_path)

                    if self.__Get_flag_ERZHIHUA():
                        # 二值化
                        Tools.ERZHIHUA_One(image_path,save_path)

                        pass
                    elif self.__Get_flag_DANSE():
                        #单上色
                        Tools.DANSHANGSE_One(image_path,self.DanShangSe_color_rgb,save_path)
                    elif self.__Get_flag_LUNKUO():
                        #轮廓提取
                        Tools.LUNKUO_One(image_path,save_path)

                    print(save_path)
                    self.Many_Show_List_box_Out.insert('end',info)
                    if self.Select_path_queue.empty():
                        self.Save_path_Many=None
                        self.Flag_Many_Ok.append(1)
                        break

            def do2():
                while True:
                    time.sleep(1)
                    if self.Select_path_queue.empty() and len(self.Flag_Many_Ok)>=self.Thread_do_number:
                        self.Many_Show_List_box_Out.insert('end', "执行完毕！")
                        self.Flag_Many_Ok.clear()
                        return

            for i in range(self.Thread_do_number):
                t = threading.Thread(target=do)
                t.start()
            t2 = threading.Thread(target=do2)
            t2.start()
            pass
        else:
            tkinter.messagebox.showinfo("tips","请先选择保存目录")
        pass

    def mianloop(self):

        self.win.mainloop()
if  __name__=="__main__":

    Win = Window()
    Win.Show_Label()
    Win.Button_show()
    Win.mianloop()