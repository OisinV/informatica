from turtle import *

n = int(input())
if (n%2) == 1:
    x = 2
    for i in range(n):
        forward(50)
        right(360*x/n)
elif n == 6:
    print("Nah mate, not happening")
elif (n%2) == 0:
    x = 3
    for i in range(n):
        forward(50)
        right(360*x/n)
