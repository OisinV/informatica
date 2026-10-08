import turtle

bgcolor('black')

p = turtle.Turtle()
r = turtle.Turtle()

r.speed(0)
p.speed(0)
r.penup()
r.hideturtle()

def cube(size, colour):
    r.pendown()
    r.fillcolor(colour)
    r.begin_fill()
    for _ in range(4):
        r.forward(size)
        r.left(90)
    r.end_fill()
    r.penup()

def wall(x, y):
    r.teleport(x, y)
    cube(30, 'dimgray')

def chest(x, y):
    r.teleport(x, y)
    cube(30, 'saddlebrown')
    r.teleport(x + 15, y + 15)
    dot(8, 'gold')

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

#def tile():

# De bouwer
p.penup()
p.teleport(-135, 75)
p.shape('turtle')
p.color('gold')

# bouw(tegel) zet een tegel op het vakje waar de bouwer staat.
# Daarna staat de bouwer weer waar hij stond, en kijkt hij dezelfde kant op.
def build():
    r.setheading(0)
    r.teleport(r.xcor()-15, r.ycor()-15)
    cube(30, 'yellow')
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
    else:
        rt = True
    return rt

def rendererReset():
    while p.xcor() != r.xcor():
        r.teleport(p.xcor(), p.ycor())
    while p.ycor() != r.ycor():
        r.teleport(p.xcor(), p.ycor())
    while p.heading() != r.heading():
        r.setheading(p.heading())

rendererReset()

onkey(forw30, 'Up')
onkey(gright, 'Right')
onkey(gleft, 'Left')
onkey(bckw30, 'Down')
onkey(build, 'z')
listen()
