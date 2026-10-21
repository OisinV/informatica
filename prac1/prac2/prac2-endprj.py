import turtle
from collections import deque
import math
from typing import Any
from playsound3 import playsound #type:ignore

# Ons spel: Pac-Man
# De held: Pac-Man
# Het doel: Alle wite bolletjes verzamelen (en naar level 255 te gaan)
# Wat houdt de held tegen: 4 Spoken: inky, blinky, pinky en clyde

# Object ID list:
# -2 = Pylance Error Negation
# -1 = Deleted
# 0 = Wall/Cube (No special effects)
# 1 = Teleporter
# 2 = Pelet
# 3 = Power Pelet

p = turtle.Turtle()
r = turtle.Turtle()

p.speed(0)
turtle.bgcolor('black')

r.speed(0)
r.ht()

debug = False

begin_x = -240
begin_y = 150
# (left most x, right most x, bottom most y, top most y) : (TypeID, ObjID)
collision: dict[tuple[int, int, int, int],tuple[int, int]] = {}
ObjData: list[dict[str, Any]] = []
CollisionIDs:tuple[int, ...] = (0,) # a tuple containing if they should do collision

GridOriginX = 75
GridOriginY = -255
GridStepSize = 30

WorldBiggestX = 390
WorldSmallestX = -240
WorldBiggestY = 180
WorldSmallestY = -660

level = 0
Points = 0
Dots = 244

# Grid
def On_Grid(x:int|float, y:int|float) -> bool:
    if GridStepSize <= 0:
        raise RuntimeError(
            "You need to initialize the Grid Step Size before using most of this module!\nUse Set_Grid() with GridStep as not blank."
        )

    x = int(round(x))
    y = int(round(y))

    return (
        (x - GridOriginX) % GridStepSize == 0
        and (y - GridOriginY) % GridStepSize == 0
    )

def GridCoords(x:int|float,y:int|float):
    if GridStepSize <= 0:
        raise RuntimeError(
            "You need to initialize the Grid Step Size before using most of this module!\nUse Set_Grid() with GridStep as not blank."
        )
    x = int(round(((x-GridOriginX) / GridStepSize))*GridStepSize + GridOriginX)
    y = int(round(((y-GridOriginY) / GridStepSize))*GridStepSize + GridOriginY)
    return x, y

# Collision
def Collision_Coord_Check(
        x:int|float,
        y:int|float,
        *,
        lbObjID:bool=False
    ) -> tuple[int|None, int|None] | int | None:
    x = int(round(x))
    y = int(round(y))
    TypeID = 0

    if not (WorldSmallestX <= x <= WorldBiggestX):
        if lbObjID:
            return 0, None
        else:
            return 0
    if not (WorldSmallestY <= y <=  WorldBiggestY):
        if lbObjID:
            return 0, None
        else:
            return 0
    
    for x1, x2, y1, y2 in collision:
        if x1 <= x <= x2 and y1 <= y <= y2:
            TypeID:int = collision[x1, x2, y1, y2][0]
            if lbObjID:
                ObjID:int = collision[x1, x2, y1, y2][1]
                return TypeID, ObjID
            else:
                return TypeID

    if lbObjID:
        return None, None
    else:
        return None

def Destination_Calculator(x:int|float, y:int|float, heading:float, step:int|float):
    theta = math.radians(heading)
    x = round(x + math.cos(theta) * step)
    y = round(y + math.sin(theta) * step)
    return x, y

# Ex:
# Delta = How much change between new and old coörds is desired
# x = current xcor
# y = current ycor
# Heading = for turtle: turtle.heading(), basically; where is the turtle looking
# turn = How much do you want the turtle to turn extra before checking? (For rotations)
def Collision_Check(
        x:int|float,
        y:int|float,
        heading:int|float,
        turn:int|float|None=None,
        slices:int=1,
        delta:int|float|None=None
    ):
    if slices <= 0:
        raise ValueError("The amount of slices must be a positive interger.")

    if delta == None:
        delta = GridStepSize

    if delta < 0:
        raise ValueError("Delta cannot be negative.")

    if turn == None:
        turn = 0

    slices = min(slices, max(1, math.ceil(abs(delta))))
    headto = (heading-turn)%360

    for i in range(1, slices+1):
        dis = int(round(delta*i/slices))
        rx, ry = Destination_Calculator(x, y, headto, dis)
        if Collision_Coord_Check(rx, ry) in CollisionIDs:
            return False
    return True

