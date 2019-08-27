from queue import Queue
import threading
import time
from traceback import format_exc
from tkinter import Tk, Menu, Label, Button, IntVar,Listbox, Entry, \
    Toplevel, Radiobutton, Checkbutton
from tkinter.filedialog import askopenfilenames
from tkinter.messagebox import showerror, showinfo, askyesno
from PIL import ImageTk, Image


from utils import *
from config import *
from settings import *

# 各种状态
STOP = 0
RUN = 1
ERROR = -1
PAUSE = 2
# 运行状态
STATE = STOP

class PopUpCaptchWindow(object):
    '''
    弹出验证码窗口
    '''
    def __init__(self,master, imgpath):
        '''
        :param master: 父窗口
        :param imgpath: 图像路径(验证码图片路径)
        '''
        top=self.top=Toplevel(master)
        self.l=Label(top,text="请输入验证码：")
        self.l.pack()

        im = Image.open(imgpath)
        img = ImageTk.PhotoImage(im)
        panel = Label(top, image=img)
        panel.image = img
        panel.pack(expand="yes")

        self.e=Entry(top)
        self.e.pack()
        self.b=Button(top,text='确定',command=self.cleanup)
        self.b.pack()
    def cleanup(self):
        self.value=self.e.get()
        self.top.destroy()


class GUI():

    def __init__(self, window, func):


        self.window = window
        self.window.title('AutoPublish')
        self.window.geometry('700x600')

        menubar = Menu(self.window)
        filemenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='设置', menu=filemenu)
        filemenu.add_command(label='帮助', command=self.helpme)
        filemenu.add_separator()  
        filemenu.add_command(label='退出', command=self.quit)
        self.window.config(menu=menubar)

        self.l = Label(window, text='')
        self.l.pack(padx=5, pady=10)


        btn1 = Button(window, text='选择MD文件', width=15, height=2, command=self.xz)
        btn1.pack()
        self.send_btn = Button(window, text='自动发布', width=15, height=2, command=func)
        self.send_btn.pack()

        self.pausebtn = Button(window, text='暂停发布', width=15, height=2, command=self.pause)
        self.pausebtn.pack()

        for k,v in PLCheck.items():
            invar = 'self.%s_IntVar'%k
            exec(invar + ' = IntVar()')
            Checkbutton(window, text = v ,variable=eval(invar), height=1, width=10).pack()


        self.lb = Listbox(window, width=300, height=200, listvariable='文章发送日志:\n')
        self.lb.pack()

        self.window.protocol("WM_DELETE_WINDOW", self.exit_callback)

    def popup(self, imgpath):
        self.w=PopUpCaptchWindow(self.window, imgpath)
        self.send_btn["state"] = "disabled"
        self.window.wait_window(self.w.top)
        self.send_btn["state"] = "normal"

    def exit_callback(self):
        global STATE
        STATE = STOP
        self.window.destroy()
        # sys.exit()

    def xz(self):
        global MDPATHS
        filenames = askopenfilenames(filetypes=[("MarkDown file", "*.md")])
        if len(filenames) > 0:
            fnlist = [fn for fn in filenames if os.path.splitext(fn)[-1] == '.md']
            fnstr = '\n'.join(fnlist)
            self.l.config(text=fnstr)
            MDPATHS = fnlist
        else:
            self.l.config(text='目前没有选择任何MarkDown文件')

    def pause(self):
        global STATE
        if STATE == PAUSE:
            self.pausebtn.config(text='暂停发送')
            STATE = RUN
        elif STATE == RUN:
            self.pausebtn.config(text='继续发送')
            STATE = PAUSE

    def helpme(self):
        showerror('帮助', '请微信联系：jingkuang_  请注明：城市、职业、来意')

    def quit(self):
        global STATE
        if STATE == RUN:
            if askyesno('危险操作', '自动发送文章任务未完成，你确定要退出?'):
                STATE = STOP
                self.window.quit()
        else:
            self.window.quit()


class Thread():
    def __init__(self, window):
        self.window = window
        self.gui = GUI(window, self.run)
        self.queue = Queue()

    def show(self):
        if STATE == STOP:
            return
        while not self.queue.empty():
            position,content = self.queue.get()
            self.gui.lb.insert(position, content)
        while self.queue.empty():
            print('sleep')
            time.sleep(2)
        self.show()

    def send(self):
        global MDPATHS
        global STATE
        STATE = RUN
        if not len(MDPATHS):
            self.gui.l.config(text='必须选择至少一个Markdown文件')
            return


        def repeat3(instance,*args, num=3):
            for i in range(num):
                res_state = instance.run(*args)
                if res_state == SUCCESS:
                    return SUCCESS
                time.sleep(1)
            return res_state


        if len(MDPATHS):

            # 要考虑中途中断以及发送失败的问题
            self.gui.l.config(text=' 文章自动进行中... ')
            self.queue.put((1,' ** 自动发送进程启动 ** '))
            send_state = {'all':0, 'success':0, 'loss_data':0, 'fail':0}

            if STATE == STOP:
                return

            if STATE == PAUSE:
                self.queue.put(('end', '自动邮件暂停'))
                while STATE == PAUSE:
                    time.sleep(5)

            for k, v in PLCheck.items():
                invar = k + '_IntVar'
                if eval('self.gui.%s'%invar).get():
                    eval(k).run(MDPATHS, self.gui)

            self.gui.l.config(text='')
        # 停止显示进程
        STATE = STOP
        showinfo('结束提示', '文章自动发送完成')

    def run(self):
        # 自动发送邮件
        self.thread1 = threading.Thread(target=self.send)
        self.thread1.start()
        # 循环显示
        self.thread2 = threading.Thread(target=self.show)
        self.thread2.start()

if __name__ == '__main__':
    # 创建窗口
    window = Tk()
    Thread(window)
    # 显示窗口 必须在所有控件后
    window.mainloop()



