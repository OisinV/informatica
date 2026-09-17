from turtle import * # type:ignore

def house():
    for i in range(7):
        if i<5:
            left(90)
        else:
            left(45 if i == 5 else 90)
        forward(50 if i<5 else 35)

for x in [-150, 0, 150]:
    teleport(x, 0)
    house()
    left(90)
