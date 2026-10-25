import turtle
from collections import deque
import math
from typing import Any
from playsound import playsound #type:ignore
from operator import itemgetter
import random
import sys

# Ons spel: Pac-Man
# De held: Pac-Man
# Het doel: Alle wite bolletjes verzamelen (en naar level 255 te gaan)
# Wat houdt de held tegen: 4 Spoken: inky, blinky, pinky en clyde

# Type ID list:
# -2 = Pylance Error Negation
# -1 = Deleted
# 0 = Wall/Cube (No special effects)
# 1 = Teleporter
# 2 = Pelet
# 3 = Power Pelet
# 4 (Special Case) = tunnel (ghost slowdown)
# 5 (Special Case) = intersection (Ghost asks which way to turn)
# 6 (Special Case) = House (ghost turns off eaten and asks which way to turn)
# 7 = Empty Spot

p = turtle.Turtle()
r = turtle.Turtle()

p.speed(0)
turtle.bgcolor('black')

r.speed(0)
r.ht()

bdebug = False

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

r.teleport(WorldBiggestX, WorldBiggestY)
r.teleport(WorldSmallestX, WorldSmallestY)

turtle.setworldcoordinates(WorldSmallestX, WorldSmallestY, WorldBiggestX, WorldBiggestY)

level = 0
Points = 0
Dots = 0

# What is the game currently doing:
# 0 = enter any key screen
# 1 = Selection and highscores
# 2 = Game
# 3 = Enter Highscore Nickname
gamestate = 0
Loop = True

# Highscore: (highscore, ID) : (level, name)
Highscores: dict[tuple[int, int],tuple[int, str]] = {
    (500, 0) : (0, 'PLC'),
    (1100, 1) : (0, 'PLC'),
    (500000, 2) : (255, 'PLC'),
    (10, 3) : (0, 'PLC'),
    (410, 4) : (0, 'PLC')
    }
LatestID = 0

print(Highscores)

# Text
TurtleText: dict[int,tuple[turtle.Turtle,int,int]] = {}

def CreateText(ID:int, x:int, y:int):
    global TurtleText
    t = turtle.Turtle()
    t.penup()
    t.hideturtle()
    t.speed(0)
    t.teleport(x, y)

    TurtleText[ID] = (t, x, y)

def WriteText(ID:int, *, text:str, TextAllign: str="Left", colour:str='white', FontName:str="Courier", FontSize:int=64, FontType:str="Bold"):
    if ID in TurtleText:
        t = TurtleText[ID][0]
        x = TurtleText[ID][1]
        y = TurtleText[ID][2]

        ClearText(ID)

        t.teleport(x, y)
        t.pendown()
        t.color(colour)
        t.write(text, False, TextAllign, font=(FontName, FontSize, FontType))
        t.penup()

def ClearText(ID:int):
    if ID in TurtleText:
        t = TurtleText[ID][0]
        x = TurtleText[ID][1]
        y = TurtleText[ID][2]

        t.clear()
        t.penup()
        t.hideturtle()
        t.speed(0)
        t.teleport(x, y)

# X, Y Distance Calculator
def Distance_Calculator(x1:int|float, y1:int|float, x2:int|float, y2:int|float):
    x = abs(x1 - x2)
    y = abs(y1 - y2)

    return x, y

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
    ) -> list[int|tuple[int, int]]:
    x = int(round(x))
    y = int(round(y))
    TypeID = 0
    returnable:list[int]|list[tuple[int, int]] = []

    x = int(round(x))
    y = int(round(y))

    if not (WorldSmallestX <= x <= WorldBiggestX):
        if lbObjID:
            return [(0, -1)]
        else:
            return [0]
    if not (WorldSmallestY <= y <=  WorldBiggestY):
        if lbObjID:
            return [(0, -1)]
        else:
            return [0]
    
    for x1, x2, y1, y2 in collision:
        if x1 <= x <= x2 and y1 <= y <= y2:
            TypeID:int = collision[x1, x2, y1, y2][0]
            if lbObjID:
                ObjID:int = collision[x1, x2, y1, y2][1]
                returnable.append((TypeID, ObjID)) #type:ignore
            else:
                returnable.append(TypeID) #type:ignore

    if not returnable:
        if lbObjID:
            returnable = [(0, -1)]
        else:
            returnable = [0]

    return returnable #type:ignore

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
        CoordCheck = Collision_Coord_Check(rx, ry)
        for tID in CoordCheck:
            if tID in CollisionIDs:
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
        nonlocal s
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
    ObjData[ObjID].update({'Disabled':False})
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
    Tupped = Create_Collision_Object(x, y, coordinates=(x+30, y+30), TypeID=1)
    ObjID = Tupped[1]
    collisobj = Tupped[0]
    TeleportPointX = int(round((collisobj[0] + collisobj[1])/2)) # X middle of the teleporter
    TeleportPointY = int(round((collisobj[2] + collisobj[3])/2)) # Y middle of the teleporter
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
    '.####o###.#.###o####.',
    '....#o#.......#o#....',
    '.####o#.##d##.#o####.',
    't....o..#...#..o....t',
    '.####o#.#####.#o####.',
    '....#o#.......#o#....',
    '.####o#.#####.#o####.',
    '.#oooooooo#oooooooo#.',
    '.#o##o###o#o###o##o#.',
    '.#*o#ooooooooooo#o*#.',
    '.##o#o#o#####o#o#o##.',
    '.#oooo#ooo#ooo#oooo#.',
    '.#o######o#o######o#',
    '.#ooooooooooooooooo#.',
    '.###################.',
]

