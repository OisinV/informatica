import turtle
import math

turtle.speed(0)

size = 200

def triangle():
    for _ in range(3):
        turtle.forward(size)
        turtle.left(120)

triangle()
turtle.left(30)
turtle.teleport(turtle.xcor() + (size + size/10) * math.cos(math.radians(turtle.heading())), turtle.ycor() + (size + size/10) * math.sin(math.radians(turtle.heading())))
turtle.left(150)
triangle()

turtle.exitonclick()