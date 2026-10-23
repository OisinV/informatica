import turtle
from collections import deque
import math
from typing import Any
from playsound import playsound #type:ignore
from operator import itemgetter
import random

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

turtle.setworldcoordinates(WorldSmallestX, WorldSmallestY, WorldBiggestX, WorldBiggestY)

level = 0
Points = 0
Dots = 0

# What is the game currently doing:
# 0 = enter any key screen
# 1 = Selection and highscores
# 2 = Game
# 3 = Game Over
# 4 = Enter Highscore Nickname
gamestate = 0
Loop = True

# Highscore: (highscore, ID) : (level, name)
Highscores: dict[tuple[int, int],tuple[int, str]] = {
    (0, 0) : (0, 'PLC'),
    (0, 1) : (0, 'PLC'),
    (0, 2) : (0, 'PLC'),
    (0, 3) : (0, 'PLC'),
    (0, 4) : (0, 'PLC')
    }

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

def WriteText(ID:int, *, text:str, TextAllign: str="Left", colour:str='white', FontName:str="Courier", FontSize:int=8, FontType:str="Bold"):
    t = TurtleText[ID][0]
    x = TurtleText[ID][1]
    y = TurtleText[ID][2]

    t.teleport(x, y)
    t.pendown()
    t.color(colour)
    t.write(text, False, TextAllign, font=(FontName, FontSize, FontType))
    t.penup()

def ClearText(ID:int):
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
    '.#........#........#.',
    '.#.##.###.#.###.##.#.',
    '.#.##.###.#.###.##.#.',
    '.#.................#.',
    '.#.##.#.#####.#.##.#.',
    '.#....#...#...#....#.',
    '.####.###.#.###.####.',
    '....#.#.......#.#....',
    '.####.#.##d##.#.####.',
    't.......#...#.......t',
    '.####.#.#####.#.####.',
    '....#.#.......#.#....',
    '.####.#.#####.#.####.',
    '.#........#........#.',
    '.#.##.###.#.###.##.#.',
    '.#..#...........#..#.',
    '.##.#.#.#####.#.#.##.',
    '.#....#...#...#....#.',
    '.#.######.#.######.#',
    '.#.................#.',
    '.###################.',
]

def world(colour:str='blue'):
    r.color(colour)
    y = begin_y
    for rij in wereld:
        x = begin_x
        for teken in rij:
            if teken == '#':
                Create_Collision_Object(x+round(GridStepSize/2), y+round(GridStepSize/2), coordinates=(x+30, y+30), TypeID=0)
                muur(x, y)
            if teken == 't':
                TeleporterCreator(x, y)
            x = x + 30
        y = y - 30

def DotLoad():
    global Dots
    y = begin_y
    for rij in wereld:
        x = begin_x
        for teken in rij:
            if teken == 'o':
                Create_Collision_Object(x+round(GridStepSize/2), y+round(GridStepSize/2), coordinates=(x+30, y+30), TypeID=2)
                puntje(x+round(GridStepSize/2), y+round(GridStepSize/2))
                Dots += 1
            if teken == '*':
                Create_Collision_Object(x+round(GridStepSize/2), y+round(GridStepSize/2), coordinates=(x+30, y+30), TypeID=3)
                puntje(x+round(GridStepSize/2), y+round(GridStepSize/2), 14)
                Dots += 1
            x = x + 30
        y = y - 30

def SpecialLoad():
    global Dots
    y = begin_y
    for rij in wereld:
        x = begin_x
        for teken in rij:
            if teken == 't':
                Create_Collision_Object(x+round(GridStepSize/2), y+round(GridStepSize/2), coordinates=(x+30, y+30), TypeID=4)
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
    for _ in range(4):
        for c in ['yellow', 'blue']:
            ClearMap()
            world(c)
    ClearMap()
    world()
    DotLoad()
    SpecialLoad()

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

    if Start == Goal:
        return 'Turn'

    if not On_Grid(StartX, StartY):
        return

    if not On_Grid(GoalX, GoalY):
        return

    if Collision_Coord_Check(*Start) in CollisionIDs:
        return

    if Collision_Coord_Check(*Goal) in CollisionIDs:
        return
    
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

        if (previous[1], previous[2]) == Start:
            break

        step = (previous[1], previous[2])

    heading = previous[0]

    return heading