Special = [
    '.###################.',
    '.#i..i...i#i...i..i#.',
    '.#.##.###.#.###.##.#.',
    '.#.##.###.#.###.##.#.',
    '.#i..i.i.i.i.i.i..i#.',
    '.#.##.#.#####.#.##.#.',
    '.#i..i#i.i#i.i#i..i#.',
    '.####.###.#.###.####.',
    '....#.#i.iii.i#.#....',
    '.####.#.##h##.#.####.',
    '.tttti.i#hhh#i.itttt.',
    '.####.#.#####.#.####.',
    '....#.#i.....i#.#....',
    '.####.#.#####.#.####.',
    '.#i..i.i.i#i.i.i..i#.',
    '.#.##.###.#.###.##.#.',
    '.#ii#i.i.i.i.i.i#ii#.',
    '.##.#.#.#####.#.#.##.',
    '.#ii.i#i.i#i.i#i.ii#.',
    '.#.######.#.######.#',
    '.#i......i.i......i#.',
    '.###################.',
]

def world(colour:str='blue'):
    r.color(colour)
    y = begin_y
    for rij in wereld:
        x = begin_x
        for teken in rij:
            if teken == '#':
                Create_Collision_Object(x, y, coordinates=(x+30, y+30), TypeID=0)
                muur(x, y)
            if teken == 't':
                TeleporterCreator(x, y)
            if teken == '.':
                Create_Collision_Object(x, y, coordinates=(x+30, y+30), TypeID=7)
            x = x + 30
        y = y - 30

def DotLoad():
    global Dots
    y = begin_y
    for rij in wereld:
        x = begin_x
        for teken in rij:
            if teken == 'o':
                Create_Collision_Object(
                    x,
                    y,
                    coordinates=(
                        x+30,
                        y+30
                    ),
                    TypeID=2
                )
                puntje(x+round(GridStepSize/2), y+round(GridStepSize/2))
                Dots += 1
            if teken == '*':
                Create_Collision_Object(
                    x,
                    y,
                    coordinates=(
                        x+30,
                        y+30
                    ),
                    TypeID=3)
                puntje(x+round(GridStepSize/2), y+round(GridStepSize/2), 14)
                Dots += 1
            x = x + 30
        y = y - 30

def SpecialLoad():
    global Dots
    y = begin_y
    for rij in Special:
        x = begin_x
        for teken in rij:
            if teken == 't':
                Create_Collision_Object(x, y, coordinates=(x+30, y+30), TypeID=4)
            if teken == 'i':
                Create_Collision_Object(x, y, coordinates=(x+30, y+30), TypeID=5)
            if teken == 'h':
                Create_Collision_Object(x, y, coordinates=(x+30, y+30), TypeID=6)
            x = x + 30
        y = y - 30

def LevelUp():
    def ClearMap():
        global Teleporter1ID, Dots
        collision.clear()
        ObjData.clear()
        Teleporter1ID = None

        r.clear()
        Dots = 0

    def worldanimation():
            nonlocal colours
            c = colours.pop(0)
            world(c)

    colours = ['yellow', 'blue', 'yellow', 'blue', 'yellow', 'blue', 'yellow', 'blue']

    for i in range(8):
        ClearMap()
        turtle.ontimer(worldanimation, 500 * i)
    
    ClearMap()
    WriteText(1, text='You Won!', colour='green', TextAllign='center')

    def ClearText13():
        global gamestate
        ClearText(13)
        gamestate = 3
        GameStateOn()

    turtle.ontimer(ClearText13, 3000)

#    world()
#    DotLoad()
#    SpecialLoad()

# AI
def bfs(StartX:int|float, StartY:int|float, StartHeading:int|float, GoalX:int|float, GoalY:int|float):
    def TeleporterDesti(x:int, y:int): #type:ignore
        ccc = Collision_Coord_Check(x, y, lbObjID=True)

        for TypeIDl, ObjIDl in ccc: #type:ignore
            if TypeIDl != 1 or ObjIDl == None:
                continue
    
            PorDat = ObjData[ObjIDl]
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
        return None
    
    global GridStepSize
    if GridStepSize <= 0:
        raise RuntimeError("Call Set_Grid to initialize this module's grid, as currently GridStepSize is 0 or a negative integer.")
    GridSize = GridStepSize

    StartHeadto = int(float(StartHeading))
    Start:tuple[int, int] = (int(round(StartX)), int(round(StartY)))
    #MovStart = (StartHeadto, *Start)
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
        return

    if not On_Grid(GoalX, GoalY):
        return

    StartCoordColl = Collision_Coord_Check(*Start)
    for coll in StartCoordColl:
        if coll in CollisionIDs:
            return

    GoalCoordColl = Collision_Coord_Check(*Goal)
    for coll in GoalCoordColl:
        if coll in CollisionIDs:
            return

    if Start == Goal:
        return 'Turn'
    
    qeue = deque([Start])
    # Child (rotation, x, y) : Parent (rotation, x, y)
    parent: dict[tuple[int, int],tuple[int, int, int] | None] = {Start:None}

    while qeue:
        current = qeue.popleft()

        if current == Goal:
            break

        # Remove opposite direction
        TempDirections = directions.copy()
        Parentof = parent[*current]
        if Parentof != None:
            RotationPar = Parentof[0]
        else:
            RotationPar = StartHeadto

        RotationElim = (round((RotationPar+180)%360))
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
            NextCoordColl = Collision_Coord_Check(nx, ny)
            if any(coll in CollisionIDs for coll in NextCoordColl):
                continue

            # Check if the next block is a portal and then change coords to destination of portal
            if any(coll == 1 for coll in NextCoordColl):
                des: tuple[int, int]|None = TeleporterDesti(*nxt) #type:ignore
                if des != None:
                    ReverseRotation = (rotation+180)%360
                    tdx, tdy = directions[ReverseRotation]
                    xdes = des[0] + tdx
                    ydes = des[1] + tdy
                    CorrDes = (xdes, ydes)

                    if CorrDes in parent:
                        continue

                    DesCoordColl = Collision_Coord_Check(*CorrDes)
                    if any(coll in CollisionIDs for coll in DesCoordColl):
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

        if (previous[1], previous[2]) == Start:
            break

        step = (previous[1], previous[2])

    heading = previous[0]

    return heading

