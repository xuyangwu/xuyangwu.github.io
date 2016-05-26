#!/usr/local/bin/python

import wx
import math
class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title = title, size = (500, 400))
        self.initFrame()

    def initFrame(self):
        self.filesize=4096
        self.buffersize=2048
        self.sender_val=0
        self.receiver_val=0
        self.sender_app_val=0
        self.receiver_app_val=0
        self.Mylayout()
        self.Centre()
        self.global_count=0
        # bind events
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.TimerHandler)
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.my_button)
        self.stage={0:1,1:2,2:3,3:4,4:5,5:6}


    def Mylayout(self):
        panel = wx.Panel(self, -1)
        self.my_button = wx.Button(panel, label = 'Restart', pos = (10, 30))
        wx.StaticText(panel, -1, "filesize", (90, 70))
        self.my_spinctrl = wx.SpinCtrl(panel, value = '4096', pos = (60, 100))
        self.my_spinctrl.SetRange(0, 10000)
        wx.StaticText(panel, -1, "buffersize", (330, 70))
        self.my_spinctrl2 = wx.SpinCtrl(panel, value = '2048', pos = (300, 100))
        self.my_spinctrl2.SetRange(0, 10000)
        wx.StaticText(panel, -1, "sender", (30, 150))
        self.sender = wx.Gauge(parent=panel,id= -1, range=self.buffersize,pos=(30, 200), size=(200, 25))
        self.sender.SetBezelFace(3)
        self.sender.SetShadowWidth(3)
        wx.StaticText(panel, -1, "receiver", (270, 150))
        self.receiver = wx.Gauge(parent=panel,id= -1, range=self.buffersize, pos=(270, 200), size=(200, 25))
        self.receiver.SetBezelFace(3)
        self.receiver.SetShadowWidth(3)
        wx.StaticText(panel, -1, "sender application", (30, 250))
        self.sender_app = wx.Gauge(parent=panel,id= -1, range=self.filesize,pos=(30, 300), size=(200, 25))
        self.sender_app.SetBezelFace(3)
        self.sender_app.SetShadowWidth(3)
        self.sender_app_val=self.filesize
        self.sender_app.SetValue(self.sender_app_val)
        wx.StaticText(panel, -1, "receiver application", (270, 250))
        self.receiver_app = wx.Gauge(parent=panel,id= -1, range=self.filesize,pos=(270, 300), size=(200, 25))
        self.receiver_app.SetBezelFace(3)
        self.receiver_app.SetShadowWidth(3)

    def OnClick(self, event):
        self.buffersize=self.my_spinctrl2.GetValue()
        self.sender.SetRange(self.buffersize)
        self.receiver.SetRange(self.buffersize)
        self.filesize=self.my_spinctrl.GetValue()
        self.sender_app.SetRange(self.filesize)
        self.receiver_app.SetRange(self.filesize)
        self.round=math.ceil(float(self.filesize)/self.buffersize)
        self.steps=3*self.round
        print self.steps
        self.state="1"
        self.global_count=0
        self.timer.Start(1000)
        self.sender_val=0
        self.filesize=self.my_spinctrl.GetValue()
        self.buffersize=self.my_spinctrl2.GetValue()
        self.sender_val=min(self.buffersize,self.filesize)
        self.sender.SetValue(self.sender_val)
        self.receiver_val=0
        self.receiver.SetValue(self.receiver_val)
        self.sender_app_val=max(0,self.filesize-self.buffersize)
        self.sender_app.SetValue(self.sender_app_val)
        self.receiver_app_val=0
        self.receiver_app.SetValue(self.receiver_app_val)
        pass

    def TimerHandler(self, event):
        self.global_count = self.global_count + 1
        if self.global_count<=self.steps:
            if self.state=="1":
                self.receiver_val=self.receiver_val+self.sender_val
                self.state="2"
            elif self.state=="2":
                self.receiver_app_val=self.receiver_app_val+self.receiver_val
                self.sender_val=0
                self.state="3"
            else:
                self.sender_val=min(self.sender_app_val, self.buffersize)
                self.sender_app_val=max(self.sender_app_val-self.buffersize, 0)
                self.receiver_app_val=self.receiver_app_val+self.receiver_val
                self.receiver_val=0
                self.state="1"
        self.sender.SetValue(self.sender_val)
        self.sender_app.SetValue(self.sender_app_val)
        self.receiver.SetValue(self.receiver_val)
        self.receiver_app.SetValue(self.receiver_app_val)

app = wx.App()
MyFrame(None, title = "Flow Control").Show()
app.MainLoop()