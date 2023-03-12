import random
import pygame

# Define the screen size
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LINE_COLOR = (255, 0, 0)

# function to draw a line using DDA algorithm
def draw_line(x1, y1, x2, y2, color, screen):
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
    pygame.display.update()


# function to init the screen
def init_screen():
    # Initialize pygame and the screen
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("DDA Algorithm Line")

    # Set the line color to red

    return screen, LINE_COLOR

# main function
def main():
    # init the screen
    screen, line_color = init_screen()

    done = False
    while not done:
        # get the first endpoint from user by clicking on the screen
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x1, y1 = pygame.mouse.get_pos()
                    done = True
                if event.type == pygame.QUIT:
                    pygame.quit()
        done = False

        # get the second endpoint from user by clicking on the screen
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x2, y2 = pygame.mouse.get_pos()
                    done = True
                if event.type == pygame.QUIT:
                    pygame.quit()
        done = False

        # Clear the screen
        screen.fill((0, 0, 0))
        
        # Draw the line
        draw_line(x1, y1, x2, y2, line_color, screen)


if __name__ == "__main__":
    main()
