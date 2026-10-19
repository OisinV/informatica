from collections import deque
from .ExceptionClasses import *
import warnings
import math

# world coörds pattern:
# +int x, -int x, +int y, -int y
# or
# bigger x, smaller x, bigger y, smaller y
# or
# right, left, top, bottom
#
# collision object pattern:
# -int x, +int x, -int y, +int y
# or
# smaller x, bigger x, smaller y, bigger y
# or
# left, right, bottom, top

# pattern: (left, right, bottom, top): objID
collision: dict[tuple[int, int, int, int],int] = {}

GridOriginX: int = 0
GridOriginY: int = 0
GridStepSize: int = 0

WorldSmallestX: int = 0
WorldBiggestX: int = 0
WorldSmallestY: int = 0
WorldBiggestY: int = 0

def Set_Grid(
            SmallestX: int|float,
            BiggestX: int|float,
            SmallestY: int|float,
            BiggestY: int|float,
            GridStep:int|float,
            GridSizeX: int|float|None=None,
            GridSizeY: int|float|None=None
        ):
    sx = int(round(SmallestX))
    bx = int(round(BiggestX))
    sy = int(round(SmallestY))
    by = int(round(BiggestY))

    if GridSizeX == None:
        gx = int(round((sx + bx)/2))
    else:
        gx = int(round(GridSizeX))

    if GridSizeY == None:
        gy = int(round((sy + by)/2))
    else:
        gy = int(round(GridSizeY))

    if int(round(GridStep)) <= 0:
        raise ValueError("GridStep must round to a positive integer.")

    if sx >= bx or sy >= by:
        raise ValueError("World bounds must have positive dimensions.")

    global GridOriginX, GridOriginY, WorldSmallestX, WorldBiggestX, WorldSmallestY, WorldBiggestY, GridStepSize
    GridOriginX = gx
    GridOriginY = gy
    GridStepSize = int(round(GridStep))

    WorldBiggestX = bx
    WorldSmallestX = sx
    WorldBiggestY = by
    WorldSmallestY = sy

def GridCoords(x:int|float,y:int|float):
    if GridStepSize <= 0:
        raise RuntimeError(
            "You need to initialize the Grid Step Size before using most of this module!\nUse Set_Grid() with GridStep as not blank."
        )
    x = int(round(((x-GridOriginX) / GridStepSize))*GridStepSize + GridOriginX)
    y = int(round(((y-GridOriginY) / GridStepSize))*GridStepSize + GridOriginY)
    return x, y

def CollisionSet(CollisionList:dict[tuple[int, int, int, int],int]|None):
    global collision
    if CollisionList != None:
        collision = CollisionList
    return collision

def Collision_Object_Calculator(
        x:int|float,
        y:int|float,
        *,
        coordinates: tuple[int|float, int|float] | None = None,
        size: tuple[int|float, int|float|None] | None=None
    ) -> tuple[int, int, int, int]:
    

    if size != None:
        x = int(round(x))
        y = int(round(y))
        width = size[0]
        height = size[1]

        if height == None:
            height = width

        if width < 0 or height < 0:
            warnings.warn("Width and height are not recommended to be negative.", CannotBeNegative, 2)

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
        )
        
    return collisionobj

def Create_Collision_Object(
        x:int|float,
        y:int|float,
        *,
        coordinates: tuple[int|float, int|float] | None = None,
        size: tuple[int|float, int|float|None] | None=None,
        objID: int|None=None
    ) -> tuple[int, int, int, int]:

    if objID == None:
        objID = 0
    

    if coordinates != None and size != None:
        raise ValueError(
            "Cannot use x1/y1 together with width/height."
        )

    if (coordinates == None) and (size == None):
        raise ValueError(
            "Provide either x1/y1 or width with optionally height.\nAlso x1/y1 and width/height also cannot be used together."
        )

    collisionobj = Collision_Object_Calculator(x, y, coordinates=coordinates, size=size)

    collision[collisionobj] = objID
    return collisionobj