# Modes
MainAIMode = 'scatter'
    #global TarBlinky, TarPinky, TarInky, TarClyde
    #px, py = (p.xcor(), p.ycor())
    #pcor = (px, py)
#
    #if int(round(p.heading())) == 90:
    #    Pink = Destination_Calculator(*pcor, 90, 120)
    #    Pinky = Destination_Calculator(*Pink, 180, 120)
    #else:
    #    Pinky = Destination_Calculator(*pcor, p.heading(), 120)
#
    ## Calc 2 tiles ahead of pacman (30 * 2)
    #tile2Pac = Destination_Calculator(*pcor, p.heading(), 60)
#
    #if clg.distance(*pcor) <= 240:
    #    ClydeCor = TarClyde
    #else:
    #    ClydeCor = pcor
#
    #TarBlinky = pcor
    #TarPinky = Pinky
    #TarInky = Distance_Calculator(*tile2Pac, blg.xcor(), blg.ycor())
    #TarClyde = ClydeCor

freight = False # Temp replacement for actual code to be added later
FreightTimerCancel = 0
EatenStreakFreight = 0

def RemoveFreight():
    global FreightTimerCancel, freight, EatenStreakFreight
    if FreightTimerCancel < 0:
        FreightTimerCancel = 0
        return
    elif FreightTimerCancel == 1:
        FreightTimerCancel -= 1
        freight = False
        EatenStreakFreight = 0
        return
    elif FreightTimerCancel > 1:
        FreightTimerCancel -= 1
        return
    else:
        return

def FreightMode():
    global freight, FreightTimerCancel
    freight = True
    FreightTimerCancel += 1
    turtle.ontimer(RemoveFreight, 7000)

LevelTimingList = [0, 7, 20, 7, 20, 5, 20, 5]
TimerList = [
    sum(LevelTimingList[:2]),
    sum(LevelTimingList[:3]),
    sum(LevelTimingList[:4]),
    sum(LevelTimingList[:5]),
    sum(LevelTimingList[:6]),
    sum(LevelTimingList[:7]),
    sum(LevelTimingList[:8])
]

ModeCounter = 0
chaselist: list[int] = []
scatterlist: list[int] = []
for i in range(7):
        if i % 2 == 0:
            chaselist.append(TimerList[i])
        else:
            scatterlist.append(TimerList[i])

# Blinky
BlinkyMode = 'scatter'
BlinkyEaten = False
BlinkyOldMode: str | None = None
def BlinkyModeChange(eaten:bool = False):
    global BlinkyMode, BlinkyOldMode
    if freight and BlinkyOldMode != 'freight':
        blg.right(180)
        BlinkyMode = 'freight'
    elif BlinkyEaten and BlinkyOldMode != 'eaten':
        blg.right(180)
        BlinkyMode = 'eaten'
    elif BlinkyMode != MainAIMode:
        blg.right(180)
        BlinkyMode = MainAIMode
    BlinkyOldMode = BlinkyMode

def BlinkyMove():
    print('BlinkyMove Triggered')
    LevelDotAngry = 20
    if BlinkyMode == 'scatter' and Dots > LevelDotAngry:
        TarBlinky = ScatterTarBlinky
    elif BlinkyMode == 'scatter' and Dots <= LevelDotAngry:
        TarBlinky = (p.xcor(), p.ycor())
    elif BlinkyMode == 'chase':
        TarBlinky = (p.xcor(), p.ycor())
    elif BlinkyMode == 'eaten':
        TarBlinky = (60, -180)
    elif BlinkyMode == 'freight':
            TurnBlink = random.randint(-1, 1) * 90
            blg.right(TurnBlink)
            return
    else:
        raise RuntimeError(f"Unknown mode: '{BlinkyMode}' !")

    Heading = bfs(blg.xcor(), blg.ycor(), blg.heading(), *TarBlinky)
    if Heading == 'Turn' or Heading == None:
        if Collision_Check(blg.xcor(), blg.ycor(), 90):
            blg.setheading(90)
        elif Collision_Check(blg.xcor(), blg.ycor(), 180):
            blg.setheading(180)
        elif Collision_Check(blg.xcor(), blg.ycor(), 270):
            blg.setheading(270)
        elif Collision_Check(blg.xcor(), blg.ycor(), 0):
            blg.setheading(0)
        print('Blinky turned because no result of bfs was acceptable')
        return

    blg.setheading(Heading)
    print(f'TarBlinky: {TarBlinky}', f'Heading: {Heading}', sep=', ')
    return

