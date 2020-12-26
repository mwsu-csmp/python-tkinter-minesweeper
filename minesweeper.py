# Python Version 2.7.3
# File: minesweeper.py

from tkinter import *
from tkinter import messagebox as tkMessageBox
from collections import deque
import random
import platform
import time
from datetime import time, date, datetime

SIZE_X = 10
SIZE_Y = 10

STATE_DEFAULT = 0
STATE_CLICKED = 1
STATE_FLAGGED = 2

BTN_CLICK = "<Button-1>"
BTN_FLAG = "<Button-2>" if platform.system() == 'Darwin' else "<Button-3>"

window = None
images = None
frame = None
labels = None

def init():
        global images
        global labels
        global frame
        global window

        # import images
        images = {
            "plain": PhotoImage(file = "images/tile_plain.gif"),
            "clicked": PhotoImage(file = "images/tile_clicked.gif"),
            "mine": PhotoImage(file = "images/tile_mine.gif"),
            "flag": PhotoImage(file = "images/tile_flag.gif"),
            "wrong": PhotoImage(file = "images/tile_wrong.gif"),
            "numbers": []
        }
        for i in range(1, 9):
            images["numbers"].append(PhotoImage(file = "images/tile_"+str(i)+".gif"))

        # set up frame
        frame = Frame(window)
        frame.pack()

        # set up labels/UI
        labels = {
            "time": Label(frame, text = "00:00:00"),
            "mines": Label(frame, text = "Mines: 0"),
            "flags": Label(frame, text = "Flags: 0")
        }
        labels["time"].grid(row = 0, column = 0, columnspan = SIZE_Y) # top full width
        labels["mines"].grid(row = SIZE_X+1, column = 0, columnspan = int(SIZE_Y/2)) # bottom left
        labels["flags"].grid(row = SIZE_X+1, column = int(SIZE_Y/2)-1, columnspan = int(SIZE_Y/2)) # bottom right

        restart() # start game
        updateTimer() # init timer

def setup():
        global flagCount
        global correctFlagCount
        global clickedCount
        global startTime
        global tiles 
        global mines
        global images
        global frame

        # create flag and clicked tile variables
        flagCount = 0
        correctFlagCount = 0
        clickedCount = 0
        startTime = None

        # create buttons
        tiles = dict({})
        mines = 0
        for x in range(0, SIZE_X):
            for y in range(0, SIZE_Y):
                if y == 0:
                    tiles[x] = {}

                id = str(x) + "_" + str(y)
                isMine = False

                # tile image changeable for debug reasons:
                gfx = images["plain"]

                # currently random amount of mines
                if random.uniform(0.0, 1.0) < 0.1:
                    isMine = True
                    mines += 1

                tile = {
                    "id": id,
                    "isMine": isMine,
                    "state": STATE_DEFAULT,
                    "coords": {
                        "x": x,
                        "y": y
                    },
                    "button": Button(frame, image = gfx),
                    "mines": 0 # calculated after grid is built
                }

                tile["button"].bind(BTN_CLICK, onClickWrapper(x, y))
                tile["button"].bind(BTN_FLAG, onRightClickWrapper(x, y))
                tile["button"].grid( row = x+1, column = y ) # offset by 1 row for timer

                tiles[x][y] = tile

        # loop again to find nearby mines and display number on tile
        for x in range(0, SIZE_X):
            for y in range(0, SIZE_Y):
                mc = 0
                for n in getNeighbors(x, y):
                    mc += 1 if n["isMine"] else 0
                tiles[x][y]["mines"] = mc

def restart():
        setup()
        refreshLabels()

def refreshLabels():
        global labels
        global flagCount
        global mines

        labels["flags"].config(text = "Flags: "+str(flagCount))
        labels["mines"].config(text = "Mines: "+str(mines))

