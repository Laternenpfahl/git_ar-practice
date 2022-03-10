import numpy as np
import matplotlib.pyplot as plt
import time
import sys
import random
import pygame
import os.path as mypath
from os import mkdir

# USAGE: python Path/to/File/Chord-changes.py *SCALE* *DURATION IN SECONDS*

# *SCALE* can be any Key out of scales_dict (below), which can be modified/expanded indefinitely
# *DURATION IN SECONDS* tells the program how long it should run AFTER start screen

# Tap SPACEBAR each time you played the chord, ESC if you want to exit

# Longterm-Results are only shown for sessions with the same duration and the same scale

# Programmed for unmodified linux home directories
# make sure "~/Documents" exists or modify line 137 - 138 in this script

scales_dict = {
    "C": ["C", "dm", "em", "F", "G", "am", "B7"],
    "D": ["D", "em", "f#m", "G", "A", "bm", "C#7"],
    "E": ["E", "f#m", "g#m", "A", "B", "c#m", "D#7"],
    "F": ["F", "gm", "am", "Bb", "C", "dm", "E7"],
    "G": ["G", "am", "bm", "C", "D", "em", "F#7"],
    "A": ["A", "bm", "c#m", "D", "E", "f#m", "G#7"],
    "Bb": ["Bb", "cm", "dm", "Eb", "F", "gm", "A7"],
    "B": ["B", "c#m", "d#m", "E", "F#", "g#m", "A#7"],
}


pygame.init()

display_width = 1200
display_height = 800

white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)

pygame.event.set_blocked(None)  # blocks all events from entering queue

pygame.event.set_allowed(pygame.KEYDOWN)  # allows button-presses and QUIT-events
pygame.event.set_allowed(pygame.QUIT)

gameDisplay = pygame.display.set_mode(
    (display_width, display_height)
)  # gamedisplay & clock
pygame.display.set_caption("Chord Changes")
gameClock = pygame.time.Clock()

myfont = pygame.font.Font("freesansbold.ttf", 300)
chord_text = myfont.render("Start", True, white, black)  # startscreen

myscale = scales_dict[str(sys.argv[1])]  # scale specified in command line

timer_start = 0  # some variables needed later
duration = 0
myindex1 = -1
myindex2 = -1
runtime = 0

score_unit = 0

start = True

score = np.zeros(len(myscale))  # arrays for statistics in the end
score_norm = np.zeros(len(myscale))
mybins = np.arange(0, len(myscale), 1)
longterm = np.array([])
longterm_labels = np.array([])

while duration <= int(sys.argv[2]) or start:

    # setting up display and clock (Note to self: Replace time.time() with gameClock)

    duration = time.time() - timer_start

    gameDisplay.fill(black)

    chord_rect = chord_text.get_rect()
    chord_rect.center = (display_width // 2, display_height // 2)

    gameDisplay.blit(chord_text, chord_rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # breaking out of loop if quit
            duration = 9999
            break

        try:
            if event.__dict__["unicode"] == " ":  # space-bar pressed does something

                if (
                    start
                ):  # start-screen only, starts timer after first time pressing SPACEBAR
                    timer_start = time.time()
                    start = False
                    duration = time.time() - timer_start
                    score_unit = time.time()

                else:  # adds time and increases the counter
                    score[myindex1] = score[myindex1] + (time.time() - score_unit)
                    score_norm[myindex1] += 1
                    score_unit = time.time()

                # making sure that the same chord doesnt come twice in a row

                myindex1 = random.randint(0, len(myscale) - 1)

                while myindex1 == myindex2:
                    myindex1 = random.randint(0, len(myscale) - 1)

                chord_text = myfont.render(myscale[myindex1], True, green, black)
                myindex2 = myindex1

            elif event.__dict__["unicode"] == "\x1b":  # esc-button equals QUIT
                duration = 9999

        except KeyError:
            pass

    runtime = gameClock.tick(30)
    pygame.display.update()

# last chord-time is added, if it was on screen for long enough

if ((time.time() - score_unit)) >= 1.5:
    score[myindex1] = score[myindex1] + (time.time() - score_unit)
    score_norm[myindex1] += 1

print(myscale)
print(score.sum())

normed_score = score[score_norm.nonzero()] / score_norm[score_norm.nonzero()]

pygame.quit()  # quitting the game and plotting the statistics below

home = mypath.expanduser("~")

if not mypath.isdir(home + "/Documents/Guitar-Practice"):
    mkdir(home + "/Documents/Guitar-Practice")

if mypath.isfile(home + "/Documents/Guitar-Practice/scorefile.txt"):
    f = open(home + "/Documents/Guitar-Practice/scorefile.txt", "a+")
    f.write(
        str(sys.argv[1])
        + f",{myscale[np.argmax(normed_score)]}"
        + f",{max(normed_score)}"
        + ","
        + str(sys.argv[2])
        + ",\n"
    )

else:
    f = open(home + "/Documents/Guitar-Practice/scorefile.txt", "w+")
    f.write(
        str(sys.argv[1])
        + f",{myscale[np.argmax(normed_score)]}"
        + f",{max(normed_score)}"
        + ","
        + str(sys.argv[2])
        + ",\n"
    )

f.seek(0)

while True:

    line_dummy = f.readline()

    if line_dummy == "":
        print("Fail")
        break

    line = line_dummy.split(",")

    if line[0] == str(sys.argv[1]) and line[3] == str(sys.argv[2]):
        longterm = np.append(longterm, float(line[2]))
        longterm_labels = np.append(longterm_labels, line[1])

print(longterm)
print(longterm_labels)

fig = plt.figure(figsize=(20, 20))

ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)

ax1.bar(mybins[score_norm.nonzero()], normed_score)
ax1.set_title("Current Session")
ax1.set_xticks(mybins)
ax1.set_xticklabels(myscale)
ax1.set_ylabel("Seconds per chord")

ax2.bar(np.arange(0, len(longterm), 1), longterm)
ax2.set_title(f"Longterm progress (Mode: {str(sys.argv[2])}s)")
ax2.set_xticks(np.arange(0, len(longterm), 1))
ax2.set_xticklabels(longterm_labels)
ax2.set_ylabel("Seconds per chord")

plt.savefig("chord_changes.png")

f.close()

quit()
