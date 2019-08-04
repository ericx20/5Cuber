import os
import cv2

# half bright colours of QiYi WuShuang
# [red, green, blue]
colours = {
    "w": [183, 183, 183],
    "y": [2, 200, 189],
    "g": [3, 134, 0],
    "b": [93, 25, 2],
    "o": [4, 25, 239],
    "r": [5, 7, 128]
    }

def identifyColour(px):
    distances = {}
    for colour in colours:
        rgb = colours[colour]
        distance = 0
        for i in range(3):
            distance += abs(rgb[i] - px[i]) ** 2
        distances[distance] = colour
    return distances[min(distances)]

# Kociemba order: URFDLB
# Scan order: RBLFUD
# Process images in order: 4, 0, 3, 5, 2, 1

cubeStickers = []
faceCenters = ""
directory = r'C:\Users\Eric Xu\Desktop\cube'
filenames = os.listdir(directory)[-6:]

for index in [4, 0, 3, 5, 2, 1]:
    filename = filenames[index]
    fileDir = directory + "\\" + filename

    img = cv2.imread(fileDir)
    img = cv2.resize(img,(600,800))
    img = cv2.GaussianBlur(img, (15, 15), 0)

    faceStickers = []
    for y in range(5):
        row = ""
        for x in range(5):
            pixel = list(img[96 * y + 179, 96 * x + 54])
            stickerColour = identifyColour(pixel)
            row += stickerColour
            if x == 2 and y == 2:
                print(pixel)
                faceCenters += stickerColour
        faceStickers.append(row)
        print(row)
    cubeStickers.append(faceStickers)
    print()

kociembaOrder = "URFDLB"
colourDict = {}
for i in range(6):
    colourDict[faceCenters[i]] = kociembaOrder[i]

kociembaString = ""
for face in cubeStickers:
    for row in face:
        for letter in row:
            kociembaString += colourDict[letter]
print(r"./usr/bin/rubiks-cube-solver.py --state", kociembaString)