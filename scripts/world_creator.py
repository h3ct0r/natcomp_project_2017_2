"""
 Example program to show using an array to back a grid on-screen.

 Sample Python/Pygame Programs
 Simpson College Computer Science
 http://programarcadegames.com/
 http://simpson.edu/computer-science/

 Explanation video: http://youtu.be/mdTeqiWyFnc
"""
import pygame
import os
import json
import time

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# This sets the WIDTH and HEIGHT of each grid location
WIDTH = 8
HEIGHT = 8

# This sets the margin between each cell
MARGIN = 1

# Create a 2 dimensional array. A two dimensional
# array is simply a list of lists.

ROW_NUMBER = 100
COLUMN_NUMBER = 100

grid = []
for row in range(ROW_NUMBER):
    # Add an empty array that will hold each cell
    # in this row
    grid.append([])
    for column in range(COLUMN_NUMBER):
        grid[row].append(0)  # Append a cell

# Set row 1, cell 5 to one. (Remember rows and
# column numbers start at zero.)
#grid[1][5] = 1

# Initialize pygame
pygame.init()

# Set the HEIGHT and WIDTH of the screen
WINDOW_SIZE = [(COLUMN_NUMBER * WIDTH) + ((MARGIN * 2) + (MARGIN * COLUMN_NUMBER)),
               (ROW_NUMBER * HEIGHT) + ((MARGIN * 2) + (MARGIN * ROW_NUMBER))]
screen = pygame.display.set_mode(WINDOW_SIZE)

# Set title of screen
pygame.display.set_caption("Array Backed Grid")

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

cell_value = 0

mouse_active = False

# -------- Main Program Loop -----------
while not done:
    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            done = True  # Flag that we are done so we exit this loop
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_active = True
            print("Down Click ")
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_active = False
            print("Up Click ")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_0:
                print("KEY '0'")
                cell_value = 0
            if event.key == pygame.K_1:
                print("KEY '1'")
                cell_value = 1
            if event.key == pygame.K_2:
                print("KEY '2'")
                cell_value = 2
            if event.key == pygame.K_s:
                print("KEY 'S'")
                with open(os.path.join("../", "dataset", "my_world_"+str(time.time())+".json"), 'w') as fp:
                    json.dump(grid, fp)

        if mouse_active:
            # User clicks the mouse. Get the position
            pos = pygame.mouse.get_pos()

            if 0 <= pos[0] < WINDOW_SIZE[0] and 0 <= pos[1] < WINDOW_SIZE[1]:
                # Change the x/y screen coordinates to grid coordinates
                column = pos[0] // (WIDTH + MARGIN)
                row = pos[1] // (HEIGHT + MARGIN)
                # Set that location to one
                grid[row][column] = cell_value
                print("Click ", pos, "Grid coordinates: ", row, column)
                print("Cell value", grid[row][column])


    # Set the screen background
    screen.fill(BLACK)

    # Draw the grid
    for row in range(ROW_NUMBER):
        for column in range(COLUMN_NUMBER):
            color = WHITE
            if grid[row][column] == 1:
                color = BLACK
            if grid[row][column] == 2:
                color = BLUE

            pygame.draw.rect(screen,
                             color,
                             [(MARGIN + WIDTH) * column + MARGIN,
                              (MARGIN + HEIGHT) * row + MARGIN,
                              WIDTH,
                              HEIGHT])

    # Limit to 60 frames per second
    clock.tick(60)

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

# Be IDLE friendly. If you forget this line, the program will 'hang'
# on exit.
pygame.quit()