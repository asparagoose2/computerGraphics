import pygame
import numpy as np

# Initialize Pygame
pygame.init()

# Set the dimensions of the screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Set the color of the curve (RGB)
curve_color = (255, 255, 0)

def draw_bezier_curve(points, steps):
    """
    Draws a Bezier curve on the Pygame screen using a list of control points
    and the number of steps to interpolate between each pair of points.
    """
    # Create the Bezier matrix
    n = len(points) - 1
    bezier_matrix = np.zeros((n+1, n+1))
    for i in range(n+1):
        for j in range(i+1):
            if j == 0 or j == i:
                bezier_matrix[i][j] = 1
            else:
                bezier_matrix[i][j] = bezier_matrix[i-1][j-1] + bezier_matrix[i-1][j]
    
    # Create a list of interpolated points along the curve
    curve_points = []
    for t in range(steps + 1):
        u = 1 - t / float(steps)
        u_vector = np.array([u**i for i in range(n+1)])
        t_vector = np.array([(t/float(steps))**i for i in range(n+1)])
        point = np.dot(np.dot(u_vector, bezier_matrix), np.dot(t_vector, points))
        curve_points.append((int(point[0]), int(point[1])))
    
    # Draw the curve by connecting the interpolated points
    for i in range(len(curve_points) - 1):
        pygame.draw.line(screen, curve_color, curve_points[i], curve_points[i+1])

# Set the control points of the curve (as a list of tuples)
control_points = [(100, 100), (300, 500), (500, 100), (700, 500)]

# Draw the curve using the control points and 100 interpolated steps between each pair of points
draw_bezier_curve(control_points, 100)

# Update the screen to show the curve
pygame.display.flip()

# Wait for the user to close the window
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# Quit Pygame
pygame.quit()
