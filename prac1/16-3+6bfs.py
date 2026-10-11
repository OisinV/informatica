import turtle
import time
import math
from collections import deque

turtle.bgcolor('black')

coll = [ # pattern: x top left, y top left, x bottom right, y bottom right
    [ # wall sets:
        [-200, -200, -200, -200]
    ],
    [ # lava sets:
        [-200, -200, -200, -200]
    ]
]
c = False
hp, mhp = 100, 100
stopped = False
monact = False

p = turtle.Turtle()
r = turtle.Turtle()

# collision for monster + monster (needs implementation)
m = turtle.Turtle()

# debug turtle
dt = turtle.Turtle()

r.speed(0)
p.speed(0)
m.speed(0)

r.penup()
r.hideturtle()

m.color('green')
m.penup()

dt.speed(0)
dt.color('orange')

def cube(size:int, colour:str, collisionAdd:int=0):
    r.pendown()
    r.fillcolor(colour)
    r.begin_fill()
    match collisionAdd:
        case 1:
            coll[0].append([int(r.xcor()), int(r.ycor()), int(r.xcor())+size, int(r.ycor())+size])
        case 2:
            coll[1].append([int(r.xcor()), int(r.ycor()), int(r.xcor())+size, int(r.ycor())+size])
        case _:
            pass
    for _ in range(4):
        r.forward(size)
        r.left(90)
    r.end_fill()
    r.penup()

def wall(x:int, y:int, collisionAdd:int=0):
    r.teleport(x, y)
    cube(30, 'dimgray', collisionAdd)

def chest(x:int, y:int):
    r.teleport(x, y)
    cube(30, 'saddlebrown')
    r.teleport(x + 15, y + 15)
    r.dot(8, 'gold')

def isonobject():
    global hp, mhp
    if c == False:
        for i in range(1, len(coll)):
            for j in range(len(coll[i])):
                if (p.xcor() >= coll[i][j][0] and p.xcor() <= coll[i][j][2]) and (p.ycor() >= coll[i][j][1] and p.ycor() <= coll[i][j][3]):
                    hp = hp - 10
                    mhp = mhp - 10
    if hp <= 0:
        print('You died')
        time.sleep(5)
        stop()
    if monact:
        monstermove()
    elif not monact:
        m.hideturtle()
    check()

def monstermove():
    monstrt = (round(m.xcor()), round(m.ycor()))
    playpos = (round(p.xcor()), round(p.ycor()))
    directions = [ # all difference, so use dx, dy for calling :) (took me too long)
        (30, 0), # east 0
        (0, 30), # north 90
        (-30, 0), # west 180
        (0, -30) # south 270
    ]

    qeue = deque([monstrt])
    parent: dict[tuple[int, int], tuple[int, int] | None] = {monstrt:None}

    while qeue:
        current = qeue.popleft()

        if current == playpos:
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

    if playpos not in parent:
        return

    step: tuple[int, int] = playpos

    while True:
        previous = parent[step]

        if previous == None:
            return

        if previous == monstrt:
            break

        step = previous

    dx = step[0] - monstrt[0]
    dy = step[1] - monstrt[1]

    heading = {
        (30, 0): 0,
        (0, 30): 90,
        (-30, 0): 180,
        (0, -30): 270
    }[(dx, dy)]

    m.setheading(heading)
    m.forward(30)

world = [
    '############',
    '#..........#',
    '#..........#',
    '#..........#',
    '#..........#',
    '#..........#',
    '############',
]

y = 90
for row in world:
    x = -180
    for char in row:
        if char == '#':
            wall(x, y)
        if char == '.':
            r.teleport(x, y)
            cube(30, 'black')
        x = x + 30
    y = y - 30

p.penup()
p.teleport(-135, 75)
p.shape('turtle')
p.color('gold')

m.teleport(135, -45)

def build():
    r.setheading(0)
    r.teleport(r.xcor()-15, r.ycor()-15)
    cube(30, 'yellow')
    rendererReset()

def build_wall():
    rendererReset()
    r.setheading(0)
    wall(int(r.xcor())-15, int(r.ycor())-15, 1)
    rendererReset()

def build_lava():
    rendererReset()
    x = int(r.xcor())
    y = int(r.ycor())
    r.setheading(0)
    r.teleport(x-15, y-15)
    cube(30, 'orange', 2)
    r.teleport(x+5, y+5)
    r.dot(8, 'darkorange')
    r.teleport(x-5, y-5)
    r.dot(8, 'darkorange')
    rendererReset()

def forw30():
    if collision():
        p.forward(30)
    else:
        #print('No')
        pass
    rendererReset()

def gright():
    p.right(90)
    rendererReset()

def gleft():
    p.left(90)
    rendererReset()

def bckw30():
    if collision(turn=180):
        p.backward(30)
    else:
        #print('No')
        pass
    rendererReset()

def ctoggle():
    global c
    if c == True:
        c = False
    elif c == False:
        c = True

def monsteracon():
    global monact
    monact = True
    m.showturtle()

def isblock(x:int, y:int, at:turtle.Turtle=p):
    if x <= -150 or x >= 150:
        return True
    if y <= -60 or y >= 90:
        return True
    
    if c == True and at == p:
        return False
    
    for x1, y1, x2, y2 in coll[0]:
        if x1 <= x <= x2 and y1 <= y <= y2:
            return True
    
    return False

def des(at:turtle.Turtle, headto:float, step:int=30):
    theta = math.radians(headto)
    x = round(at.xcor() + math.cos(theta) * step)
    y = round(at.ycor() + math.sin(theta) * step)
    dt.teleport(x, y)
    return x, y

def collision(hwm:int=30, at:turtle.Turtle=p, turn:int=0):
    headto = (at.heading()-turn)%360
    x, y = des(at, headto, hwm)
    return not isblock(x, y, at)

def rendererReset(art:turtle.Turtle=r, aet:turtle.Turtle=p): # active renderer turtle, active entity turtle
    art.teleport(aet.xcor(), aet.ycor())
    art.setheading(aet.heading())

def erase():
    r.teleport(r.xcor()-15, r.ycor()-15)
    r.setheading(0)

    x, y = int(r.xcor()), int(r.ycor())
    t = [x, y, x+30, y+30]

    cube(30, 'black')

    for layer in coll:
        if t in layer:
            layer.remove(t)

    rendererReset()

def debug():
    print(coll)

rendererReset()

# check every 1 second "is on object?"
def check():
    global stopped
    if stopped == False:
        turtle.ontimer(isonobject, 1000)

check()

def stop():
    turtle.bye()
    global stopped
    stopped = True

turtle.onkey(forw30, 'Up')
turtle.onkey(gright, 'Right')
turtle.onkey(gleft, 'Left')
turtle.onkey(bckw30, 'Down')
turtle.onkey(build, 'b')
turtle.onkey(build_wall, 'm')
turtle.onkey(build_lava, 'l')
turtle.onkey(debug, '1')
turtle.onkey(stop, 's')
turtle.onkey(ctoggle, ',')
turtle.onkey(erase, 'e')
turtle.onkey(monsteracon, '0')
turtle.listen()
turtle.mainloop()
