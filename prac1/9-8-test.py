import turtle
import math

def triangle():
    for _ in range(3):
        turtle.forward(size)
        turtle.left(120)

n = int(input('How many sides? (default: 5) ') or '5')
size = int(input('How big does it need to be? (default: 50) ') or '50')

if n != 6:
    k = 2
    while math.gcd(n, k) != 1:
        k += 1
    
    for _ in range(n):
        turtle.forward(size)
        turtle.right(360*k/n)

elif n == 6: # the pissy 6 pointed star code, since it has to be special.
    triangle()
    turtle.left(30)
    turtle.penup()
    turtle.forward(size + size/10)
    turtle.pendown()
    turtle.left(150)
    triangle()

turtle.exitonclick()