# Collision Change Code
def Collision_Object_Calculator(
        x:int|float,
        y:int|float,
        *,
        coordinates: tuple[int|float, int|float] | None = None,
        size: tuple[int|float, int|float|None] | int | None=None
    ) -> tuple[int, int, int, int]:
    

    if size != None:
        x = int(round(x))
        y = int(round(y))
        if isinstance(size, int):
            width = size
            height = size
        else:
            width = size[0]
            height = size[1]

        if height == None:
            height = width

        collisionobj: tuple[int, int, int, int] = (
            int(math.floor(x-width/2)),
            int(math.ceil(x+width/2)),
            int(math.floor(y-height/2)),
            int(math.ceil(y+height/2))
        )

    elif coordinates != None:
        x0 = int(round(min(x, coordinates[0])))
        x1 = int(round(max(x, coordinates[0])))
        y0 = int(round(min(y, coordinates[1])))
        y1 = int(round(max(y, coordinates[1])))
    
        collisionobj: tuple[int, int, int, int] = (
            int(x0),
            int(x1),
            int(y0),
            int(y1)
        )
    else:
        raise LookupError(
            "WHAT? Please report this to github!\nAs I currently, while writing this code cannot imagine this situation.\nhttps://github.com/OisinV/informatica/issues"
        ) # Yes, imported code from my lib
        
    return collisionobj

def Create_Collision_Object(
        x:int|float,
        y:int|float,
        *,
        coordinates: tuple[int|float, int|float] | None = None,
        size: tuple[int|float, int|float|None] | int | None=None,
        TypeID: int|None=None,
        ObjID: int|None=None
    ) -> tuple[tuple[int, int, int, int], int]:

    if TypeID == None:
        TypeID = 0
    

    if coordinates != None and size != None:
        raise ValueError(
            "Cannot use x1/y1 together with width/height."
        )

    if (coordinates == None) and (size == None):
        raise ValueError(
            "Provide either x1/y1 or width with optionally height.\nAlso x1/y1 and width/height also cannot be used together."
        )

    collisionobj = Collision_Object_Calculator(x, y, coordinates=coordinates, size=size)

    if ObjID == None:
        ObjID = len(ObjData)

    collision[collisionobj] = (TypeID, ObjID)
    ObjData.append({'Disabled':False, 'Type':TypeID})
    return collisionobj, ObjID

def Remove_Collision_Object(
        x:int|float,
        y:int|float,
        *,
        coordinates: tuple[int|float, int|float] | None = None,
        size: tuple[int|float, int|float|None] | int | None=None,
        TypeID: tuple[int, ...]|int|None=None
    ) -> tuple[tuple[int, int, int, int], bool]:

    if TypeID == None:
        TypeID = 0
    

    if coordinates != None and size != None:
        raise ValueError(
            "Cannot use x1/y1 together with width/height."
        )

    if (coordinates == None) and (size == None):
        raise ValueError(
            "Provide either x1/y1 or width with optionally height.\nAlso x1/y1 and width/height also cannot be used together."
        )

    collisionobj = Collision_Object_Calculator(x, y, coordinates=coordinates, size=size)

    s = False

    def deletus():
            c = collision[collisionobj][1]
            v = collision[collisionobj][0]
            ObjData[c]['Disabled'] = True
            ObjData[c]['Type'] = v
            collision[collisionobj] = (-1, c)
            s = True # type:ignore

    if collisionobj in collision:
        if isinstance(TypeID, tuple):
            if -1 in TypeID:
                deletus()
            elif collision[collisionobj][0] in TypeID:
                deletus()
        else:
            if collision[collisionobj][0] == TypeID:
                deletus()
            elif TypeID == -1:
                deletus()
    return collisionobj, s

def Undelete_Collision_Object(
        x:int|float,
        y:int|float,
        *,
        coordinates: tuple[int|float, int|float] | None = None,
        size: tuple[int|float, int|float|None] | int | None=None,
        TypeID: int|None=None
    ) -> tuple[tuple[int, int, int, int], int]:

    collisobj = Collision_Object_Calculator(x, y, coordinates=coordinates, size=size)
    ObjID = collision[collisobj][1]

    if TypeID == None:
        TypeID = int(ObjData[ObjID]['Type'])    

    if coordinates != None and size != None:
        raise ValueError(
            "Cannot use x1/y1 together with width/height."
        )

    if (coordinates == None) and (size == None):
        raise ValueError(
            "Provide either x1/y1 or width with optionally height.\nAlso x1/y1 and width/height also cannot be used together."
        )

    collisionobj = Collision_Object_Calculator(x, y, coordinates=coordinates, size=size)

    collision[collisionobj] = (TypeID, ObjID)
    ObjData.append({'Disabled':False})
    return collisionobj, ObjID