# Pinky
PinkyMode = 'scatter'
PinkyEaten = False
PinkyOldMode: str | None = None
def PinkyModeChange(eaten:bool = False):
    global PinkyMode, PinkyOldMode
    if freight and PinkyOldMode != 'freight':
        pig.right(180)
        PinkyMode = 'freight'
    elif PinkyEaten and PinkyOldMode != 'eaten':
        pig.right(180)
        PinkyMode = 'eaten'
    elif PinkyMode != MainAIMode:
        pig.right(180)
        PinkyMode = MainAIMode
    PinkyOldMode = PinkyMode

def PinkyMove():
    if PinkyMode == 'scatter':
        TarPinky = ScatterTarPinky
    elif PinkyMode == 'chase':
        if int(round(p.heading())) == 90:
            Pink: tuple[int, int] = Destination_Calculator(p.xcor(), p.ycor(), 90, 120)
            Pinky = Destination_Calculator(*Pink, 180, 120)
        else:
            Pinky = Destination_Calculator(p.xcor(), p.ycor(), p.heading(), 120)
        TarPinky = Pinky
    elif PinkyMode == 'eaten':
        TarPinky = (60, -180)
    elif PinkyMode == 'freight':
        TarPinky = (p.xcor(), p.ycor())
        TurnPink = random.randint(-1, 1) * 90
        pig.right(TurnPink)
        return
    else:
        raise RuntimeError(f"Unknown mode: '{PinkyMode}' !")

    Heading = bfs(pig.xcor(), pig.ycor(), pig.heading(), *TarPinky)
    if Heading == None:
        return
    if Heading == 'Turn':
        if Collision_Check(pig.xcor(), pig.ycor(), 90):
            pig.setheading(90)
        elif Collision_Check(pig.xcor(), pig.ycor(), 180):
            pig.setheading(180)
        elif Collision_Check(pig.xcor(), pig.ycor(), 270):
            pig.setheading(270)
        elif Collision_Check(pig.xcor(), pig.ycor(), 0):
            pig.setheading(0)
        return

    pig.setheading(Heading)
    return

# Inky
InkyMode = 'scatter'
InkyEaten = False
InkyOldMode: str | None = None
def InkyModeChange(eaten:bool = False):
    global InkyMode, InkyOldMode
    if freight and InkyOldMode != 'freight':
        ing.right(180)
        InkyMode = 'freight'
    elif InkyEaten and InkyOldMode != 'eaten':
        ing.right(180)
        InkyMode = 'eaten'
    elif InkyMode != MainAIMode:
        ing.right(180)
        InkyMode = MainAIMode
    InkyOldMode = InkyMode

def InkyMove():
    if InkyMode == 'scatter':
        TarInky = ScatterTarInky
    elif InkyMode == 'chase':
        tile2Pac = Destination_Calculator(p.xcor(), p.ycor(), p.heading(), 60)
        TarInky = (2*tile2Pac[0] - blg.xcor(), 2*tile2Pac[1] - blg.ycor())
    elif InkyMode == 'eaten':
        TarInky = (60, -180)
    elif InkyMode == 'freight':
        TurnInk = random.randint(-1, 1) * 90
        ing.right(TurnInk)
        return
    else:
        raise RuntimeError(f"Unknown mode: '{InkyMode}' !")

    Heading = bfs(ing.xcor(), ing.ycor(), ing.heading(), *TarInky)
    if Heading == None:
        return
    if Heading == 'Turn':
        if Collision_Check(ing.xcor(), ing.ycor(), 90):
            ing.setheading(90)
        elif Collision_Check(ing.xcor(), ing.ycor(), 180):
            ing.setheading(180)
        elif Collision_Check(ing.xcor(), ing.ycor(), 270):
            ing.setheading(270)
        elif Collision_Check(ing.xcor(), ing.ycor(), 0):
            ing.setheading(0)
        return

    ing.setheading(Heading)
    return

# Clyde
ClydeMode = 'scatter'
ClydeEaten = False
ClydeOldMode: str | None = None
def ClydeModeChange(eaten:bool = False):
    global ClydeMode, ClydeOldMode
    if freight and ClydeOldMode != 'freight':
        clg.right(180)
        ClydeMode = 'freight'
    elif ClydeEaten and ClydeOldMode != 'eaten':
        clg.right(180)
        ClydeMode = 'eaten'
    elif ClydeMode != MainAIMode:
        clg.right(180)
        ClydeMode = MainAIMode
    ClydeOldMode = ClydeMode

