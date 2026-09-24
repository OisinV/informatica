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
            print('1: ' + str(size[j+(j%2)]))
            left(90)
            forward(size[j+(1)])
            print('2: ' + str(size[j+(1)]))
            left(90)
        end_fill()
        forward(60)

flag(['blue', 'white', 'red'], [60, 120, 60, 120])
#forward(40)
#right(90)
#flag(['black', 'red', 'yellow'], [120, 60, 120, 60])