class UnknownError(Exception):
    pass

def blok(maat:int|float, kleur:str):
    r.fillcolor(kleur)
    r.begin_fill()
    for _ in range(4):
        r.forward(maat)
        r.left(90)
    r.end_fill()

def muur(x:int|float, y:int|float):
    r.teleport(x, y)
    blok(30, 'Black')

def puntje(x:int|float, y:int|float, lsize:int|float=8):
    r.teleport(x, y)
    r.dot(int(round(lsize)),'white')

#def teleport(x:int|float, y:int|float):
#    r.teleport(x, y)
#    blok(30, 'black')
#    r.dot(8, 'yellow')

Teleporter1ID:int|None = None
def TeleporterCreator(x:int|float, y:int|float):
    Tupped = Create_Collision_Object(x, y, size=(30, None), TypeID=1)
    ObjID = Tupped[1]
    collisobj = Tupped[0]
    GridHalfStep = int(round(GridStepSize / 2))
    TeleportPointX = int(round((collisobj[0] + collisobj[1])/2))+GridHalfStep # X middle of the teleporter
    TeleportPointY = int(round((collisobj[2] + collisobj[3])/2))+GridHalfStep # Y middle of the teleporter
    ObjData[ObjID]['TeleportPointX'] = TeleportPointX
    ObjData[ObjID]['TeleportPointY'] = TeleportPointY

    global Teleporter1ID
    if Teleporter1ID == None:
        Teleporter1ID = ObjID
    else:
        # To-Do: 2nd teleporter ID to linked of 1st then 1st teleporter ID to linked of 2nd,
        # then when teleport is called (check disabled),
        # use linked as to point where to teleport and turn 180.
        ObjData[ObjID]['Linked'] = Teleporter1ID
        ObjData[Teleporter1ID]['Linked'] = ObjID
        Teleporter1ID = None

wereld = [
    '.###################.',
    '.#oooooooo#oooooooo#.',
    '.#*##o###o#o###o##*#.',
    '.#o##o###o#o###o##o#.',
    '.#ooooooooooooooooo#.',
    '.#o##o#o#####o#o##o#.',
    '.#oooo#ooo#ooo#oooo#.',
    '.####o###o#o###o####.',
    '....#o#ooooooo#o#....',
    '.####o#o##d##o#o####.',
    't....ooo#...#ooo....t',
    '.####o#o#####o#o####.',
    '....#o#ooooooo#o#....',
    '.####o#o#####o#o####.',
    '.#oooooooo#oooooooo#.',
    '.#o##o###o#o###o##o#.',
    '.#*o#ooooooooooo#o*#.',
    '.##o#o#o#####o#o#o##.',
    '.#oooo#ooo#ooo#oooo#.',
    '.#o######o#o######o#',
    '.#ooooooooooooooooo#.',
    '.###################.',
    
]

r.color('blue')
y = begin_y
for rij in wereld:
    x = begin_x
    for teken in rij:
        if teken == '#':
            Create_Collision_Object(x+round(GridStepSize/2), y+round(GridStepSize/2), coordinates=(x+30, y+30), TypeID=0)
            muur(x, y)
        if teken == 't':
            TeleporterCreator(x, y)
        if teken == 'o':
            Create_Collision_Object(x+round(GridStepSize/2), y+round(GridStepSize/2), coordinates=(x+30, y+30), TypeID=2)
            puntje(x+round(GridStepSize/2), y+round(GridStepSize/2))
        if teken == '*':
            Create_Collision_Object(x+round(GridStepSize/2), y+round(GridStepSize/2), coordinates=(x+30, y+30), TypeID=3)
            puntje(x+round(GridStepSize/2), y+round(GridStepSize/2), 14)
        x = x + 30
    y = y - 30

def ResetDots():
    y = begin_y
    for row in wereld:
        x = begin_x
        for char in row:
            if char == 'o':
                puntje(x+round(GridStepSize/2), y+round(GridStepSize/2))
            if char == '*':
                puntje(x+round(GridStepSize/2), y+round(GridStepSize/2), 14)
            x += 30
        y -= 30

