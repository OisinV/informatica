from turtle import *

for i in range(48):
    forward(20 + 10 * int(i/4))
    right(90)
    right(30 if (i%4)==3 else 0)
