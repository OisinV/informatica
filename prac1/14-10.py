from turtle import *

speed(0)

def balk(breedte):
    fillcolor('teal')
    begin_fill()
    for zijde in range(2):
        forward(breedte)
        left(90)
        forward(15)
        left(90)
    end_fill()

rij = '#'
maat = 243
y = 120

for ronde in range(5):
    print(rij)
    x = -121
    for teken in rij:
        if teken == '#':
            teleport(x, y)
            balk(maat)
        x = x + maat
    rij = rij.replace('.', '...')
    rij = rij.replace('#', '#.#')
    maat = maat / 3
    y = y - 30
