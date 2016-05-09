# -*- coding: utf-8 -*-
import wx

import numpy as np
import math
import matplotlib

# matplotlib采用WXAgg为后台,将matplotlib嵌入wxPython中
matplotlib.use("WXAgg")

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
from matplotlib.ticker import MultipleLocator, FuncFormatter
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.pyplot import gcf, setp

import pylab
from matplotlib import pyplot
from matplotlib import pyplot as plt   
from matplotlib import animation   

block_number=20

class Knob:
    """
    Knob - simple class with a "setKnob" method.  
    A Knob instance is attached to a Param instance, e.g. param.attach(knob)
    Base class is for documentation purposes.
    """
    def setKnob(self, value):
        pass

class Param:
    """
    The idea of the "Param" class is that some parameter in the GUI may have
    several knobs that both control it and reflect the parameter's state, e.g.
    a slider, text, and dragging can all change the value of the frequency in
    the waveform of this example.  
    The class allows a cleaner way to update/"feedback" to the other knobs when 
    one is being changed.  Also, this class handles min/max constraints for all
    the knobs.
    Idea - knob list - in "set" method, knob object is passed as well
      - the other knobs in the knob list have a "set" method which gets
        called for the others.
    """
    def __init__(self, initialValue=None, minimum=0., maximum=10):
        self.minimum = minimum
        self.maximum = maximum
        if initialValue != self.constrain(initialValue):
            raise ValueError('illegal initial value')
        self.value = initialValue
        self.knobs = []
        
    def attach(self, knob):
        self.knobs += [knob]
        
    def set(self, value, knob=None):
        self.value = value
        self.value = self.constrain(value)
        for feedbackKnob in self.knobs:
            if feedbackKnob != knob:
                feedbackKnob.setKnob(self.value)
        return self.value

    def constrain(self, value):
        if value <= self.minimum:
            value = self.minimum
        elif value >= self.maximum:
            value = self.maximum
        return value

class SliderGroup(Knob):
    def __init__(self, parent, label, param):
        self.sliderLabel = wx.StaticText(parent, label=label)
        self.sliderText = wx.TextCtrl(parent, -1, style=wx.TE_PROCESS_ENTER)
        self.setKnob(param.value)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.sliderLabel, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=2)
        sizer.Add(self.sliderText, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=1)
        self.sizer = sizer

        self.sliderText.Bind(wx.EVT_TEXT_ENTER, self.sliderTextHandler)

        self.param = param
        self.param.attach(self)

    def sliderHandler(self, evt):
        value = evt.GetInt()
        self.param.set(value)
        
    def sliderTextHandler(self, evt):
        value = float(self.sliderText.GetValue())
        self.param.set(value)
        
    def setKnob(self, value):
        self.sliderText.SetValue('%g'%value)
        

Writer = animation.writers['ffmpeg']
writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)

