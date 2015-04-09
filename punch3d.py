"""OpenGL program in Python
Draws a reference grid and a randomly generated 3d path.
We'll soon use it to plot data fetched from a 3-axis accelerometer connected to an Arduino.
"""

import OpenGL
from OpenGL.GLUT import *
from OpenGL.GL import *
from sys import argv


baudrate = 9600
port = "/dev/ttyACM0"

import serial
import sys


def parse_data(line):
    M = line.split("M:")[1].strip()
    A = line.split("A:")[1].split("M:")[0].strip()
    M = [int(v) for v in M.split("\t")]
    A = [int(v) for v in A.split("\t")]
    return [A, M]


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

import math
angle = 0
def render_scene(A, M):
    global angle, path
#    angle += 0.4
    angle = 360*math.atan2(M[1], M[0])/(2*3.1415)

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
    ser = serial.Serial(port, baudrate, timeout=1)
    while True:
        try:
            line = ser.readline()
            try:
                A, M = parse_data(line)
                print "acel x=%d y=%d z=%d\n" % (A[0], A[1], A[2])
                print "Mag x=%d y=%d z=%d\n\n" % (M[0], M[1], M[2])
                opengl_init()
                render_scene(A, M)
            except IndexError:
                #sometimes in the beginning of a read we get only half of a line, which breaks the parser.
                #here we simply ignore that sample and move on.
                pass
        except KeyboardInterrupt:
            ser.close()
            sys.exit()

glutInit(argv) 
glutInitWindowSize(1200, 1200)
glutCreateWindow("PunchSense")
glutDisplayFunc(render_routine)
opengl_init()
glutMainLoop()
