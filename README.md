# 5Cuber
An original 5x5 Rubik's cube solving robot powered by Python, OpenCV, and Lego Mindstorms
![alt text](https://i.imgur.com/vOwPCCQ.jpg)

## How it works
  * All six sides of the cube are scanned with OpenCV image processing, which identifies the colours of the tiles
  * This colour information is then passed onto an [NxNxN cube solving algorithm](https://github.com/dwalton76/rubiks-cube-NxNxN-solver) written by [dwalton76](https://github.com/dwalton76). The algorithm generates a solution to solve the 5x5 cube
  * The robot then executes the solution one move at a time, using a combination of 4 mechanisms to manipulate the cube as needed. The robot is controlled by a Python script that interprets the move notation and keeps track of the cube's 3D orientation during the solve

More pictures and a video coming soon!
![alt text](https://i.imgur.com/4OY9197.jpg)
