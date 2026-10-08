import turtle

speed(0)
bgcolor('black')

p = turtle.Turtle()
r = turtle.Turtle()

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

# De bouwer
p.penup()
p.teleport(-135, 75)
p.shape('turtle')
p.color('gold')

# bouw(tegel) zet een tegel op het vakje waar de bouwer staat.
# Daarna staat de bouwer weer waar hij stond, en kijkt hij dezelfde kant op.
def build(tile):
    r.setheading(0)
    r.tile(x - 15, y - 15)

def forw30():
    if collision() == True:
        p.forward(30)
    else:
        print('No')

def gright():
    p.right(90)

def gleft():
    p.left(90)

def bckw30():
    if collision() == True:
        p.forward(30)
    else:
        print('No')

def collision(hwm:int=30):
    r.forward(hwm)
    if r.xcor() >= 180:
        return False
    elif r.xcor() <= -180:
        return False
    elif r.ycor() >= 90:
        return False
    elif r.ycor() <= -90:
        return False
    else:
        return True

while p.xcor() != r.xcor():
    r.teleport(p.xcor(), p.ycor())
while p.ycor() != r.ycor():
    r.teleport(p.xcor(), p.ycor())
while p.heading() != r.heading():
    r.setheading(p.heading())

onkey(forw30, 'Up')
listen()
