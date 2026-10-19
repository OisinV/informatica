import turtle
from collections import deque
import math

# Ons spel: Pac-Man
# De held: Pac-Man
# Het doel: Alle wite bolletjes verzamelen
# Wat houdt de held tegen: 4 Spoken: inky, blinky, pinky en clyde

p = turtle.Turtle()
r = turtle.Turtle()

p.speed(0)
p.bgcolor('black')

r.speed(0)
r.ht()

begin_x = -240
begin_y = 150
collision: dict[tuple[int, int, int, int],int] = {}

GridOriginX = 15
GridOriginY = 15
GridStepSize = 30

WorldBiggestX = 240
WorldSmallestX = -240
WorldBiggestY = 150
WorldSmallestY = -660

level = 0

def blok(maat, kleur):
    r.fillcolor(kleur)
    r.begin_fill()
    for zijde in range(4):
        r.forward(maat)
        r.left(90)
    r.end_fill()

def muur(x, y):
    r.teleport(x, y)
    blok(30, 'Black')

def puntje(x, y):
    r.teleport(x, y)
    r.dot(8,'white')

def teleport(x, y):
    r.teleport(x, y)
    block (30, 'black')
    r.dot(8, 'yellow')
wereld = [
    '###################',
    '#oooooooo#oooooooo#',
    '#o##o###o#o###o##o#',
    '#o##o###o#o###o##o#',
    '#ooooooooooooooooo#',
    '#o##o#o#####o#o##o#',
    '#oooo#ooo#ooo#oooo#',
    '####o###o#o###o####',
    '...#o#ooooooo#o#...',
    '####o#o##.##o#o####',
    '....ooo#...#ooo....',
    '####o#o#####o#o####',
    '...#o#ooooooo#o#...',
    '####o#o#####o#o####',
    '#oooooooo#oooooooo#',
    '#o##o###o#o###o##o#',
    '#oo#ooooooooooo#oo#',
    '##o#o#o#####o#o#o##',
    '#oooo#ooo#ooo#oooo#',
    '#o######ooo######o#',
    '#ooooooooooooooooo#',
    '###################',
    
]

r.color('blue')
y = begin_y
for rij in wereld:
    x = begin_x
    for teken in rij:
        if teken == '#':
            muur(x, y)
        if teken == 'o':
            puntje(x+round(GridStepSize/2), y+round(GridStepSize/2))
        x = x + 30
    y = y - 30

# AI
def bfs(x:int, y:int, ai:turtle.Turtle):
    currpos = (round(ai.xcor()), round(ai.ycor())) # current position
    tarpos = (x, y) # target position
    directions = [ # all difference, so use dx, dy for calling :) (took me too long)
        (GridStepSize, 0), # east 0
        (0, GridStepSize), # north 90
        (-GridStepSize, 0), # west 180
        (0, -GridStepSize) # south 270
    ]

    qeue = deque([currpos])
    parent: dict[tuple[int, int], tuple[int, int] | None] = {currpos:None}

    while qeue:
        current = qeue.popleft()

        if current == tarpos:
            break

        for dx, dy in directions:
            nx = current[0] + dx
            ny = current[1] + dy
            nxt = (nx, ny)

            if nxt in parent:
                continue

            if isblock(nx, ny, m):
                continue

            parent[nxt] = current
            qeue.append(nxt)

    if tarpos not in parent:
        return

    step: tuple[int, int] = tarpos

    while True:
        previous = parent[step]

        if previous == None:
            return

        if previous == currpos:
            break

        step = previous

    dx = step[0] - currpos[0]
    dy = step[1] - currpos[1]

    heading = {
        (30, 0): 0,
        (0, 30): 90,
        (-30, 0): 180,
        (0, -30): 270
    }[(dx, dy)]

    ai.setheading(heading)
    ai.forward(30)

# Blinky


# De held
p.penup()
p.teleport(begin_x + 45, begin_y - 15)
p.shape('turtle')
p.color('gold')

def rechts():
    p.setheading(0)
#    p.forward(GridStepSize)

def links():
    p.setheading(180)
#    p.forward(GridStepSize)

def omhoog():
    p.setheading(90)
#    p.forward(GridStepSize)

def omlaag():
    p.setheading(270)
#    p.forward(GridStepSize)

# Tick Loop (elke 1s)
def TickLoop():
    # blinky, inky, pinky, clyde not yet finished
    ontimer(TickLoop, 500)
def WalkLoop():
    p.forward(30)
    t = 0
    min(20 - 5 * level)
    time = 500 / (1-t*0.01)
    ontimer(WalkLoop, time)

TickLoop()

onkey(rechts, 'Right')
onkey(links, 'Left')
onkey(omhoog, 'Up')
onkey(omlaag, 'Down')
listen()