def ClydeMove():
    if ClydeMode == 'scatter':
        TarClyde = ScatterTarClyde
    elif ClydeMode == 'chase':
        if clg.distance(p.xcor(), p.ycor()) <= 240:
            TarClyde = ScatterTarClyde
        else:
            TarClyde = (p.xcor(), p.ycor())
    elif ClydeMode == 'eaten':
        TarClyde = (60, -180)
    elif ClydeMode == 'freight':
            TurnClyde = random.randint(-1, 1) * 90
            clg.right(TurnClyde)
            return
    else:
        raise RuntimeError(f"Unknown mode: '{ClydeMode}' !")

    Heading = bfs(clg.xcor(), clg.ycor(), clg.heading(), *TarClyde)
    if Heading == None:
        return
    if Heading == 'Turn':
        if Collision_Check(clg.xcor(), clg.ycor(), 90):
            clg.setheading(90)
        elif Collision_Check(clg.xcor(), clg.ycor(), 180):
            clg.setheading(180)
        elif Collision_Check(clg.xcor(), clg.ycor(), 270):
            clg.setheading(270)
        elif Collision_Check(clg.xcor(), clg.ycor(), 0):
            clg.setheading(0)
        return

    clg.setheading(Heading)
    return

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
        #TargetTurtle.setheading((180-TargetTurtle.heading())%360)
        #print(str((180-TargetTurtle.heading())%360))
        TargetTurtle.forward(GridStepSize)

# Game Over
def GameOver():
    def TextWhipe():
        ClearText(1)

    WriteText(1, text='You Died!', colour='red', TextAllign='center')

    turtle.ontimer(TextWhipe, 3000)

    turtle.onkey(None, 'Right') # type:ignore
    turtle.onkey(None, 'Left') # type:ignore
    turtle.onkey(None, 'Up') # type:ignore
    turtle.onkey(None, 'Down') # type:ignore
    turtle.onkey(None, 'd') # type:ignore

    r.clear()
    
    global gamestate, Loop, ModeCounter
    Loop = False
    gamestate = 3
    ModeCounter = 0
    GameStateOn()

# Tick Loops
LevelTimeElapsed = 0

def InitLoops():
    global Loop
    Loop = True
    WalkLoop()
    TickLoop()

    BlinkyLoop()
    PinkyLoop()
    InkyLoop()
    ClydeLoop()

def TickLoop():
    global level, Dots, LevelTimeElapsed, EatenStreakFreight, Points, ModeCounter, MainAIMode

    ModeCounter += 1
    ChaseNumber = int(math.floor(ModeCounter/2))
    if ChaseNumber in chaselist:
        MainAIMode = 'chase'
    elif ChaseNumber in scatterlist:
        MainAIMode = 'scatter'
    
    if Dots == 0:
        level += 1
        LevelUp()
     
    LevelTimeElapsed += 1
    # blinky, inky, pinky, clyde not yet finished (each their own loop)
    if Loop:
        turtle.ontimer(TickLoop, 500)
    else:
        return

# Ghost speed: 50% level 1, 60% de rest als in freight
# Ghost speed tunnel: 40% tot 50%
# Eaten Speed: 200%

def BlinkyLoop():
    t = -5

    BlinkyModeChange()


    Tuppd = Collision_Coord_Check(blg.xcor(), blg.ycor(), lbObjID=True)

    for TypeIDl, ObjIDl in Tuppd: #type:ignore
        if TypeIDl == 0:
            blg.teleport(begin_x+75, begin_y-15)
            print('Out of Bounds')

        elif TypeIDl == 1:
            if ObjIDl != None:
                teleportertp(ObjIDl, blg) #type:ignore

        elif TypeIDl == 4:
            t -= 60

        elif TypeIDl in [5, 6]:
            BlinkyMove()

        if TypeIDl == 6:
            global BlinkyEaten
            BlinkyEaten = False

    BlinkySoonToBe = Destination_Calculator(blg.xcor(), blg.ycor(), blg.heading(), 30)
    Tuppld = Collision_Coord_Check(*BlinkySoonToBe)
    FutureTypeID = Tuppld

    for FTypeID in FutureTypeID:
        if isinstance(FTypeID, int):
            if FTypeID == 1:
                blg.forward(30)

            elif FTypeID not in CollisionIDs:
                blg.forward(30)

    t -= max(20 - 5 * level, 0)

    time = int(round(142 / (1+(t*0.01))))

    if Loop:
        turtle.ontimer(BlinkyLoop, time)
    else:
        return

def PinkyLoop():
    t = -5

    PinkyModeChange()


    Tuppd = Collision_Coord_Check(pig.xcor(), pig.ycor(), lbObjID=True)

    for TypeIDl, ObjIDl in Tuppd: #type:ignore
        if TypeIDl == 0:
            pig.teleport(begin_x+75, begin_y-15)
            print('Out of Bounds')

        elif TypeIDl == 1:
            if ObjIDl != None:
                teleportertp(ObjIDl, pig) #type:ignore

        elif TypeIDl == 4:
            t -= 60

        elif TypeIDl in [5, 6]:
            PinkyMove()

        if TypeIDl == 6:
            global PinkyEaten
            PinkyEaten = False

    PinkySoonToBe = Destination_Calculator(pig.xcor(), pig.ycor(), pig.heading(), 30)
    Tuppld = Collision_Coord_Check(*PinkySoonToBe)
    FutureTypeID = Tuppld

    for FTypeID in FutureTypeID:
        if isinstance(FTypeID, int):
            if FTypeID == 1:
                pig.forward(30)
    
            elif FTypeID not in CollisionIDs:
                pig.forward(30)
    
    t -= max(20 - 5 * level, 0)
    
    time = int(round(142 / (1+(t*0.01))))
    
    if Loop:
        turtle.ontimer(PinkyLoop, time)
    else:
        return