def Remove_Collision_Object(
        x:int|float,
        y:int|float,
        *,
        coordinates: tuple[int|float, int|float] | None = None,
        size: tuple[int|float, int|float|None] | None=None,
        objID: tuple[int, ...]|int|None=None
    ) -> tuple[tuple[int, int, int, int], bool]:

    if objID == None:
        objID = 0
    

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
    if collisionobj in collision:
        if isinstance(objID, tuple):
            if -1 in objID:
                del collision[collisionobj]
                s = True
            elif collision[collisionobj] in objID:
                del collision[collisionobj]
                s = True
        else:
            if collision[collisionobj] == objID:
                del collision[collisionobj]
                s = True
            elif objID == -1:
                del collision[collisionobj]
                s = True
    return collisionobj, s

def On_Grid(x:int, y:int) -> bool:
    if GridStepSize <= 0:
        raise RuntimeError(
            "You need to initialize the Grid Step Size before using most of this module!\nUse Set_Grid() with GridStep as not blank."
        )

    return (
        (x - GridOriginX) % GridStepSize == 0
        and (y - GridOriginY) % GridStepSize == 0
    )

# StartX and StartY = Where is the thing that is gonna move
# GoalX and GoalY = Where is the thing we wanna move towards
def bfs(StartX:int, StartY:int, GoalX:int, GoalY:int):
    global GridStepSize
    if GridStepSize <= 0:
        raise RuntimeError("Call Set_Grid to initialize this module's grid, as currently GridStepSize is 0 or a negative integer.")
    GridSize = GridStepSize

    Start = (round(StartX), round(StartY))
    Goal = (round(GoalX), round(GoalY))
    directions = [ # all difference, so use dx, dy for calling :) (took me too long)
        (GridSize, 0), # east 0
        (0, GridSize), # north 90
        (-GridSize, 0), # west 180
        (0, -GridSize) # south 270
    ]

    if not On_Grid(StartX, StartY):
        return False

    if not On_Grid(GoalX, GoalY):
        return False

    if Collision_Coord_Check(*Start):
        return False

    if Collision_Coord_Check(*Goal):
        return False
    
    qeue = deque([Start])
    parent: dict[tuple[int, int], tuple[int, int] | None] = {Start:None}

    while qeue:
        current = qeue.popleft()

        if current == Goal:
            break

        for dx, dy in directions:
            nx = current[0] + dx
            ny = current[1] + dy
            nxt = (nx, ny)

            if nxt in parent:
                continue

            if Collision_Coord_Check(nx, ny):
                continue

            parent[nxt] = current
            qeue.append(nxt)

    if Goal not in parent:
        return

    step: tuple[int, int] = Goal

    while True:
        previous = parent[step]

        if previous == None:
            return

        if previous == Start:
            break

        step = previous

    dx = step[0] - Start[0]
    dy = step[1] - Start[1]

    heading = {
        (GridSize, 0): 0,
        (0, GridSize): 90,
        (-GridSize, 0): 180,
        (0, -GridSize): 270
    }[(dx, dy)]

    return heading

def Collision_Coord_Check(x:int, y:int):
    
    if not (WorldSmallestX <= x <= WorldBiggestX):
        return True
    if not (WorldSmallestY <= y <=  WorldBiggestY):
        return True
    
    for x1, x2, y1, y2 in collision:
        if x1 <= x <= x2 and y1 <= y <= y2:
            return True
        
    return False

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
        turn:int|float,
        slices:int=1,
        delta:int|float|None=None
    ):
    if slices >= 1000:
        warnings.warn(
            "This amount of slices is too many, as a safety, I have stopped the function.",
            RecommendedTooBig,
            2
        )
        return
    if slices >= 150:
        warnings.warn(
            "This amount of slices is too many, it is recomended that you make the amount smaller as to make this less expensive for the computer to calculate.",
            RecommendedTooBig,
            2
        )
    if slices <= 0:
        raise ValueError("The amount of slices must be a positive interger.")

    if delta == None:
        delta = GridStepSize

    if delta < 0:
        raise ValueError("Delta cannot be negative.")

    slices = min(slices, max(1, math.ceil(abs(delta))))
    headto = (heading-turn)%360

    for i in range(1, slices+1):
        dis = int(round(delta*i/slices))
        rx, ry = Destination_Calculator(x, y, headto, dis)
        if Collision_Coord_Check(rx, ry):
            return False
    return True
