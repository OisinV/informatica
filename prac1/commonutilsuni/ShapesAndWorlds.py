import turtle

saw = turtle.Turtle()

world = [
    '############',
    '#..........#',
    '#..........#',
    '#..........#',
    '#..........#',
    '#..........#',
    '############',
]

TopLeftY =  90
TopLeftX = -180
intialised, TrueAll = False, False

class _NotInitialisedError(Exception):
    pass

def WorldInitialise(lTopLeftY:int|None=None, lTopLeftX:int|None=None, lworld:list[str]|None=None, *, lTrueAll:bool|None=None):
    global TopLeftY, TopLeftX, world, TrueAll, intialised
    if not (lTopLeftY == None or lTopLeftX == None):
        TopLeftY = int(round(lTopLeftY))
        TopLeftX = int(round(lTopLeftX))
    if lworld != None:
        world = lworld
    if lTrueAll != None:
        TrueAll = lTrueAll
    intialised = True

def WorldMaker():
    if intialised:
        y = 90
        for row in world:
            x = -180
            for char in row:
                if char == '#':
                    wall(x, y)
                if char == '.':
                    saw.teleport(x, y)
                    cube(30, 'black')
                x = x + 30
            y = y - 30
    else:
        raise _NotInitialisedError("Please initialise the code by using WorldInitialise!")

def Template():
    if intialised:
        pass
    else:
        raise _NotInitialisedError("Please initialise the code by using WorldInitialise!")

__all__ = ["WorldInitialise", "WorldMaker"]
