#copyright 2012-2013 James McCauley
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
A shortest-path forwarding application.
This is a standalone L2 switch that learns ethernet addresses
across the entire network and picks short paths between them.
You shouldn't really write an application this way -- you should
keep more state in the controller (that is, your flow tables),
and/or you should make your topology more static.  However, this
does (mostly) work. :)
Depends on openflow.discovery
Works with openflow.spanning_tree
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.recoco import Timer
from collections import defaultdict
from pox.openflow.discovery import Discovery
from pox.lib.util import dpid_to_str
import time

log = core.getLogger()

# Adjacency map.  [sw1][sw2] -> port from sw1 to sw2
adjacency = defaultdict(lambda:defaultdict(lambda:None))

# Switches we know of.  [dpid] -> Switch
switches = {}

# ethaddr -> (switch, port)
mac_map = {}

# [sw1][sw2] -> (distance, intermediate)
path_map = defaultdict(lambda:defaultdict(lambda:(None,None)))

# Waiting path.  (dpid,xid)->WaitingPath
waiting_paths = {}

# Time to not flood in seconds
FLOOD_HOLDDOWN = 5

# Flow timeouts
FLOW_IDLE_TIMEOUT = 10
FLOW_HARD_TIMEOUT = 30

# How long is allowable to set up a path?
PATH_SETUP_TIME = 4

linkdelay=defaultdict(lambda:defaultdict(lambda:(None,None)))

line1 = range(28)
delay1 = [2,2,3,3,2,3,2,3,3,2,2,3,1,2,2,3,2,2,2,2,3,2,3,3,3,2,2]
for i in range(27):
        linkdelay[(line1[i],line1[i+1])]=delay1[i]
        linkdelay[(line1[i+1],line1[i])]=delay1[i]
line2 = range(28,46)+[15]+range(46,57)
delay2 = [3,7,5,3,5,3,3,1,3,2,4,1,3,3,2,2,3,3,2,2,3,3,2,3,2,3,7,2,3]
for i in range(29):
        linkdelay[(line2[i],line2[i+1])]=delay2[i]
        linkdelay[(line2[i+1],line2[i])]=delay2[i]
line3 = [23]+range(57,63)+[49]+range(63,67)+[12]+range(67,83)
delay3 = [2,3,2,2,2,3,2,2,2,3,2,3,3,2,3,2,2,3,2,1,2,2,3,2,5,2,2,2]
for i in range(28):
        linkdelay[(line3[i],line3[i+1])]=delay3[i]
        linkdelay[(line3[i+1],line3[i])]=delay3[i]
line4 = range(60,63)+[49]+range(63,67)+[13,68]+range(83,88)+[43]+range(88,97)+[22]
delay4 = [2,2,2,1,2,3,2,3,2,2,2,3,2,2,2,2,3,3,3,2,3,1,3,2,2]
for i in range(25):
        linkdelay[(line4[i],line4[i+1])]=delay4[i]
        linkdelay[(line4[i+1],line4[i])]=delay4[i]
line5 = [27]+range(97,107)
delay5 = [2,2,4,3,3,2,3,2,3,2]
for i in range(10):
        linkdelay[(line5[i],line5[i+1])]=delay5[i]
        linkdelay[(line5[i+1],line5[i])]=delay5[i]
line6 = range(107,123)+[43,124,90]+range(124,133)
delay6 = [2,3,3,3,2,2,2,2,3,2,2,3,2,2,3,2,3,2,3,2,3,2,3,2,2,2,2]
for i in range(27):
        linkdelay[(line6[i],line6[i+1])]=delay6[i]
        linkdelay[(line6[i+1],line6[i])]=delay6[i]
line7 = [133,39,134,135,136,126]+range(137,142)+[95,142,18,47,143,144,65]+range(145,160)
delay7 = [3,2,3,2,3,2,2,2,2,3,2,2,3,2,3,2,2,3,2,2,2,2,3,2,2,3,3,6,3,2,4,2]
for i in range(32):
        linkdelay[(line7[i],line7[i+1])]=delay7[i]
        linkdelay[(line7[i+1],line7[i])]=delay7[i]
line8 = range(160,166)+[132,166,167,138,168,92,169,170,171,15,172,173,174,69]+range(175,185)
delay8 = [2,2,2,4,3,4,2,2,2,2,3,2,2,2,2,2,2,3,2,3,2,2,2,2,2,2,2,2,1]
for i in range(29):
        linkdelay[(line8[i],line8[i+1])]=delay8[i]
        linkdelay[(line8[i+1],line8[i])]=delay8[i]