######################################################################################
class MPL_Panel_base(wx.Panel):
    ''' #MPL_Panel_base面板,可以继承或者创建实例'''
    def __init__(self,parent):
        wx.Panel.__init__(self,parent=parent, id=-1)

        self.Figure = plt.figure()
        self.window_size=Param(5., minimum=1., maximum=6.)
        self.frequencySliderGroup = SliderGroup(self, label='window size:', param=self.window_size)
        self.window_size.attach(self)
        self.FigureCanvas = FigureCanvas(self,-1,self.Figure)
        
        #self.NavigationToolbar = NavigationToolbar(self.FigureCanvas)

        self.StaticText = wx.StaticText(self,-1,label='Max window sizw is 6')

        self.SubBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SubBoxSizer.Add(self.frequencySliderGroup.sizer, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=5)

        #self.SubBoxSizer.Add(self.NavigationToolbar,proportion =0, border = 2,flag = wx.ALL | wx.EXPAND)
        self.SubBoxSizer.Add(self.StaticText,proportion =-1, border = 2,flag = wx.ALL | wx.EXPAND)

        self.TopBoxSizer = wx.BoxSizer(wx.VERTICAL)
        self.TopBoxSizer.Add(self.SubBoxSizer,proportion =-1, border = 2,flag = wx.ALL | wx.EXPAND)
        self.TopBoxSizer.Add(self.FigureCanvas,proportion =-10, border = 2,flag = wx.ALL | wx.EXPAND)

        self.SetSizer(self.TopBoxSizer)
        #self.SetSizer(sizer)

        ###方便调用
        self.pylab=pylab
        self.pl=pylab
        self.pyplot=pyplot
        self.numpy=np
        self.np=np
        self.plt=pyplot

        def sizeHandler(self, *args, **kwargs):
            self.canvas.SetSize(self.GetSize())
    
    def repaint(self):
        self.canvas.draw()

    def setKnob(self, value):
        #setp(data=self.window_size.value)
        self.repaint()

    def UpdatePlot(self):
        '''#修改图形的任何属性后都必须使用self.UpdatePlot()更新GUI界面 '''
        self.FigureCanvas.draw()


    def plot(self,*args,**kwargs):
        '''#最常用的绘图命令plot '''
        #fig = self.Figure
        ax=self.Figure.add_subplot(111)
        line, = ax.plot([], [], lw=2)
        def init():  
            line.set_data([], [])
        #ax.grid(True, linestyle='-',color='0.75')
        ax.set_xlim([-50,250])
        ax.set_ylim([-50,250])
        x=(np.linspace(0,10*block_number-10,block_number)).tolist()
        y=(np.zeros(block_number)).tolist()
        scat=plt.scatter(x,y,s=40, c='blue')
        scat.set_alpha(0.8)

        scat3=plt.scatter(x,y,s=40, c='yellow')
        scat3.set_alpha(0.8)

        scat1=plt.scatter(x,y,s=40,c='green') 
        scat1.set_alpha(0.8)
        
        scat2=plt.scatter(x,y,s=40,c='cyan')
        scat2.set_alpha(0.8)

        scat4=plt.scatter(x,y,s=40,c='black')
        scat4.set_alpha(0.8)

        scat5=plt.scatter(x,y,s=40,c='red')
        scat5.set_alpha(0.8)
        #scat for up node
        #scat3 for down node
        #scat1 for unsended downside
        #scat2 for unaccepted upside
        #scat4 for down sended node
        #scat5 for up accepted node
        def _update_plot(i,fig,scat, scat1, scat2, scat3, scat4, scat5, line):
            i=8*i
            position=(np.ones(block_number)*(-100)).tolist()
            position1=(np.zeros(block_number)*200).tolist()
            position2=(np.ones(block_number)).tolist()
            position3=(np.ones(block_number)*200).tolist()
            wind_val = int(math.ceil(self.window_size.value))
            Interval_time=20
            begin_node=-1

            period=(20/wind_val)*400
            if period*wind_val<8000:
                period=period+400
            period=period+(wind_val-1)*20
            period=period+(20%wind_val)*20
            if i>=period:
                i=i%period
            for index in range(block_number):
                batch_index=index/wind_val
                start_time=batch_index*400+(index%wind_val)*Interval_time
                end_time=start_time+400
                if i<end_time and i>=start_time:
                    if begin_node==-1:
                        begin_node=index
                    temp=i-start_time
                    if temp>200:
                        position3[index]=400-temp
                    else:
                        position[index]=temp
            if begin_node==-1:
                print i
            x0=range(block_number)
            x0=[elem*10 for elem in x0]

            position1=np.zeros(block_number)
            position2=np.ones(block_number)*200
            position4=np.ones(block_number)*(-200)
            position5=np.ones(block_number)*(-200)
            for k in range(begin_node):
                position1[k]=-200
                position2[k]=-200
                position4[k]=0
                position5[k]=200

            offset=list(zip(x0, position))
            offset1=list(zip(x0, position1))
            offset2=list(zip(x0, position2))
            offset3=list(zip(x0, position3))
            offset4=list(zip(x0, position4))
            offset5=list(zip(x0, position5))
            
            scat.set_offsets(offset)
            scat1.set_offsets(offset1)
            scat2.set_offsets(offset2)
            scat3.set_offsets(offset3)
            scat4.set_offsets(offset4)
            scat5.set_offsets(offset5)
            plt.legend([line, scat, scat1,scat2,scat3,scat4,scat5], ['Slidewindow', 'sending data', 'unsending data', 'unack data', 'ack', 'sended data', 'confirmed data'])
            left_node=begin_node
            right_node=begin_node+wind_val-1
            if right_node>=20:
                right_node=19
            x=[left_node*10-5, right_node*10+5, right_node*10+5, left_node*10-5, left_node*10-5]
            y=[-7, -7, 7, 7, -7]
            line.set_data(x, y)
            return scat, scat1, scat2,scat3,scat4,scat5,line
        anim = animation.FuncAnimation(self.Figure, _update_plot, fargs=(self.Figure, scat, scat1, scat2, scat3, scat4, scat5, line), frames=5000, interval=10)
        anim.save('im.mp4', writer=writer)
        plt.show()
        self.UpdatePlot()

    def cla(self):
        ''' # 再次画图前,必须调用该命令清空原来的图形  '''
        self.Figure.clear()
        self.Figure.set_canvas(self.FigureCanvas)
        self.UpdatePlot()
        