def InkyLoop():
    t = -5

    InkyModeChange()


    Tuppd = Collision_Coord_Check(ing.xcor(), ing.ycor(), lbObjID=True)

    for TypeIDl, ObjIDl in Tuppd: #type:ignore
        if TypeIDl == 0:
            ing.teleport(begin_x+75, begin_y-15)
            print('Out of Bounds')

        elif TypeIDl == 1:
            if ObjIDl != None:
                teleportertp(ObjIDl, ing) #type:ignore

        elif TypeIDl == 4:
            t -= 60

        elif TypeIDl in [5, 6]:
            InkyMove()

        if TypeIDl == 6:
            global InkyEaten
            InkyEaten = False

    InkySoonToBe = Destination_Calculator(ing.xcor(), ing.ycor(), ing.heading(), 30)
    Tuppld = Collision_Coord_Check(*InkySoonToBe)
    FutureTypeID = Tuppld


    for FTypeID in FutureTypeID:
        if isinstance(FTypeID, int):
            if FTypeID == 1:
                ing.forward(30)
    
            elif FTypeID not in CollisionIDs:
                ing.forward(30)
    
    t -= max(20 - 5 * level, 0)
    
    time = int(round(142 / (1+(t*0.01))))
    
    if Loop:
        turtle.ontimer(InkyLoop, time)
    else:
        return

def ClydeLoop():
    t = -5

    ClydeModeChange()


    Tuppd = Collision_Coord_Check(clg.xcor(), clg.ycor(), lbObjID=True)

    for TypeIDl, ObjIDl in Tuppd: #type:ignore
        if TypeIDl == 0:
            clg.teleport(begin_x+75, begin_y-15)
            print('Out of Bounds')

        elif TypeIDl == 1:
            if ObjIDl != None:
                teleportertp(ObjIDl, clg) #type:ignore

        elif TypeIDl == 4:
            t -= 60

        elif TypeIDl in [5, 6]:
            ClydeMove()

        if TypeIDl == 6:
            global ClydeEaten
            ClydeEaten = False

    ClydeSoonToBe = Destination_Calculator(clg.xcor(), clg.ycor(), clg.heading(), 30)
    Tuppld = Collision_Coord_Check(*ClydeSoonToBe)
    FutureTypeID = Tuppld

    for FTypeID in FutureTypeID:
        if isinstance(FTypeID, int):
            if FTypeID == 1:
                clg.forward(30)
    
            elif FTypeID not in CollisionIDs:
                clg.forward(30)
    
    t -= max(20 - 5 * level, 0)
    
    time = int(round(142 / (1+(t*0.01))))
    
    if Loop:
        turtle.ontimer(ClydeLoop, time)
    else:
        return

LevelDotSlowdown = 11.25
LevelFreightSpeedUp = 12.5
def WalkLoop():
    global Dots, Points, EatenStreakFreight, BlinkyEaten, PinkyEaten, InkyEaten, ClydeEaten
    t = 0

    p_cor = (p.xcor(), p.ycor())

    blg_to_p_dis = blg.distance(*p_cor)
    if blg_to_p_dis <= 25:
        if BlinkyMode == 'freight':
            Points += 200 * (2 ** EatenStreakFreight)
            EatenStreakFreight += 1
            BlinkyEaten = True
        if not BlinkyMode in ['freight', 'eaten']:
            GameOver()

    pig_to_p_dis = pig.distance(*p_cor)
    if pig_to_p_dis <= 25:
        if PinkyMode == 'freight':
            Points += 200 * (2 ** EatenStreakFreight)
            EatenStreakFreight += 1
            PinkyEaten = True
            PinkyModeChange(True)
        if not PinkyMode in ['freight', 'eaten']:
            GameOver()

    ing_to_p_dis = ing.distance(*p_cor)
    if ing_to_p_dis <= 25:
        if InkyMode == 'freight':
            Points += 200 * (2 ** EatenStreakFreight)
            EatenStreakFreight += 1
            InkyEaten = True
            InkyModeChange(True)
        if not InkyMode in ['freight', 'eaten']:
            GameOver()

    clg_to_p_dis = clg.distance(*p_cor)
    if clg_to_p_dis <= 25:
        if ClydeMode == 'freight':
            Points += 200 * (2 ** EatenStreakFreight)
            EatenStreakFreight += 1
            ClydeEaten = True
            ClydeModeChange(True)
        if not ClydeMode in ['freight', 'eaten']:
            GameOver()

    if Collision_Check(p.xcor(), p.ycor(), p.heading()):
        p.forward(30)

    Tuppd = Collision_Coord_Check(p.xcor(), p.ycor(), lbObjID=True)

    for TypeIDl, ObjIDl in Tuppd: #type:ignore
        if TypeIDl == 0:
            p.teleport(begin_x+75, begin_y-15)
            print('Out of Bounds')

        if TypeIDl == 1:
            if ObjIDl != None:
                teleportertp(ObjIDl, p) #type:ignore

        if TypeIDl == 2:
            Remove_Collision_Object(
                p.xcor()-round(GridStepSize/2),
                p.ycor()-round(GridStepSize/2),
                coordinates=(
                    p.xcor()-round(GridStepSize/2)+30,
                    p.ycor()-round(GridStepSize/2)+30
                ),
                TypeID=2
            )
            Dots -= 1
            Points += 10
            r.teleport(p.xcor()-14, p.ycor()-14)
            r.setheading(0)
            r.penup()
            blok(28, 'black')
            r.pendown()
            t -= LevelDotSlowdown

        if TypeIDl == 3:
            rem = Remove_Collision_Object(
                p.xcor()-round(GridStepSize/2),
                p.ycor()-round(GridStepSize/2),
                coordinates=(
                    p.xcor()+round(GridStepSize/2),
                    p.ycor()+round(GridStepSize/2)
                ),
                TypeID=3
            )

            if rem[1]:
                Dots -= 1
                Points += 50
                r.teleport(p.xcor()-14, p.ycor()-14)
                r.setheading(0)
                r.penup()
                blok(28, 'black')
                r.pendown()
                t -= LevelDotSlowdown
                FreightMode()

    #if ObjID == None or TypeID == None:
    #    p.teleport(begin_x+75, begin_y-15)
    #    ObjID=0
    #    TypeID=-2
    #    print('Out of Bounds\nXcor: ' + str(p.xcor()) + ', Ycor: ' + str(p.ycor()))

    if freight:
        t += LevelFreightSpeedUp

    if bdebug:
        print(p.xcor(), p.ycor())

    t -= max(20 - 5 * level, 0)

    time = int(round(142 / (1+(t*0.01))))

    WriteText(11, text=f'Highscore: {Points}', FontSize=128)
    WriteText(12, text=f'Level: {level+1}', FontSize=128)

    if Loop:
        turtle.ontimer(WalkLoop, time)
    else:
        return