line9 = [185,42,186,187,169,188,189,190,142,20,60]+range(191,206)
delay9 = [4,2,4,3,2,2,2,2,3,3,3,3,2,3,3,3,4,6,5,3,4,4,3,3,4]
for i in range(25):
        linkdelay[(line9[i],line9[i+1])]=delay9[i]
        linkdelay[(line9[i+1],line9[i])]=delay9[i]
line10 = range(206,212)+[176,213,83,214,215,45,216,170,217,17,18,218,219,61]+range(220,226)+[54,55]
delay10 = [1,2,3,2,2,2,2,2,2,3,2,2,3,2,3,3,2,3,2,2,3,2,2,2,3,4,1]
for i in range(27):
        linkdelay[(line10[i],line10[i+1])]=delay10[i]
        linkdelay[(line10[i+1],line10[i])]=delay10[i]
linkdelay[(223,237)]=4
linkdelay[(237,223)]=4
linkdelay[(237,301)]=2
linkdelay[(301,237)]=2
linkdelay[(301,302)]=3
linkdelay[(302,301)]=3
line11 = range(226,233)+[132]+range(233,237)+[20,219,48,238,64]+range(239,248)+range(252,259)
delay11 = [2,3,5,3,2,5,3,2,2,3,3,3,4,2,2,2,2,3,2,3,2,2,5,5,3,4,6,3,3,2,3,2]
for i in range(32):
        linkdelay[(line11[i],line11[i+1])]=delay11[i]
linkdelay[(249,250)]=4
linkdelay[(250,249)]=4
linkdelay[(250,251)]=2
linkdelay[(251,250)]=2
line12 = range(259,263)+[114]+range(263,269)+[85,269,270,215,172,13,46,17,190,94,141,235,58,22]+range(271,278)
delay12 = [2,3,2,3,2,2,2,3,2,3,3,2,3,2,3,3,3,3,2,2,2,2,3,2,2,3,3,2,2,3,3]
for i in range(31):
        linkdelay[(line12[i],line12[i+1])]=delay12[i]
        linkdelay[(line12[i+1],line12[i])]=delay12[i]
line13 = range(278,284)+[63,238,284,144,285,13,286,46,287,217,188,288,289]
delay13 = [2,4,3,2,3,4,2,3,2,2,3,1,3,2,3,2,2,3]
for i in range(18):
        linkdelay[(line13[i],line13[i+1])]=delay13[i]
        linkdelay[(line13[i+1],line13[i])]=delay13[i]
line16 = [39,290,228]+range(291,301)
delay16 = [5,5,4,4,3,4,6,7,6,10,6,4]
for i in range(12):
        linkdelay[(line16[i],line16[i+1])]=delay16[i]
        linkdelay[(line16[i+1],line16[i])]=delay16[i]

def _calc_paths ():
  """
  Essentially Floyd-Warshall algorithm
  """
  def dump ():
    for i in sws:
      for j in sws:
        a = path_map[i][j][0]
        #a = adjacency[i][j]
        if a is None: a = "*"
        print a,
      print

  sws = switches.values()
  path_map.clear()
  for k in sws:
    for j,port in adjacency[k].iteritems():
      if port is None: continue
      path_map[k][j] = (linkdelay[(k,j)],None)
    path_map[k][k] = (0,None) # distance, intermediate

  #dump()
  distance={}
  for k in sws:
    for i in sws:
      if path_map[k][i][0] is not None:
        distance[(k,i)]=path_map[k][i][0]
      else:
        distance[(k,i)]=999
  min_distance=999
  min_index=-2
  visited={}
  for source in sws:
    for i in sws:
      visited[i]=0
    for k in range(len(sws)):
      min_index=-2
      min_distance=999
      for i in sws:
        if visited[i]==0:
          if distance[(source,i)]<min_distance:
            min_distance=distance[(source,i)]
            min_index=i
      visited[min_index]=1
      for j in sws:
        if visited[j]==0:
          sourcej_dist = min_distance+distance[(min_index,j)]
          if sourcej_dist<distance[(source,j)]:
            # i -> k -> j is better than existing
            distance[(source,j)]=sourcej_dist
            path_map[source][j] = (sourcej_dist, min_index)

  #print "--------------------"
  #dump()


