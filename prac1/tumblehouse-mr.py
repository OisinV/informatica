from turtle import * # type:ignore

def house():
    for i in range(7):
        if i<5:
            left(90)
        else:
            left(45 if i == 5 else 90)
        forward(50 if i<5 else 35)

for x, y in [(-100, 0), (35, -35), (150, -50)]:
    teleport(x, y)
    house()
    left(90)
