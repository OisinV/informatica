from collections import deque
import math

# world coörds pattern:
# +int x, -int x, +int y, -int y
# or
# bigger x, smaller x, bigger y, smaller y
#
# collision object pattern:
# -int x, +int x, -int y, +int y
# or
# smaller x, bigger x, smaller y, bigger y

# pattern: left, right, bottom, top
collision: set[tuple[int, int, int, int]] = set()

def CollisionSet(CollisionList:set[tuple[int, int, int, int]]|None):
    global collision
    if CollisionList != None:
        collision = CollisionList
    return collision

def Create_Collision_Object(
        x:int|float,
        y:int|float,
        x1:int|float|None=None,
        y1:int|float|None=None,
        width:int|float|None=None,
        height:int|float|None=None
    ):
    global collisionobj
    
    coordinates = x1 != None or y1 != None
    dimensions = width != None or height != None

    if coordinates and dimensions:
        raise ValueError(
            "Cannot use x1/y1 together with width/height."
        )

    if coordinates and (x1 == None or y1 == None):
        raise ValueError(
            "Both x1 and y1 must be provided."
        )

    if not coordinates and width == None:
        raise ValueError(
            "Provide either x1/y1 or width with optionally height.\nAlso x1/y1 also cannot be used together."
        )

    if height == None and dimensions:
        height = width

    if dimensions:
        x = int(round(x))
        y = int(round(y))
        
        collisionobj: tuple[int, int, int, int] = (
            int(x-width/2), # type:ignore
            int(x+width/2), # type:ignore
            int(y-height/2), # type:ignore
            int(y+height/2) # type:ignore
        )
    if coordinates:
        x = int(round(x))
        x1 = int(round(x1)) # type:ignore
        y = int(round(y))
        y1 = int(round(y1)) # type:ignore
    
        collisionobj: tuple[int, int, int, int] = (
            int(x),
            int(x1),
            int(y),
            int(y1)
        )

    collision.add(collisionobj)
    return None

def Remove_Collision_Object(
        x:int|float,
        y:int|float,
        x1:int|float|None=None,
        y1:int|float|None=None,
        width:int|float|None=None,
        height:int|float|None=None
    ):
    global collisionobj

    coordinates = x1 != None or y1 != None
    dimensions = width != None or height != None

    if coordinates and dimensions:
        raise ValueError(
            "Cannot use x1/y1 together with width/height."
        )

    if coordinates and (x1 == None or y1 == None):
        raise ValueError(
            "Both x1 and y1 must be provided."
        )

    if not coordinates and width == None:
        raise ValueError(
            "Provide either x1/y1 or width with optionally height.\nAlso x1/y1 also cannot be used together."
        )

    if height == None and dimensions:
        height = width

    if dimensions:
        x = int(round(x))
        y = int(round(y))

        collisionobj: tuple[int, int, int, int] = (
            int(x-width/2), # type:ignore
            int(x+width/2), # type:ignore
            int(y-height/2), # type:ignore
            int(y+height/2) # type:ignore
        )
    if coordinates:
        x = int(round(x))
        x1 = int(round(x1)) # type:ignore
        y = int(round(y))
        y1 = int(round(y1)) # type:ignore
    
        collisionobj: tuple[int, int, int, int] = (
            int(x),
            int(x1),
            int(y),
            int(y1)
        )
    
    while collisionobj in collision:
        collision.discard(collisionobj)
    return None

# StartX and StartY = Where is the thing that is gonna move
# GoalX and GoalY = Where is the thing we wanna move towards
def bfs(StartX:int, StartY:int, GoalX:int, GoalY:int, GridSize:int):
    Start = (round(StartX), round(StartY))
    Goal = (round(GoalX), round(GoalY))
    directions = [ # all difference, so use dx, dy for calling :) (took me too long)
        (GridSize, 0), # east 0
        (0, GridSize), # north 90
        (-GridSize, 0), # west 180
        (0, -GridSize) # south 270
    ]

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
def Collision_Check(delta:int|float, x:int|float, y:int|float, heading:int|float, turn:int|float):
    headto = (heading-turn)%360
    x, y = Destination_Calculator(x, y, headto, delta)
    return not Collision_Coord_Check(x, y)