def _get_raw_path (src, dst):
  """
  Get a raw path (just a list of nodes to traverse)
  """
  if len(path_map) == 0: _calc_paths()
  if src is dst:
    # We're here!
    return []
  if path_map[src][dst][0] is None:
    return None
  intermediate = path_map[src][dst][1]
  if intermediate is None:
    # Directly connected
    return []
  return _get_raw_path(src, intermediate) + [intermediate] + \
         _get_raw_path(intermediate, dst)


def _check_path (p):
  """
  Make sure that a path is actually a string of nodes with connected ports
  returns True if path is valid
  """
  for a,b in zip(p[:-1],p[1:]):
    if adjacency[a[0]][b[0]] != a[2]:
      return False
    if adjacency[b[0]][a[0]] != b[1]:
      return False
  return True
  
def _get_path (src, dst, first_port, final_port):
  """
  Gets a cooked path -- a list of (node,in_port,out_port)
  """
  # Start with a raw path...
  if src == dst:
    path = [src]
  else:
    path = _get_raw_path(src, dst)
    if path is None: return None
    path = [src] + path + [dst]
    if path is None: return None
    print "src=",src," dst=",dst
    print time.time(),": ",path
  # Now add the ports
  r = []
  in_port = first_port
  for s1,s2 in zip(path[:-1],path[1:]):
    out_port = adjacency[s1][s2]
    r.append((s1,in_port,out_port))
    in_port = adjacency[s2][s1]
  r.append((dst,in_port,final_port))

  assert _check_path(r), "Illegal path!"

  return r


class WaitingPath (object):
  """
  A path which is waiting for its path to be established
  """
  def __init__ (self, path, packet):
    """
    xids is a sequence of (dpid,xid)
    first_switch is the DPID where the packet came from
    packet is something that can be sent in a packet_out
    """
    self.expires_at = time.time() + PATH_SETUP_TIME
    self.path = path
    self.first_switch = path[0][0].dpid
    self.xids = set()
    self.packet = packet

    if len(waiting_paths) > 1000:
      WaitingPath.expire_waiting_paths()

  def add_xid (self, dpid, xid):
    self.xids.add((dpid,xid))
    waiting_paths[(dpid,xid)] = self

  @property
  def is_expired (self):
    return time.time() >= self.expires_at

  def notify (self, event):
    """
    Called when a barrier has been received
    """
    self.xids.discard((event.dpid,event.xid))
    if len(self.xids) == 0:
      # Done!
      if self.packet:
        log.debug("Sending delayed packet out %s"
                  % (dpid_to_str(self.first_switch),))
        msg = of.ofp_packet_out(data=self.packet,
            action=of.ofp_action_output(port=of.OFPP_TABLE))
        core.openflow.sendToDPID(self.first_switch, msg)

      core.l2_multi.raiseEvent(PathInstalled(self.path))


  @staticmethod
  def expire_waiting_paths ():
    packets = set(waiting_paths.values())
    killed = 0
    for p in packets:
      if p.is_expired:
        killed += 1
        for entry in p.xids:
          waiting_paths.pop(entry, None)
    if killed:
      log.error("%i paths failed to install" % (killed,))


class PathInstalled (Event):
  """
  Fired when a path is installed
  """
  def __init__ (self, path):
    Event.__init__(self)
    self.path = path