# Modes
MainAIMode = 'scatter'
def scatter():
    global MainAIMode
    MainAIMode = 'scatter'
    #global TarBlinky, TarInky, TarPinky, TarClyde
    #TarBlinky = (315, 135)
    #TarInky = (315, -435)
    #TarPinky = (-165, 135)
    #TarClyde = (-165, -435)

def chase():
    global MainAIMode
    MainAIMode = 'chase'
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

def ModeSwitch():
    LevelTimingList = [0, 7000, 20000, 7000, 20000, 5000, 20000, 5000] # THIS IS DEFINED PER LEVEL THESE ARE JUST TEST VARS!!!

    TimerList = [
        LevelTimingList[0],
        sum(LevelTimingList[:2]),
        sum(LevelTimingList[:3]),
        sum(LevelTimingList[:4]),
        sum(LevelTimingList[:5]),
        sum(LevelTimingList[:6]),
        sum(LevelTimingList[:7]),
        sum(LevelTimingList[:8])
    ]

    for Timer in range(0, 7, 2):
        turtle.ontimer(scatter, TimerList[Timer])
        turtle.ontimer(chase, TimerList[Timer])

# Blinky
BlinkyMode = 'scatter'
def BlinkyModeChange(eaten:bool=False):
    global BlinkyMode
    if freight:
        blg.right(180)
        BlinkyMode = 'scatter'
    elif eaten:
        blg.right(180)
        BlinkyMode = 'eaten'
    else:
        blg.right(180)
        BlinkyMode = MainAIMode

def BlinkyMove():
    LevelDotAngry = 20
    if BlinkyMode == 'scatter' and Dots > LevelDotAngry:
        TarBlinky = (315, 135)
    elif BlinkyMode == 'scatter' and Dots <= LevelDotAngry:
        TarBlinky = (p.xcor(), p.ycor())
    elif BlinkyMode == 'chase':
        TarBlinky = (p.xcor(), p.ycor())
    elif BlinkyMode == 'eaten':
        TarBlinky = (60, -180)
    elif BlinkyMode == 'freight':
        TarBlinky = (p.xcor(), p.ycor())
        TurnBlink = random.randint(-1, 1)
        blg.right(90*TurnBlink)
        blg.forward(30)
    else:
        raise RuntimeError(f"Unknown mode: '{BlinkyMode}' !")

    Heading = bfs(blg.xcor(), blg.ycor(), blg.heading(), *TarBlinky)
    if Heading == None:
        return
    if Heading == 'Turn':
        if Collision_Check(blg.xcor(), blg.ycor(), 90):
            blg.setheading(90)
            blg.forward(30)
        elif Collision_Check(blg.xcor(), blg.ycor(), 180):
            blg.setheading(180)
            blg.forward(30)
        elif Collision_Check(blg.xcor(), blg.ycor(), 270):
            blg.setheading(270)
            blg.forward(30)
        elif Collision_Check(blg.xcor(), blg.ycor(), 0):
            blg.setheading(0)
            blg.forward(30)
        return

    blg.setheading(Heading)
    if Collision_Check(blg.xcor(), blg.ycor(), Heading):
        blg.forward(30)
    return

# Pinky
PinkyMode = 'scatter'
def PinkyModeChange(eaten:bool = False):
    global PinkyMode
    if freight:
        pig.right(180)
        PinkyMode = 'scatter'
    elif eaten:
        pig.right(180)
        PinkyMode = 'eaten'
    else:
        pig.right(180)
        PinkyMode = MainAIMode

