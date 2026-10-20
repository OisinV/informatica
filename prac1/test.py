# m t (empty)

heading = 90

t = {
    0:(30, 0),
    90:(0, 30),
    180:(-30, 0),
    270:(0,-30)
}
t.pop(360-heading)
t = list(t.values())
print(t)