class Switch (EventMixin):
  def __init__ (self):
    self.connection = None
    self.ports = None
    self.dpid = None
    self._listeners = None
    self._connected_at = None

  def __repr__ (self):
    return dpid_to_str(self.dpid)

  def _install (self, switch, in_port, out_port, match, buf = None):
    msg = of.ofp_flow_mod()
    msg.match = match
    msg.match.in_port = in_port
    msg.idle_timeout = FLOW_IDLE_TIMEOUT
    msg.hard_timeout = FLOW_HARD_TIMEOUT
    msg.actions.append(of.ofp_action_output(port = out_port))
    msg.buffer_id = buf
    switch.connection.send(msg)

  def _install_path (self, p, match, packet_in=None):
    wp = WaitingPath(p, packet_in)
    for sw,in_port,out_port in p:
      self._install(sw, in_port, out_port, match)
      msg = of.ofp_barrier_request()
      sw.connection.send(msg)
      wp.add_xid(sw.dpid,msg.xid)

  def install_path (self, dst_sw, last_port, match, event):
    """
    Attempts to install a path between this switch and some destination
    """
    p = _get_path(self, dst_sw, event.port, last_port)
    if p is None:
      log.warning("Can't get from %s to %s", match.dl_src, match.dl_dst)

      import pox.lib.packet as pkt

      if (match.dl_type == pkt.ethernet.IP_TYPE and
          event.parsed.find('ipv4')):
        # It's IP -- let's send a destination unreachable
        log.debug("Dest unreachable (%s -> %s)",
                  match.dl_src, match.dl_dst)

        from pox.lib.addresses import EthAddr
        e = pkt.ethernet()
        e.src = EthAddr(dpid_to_str(self.dpid)) #FIXME: Hmm...
        e.dst = match.dl_src
        e.type = e.IP_TYPE
        ipp = pkt.ipv4()
        ipp.protocol = ipp.ICMP_PROTOCOL
        ipp.srcip = match.nw_dst #FIXME: Ridiculous
        ipp.dstip = match.nw_src
        icmp = pkt.icmp()
        icmp.type = pkt.ICMP.TYPE_DEST_UNREACH
        icmp.code = pkt.ICMP.CODE_UNREACH_HOST
        orig_ip = event.parsed.find('ipv4')

        d = orig_ip.pack()
        d = d[:orig_ip.hl * 4 + 8]
        import struct
        d = struct.pack("!HH", 0,0) + d #FIXME: MTU
        icmp.payload = d
        ipp.payload = icmp
        e.payload = ipp
        msg = of.ofp_packet_out()
        msg.actions.append(of.ofp_action_output(port = event.port))
        msg.data = e.pack()
        self.connection.send(msg)

      return

    log.debug("Installing path for %s -> %s %04x (%i hops)",
        match.dl_src, match.dl_dst, match.dl_type, len(p))

    # We have a path -- install it
    self._install_path(p, match, event.ofp)

    # Now reverse it and install it backwards
    # (we'll just assume that will work)
    p = [(sw,out_port,in_port) for sw,in_port,out_port in p]
    self._install_path(p, match.flip())

  def _handle_PacketIn (self, event):
    def flood ():
      """ Floods the packet """
      if self.is_holding_down:
        log.warning("Not flooding -- holddown active")
      msg = of.ofp_packet_out()
      # OFPP_FLOOD is optional; some switches may need OFPP_ALL
      msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
      msg.buffer_id = event.ofp.buffer_id
      msg.in_port = event.port
      self.connection.send(msg)

    def drop ():
      # Kill the buffer
      if event.ofp.buffer_id is not None:
        msg = of.ofp_packet_out()
        msg.buffer_id = event.ofp.buffer_id
        event.ofp.buffer_id = None # Mark is dead
        msg.in_port = event.port
        self.connection.send(msg)

    packet = event.parsed

    loc = (self, event.port) # Place we saw this ethaddr
    oldloc = mac_map.get(packet.src) # Place we last saw this ethaddr

    if packet.effective_ethertype == packet.LLDP_TYPE:
      drop()
      return

    if oldloc is None:
      if packet.src.is_multicast == False:
        mac_map[packet.src] = loc # Learn position for ethaddr
        log.debug("Learned %s at %s.%i", packet.src, loc[0], loc[1])
    elif oldloc != loc:
      # ethaddr seen at different place!
      if core.openflow_discovery.is_edge_port(loc[0].dpid, loc[1]):
        # New place is another "plain" port (probably)
        log.debug("%s moved from %s.%i to %s.%i?", packet.src,
                  dpid_to_str(oldloc[0].dpid), oldloc[1],
                  dpid_to_str(   loc[0].dpid),    loc[1])
        if packet.src.is_multicast == False:
          mac_map[packet.src] = loc # Learn position for ethaddr
          log.debug("Learned %s at %s.%i", packet.src, loc[0], loc[1])
      elif packet.dst.is_multicast == False:
        # New place is a switch-to-switch port!
        # Hopefully, this is a packet we're flooding because we didn't
        # know the destination, and not because it's somehow not on a
        # path that we expect it to be on.
        # If spanning_tree is running, we might check that this port is
        # on the spanning tree (it should be).
        if packet.dst in mac_map:
          # Unfortunately, we know the destination.  It's possible that
          # we learned it while it was in flight, but it's also possible
          # that something has gone wrong.
          log.warning("Packet from %s to known destination %s arrived "
                      "at %s.%i without flow", packet.src, packet.dst,
                      dpid_to_str(self.dpid), event.port)


    if packet.dst.is_multicast:
      log.debug("Flood multicast from %s", packet.src)
      flood()
    else:
      if packet.dst not in mac_map:
        log.debug("%s unknown -- flooding" % (packet.dst,))
        flood()
      else:
        dest = mac_map[packet.dst]
        match = of.ofp_match.from_packet(packet)
        self.install_path(dest[0], dest[1], match, event)

  def disconnect (self):
    if self.connection is not None:
      log.debug("Disconnect %s" % (self.connection,))
      self.connection.removeListeners(self._listeners)
      self.connection = None
      self._listeners = None

  def connect (self, connection):
    if self.dpid is None:
      self.dpid = connection.dpid
    assert self.dpid == connection.dpid
    if self.ports is None:
      self.ports = connection.features.ports
    self.disconnect()
    log.debug("Connect %s" % (connection,))
    self.connection = connection
    self._listeners = self.listenTo(connection)
    self._connected_at = time.time()

  @property
  def is_holding_down (self):
    if self._connected_at is None: return True
    if time.time() - self._connected_at > FLOOD_HOLDDOWN:
      return False
    return True

  def _handle_ConnectionDown (self, event):
    self.disconnect()