def PinkyMove():
    if PinkyMode == 'scatter':
        TarPinky = (-165, 135)
    elif PinkyMode == 'chase':
        if int(round(p.heading())) == 90:
            Pink: tuple[int, int] = Destination_Calculator(p.xcor(), p.ycor(), 90, 120)
            Pinki = Destination_Calculator(*Pink, 180, 120)
            Pinky = (Pinki[0]*2, Pinki[1]*2)
        else:
            Pinki = Destination_Calculator(p.xcor(), p.ycor(), p.heading(), 120)
            Pinky = (Pinki[0]*2, Pinki[1]*2)
        TarPinky = Pinky
    elif PinkyMode == 'eaten':
        TarPinky = (60, -180)
    elif PinkyMode == 'freight':
        TarPinky = (p.xcor(), p.ycor())
        TurnPink = random.randint(-1, 1)
        pig.right(90*TurnPink)
        pig.forward(30)
    else:
        raise RuntimeError(f"Unknown mode: '{PinkyMode}' !")

    Heading = bfs(pig.xcor(), pig.ycor(), pig.heading(), *TarPinky)
    if Heading == None:
        return
    if Heading == 'Turn':
        if Collision_Check(pig.xcor(), pig.ycor(), 90):
            pig.setheading(90)
            pig.forward(30)
        elif Collision_Check(pig.xcor(), pig.ycor(), 180):
            pig.setheading(180)
            pig.forward(30)
        elif Collision_Check(pig.xcor(), pig.ycor(), 270):
            pig.setheading(270)
            pig.forward(30)
        elif Collision_Check(pig.xcor(), pig.ycor(), 0):
            pig.setheading(0)
            pig.forward(30)
        return

    pig.setheading(Heading)
    if Collision_Check(pig.xcor(), pig.ycor(), Heading):
        pig.forward(30)
    return

# Pinky
PinkyMode = 'scatter'
def PinkyModeChange(eaten:bool = False):
    global PinkyMode
    if freight:
        pig.right(180)
        PinkyMode = 'scatter'
    elif eaten:
        pig.right(180)
        PinkyMode = 'eaten'
    else:
        pig.right(180)
        PinkyMode = MainAIMode

def PinkyMove():
    if PinkyMode == 'scatter':
        TarPinky = (-165, 135)
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
        TurnPink = random.randint(-1, 1)
        pig.right(90*TurnPink)
        pig.forward(30)
    else:
        raise RuntimeError(f"Unknown mode: '{PinkyMode}' !")

    Heading = bfs(pig.xcor(), pig.ycor(), pig.heading(), *TarPinky)
    if Heading == None:
        return
    if Heading == 'Turn':
        if Collision_Check(pig.xcor(), pig.ycor(), 90):
            pig.setheading(90)
            pig.forward(30)
        elif Collision_Check(pig.xcor(), pig.ycor(), 180):
            pig.setheading(180)
            pig.forward(30)
        elif Collision_Check(pig.xcor(), pig.ycor(), 270):
            pig.setheading(270)
            pig.forward(30)
        elif Collision_Check(pig.xcor(), pig.ycor(), 0):
            pig.setheading(0)
            pig.forward(30)
        return

    pig.setheading(Heading)
    if Collision_Check(pig.xcor(), pig.ycor(), Heading):
        pig.forward(30)
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
    WriteText(1, text='You Died!', colour='red', TextAllign='center')

    turtle.onkey(None, 'Right') # type:ignore
    turtle.onkey(None, 'Left') # type:ignore
    turtle.onkey(None, 'Up') # type:ignore
    turtle.onkey(None, 'Down') # type:ignore
    turtle.onkey(None, 'd') # type:ignore

    r.clear()
    
    global gamestate, Loop
    Loop = False
    gamestate = 0
    GameStateOn()

# Tick Loops
LevelTimeElapsed = 0

def InitLoops():
    global Loop
    Loop = True
    WalkLoop()
    TickLoop()
    BlinkyLoop()