def DebugPost():
    print(str(p.xcor()) + ', ' + str(p.ycor()))

CreateText(0, GridOriginX, -30) # Press any key
CreateText(1, GridOriginX, 30) # You Died text
CreateText(2, -60, 150) # Play Game
CreateText(3, -60, 120) # Options (This cannot be implemented since it uses a json to store values, but it is intended for when I have time)
CreateText(4, -60, 90) # Exit Game
for i in range(6): # creates 5 highscore texts and a header with highscore as text
    CreateText(i+5, -60, 30-30*i)
CreateText(11, 450, 180)
CreateText(12, 450, 0)
CreateText(13, GridOriginX, -30) # Highscore input and other highscore text thing stuff (totally written while tired! Nothing else (pinky promise NOT!))

# AIs/Enemies
ScatterTarBlinky = (315, 135)
ScatterTarInky = (315, -435)
ScatterTarPinky = (-165, 135)
ScatterTarClyde = (-165, -445)

blg = turtle.Turtle()
blg.speed(0)
blg.color('red')
blg.penup()
blg.teleport(75, -135)
blg.setheading(90)
blg.ht()

pig = turtle.Turtle()
pig.speed(0)
pig.color('deeppink')
pig.penup()
pig.teleport(75, -135)
pig.setheading(90)
pig.ht()

ing = turtle.Turtle()
ing.speed(0)
ing.color('cyan')
ing.penup()
ing.teleport(75, -135)
ing.setheading(90)
ing.ht()

clg = turtle.Turtle()
clg.speed(0)
clg.color('sandybrown')
clg.penup()
clg.teleport(75, -135)
clg.setheading(90)
clg.ht()

def ClearGhosts():
    blg.speed(0)
    blg.color('red')
    blg.penup()
    blg.teleport(75, -135)
    blg.setheading(90)
    blg.ht()

    pig.speed(0)
    pig.color('deeppink')
    pig.penup()
    pig.teleport(75, -135)
    pig.setheading(90)
    pig.ht()

    ing.speed(0)
    ing.color('cyan')
    ing.penup()
    ing.teleport(75, -135)
    ing.setheading(90)
    ing.ht()

    clg.speed(0)
    clg.color('sandybrown')
    clg.penup()
    clg.teleport(75, -135)
    clg.setheading(90)
    clg.ht()

def ShowGhosts():
    blg.st()
    pig.st()
    ing.st()
    clg.st()