def gameOver(won):
        global SIZE_X
        global SIZE_Y
        global tiles 
        global window

        for x in range(0, SIZE_X):
            for y in range(0, SIZE_Y):
                if tiles[x][y]["isMine"] == False and tiles[x][y]["state"] == STATE_FLAGGED:
                    tiles[x][y]["button"].config(image = images["wrong"])
                if tiles[x][y]["isMine"] == True and tiles[x][y]["state"] != STATE_FLAGGED:
                    tiles[x][y]["button"].config(image = images["mine"])

        window.update()

        msg = None
        if won:
            msg = "You Win! Play again?"
        else:
            msg = "You Lose! Play again?"

        res = tkMessageBox.askyesno("Game Over", msg)
        if res:
            restart()
        else:
            window.quit()

def updateTimer():
        global startTime
        global frame 
        global labels 

        ts = "00:00:00"
        if startTime != None:
            delta = datetime.now() - startTime
            ts = str(delta).split('.')[0] # drop ms
            if delta.total_seconds() < 36000:
                ts = "0" + ts # zero-pad
        labels["time"].config(text = ts)
        frame.after(100, updateTimer)

def getNeighbors(x, y):
        global tiles

        neighbors = []
        coords = [
            {"x": x-1,  "y": y-1},  #top right
            {"x": x-1,  "y": y},    #top middle
            {"x": x-1,  "y": y+1},  #top left
            {"x": x,    "y": y-1},  #left
            {"x": x,    "y": y+1},  #right
            {"x": x+1,  "y": y-1},  #bottom right
            {"x": x+1,  "y": y},    #bottom middle
            {"x": x+1,  "y": y+1},  #bottom left
        ]
        for n in coords:
            try:
                neighbors.append(tiles[n["x"]][n["y"]])
            except KeyError:
                pass
        return neighbors

def onClickWrapper(x, y):
        global tiles

        return lambda Button: onClick(tiles[x][y])

def onRightClickWrapper(x, y):
        global tiles

        return lambda Button: onRightClick(tiles[x][y])

def onClick(tile):
        global startTime
        global images 
        global mines
        global clickedCount

        if startTime == None:
            startTime = datetime.now()

        if tile["isMine"] == True:
            # end game
            gameOver(False)
            return

        # change image
        if tile["mines"] == 0:
            tile["button"].config(image = images["clicked"])
            clearSurroundingTiles(tile["id"])
        else:
            tile["button"].config(image = images["numbers"][tile["mines"]-1])
        # if not already set as clicked, change state and count
        if tile["state"] != STATE_CLICKED:
            tile["state"] = STATE_CLICKED
            clickedCount += 1
        if clickedCount == (SIZE_X * SIZE_Y) - mines:
            gameOver(True)

def onRightClick(tile):
        global startTime
        global images
        global flagCount
        global correctFlagCount

        if startTime == None:
            startTime = datetime.now()

        # if not clicked
        if tile["state"] == STATE_DEFAULT:
            tile["button"].config(image = images["flag"])
            tile["state"] = STATE_FLAGGED
            tile["button"].unbind(BTN_CLICK)
            # if a mine
            if tile["isMine"] == True:
                correctFlagCount += 1
            flagCount += 1
            refreshLabels()
        # if flagged, unflag
        elif tile["state"] == 2:
            tile["button"].config(image = images["plain"])
            tile["state"] = 0
            tile["button"].bind(BTN_CLICK, onClickWrapper(tile["coords"]["x"], tile["coords"]["y"]))
            # if a mine
            if tile["isMine"] == True:
                correctFlagCount -= 1
            flagCount -= 1
            refreshLabels()

def clearSurroundingTiles(id):
        queue = deque([id])

        while len(queue) != 0:
            key = queue.popleft()
            parts = key.split("_")
            x = int(parts[0])
            y = int(parts[1])

            for tile in getNeighbors(x, y):
                clearTile(tile, queue)

def clearTile(tile, queue):
        global clickedCount
        global images

        if tile["state"] != STATE_DEFAULT:
            return

        if tile["mines"] == 0:
            tile["button"].config(image = images["clicked"])
            queue.append(tile["id"])
        else:
            tile["button"].config(image = images["numbers"][tile["mines"]-1])

        tile["state"] = STATE_CLICKED
        clickedCount += 1

### END OF CLASSES ###

def main():
    global window

    # create Tk instance
    window = Tk()
    # set program title
    window.title("Minesweeper")
    # create game instance
    init()
    # run event loop
    window.mainloop()

if __name__ == "__main__":
    main()