def TickLoop():
    print('Main AI Loop: ' + MainAIMode + ', Blinky: ' + BlinkyMode + ', Pinky: ' + PinkyMode)

    p_cor = (p.xcor(), p.ycor())
    blg_cor = (blg.xcor(), blg.ycor())
    pig_cor = (pig.xcor(), pig.ycor())
    ing_cor = (ing.xcor(), ing.ycor())
    clg_cor = (clg.xcor(), clg.ycor())

    global level, Dots, LevelTimeElapsed, EatenStreakFreight, Points

    blg_to_p_dis = Distance_Calculator(*blg_cor, *p_cor)
    if blg_to_p_dis[0] <= 25 and blg_to_p_dis[1] <= 25:
        if BlinkyMode == 'freight':
            Points += 200 * (2 ** EatenStreakFreight)
            EatenStreakFreight += 1
            BlinkyModeChange(True)
        if not BlinkyMode in ['freight', 'eaten']:
            GameOver()

    pig_to_p_dis = Distance_Calculator(*pig_cor, *p_cor)
    if pig_to_p_dis[0] <= 25 and pig_to_p_dis[1] <= 25:
        if PinkyMode == 'freight':
            Points += 200 * (2 ** EatenStreakFreight)
            EatenStreakFreight += 1
            PinkyModeChange(True)
        if not BlinkyMode in ['freight', 'eaten']:
            GameOver()

    InkyMode = 'scatter' #temp
    ing_to_p_dis = Distance_Calculator(*ing_cor, *p_cor)
    if ing_to_p_dis[0] <= 25 and ing_to_p_dis[1] <= 25:
        if InkyMode == 'freight':
            Points += 200 * (2 ** EatenStreakFreight)
            EatenStreakFreight += 1
            InkyModeChange(True)
        if not BlinkyMode in ['freight', 'eaten']:
            GameOver()

    ClydeMode = 'scatter' #temp
    clg_to_p_dis = Distance_Calculator(*clg_cor, *p_cor)
    if clg_to_p_dis[0] <= 25 and clg_to_p_dis[1] <= 25:
        if ClydeMode == 'freight':
            Points += 200 * (2 ** EatenStreakFreight)
            EatenStreakFreight += 1
            ClydeModeChange(True)
        if not BlinkyMode in ['freight', 'eaten']:
            GameOver()
            
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

    BlinkyMove()

    Tuppd = Collision_Coord_Check(blg.xcor(), blg.ycor(), lbObjID=True)
    if isinstance(Tuppd, tuple):
        Tupped:tuple[int|None, int|None] = Tuppd
        TypeID = Tupped[0]
        ObjID = Tupped[1]
    else:
        TypeID = -100
        ObjID = -10000
        raise RuntimeError("How?")

    if ObjID != None and TypeID != None:
        if TypeID == 0:
            blg.teleport(begin_x+75, begin_y-15)
            print('Out of Bounds')

        if TypeID == 1:
            teleportertp(ObjID, blg)

        if TypeID == 4:
            t -= 60

    t -= max(20 - 5 * level, 0)

    print('Blinky: ' + str(time := int(round(142 / (1+(t*0.01))))))

    if Loop:
        turtle.ontimer(BlinkyLoop, time)
    else:
        return

LevelDotSlowdown = 11.25
LevelFreightSpeedUp = 12.5
def WalkLoop():
    t = 0

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
            print('trig 2')
            Remove_Collision_Object(p.xcor()+round(GridStepSize/2), p.ycor()+round(GridStepSize/2), coordinates=(p.xcor()+30, p.ycor()+30), TypeID=2)
            Dots -= 1
            Points += 10
            r.teleport(p.xcor()-14, p.ycor()-14)
            r.setheading(0)
            r.penup()
            blok(28, 'black')
            r.pendown()
            t -= LevelDotSlowdown

        if TypeID == 3:
            print('trig 3')
            Remove_Collision_Object(p.xcor()+round(GridStepSize/2), p.ycor()+round(GridStepSize/2), coordinates=(p.xcor()+30, p.ycor()+30), TypeID=3)
            Dots -= 1
            Points += 50
            r.teleport(p.xcor()-14, p.ycor()-14)
            r.setheading(0)
            r.penup()
            blok(28, 'black')
            r.pendown()
            t -= LevelDotSlowdown
            FreightMode()
        #print(Dots)

    if freight:
        t += LevelFreightSpeedUp

    if bdebug:
        print(p.xcor(), p.ycor())

    t -= max(20 - 5 * level, 0)

    print('Paccy: ' + str(time := int(round(142 / (1+(t*0.01))))))

    if Loop:
        turtle.ontimer(WalkLoop, time)
    else:
        return

