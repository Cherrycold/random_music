'''
@Author: your name
@Date: 2020-04-02 13:54:57
@LastEditTime: 2020-08-26 21:21:14
@LastEditors: your name
@Description: 
@FilePath: \src\music.py
'''
# encoding:utf-8
import time
import os
from pygame import mixer
import time
import random
from tkinter import *
import tkinter.scrolledtext as scrolledtext
import _thread
import threading
import queue
import configparser

config = configparser.ConfigParser()
config.read('config.ini',encoding="UTF-8")
config_list = config['config']

_path = config_list['path'].replace('\\','/')
_time = config_list['time']
_Intervals_min = config_list['Intervals_min']
_Intervals_max = config_list['Intervals_max']
# _time = config.get('config',"time")
# _Intervals_min = config.get('config',"Intervals_min")
# _Intervals_max = config.get('config',"Intervals_max")


msg_type = {
    "start" : 1,
    "over" : 2,
}
 
def file_name(path): 
    list=[]
    for _,_,t in os.walk(path):
        for name in t :
            if "mp3" in name :
                list.append(name)
    return list

class logmgr(object):
    def __init__(self,player):
        rootpath = os.path.abspath(os.path.dirname(os.getcwd()))
        folder = os.path.exists(rootpath+"/log")
        if not folder:
            os.makedirs(rootpath+"/log")
        filename = rootpath+"/log/"+time.strftime("%m_%d_%H", time.localtime())
        self.file = open(filename,'w')
        self.player = player
    def logout(self,outstr):
        log = "[ "+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+" ] : " + outstr + "\n"
        self.file.write(log)
        self.file.flush()
        self.player.scr.insert(END,log)
        self.player.scr.update()
        return log

class Player(object):
    def __init__(self):
        self.flag = TRUE
        self.path = _path[1:-1]
        self.log = logmgr(self)
        self.wks = file_name(self.path)
        
        self.stop_flag = FALSE
        
    
        mixer.init()

    def playMp3(self):
        if len(self.wks) == 0:
            self.log.logout("没有声音文件")
            return
        self.flag = TRUE
        num = random.randint(0,len(self.wks)-1)
        self.log.logout("Play "+self.wks[num])
        # self.scr.insert(END,self.log.logout("Play "+self.wks[num]))
        # self.scr.update()
        mixer.music.load(self.path+"/"+self.wks[num])
        mixer.music.play(1)

    def pause_music(self):
        if self.flag == FALSE:
            mixer.music.unpause()
            self.flag = TRUE
            self.log.logout("Unpause")
            # self.scr.insert(END,self.log.logout("Unpause"))
            return
        mixer.music.pause()
        self.log.logout("Pause")
        # self.scr.insert(END,self.log.logout("Pause"))
        self.flag = FALSE
    def open_over_thread(self):
        #启动线程监听结束
        while True:
            time.sleep(5)
            if self.flag and not mixer.music.get_busy():
                self.playMp3()
            if not self.stop_flag:
                break
        return
    def auto_start(self):
        if len(self.wks) == 0:
            self.log.logout("没有声音文件")
            return
        self.over.place_forget()
        self.start.place_forget()
        self.restart.place_forget()
        self.playMp3()
        self.stop_flag = TRUE
        t1 = threading.Thread(target=self.open_over_thread)
        t1.setDaemon(True)
        t1.start()
        threading.Timer(60 * _time ,self.auto_stop).start()
        self.log.logout("after 3min over")
        # self.scr.insert(END,self.log.logout("after 3min over"))
        self.scr.update()
    def auto_stop(self):
        self.pause_music()
        self.stop_flag = FALSE
        randomtime = random.randint(_Intervals_min,_Intervals_max)*60
        threading.Timer(randomtime,self.auto_start).start()
        self.log.logout("after "+str(randomtime/60)+"min restart")
        # self.scr.insert(END,self.log.logout("after "+str(randomtime/60)+"min restart"))
        self.scr.update()
    def painter(self):
        frame1 = Tk()
        sw = frame1.winfo_screenwidth()
        sh = frame1.winfo_screenheight()
        ww = 640
        wh = 480
        frame1.geometry("%dx%d+%d+%d" %(ww,wh,(sw-ww) / 2,(sh-wh) / 2))            #设置窗口的大小为640*480
        frame1.resizable()                                  #窗口大小可以通过鼠标拖动改变，app.master.resizable(0,0)则表示窗口大小不可改变
        frame1.title("Windows")                             #设置窗口的名称         
        

        
        #启动一个线程，监听消息
        # t1 = threading.Thread(target=self.process_msg)
        # t1.setDaemon(True)
        # t1.start()

        self.scr = scrolledtext.ScrolledText(frame1, width=70, height=13)  #滚动文本框（宽，高（这里的高应该是以行数为单位），字体样式）
        self.scr.place(x=50, y=50) #滚动文本框在页面的位置

        self.start = Button(frame1, text="开始播放",height = 2, width=12, command=player.playMp3)
        self.start.place(x=70,y=329)
        
        self.over = Button(frame1, text="停止/继续播放",height = 2, width=12, command=player.pause_music)
        self.over.place(x=440,y=329)
        
        self.restart = Button(frame1, text="自动播放",height = 2, width=12, command=player.auto_start)
        self.restart.place(x=250,y=329)

        frame1.mainloop()
if __name__ =='__main__':
    player = Player()
    player.painter()
