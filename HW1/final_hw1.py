import random
from tkinter import Tk, simpledialog
import pygame
import math

# Define the screen size
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
DIAGONAL_LINE_COLOR = (255, 0, 0)  
RHOMBUS_LINE_COLOR = (0, 255, 0) 
SMALL_CIRCLE_COLOR = (0, 0, 255)
BEZIER_CURVE_COLOR = (255, 255, 0)


# RHOMBUS_SHARP_ANGLE_IN_RADIANS = math.atan((1/2)/(2/3))


# Function to calculate the length of a line segment
def length(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Function to calculate the angle of a line segment
def angle(x1, y1, x2, y2):
    return math.atan2(x2 - x1, y2 - y1)

# Function to calculate the coordinates of a point given the length and angle
def point_at_distance(x, y, length, angle):
    return x + length * math.cos(angle), y + length * math.sin(angle)

# Function to calculate a perpendicular line to a given line
def perpendicular_line(x1, y1, x2, y2):
    l = length(x1, y1, x2, y2)
    a = angle(x1, y1, x2, y2)
    pl = l * (2 / 3)

    px1, py1 = point_at_distance(x1, y1, pl, a + math.pi / 2)
    px2, py2 = point_at_distance(x2, y2, pl, a + math.pi / 2)

    return px1, py1, px2, py2



# function to draw a line using DDA algorithm
def draw_line(x1, y1, x2, y2, color, screen, draw=False):
    dx = x2 - x1
    dy = y2 - y1

    if abs(dx) > abs(dy):
        steps = abs(dx)
    else:
        steps = abs(dy)

    x_increment = dx / steps
    y_increment = dy / steps

    x = x1
    y = y1

    # Draw the line
    for i in range(steps):
        screen.set_at((int(x), int(y)), color)
        x += x_increment
        y += y_increment

    # Update the screen
    if draw:
        pygame.display.update()


def draw_rhombus(p1: tuple, p2: tuple, p3: tuple, p4: tuple, color, screen):
    draw_line(p1[0], p1[1], p2[0], p2[1], color, screen)
    draw_line(p2[0], p2[1], p3[0], p3[1], color, screen)
    draw_line(p3[0], p3[1], p4[0], p4[1], color, screen)
    draw_line(p4[0], p4[1], p1[0], p1[1], color, screen)

def draw_circle(circle_x, circle_y, circle_radius, color, screen):
    x = 0
    y = circle_radius
    d = 3 - 2 * circle_radius
    while x <= y:
        # Plot the points of the circle using symmetry
        screen.set_at((circle_x + x, circle_y + y), color)
        screen.set_at((circle_x - x, circle_y + y), color)
        screen.set_at((circle_x + x, circle_y - y), color)
        screen.set_at((circle_x - x, circle_y - y), color)
        screen.set_at((circle_x + y, circle_y + x), color)
        screen.set_at((circle_x - y, circle_y + x), color)
        screen.set_at((circle_x + y, circle_y - x), color)
        screen.set_at((circle_x - y, circle_y - x), color)
        x += 1
        if d > 0:
            y -= 1
            d = d + 4 * (x - y) + 10
        else:
            d = d + 4 * x + 6

def draw_bezier_curve(points, steps, screen, color):
    return_points = []
    for t in range(steps):
        t = t / steps
        x = ((1-t)**3)*points[0][0] + 3*((1-t)**2)*t*points[1][0] + 3*(1-t)*(t**2)*points[2][0] + (t**3)*points[3][0]
        y = ((1-t)**3)*points[0][1] + 3*((1-t)**2)*t*points[1][1] + 3*(1-t)*(t**2)*points[2][1] + (t**3)*points[3][1]
        return_points.append((int(x), int(y)))
    return_points.append(points[3])
    for i in range(len(return_points) - 1):
        draw_line(return_points[i][0], return_points[i][1], return_points[i+1][0], return_points[i+1][1], color, screen)
    

# function to init the screen
def init_screen():
    # Initialize pygame and the screen
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("HW1: Ofir Duchovne")

    # write indtructions on screen
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render('Click on 2 points to draw the picture', True, (255, 255, 255), (0, 0, 0))
    textRect = text.get_rect()
    textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    screen.blit(text, textRect)

    return screen


def get_point_from_user():
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                done = True
            if event.type == pygame.QUIT:
                exit()
    done = False
    return x, y



# main function
def main():
    # init the screen
    screen = init_screen()

    done = False
    while True:
        # Clear the screen
        screen.fill((0, 0, 0))

        # get 2 points from user, this line is the long diagonal of the rhombus
        x1, y1 = get_point_from_user()
        x2, y2 = get_point_from_user()


        # calculate the angle of the long diagonal
        l = length(x1, y1, x2, y2)

        # calculate the 2 other points of the rhombus's diagonal line (short diagonal) 
        # which is perpendicular to the long diagonal and has a length of 2/3 the long diagonal


        # calculate the middle point of the long diagonal
        mx = (x1 + x2) // 2
        my = (y1 + y2) // 2

        alfa  = math.atan((y2-y1)/(x2-x1))

        delta_x =(1/3)*l*math.sin(alfa)
        delta_y =(1/3)*l*math.cos(alfa)

        x3 =  mx - delta_x
        y3 =  my + delta_y
        x4 =  mx + delta_x
        y4 =  my - delta_y

    

        

        # round the coordinates
        x3 = round(x3)
        y3 = round(y3)
        x4 = round(x4)
        y4 = round(y4)

 
        # draw the diagonal
        draw_line(x1, y1, x2, y2, DIAGONAL_LINE_COLOR, screen, True)
        draw_line(x3, y3, x4, y4, DIAGONAL_LINE_COLOR, screen)

        draw_rhombus((x1, y1), (x3, y3), (x2, y2),(x4, y4), RHOMBUS_LINE_COLOR, screen)
        draw_circle(mx, my, round((1/3)*l), SMALL_CIRCLE_COLOR, screen)
        draw_circle(mx, my, round(l//2), SMALL_CIRCLE_COLOR, screen)

        # ask the user to choose a number of steps for the bezier curve
        steps = int(input("Enter number of steps for the bezier curve: "))
     

        draw_bezier_curve([(x1, y1), (x3, y3),(x4, y4),(x2, y2)], steps, screen, BEZIER_CURVE_COLOR)

        pygame.display.update()




        
        


if __name__ == "__main__":
    main()
