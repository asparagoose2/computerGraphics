import pygame

# Define the screen size
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Define the line endpoints
x1 = 50
y1 = 50
x2 = 750
y2 = 550

# Initialize pygame and the screen
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("DDA Algorithm Line")

# Set the line color to red
line_color = (255, 0, 0)

# Implement the DDA algorithm
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
    screen.set_at((int(x), int(y)), line_color)
    x += x_increment
    y += y_increment

# Update the screen
pygame.display.update()

# Wait for the user to close the window
done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

# Quit pygame and close the window
pygame.quit()