################################################################



################################################################
class MPL_Panel(MPL_Panel_base):
    ''' #MPL_Panel重要面板,可以继承或者创建实例 '''
    def __init__(self,parent):
        MPL_Panel_base.__init__(self,parent=parent)

        #测试一下
        self.FirstPlot()


    #仅仅用于测试和初始化,意义不大
    def FirstPlot(self):
        #self.rc('lines',lw=5,c='r')
        #self.cla()
        x = np.arange(-5,5,0.25)
        y = np.sin(x)
        self.plot(x,y,'--^g')


###############################################################################
#  MPL_Frame添加了MPL_Panel的1个实例
###############################################################################
class MPL_Frame(wx.Frame):
    """MPL_Frame可以继承,并可修改,或者直接使用"""
    def __init__(self,title="MPL_Frame Example In wxPython",size=(800,500)):
        wx.Frame.__init__(self,parent=None,title = title,size=size)

        self.MPL = MPL_Panel_base(self)

        #创建FlexGridSizer
        self.FlexGridSizer=wx.FlexGridSizer( rows=9, cols=1, vgap=5,hgap=5)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)

        self.RightPanel = wx.Panel(self,-1)

        #测试按钮1
        self.Button1 = wx.Button(self.RightPanel,-1,"start",size=(100,40),pos=(10,50))
        self.Button1.Bind(wx.EVT_BUTTON,self.Button1Event)

        
        #加入Sizer中
        self.FlexGridSizer.Add(self.Button1,proportion =0, border = 5,flag = wx.ALL | wx.EXPAND)

        self.RightPanel.SetSizer(self.FlexGridSizer)
        
        self.BoxSizer=wx.BoxSizer(wx.HORIZONTAL)
        self.BoxSizer.Add(self.MPL,proportion =-10, border = 2,flag = wx.ALL | wx.EXPAND)
        self.BoxSizer.Add(self.RightPanel,proportion =0, border = 2,flag = wx.ALL | wx.EXPAND)
        
        self.SetSizer(self.BoxSizer)    

        #状态栏
        self.StatusBar()

        #MPL_Frame界面居中显示
        self.Centre(wx.BOTH)



    #按钮事件,用于测试
    
    def Button1Event(self,event):
        self.MPL.cla()#必须清理图形,才能显示下一幅图
        x=np.arange(-10,10,0.25)
        y=np.cos(x)
        self.MPL.plot(x,y,'--*g')
        self.MPL.UpdatePlot()#必须刷新才能显示
    '''
    def Button1Event(self,event):
        self.MPL.cla()#必须清理图形,才能显示下一幅图
        # first set up the figure, the axis, and the plot element we want to animate   
    '''




    #打开文件,用于测试
    def DoOpenFile(self):
        wildcard = r"Data files (*.dat)|*.dat|Text files (*.txt)|*.txt|ALL Files (*.*)|*.*"
        open_dlg = wx.FileDialog(self,message='Choose a file',wildcard = wildcard, style=wx.OPEN|wx.CHANGE_DIR)
        if open_dlg.ShowModal() == wx.ID_OK:
            path=open_dlg.GetPath()
            try:
                file = open(path, 'r')
                text = file.read()
                file.close()
            except IOError, error:
                dlg = wx.MessageDialog(self, 'Error opening file\n' + str(error))
                dlg.ShowModal()

        open_dlg.Destroy()



    #自动创建状态栏
    def StatusBar(self):
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(3)
        self.statusbar.SetStatusWidths([-2, -2, -1])



#主程序测试
if __name__ == '__main__':
    app = wx.PySimpleApp()
    #frame = MPL2_Frame()
    frame =MPL_Frame()
    frame.Center()
    frame.Show()
    app.MainLoop()