class l2_multi (EventMixin):

  _eventMixin_events = set([
    PathInstalled,
  ])

  def __init__ (self):
    # Listen to dependencies
    def startup ():
      core.openflow.addListeners(self, priority=0)
      core.openflow_discovery.addListeners(self)
    core.call_when_ready(startup, ('openflow','openflow_discovery'))

  def _handle_LinkEvent (self, event):
    def flip (link):
      return Discovery.Link(link[2],link[3], link[0],link[1])

    l = event.link
    sw1 = switches[l.dpid1]
    sw2 = switches[l.dpid2]

    # Invalidate all flows and path info.
    # For link adds, this makes sure that if a new link leads to an
    # improved path, we use it.
    # For link removals, this makes sure that we don't use a
    # path that may have been broken.
    #NOTE: This could be radically improved! (e.g., not *ALL* paths break)
    clear = of.ofp_flow_mod(command=of.OFPFC_DELETE)
    for sw in switches.itervalues():
      if sw.connection is None: continue
      sw.connection.send(clear)
    path_map.clear()

    if event.removed:
      # This link no longer okay
      if sw2 in adjacency[sw1]: del adjacency[sw1][sw2]
      if sw1 in adjacency[sw2]: del adjacency[sw2][sw1]

      # But maybe there's another way to connect these...
      for ll in core.openflow_discovery.adjacency:
        if ll.dpid1 == l.dpid1 and ll.dpid2 == l.dpid2:
          if flip(ll) in core.openflow_discovery.adjacency:
            # Yup, link goes both ways
            adjacency[sw1][sw2] = ll.port1
            adjacency[sw2][sw1] = ll.port2
            # Fixed -- new link chosen to connect these
            break
    else:
      # If we already consider these nodes connected, we can
      # ignore this link up.
      # Otherwise, we might be interested...
      if adjacency[sw1][sw2] is None:
        # These previously weren't connected.  If the link
        # exists in both directions, we consider them connected now.
        if flip(l) in core.openflow_discovery.adjacency:
          # Yup, link goes both ways -- connected!
          adjacency[sw1][sw2] = l.port1
          adjacency[sw2][sw1] = l.port2

      # If we have learned a MAC on this port which we now know to
      # be connected to a switch, unlearn it.
      bad_macs = set()
      for mac,(sw,port) in mac_map.iteritems():
        if sw is sw1 and port == l.port1: bad_macs.add(mac)
        if sw is sw2 and port == l.port2: bad_macs.add(mac)
      for mac in bad_macs:
        log.debug("Unlearned %s", mac)
        del mac_map[mac]

  def _handle_ConnectionUp (self, event):
    sw = switches.get(event.dpid)
    if sw is None:
      # New switch
      sw = Switch()
      switches[event.dpid] = sw
      sw.connect(event.connection)
    else:
      sw.connect(event.connection)

  def _handle_BarrierIn (self, event):
    wp = waiting_paths.pop((event.dpid,event.xid), None)
    if not wp:
      #log.info("No waiting packet %s,%s", event.dpid, event.xid)
      return
    #log.debug("Notify waiting packet %s,%s", event.dpid, event.xid)
    wp.notify(event)


def launch ():
  core.registerNew(l2_multi)

  timeout = min(max(PATH_SETUP_TIME, 5) * 2, 15)
  Timer(timeout, WaitingPath.expire_waiting_paths, recurring=True)