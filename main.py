#!/usr/bin/env python3

"""
WARNING:
Before running the program, ensure that the robot is in initial state:
 - Clamp is contracted completely
 - Turntable is aligned
 - Plunger is at the lowest position

RUNNING THE PROGRAM:
1) In VS Code ev3dev Device Browser, right click connected ev3 device
   and click "Open SSH Terminal"
2) In the terminal, type "brickrun -r ./5Cuber/main.py" and press Enter
Now the robot can accept text input from terminal
"""

from ev3dev.ev3 import *
from time import sleep

MOTORSPEED = 400

# This array stores the amount the plunger needs to push the cube up
# for the different turn widths
# width:       1    2    3    4
plunge = [0.0, 4.3, 2.9, 1.5, 0.0]

# Initialize motors and button
mA = MediumMotor('outA')
mB = LargeMotor('outB')
mC = LargeMotor('outC')
mD = LargeMotor('outD')
mA.reset()
mB.reset()
mC.reset()
mD.reset()
button = Button()


def waitButtonPress():
    global button
    while True:
        if button.any():
            break

def spinClamp(quarterTurns):
    mA.run_to_rel_pos(position_sp=quarterTurns*-90, speed_sp=MOTORSPEED, stop_action="hold")
    mA.wait_while('running')

# One unit is the length of a LEGO stud
# 6 units: clamp contracts completely
# 5.3 units: optimal for gripping 5x5
# 0 units: clamp expands completely
def clamp(units):
    if units < 0 or units > 6:
        print("ERROR:", units, "units out of clamp range")
    else:
        pos = (6 - units) / 2 * 56.25
        mB.run_to_abs_pos(position_sp=pos, speed_sp=MOTORSPEED, stop_action="hold")
        mB.wait_while('running')

def turnTable(quarterTurns, shake):
    degrees = quarterTurns*-210
    if shake:
        mC.run_to_rel_pos(position_sp=degrees*1.1, speed_sp=MOTORSPEED, stop_action="hold")
        mC.wait_while('running')
        time.sleep(0.1)
        mC.run_to_rel_pos(position_sp=degrees*-0.14, speed_sp=MOTORSPEED, stop_action="hold")
        mC.wait_while('running')
        mC.run_to_rel_pos(position_sp=degrees*0.04, speed_sp=MOTORSPEED, stop_action="hold")
    else:
        mC.run_to_rel_pos(position_sp=degrees, speed_sp=MOTORSPEED, stop_action="hold")
    mC.wait_while('running')

# 0 units: plunger at bottom
# 6 units: plunger at top
def raisePlunger(units):
    if units < 0 or units > 6:
        print("ERROR:", units, "units out of plunger range")
    else:
        pos = units * 56.25
        mD.run_to_abs_pos(position_sp=pos, speed_sp=MOTORSPEED, stop_action="hold")
        mD.wait_while('running')

# Runs the scan process
def scan():
    # Wait for user to start the scan process
    waitButtonPress()
    
    # Scan RBLF
    for i in range(4):
        turnTable(1, False)
        raisePlunger(4.5)
        waitButtonPress()
        if i != 3:
            raisePlunger(0)
    
    # Scan U
    raisePlunger(6)
    clamp(5.3)
    raisePlunger(3)
    spinClamp(-1)
    raisePlunger(6)
    clamp(0)
    raisePlunger(4.5)
    waitButtonPress()

    # Scan D
    raisePlunger(6)
    clamp(5.3)
    raisePlunger(3)
    spinClamp(2)
    raisePlunger(6)
    clamp(0)
    raisePlunger(4.5)
    waitButtonPress()

    # Move cube back
    raisePlunger(6)
    clamp(5.3)
    raisePlunger(3)
    spinClamp(-1)
    raisePlunger(6)
    clamp(0)
    raisePlunger(0)

# Interprets WCA 5x5 notation and returns the parameters of a 5x5 move
# Stuff like "U D' Lw2 3Rw'"
# However, cube rotations and slice moves are not supported (yet)
def interpretMove(move):
    # The target face that needs to be turned
    try:
        int(move[0])
        # Then it starts with a number, so take the second character
        face = move[1]
    except ValueError:
        # Then it doesn't start with a number, take the first character instead
        face = move[0]

    # The rotation of the face
    if move[-1] == "'":  # ' means a quarter turn CCW
        rotation = -1
    elif move[-1] == "2":  # "2" means two quarter turns CW/CCW
        rotation = 2
    else:  # then the move must be a quarter turn CW
        rotation = 1

    # The "width" of the move
    if "w" in move:  # It's a "wide" move meaning width > 1
        # For 2wide, 3wide or 4wide moves that start with 2, 3 or 4
        if move[0] in ["2", "3", "4"]:
            width = int(move[0])
        # With no number in front, we assume it's 2wide
        else:
            width = 2
    else:  # It's a non-wide move so width is 1
        width = 1
    
    return face, rotation, width

