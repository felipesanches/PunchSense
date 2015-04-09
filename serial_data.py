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

ser = serial.Serial(port, baudrate, timeout=1)
while True:
    try:
        line = ser.readline()
        try:
            A, M = parse_data(line)
            print "acel x=%d y=%d z=%d\n" % (A[0], A[1], A[2])
            print "Mag x=%d y=%d z=%d\n\n" % (M[0], M[1], M[2])
        except IndexError:
            #sometimes in the beginning of a read we get only half of a line, which breaks the parser.
            #here we simply ignore that sample and move on.
            pass
    except KeyboardInterrupt:
        ser.close()
        sys.exit()

