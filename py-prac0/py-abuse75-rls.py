def cube(size, colouring):
    fillcolor(colour[colouring]); begin_fill()
    for side in range(4): forward(size); left(90)
    end_fill(); forward(size)

def cloud(colouring):
    xstart, ystart = xcor(), ycor()
    for x, y in [(0, 0), (27, 0), (14, 6)]: teleport((xstart+x), (ystart+y)); dot(20, colour[colouring])

from turtle import *; hideturtle(); speed(0); bgcolor('deepskyblue'); colour = ['orange', 'yellow', 'white', 'green', 'red', 'brown']; teleports = [[-235, -235, -45, -45, 140, 140, -195, 140, 75, 90, -199, 181, 116, -110, 20], [125, 105, 125, 105, 125, 105, 55, 35, 100, 100, -130, -130, -130, -120, -120]]; text = ['MARIO', '0000100', 'WORLD', '1-1T', 'TIME', '390']; cube(20, 1); teleport(-80, -60); [teleport(teleports[0][i+6], teleports[1][i+6]) or cloud(2 if i < 4 else 3) for i in range(7)]; [teleport(teleports[0][i+13], teleports[1][i+13]) or dot(20, colour[i+4]) for i in range(2)]; teleport(-80, -60); [cube(20, (i % 2)) for i in range(8)]; teleport(-240, -150); [cube(20, 0) for i in range(24)]; color('white'); [teleport(teleports[0][i], teleports[1][i]) or write(text[i], font=('Courier', 11, 'bold')) for i in range(6)]

exitonclick()
