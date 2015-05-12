"""OpenGL program in Python
Draws a reference grid and a randomly generated 3d path.
We'll soon use it to plot data fetched from a 3-axis accelerometer connected to an Arduino.
"""

tolerable_error = 500 #msec
main_theme_start_time = (60*1 + 45)


render_3d = False
render_graph = False
arduino_bridge = False #read i2c data directly from RPi GPIO instad
log_data = False

if not arduino_bridge:
    from Adafruit_LSM303 import Adafruit_LSM303

#song and feedback sound samples 
MAIN_THEME = 'data/main_theme.mp3'
GOOD_FEEDBACK = 'data/good_feedback.ogg'
BAD_FEEDBACK = 'data/bad_feedback.ogg'

import pygame
pygame.mixer.init()
pygame.mixer.pre_init(44100, -16, 2, 2048)
main_theme = pygame.mixer.music.load(MAIN_THEME)
good_sample = pygame.mixer.Sound(GOOD_FEEDBACK)
bad_sample = pygame.mixer.Sound(BAD_FEEDBACK)

hit_patterns = [
    {
        'name': "warm-up / freestyle",
        'start': "0:00.000",
        'loop_length': "1:40.000",
        'hits': [],
        'loops': 1 #this means it will play once (it won't loop!)
    },
    {
        'name': "jab, jab; jab, right",
        'start': "1:50.000",
        'loop_length': "0:04.000",
        'hits': [
            {
                'name': "jab",
                'time': "0:02.001",
            },
            {
                'name': "jab",
                'time': "0:02.335",
            },
            {
                'name': "jab",
                'time': "0:03.168",
            },
            {
                'name': "right",
                'time': "0:03.666",
            },
        ],
        'loops': 48
    },
    {
        'name': "[break]",
        'start': "5:00.000",
        'loop_length': "0:50.000",
        'hits': [],
        'loops': 1
    },
    {
        'name': "jab, direto; cruzado, direto",
        'start': "6:00.000",
        'loop_length': "0:03.986",
        'hits': [
            {
                'name': "jab",
                'time': "0:02.668",
            },
            {
                'name': "direto",
                'time': "0:03.002",
            },
            {
                'name': "cruzado",
                'time': "0:04.496",
            },
            {
                'name': "direto",
                'time': "0:04.852",
            },
        ],
        'loops': 48
    }
]

player_score = 0

import math
def parse_time(s):
    minutes, seconds = s.split(":")
    msecs = 1000*(int(minutes)*60 + float(seconds))
#    print "s: %s (msecs: %f)" % (s, msecs)
    return msecs

def evaluate_hit(hit_time):
    global player_score
    min_error = None
    for pattern in hit_patterns:
        for hit in pattern['hits']:
            for i in range(pattern['loops']):
                _start = parse_time(pattern['start'])
                _loop_length = parse_time(pattern['loop_length'])
                _time = parse_time(hit['time'])
                absolute_candidate_time = _start + i*_loop_length + _time
                error = math.fabs(absolute_candidate_time - hit_time)
                #print "error: %f candidate: %f hit_time: %f" % (error, absolute_candidate_time, hit_time)
                if error < tolerable_error:
                    good_sample.play()
                    player_score +=1
                    if player_score == 4:
                        print "GREAT!"
                        #good_sample.play() ##this is wrong! It is not time-aligned to the main theme.
                        player_score = 0
                    return "GOOD (%d msecs)" % (error)
                if error < min_error or min_error == None:
                   min_error = error

    player_score = 0
    bad_sample.play()
    return "BAD (%d msecs)" % (min_error)

if render_3d:
    import OpenGL
    from OpenGL.GLUT import *
    from OpenGL.GL import *

from sys import argv

#Ideal adjustment for the actual boking bag setup
#hit_intensity_threashold = 20000

#Adjustment for holding the Arduino with the acelerometer sensor directly in bare hands
hit_intensity_threashold = 2000

if arduino_bridge:
    baudrate = 9600
    port = "/dev/ttyACM0"

    import serial

import sys

MAX_SAMPLES=1
samples = [0.0 for i in range(MAX_SAMPLES)]
cur_sample = 0

def add_sample(s):
    global samples, cur_sample
    samples[cur_sample] = s
    cur_sample = (cur_sample+1) % MAX_SAMPLES

DETECT_DEBOUNCE = 10 #delay between hit detections
                   #(measured in ammount of samples)

inhibit_counter = 0
def detect_hit():
    global samples, cur_sample, inhibit_counter

    if inhibit_counter > 0:
        inhibit_counter -= 1
        return False

    if samples[cur_sample] > hit_intensity_threashold:
            #print "samples[%d]=%f" % (cur_sample, samples[cur_sample])
            inhibit_counter = DETECT_DEBOUNCE
            return True

    return False

def parse_data(line):
    #print "line: '%s'" % line
    M = line.split("M:")[1].strip()
    A = line.split("A:")[1].split("M:")[0].strip()
    M = [float(v.strip()) for v in M.split("\t")]
    A = [float(v.strip()) for v in A.split("\t")]
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

def opengl_init (hit=False):
    "Set up several OpenGL state variables"
    # Background color
    if (hit):
        glClearColor (0.9, 0.6, 6.0, 0.0)
    else:
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
    glRotatef(angle+90, 0.0, 0.0, 1.0)
    render_grid(heihgt=0.3)

    if (render_graph):
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

def vector_cross(a, b):
    cross = [0, 0, 0]
    cross[0] = (a[1] * b[2]) - (a[2] * b[1])
    cross[1] = (a[2] * b[0]) - (a[0] * b[2])
    cross[2] = (a[0] * b[1]) - (a[1] * b[0])
    return cross

def vector_module(a):
    return math.sqrt(vector_dot(a, a))

def vector_dot(a, b):
  return (a[0] * b[0]) + (a[1] * b[1]) + (a[2] * b[2])

def vector_normalize(v):
    mag = vector_module(v)
    v[0] /= mag
    v[1] /= mag
    v[2] /= mag
    return v

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

def main_routine():
    init_path()

    if arduino_bridge:
        ser = serial.Serial(port, baudrate, timeout=1)
    else:
        lsm = Adafruit_LSM303()

    pygame.mixer.music.play(0, main_theme_start_time)

    while True:
        try:
            if arduino_bridge:
                line = ser.readline()
            else:
                A, M = lsm.read()
            try:
                if arduino_bridge:
                    A, M = parse_data(line)

                if (log_data):
                    print "acel x=%d y=%d z=%d\n" % (A[0], A[1], A[2])
                    print "Mag x=%d y=%d z=%d\n\n" % (M[0], M[1], M[2])

                add_sample(vector_module(A))
                hit = detect_hit()
                if (hit):
                    #A hit has been detected.
                    #Do something here!
                    hit_time = pygame.mixer.music.get_pos() + main_theme_start_time*1000
                    print "Detected a %s hit at: %s" % (evaluate_hit(hit_time), hit_time)

                if render_3d:
                    opengl_init(hit)
                    render_scene(A, M)
            except IndexError, ValueError:
                #sometimes in the beginning of a read we get only half of a line, which breaks the parser.
                #here we simply ignore that sample and move on.
                pass
        except KeyboardInterrupt:
            if arduino_bridge:
                ser.close()
            sys.exit()

if render_3d:
    glutInit(argv) 
    glutInitWindowSize(1200, 1200)
    glutCreateWindow("PunchSense")
    glutDisplayFunc(main_routine)
    opengl_init()
    glutMainLoop()
else:
    while True:
        main_routine()

