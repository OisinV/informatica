import turtle

turtle.speed(0)

size = 200

def triangle():
    for _ in range(3):
        turtle.forward(size)
        turtle.left(120)

triangle()
turtle.left(30)
turtle.penup()
turtle.forward(size + size/10)
turtle.pendown()
turtle.left(150)
triangle()

turtle.exitonclick()