def removeDuplicates(solution):
    solution = solution.split(" ")
    newSolution = ""
    nextMoveSkip = False
    for i in range(len(solution)-1):
        if nextMoveSkip:
            print("This move is to be skipped. Moving on...")
            nextMoveSkip = False
        else:
            currMove = solution[i]
            nextMove = solution[i+1]
            print("current move:", currMove)
            print("next move:", nextMove)

            currFace = currMove.replace("'", "").replace("2", "")
            nextFace = nextMove.replace("'", "").replace("2", "")
            print("current face:", currFace)
            print("next face:", nextFace)

            # If the curr and next affect the exact same face:
            if currFace == nextFace:
                print("They are the same. Something can be simplified")
                nextMoveSkip = True
                rotation = 0
                for move in [currMove, nextMove]:
                    if "'" in move:
                        rotation -= 1
                    elif "2" in move:
                        rotation += 2
                    else:
                        rotation += 1
                rotation = rotation % 4
                print("net rotation:", rotation)
                if rotation != 0:
                    newMove = currFace + str(rotation)
                    print("let's make a new move", newMove)
                    newSolution += newMove + " "
                else:
                    print("the two moves cancelled each other")
            else:
                newSolution += currMove + " "
        print()
    if not nextMoveSkip:
        newSolution += solution[-1]
    return newSolution

# Applies cube rotations to the order of the faces
def transform(order, cubeRotations):
    for rotation in cubeRotations:
        axis, quarterTurns = rotation
        if quarterTurns == -1:
            quarterTurns = 3  # A CCW quarter turn is the same as 3 CW
        # Now we rotate the four faces that are affected by the rotation
        if axis == "x":
            for i in range(quarterTurns):
                cycle = [order[1][1], order[2][1], order[1][3], order[0][1]]
                for [a, b, c] in [[0, 1, 0], [1, 1, 1], [2, 1, 2], [1, 3, 3]]:
                    order[a][b] = cycle[c]
        else:  # y rotation
            for i in range(quarterTurns):
                end = order[1][0]
                order[1] = order[1][1:4]
                order[1].append(end)
    return order

# Runs WCA 5x5 notation as actual moves
def runSolution(solution):
    # We will keep track of the order/position of the faces in a 2D array
    # The robot is only capable of x and y rotations, so the array is
    # laid out in a cross shape to represent x and y rotations as row and
    # column shifts (the X's represent empty spots)
    order = [
        ["X", "U", "X", "X"],
        ["L", "F", "R", "B"],
        ["X", "D", "X", "X"]
        ]
    moves = solution.split(" ")
    for move in moves:
        doRotations = True
        print("MOVE:", move)
        face, faceRotation, width = interpretMove(move)

        print(face, faceRotation, width)

        # We want the target face to be facing downwards
        # If not, we need to rotate the cube so it faces downwards
        # and then update the order of the faces to match the actual cube
        # Each cube rotation is an x or y indicating axis, and the number of CW quarter turns
        if face == order[0][1]:
            cubeRotations = [["x", 2]]
        elif face == order[1][0]:
            cubeRotations = [["y", 1], ["x", 1]]
        elif face == order[1][1]:
            cubeRotations = [["x", -1]]
        elif face == order[1][2]:
            cubeRotations = [["y", 1], ["x", -1]]
        elif face == order[1][3]:
            cubeRotations = [["x", 1]]
        # Otherwise, face is already in order[2][1] which means
        # it's already in the right spot, no rotation necessary
        else:
            doRotations = False

        # Perform cube rotations
        # spinClamp does x rotations, turnTable does y rotations
        print("ROTATIONS:", cubeRotations)
        if doRotations:
            order = transform(order, cubeRotations)
            for rotation in cubeRotations:
                axis, quarterTurns = rotation
                if axis == "x":
                    raisePlunger(6)  # Lift the cube up completely
                    clamp(5.3)  # Hold it tightly
                    raisePlunger(3)  # Lower the plunger to not interfere
                    spinClamp(quarterTurns)  # Perform the x rotation
                    raisePlunger(6)  # Raise the plunger to catch the cube
                    clamp(0)  # Release the cube

                else:  # y rotation
                    turnTable(quarterTurns, False)
        # Perform face rotations
        # NOTE: a CW turn to the cube is a CCW turn of the turntable!
        raisePlunger(plunge[width])  # Lift cube to specific level based on turn width
        clamp(5.3)  # Hold the cube in place
        turnTable(faceRotation*-1, True)  # Rotate the face
        clamp(0)  # Release the cube

def main():
    Leds.all_off()
    clamp(0)
    scan()
    solution = removeDuplicates(input("ENTER SOLUTION: "))
    runSolution(solution)
    Sound.beep().wait()
    raisePlunger(4)
    turnTable(8)
    print("CUBE SOLVED")

main()