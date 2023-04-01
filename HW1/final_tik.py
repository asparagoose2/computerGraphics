import tkinter as tk
from tkinter import Canvas, Label, Tk, simpledialog
from tkinter import messagebox
import tkinter.colorchooser as cc
import math

# Define the screen size
SCREEN_WIDTH = 1700
SCREEN_HEIGHT = 1200
SETTINGS_WINDOW_WIDTH = 300
SETTINGS_WINDOW_HEIGHT = 300
COLOR_THEME = []
DAFAULT_COLOR_THEME = ["#b9fbc0","#ffd670","#ff9770","#ff70a6","#70d6ff"]
DIAGONAL_LINE_INDEX = 0
RHOMBUS_LINE_INDEX = 1
SMALL_CIRCLE_INDEX = 2
BIG_CIRCLE_INDEX = 3
BEZIER_CURVE_INDEX = 4

COLOR_LABELS = ["Diagonal Line Color", "Rhombus Line Color", "Small Circle Color", "Big Circle Color", "Bezier Curve Color"]

BACKGROUND_COLOR = "#000000"
LINE_WIDTH = 2

MINIMUM_LINE_LENGTH = 120

point1 = None
point2 = None
waiting_for_points = False
screen: Canvas = None
root: Tk = None

# Function to calculate the length of a line segment
def length(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Function to draw a pixel on the screen
def put_pixel(x, y, color, screen: Canvas):
    screen.create_line(x, y, x+1, y+1, fill=color, width=LINE_WIDTH)

# function to draw a line using DDA algorithm
def draw_line(x1, y1, x2, y2, color, screen: Canvas):

    # Calculate the change in x and y between the two points
    dx = x2 - x1
    dy = y2 - y1

    # Determine which direction has the larger change
    if abs(dx) > abs(dy):
        steps = abs(dx)
    else:
        steps = abs(dy)

    if steps == 0:
        steps = 1

    # Calculate the amount to increment x and y on each step
    x_increment = dx / steps
    y_increment = dy / steps

    # Set the initial x and y positions
    x = x1
    y = y1

    # Draw the line
    for i in range(steps):

        # Draw a pixel at the current x and y position
        put_pixel(int(x), int(y), color, screen)

        # Increment x and y by the calculated increments
        x += x_increment
        y += y_increment


def draw_rhombus(p1: tuple, p2: tuple, p3: tuple, p4: tuple, color, screen):
    # Draw the rhombus lines, points are given in order
    draw_line(p1[0], p1[1], p2[0], p2[1], color, screen)
    draw_line(p2[0], p2[1], p3[0], p3[1], color, screen)
    draw_line(p3[0], p3[1], p4[0], p4[1], color, screen)
    draw_line(p4[0], p4[1], p1[0], p1[1], color, screen)

def draw_circle(circle_x, circle_y, circle_radius, color, screen):
    # Initialize the x and y coordinates of the first point on the circle
    # (which is at 0 degrees) and the value of a variable called d.
    x = 0
    y = circle_radius
    d = 3 - 2 * circle_radius

    # Loop while x is less than or equal to y.
    while x <= y:
        # Plot the points of the circle using symmetry
        put_pixel(circle_x + x, circle_y + y, color,screen)
        put_pixel(circle_x - x, circle_y + y, color,screen)
        put_pixel(circle_x + x, circle_y - y, color,screen)
        put_pixel(circle_x - x, circle_y - y, color,screen)
        put_pixel(circle_x + y, circle_y + x, color,screen)
        put_pixel(circle_x - y, circle_y + x, color,screen)
        put_pixel(circle_x + y, circle_y - x, color,screen)
        put_pixel(circle_x - y, circle_y - x, color,screen)
        
        # Increment x by 1.
        x += 1

        # If d is greater than 0, decrement y by 1 and update the value of d.
        if d > 0:
            y -= 1
            d = d + 4 * (x - y) + 10

        # Otherwise, update the value of d without changing y.
        else:
            d = d + 4 * x + 6

def draw_bezier_curve(points, steps, screen, color):
    # Create an empty list to hold the points on the curve
    curve_points = []

    # Loop through the number of steps specified by the user
    for t in range(steps):

        # Calculate the value of t between 0 and 1
        t = t / steps

        # Calculate the x and y values of the point on the curve
        x = ((1-t)**3)*points[0][0] + 3*((1-t)**2)*t*points[1][0] + 3*(1-t)*(t**2)*points[2][0] + (t**3)*points[3][0]
        y = ((1-t)**3)*points[0][1] + 3*((1-t)**2)*t*points[1][1] + 3*(1-t)*(t**2)*points[2][1] + (t**3)*points[3][1]

        # Add the point to the curve_points list
        curve_points.append((int(x), int(y)))

    # Add the last point to the curve_points list
    curve_points.append(points[len(points)-1])

    # Loop through the list of points and draw lines between each pair of adjacent points
    for i in range(len(curve_points) - 1):
        draw_line(curve_points[i][0], curve_points[i][1], curve_points[i+1][0], curve_points[i+1][1], color, screen)
    

def validate_points():
    global point1, point2, waiting_for_points
    if point1 is None or point2 is None:
        messagebox.showerror("Error", "You must select two points")
        return False
    if point1 == point2:
        messagebox.showerror("Error", "The two points must be different")
        return False
    if length(point1[0], point1[1], point2[0], point2[1]) < MINIMUM_LINE_LENGTH:
        messagebox.showerror("Error", "The two points must be at least {} pixels apart".format(MINIMUM_LINE_LENGTH))
        return False
    return True

def handle_click(event: tk.Event):
    global point1, point2, waiting_for_points
    if waiting_for_points:
        # draw the point on the screen
        screen.create_oval(event.x - 5, event.y - 5, event.x + 5, event.y + 5, fill="red")
        # Store the first point if it hasn't been set yet
        if point1 is None:
            point1 = (event.x, event.y)
        else:
            point2 = (event.x, event.y)
            if validate_points():
                waiting_for_points = False
                draw_picture(screen)            
            else:
                # Reset the points and start over
                point1 = None
                point2 = None
                screen.delete("all")


def get_integer_from_user():
    input = simpledialog.askinteger("Input", "Enter the number of sections for the Bezier curve:", initialvalue=100, minvalue=3, maxvalue=1000)
    return input

def draw_picture(screen: Canvas):
    global waiting_for_points, point1, point2

    steps = get_integer_from_user()
    if steps is None:
        steps = 100

    # Clear the screen
    screen.delete("all")

    if point1[0] > point2[0]:
        point1, point2 = point2, point1

    x1, y1 = point1
    x2, y2 = point2

    # calculate the angle of the long diagonal
    l = length(x1, y1, x2, y2)

    # calculate the middle point of the long diagonal
    mx = (x1 + x2) // 2
    my = (y1 + y2) // 2

    # calculate the angle of the long diagonal
    alfa  = math.atan((y2-y1)/(x2-x1))

    # calculate the x and y deltas for the short diagonals
    delta_x =(1/3)*l*math.sin(alfa)
    delta_y =(1/3)*l*math.cos(alfa)

    # calculate the coordinates of the short diagonals
    x3 =  mx - delta_x
    y3 =  my + delta_y
    x4 =  mx + delta_x
    y4 =  my - delta_y
    
    # round the coordinates to avoid floating point errors
    x3 = round(x3)
    y3 = round(y3)
    x4 = round(x4)
    y4 = round(y4)


    # draw the diagonal lines
    draw_line(x1, y1, x2, y2, DIAGONAL_LINE_COLOR, screen)
    draw_line(x3, y3, x4, y4, DIAGONAL_LINE_COLOR, screen)
    # draw the rest of the picture
    draw_rhombus((x1, y1), (x3, y3), (x2, y2),(x4, y4), RHOMBUS_LINE_COLOR, screen)
    draw_circle(mx, my, round((1/3)*l), SMALL_CIRCLE_COLOR, screen)
    draw_circle(mx, my, round(l//2), BIG_CIRCLE_COLOR, screen)
    draw_bezier_curve([(x1, y1), (x3, y3),(x4, y4),(x2, y2)], steps, screen, BEZIER_CURVE_COLOR)
    
    # Reset the points
    point1 = None
    point2 = None
    waiting_for_points = True


def create_color_picker_window():
    # Create a list to store the selected colors
    color_root = tk.Tk()
    color_root.title("Settings")
    line_width = tk.IntVar(master=color_root ,value=2)

    width_title_label = tk.Label(color_root, text="Select line width")
    width_title_label.pack()
    line_width_scale = tk.Scale(color_root, from_=1, to=4, orient=tk.HORIZONTAL, variable=line_width)
    line_width_scale.pack(padx=0, pady=10)

    selected_colors = DAFAULT_COLOR_THEME

    # Create a function to apply the selected color
    def apply_color(index):
        hex_color = color_labels[index].cget("bg")

        # Show a color picker dialog to let the user choose a color
        selected_color = cc.askcolor(color=hex_color, title="Choose a color")

        # Set the background of the label to the selected color
        if selected_color:
            color_labels[index].configure(bg=selected_color[1])
            selected_colors[index] = selected_color[1]

    color_title_label = tk.Label(color_root, text="Select 4 colors")
    color_title_label.pack()

    # Create 4 Labels to display the selected colors
    color_labels = []
    for i in range(5):
        color_label = tk.Label(color_root, text=COLOR_LABELS[i], bg=DAFAULT_COLOR_THEME[i], width=20, height=3)
        color_label.bind("<Button-1>", lambda event, i=i: apply_color(i))
        color_labels.append(color_label)


    # Pack the widgets into the window
    for i in range(5):
        color_labels[i].pack(padx=10, pady=10)

    # Create a function to handle closing the window
    def apply_color_selection():
        print("Selected colors: ", selected_colors)
        global DIAGONAL_LINE_COLOR, RHOMBUS_LINE_COLOR, SMALL_CIRCLE_COLOR, BIG_CIRCLE_COLOR, BEZIER_CURVE_COLOR,LINE_WIDTH
        DIAGONAL_LINE_COLOR = selected_colors[DIAGONAL_LINE_INDEX]
        RHOMBUS_LINE_COLOR = selected_colors[RHOMBUS_LINE_INDEX]
        SMALL_CIRCLE_COLOR = selected_colors[SMALL_CIRCLE_INDEX]
        BIG_CIRCLE_COLOR = selected_colors[BIG_CIRCLE_INDEX]
        BEZIER_CURVE_COLOR = selected_colors[BEZIER_CURVE_INDEX]

        LINE_WIDTH = line_width.get()

        # Close the window
        color_root.destroy()

    # Create a Button to close the window
    close_button = tk.Button(color_root, text="Apply", command=apply_color_selection)
    close_button.pack(padx=10, pady=10)
    color_root.mainloop()

# main function
def main():
    # init the screen
    global waiting_for_points, point1, point2, screen, root
    create_color_picker_window()
    root = Tk()
    root.title("HW1: Ofir Duchovne")
    screen = Canvas(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bg=BACKGROUND_COLOR)
    screen.pack()

    # Settings wondow 
    label = Label(root, text="Click on the screen to select 2 points")
    label.pack()

    waiting_for_points = True

    screen.bind("<Button-1>", handle_click)

    print("before mainloop")
    root.mainloop()
    print("after mainloop")
        

if __name__ == "__main__":
    main()

