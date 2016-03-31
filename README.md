# xuyangwu.github.io
Read me:

  There is three document about dijkstra algorithm, where dijkstra_origion.py was based on the l2_multi.py and just change the routing algorithm from floyd to dijkstra,
  however, this waste a lot of computations, about n^3, therefore we create the dijkstra_reasonable to repair this problem, and reduce the complexity
  of calculating shortest paths between two hosts from n^3 to n^2, and that is more reasonable, because there is two cases that the switch will call the function
  to calculate the path, 
  1) there is no paths or wrong paths between tw switches
  2) timeout
  For the first case, we just need to construct the shortest paths between two switches, n^3 of calculations is too high
  These two document can be applied to possibly every topos, however, the third document dijkstra_for_subway.py, it add some specific information of the subway network,
  therefore, it can not be applied to other topos.
  
  The topo was completed together by XinGao, Xuyang Wu, Zhaoxi Wu
  
  The Bellman-ford document also need modification, because some times it will failed because of some reasons
