README

The two folders contain test cases for the Euclidean Steiner tree problem with soft and solid obstacles or a mix thereof.  Two files named

obstaclei.csv   and  terminalsi.csv,

where i is the problem instance number,  belong together to build one test instance.

The files are organised as follows:

- In the obstacle file  each obstacle is separated by an empty line. For each obstacle the first number contains the obstacle's crossing weight followed by the x- and y-coordinated of the polygon's corner points in the order the edges are connected. The last corner point is supposed to be connect back to the first one. In case of a solid obstacle the crossing weight says "max".  

  Examples are:

  

  for two solid obstacles:

  max														
  3.4225,	3.76125
  5.5625,	4.40125
  6.2825,	6.16125
  7.4225,	4.82125
  7.7225,	3.02125
  5.5,	2.8
  	
  max	
  1.25,	6.2
  2.2,	4.8
  0.5,	5



​	and for two soft obstacles:

​	1.1	
​	0.098,	0.9
​	0.21,	0.902
​	0.204,	0.488
​	0.094,	0.488
​	
​	1.1	
​	0.602,	0.81
​	0.578,	0.6
​	0.766,	0.466
​	0.912,	0.704
​	0.72,	0.622
​	0.718,	0.834



- The  terminal file contains the x- and y-coordinates of the terminals. The first line can be ignored. An example is given below

  Xcoord,	Ycoord
  0.644,	0.242
  0.24,	0.386
  0.048,	0.39
  0.152,	0.15
  0.654,	0.698
  0.526,	0.87
  0.156,	0.85
  0.43,	0.59
  0.91,	0.72
  0.88,	0.634
  0.728,	0.406



Note: 

Some of the problem instances in the "Soft" folder contain the points for the Sierpinski triangle instance. This was adapted from 

Garrote et al. (2019) "Weighted Euclidean Steiner Trees for Disaster-Aware Network Design", IEEE,*15th International Conference on the Design of Reliable Communication Networks, DRCN 2019* 