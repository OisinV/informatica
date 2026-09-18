from turtle import * # type:ignore

for i in range(48):
    forward(20 + 10 * (i//4))
    right(120 if (i%4)==3 else 90)
