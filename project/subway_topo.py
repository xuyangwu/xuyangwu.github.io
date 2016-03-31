from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import irange,dumpNodeConnections
from mininet.log import setLogLevel

class MyTopo(Topo):
        "Metro Lines Topology"
        "14 lines"

        def __init__(self):
                # Initialize topology and default options
                Topo.__init__(self)
                switchs = []
                hosts = []


                for i in range(303):
                        switch = self.addSwitch('s%s'%i)
                        switchs.append(switch)
                        host = self.addHost('h%s'%i)
                        hosts.append(host)
                        self.addLink(switch, host, delay='0.1ms', loss=0, max_queue_size=1000, use_htb=True)

                line1 = range(28)
                delay1 = [2,2,3,3,2,3,2,3,3,2,2,3,1,2,2,3,2,2,2,2,3,2,3,3,3,2,2]
                for i in range(27):
                        self.addLink(switchs[line1[i]], switchs[line1[i+1]], bw=1, delay=delay1[i], loss=0, max_queue_size=1000, use_htb=True)

                line2 = range(28,46)+[15]+range(46,57)
                delay2 = [3,7,5,3,5,3,3,1,3,2,4,1,3,3,2,2,3,3,2,2,3,3,2,3,2,3,7,2,3]
                for i in range(29):
                        self.addLink(switchs[line2[i]], switchs[line2[i+1]], bw=1, delay=delay2[i], loss=0, max_queue_size=1000, use_htb=True)

                line3 = [23]+range(57,63)+[49]+range(63,67)+[12]+range(67,83)
                delay3 = [2,3,2,2,2,3,2,2,2,3,2,3,3,2,3,2,2,3,2,1,2,2,3,2,5,2,2,2]
                for i in range(28):
                        self.addLink(switchs[line3[i]], switchs[line3[i+1]], bw=1, delay=delay3[i], loss=0, max_queue_size=1000, use_htb=True)

                line4 = range(60,63)+[49]+range(63,67)+[13,68]+range(83,88)+[43]+range(88,97)+[22]
                delay4 = [2,2,2,1,2,3,2,3,2,2,2,3,2,2,2,2,3,3,3,2,3,1,3,2,2]
                for i in range(25):
                        self.addLink(switchs[line4[i]], switchs[line4[i+1]], bw=1, delay=delay4[i], loss=0, max_queue_size=1000, use_htb=True)

                line5 = [27]+range(97,107)
                delay5 = [2,2,4,3,3,2,3,2,3,2]
                for i in range(10):
                        self.addLink(switchs[line5[i]], switchs[line5[i+1]], bw=1, delay=delay5[i], loss=0, max_queue_size=1000, use_htb=True)

                line6 = range(107,123)+[43,124,90]+range(124,133)
                delay6 = [2,3,3,3,2,2,2,2,3,2,2,3,2,2,3,2,3,2,3,2,3,2,3,2,2,2,2]
                for i in range(27):
                        self.addLink(switchs[line6[i]], switchs[line6[i+1]], bw=1, delay=delay6[i], loss=0, max_queue_size=1000, use_htb=True)

                line7 = [133,39,134,135,136,126]+range(137,142)+[95,142,18,47,143,144,65]+range(145,160)
                delay7 = [3,2,3,2,3,2,2,2,2,3,2,2,3,2,3,2,2,3,2,2,2,2,3,2,2,3,3,6,3,2,4,2]
                for i in range(32):
                        self.addLink(switchs[line7[i]], switchs[line7[i+1]], bw=1, delay=delay7[i], loss=0, max_queue_size=1000, use_htb=True)

                line8 = range(160,166)+[132,166,167,138,168,92,169,170,171,15,172,173,174,69]+range(175,185)
                delay8 = [2,2,2,4,3,4,2,2,2,2,3,2,2,2,2,2,2,3,2,3,2,2,2,2,2,2,2,2,1]
                for i in range(29):
                        self.addLink(switchs[line8[i]], switchs[line8[i+1]], bw=1, delay=delay8[i], loss=0, max_queue_size=1000, use_htb=True)

                line9 = [185,42,186,187,169,188,189,190,142,20,60]+range(191,206)
                delay9 = [4,2,4,3,2,2,2,2,3,3,3,3,2,3,3,3,4,6,5,3,4,4,3,3,4]
                for i in range(25):
                        self.addLink(switchs[line9[i]], switchs[line9[i+1]], bw=1, delay=delay9[i], loss=0, max_queue_size=1000, use_htb=True)

                line10 = range(206,212)+[176,213,83,214,215,45,216,170,217,17,18,218,219,61]+range(220,226)+[54,55]
                delay10 = [1,2,3,2,2,2,2,2,2,3,2,2,3,2,3,3,2,3,2,2,3,2,2,2,3,4,1]
                for i in range(27):
                        self.addLink(switchs[line10[i]], switchs[line10[i+1]], bw=1, delay=delay10[i], loss=0, max_queue_size=1000, use_htb=True)
                self.addLink(switchs[223],switchs[237], bw=1, delay=4, loss=0, max_queue_size=1000, use_htb=True)
                self.addLink(switchs[237],switchs[301], bw=1, delay=2, loss=0, max_queue_size=1000, use_htb=True)
                self.addLink(switchs[301],switchs[302], bw=1, delay=3, loss=0, max_queue_size=1000, use_htb=True)

                line11 = range(226,233)+[132]+range(233,237)+[20,219,48,238,64]+range(239,248)+range(252,259)
                delay11 = [2,3,5,3,2,5,3,2,2,3,3,3,4,2,2,2,2,3,2,3,2,2,5,5,3,4,6,3,3,2,3,2]
                for i in range(32):
                        self.addLink(switchs[line11[i]], switchs[line11[i+1]], bw=1, delay=delay11[i], loss=0, max_queue_size=1000, use_htb=True)
                self.addLink(switchs[248],switchs[249], bw=1, delay=3, loss=0, max_queue_size=1000, use_htb=True)
                self.addLink(switchs[249],switchs[250], bw=1, delay=4, loss=0, max_queue_size=1000, use_htb=True)
                self.addLink(switchs[250],switchs[251], bw=1, delay=2, loss=0, max_queue_size=1000, use_htb=True)

                line12 = range(259,263)+[114]+range(263,269)+[85,269,270,215,172,13,46,17,190,94,141,235,58,22]+range(271,278)
                delay12 = [2,3,2,3,2,2,2,3,2,3,3,2,3,2,3,3,3,3,2,2,2,2,3,2,2,3,3,2,2,3,3]
                for i in range(31):
                        self.addLink(switchs[line12[i]], switchs[line12[i+1]], bw=1, delay=delay12[i], loss=0, max_queue_size=1000, use_htb=True)

                line13 = range(278,284)+[63,238,284,144,285,13,286,46,287,217,188,288,289]
                delay13 = [2,4,3,2,3,4,2,3,2,2,3,1,3,2,3,2,2,3]
                for i in range(18):
                        self.addLink(switchs[line13[i]], switchs[line13[i+1]], bw=1, delay=delay13[i], loss=0, max_queue_size=1000, use_htb=True)

                line16 = [39,290,228]+range(291,301)
                delay16 = [5,5,4,4,3,4,6,7,6,10,6,4]
                for i in range(12):
                        self.addLink(switchs[line16[i]], switchs[line13[i+1]], bw=1, delay=delay16[i], loss=0, max_queue_size=1000, use_htb=True)

topos={'mytopo':(lambda:MyTopo())}
                                                                                                                                                                                                                                           