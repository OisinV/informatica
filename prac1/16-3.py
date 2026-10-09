import turtle
import time
import math

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

p = turtle.Turtle()
r = turtle.Turtle()

# collision for monster + monster (needs implementation)
mc = turtle.Turtle()
m = turtle.Turtle()

r.speed(0)
p.speed(0)
mc.speed(0)
m.speed(0)
r.penup()
r.hideturtle()
mc.penup()
mc.hideturtle()
m.penup()

def cube(size:int, colour:str, collisionAdd:int=0):
    r.pendown()
    r.fillcolor(colour)
    r.begin_fill()
    match collisionAdd:
        case 1:
            coll[0].append([int(r.xcor()), int(r.ycor()), int(r.xcor())+size, int(r.ycor())+size])
        case 2:
            coll[1].append([int(r.xcor()), int(r.ycor()), int(r.xcor())+size, int(r.ycor())+size])
        case -1:
            for i in range(len(coll)):
                for j in range(len(coll[i])):
                    if (p.xcor() >= coll[i][j][0] and p.xcor() <= coll[i][j][2]) and (p.ycor() >= coll[i][j][1] and p.ycor() <= coll[i][j][3]):
                        try:
                            coll[i].remove([int(r.xcor()), int(r.ycor()), int(r.xcor())+size, int(r.ycor())+size])
                            break
                        except ValueError:
                            pass
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
    monstermove()
    check()

def monstermove():
    dx = p.xcor() - m.xcor()
    dy = p.ycor() - m.ycor()
    turnamount = math.degrees(math.atan2(dy, dx))
    
    turnamount = round(turnamount / 90) * 90
    t = turnamount

    m.setheading(turnamount)
    
    if collision(at=mc, aet=mc) == True:
        m.forward(30)
    elif collision(at=mc, turn=90, aet=mc) == True:
        m.right(90)
        m.forward(30)
    elif collision(at=mc, turn=-90, aet=mc) == True:
        m.right(-90)
        m.forward(30)
    elif collision(at=mc, turn=180, aet=mc) == True:
        m.right(180)
        m.forward(30)
    rendererReset(art=mc, aet=m)

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
    if collision() == True:
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
    r.right(180)
    if collision() == True:
        p.backward(30)
    else:
        #print('No')
        pass
    r.right(180)
    rendererReset()

def ctoggle():
    global c
    if c == True:
        c = False
    elif c == False:
        c = True

def isblock(x):
    if x <= -150 or x >= 150:
        return True
    if y <= -60 or y >= 90:
        return True
    
    if c:
        return False
    
    for x1, y1, x2, y2 in coll[0]:
        if x1 <= x <= x2 and y1 <= y <= y2:
            return True
    
    return False

def collision(hwm:int=30, at:turtle.Turtle=r, turn:int=0, aet:turtle.Turtle=p):
    rendererReset(at, aet)
    if turn != 0: at.right(turn)
    at.forward(hwm)
    rt = False
    if at.xcor() >= 150:
        rt = False
    elif at.xcor() <= -150:
        rt = False
    elif at.ycor() >= 90:
        rt = False
    elif at.ycor() <= -60:
        rt = False
    elif andsy(at) == True:
        rt = False
    else:
        rt = True
    return rt

def andsy(at:turtle.Turtle=r):
    if c == True:
        return False
    for i in range(len(coll[0])):
        if (at.xcor() >= coll[0][i][0] and at.xcor() <= coll[0][i][2]) and (at.ycor() >= coll[0][i][1] and at.ycor() <= coll[0][i][3]):
            return True
    return False

def rendererReset(art:turtle.Turtle=r, aet:turtle.Turtle=p): # active renderer turtle, active entity turtle
    art.teleport(aet.xcor(), aet.ycor())
    art.setheading(aet.heading())

def erase():
    r.teleport(r.xcor()-15, r.ycor()-15)
    r.setheading(0)
    cube(30, 'black', -1)
    rendererReset()

#def debug():
#    print('rcor: ' + str(r.xcor()) + ' ' + str(r.ycor()) + ', coll: ' + str(coll) + ', hp: ' + str(hp))

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
#turtle.onkey(debug, 'd')
turtle.onkey(stop, 's')
turtle.onkey(ctoggle, ',')
turtle.onkey(erase, 'e')
turtle.listen()
turtle.mainloop()