# AI
def bfs(StartX:int|float, StartY:int|float, StartHeading:int|float, GoalX:int|float, GoalY:int|float):
    def TeleporterDesti(x:int, y:int): #type:ignore
        ccc = Collision_Coord_Check(x, y, lbObjID=True)
        if isinstance(ccc, tuple):
            TypeID, ObjID = ccc
        else: return None

        if TypeID != 1 or ObjID == None:
            return None

        PorDat = ObjData[ObjID]
        LinkedID = PorDat['Linked']

        if LinkedID == None:
            return None

        LinkDat: dict[str, Any] = ObjData[LinkedID] #type:ignore

        if PorDat['Disabled'] or LinkDat['Disabled']:
            return None

        LinkTPX = LinkDat['TeleportPointX'] #type:ignore
        LinkTPY = LinkDat['TeleportPointY'] #type:ignore

        if not On_Grid(LinkTPX, LinkTPY): #type:ignore
            LinkTPX, LinkTPY = GridCoords(LinkTPX, LinkTPY) #type:ignore

        return LinkTPX, LinkTPY #type:ignore
    
    global GridStepSize
    if GridStepSize <= 0:
        raise RuntimeError("Call Set_Grid to initialize this module's grid, as currently GridStepSize is 0 or a negative integer.")
    GridSize = GridStepSize

    StartHeadto = int(float(StartHeading))
    Start:tuple[int, int] = (int(round(StartX)), int(round(StartY)))
    MovStart = (StartHeadto, *Start)
    Goal:tuple[int, int] = (int(round(GoalX)), int(round(GoalY)))
    directions = { # all difference, so use dx, dy for calling :) (took me too long)
        0 : (GridSize, 0), # east 0
        90 : (0, GridSize), # north 90
        180 : (-GridSize, 0), # west 180
        270 : (0, -GridSize) # south 270
    }
    #directions.pop((StartHeadto + 180)%360)
    #direcval = list(directions.values())
    #direckeys = list(directions.keys())
    #directions = {
    #    direcval[0]: direckeys[0],
    #    direcval[1]: direckeys[1],
    #    direcval[2]: direckeys[2],
    #    direcval[3]: direckeys[3]
    #}

    if not On_Grid(StartX, StartY):
        return False

    if not On_Grid(GoalX, GoalY):
        return False

    if Collision_Coord_Check(*Start) in CollisionIDs:
        return False

    if Collision_Coord_Check(*Goal) in CollisionIDs:
        return False
    
    qeue = deque([Start])
    # Child (rotation, x, y) : Parent (rotation, x, y)
    parent: dict[tuple[int, int],tuple[int, int, int] | None] = {Start:None}

    while qeue:
        current = qeue.popleft()

        if current == Goal:
            break

        TempDirections = directions
        Parentof = parent[*current]
        if Parentof != None:
            RotationPar = Parentof[0]
        else:
            RotationPar = StartHeadto

        RotationElim = (RotationPar+180)%360
        TempDirections.pop(RotationElim)

        for rotation in TempDirections:
            dx, dy = TempDirections[rotation]
            nx = current[0] + dx
            ny = current[1] + dy
            nxt = (nx, ny)

            # Check if already a child
            if nxt in parent:
                continue

            # Collision check
            if Collision_Coord_Check(nx, ny) in CollisionIDs:
                continue

            # Check if the next block is a portal and then change coords to destination of portal
            if Collision_Coord_Check(nxt[0], nxt[1]) == 1:
                des: tuple[int, int]|None = TeleporterDesti(*nxt) #type:ignore
                if des != None:
                    ReverseRotation = (rotation+180)%360
                    tdx, tdy = directions[ReverseRotation]
                    xdes = des[0] + tdx
                    ydes = des[1] + tdy
                    CorrDes = (xdes, ydes)

                    if CorrDes in parent:
                        continue

                    if Collision_Coord_Check(*CorrDes) in CollisionIDs: #type:ignore
                        continue

                    parent[CorrDes] = (ReverseRotation, *current)
                    qeue.append(CorrDes)
            
            else:
                parent[nxt[0], nxt[1]] = (rotation, *current)
                qeue.append((nxt[0], nxt[1]))

    if Goal not in parent:
        return

    step: tuple[int, int] = Goal

    while True:
        previous = parent[step]

        if previous == None:
            return

        if (previous[0], previous[1]) == Start:
            break

        step = (previous[0], previous[1])

    heading = previous[2]

    return heading

