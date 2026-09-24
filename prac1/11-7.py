from turtle import *
bgcolor('lightgray')
speed(0)

kleuren = ['blue', 'white', 'red']

def flag(colorsFlag=[], size=[]):
    for i in range(len(colorsFlag)):
        color(colorsFlag[i])
        begin_fill()
        for j in range(2):
            forward(size[j+(j%2)])
            left(90)
            forward(size[j+(1+j%2)])
            left(90)
        end_fill()
        forward(size[0])

flag(['blue', 'white', 'red'], [60, 120, 60, 120])
teleport(xcor()+40, ycor()+120)
right(90)
flag(['black', 'red', 'yellow'], [40, 180, 40, 180])
