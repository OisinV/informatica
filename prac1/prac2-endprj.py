import turtle
from collections import deque
import time
import math

# Ons spel:
# De held:
# Het doel:
# Wat houdt de held tegen:

p = turtle.Turtle()

p.speed(0)
p.bgcolor('black')

begin_x = -240
begin_y = 150
gStepSize = 30
collision: dict[tuple[int, int, int, int],int] = {}

def blok(maat, kleur):
    p.fillcolor(kleur)
    p.begin_fill()
    for zijde in range(4):
        p.forward(maat)
        p.left(90)
    p.end_fill()

def muur(x, y):
    p.teleport(x, y)
    blok(30, 'Black')

wereld = [
    '###################',
    '#........#........#',
    '#.##.###.#.###.##.#',
    '#.##.###.#.###.##.#',
    '#.................#',
    '#.##.#.#####.#.##.#',
    '#....#...#...#....#',
    '####.###.#.###.####',
    '...#.#.......#.#...',
    '####.#.......#.####',
    '...................',
    '####.#.......#.####',
    '...#.#.......#.#...',
    '####.#.#####.#.####',
    '#........#........#',
    '#........#........#',
    '#.................#',
    '#....#.#####.#....#',
    '#....#...#...#....#',
    '#.######.#.######.#',
    '#.................#',
    '###################',
    
]

y = begin_y
for rij in wereld:
    x = begin_x
    for teken in rij:
        if teken == '#':
            p.color('blue')
            muur(x, y)
        x = x + 30
    y = y - 30

# AI
def bfs(x:int, y:int, ai:turtle.Turtle):
    currpos = (round(ai.xcor()), round(ai.ycor())) # current position
    tarpos = (x, y) # target position
    directions = [ # all difference, so use dx, dy for calling :) (took me too long)
        (30, 0), # east 0
        (0, 30), # north 90
        (-30, 0), # west 180
        (0, -30) # south 270
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
penup()
teleport(begin_x + 45, begin_y - 15)
shape('turtle')
color('gold')

def rechts():
    p.setheading(0)
    p.forward(gStepSize)

def links():
    p.setheading(180)
    p.forward(gStepSize)

def omhoog():
    p.setheading(90)
    p.forward(gStepSize)

def omlaag():
    p.setheading(270)
    p.forward(gStepSize)

# Tick Loop (elke 1s)


onkey(rechts, 'Right')
onkey(links, 'Left')
onkey(omhoog, 'Up')
onkey(omlaag, 'Down')
listen()
