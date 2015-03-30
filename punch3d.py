"""OpenGL program in Python
Draws a reference grid and a randomly generated 3d path.
We'll soon use it to plot data fetched from a 3-axis accelerometer connected to an Arduino.
"""

import OpenGL
from OpenGL.GLUT import *
from OpenGL.GL import *
from sys import argv

def render_grid(grid_size=0.1, M=8, N=5, heihgt=0):
    for x in range(M):
        for y in range(N):
            glBegin(GL_POLYGON)
            glNormal3f(0, 0, 1)
            glVertex3fv ([(x-float(M)/2) * grid_size,     (y-float(N)/2) * grid_size,   heihgt])
            glVertex3fv ([(x+1-float(M)/2) * grid_size,   (y-float(N)/2) * grid_size,   heihgt])
            glVertex3fv ([(x+1-float(M)/2) * grid_size,   (y+1-float(N)/2) * grid_size, heihgt])
            glVertex3fv ([(x-float(M)/2) * grid_size,     (y+1-float(N)/2) * grid_size, heihgt])
            glEnd()

import random
path = []
def init_path():
    global path
    path = []
    for i in range(20):
        dx = 0.02*(random.randint(-100, 100)/100.0)
        dy = 0.02*(random.randint(-100, 100)/100.0)
        dz = 0.04
        path.append([dx, dy, dz])

def opengl_init ():
    "Set up several OpenGL state variables"
    # Background color
    glClearColor (0.0, 0.0, 0.0, 0.0)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0);
    glShadeModel(GL_SMOOTH)
    glLightfv(GL_LIGHT0, GL_POSITION, [10, 10, 10, 1.0]);

    # Projection matrix
    glMatrixMode(GL_PROJECTION)
#    glPolygonMode(GL_FRONT, GL_LINE);
    glPolygonMode(GL_BACK, GL_LINE);
    glLoadIdentity()
    glOrtho(0.0, 1.0, 0.0, 1.0, -1.0, 1.0)

angle = 0
def render_scene():
    global angle, path
    angle += 0.4

    if (int(angle) % 30==0):
        init_path()

    # Clear frame buffer
    glClear (GL_COLOR_BUFFER_BIT);

    glTranslatef(0.0, -0.5, 0.5)

    glTranslatef(0.5, 0.5, 0.0)
    glRotatef(-90 -30, 1.0, 0.0, 0.0)
    glRotatef(angle, 0.0, 0.0, 1.0)
    render_grid(heihgt=0.3)

    glTranslatef(-0.5, -0.5, 0.0)

    # Set draw color to white
    glColor3f (1.0, 1.0, 1.0)

    x,y,z = [0.5, 0.5, 0.3]
    for i in range(len(path)):
        dx, dy, dz = path[i]
        render_segment(x, y, z, dx, dy, dz)
        x += dx
        y += dy
        z += dz

    # Flush and swap buffers
    glutSwapBuffers()

from math import cos, sin, sqrt
def render_segment(x,y,z, dx, dy, dz, r=0.04):
    N=20
    glColor3f(0.5, 0.0, 1.0)
    for i in range(N):
        glBegin(GL_POLYGON)
        glNormal3f(sin((i+0.5)*2*3.1415/N), cos((i+0.5)*2*3.1415/N), sqrt(dx*dx+dy*dy))
        glVertex3fv ([x+r*sin(i*2*3.1415/N), y+r*cos(i*2*3.1415/N), z])
        glVertex3fv ([x+r*sin((i+1)*2*3.1415/N), y+r*cos((i+1)*2*3.1415/N), z])
        glVertex3fv ([x+dx+r*sin((i+1)*2*3.1415/N), y+dy+r*cos((i+1)*2*3.1415/N), z+dz])
        glVertex3fv ([x+dx+r*sin(i*2*3.1415/N), y+dy+r*cos(i*2*3.1415/N), z+dz])
        glEnd()

def render_routine():
    init_path()
    while True:
        opengl_init()
        render_scene()

glutInit(argv) 
glutInitWindowSize(1200, 1200)
glutCreateWindow("PunchSense")
glutDisplayFunc(render_routine)
opengl_init()
glutMainLoop()
