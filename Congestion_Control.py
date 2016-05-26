#!/usr/local/bin/python

import wx

class MyFrame(wx.Frame):
    global_count = 0
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title = title, size = (800, 400))
        self.initFrame()

    def initFrame(self):
        self.Mylayout()
        self.Mycreatepacket()
        self.Centre()
        self.Show(True)
        wx.StaticText(self, -1, "Retransmission threshold", (630, 10))
        wx.StaticText(self, 1, "Reverse Clock", (630, 65))
        self.text = wx.TextCtrl(self, -1, "14", (630, 40), (110, 20))# The position of input bar
        h = self.text.GetSize().height
        w = self.text.GetSize().width + self.text.GetPosition().x+2

        self.spin = wx.SpinButton(self, -1,
                                  (w, 40),# The position of the right part
                                  (h*2/3, h),
                                  wx.SP_VERTICAL)
        self.spin.SetRange(1, 100)
        self.Bind(wx.EVT_SPIN, self.OnSpin, self.spin)

        # bind events
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.TimerHandler)

        # self.timer.Start(1000)
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.my_button)
        self.Bind(wx.EVT_PAINT, self.Mydraw)
        self.left_index=0
        self.right_index=self.packet_num-1
        self.tmp=0

    def get_val(self):
        return self.text.GetValue()

    def OnSpin(self, event):
        self.spin.SetValue(str(event.GetPosition()))

    def Mylayout(self):
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.my_button = wx.Button(self, label = 'Click me')
        self.my_spinctrl = wx.SpinCtrl(self, value = '0', pos = (630, 90))
        self.my_spinctrl.SetRange(0, 20)
        self.vbox.Add(self.my_button, flag = wx.ALL, border = 4)
        self.SetSizer(self.vbox)

    def OnClick(self, event):
        self.timer.Start()
        pass

    def TimerHandler(self, event):
        MyFrame.global_count = MyFrame.global_count + 1
        self.tmp=self.tmp+1
        if self.tmp==51:
            self.tmp=1
        tmpval=self.my_spinctrl.GetValue()
        self.my_spinctrl.SetValue(tmpval-self.tmp/50)
        if self.flying_packet[0].y==50:
            self.my_spinctrl.SetValue(int(self.get_val()))
        for i in range(len(self.flying_packet)):
            if self.flying_packet[i].direction == "down":
                self.flying_packet[i].y  = self.flying_packet[i].y + 1
                if self.flying_packet[i].y >= 350:
                    self.flying_packet[i].direction = "up"
            if self.flying_packet[i].direction == "up":
                self.flying_packet[i].y  = self.flying_packet[i].y - 1
                if self.flying_packet[i].y <= 50:
                    self.flying_packet[i].direction = "down"
            if self.flying_packet[i].retransmitting=="yes":
                if self.candidate_packet[i].direction == "down":
                    self.candidate_packet[i].y  = self.candidate_packet[i].y + 1
                    if self.candidate_packet[i].y >= 350:
                        self.candidate_packet[i].direction = "up"
                if self.candidate_packet[i].direction == "up":
                    self.candidate_packet[i].y  = self.candidate_packet[i].y - 1
                    if self.candidate_packet[i].y <= 50:
                        self.candidate_packet[i].direction = "down"
                if self.candidate_packet[i].direction=="up" and self.candidate_packet[i].y==50:
                    self.flying_packet[i].retransmitting="no"
                if self.candidate_packet[i].y==349 and self.flying_packet[i].index != self.candidate_packet[i].index:
                    self.flying_packet[i].retransmitting="no"
                    self.candidate_packet[i].y=-50
            if self.flying_packet[i].stop == 'yes' and self.flying_packet[i].y == 50:
                self.left_index=self.left_index+1
                if self.left_index >= self.solid_num:
                    self.left_index=0
                self.flying_packet[i].stop="no"
                self.right_index=self.left_index+self.packet_num-1
                if self.right_index>=self.solid_num:
                    self.right_index=self.solid_num-1
                    self.flying_packet[i].index=-1000
                else:
                    self.flying_packet[i].index=(self.flying_packet[i].index+self.packet_num) %self.solid_num

                self.flying_packet[i].x=self.flying_packet[i].index*50+50
                self.flying_packet[i].starttime=self.global_count
            if self.flying_packet[i].starttime < self.global_count-50*int(self.get_val()):
                self.flying_packet[i].starttime=self.global_count
                self.candidate_packet[i].x=self.flying_packet[i].x
                self.candidate_packet[i].y=50
                self.flying_packet[i].retransmitting="yes"
                self.candidate_packet[i].starttime=self.global_count
                self.my_spinctrl.SetValue(int(self.get_val()))
            if self.flying_packet[i].stop=="no" and self.flying_packet[i].y == 100:
                self.flying_packet[i].stop="yes"
            if self.global_count>3*12*50+120:
                for k in range(len(self.flying_packet)):
                    self.flying_packet[k].y=50
                    self.left_index=-1
        self.Refresh()

    def Mycreatepacket(self):
        self.packet_num = 4
        self.solid_num=12
        self.top_packet = [MyPacket(i*50+50, 50, "blue", self.global_count,i) for i in range(self.solid_num)]
        self.bottom_packet = [MyPacket(i*50+50, 350, "yellow", self.global_count,i) for i in range(self.solid_num)]
        self.flying_packet = [MyPacket(i*50+50, 50-i*40, "green", i*40,i) for i in range(self.packet_num)]
        self.candidate_packet = [MyPacket(i*50+50, 50, "blue", self.global_count,i) for i in range(self.packet_num)]



    def Mydraw(self, event):
        dc = wx.PaintDC(self)
        if self.left_index>=0:
            dc.DrawRectangle(self.bottom_packet[self.left_index].x-self.flying_packet[0].r, 50-self.flying_packet[0].r,(self.right_index-self.left_index)*50+20, 2*self.flying_packet[0].r)
        dc.SetBrush(wx.Brush("#00ffff", wx.SOLID))
        for packet in self.top_packet:
            dc.DrawCircle(packet.x,packet.y,packet.r)


        dc.SetBrush(wx.Brush("#ffff00", wx.SOLID))
        for packet in self.bottom_packet:
            dc.DrawCircle(packet.x, packet.y, packet.r)

        dc.SetBrush(wx.Brush("#00ff00", wx.SOLID))
        for packet in self.flying_packet:
            if packet.y>=50:
                dc.DrawCircle(packet.x, packet.y, packet.r)


        dc.SetBrush(wx.Brush("#00ff00", wx.SOLID))
        for packet in self.candidate_packet:
            if packet.y>=50:
                dc.DrawCircle(packet.x, packet.y, packet.r)

class MyPacket(object):
    def __init__(self, x, y, state,starttime, index):
        self.x = x
        self.y = y
        self.state = state
        self.r = 10
        self.direction = "down"
        self.starttime=starttime
        self.index=index
        self.retransmitting="no"
        self.stop="no"

app = wx.App()
MyFrame(None, title = "7.Dynamic")
app.MainLoop()