# Modes
TarBlinky = (315, 135)
TarInky = (315, -435)
TarPinky = (-165, 135)
TarClyde = (-165, -435)

def scatter():
    global TarBlinky, TarInky, TarPinky, TarClyde
    TarBlinky = (315, 135)
    TarInky = (315, -435)
    TarPinky = (-165, 135)
    TarClyde = (-165, -435)

# Blinky


# De held
p.penup()
p.teleport(45, -315)
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

def teleportertp(ObjID:int, TargetTurtle:turtle.Turtle):
    # To-Do: 2nd teleporter ID to linked of 1st then 1st teleporter ID to linked of 2nd,
    # then when teleport is called (check disabled),
    # use linked as to point where to teleport and turn 180.
    Portal2ID = ObjData[ObjID]['Linked']

    # portal 1 is where target comes from, portal 2 is the portal linked to portal 1
    Portal1Data = ObjData[ObjID]
    Portal2Data = ObjData[Portal2ID] # type:ignore
    if Portal1Data['Disabled'] or Portal2Data['Disabled']:
        RuntimeError("One of the portals is not properly linked.")
    else:
        x:int = Portal2Data['TeleportPointX'] # type:ignore
        y:int = Portal2Data['TeleportPointY'] # type:ignore
        TargetTurtle.teleport(x, y) # type:ignore
        TargetTurtle.setheading((180+TargetTurtle.heading())%360)
        TargetTurtle.forward(GridStepSize)

# Tick Loops
def InitLoops():
    WalkLoop()
    TickLoop()

def TickLoop():
    global level, Dots
    if Dots == 0:
        level += 1
        Dots = 244
        ResetDots()
    # blinky, inky, pinky, clyde not yet finished (each their own loop)
    turtle.ontimer(TickLoop, 500)

def WalkLoop():
    global Dots, Points
    if Collision_Check(p.xcor(), p.ycor(), p.heading()):
        p.forward(30)

    Tuppd = Collision_Coord_Check(p.xcor(), p.ycor(), lbObjID=True)
    if isinstance(Tuppd, tuple):
        Tupped:tuple[int|None, int|None] = Tuppd
        TypeID = Tupped[0]
        ObjID = Tupped[1]
    else:
        TypeID = -100
        ObjID = -10000
        raise RuntimeError("How?")

    #if ObjID == None or TypeID == None:
    #    p.teleport(begin_x+75, begin_y-15)
    #    ObjID=0
    #    TypeID=-2
    #    print('Out of Bounds\nXcor: ' + str(p.xcor()) + ', Ycor: ' + str(p.ycor()))

    if ObjID != None and TypeID != None:
        if TypeID == 0:
            p.teleport(begin_x+75, begin_y-15)
            print('Out of Bounds')

        if TypeID == 1:
            teleportertp(ObjID, p)

        if TypeID == 2:
            Remove_Collision_Object(p.xcor(), p.ycor(), size=30, TypeID=2)
            Dots -= 1
            Points += 10
            r.teleport(p.xcor()-14, p.ycor()-14)
            r.setheading(0)
            r.penup()
            blok(28, 'black')
            r.pendown()

        if TypeID == 3:
            Remove_Collision_Object(p.xcor(), p.ycor(), size=30, TypeID=3)
            Dots -= 1
            Points += 50
            r.teleport(p.xcor()-14, p.ycor()-14)
            r.setheading(0)
            r.penup()
            blok(28, 'black')
            r.pendown()

    if debug:
        print(p.xcor(), p.ycor())

    t = 0

    max(20 - 5 * level, 0)

    time = int(round(500 / (1-t*0.01)))

    turtle.ontimer(WalkLoop, time)

def DebugPost():
    print(str(p.xcor()) + ', ' + str(p.ycor()))

InitLoops()

turtle.onkey(rechts, 'Right')
turtle.onkey(links, 'Left')
turtle.onkey(omhoog, 'Up')
turtle.onkey(omlaag, 'Down')
turtle.onkey(DebugPost, 'd')
turtle.listen()
turtle.mainloop()

# Ghost Note:
# If they don't turn for collision, then force them to move by turning 90 right or left, DO NOT GO BACKWARD!
# Each ghost their own mode (scatter, chase, freight, eaten) + a global mode which they check after returning to scatter+chase

# Point note:
# Pellet = 10p
# Power Pellet = 50p
# 1st ghost in 1 freight = 200
# 2nd ghost in 1 freight = 400
# 3rd ghost in 1 freight = 800
# 4th ghost in 1 freight = 1600