def GameStateOn():
    global gamestate
    match gamestate:
        case 0: # Press any key (not so any)
            for i in range(15):
                if i == 1:
                    continue
                ClearText(i)
            ClearGhosts()
            p.ht()

            WriteText(0, text='Press Space or Z To Start...', TextAllign='center')

            def GameStateNext():
                global gamestate
                turtle.onkey(None, 'space') #type:ignore

                for i in range(15):
                    if i == 1:
                        continue
                    ClearText(i)

                gamestate += 1
                GameStateOn()

            #def debug():
            #    print(gamestate)

            turtle.onkey(GameStateNext, 'space')
            turtle.onkey(GameStateNext, 'z')
            turtle.listen()
        case 1:
            try:
                for i in range(15):
                    if i == 1:
                        continue
                    ClearText(i)
                ClearGhosts()
                WriteText(2, text='Play Game', TextAllign='left')
                WriteText(3, text='Options (WIP, not designed for website!)', TextAllign='left')
                WriteText(4, text='Exit', TextAllign='left')
                WriteText(5, text='Highscores', TextAllign='left')
                
                p.st()
                p.shape('classic')
                p.color('green')
                p.setheading(0)

                sel = 0
                HighscoreKeys = Highscores.keys()

                HighscoreKeys = sorted(HighscoreKeys, key=itemgetter(0), reverse=True)

                # ID : (Highscore, Level, Name, Highscore in Str)
                HighscoreStr: dict[int,tuple[int, int, str, str]] = {}
                for iteration, (hs, id) in enumerate(HighscoreKeys):
                    ZeroNumber = str(hs).zfill(8)
                    DataTransfer = Highscores[(hs, id)]
                    HighscoreStr[id] = (hs, *DataTransfer, ZeroNumber)
                    if iteration < 6:
                        WriteText(iteration+6, text=f'Rank: {iteration+1}\tHighscore: {ZeroNumber}\tLevel: {DataTransfer[0]}\tName: {DataTransfer[1]}')

                # Complete this code
                def ActionEvent():
                    nonlocal sel
                    if sel < 0:
                        sel = 2
                    match sel:
                        case 0:
                            global gamestate
                            turtle.onkey(None, 'z') #type:ignore
                            turtle.onkey(None, 'Enter') #type:ignore
                            turtle.onkey(None, 'Up') #type:ignore
                            turtle.onkey(None, 'Down') #type:ignore
                            for i in range(15):
                                if i == 1:
                                    continue
                                ClearText(i)
                            gamestate = 2
                            GameStateOn()
                        case 1: # Options
                            pass
                        case 2: # quit
                            sys.exit()
                        case _:
                            sel = 0
                            ActionEvent()

                def Drawer():
                    nonlocal sel
                    if sel < 0:
                        sel = 2
                    match sel:
                        case 0:
                            p.teleport(-90, 150)
                        case 1:
                            p.teleport(-90, 120)
                        case 2:
                            p.teleport(-90, 90)
                        case _:
                            sel = 0
                            Drawer()

                def MinusSel():
                    nonlocal sel
                    sel -= 1
                    #print(sel)
                    Drawer()

                def PlusSel():
                    nonlocal sel
                    sel += 1
                    #print(sel)
                    Drawer()

                Drawer()

                turtle.onkey(ActionEvent, 'z')
                turtle.onkey(ActionEvent, 'Enter')
                turtle.onkey(MinusSel, 'Up')
                turtle.onkey(PlusSel, 'Down')
                turtle.listen()
            except Exception as e:
                print(f'Gamestate 1 Crashed and returned to state 0\nException: {e}')
                gamestate = 0
                GameStateOn()
        case 2:
            global collision
            collision = {}
            for i in range(15):
                if i == 1:
                    continue
                ClearText(i)
            #try:
            # World Map Loader
            world()
            DotLoad()
            SpecialLoad()

            # Player Character
            p.penup()
            p.teleport(45, -315)
            p.shape('circle')
            p.color('gold')

            ShowGhosts()

            InitLoops()

            turtle.onkey(rechts, 'Right')
            turtle.onkey(links, 'Left')
            turtle.onkey(omhoog, 'Up')
            turtle.onkey(omlaag, 'Down')
            turtle.onkey(DebugPost, 'd')
            turtle.listen()
            #except Exception as e:
            #    print(f'Gamestate 2 Crashed and returned to state 0\nException: {e}')
            #    gamestate = 0
        case 3:
            for i in range(15):
                if i == 1:
                    continue
                ClearText(i)

            Name = ['.', '.', '.']
            EditIndex = 0

            JoinedName = "".join(Name)
            print(f'Highscore: {Points}, Level: {level+1}, Name: {JoinedName}')

            WriteText(13, text=f'Highscore: {Points}, Level: {level+1}, Name: {JoinedName}', TextAllign='center', FontSize=128)

            def NextGameState():
                for key in 'qwertyuiopasdfghjklzxcvbnm':
                    turtle.onkey(None, key) #type:ignore

                def change():
                    global gamestate
                    gamestate = 0
                    GameStateOn()

                turtle.ontimer(change, 3000)

            def HandleKey(key: str):
                nonlocal Name, EditIndex
                Name[EditIndex] = key
                EditIndex += 1

                JoinedName = ("".join(Name)).upper()

                WriteText(13, text=f'Highscore: {Points}, Level: {level+1}, Name: {JoinedName}', TextAllign='center', FontSize=128)
                
                if EditIndex == 3:
                    NextGameState()

            for key in 'qwertyuiopasdfghjklzxcvbnm':
                turtle.onkey(lambda k=key: HandleKey(k), key)

            turtle.listen()
            
        case _:
            gamestate = 0
            GameStateOn()

GameStateOn()

def debug():
    print()
    print(gamestate)

turtle.onkey(debug, 'd')
turtle.listen()

# Mainsyloopsy
turtle.mainloop()

#playsound('01-start-game.mp3') 

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

# ToDO:
# Highscores
# if destination == teleporter do forward
# Add ghost intersections

# ToDo Fuller Version:
# Add sound
# Add intersection qeueus
#
# If time surplus:
# Change everything into classes