import math
import random
import tkinter as tk
from tkinter import *
import numpy as np
from PIL import Image, ImageTk

N = 50
iter = 16
SCALE = 1
t = 0
size = N
dt = 0.5
diff = 0.00001
visc = 0.00000001
colorcode = []
# particles are rectangles with colors
particles = []
root = tk.Tk()

canvas = tk.Canvas(root, width=1215, height=1215)
# saving colors from black to blue to green to red and then fetching it as density
ss = "0123456789abcdef"
nss = "fedcba9876543210"
for x in ss:
    for y in ss:
        colorcode.append("#" + "00" + "00" + str(x) + str(y))
for x in ss:
    for y in ss:
        colorcode.append("#" + "00" + str(x) + str(y) + "ff")
for x in nss:
    for y in nss:
        colorcode.append("#" + "00" + "ff" + str(x) + str(y))
for x in ss:
    for y in ss:
        colorcode.append("#" + str(x) + str(y) + "ff" + "00")
for x in nss:
    for y in nss:
        colorcode.append("#" + "ff" + str(x) + str(y) + "00")
# added this if the intensity is above the color range, so the density above a certain threshold will be red
for x in range(80000):
    colorcode.append("#ff0000")
# making rectangles
for y in range(0, 1200, 24):
    for x in range(0, 1200, 24):
        particles.append([canvas.create_rectangle(x, y, x + 24, y + 24, fill="grey" + str(5), width=0)])

canvas.pack()
pixels = np.zeros((N, N))

s = [0] * (N * N)
density = [0] * (N * N)

Vx = [0] * (N * N)
Vy = [0] * (N * N)

Vx0 = [0] * (N * N)
Vy0 = [0] * (N * N)


# function to use 1D array and fake the extra two dimensions --> 3D
def IX(x, y):
    return x + y * N


def set_bnd(b, x):
    for i in range(1, N - 1):
        x[IX(i, 0)] = -x[IX(i, 1)] if b == 2 else x[IX(i, 1)]
        x[IX(i, N - 1)] = -x[IX(i, N - 2)] if b == 2 else x[IX(i, N - 2)]

    for j in range(1, N - 1):
        x[IX(0, j)] = -x[IX(1, j)] if b == 1 else x[IX(1, j)];
        x[IX(N - 1, j)] = -x[IX(N - 2, j)] if b == 1 else x[IX(N - 2, j)]

    x[IX(0, 0)] = 0.5 * (x[IX(1, 0)] + x[IX(0, 1)])
    x[IX(0, N - 1)] = 0.5 * (x[IX(1, N - 1)] + x[IX(0, N - 2)])
    x[IX(N - 1, 0)] = 0.5 * (x[IX(N - 2, 0)] + x[IX(N - 1, 1)])
    x[IX(N - 1, N - 1)] = 0.5 * (x[IX(N - 2, N - 1)] + x[IX(N - 1, N - 2)])


def lin_solve(b, x, x0, a, c):
    cRecip = 1.0 / c
    for t in range(iter):
        for j in range(1, N - 1):
            for i in range(1, N - 1):
                x[IX(i, j)] = (x0[IX(i, j)] + a * (
                        x[IX(i + 1, j)] + x[IX(i - 1, j)] + x[IX(i, j + 1)] + x[IX(i, j - 1)])) * cRecip
        set_bnd(b, x)


def diffuse(b, x, x0, diff, dt):
    a = dt * diff * (N - 2) * (N - 2)
    lin_solve(b, x, x0, a, 1 + 6 * a)


def project(velocX, velocY, p, div):
    for j in range(1, N - 1):
        for i in range(1, N - 1):
            div[IX(i, j)] = (-0.5 * (
                    velocX[IX(i + 1, j)] - velocX[IX(i - 1, j)] + velocY[IX(i, j + 1)] - velocY[IX(i, j - 1)])) / N
            p[IX(i, j)] = 0
    set_bnd(0, div)
    set_bnd(0, p)
    lin_solve(0, p, div, 1, 6)
    for j in range(1, N - 1):
        for i in range(1, N - 1):
            velocX[IX(i, j)] -= 0.5 * (p[IX(i + 1, j)] - p[IX(i - 1, j)]) * N
            velocY[IX(i, j)] -= 0.5 * (p[IX(i, j + 1)] - p[IX(i, j - 1)]) * N
    set_bnd(1, velocX)
    set_bnd(2, velocY)


