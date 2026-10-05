from turtle import *

speed(0)
bgcolor('black')

def cube(size:int, colour0:str, colour1:str='NONE'):
    fillcolor(colour0)
    begin_fill()
    for zijde in range(4):
        forward(size)
        left(90)
    end_fill()
    if colour1 != 'NONE':
        teleport(xcor()+15, ycor()+15)
        dot(8, colour1)

def AUM():
    teleport

world = [
    '##..####..##',
    '#k........k#',
    '............',
    '#..........#',
    '##..####..##',
]

y = 90
for row in world:
    x = -180
    for char in row:
        if char == '#':
            teleport(x, y)
            cube(30, 'dimgray')
        if char == 'k':
            teleport(x, y)
            cube(30, 'saddlebrown', 'gold')
        x = x + 30
    y = y - 30



#teleport(x + 15, y + 15)
#dot(24, 'limegreen')
#teleport(x + 10, y + 18)
#dot(5, 'black')
#teleport(x + 20, y + 18)
#dot(5, 'black')