def DebugPost():
    print(str(p.xcor()) + ', ' + str(p.ycor()))

CreateText(0, GridOriginX, -30) # Press any key
CreateText(1, GridOriginX, 30) # You Died text

# AIs/Enemies
TarBlinky = (315, 135)
TarInky = (315, -435)
TarPinky = (-165, 135)
TarClyde = (-165, -435)

blg = turtle.Turtle()
blg.speed(0)
blg.color('red')
blg.penup()
blg.teleport(75, -135)
blg.setheading(90)

pig = turtle.Turtle()
pig.speed(0)
pig.color('deeppink')
pig.penup()
pig.teleport(*TarPinky)

ing = turtle.Turtle()
ing.speed(0)
ing.color('cyan')
ing.penup()
ing.teleport(*TarInky)

clg = turtle.Turtle()
clg.speed(0)
clg.color('sandybrown')
clg.penup()
clg.teleport(*TarClyde)

def GameStateOn():
    global gamestate
    match gamestate:
        case 0: # Press any key (not so any)
            WriteText(0, text='Press Any Key To Start...', TextAllign='center')

            def GameStateNext():
                global gamestate
                turtle.onkey(None, 'space') #type:ignore

                ClearText(0)
                ClearText(1)

                gamestate += 1
                GameStateOn()

            #def debug():
            #    print(gamestate)

            turtle.onkey(GameStateNext, 'space')
            turtle.listen()
        case 1:
            try:
                sel = 0
                print(Highscores)
                print(HighscoreKeys := Highscores.keys())

                print(HighscoreKeys)
                HighscoreKeys = sorted(HighscoreKeys, key=itemgetter(0))

                HighscoreStr: dict[tuple[int, int],tuple[int, str, str]] = {}
                for hs, id in HighscoreKeys:
                    ZeroNumber = str(hs).zfill(8)
                    DataTransfer = Highscores[(hs, id)]
                    HighscoreStr[(hs, id)] = (*DataTransfer, ZeroNumber)

                # Complete this code
                def ActionEvent():
                    nonlocal sel
                    if sel < 0:
                        sel = 5
                    match sel:
                        case 0:
                            global gamestate
                            turtle.onkey(None, 'z') #type:ignore
                            turtle.onkey(None, 'Enter') #type:ignore
                            turtle.onkey(None, 'Up') #type:ignore
                            turtle.onkey(None, 'Down') #type:ignore
                            gamestate = 2
                            GameStateOn()
                        case 1: # Start Menu
                            pass
                        case 2: # quit
                            pass
                        case _:
                            sel = 0
                            ActionEvent()

                def MinusSel():
                    nonlocal sel
                    sel -= 1

                def PlusSel():
                    nonlocal sel
                    sel += 1

                turtle.onkey(ActionEvent, 'z')
                turtle.onkey(ActionEvent, 'Enter')
                turtle.onkey(MinusSel, 'Up')
                turtle.onkey(PlusSel, 'Down')
                turtle.listen()
            except Exception as e:
                print(f'Gamestate 1 Crashed and returned to state 0\nException: {e}')
                gamestate = 0
        case 2:
            #try:
                # World Map Loader
                world()
                DotLoad()

                # Player Character
                p.penup()
                p.teleport(45, -315)
                p.shape('circle')
                p.color('gold')

                ModeSwitch()

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
        case _:
            gamestate = 0

GameStateOn()

def debug():
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