def advect(b, d, d0, velocX, velocY, dt):
    dtx = dt * (N - 2)
    dty = dt * (N - 2)
    Nfloat = N - 2
    for j in range(1, N - 1):
        for i in range(1, N - 1):
            tmp1 = dtx * velocX[IX(i, j)]
            tmp2 = dty * velocY[IX(i, j)]
            x = i - tmp1
            y = j - tmp2

            if x < 0.5:
                x = 0.5
            if x > Nfloat + 0.5:
                x = Nfloat + 0.5
            i0 = math.floor(x)
            i1 = i0 + 1.0
            if y < 0.5:
                y = 0.5
            if y > Nfloat + 0.5:
                y = Nfloat + 0.5
            j0 = math.floor(y)
            j1 = j0 + 1.0

            s1 = x - i0
            s0 = 1.0 - s1
            t1 = y - j0
            t0 = 1.0 - t1

            i0i = int(i0)
            i1i = int(i1)
            j0i = int(j0)
            j1i = int(j1)

            d[IX(i, j)] = s0 * (t0 * d0[IX(i0i, j0i)] + t1 * d0[IX(i0i, j1i)]) + s1 * (
                    t0 * d0[IX(i1i, j0i)] + t1 * d0[IX(i1i, j1i)])

    set_bnd(b, d)


def addDensity(x, y, amount):
    index = IX(x, y)
    density[index] += amount


def addVelocity(x, y, amountX, amountY):
    index = IX(x, y)
    Vx[index] += amountX
    Vy[index] += amountY


def renderD():
    for i in range(N):
        for j in range(N):
            x = i * SCALE
            y = j * SCALE
            d = density[IX(i, j)]  # use this to render
            canvas.itemconfig(particles[IX(i, j)], fill=colorcode[int(d)])


def step():
    diffuse(1, Vx0, Vx, visc, dt)
    diffuse(2, Vy0, Vy, visc, dt)

    project(Vx0, Vy0, Vx, Vy)

    advect(1, Vx, Vx0, Vx0, Vy0, dt)
    advect(2, Vy, Vy0, Vx0, Vy0, dt)

    project(Vx, Vy, Vx0, Vy0)
    diffuse(0, s, density, diff, dt)
    advect(0, density, s, Vx, Vy, dt)


mousedown = False


def mouse_down(e):
    global mousedown
    mousedown = True


def mouse_up(e):
    global mousedown
    mousedown = False


vx = 0.0
vy = 0.0
mx = 0
my = 0
omx = 0
omy = 0


def clamp(num, min_value, max_value):
    return max(min(num, max_value), min_value)


def addfluid():
    if mousedown:
        cx = mx
        cy = my
        if cx == 0:
            cx += 2
        if cy == 0:
            cy += 2
        if cx > 48:
            cx -= 2
        if cy > 48:
            cy -= 2
        for i in range(-1, 2):
            for j in range(-1, 2):
                addDensity(cx + i, cy + j, 350)
        for i in range(2):
            addVelocity(cx, cy, clamp(vx / 8.0, -1.5, 1.5) + random.uniform(-1.0, 1.0),
                        clamp(vy / 8.0, -1., 1.) + random.uniform(-1., 1.))


def motion(event):
    global mx, my, vx, vy, omx, omy
    mx = event.x
    my = event.y
    mx //= 24
    my //= 24
    vx = omx - mx
    vy = omy - my
    omx = mx
    omy = my


root.bind('<Motion>', motion)
root.bind('<Button 1>', mouse_down)
root.bind('<ButtonRelease 1>', mouse_up)
b = 0
while (1):
    root.update()
    addfluid()
    step()
    renderD()
    b += 1
