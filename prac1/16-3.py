import turtle
import time

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
hp = 100
stopped = False

p = turtle.Turtle()
r = turtle.Turtle()

r.speed(0)
p.speed(0)
r.penup()
r.hideturtle()

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
            # add "is within these coörds so delete" function, what to do?:
            # Check if it is with one of the coörds and then delete those coörds
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
    global hp
    if c == False:
        for i in range(1, len(coll)):
            for j in range(len(coll[i])):
                if (p.xcor() >= coll[i][j][0] and p.xcor() <= coll[i][j][2]) and (p.ycor() >= coll[i][j][1] and p.ycor() <= coll[i][j][3]):
                    hp = hp - 10
    if hp <= 0:
        print('You died')
        time.sleep(5)
        stop()
    check()

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
        x = x + 30
    y = y - 30

p.penup()
p.teleport(-135, 75)
p.shape('turtle')
p.color('gold')

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
    if collision() == True:
        p.right(180)
        p.forward(30)
        p.right(180)
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

def collision(hwm:int=30):
    r.forward(hwm)
    rt = False
    if r.xcor() >= 150:
        rt = False
    elif r.xcor() <= -150:
        rt = False
    elif r.ycor() >= 90:
        rt = False
    elif r.ycor() <= -60:
        rt = False
    elif andsy() == True:
        rt = False
    else:
        rt = True
    return rt

def andsy():
    if c == True:
        return False
    for i in range(len(coll[0])):
        if (r.xcor() >= coll[0][i][0] and r.xcor() <= coll[0][i][2]) and (r.ycor() >= coll[0][i][1] and r.ycor() <= coll[0][i][3]):
            return True
    return False

def rendererReset():
    r.teleport(p.xcor(), p.ycor())
    r.setheading(p.heading())

def erase():
    r.teleport(r.xcor()-15, r.ycor()-15)
    r.setheading(0)
    cube(30, 'black', -1)
    rendererReset()

def debug():
    print('rcor: ' + str(r.xcor()) + ' ' + str(r.ycor()) + ', coll: ' + str(coll) + ', hp: ' + str(hp))

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
turtle.onkey(debug, 'd')
turtle.onkey(stop, 's')
turtle.onkey(ctoggle, ',')
turtle.onkey(erase, 'e')
turtle.listen()
turtle.mainloop()
